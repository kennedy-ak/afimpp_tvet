import os

from django import forms
from .models import Enrollment, Payment, CourseRegistration

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
ALLOWED_DOCUMENT_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf'}


def _validate_file_extension(file, allowed_extensions):
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed_extensions:
        raise forms.ValidationError(
            f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(allowed_extensions))}"
        )

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = []  # User and course will be set in the view
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_method']
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
        }

    # Mobile Money specific fields
    mobile_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mobile Money Number',
            'id': 'mobile_number'
        })
    )

    mobile_network = forms.ChoiceField(
        choices=[
            ('', 'Select Network'),
            ('mtn', 'MTN Mobile Money'),
            ('vodafone', 'Vodafone Cash'),
            ('airteltigo', 'AirtelTigo Money'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'mobile_network'
        })
    )


class CourseRegistrationForm(forms.ModelForm):
    """Comprehensive course registration form"""
    class Meta:
        model = CourseRegistration
        fields = [
            'prefix', 'first_name', 'middle_name', 'last_name', 'date_of_birth', 'gender', 'nationality',
            'home_address', 'address_line_2', 'city', 'state_region', 'postal_code', 'phone_number', 'email_address',
            'highest_education', 'qualifications_certificates', 'institutions_attended',
            'current_occupation', 'years_of_experience', 'relevant_skills',
            'passport_photo', 'birth_certificate_or_id', 'education_certificates',
            'terms_conditions_accepted'
        ]
        widgets = {
            # Personal Information
            'prefix': forms.Select(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Middle Name (optional)'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nationality'}),
            
            # Contact Details
            'home_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Home Address'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 2 (optional)'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state_region': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State/Region'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'email_address': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            
            # Educational Background
            'highest_education': forms.Select(attrs={'class': 'form-control'}),
            'qualifications_certificates': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'List your qualifications/certificates'}),
            'institutions_attended': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'List institutions you have attended'}),
            
            # Work Experience
            'current_occupation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Current/Last Occupation (optional)'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Years of Experience (optional)'}),
            'relevant_skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Relevant Skills (optional)'}),
            
            # Documents
            'passport_photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/jpeg,image/png'}),
            'birth_certificate_or_id': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpeg,.jpg,.png'}),
            'education_certificates': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.jpeg,.jpg,.png'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make certain fields required
        self.fields['terms_conditions_accepted'].required = True
        self.fields['terms_conditions_accepted'].widget = forms.CheckboxInput(attrs={'class': 'form-check-input'})
        
    def clean_passport_photo(self):
        file = self.cleaned_data.get('passport_photo')
        if file:
            if file.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError("Passport photo must be less than 5MB")
            _validate_file_extension(file, ALLOWED_IMAGE_EXTENSIONS)
        return file

    def clean_birth_certificate_or_id(self):
        file = self.cleaned_data.get('birth_certificate_or_id')
        if file:
            if file.size > 10 * 1024 * 1024:  # 10MB
                raise forms.ValidationError("Birth certificate/ID must be less than 10MB")
            _validate_file_extension(file, ALLOWED_DOCUMENT_EXTENSIONS)
        return file

    def clean_education_certificates(self):
        file = self.cleaned_data.get('education_certificates')
        if file:
            if file.size > 10 * 1024 * 1024:  # 10MB
                raise forms.ValidationError("Education certificate must be less than 10MB")
            _validate_file_extension(file, ALLOWED_DOCUMENT_EXTENSIONS)
        return file