from urllib.parse import urlparse

from django import forms
from django.utils.text import slugify
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from .models import Document, DocumentFolder


def _folder_choices(include_all=False):
    folders = list(DocumentFolder.objects.order_by('name').values_list('key', 'name'))
    if not folders:
        folders = list(Document.SECTION_CHOICES)
    if include_all:
        return [('', 'All Folders')] + folders
    return folders


def _generate_folder_key(name):
    base_key = slugify(name).replace('-', '_').upper() or 'FOLDER'
    existing_keys = set(
        DocumentFolder.objects.filter(key__startswith=base_key).values_list('key', flat=True)
    )
    if base_key not in existing_keys:
        return base_key
    counter = 1
    key = f'{base_key}_{counter}'
    while key in existing_keys:
        counter += 1
        key = f'{base_key}_{counter}'
    return key


def _is_google_docs_url(url):
    parsed = urlparse(url or '')
    return parsed.scheme in ('http', 'https') and parsed.netloc == 'docs.google.com' and (
        '/document/' in parsed.path
    )


def _is_google_sheets_url(url):
    parsed = urlparse(url or '')
    return parsed.scheme in ('http', 'https') and parsed.netloc == 'docs.google.com' and (
        '/spreadsheets/' in parsed.path
    )


def _validate_google_links(form, cleaned_data, has_file):
    google_docs_url = cleaned_data.get('google_docs_url')
    google_sheets_url = cleaned_data.get('google_sheets_url')
    if google_docs_url and google_sheets_url:
        form.add_error(
            None,
            forms.ValidationError(
                'Please provide either a Google Docs or Google Sheets URL, not both.',
                code='invalid',
            ),
        )
    if google_docs_url and not _is_google_docs_url(google_docs_url):
        form.add_error(
            'google_docs_url',
            forms.ValidationError(
                'Google Docs URL must be a valid docs.google.com document link.',
                code='invalid',
            ),
        )
    if google_sheets_url and not _is_google_sheets_url(google_sheets_url):
        form.add_error(
            'google_sheets_url',
            forms.ValidationError(
                'Google Sheets URL must be a valid docs.google.com spreadsheets link.',
                code='invalid',
            ),
        )
    if not has_file and not google_docs_url and not google_sheets_url:
        form.add_error(
            None,
            forms.ValidationError(
                'Please either upload a file or provide a Google Docs/Sheets URL.',
                code='required',
            ),
        )


class DocumentUploadForm(forms.ModelForm):
    """Form for uploading documents"""
    class Meta:
        model = Document
        fields = [
            'title',
            'description',
            'file',
            'google_docs_url',
            'google_sheets_url',
            'classification',
            'section',
            'category',
            'tags',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'tags': forms.TextInput(attrs={'placeholder': 'Enter tags separated by commas'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.add_input(Submit('submit', 'Upload Document', css_class='btn btn-primary'))
        self.fields['section'].choices = _folder_choices()
        self.fields['section'].label = 'Folder'
        self.fields['file'].required = False
        self.fields['google_docs_url'].label = 'Google Docs URL'
        self.fields['google_sheets_url'].label = 'Google Sheets URL'
        self.fields['google_docs_url'].help_text = 'Paste a Google Docs link to create a linked document.'
        self.fields['google_sheets_url'].help_text = 'Paste a Google Sheets link to create a linked document.'

    def clean_file(self):
        """Validate file type and size"""
        from django.conf import settings
        
        file = self.cleaned_data.get('file')
        if file:
            # Check file size
            if file.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                raise forms.ValidationError(
                    f'File size must not exceed {settings.FILE_UPLOAD_MAX_MEMORY_SIZE / (1024*1024)}MB'
                )
            
            # Check file type
            if file.content_type not in settings.ALLOWED_DOCUMENT_TYPES:
                raise forms.ValidationError(
                    f'File type {file.content_type} is not allowed. Allowed types: PDF, Word, Excel, Text, Images'
                )
        
        return file

    def clean(self):
        cleaned_data = super().clean()
        _validate_google_links(self, cleaned_data, bool(cleaned_data.get('file')))
        return cleaned_data


class DocumentUpdateForm(forms.ModelForm):
    """Form for updating document metadata"""
    class Meta:
        model = Document
        fields = [
            'title',
            'description',
            'google_docs_url',
            'google_sheets_url',
            'classification',
            'section',
            'category',
            'tags',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'tags': forms.TextInput(attrs={'placeholder': 'Enter tags separated by commas'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Update Document', css_class='btn btn-primary'))
        self.fields['section'].choices = _folder_choices()
        self.fields['section'].label = 'Folder'
        self.fields['google_docs_url'].label = 'Google Docs URL'
        self.fields['google_sheets_url'].label = 'Google Sheets URL'
        self.fields['google_docs_url'].help_text = 'Optional Google Docs link for this document.'
        self.fields['google_sheets_url'].help_text = 'Optional Google Sheets link for this document.'

    def clean(self):
        cleaned_data = super().clean()
        has_file = bool(getattr(self.instance, 'file', None))
        _validate_google_links(self, cleaned_data, has_file)
        return cleaned_data


class DocumentSearchForm(forms.Form):
    """Form for searching and filtering documents"""
    query = forms.CharField(
        max_length=255, 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Search by title or filename...'})
    )
    classification = forms.ChoiceField(
        choices=[('', 'All Classifications')] + Document.CLASSIFICATION_CHOICES,
        required=False
    )
    section = forms.ChoiceField(choices=(), required=False, label='Folder')
    category = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Category...'})
    )
    owner = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Owner username...'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        self.helper.add_input(Submit('submit', 'Search', css_class='btn btn-primary'))
        self.fields['section'].choices = _folder_choices(include_all=True)


class DocumentFolderForm(forms.ModelForm):
    """Form for managing document folders"""
    class Meta:
        model = DocumentFolder
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Folder name'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save Folder', css_class='btn btn-primary'))

    def clean_name(self):
        name = self.cleaned_data.get('name', '')
        if not slugify(name):
            raise forms.ValidationError('Folder name must include letters or numbers.')
        return name

    def save(self, commit=True):
        folder = super().save(commit=False)
        if not folder.key:
            folder.key = _generate_folder_key(folder.name)
        if commit:
            folder.save()
        return folder
