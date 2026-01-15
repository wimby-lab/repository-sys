from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
from django.db.models import Q
from django.utils import timezone
from .models import Document
from .forms import DocumentUploadForm, DocumentUpdateForm, DocumentSearchForm
from .permissions import can_access_document, get_accessible_documents
from accounts.utils import log_audit
from accounts.decorators import manager_or_admin_required
import os


@login_required
def document_list(request):
    """List documents with search and filter"""
    form = DocumentSearchForm(request.GET)
    
    # Get base queryset with access control - exclude archived documents
    documents = Document.objects.select_related('owner').filter(
        get_accessible_documents(request.user),
        is_archived=False
    ).distinct()
    
    # Apply search filters
    if form.is_valid():
        query = form.cleaned_data.get('query')
        if query:
            documents = documents.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) |
                Q(file__icontains=query)
            )
        
        classification = form.cleaned_data.get('classification')
        if classification:
            documents = documents.filter(classification=classification)
        
        category = form.cleaned_data.get('category')
        if category:
            documents = documents.filter(category__icontains=category)
        
        owner = form.cleaned_data.get('owner')
        if owner:
            documents = documents.filter(owner__username__icontains=owner)
        
        date_from = form.cleaned_data.get('date_from')
        if date_from:
            documents = documents.filter(created_at__gte=date_from)
        
        date_to = form.cleaned_data.get('date_to')
        if date_to:
            documents = documents.filter(created_at__lte=date_to)
    
    return render(request, 'documents/document_list.html', {
        'documents': documents,
        'form': form
    })


@login_required
def document_upload(request):
    """Upload a new document"""
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.owner = request.user
            document.file_size = document.file.size
            document.file_type = document.file.content_type
            document.save()
            
            log_audit(
                request.user,
                'DOCUMENT_UPLOAD',
                f'Uploaded document: {document.title}',
                request
            )
            
            messages.success(request, 'Document uploaded successfully!')
            return redirect('documents:document_detail', pk=document.pk)
    else:
        form = DocumentUploadForm()
    
    return render(request, 'documents/document_upload.html', {'form': form})


@login_required
def document_detail(request, pk):
    """View document details"""
    document = get_object_or_404(Document, pk=pk)
    
    # Check access permission
    if not can_access_document(request.user, document):
        messages.error(request, 'You do not have permission to view this document.')
        return redirect('documents:document_list')
    
    log_audit(
        request.user,
        'DOCUMENT_VIEW',
        f'Viewed document: {document.title}',
        request
    )
    
    return render(request, 'documents/document_detail.html', {'document': document})


@login_required
def document_download(request, pk):
    """Download a document"""
    document = get_object_or_404(Document, pk=pk)
    
    # Check access permission
    if not can_access_document(request.user, document):
        messages.error(request, 'You do not have permission to download this document.')
        return redirect('documents:document_list')
    
    log_audit(
        request.user,
        'DOCUMENT_DOWNLOAD',
        f'Downloaded document: {document.title}',
        request
    )
    
    # Serve file
    if os.path.exists(document.file.path):
        response = FileResponse(document.file.open('rb'), as_attachment=True)
        return response
    else:
        raise Http404("Document file not found")


@login_required
def document_update(request, pk):
    """Update document metadata"""
    document = get_object_or_404(Document, pk=pk)
    
    # Only owner, manager, or admin can update
    if not (document.owner == request.user or request.user.is_manager or request.user.is_admin):
        messages.error(request, 'You do not have permission to update this document.')
        return redirect('documents:document_detail', pk=pk)
    
    if request.method == 'POST':
        form = DocumentUpdateForm(request.POST, instance=document)
        if form.is_valid():
            form.save()
            
            log_audit(
                request.user,
                'DOCUMENT_UPDATE',
                f'Updated document: {document.title}',
                request
            )
            
            messages.success(request, 'Document updated successfully!')
            return redirect('documents:document_detail', pk=pk)
    else:
        form = DocumentUpdateForm(instance=document)
    
    return render(request, 'documents/document_update.html', {
        'form': form,
        'document': document
    })


@login_required
@manager_or_admin_required
def document_delete(request, pk):
    """Archive a document (soft delete)"""
    document = get_object_or_404(Document, pk=pk)
    
    # Only owner, manager, or admin can archive
    if not (document.owner == request.user or request.user.is_manager or request.user.is_admin):
        messages.error(request, 'You do not have permission to archive this document.')
        return redirect('documents:document_detail', pk=pk)
    
    if request.method == 'POST':
        title = document.title
        
        # Archive the document instead of deleting
        document.is_archived = True
        document.archived_at = timezone.now()
        document.archived_by = request.user
        document.save()
        
        log_audit(
            request.user,
            'DOCUMENT_ARCHIVE',
            f'Archived document: {title}',
            request
        )
        
        messages.success(request, 'Document archived successfully!')
        return redirect('documents:document_list')
    
    return render(request, 'documents/document_delete.html', {'document': document})

