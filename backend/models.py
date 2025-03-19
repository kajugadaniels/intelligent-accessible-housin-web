import os
import random
from django.db import models
from frontend.models import *
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
        ('User', 'User'),
        ('House Provider', 'House Provider'),
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
    REQUIRED_FIELDS = ['name', 'phone_number', 'role']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # Handle image deletion and update slug on name change
        try:
            orig = User.objects.get(pk=self.pk)
        except User.DoesNotExist:
            orig = None

        if orig:
            if orig.image and self.image != orig.image:
                orig.image.delete(save=False)
            if orig.role != self.role:
                self.setPermissions()
            if orig.name != self.name:
                self.slug = self.generate_unique_slug()
        else:
            if not self.slug:
                self.slug = self.generate_unique_slug()

        super(User, self).save(*args, **kwargs)
        self.setPermissions()

    def setPermissions(self):
        """
        Since role does not have associated permissions,
        simply clear any assigned user permissions.
        """
        self.user_permissions.clear()

    def generate_unique_slug(self):
        base_slug = slugify(self.name)
        slug = base_slug
        counter = 1
        while User.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name.split()[0] if self.name else self.email

class Amenity(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='amenities_created')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Amenities"

def category_image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    return f'categories/category_{slugify(instance.name)}{file_extension}'

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = ProcessedImageField(
        upload_to=category_image_path,
        format='JPEG',
        processors=[ResizeToFill(500, 500)],
        options={'quality': 90},
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

def property_image_path(instance, filename):
    base_filename, file_extension = os.path.splitext(filename)
    return f'properties/property_{slugify(instance.name)}_{instance.created_at}{file_extension}'

class Property(models.Model):
    CITY_CHOICES = (
        ('Rebero', 'Rebero'),
        ('Gacuriro', 'Gacuriro'),
        ('Nyamirambo', 'Nyamirambo'),
        ('Nyamata', 'Nyamata'),
        ('Gisenyi', 'Gisenyi'),
        ('Kacyiru', 'Kacyiru'),
        ('Kabeza', 'Kabeza'),
        ('Kicukiro', 'Kicukiro'),
    )
    TYPE_CHOICES = (
        ('Featured', 'Featured'),
        ('Rent', 'Rent'),
        ('Sale', 'Sale'),
    )
    CATEGORY_CHOICES = (
        ('House', 'House'),
        ('Apartment', 'Apartment'),
        ('Villa', 'Villa'),
        ('Office', 'Office'),
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()

    # Separate fields for price in USD and RWF
    price_usd = models.IntegerField(null=True, blank=True)
    price_rwf = models.IntegerField(null=True, blank=True)

    city = models.CharField(max_length=30, choices=CITY_CHOICES, null=True, blank=True)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='properties')
    bathroom = models.IntegerField(null=True, blank=True)
    capacity = models.IntegerField(null=True, blank=True)
    size = models.CharField(max_length=255, null=True, blank=True)
    image = ProcessedImageField(
        upload_to=property_image_path,
        format='JPEG',
        processors=[ResizeToFill(1340, 894)],
        options={'quality': 90},
        null=True,
        blank=True,
    )
    amenities = models.ManyToManyField('Amenity', blank=True)
    address = models.CharField(max_length=255, default='Kigali Rwanda')

    nearby_hospital = models.CharField(max_length=255, null=True, blank=True, help_text="Nearby hospital name or details")
    nearby_school = models.CharField(max_length=255, null=True, blank=True, help_text="Nearby school name or details")
    nearby_market = models.CharField(max_length=255, null=True, blank=True, help_text="Nearby market name or details")
    nearby_transport = models.CharField(max_length=255, null=True, blank=True, help_text="Nearby transport options or station")
    nearby_park = models.CharField(max_length=255, null=True, blank=True, help_text="Nearby park or recreational area")
    nearby_gym = models.CharField(max_length=255, null=True, blank=True, help_text="Nearby gym or fitness center")

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='properties_created')
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
        processors=[ResizeToFill(1340, 894)],
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
    property = models.ForeignKey(
        Property,
        related_name='propertyreview',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
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

class Contract(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Terminated', 'Terminated'),
        ('Expired', 'Expired'),
        ('Pending', 'Pending'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
        ('Overdue', 'Overdue'),
    )

    rent_application = models.OneToOneField(RentApplication, on_delete=models.CASCADE, related_name='contract', null=True, blank=True)

    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tenant_contracts')
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agent_contracts')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='contracts')

    contract_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    start_date = models.DateField(default=timezone.now, help_text="The start date of the rental contract.")
    end_date = models.DateField(help_text="The end date of the rental contract.")
    rental_period_months = models.PositiveIntegerField(help_text="The length of the rental period in months.")
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Monthly rent amount.")
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, help_text="Security deposit amount.")
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='Pending', help_text="The current payment status of the contract.")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending', help_text="The current status of the contract (e.g., Active, Terminated).")
    signed_date = models.DateField(null=True, blank=True, help_text="The date when both parties signed the contract.")
    
    additional_terms = models.TextField(null=True, blank=True, help_text="Any additional terms or agreements in the contract.")
    rent_due_date = models.DateField(help_text="The date when the rent is due each month.")
    payment_method = models.CharField(max_length=100, blank=True, null=True, help_text="The agreed method of payment (e.g., Bank Transfer, Cash).")
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Contract #{self.contract_number} between {self.tenant.name} and {self.agent.name} for {self.property.name}"

    class Meta:
        verbose_name_plural = "Contracts"
        ordering = ['start_date']
