from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from documents.models import Document
from documents.permissions import get_accessible_documents
from accounts.models import AuditLog
from accounts.decorators import manager_or_admin_required
import csv
from datetime import datetime


@login_required
@manager_or_admin_required
def document_inventory(request):
    """Document inventory report"""
    documents = Document.objects.filter(
        get_accessible_documents(request.user)
    ).select_related('owner').distinct()
    
    # Apply filters
    classification = request.GET.get('classification')
    if classification:
        documents = documents.filter(classification=classification)
    
    category = request.GET.get('category')
    if category:
        documents = documents.filter(category__icontains=category)
    
    context = {
        'documents': documents,
        'classification_choices': Document.CLASSIFICATION_CHOICES,
    }
    
    return render(request, 'reports/document_inventory.html', context)


@login_required
@manager_or_admin_required
def activity_report(request):
    """Activity report"""
    logs = AuditLog.objects.select_related('user').order_by('-timestamp')
    
    # Apply filters
    action = request.GET.get('action')
    if action:
        logs = logs.filter(action=action)
    
    user_id = request.GET.get('user')
    if user_id:
        logs = logs.filter(user_id=user_id)
    
    date_from = request.GET.get('date_from')
    if date_from:
        logs = logs.filter(timestamp__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        logs = logs.filter(timestamp__lte=date_to)
    
    # Limit to latest 1000 for performance
    logs = logs[:1000]
    
    context = {
        'logs': logs,
        'action_choices': AuditLog.ACTION_CHOICES,
    }
    
    return render(request, 'reports/activity_report.html', context)


@login_required
@manager_or_admin_required
def export_inventory_csv(request):
    """Export document inventory to CSV"""
    documents = Document.objects.filter(
        get_accessible_documents(request.user)
    ).select_related('owner').distinct()
    
    # Apply filters
    classification = request.GET.get('classification')
    if classification:
        documents = documents.filter(classification=classification)
    
    category = request.GET.get('category')
    if category:
        documents = documents.filter(category__icontains=category)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="document_inventory_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Title', 'Owner', 'Classification', 'Category', 'Tags', 'File Size (bytes)', 'Created At', 'Updated At'])
    
    for doc in documents:
        writer.writerow([
            doc.title,
            doc.owner.username,
            doc.get_classification_display(),
            doc.category,
            doc.tags,
            doc.file_size,
            doc.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            doc.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])
    
    return response


@login_required
@manager_or_admin_required
def export_activity_csv(request):
    """Export activity report to CSV"""
    logs = AuditLog.objects.select_related('user').order_by('-timestamp')
    
    # Apply filters
    action = request.GET.get('action')
    if action:
        logs = logs.filter(action=action)
    
    user_id = request.GET.get('user')
    if user_id:
        logs = logs.filter(user_id=user_id)
    
    date_from = request.GET.get('date_from')
    if date_from:
        logs = logs.filter(timestamp__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        logs = logs.filter(timestamp__lte=date_to)
    
    # Limit to latest 1000 for performance
    logs = logs[:1000]
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="activity_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['User', 'Action', 'Description', 'IP Address', 'Timestamp'])
    
    for log in logs:
        writer.writerow([
            log.user.username,
            log.get_action_display(),
            log.description,
            log.ip_address or '',
            log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        ])
    
    return response

