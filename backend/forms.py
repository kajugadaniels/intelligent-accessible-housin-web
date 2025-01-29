from django import forms
from backend.models import *
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password, get_password_validators

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
            try:
                user = User.objects.get(email=email)  # Get user by email
                user = authenticate(phone_number=user.phone_number, password=password)  # Authenticate using phone_number
                if not user:
                    raise forms.ValidationError(_('The email or password you entered is incorrect. Please try again.'))
                if not user.is_active:
                    raise forms.ValidationError(_('Your account is currently inactive. Please contact support for assistance.'))
                cleaned_data['user'] = user
            except User.DoesNotExist:
                raise forms.ValidationError(_('The email or password you entered is incorrect. Please try again.'))
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
        model = User  # Ensure you have imported the User model
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

class PasswordChangeForm(forms.Form):
    """
    Form for changing user password.
    """
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your current password',
            'required': 'required',
            'id': 'current_password',
        }),
        label=_('Current Password'),
        error_messages={
            'required': _('Please enter your current password.'),
        }
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your new password',
            'required': 'required',
            'id': 'new_password',
        }),
        label=_('New Password'),
        help_text=_('Your password must contain at least 8 characters, including a mix of letters, numbers, and symbols.'),
        error_messages={
            'required': _('Please enter a new password.'),
        }
    )
    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your new password',
            'required': 'required',
            'id': 'confirm_new_password',
        }),
        label=_('Confirm New Password'),
        error_messages={
            'required': _('Please confirm your new password.'),
        }
    )

    def __init__(self, user, *args, **kwargs):
        """
        Initialize the form with the current user.
        """
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError(_('Your current password was entered incorrectly. Please enter it again.'))
        return current_password

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        validate_password(new_password, self.user)
        return new_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')

        if new_password and confirm_new_password:
            if new_password != confirm_new_password:
                self.add_error('confirm_new_password', _('The new passwords do not match. Please enter them again.'))

        return cleaned_data
