from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import User, Role
from .models import Document, DocumentFolder
from .forms import DocumentFolderForm, DocumentSearchForm
from .permissions import can_access_document


class DocumentAccessTests(TestCase):
    """Test document access control"""
    
    def setUp(self):
        self.client = Client()
        
        # Create roles
        self.admin_role = Role.objects.create(name=Role.ADVISER)
        self.manager_role = Role.objects.create(name=Role.PRESIDENT)
        self.user_role = Role.objects.create(name=Role.AUDITOR)
        
        # Create users
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
        self.user1 = User.objects.create_user(
            username='user1',
            password='pass',
            role=self.user_role
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='pass',
            role=self.user_role
        )
        
        # Create test documents
        self.public_doc = Document.objects.create(
            title='Public Document',
            owner=self.user1,
            classification='PUBLIC',
            file='test.txt',
            file_type='text/plain',
            file_size=100
        )
        
        self.internal_doc = Document.objects.create(
            title='Internal Document',
            owner=self.user1,
            classification='INTERNAL',
            file='test.txt',
            file_type='text/plain',
            file_size=100
        )
        
        self.restricted_doc = Document.objects.create(
            title='Restricted Document',
            owner=self.user1,
            classification='RESTRICTED',
            file='test.txt',
            file_type='text/plain',
            file_size=100
        )
        
    def test_owner_can_access_own_documents(self):
        """Test document owner can access their own documents"""
        self.assertTrue(can_access_document(self.user1, self.public_doc))
        self.assertTrue(can_access_document(self.user1, self.internal_doc))
        self.assertTrue(can_access_document(self.user1, self.restricted_doc))
        
    def test_adviser_can_access_all_documents(self):
        """Test adviser can access all documents"""
        self.assertTrue(can_access_document(self.admin, self.public_doc))
        self.assertTrue(can_access_document(self.admin, self.internal_doc))
        self.assertTrue(can_access_document(self.admin, self.restricted_doc))
        
    def test_president_cannot_access_restricted(self):
        """Test president cannot access restricted documents"""
        self.assertTrue(can_access_document(self.manager, self.public_doc))
        self.assertTrue(can_access_document(self.manager, self.internal_doc))
        self.assertFalse(can_access_document(self.manager, self.restricted_doc))
        
    def test_officer_can_access_public_only(self):
        """Test officer can only access public documents by default"""
        self.assertTrue(can_access_document(self.user2, self.public_doc))
        self.assertFalse(can_access_document(self.user2, self.internal_doc))
        self.assertFalse(can_access_document(self.user2, self.restricted_doc))
        
    def test_shared_document_access(self):
        """Test user can access documents shared with them"""
        self.internal_doc.shared_with.add(self.user2)
        self.assertTrue(can_access_document(self.user2, self.internal_doc))
        
    def test_document_upload_requires_login(self):
        """Test document upload requires authentication"""
        response = self.client.get(reverse('documents:document_upload'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
    def test_authenticated_user_can_upload(self):
        """Test authenticated user can access upload page"""
        self.client.login(username='user1', password='pass')
        response = self.client.get(reverse('documents:document_upload'))
        self.assertEqual(response.status_code, 200)

    def test_upload_sets_file_metadata(self):
        """Test upload stores file metadata from the uploaded file"""
        self.client.login(username='user1', password='pass')
        upload = SimpleUploadedFile(
            'hello.txt',
            b'hello',
            content_type='text/plain'
        )

        response = self.client.post(
            reverse('documents:document_upload'),
            {
                'title': 'Hello',
                'description': 'Test upload',
                'file': upload,
                'classification': 'PUBLIC',
                'section': 'GENERAL',
                'category': 'General',
                'tags': 'test',
            }
        )

        self.assertEqual(response.status_code, 302)
        document = Document.objects.get(title='Hello')
        self.assertEqual(document.file_size, 5)
        self.assertEqual(document.file_type, 'text/plain')
        
    def test_archived_documents_not_in_list(self):
        """Test archived documents are not shown in document list"""
        # Archive a document
        self.public_doc.is_archived = True
        self.public_doc.archived_by = self.admin
        self.public_doc.save()
        
        # Login and get document list
        self.client.login(username='user2', password='pass')
        response = self.client.get(reverse('documents:document_list'))
        
        # Archived document should not be in the list
        self.assertNotContains(response, self.public_doc.title)
        
    def test_archived_document_detail_blocked(self):
        """Test archived documents cannot be accessed via detail view"""
        # Archive a document
        self.public_doc.is_archived = True
        self.public_doc.archived_by = self.admin
        self.public_doc.save()
        
        # Try to access archived document
        self.client.login(username='user2', password='pass')
        response = self.client.get(reverse('documents:document_detail', args=[self.public_doc.pk]))
        
        # Should redirect with error message
        self.assertEqual(response.status_code, 302)
        
    def test_archived_document_download_blocked(self):
        """Test archived documents cannot be downloaded"""
        # Archive a document
        self.public_doc.is_archived = True
        self.public_doc.archived_by = self.admin
        self.public_doc.save()
        
        # Try to download archived document
        self.client.login(username='user2', password='pass')
        response = self.client.get(reverse('documents:document_download', args=[self.public_doc.pk]))
        
        # Should redirect with error message
        self.assertEqual(response.status_code, 302)

    def test_document_list_filters_by_section(self):
        """Test document list can be filtered by section"""
        folder = DocumentFolder.objects.get(key='GENERAL')
        section_value = folder.key
        section_doc = Document.objects.create(
            title='Section Document',
            owner=self.user1,
            classification='PUBLIC',
            section=section_value,
            file='test.txt',
            file_type='text/plain',
            file_size=100
        )

        self.client.login(username='user1', password='pass')
        response = self.client.get(reverse('documents:document_list'), {'section': section_value})

        self.assertContains(response, section_doc.title)
        self.assertNotContains(response, self.public_doc.title)


class DocumentFolderTests(TestCase):
    """Test document folder management"""

    def test_folder_form_generates_key(self):
        form = DocumentFolderForm(data={'name': 'Project Docs'})
        self.assertTrue(form.is_valid())
        folder = form.save()
        self.assertEqual(folder.key, 'PROJECT_DOCS')

    def test_search_form_includes_folder_choices(self):
        folder = DocumentFolder.objects.create(key='FINANCE', name='Finance')
        form = DocumentSearchForm()
        self.assertIn((folder.key, folder.name), form.fields['section'].choices)


class DocumentModelTests(TestCase):
    """Test document model"""
    
    def setUp(self):
        self.user_role = Role.objects.create(name=Role.SECRETARY)
        self.user = User.objects.create_user(
            username='testuser',
            password='pass',
            role=self.user_role
        )
        
    def test_document_creation(self):
        """Test document can be created"""
        doc = Document.objects.create(
            title='Test Document',
            owner=self.user,
            classification='PUBLIC',
            file='test.txt',
            file_type='text/plain',
            file_size=100
        )
        self.assertEqual(doc.title, 'Test Document')
        self.assertEqual(doc.owner, self.user)
        self.assertEqual(doc.section, Document.SECTION_CHOICES[0][0])
        self.assertFalse(doc.is_archived)
        
    def test_document_tags_list(self):
        """Test document tags parsing"""
        doc = Document.objects.create(
            title='Test Document',
            owner=self.user,
            classification='PUBLIC',
            tags='tag1, tag2, tag3',
            file='test.txt',
            file_type='text/plain',
            file_size=100
        )
        tags = doc.get_tags_list()
        self.assertEqual(len(tags), 3)
        self.assertIn('tag1', tags)
        self.assertIn('tag2', tags)
        self.assertIn('tag3', tags)
        
    def test_document_archiving(self):
        """Test document can be archived"""
        from django.utils import timezone
        
        doc = Document.objects.create(
            title='Test Document',
            owner=self.user,
            classification='PUBLIC',
            file='test.txt',
            file_type='text/plain',
            file_size=100
        )
        self.assertFalse(doc.is_archived)
        
        # Archive the document
        doc.is_archived = True
        doc.archived_by = self.user
        doc.archived_at = timezone.now()
        doc.save()
        
        self.assertTrue(doc.is_archived)
        self.assertEqual(doc.archived_by, self.user)
        self.assertIsNotNone(doc.archived_at)
