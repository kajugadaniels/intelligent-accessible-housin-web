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
    created_by = UserSerializer()  # Now retrieving full user details
    amenities = AmenitySerializer(many=True)
    images = PropertyImageSerializer(many=True)
    reviews = PropertyReviewSerializer(source='propertyreview', many=True)  # Corrected to use the reverse relation
    review_data = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            'id', 'name', 'slug', 'description', 
            'price_usd', 'price_rwf', 'city', 'type', 'category',
            'bathroom', 'capacity', 'size', 'image', 'address',
            'created_by', 'created_at', 'updated_at', 
            'amenities', 'images', 'reviews', 'review_data'
        ]

    def get_review_data(self, obj):
        """
        Only returns review data if there are reviews.
        Otherwise, returns None.
        """
        reviews = obj.propertyreview.filter(status=True)  # Filter for active reviews
        if reviews.exists():
            avg_ratings = reviews.aggregate(
                avg_location=Avg('location'),
                avg_staff=Avg('staff'),
                avg_cleanliness=Avg('cleanliness'),
                avg_value_for_money=Avg('value_for_money'),
                avg_comfort=Avg('comfort'),
                avg_facilities=Avg('facilities'),
                avg_free_wifi=Avg('free_wifi')
            )

            # Calculate overall rating if there are reviews
            overall_rating = (
                avg_ratings['avg_location'] +
                avg_ratings['avg_staff'] +
                avg_ratings['avg_cleanliness'] +
                avg_ratings['avg_value_for_money'] +
                avg_ratings['avg_comfort'] +
                avg_ratings['avg_facilities'] +
                avg_ratings['avg_free_wifi']
            ) / 7 if all(value is not None for value in avg_ratings.values()) else 0

            return {
                'total_reviews': reviews.count(),
                'overall_rating': round(overall_rating, 2) if overall_rating else 0
            }
        else:
            return None  # No reviews, so return None
