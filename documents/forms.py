from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from .models import Document


class DocumentUploadForm(forms.ModelForm):
    """Form for uploading documents"""
    class Meta:
        model = Document
        fields = ['title', 'description', 'file', 'classification', 'category', 'tags']
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
        fields = ['title', 'description', 'classification', 'category', 'tags']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'tags': forms.TextInput(attrs={'placeholder': 'Enter tags separated by commas'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Update Document', css_class='btn btn-primary'))


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
