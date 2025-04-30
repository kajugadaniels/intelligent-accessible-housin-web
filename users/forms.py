from django import forms
from users.models import *
from django.utils.translation import gettext_lazy as _

class RentApplicationForm(forms.ModelForm):
    class Meta:
        model = RentApplication
        fields = [
            'preferred_move_in_date', 'rental_period_months',
            'id_number_image', 'applicant_image',
            'has_children', 'number_of_children',
            'has_pet', 'pet_details',
            'has_disability', 'disability_details',
            'marital_status', 'employment_status', 'monthly_income',
            'references', 'message'
        ]
        widgets = {
            'preferred_move_in_date': forms.DateInput(attrs={'type':'date','class':'form-control'}),
            'rental_period_months': forms.NumberInput(attrs={'class':'form-control'}),
            'id_number_image': forms.ClearableFileInput(attrs={'class':'form-control'}),
            'applicant_image': forms.ClearableFileInput(attrs={'class':'form-control'}),
            'has_children': forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'number_of_children': forms.NumberInput(attrs={'class':'form-control'}),
            'has_pet': forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'pet_details': forms.Textarea(attrs={'class':'form-control','rows':2}),
            'has_disability': forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'disability_details': forms.Textarea(attrs={'class':'form-control','rows':2}),
            'marital_status': forms.Select(attrs={'class':'form-control'}),
            'employment_status': forms.Select(attrs={'class':'form-control'}),
            'monthly_income': forms.NumberInput(attrs={'class':'form-control'}),
            'references': forms.Textarea(attrs={'class':'form-control','rows':3}),
            'message': forms.Textarea(attrs={'class':'form-control','rows':3}),
        }
        labels = {
            'preferred_move_in_date': _('Preferred Move-in Date'),
            'rental_period_months': _('Rental Period (months)'),
            'id_number_image': _('ID Document Image'),
            'applicant_image': _('Your Photo'),
            'has_children': _('Do you have children?'),
            'number_of_children': _('Number of Children'),
            'has_pet': _('Do you have pets?'),
            'pet_details': _('Pet Details'),
            'has_disability': _('Do you have any disability?'),
            'disability_details': _('Disability Details'),
            'marital_status': _('Marital Status'),
            'employment_status': _('Employment Status'),
            'monthly_income': _('Monthly Income (USD)'),
            'references': _('References'),
            'message': _('Additional Message'),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('has_children') and not cleaned.get('number_of_children'):
            self.add_error('number_of_children', _('Please specify number of children.'))
        if cleaned.get('has_pet') and not cleaned.get('pet_details'):
            self.add_error('pet_details', _('Please provide details about your pet(s).'))
        if cleaned.get('has_disability') and not cleaned.get('disability_details'):
            self.add_error('disability_details', _('Please provide details of your disability.'))
        return cleaned