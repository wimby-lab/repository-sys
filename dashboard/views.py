from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from documents.models import Document
from documents.permissions import get_accessible_documents
from accounts.models import AuditLog
from django.db.models import Count, Q
from datetime import timedelta
from django.utils import timezone


@login_required
def index(request):
    """Dashboard home page"""
    user = request.user
    
    # Get accessible documents
    accessible_docs = Document.objects.filter(
        get_accessible_documents(user)
    ).distinct()
    
    # Total documents count
    total_documents = accessible_docs.count()
    
    # User's own documents
    my_documents = accessible_docs.filter(owner=user).count()
    
    # Recent uploads (last 7 days)
    last_week = timezone.now() - timedelta(days=7)
    recent_uploads = accessible_docs.filter(created_at__gte=last_week).count()
    
    # Recent documents
    recent_docs = accessible_docs.order_by('-created_at')[:5]
    
    # Documents by classification
    docs_by_classification = accessible_docs.values('classification').annotate(
        count=Count('id')
    ).order_by('classification')
    
    # Recent activity (if admin or manager)
    recent_activity = None
    if user.is_admin or user.is_manager:
        recent_activity = AuditLog.objects.select_related('user').order_by('-timestamp')[:10]
    
    context = {
        'total_documents': total_documents,
        'my_documents': my_documents,
        'recent_uploads': recent_uploads,
        'recent_docs': recent_docs,
        'docs_by_classification': docs_by_classification,
        'recent_activity': recent_activity,
    }
    
    return render(request, 'dashboard/index.html', context)

