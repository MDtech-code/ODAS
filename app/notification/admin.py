from django.contrib import admin
from .models import Notification
from django.contrib.contenttypes.admin import GenericStackedInline


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for the Notification model.
    """
    list_display = ('user', 'notification_type', 'is_read', 'created_at', 'updated_at')
    list_filter = ('notification_type', 'is_read', 'created_at', 'updated_at')
    search_fields = ('user__username', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        """
        Custom action to mark notifications as read.
        """
        queryset.update(is_read=True)
        self.message_user(request, "Selected notifications have been marked as read.")
    mark_as_read.short_description = "Mark selected notifications as read"

    def mark_as_unread(self, request, queryset):
        """
        Custom action to mark notifications as unread.
        """
        queryset.update(is_read=False)
        self.message_user(request, "Selected notifications have been marked as unread.")
    mark_as_unread.short_description = "Mark selected notifications as unread"
