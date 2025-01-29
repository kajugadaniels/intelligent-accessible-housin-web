import os
from django.db import models
from backend.managers import *
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
