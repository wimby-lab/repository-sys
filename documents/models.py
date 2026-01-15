from django.db import models
from django.conf import settings
import os


def document_upload_path(instance, filename):
    """Generate upload path for documents"""
    return f'documents/{instance.classification}/{instance.owner.username}/{filename}'


class Document(models.Model):
    """Document model with metadata and access control"""
    CLASSIFICATION_CHOICES = [
        ('PUBLIC', 'Public'),
        ('INTERNAL', 'Internal'),
        ('CONFIDENTIAL', 'Confidential'),
        ('RESTRICTED', 'Restricted'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to=document_upload_path)
    file_size = models.IntegerField(default=0)  # in bytes
    file_type = models.CharField(max_length=100)
    
    # Metadata
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_documents'
    )
    classification = models.CharField(
        max_length=20,
        choices=CLASSIFICATION_CHOICES,
        default='INTERNAL'
    )
    category = models.CharField(max_length=100, blank=True)
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Access control
    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='shared_documents'
    )
    
    def __str__(self):
        return self.title
    
    def get_tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    def get_file_extension(self):
        """Get file extension"""
        return os.path.splitext(self.file.name)[1].lower()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'classification']),
            models.Index(fields=['created_at']),
            models.Index(fields=['category']),
        ]

