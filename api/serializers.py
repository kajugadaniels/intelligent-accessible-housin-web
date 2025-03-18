from django.db.models import Q
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password

class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    identifier = serializers.CharField(help_text="Enter your email or phone number.")
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs.get('identifier')
        password = attrs.get('password')

        if not identifier:
            raise serializers.ValidationError("Identifier (email or phone number) is required.")
        if not password:
            raise serializers.ValidationError("Password is required.")

        User = get_user_model()
        try:
            user = User.objects.get(
                Q(email__iexact=identifier) | Q(phone_number=identifier)
            )
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with the provided email or phone number.")

        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect password. Please check your credentials.")

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        attrs['refresh'] = str(refresh)
        attrs['access'] = str(refresh.access_token)

        return attrs
