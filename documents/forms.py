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


class DocumentUploadForm(forms.ModelForm):
    """Form for uploading documents"""
    class Meta:
        model = Document
        fields = ['title', 'description', 'file', 'classification', 'section', 'category', 'tags']
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


class DocumentUpdateForm(forms.ModelForm):
    """Form for updating document metadata"""
    class Meta:
        model = Document
        fields = ['title', 'description', 'classification', 'section', 'category', 'tags']
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
