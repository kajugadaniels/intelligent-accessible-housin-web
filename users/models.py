from backend.models import *
from django.db import models
from django.utils import timezone
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

class RentApplication(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
        ('Moved Out', 'Moved Out'),
    )

    MARITAL_STATUS_CHOICES = (
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Divorced', 'Divorced'),
        ('Widowed', 'Widowed'),
    )

    EMPLOYMENT_STATUS_CHOICES = (
        ('Employed', 'Employed'),
        ('Unemployed', 'Unemployed'),
        ('Student', 'Student'),
        ('Retired', 'Retired'),
    )

    user = models.ForeignKey('backend.User', on_delete=models.CASCADE, related_name='rent_applications')
    property = models.ForeignKey('backend.Property', on_delete=models.CASCADE, related_name='rent_applications')
    preferred_move_in_date = models.DateField(null=True, blank=True)
    rental_period_months = models.PositiveIntegerField(null=True, blank=True)

    # New fields
    id_number_image = ProcessedImageField(
        upload_to='id_numbers/',
        processors=[ResizeToFill(800, 600)],
        format='JPEG',
        options={'quality': 90},
        null=True,
        blank=True,
        help_text="Upload a clear photo of your ID."
    )
    applicant_image = ProcessedImageField(
        upload_to='applicant_images/',
        processors=[ResizeToFill(720, 720)],
        format='JPEG',
        options={'quality': 90},
        null=True,
        blank=True,
        help_text="Upload a recent portrait photo."
    )
    has_children = models.BooleanField(default=False)
    number_of_children = models.PositiveIntegerField(null=True, blank=True)

    has_pet = models.BooleanField(default=False)
    pet_details = models.TextField(null=True, blank=True)

    has_disability = models.BooleanField(default=False)
    disability_details = models.TextField(null=True, blank=True)

    marital_status = models.CharField(
        max_length=20,
        choices=MARITAL_STATUS_CHOICES,
        default='Single'
    )
    employment_status = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_STATUS_CHOICES,
        default='Employed'
    )
    monthly_income = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Your gross monthly income in USD."
    )
    references = models.TextField(null=True, blank=True, help_text="Please provide 2 references and their contacts.")

    message = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Application by {self.user.name} for {self.property.name}"

    class Meta:
        verbose_name_plural = "Rent Applications"