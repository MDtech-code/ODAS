from django.contrib import admin
from .models import Article, Comment


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for the Article model.
    """
    list_display = ('title', 'doctor', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'doctor__user__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for the Comment model.
    """
    list_display = ('article', 'patient', 'is_approved', 'created_at', 'updated_at')
    list_filter = ('is_approved', 'created_at', 'updated_at')
    search_fields = ('article__title', 'patient__user__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    
