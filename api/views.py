from users.models import *
from backend.models import *
from api.serializers import *
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.exceptions import InvalidToken

class LoginView(APIView):
    """
    Handle login using an identifier (email, phone number, or username) and password.
    Returns JWT tokens upon successful authentication.
    """
    def post(self, request, *args, **kwargs):
        """
        Handle login request and return JWT tokens.
        """
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            return Response(
                {
                    "access": serializer.validated_data['access'],
                    "refresh": serializer.validated_data['refresh']
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {"detail": "Validation error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

class LogoutView(APIView):
    """
    Handle logout by blacklisting the refresh token.
    """
    def post(self, request, *args, **kwargs):
        try:
            # Get the refresh token from the request headers
            refresh_token = request.data.get('refresh', None)
            if not refresh_token:
                return Response({"detail": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"detail": "Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)

        except InvalidToken:
            return Response({"detail": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    """
    Handle new user registration.
    """
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"detail": "User created successfully", "user": {"id": user.id, "email": user.email}},
                status=status.HTTP_201_CREATED
            )

        return Response(
            {"detail": "Validation error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

class VerifyTokenView(APIView):
    """
    Endpoint to verify the access token and retrieve user details.
    """

    def get(self, request, *args, **kwargs):
        """
        This will check if the access token is valid and return user details.
        """
        try:
            # Retrieve the token from the Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return Response({"detail": "Authorization header missing."}, status=status.HTTP_400_BAD_REQUEST)

            token = auth_header.split(' ')[1]  # Extract token from 'Bearer <token>'

            # Validate the token
            access_token = AccessToken(token)  # This will check if token is valid and not expired

            # If token is valid, retrieve user
            user = User.objects.get(id=access_token['user_id'])
            user_data = UserSerializer(user).data

            return Response({
                "detail": "Token is valid",
                "user": user_data
            }, status=status.HTTP_200_OK)

        except InvalidToken as e:
            # Token is invalid or expired
            return Response({
                "detail": "Invalid or expired token.",
                "error": str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)
        except TokenError as e:
            # Handle any other token errors
            return Response({
                "detail": "Token error.",
                "error": str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            # If no user is found for the token
            return Response({
                "detail": "User associated with this token not found."
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "detail": "An unexpected error occurred.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DashboardAPIView(APIView):
    """
    Retrieve summary metrics for the logged-in user:
      - application counts by status
      - contract counts by status/payment
      - chart data (labels + values)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.role != 'User' and not user.is_superuser:
            return Response(
                {'detail': 'You are not authorized to view this resource.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Application metrics
        total_apps       = RentApplication.objects.filter(user=user).count()
        pending_apps     = RentApplication.objects.filter(user=user, status='Pending').count()
        accepted_apps    = RentApplication.objects.filter(user=user, status='Accepted').count()
        rejected_apps    = RentApplication.objects.filter(user=user, status='Rejected').count()
        moved_out_apps   = RentApplication.objects.filter(user=user, status='Moved Out').count()

        # Contract metrics
        total_contracts  = Contract.objects.filter(tenant=user).count()
        active_contracts = Contract.objects.filter(tenant=user, status='Active').count()
        overdue_contracts= Contract.objects.filter(tenant=user, payment_status='Overdue').count()

        data = {
            'total_applications': total_apps,
            'pending_applications': pending_apps,
            'accepted_applications': accepted_apps,
            'rejected_applications': rejected_apps,
            'moved_out_applications': moved_out_apps,
            'total_contracts': total_contracts,
            'active_contracts': active_contracts,
            'overdue_contracts': overdue_contracts,
            'status_labels': ['Pending', 'Accepted', 'Rejected', 'Moved Out'],
            'status_data': [pending_apps, accepted_apps, rejected_apps, moved_out_apps],
        }

        return Response(data, status=status.HTTP_200_OK)

class GetAmenitiesView(APIView):
    """
    Retrieve a list of all amenities with their properties.
    """
    def get(self, request, *args, **kwargs):
        amenities = Amenity.objects.all().order_by('-id')

        # Serialize the amenities with their properties
        serializer = AmenityNestedSerializer(amenities, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

class ShowAmenityView(APIView):
    """
    Retrieve a single amenity by ID along with all properties that have this amenity.
    """
    def get(self, request, id, *args, **kwargs):
        try:
            amenity = Amenity.objects.get(id=id)
        except Amenity.DoesNotExist:
            return Response({"detail": "Amenity not found."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the amenity with its associated properties
        serializer = AmenityNestedSerializer(amenity, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

class GetCategoriesView(APIView):
    """
    Retrieve a list of all categories with their properties.
    """
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all().order_by('-id')

        # Serialize the categories with their properties
        serializer = CategoryNestedSerializer(categories, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

class ShowCategoryView(APIView):
    """
    Retrieve a single category by ID along with all properties in that category.
    """
    def get(self, request, id, *args, **kwargs):
        try:
            category = Category.objects.get(id=id)  # Fetch category by ID
        except Category.DoesNotExist:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the category with its associated properties
        serializer = CategoryNestedSerializer(category, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

class GetPropertiesView(APIView):
    """
    Retrieve a list of all properties. This is not protected.
    """
    def get(self, request, *args, **kwargs):
        properties = Property.objects.all().order_by('-id')

        # Optional: You can add filtering here based on query params, like city, price, etc.

        # If a serializer exists for Property
        serializer = PropertySerializer(properties, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

class ShowPropertyView(APIView):
    """
    Retrieve a single property by ID. This is not protected.
    """
    def get(self, request, id, *args, **kwargs):
        try:
            property = Property.objects.get(id=id)
        except Property.DoesNotExist:
            return Response({"detail": "Property not found."}, status=status.HTTP_404_NOT_FOUND)

        # Assuming you have a PropertySerializer to return the property data
        serializer = PropertySerializer(property, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

class NotificationsAPIView(APIView):
    """
    Retrieve the latest notifications for the logged-in user.
    
    - For regular users:
        • new_properties: last 10 properties added
        • user_applications: last 10 of their rent applications
        • user_contracts:   last 10 of their contracts
    - For house providers:
        • accepted_contracts: last 10 contracts on their properties with status='Accepted'
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        if user.role == 'User' or user.is_superuser:
            # Regular user notifications
            new_properties = Property.objects.order_by('-created_at')[:10]
            user_apps = RentApplication.objects.filter(user=user).order_by('-created_at')[:10]
            user_contracts = Contract.objects.filter(tenant=user).order_by('-created_at')[:10]

            return Response({
                "notif_type": "user",
                "new_properties": PropertySerializer(new_properties, many=True, context={'request': request}).data,
                "user_applications": [
                    {
                        "id": app.id,
                        "property": app.property.name,
                        "status": app.status,
                        "submitted_at": app.created_at
                    }
                    for app in user_apps
                ],
                "user_contracts": [
                    {
                        "id": c.id,
                        "contract_number": c.contract_number,
                        "status": c.status,
                        "payment_status": c.payment_status,
                        "updated_at": c.updated_at
                    }
                    for c in user_contracts
                ]
            }, status=status.HTTP_200_OK)

        else:
            # House provider notifications
            accepted_contracts = Contract.objects.filter(
                property__created_by=user,
                status='Accepted'
            ).order_by('-updated_at')[:10]

            return Response({
                "notif_type": "provider",
                "accepted_contracts": [
                    {
                        "id": c.id,
                        "contract_number": c.contract_number,
                        "tenant": c.tenant.name,
                        "status": c.status,
                        "updated_at": c.updated_at
                    }
                    for c in accepted_contracts
                ]
            }, status=status.HTTP_200_OK)

class ApplicationsAPIView(APIView):
    """
    Retrieve all rent applications for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.role != 'User' and not user.is_superuser:
            return Response(
                {'detail': 'You are not authorized to view this resource.'},
                status=status.HTTP_403_FORBIDDEN
            )

        applications = RentApplication.objects.filter(user=user).order_by('-created_at')
        data = []
        for app in applications:
            data.append({
                'id': app.id,
                'property': {
                    'id': app.property.id,
                    'name': app.property.name,
                },
                'preferred_move_in_date': app.preferred_move_in_date.isoformat() if app.preferred_move_in_date else None,
                'rental_period_months': app.rental_period_months,
                'status': app.status,
                'created_at': app.created_at.isoformat(),
            })

        return Response(data, status=status.HTTP_200_OK)