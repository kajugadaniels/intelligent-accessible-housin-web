from django import forms
from backend.models import *
from users.models import *
from django.utils.translation import gettext_lazy as _

class RentApplicationForm(forms.ModelForm):
    """
    Form for creating a rent application.
    """
    class Meta:
        model = RentApplication
        fields = ['preferred_move_in_date', 'rental_period_months', 'message']
        widgets = {
            'preferred_move_in_date': forms.DateInput(attrs={
                'placeholder': 'Preferred move-in date',
                'type': 'date',
                'required': 'required',
                'class': 'form-control'
            }),
            'rental_period_months': forms.NumberInput(attrs={
                'placeholder': 'Rental period in months',
                'required': 'required',
                'class': 'form-control'
            }),
            'message': forms.Textarea(attrs={
                'placeholder': 'Additional message (optional)',
                'class': 'form-control'
            }),
        }
        labels = {
            'preferred_move_in_date': _('Preferred Move-in Date'),
            'rental_period_months': _('Rental Period (in months)'),
            'message': _('Message'),
        }