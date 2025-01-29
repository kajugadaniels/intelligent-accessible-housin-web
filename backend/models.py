import os
from django.db import models
from backend.managers import *
from django.db.models import Avg
from django.utils import timezone
from django.utils.text import slugify
from imagekit.processors import ResizeToFill
from imagekit.models import ProcessedImageField
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Permission

def user_image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    return f'profile_images/user_{slugify(instance.slug)}_{instance.phone_number}{file_extension}'

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Director', 'Director'),
        ('Teacher', 'Teacher'),
        ('Student', 'Student'),
    )

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    image = ProcessedImageField(
        upload_to=user_image_path,
        processors=[ResizeToFill(720, 720)],
        format='JPEG',
        options={'quality': 90},
        null=True,
        blank=True,
    )
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    slug = models.SlugField(unique=True, max_length=255, null=True, blank=True)

    added_by = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='added_users')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone_number']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # Handle image deletion and permissions assignment
        try:
            orig = User.objects.get(pk=self.pk)
        except User.DoesNotExist:
            orig = None

        if orig:
            # Handle image deletion if image has changed
            if orig.image and self.image != orig.image:
                orig.image.delete(save=False)
            # Handle role change
            if orig.role != self.role:
                self.set_permissions()
            # Handle name change to update slug
            if orig.name != self.name:
                self.slug = self.generate_unique_slug()
        else:
            # New instance; generate slug if not provided
            if not self.slug:
                self.slug = self.generate_unique_slug()

        super(User, self).save(*args, **kwargs)

        # Assign permissions based on role after saving
        self.set_permissions()

    def set_permissions(self):
        if self.role:
            self.user_permissions.set(self.role.permissions.all())
        else:
            self.user_permissions.clear()

    def generate_unique_slug(self):
        """
        Generates a unique slug from the user's name.
        If the slug already exists, appends a numerical suffix to make it unique.
        """
        base_slug = slugify(self.name)
        slug = base_slug
        counter = 1
        while User.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    def get_full_name(self):
        """
        Returns the user's full name.
        """
        return self.name

    def get_short_name(self):
        """
        Returns the user's short name.
        """
        return self.name.split()[0] if self.name else self.email

class Amenity(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Amenities"

def property_image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    return f'properties/property_{slugify(instance.name)}_{instance.created_at}{file_extension}'

class Property(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()

    # Separate fields for price in USD and RWF
    price_usd = models.IntegerField(null=True, blank=True)
    price_rwf = models.IntegerField(null=True, blank=True)

    capacity = models.IntegerField()
    size = models.CharField(max_length=255, null=True, blank=True)
    image = ProcessedImageField(
        upload_to=property_image_path,
        format='JPEG',
        options={'quality': 90},
        null=True,
        blank=True,
    )
    amenities = models.ManyToManyField('Amenity', blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        base_slug = slugify(self.name)
        unique_slug = base_slug
        num = 1
        while Property.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{base_slug}-{num}"
            num += 1
        return unique_slug

    # Method to retrieve review data (total reviews and average ratings)
    def get_review_data(self):
        reviews = self.propertyreview.filter(status=True)  # Filter reviews with status=True
        total_reviews = reviews.count()
        
        # Aggregate average ratings
        avg_ratings = reviews.aggregate(
            avg_location=Avg('location'),
            avg_staff=Avg('staff'),
            avg_cleanliness=Avg('cleanliness'),
            avg_value_for_money=Avg('value_for_money'),
            avg_comfort=Avg('comfort'),
            avg_facilities=Avg('facilities'),
            avg_free_wifi=Avg('free_wifi')
        )

        # Calculate overall rating
        if total_reviews > 0:
            overall_rating = (
                avg_ratings['avg_location'] +
                avg_ratings['avg_staff'] +
                avg_ratings['avg_cleanliness'] +
                avg_ratings['avg_value_for_money'] +
                avg_ratings['avg_comfort'] +
                avg_ratings['avg_facilities'] +
                avg_ratings['avg_free_wifi']
            ) / 7
        else:
            overall_rating = 0  # Default to 0 if no reviews

        return {
            'total_reviews': total_reviews,
            'overall_rating': round(overall_rating, 2) if overall_rating else 0
        }

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Properties"

def property_add_on_image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    random_number = random.randint(1000, 9999)
    return f'properties/add_on/{random_number}_{instance.created_at}{file_extension}'

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, related_name='images', on_delete=models.CASCADE)
    image = ProcessedImageField(
        upload_to=property_add_on_image_path,
        # processors=[ResizeToFill(1340, 894)],
        format='JPEG',
        options={'quality': 90},
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.property.name} - {self.created_at}"

    class Meta:
        verbose_name_plural = "Property Images"

class PropertyReview(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    location = models.IntegerField(default=5, null=True, blank=True)
    staff = models.IntegerField(default=5, null=True, blank=True)
    cleanliness = models.IntegerField(default=5, null=True, blank=True)
    value_for_money = models.IntegerField(default=5, null=True, blank=True)
    comfort = models.IntegerField(default=5, null=True, blank=True)
    facilities = models.IntegerField(default=5, null=True, blank=True)
    free_wifi = models.IntegerField(default=5, null=True, blank=True)
    status = models.BooleanField(default=1, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Review by {self.name} for {self.property.name}"

    class Meta:
        verbose_name_plural = "Property Reviews"