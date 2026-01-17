from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'classification', 'section', 'category', 'file_size', 'created_at']
    list_filter = ['classification', 'section', 'category', 'created_at']
    search_fields = ['title', 'description', 'owner__username', 'tags']
    readonly_fields = ['created_at', 'updated_at', 'file_size', 'file_type']
    filter_horizontal = ['shared_with']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'file')
        }),
        ('Metadata', {
            'fields': ('owner', 'classification', 'section', 'category', 'tags')
        }),
        ('File Information', {
            'fields': ('file_size', 'file_type')
        }),
        ('Access Control', {
            'fields': ('shared_with',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
