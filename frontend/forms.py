from django import forms
from backend.models import *
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password

class LoginForm(forms.Form):
    email = forms.EmailField(
        max_length=255,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'required': 'required',
            'id': 'emailaddress',
        }),
        label=_('Email Address'),
        error_messages={
            'required': _('Please enter your email address.'),
            'invalid': _('Enter a valid email address.'),
        }
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'required': 'required',
            'id': 'password',
        }),
        label=_('Password'),
        error_messages={
            'required': _('Please enter your password.'),
        }
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError(_('The email or password you entered is incorrect. Please try again.'))
            if not user.is_active:
                raise forms.ValidationError(_('Your account is currently inactive. Please contact support for assistance.'))
            cleaned_data['user'] = user
        else:
            if not email:
                self.add_error('email', _('Email address is required.'))
            if not password:
                self.add_error('password', _('Password is required.'))
        return cleaned_data

class UserProfileForm(forms.ModelForm):
    """
    Form for updating user profile information.
    """
    class Meta:
        model = User
        fields = ['name', 'email', 'phone_number', 'image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name',
                'required': 'required',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address',
                'required': 'required',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number',
                'required': 'required',
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
        }
        labels = {
            'name': _('Full Name'),
            'email': _('Email Address'),
            'phone_number': _('Phone Number'),
            'image': _('Profile Image'),
        }
        error_messages = {
            'name': {
                'required': _('Please enter your full name.'),
                'max_length': _('Name cannot exceed 255 characters.'),
            },
            'email': {
                'required': _('Please enter your email address.'),
                'invalid': _('Enter a valid email address.'),
                'unique': _('This email address is already in use.'),
            },
            'phone_number': {
                'required': _('Please enter your phone number.'),
                'unique': _('This phone number is already in use.'),
                'max_length': _('Phone number cannot exceed 15 characters.'),
            },
            'image': {
                'invalid': _('Please upload a valid image file.'),
            },
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(_('This email address is already in use. Please use a different one.'))
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if User.objects.filter(phone_number=phone_number).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(_('This phone number is already in use. Please use a different one.'))
        return phone_number