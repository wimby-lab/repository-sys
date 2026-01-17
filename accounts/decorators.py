from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """Decorator to require adviser role"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        if not request.user.is_admin and not request.user.is_superuser:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard:index')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def manager_or_admin_required(view_func):
    """Decorator to require president or adviser role"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        if not (request.user.is_admin or request.user.is_manager or request.user.is_superuser):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard:index')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view
