from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    """Role model for RBAC"""
    ADVISER = 'ADVISER'
    PRESIDENT = 'PRESIDENT'
    VICE_PRESIDENT = 'VICE_PRESIDENT'
    SECRETARY = 'SECRETARY'
    ASSISTANT_SECRETARY = 'ASSISTANT_SECRETARY'
    TREASURER = 'TREASURER'
    ASSISTANT_TREASURER = 'ASSISTANT_TREASURER'
    AUDITOR = 'AUDITOR'
    BUSINESS_MANAGER = 'BUSINESS_MANAGER'
    PIO = 'PIO'
    ATHLETIC_MANAGER_MALE = 'ATHLETIC_MANAGER_MALE'
    ATHLETIC_MANAGER_FEMALE = 'ATHLETIC_MANAGER_FEMALE'
    BSCS_1A_REPRESENTATIVE = 'BSCS_1A_REPRESENTATIVE'
    BSCS_1B_REPRESENTATIVE = 'BSCS_1B_REPRESENTATIVE'
    BSCS_2A_REPRESENTATIVE = 'BSCS_2A_REPRESENTATIVE'
    BSCS_2B_REPRESENTATIVE = 'BSCS_2B_REPRESENTATIVE'
    BSCS_3A_REPRESENTATIVE = 'BSCS_3A_REPRESENTATIVE'
    BSCS_3B_REPRESENTATIVE = 'BSCS_3B_REPRESENTATIVE'
    BSCS_4A_REPRESENTATIVE = 'BSCS_4A_REPRESENTATIVE'
    BSCS_4B_REPRESENTATIVE = 'BSCS_4B_REPRESENTATIVE'
    
    ROLE_CHOICES = [
        (ADVISER, 'Adviser'),
        (PRESIDENT, 'President'),
        (VICE_PRESIDENT, 'Vice President'),
        (SECRETARY, 'Secretary'),
        (ASSISTANT_SECRETARY, 'Assistant Secretary'),
        (TREASURER, 'Treasurer'),
        (ASSISTANT_TREASURER, 'Assistant Treasurer'),
        (AUDITOR, 'Auditor'),
        (BUSINESS_MANAGER, 'Business Manager'),
        (PIO, 'PIO'),
        (ATHLETIC_MANAGER_MALE, 'Athletic Manager (Male)'),
        (ATHLETIC_MANAGER_FEMALE, 'Athletic Manager (Female)'),
        (BSCS_1A_REPRESENTATIVE, 'BSCS 1A Representative'),
        (BSCS_1B_REPRESENTATIVE, 'BSCS 1B Representative'),
        (BSCS_2A_REPRESENTATIVE, 'BSCS 2A Representative'),
        (BSCS_2B_REPRESENTATIVE, 'BSCS 2B Representative'),
        (BSCS_3A_REPRESENTATIVE, 'BSCS 3A Representative'),
        (BSCS_3B_REPRESENTATIVE, 'BSCS 3B Representative'),
        (BSCS_4A_REPRESENTATIVE, 'BSCS 4A Representative'),
        (BSCS_4B_REPRESENTATIVE, 'BSCS 4B Representative'),
    ]

    REGULAR_ROLES = frozenset({
        VICE_PRESIDENT,
        SECRETARY,
        ASSISTANT_SECRETARY,
        TREASURER,
        ASSISTANT_TREASURER,
        AUDITOR,
        BUSINESS_MANAGER,
        PIO,
        ATHLETIC_MANAGER_MALE,
        ATHLETIC_MANAGER_FEMALE,
        BSCS_1A_REPRESENTATIVE,
        BSCS_1B_REPRESENTATIVE,
        BSCS_2A_REPRESENTATIVE,
        BSCS_2B_REPRESENTATIVE,
        BSCS_3A_REPRESENTATIVE,
        BSCS_3B_REPRESENTATIVE,
        BSCS_4A_REPRESENTATIVE,
        BSCS_4B_REPRESENTATIVE,
    })
    
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
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
    def is_adviser(self):
        return self.role and self.role.name == Role.ADVISER
    
    @property
    def is_president(self):
        return self.role and self.role.name == Role.PRESIDENT

    @property
    def is_admin(self):
        """Alias for adviser role checks for backward compatibility."""
        return self.is_adviser

    @property
    def is_manager(self):
        """Alias for president role checks for backward compatibility."""
        return self.is_president
    
    @property
    def is_regular_user(self):
        if not self.role:
            return True
        return self.role.name in Role.REGULAR_ROLES
    
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
        ('ACCOUNT_ACTIVATE', 'Account Activate'),
        ('ACCOUNT_DEACTIVATE', 'Account Deactivate'),
        ('DOCUMENT_UPLOAD', 'Document Upload'),
        ('DOCUMENT_VIEW', 'Document View'),
        ('DOCUMENT_DOWNLOAD', 'Document Download'),
        ('DOCUMENT_UPDATE', 'Document Update'),
        ('DOCUMENT_DELETE', 'Document Delete'),
        ('DOCUMENT_ARCHIVE', 'Document Archive'),
        ('DOCUMENT_FOLDER_CREATE', 'Document Folder Create'),
        ('DOCUMENT_FOLDER_UPDATE', 'Document Folder Update'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"
    
    class Meta:
        ordering = ['-timestamp']
