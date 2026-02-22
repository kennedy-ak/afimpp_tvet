import os

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, RegistrationCode

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png'}

class CustomUserCreationForm(UserCreationForm):
    registration_code = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your registration code (e.g., AFIMPP-XXXXXX)',
            'style': 'text-transform: uppercase;'
        }),
        help_text='Enter the registration code provided to you when you called to express interest'
    )

    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email Address'
    }))

    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label=""
    )

    class Meta:
        model = User
        fields = ['registration_code', 'username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2', 'terms_accepted']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})

    def clean_registration_code(self):
        code = self.cleaned_data.get('registration_code', '').strip().upper()

        if not code:
            raise forms.ValidationError('Registration code is required.')

        try:
            reg_code = RegistrationCode.objects.get(code=code)
        except RegistrationCode.DoesNotExist:
            raise forms.ValidationError('Invalid registration code. Please contact us at 0557782728 to obtain a valid code.')

        if not reg_code.is_valid:
            if reg_code.is_used:
                raise forms.ValidationError('This registration code has already been used.')
            else:
                raise forms.ValidationError('This registration code has expired. Please contact us to get a new code.')

        return code


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'date_of_birth', 'address', 'profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/jpeg,image/png'}),
        }

    def clean_profile_picture(self):
        file = self.cleaned_data.get('profile_picture')
        if file and hasattr(file, 'size'):
            if file.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError("Profile picture must be less than 5MB")
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in ALLOWED_IMAGE_EXTENSIONS:
                raise forms.ValidationError(
                    f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_IMAGE_EXTENSIONS))}"
                )
        return file