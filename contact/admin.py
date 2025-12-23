from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    list_editable = ['is_read']
    date_hierarchy = 'created_at'
    readonly_fields = ['name', 'email', 'subject', 'message', 'created_at']
    
    def has_add_permission(self, request):
        # Disable adding messages from admin
        return False