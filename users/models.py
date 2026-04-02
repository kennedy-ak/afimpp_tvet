from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True, max_length=500)
    address = models.TextField(blank=True, null=True)

    # Student specific fields
    is_student = models.BooleanField(default=False)
    student_id = models.CharField(max_length=20, blank=True, null=True, unique=True)

    # Terms acceptance
    terms_accepted = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class RegistrationCode(models.Model):
    """Registration codes given to prospective students who call to express interest"""
    code = models.CharField(max_length=20, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    used_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='registration_code_used')
    used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Optional expiration date")

    # Contact information of person who requested the code
    contact_name = models.CharField(max_length=200, blank=True, null=True)
    contact_phone = models.CharField(max_length=15, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True, help_text="Admin notes about this registration code")

    def __str__(self):
        return f"{self.code} - {'Used' if self.is_used else 'Available'}"

    @property
    def is_valid(self):
        """Check if code is valid (not used and not expired)"""
        from django.utils import timezone
        if self.is_used:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True

    class Meta:
        verbose_name = 'Registration Code'
        verbose_name_plural = 'Registration Codes'
        ordering = ['-created_at']