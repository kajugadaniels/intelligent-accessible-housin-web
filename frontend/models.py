from django.db import models
from django.utils import timezone

class RentApplication(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
        ('Moved Out', 'Moved Out'),
    )

    user = models.ForeignKey('backend.User', on_delete=models.CASCADE, related_name='rent_applications')
    property = models.ForeignKey('backend.Property', on_delete=models.CASCADE, related_name='rent_applications')
    preferred_move_in_date = models.DateField(null=True, blank=True)
    rental_period_months = models.PositiveIntegerField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Application by {self.user.name} for {self.property.name}" 

    class Meta:
        verbose_name_plural = "Rent Applications"
