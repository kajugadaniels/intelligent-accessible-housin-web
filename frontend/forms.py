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