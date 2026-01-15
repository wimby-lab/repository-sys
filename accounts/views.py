from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from .forms import UserRegistrationForm, UserLoginForm, CustomPasswordResetForm, RoleAssignmentForm
from .models import User, Role
from .utils import log_audit
from .decorators import admin_required


def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Assign default USER role
            user_role, _ = Role.objects.get_or_create(name=Role.USER)
            user.role = user_role
            user.save()
            
            log_audit(user, 'REGISTER', f'New user registered: {user.username}', request)
            
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('accounts:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                log_audit(user, 'LOGIN', f'User logged in', request)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('dashboard:index')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def user_logout(request):
    """User logout view"""
    log_audit(request.user, 'LOGOUT', f'User logged out', request)
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')


class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view"""
    form_class = CustomPasswordResetForm
    template_name = 'accounts/password_reset.html'
    success_url = reverse_lazy('accounts:password_reset_done')
    email_template_name = 'accounts/password_reset_email.html'


@login_required
@admin_required
def role_management(request):
    """Role management view (admin only)"""
    if request.method == 'POST':
        form = RoleAssignmentForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            role = form.cleaned_data['role']
            old_role = user.role
            user.role = role
            user.save()
            
            log_audit(
                request.user,
                'ROLE_CHANGE',
                f'Changed role for {user.username} from {old_role} to {role}',
                request
            )
            
            messages.success(request, f'Role updated for {user.username}')
            return redirect('accounts:role_management')
    else:
        form = RoleAssignmentForm()
    
    users = User.objects.select_related('role').all()
    return render(request, 'accounts/role_management.html', {
        'form': form,
        'users': users
    })

