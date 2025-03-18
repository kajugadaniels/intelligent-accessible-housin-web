from backend.models import *
from django.db.models import Q
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
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

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new user.
    """
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = ['name', 'email', 'phone_number', 'password', 'confirm_password']
    
    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')

        if password != confirm_password:
            raise serializers.ValidationError("The two password fields didn’t match.")
        
        # Validate the password according to Django's password validation settings
        try:
            validate_password(password)
        except ValidationError as error:
            raise serializers.ValidationError({"password": error.messages})

        return attrs

    def create(self, validated_data):
        # Remove confirm_password since it's not stored
        validated_data.pop('confirm_password')
        user = get_user_model().objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'],
            phone_number=validated_data['phone_number'],
        )
        return user

class AmenitySerializer(serializers.ModelSerializer):
    """
    Serializer for Amenity data.
    """
    class Meta:
        model = Amenity
        fields = ['id', 'name']


class PropertyImageSerializer(serializers.ModelSerializer):
    """
    Serializer for Property Image data.
    """
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'created_at']


class PropertyReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Property Review data.
    """
    class Meta:
        model = PropertyReview
        fields = [
            'id', 'name', 'email', 'comment', 
            'location', 'staff', 'cleanliness', 'value_for_money', 
            'comfort', 'facilities', 'free_wifi', 'status', 'created_at'
        ]

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User data.
    This will provide detailed user information (the creator of the property).
    """
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'phone_number', 'role']


class PropertySerializer(serializers.ModelSerializer):
    """
    Serializer for detailed property information.
    """
    city = serializers.CharField(source='get_city_display')
    type = serializers.CharField(source='get_type_display')
    category = serializers.CharField(source='get_category_display')
    created_by = UserSerializer()
    amenities = AmenitySerializer(many=True)
    images = PropertyImageSerializer(many=True)
    # reviews = PropertyReviewSerializer(many=True)
    review_data = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            'id', 'name', 'slug', 'description', 
            'price_usd', 'price_rwf', 'city', 'type', 'category',
            'bathroom', 'capacity', 'size', 'image', 'address',
            'created_by', 'created_at', 'updated_at', 
            'amenities', 'images', 'review_data'
        ]

    # def get_review_data(self, obj):
    #     """
    #     Method to calculate and return review data.
    #     """
    #     review_data = obj.get_review_data()
    #     return review_data
