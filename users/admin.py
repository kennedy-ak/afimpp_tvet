from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, RegistrationCode
import secrets
import string

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_student', 'student_id', 'is_staff']
    list_filter = ['is_student', 'is_staff', 'is_superuser', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'student_id']

    fieldsets = list(BaseUserAdmin.fieldsets) + [
        ('Additional Info', {
            'fields': ('phone', 'date_of_birth', 'profile_picture', 'address', 'is_student', 'student_id')
        }),
    ]

    add_fieldsets = list(BaseUserAdmin.add_fieldsets) + [
        ('Additional Info', {
            'fields': ('email', 'phone', 'is_student')
        }),
    ]


@admin.register(RegistrationCode)
class RegistrationCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'contact_name', 'contact_phone', 'is_used', 'used_by', 'created_at', 'expires_at']
    list_filter = ['is_used', 'created_at']
    search_fields = ['code', 'contact_name', 'contact_phone', 'contact_email']
    readonly_fields = ['created_at', 'used_at', 'used_by']

    fieldsets = [
        ('Code Information', {
            'fields': ('code', 'is_used', 'expires_at')
        }),
        ('Contact Information', {
            'fields': ('contact_name', 'contact_phone', 'contact_email', 'notes')
        }),
        ('Usage Information', {
            'fields': ('used_by', 'used_at', 'created_at')
        }),
    ]

    actions = ['generate_codes']

    def generate_codes(self, request, queryset):
        """Generate a new registration code"""
        # Generate 5 random codes
        codes_generated = 0
        for _ in range(5):
            # Generate a unique code like AFIMPP-XXXXX
            code = 'AFIMPP-' + ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            # Check if code already exists
            if not RegistrationCode.objects.filter(code=code).exists():
                RegistrationCode.objects.create(code=code)
                codes_generated += 1

        self.message_user(request, f'{codes_generated} registration codes generated successfully.')

    generate_codes.short_description = 'Generate 5 new registration codes'