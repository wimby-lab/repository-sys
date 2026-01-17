from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Role, AuditLog


class AuthenticationTests(TestCase):
    """Test authentication functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user_role = Role.objects.create(name=Role.VICE_PRESIDENT, description='Vice President')
        
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

    def test_login_page_system_name(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertContains(response, 'COMSOC Repository System')


class RoleBasedAccessTests(TestCase):
    """Test role-based access control"""
    
    def setUp(self):
        self.client = Client()
        self.admin_role = Role.objects.create(name=Role.ADVISER)
        self.manager_role = Role.objects.create(name=Role.PRESIDENT)
        self.user_role = Role.objects.create(name=Role.AUDITOR)
        
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
        
    def test_adviser_can_access_role_management(self):
        """Test adviser can access role management"""
        self.client.login(username='admin', password='pass')
        response = self.client.get(reverse('accounts:role_management'))
        self.assertEqual(response.status_code, 200)
        
    def test_officer_cannot_access_role_management(self):
        """Test officer cannot access role management"""
        self.client.login(username='user', password='pass')
        response = self.client.get(reverse('accounts:role_management'))
        self.assertEqual(response.status_code, 302)  # Redirect
        
    def test_role_properties(self):
        """Test role property methods"""
        self.assertTrue(self.admin.is_adviser)
        self.assertTrue(self.admin.is_admin)
        self.assertFalse(self.admin.is_manager)
        self.assertFalse(self.admin.is_regular_user)
        
        self.assertFalse(self.manager.is_admin)
        self.assertTrue(self.manager.is_president)
        self.assertTrue(self.manager.is_manager)
        self.assertFalse(self.manager.is_regular_user)
        
        self.assertFalse(self.user.is_admin)
        self.assertFalse(self.user.is_manager)
        self.assertTrue(self.user.is_regular_user)

    def test_unassigned_user_is_regular(self):
        """Test users without roles are treated as regular users"""
        unassigned = User.objects.create_user(
            username='unassigned',
            password='pass',
            role=None
        )
        self.assertTrue(unassigned.is_regular_user)

    def test_adviser_can_toggle_user_active(self):
        """Test adviser can deactivate another user"""
        self.client.login(username='admin', password='pass')
        response = self.client.post(reverse('accounts:toggle_user_active', args=[self.user.id]))
        self.assertRedirects(response, reverse('accounts:role_management'))
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertTrue(AuditLog.objects.filter(user=self.admin, action='ACCOUNT_DEACTIVATE').exists())

    def test_adviser_cannot_toggle_own_active_status(self):
        """Test adviser cannot deactivate self"""
        self.client.login(username='admin', password='pass')
        response = self.client.post(reverse('accounts:toggle_user_active', args=[self.admin.id]))
        self.assertRedirects(response, reverse('accounts:role_management'))
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

    def test_officer_cannot_toggle_user_active(self):
        """Test officer cannot deactivate users"""
        self.client.login(username='user', password='pass')
        response = self.client.post(reverse('accounts:toggle_user_active', args=[self.manager.id]))
        self.assertRedirects(response, reverse('dashboard:index'))
        self.manager.refresh_from_db()
        self.assertTrue(self.manager.is_active)


class AuditLogTests(TestCase):
    """Test audit logging"""
    
    def setUp(self):
        self.user_role = Role.objects.create(name=Role.TREASURER)
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
