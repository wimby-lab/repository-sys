from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    """Role model for RBAC"""
    ADMIN = 'ADMIN'
    MANAGER = 'MANAGER'
    USER = 'USER'
    
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (MANAGER, 'Manager'),
        (USER, 'User'),
    ]
    
    name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.get_name_display()
    
    class Meta:
        ordering = ['name']


class User(AbstractUser):
    """Extended User model with role support"""
    role = models.ForeignKey(
        Role, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='users'
    )
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username
    
    @property
    def is_admin(self):
        return self.role and self.role.name == Role.ADMIN
    
    @property
    def is_manager(self):
        return self.role and self.role.name == Role.MANAGER
    
    @property
    def is_regular_user(self):
        return self.role and self.role.name == Role.USER
    
    class Meta:
        ordering = ['-created_at']


class AuditLog(models.Model):
    """Audit log for tracking sensitive actions"""
    ACTION_CHOICES = [
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('REGISTER', 'Register'),
        ('PASSWORD_RESET', 'Password Reset'),
        ('ROLE_CHANGE', 'Role Change'),
        ('DOCUMENT_UPLOAD', 'Document Upload'),
        ('DOCUMENT_VIEW', 'Document View'),
        ('DOCUMENT_DOWNLOAD', 'Document Download'),
        ('DOCUMENT_UPDATE', 'Document Update'),
        ('DOCUMENT_DELETE', 'Document Delete'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"
    
    class Meta:
        ordering = ['-timestamp']

