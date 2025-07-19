from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            if user.role == 'admin':
                return redirect('adminportal:dashboard')  # assuming no namespace for admin
            elif user.role == 'employee':
                return redirect('employeeportal:employee_dashboard')  # updated with namespace
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
