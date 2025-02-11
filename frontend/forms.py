from django import forms
from backend.models import *
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password

class LoginForm(forms.Form):
    email = forms.EmailField(
        max_length=255,
        widget=forms.EmailInput(attrs={
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
                'placeholder': 'Enter your full name',
                'required': 'required',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter your email address',
                'required': 'required',
            }),
            'phone_number': forms.TextInput(attrs={
                'placeholder': 'Enter your phone number',
                'required': 'required',
            }),
            'image': forms.ClearableFileInput(attrs={
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

class RegisterForm(forms.ModelForm):
    """
    Form for registering a new user with role 'User' by default.
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter Password',
            'required': 'required',
            'id': 'password',
        }),
        label=_('Password'),
        error_messages={'required': _('Please enter a password.')},
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password',
            'required': 'required',
            'id': 'confirm_password',
        }),
        label=_('Confirm Password'),
        error_messages={'required': _('Please confirm your password.')},
    )

    class Meta:
        model = User
        fields = ['name', 'email', 'phone_number']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Enter your name',
                'required': 'required',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter your email address',
                'required': 'required',
            }),
            'phone_number': forms.TextInput(attrs={
                'placeholder': 'Enter your phone number',
                'required': 'required',
            }),
        }
        labels = {
            'name': _('Name'),
            'email': _('Email Address'),
            'phone_number': _('Phone Number'),
        }
        error_messages = {
            'name': {'required': _('Please enter your name.')},
            'email': {
                'required': _('Please enter your email address.'),
                'invalid': _('Enter a valid email address.'),
            },
            'phone_number': {'required': _('Please enter your phone number.')},
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                self.add_error('confirm_password', _('The passwords do not match.'))
            try:
                validate_password(password)
            except forms.ValidationError as error:
                self.add_error('password', error)
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('This email address is already in use.'))
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if User.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError(_('This phone number is already in use.'))
        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        # Set the default role to 'User'
        user.role = "User"
        if commit:
            user.save()
        return user