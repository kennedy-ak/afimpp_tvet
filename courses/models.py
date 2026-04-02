from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()

class Course(models.Model):
    LEVEL_CHOICES = [
        ('3', 'Level 3'),
        ('4', 'Level 4'),
        ('5', 'Level 5'),
    ]
    
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    short_title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField()
    level = models.CharField(max_length=1, choices=LEVEL_CHOICES)
    duration_months = models.IntegerField(help_text="Duration in months")
    image = models.ImageField(upload_to='courses/', blank=True, null=True, max_length=500)
    
    # Course details
    overview = models.TextField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True, help_text="Enter each requirement on a new line")
    learning_mode = models.CharField(max_length=200, default="Blended Learning (Online + Face-to-Face)")
    
    # Pricing
    from decimal import Decimal
    
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    
    # Status
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'


class CourseModule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    class Meta:
        ordering = ['order']


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    enrolled_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
    
    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-enrolled_at']


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Credit/Debit Card'),
        ('mobile_money', 'Mobile Money'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.enrollment.user.username} - GHS {self.amount}"
    
    class Meta:
        ordering = ['-created_at']


class CourseRegistration(models.Model):
    """Comprehensive registration information for course enrollment"""
    PREFIX_CHOICES = [
        ('Mr', 'Mr'),
        ('Mrs', 'Mrs'),
        ('Ms', 'Ms'),
        ('Dr', 'Dr'),
        ('Prof', 'Prof'),
        ('Engr', 'Engr'),
    ]
    
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    
    EDUCATION_CHOICES = [
        ('Primary', 'Primary'),
        ('JHS', 'JHS (Junior High School)'),
        ('SHS', 'SHS (Senior High School)'),
        ('Diploma', 'Diploma'),
        ('Certificate', 'Certificate'),
        ('Associate', 'Associate Degree'),
        ('Bachelor', "Bachelor's Degree"),
        ('Master', "Master's Degree"),
        ('PhD', 'PhD'),
        ('Other', 'Other'),
    ]
    
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='registration')
    
    # Personal Information
    prefix = models.CharField(max_length=10, choices=PREFIX_CHOICES)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    nationality = models.CharField(max_length=100)
    
    # Contact Details
    home_address = models.TextField()
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state_region = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=15)
    email_address = models.EmailField()
    
    # Educational Background
    highest_education = models.CharField(max_length=50, choices=EDUCATION_CHOICES)
    qualifications_certificates = models.TextField(help_text="List your qualifications/certificates")
    institutions_attended = models.TextField(help_text="List institutions you've attended")
    
    # Work Experience
    current_occupation = models.CharField(max_length=200, blank=True, null=True)
    years_of_experience = models.IntegerField(blank=True, null=True)
    relevant_skills = models.TextField(blank=True, null=True)
    
    # Required Documents
    passport_photo = models.FileField(upload_to='documents/passport_photos/', help_text="JPEG/PNG, max 5MB")
    birth_certificate_or_id = models.FileField(upload_to='documents/birth_certificates/', help_text="PDF/JPEG/PNG, max 10MB")
    education_certificates = models.FileField(upload_to='documents/education_certificates/', help_text="PDF/JPEG/PNG, max 10MB each, multiple files allowed")
    
    # Agreement
    terms_conditions_accepted = models.BooleanField()
    registration_fee_paid = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Registration for {self.enrollment.user.username} - {self.enrollment.course.title}"
    
    @property
    def full_name(self):
        """Return full name including prefix and middle name"""
        parts = [self.prefix, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return " ".join(parts)
    
    class Meta:
        verbose_name = 'Course Registration'
        verbose_name_plural = 'Course Registrations'