from django.contrib import admin
from .models import Course, CourseModule, Enrollment, Payment

class CourseModuleInline(admin.TabularInline):
    model = CourseModule
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'level', 'duration_months', 'price', 'is_active', 'featured', 'created_at']
    list_filter = ['level', 'is_active', 'featured', 'created_at']
    search_fields = ['title', 'short_title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_active', 'featured']
    inlines = [CourseModuleInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'short_title', 'level', 'duration_months', 'image')
        }),
        ('Course Details', {
            'fields': ('description', 'overview', 'requirements', 'learning_mode')
        }),
        ('Pricing & Status', {
            'fields': ('price', 'is_active', 'featured')
        }),
    )

@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    search_fields = ['title', 'description']
    list_editable = ['order']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'status', 'payment_status', 'enrolled_at']
    list_filter = ['status', 'payment_status', 'enrolled_at']
    search_fields = ['user__username', 'user__email', 'course__title']
    list_editable = ['status', 'payment_status']
    date_hierarchy = 'enrolled_at'
    
    fieldsets = (
        ('Enrollment Information', {
            'fields': ('user', 'course')
        }),
        ('Status', {
            'fields': ('status', 'payment_status')
        }),
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'amount', 'payment_method', 'transaction_id', 'status', 'created_at']
    list_filter = ['payment_method', 'status', 'created_at']
    search_fields = ['transaction_id', 'enrollment__user__username', 'enrollment__user__email']
    readonly_fields = ['transaction_id', 'created_at']
    date_hierarchy = 'created_at'