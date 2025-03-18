from api.serializers import *
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

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
