from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Role, AuditLog


class AuthenticationTests(TestCase):
    """Test authentication functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user_role = Role.objects.create(name=Role.USER, description='Regular user')
        
    def test_user_registration(self):
        """Test user can register"""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(User.objects.filter(username='testuser').exists())
        
    def test_user_login(self):
        """Test user can login"""
        user = User.objects.create_user(
            username='testuser',
            password='SecurePass123!',
            role=self.user_role
        )
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'SecurePass123!',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
    def test_user_logout(self):
        """Test user can logout"""
        user = User.objects.create_user(
            username='testuser',
            password='SecurePass123!',
            role=self.user_role
        )
        self.client.login(username='testuser', password='SecurePass123!')
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)


class RoleBasedAccessTests(TestCase):
    """Test role-based access control"""
    
    def setUp(self):
        self.client = Client()
        self.admin_role = Role.objects.create(name=Role.ADMIN)
        self.manager_role = Role.objects.create(name=Role.MANAGER)
        self.user_role = Role.objects.create(name=Role.USER)
        
        self.admin = User.objects.create_user(
            username='admin',
            password='pass',
            role=self.admin_role
        )
        self.manager = User.objects.create_user(
            username='manager',
            password='pass',
            role=self.manager_role
        )
        self.user = User.objects.create_user(
            username='user',
            password='pass',
            role=self.user_role
        )
        
    def test_admin_can_access_role_management(self):
        """Test admin can access role management"""
        self.client.login(username='admin', password='pass')
        response = self.client.get(reverse('accounts:role_management'))
        self.assertEqual(response.status_code, 200)
        
    def test_user_cannot_access_role_management(self):
        """Test regular user cannot access role management"""
        self.client.login(username='user', password='pass')
        response = self.client.get(reverse('accounts:role_management'))
        self.assertEqual(response.status_code, 302)  # Redirect
        
    def test_role_properties(self):
        """Test role property methods"""
        self.assertTrue(self.admin.is_admin)
        self.assertFalse(self.admin.is_manager)
        self.assertFalse(self.admin.is_regular_user)
        
        self.assertFalse(self.manager.is_admin)
        self.assertTrue(self.manager.is_manager)
        self.assertFalse(self.manager.is_regular_user)
        
        self.assertFalse(self.user.is_admin)
        self.assertFalse(self.user.is_manager)
        self.assertTrue(self.user.is_regular_user)


class AuditLogTests(TestCase):
    """Test audit logging"""
    
    def setUp(self):
        self.user_role = Role.objects.create(name=Role.USER)
        self.user = User.objects.create_user(
            username='testuser',
            password='pass',
            role=self.user_role
        )
        
    def test_audit_log_creation(self):
        """Test audit log can be created"""
        log = AuditLog.objects.create(
            user=self.user,
            action='LOGIN',
            description='User logged in'
        )
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, 'LOGIN')

