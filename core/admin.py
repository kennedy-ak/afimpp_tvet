from django.contrib import admin
from .models import GalleryImage, Newsletter, SiteSettings

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active', 'uploaded_at']
    list_filter = ['is_active', 'uploaded_at']
    search_fields = ['title', 'description']
    list_editable = ['order', 'is_active']
    date_hierarchy = 'uploaded_at'

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']
    list_editable = ['is_active']
    date_hierarchy = 'subscribed_at'

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'site_email', 'site_phone']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('site_name', 'site_email', 'site_phone', 'site_address')
        }),
        ('Hero Section', {
            'fields': ('hero_subtitle', 'hero_title', 'hero_description')
        }),
        ('About Section', {
            'fields': ('about_title', 'about_description')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'linkedin_url', 'instagram_url')
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion
        return False