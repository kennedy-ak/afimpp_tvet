from django.contrib import admin
from .models import ChatConversation, ChatMessage


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ['role', 'content', 'created_at', 'context_used']
    can_delete = False


@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'ip_address', 'created_at', 'updated_at', 'message_count']
    list_filter = ['created_at', 'user']
    search_fields = ['session_id', 'user__username', 'user__email', 'ip_address']
    readonly_fields = ['session_id', 'created_at', 'updated_at', 'ip_address', 'user_agent']
    inlines = [ChatMessageInline]

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'

    fieldsets = (
        ('Conversation Info', {
            'fields': ('session_id', 'user', 'ip_address', 'user_agent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'role', 'content_preview', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['content', 'conversation__session_id']
    readonly_fields = ['created_at']

    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'

    fieldsets = (
        ('Message Info', {
            'fields': ('conversation', 'role', 'content')
        }),
        ('RAG Context', {
            'fields': ('context_used',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )
