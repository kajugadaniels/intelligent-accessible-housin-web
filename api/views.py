from backend.models import *
from api.serializers import *
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
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