from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from core.models import User # Import your custom User model


@csrf_exempt
def user_login(request):
    if settings.DEBUG:
        # Auto-login for development
        admin_email = 'admin@example.com'
        admin_password = 'password' # Use a simple password for dev

        try:
            user = User.objects.get(email=admin_email)
        except User.DoesNotExist:
            # Create admin user if it doesn't exist
            user = User.objects.create_user(
                email=admin_email,
                username='admin',
                password=admin_password,
                role='admin',
                is_staff=True,
                is_superuser=True
            )
            messages.info(request, f"Auto-created admin user: {admin_email}/{admin_password}")

        login(request, user)
        messages.success(request, "Auto-logged in as admin for development.")
        return redirect('adminportal:dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            if user.role == 'admin':
                return redirect('adminportal:dashboard')
            elif user.role == 'employee':
                return redirect('employeeportal:employee_dashboard')
            else:
                messages.error(request, 'Invalid role assigned.')
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'login.html')


@login_required
def user_logout(request):
    logout(request)
    messages.success(request, '✅ You have been logged out successfully.')
    return redirect('login')
