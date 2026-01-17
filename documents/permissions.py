from django.db.models import Q


def can_access_document(user, document):
    """Check if user can access a document"""
    # Advisers can access all documents
    if user.is_admin or user.is_superuser:
        return True
    
    # Presidents can access all documents except restricted
    if user.is_manager and document.classification != 'RESTRICTED':
        return True
    
    # Owner can always access their own documents
    if document.owner == user:
        return True
    
    # Check if document is shared with the user
    if document.shared_with.filter(id=user.id).exists():
        return True
    
    # Public documents can be accessed by anyone
    if document.classification == 'PUBLIC':
        return True
    
    return False


def get_accessible_documents(user):
    """Get queryset of documents accessible to the user"""
    if user.is_admin or user.is_superuser:
        # Advisers can see all documents
        return Q()
    elif user.is_manager:
        # Presidents can see all except restricted
        return Q(classification__in=['PUBLIC', 'INTERNAL', 'CONFIDENTIAL']) | Q(owner=user)
    else:
        # Regular users can see their own, shared with them, and public documents
        return Q(owner=user) | Q(shared_with=user) | Q(classification='PUBLIC')
