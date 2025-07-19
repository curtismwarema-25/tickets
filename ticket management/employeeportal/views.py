from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.models import Ticket, Client





#employee dashboard
@login_required
def employee_dashboard(request):
    completed_tickets = Ticket.objects.filter(technician=request.user, status='completed').count()
    pending_tickets = Ticket.objects.filter(technician=request.user, status='pending').count()
    high_priority = Ticket.objects.filter(technician=request.user, priority='high').count()

    return render(request, 'employeeportal/base.html', {
        'completed_count': completed_tickets,
        'pending_count': pending_tickets,
        'high_priority_count': high_priority
    })


#employee ticket handler
@login_required
def employee_tickets(request):
    user = request.user
    filter_option = request.GET.get('filter', '')
    status = request.GET.get('status', '')
    search_query = request.GET.get('search', '')

    # Base queryset - all tickets assigned to the user
    tickets = Ticket.objects.filter(technician=user)

    if search_query:
        tickets = tickets.filter(title__icontains=search_query)

    # Apply filters
    if filter_option == 'high_priority':
        tickets = tickets.filter(priority='high')
    elif filter_option == 'my_tickets':
        # Already filtered by technician=user, so no additional filter needed
        pass
    elif filter_option == 'overdue':
        from django.utils import timezone
        tickets = tickets.filter(deadline__lt=timezone.now().date(), status__in=['pending', 'in_progress'])
    elif status:
        tickets = tickets.filter(status=status)

    tickets = tickets.order_by('status', '-created_at')

    clients = Client.objects.all()
    from core.models import User
    admins = User.objects.filter(role='admin')

    return render(request, 'employeeportal/tickets.html', {
        'tickets': tickets,
        'clients': clients,
        'status': status,
        'filter_option': filter_option,
        'search_query': search_query,
        'admins': admins,
    })



#ticket defination
@login_required
def ticket_detail(request, pk):
    ticket = Ticket.objects.get(pk=pk, technician=request.user)
    return render(request, 'partials/ticket_detail_partial.html', {'ticket': ticket})


#clients dashboard views
from core.models import Client
@login_required
def employee_clients(request):
    clients = Client.objects.all()
    return render(request, 'employeeportal/clients.html', {'clients': clients})


#employee create ticket
from django.contrib import messages
from core.models import Ticket, Client

@login_required
def employee_create_ticket(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority')
        deadline = request.POST.get('deadline')
        admin_id = request.POST.get('admin')

        internal_client = Client.objects.get(name="Internal Employee")
        admin_user = None
        if admin_id:
            from core.models import User
            try:
                admin_user = User.objects.get(id=admin_id, role='admin')
            except User.DoesNotExist:
                admin_user = None

        Ticket.objects.create(
            title=title,
            description=description,
            priority=priority,
            deadline=deadline,
            creator=request.user,
            client=internal_client,
            technician=admin_user if admin_user else None,
        )

        messages.success(request, "✅ Ticket created successfully.")
        return redirect('employeeportal:employee_tickets')

    return render(request, 'employeeportal/employee_create_ticket.html')


#django json view details ticket
from django.http import JsonResponse

@login_required
def ticket_detail_json(request, pk):
    ticket = Ticket.objects.get(pk=pk, technician=request.user)
    data = {
        'id': ticket.id,
        'title': ticket.title,
        'description': ticket.description,
        'priority': ticket.priority,
        'status': ticket.status,
        'created_at': ticket.created_at.strftime('%Y-%m-%d'),
        'client': ticket.client.name,
        'issue_description': ticket.issue_description or '',
        'solution': ticket.solution or '',
        'signoff_attachment': ticket.signoff_attachment or '',
    }
    return JsonResponse(data)



from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from core.models import Ticket

@csrf_exempt
@login_required
def complete_ticket(request):
    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        issue_description = request.POST.get('issue_description')
        solution = request.POST.get('solution')
        signoff_file = request.FILES.get('signoff_attachment')

        if not issue_description or not solution:
            return JsonResponse({'error': '⚠️ Issue and solution are required.'}, status=400)

        try:
            ticket = Ticket.objects.get(pk=ticket_id, technician=request.user)
        except Ticket.DoesNotExist:
            return JsonResponse({'error': 'Ticket not found or unauthorized.'}, status=404)

        # Update ticket
        ticket.issue_description = issue_description
        ticket.solution = solution
        ticket.status = 'pending_approval'
        if signoff_file:
            ticket.signoff_attachment = signoff_file.name  # You can improve file handling later
        ticket.save()

        # ✅ Only send email if technician enabled notifications
        technician = request.user
        if technician.email_notifications_enabled and technician.notify_on_completion:
            try:
                send_mail(
                    subject=f"Confirmation: Ticket #{ticket.id} Completed",
                    message=f"You have successfully completed Ticket #{ticket.id} - '{ticket.title}'.\n\n"
                            f"Issue: {issue_description}\n"
                            f"Solution: {solution}\n\n"
                            f"Thank you for your effort!",
                    from_email='manzonjogu91@gmail.com',
                    recipient_list=[technician.email],
                    fail_silently=False,
                )
            except Exception as e:
                print("Email send failed:", e)

        return JsonResponse({'message': '✅ Ticket completed successfully!'})

#profile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from core.models import Ticket

@login_required
def profile_view(request):
    user = request.user
    tickets = Ticket.objects.filter(creator=user).order_by('-created_at')
    status_filter = request.GET.get('status')

    if status_filter:
        tickets = tickets.filter(status=status_filter)

    password_form = PasswordChangeForm(user=user)

    if request.method == "POST":
        if "change_password" in request.POST:
            password_form = PasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, "✅ Password changed successfully.")
            else:
                messages.error(request, "⚠️ Please correct the password error below.")

        elif "update_profile" in request.POST:
            user.username = request.POST.get("username")
            user.email = request.POST.get("email")
            user.save()
            messages.success(request, "✅ Profile updated successfully.")

        elif "update_notifications" in request.POST:
            user.email_notifications_enabled = bool(request.POST.get("enable_email"))
            user.notify_on_assignment = bool(request.POST.get("notify_assignment"))
            user.notify_on_completion = bool(request.POST.get("notify_completion"))
            user.save()
            messages.success(request, "✅ Email preferences updated.")


    return render(request, "employeeportal/profile.html", {
        "user": user,
        "tickets": tickets,
        "status_filter": status_filter,
        "password_form": password_form
    })



#settings view
from django.contrib.auth.decorators import login_required

@login_required
def settings_view(request):
    section = request.GET.get('section', 'general')

    if request.method == 'POST' and section == 'email':
        user = request.user
        user.email_notifications_enabled = 'enable_email' in request.POST
        user.notify_on_assignment = 'notify_assignment' in request.POST if user.email_notifications_enabled else False
        user.notify_on_completion = 'notify_completion' in request.POST if user.email_notifications_enabled else False
        user.save()
        messages.success(request, "✅ Email notification settings updated.")
        return redirect(f"{request.path}?section=email")

    return render(request, 'employeeportal/settings.html', {
        'section': section,
        'user': request.user,  # ✅ Pass user to template for checkbox rendering
    })


#notifications and messages views
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import Notification, Message

@login_required
def notifications_view(request):
    notifications = request.user.notifications.order_by('-created_at')
    
    # ✅ Flash message
    messages.info(request, f"You have {notifications.filter(is_read=False).count()} new notification(s).")
    
    # Optionally mark them as read
    notifications.update(is_read=True)

    return render(request, 'employeeportal/notifications.html', {'notifications': notifications})

@login_required
def messages_view(request):
    messages_list = request.user.received_messages.order_by('-created_at')

    # ✅ Flash message
    messages.success(request, f"You have {messages_list.filter(is_read=False).count()} new message(s).")
    
    # Optionally mark them as read
    messages_list.update(is_read=True)

    return render(request, 'employeeportal/messages.html', {'messages': messages_list})


# views.py

@login_required
def email_notification_settings(request):
    user = request.user

    if request.method == 'POST':
        enable_all = 'enable_email' in request.POST
        notify_assignment = 'notify_assignment' in request.POST
        notify_completion = 'notify_completion' in request.POST

        user.email_notifications_enabled = enable_all
        user.notify_on_assignment = notify_assignment if enable_all else False
        user.notify_on_completion = notify_completion if enable_all else False
        user.save()

        messages.success(request, "✅ Notification preferences updated.")

    return render(request, 'partials/email.html')  # or wherever your form lives
