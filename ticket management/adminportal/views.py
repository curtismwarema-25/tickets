from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from core.models import Ticket, Client, User, Notification, SystemSetting
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Count, Q, Avg, DurationField, ExpressionWrapper, F, Case, When, Value, IntegerField
from datetime import datetime
from django.http import JsonResponse
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@user_passes_test(is_admin)
@login_required
def admin_dashboard(request):
    total_tickets = Ticket.objects.count()
    completed_tickets = Ticket.objects.filter(status='completed').count()
    pending_tickets = Ticket.objects.filter(status='pending').count()
    high_priority_tickets = Ticket.objects.filter(priority='high').count()

    top_clients = Client.objects.annotate(ticket_count=Count('ticket')).order_by('-ticket_count')[:3]
    
    technician_workload = User.objects.filter(role='employee').annotate(
        ticket_count=Count('assigned_tickets')
    ).order_by('-ticket_count')

    recent_activity = Ticket.objects.order_by('-created_at')[:5]

    context = {
        'total_tickets': total_tickets,
        'completed_tickets': completed_tickets,
        'pending_tickets': pending_tickets,
        'high_priority_tickets': high_priority_tickets,
        'top_clients': top_clients,
        'technician_workload': technician_workload,
        'recent_activity': recent_activity,
    }
    return render(request, 'adminportal/dashboard.html', context)

@user_passes_test(is_admin)
def clients_view(request):
    query = request.GET.get('q', '')
    company_filter = request.GET.get('company')
    clients_list = Client.objects.annotate(ticket_count=Count('ticket')).order_by('-ticket_count')

    if query:
        clients_list = clients_list.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(company__icontains=query)
        )
    
    if company_filter and company_filter != 'all':
        clients_list = clients_list.filter(company=company_filter)

    total_clients = Client.objects.count()
    total_tickets = Ticket.objects.count()
    avg_tickets_per_client = total_tickets / total_clients if total_clients > 0 else 0

    context = {
        'clients': clients_list,
        'total_clients': total_clients,
        'total_tickets': total_tickets,
        'avg_tickets_per_client': round(avg_tickets_per_client, 1),
        'search_query': query,
        'company_filter': company_filter,
        'companies': Client.objects.values_list('company', flat=True).distinct(),
    }
    return render(request, 'adminportal/clients.html', context)

@user_passes_test(is_admin)
def add_client(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        company = request.POST.get('company')
        if name and email and phone and company:
            Client.objects.create(name=name, email=email, phone=phone, company=company)
            messages.success(request, f"Client '{name}' was successfully added.")
        return redirect('adminportal:clients')

@user_passes_test(is_admin)
def edit_client(request):
    if request.method == 'POST':
        client = get_object_or_404(Client, id=request.POST['client_id'])
        client.name = request.POST['name']
        client.email = request.POST['email']
        client.phone = request.POST['phone']
        client.company = request.POST['company']
        client.save()
        messages.success(request, "Client updated successfully.")
    return redirect('adminportal:clients')

@user_passes_test(is_admin)
def delete_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    client.delete()
    messages.success(request, "Client deleted successfully.")
    return redirect('adminportal:clients')

@user_passes_test(is_admin)
def employees_view(request):
    employees = User.objects.filter(role='employee')
    for emp in employees:
        emp.display_password = getattr(emp, '_plain_password', None)
    
    # Calculate statistics
    total_employees = employees.count()
    total_tickets = Ticket.objects.count()
    avg_tickets_per_employee = total_tickets / total_employees if total_employees > 0 else 0
    
    # Find top performer (employee with most assigned tickets)
    top_performer = employees.annotate(
        ticket_count=Count('assigned_tickets')
    ).order_by('-ticket_count').first()
    
    context = {
        'employees': employees,
        'total_employees': total_employees,
        'total_tickets': total_tickets,
        'avg_tickets_per_employee': round(avg_tickets_per_employee, 1),
        'top_performer': top_performer,
    }
    
    return render(request, 'adminportal/employees.html', context)

def add_employee(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        specialization = request.POST.get('specialization')
        role = request.POST.get('role')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('adminportal:employees')
        password = request.POST.get('password')
        user = User.objects.create_user(
            username=name, email=email, role=role, specialization=specialization, password=password
        )
        user._plain_password = password
        user.save()
        messages.success(request, 'Employee added successfully!')
        return redirect('adminportal:employees')

def delete_employee(request, employee_id):
    employee = get_object_or_404(User, id=employee_id)
    if request.method == 'POST':
        employee_name = employee.username
        employee.delete()
        messages.success(request, f'Employee {employee_name} has been deleted successfully.')
    return redirect('adminportal:employees')

def edit_employee(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        employee = get_object_or_404(User, id=employee_id, role='employee')
        employee.username = request.POST.get('name')
        employee.email = request.POST.get('email')
        employee.specialization = request.POST.get('specialization')
        employee.status = request.POST.get('status')
        employee.save()
        messages.success(request, 'Employee updated successfully!')
        return redirect('adminportal:employees')

def toggle_employee_status(request, employee_id):
    if request.method == 'POST':
        employee = get_object_or_404(User, id=employee_id, role='employee')
        new_status = request.POST.get('status')
        if new_status in ['active', 'inactive']:
            employee.status = new_status.capitalize()
            employee.save()
            messages.success(request, f'Employee status updated to {employee.status}.')
        else:
            messages.error(request, 'Invalid status provided.')
    return redirect('adminportal:employees')

def tickets_view(request):
    tickets = Ticket.objects.select_related('creator', 'technician', 'client')

    # Global Search
    query = request.GET.get('q', '').strip()
    if query:
        tickets = tickets.filter(Q(title__icontains=query) | Q(description__icontains=query))

    # Filter by Status, Priority, Assignee (from modal)
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    technician_filter = request.GET.get('technician')

    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
    if technician_filter:
        tickets = tickets.filter(technician_id=technician_filter)

    # Sorting
    sort_by = request.GET.get('sort_by', 'created_at') # Default sort by created_at
    order = request.GET.get('order', 'desc') # Default order descending

    if sort_by in ['id', 'title', 'created_at', 'deadline']:
        if order == 'desc':
            tickets = tickets.order_by(f'-{sort_by}')
        else:
            tickets = tickets.order_by(sort_by)
    else:
        # Fallback for invalid sort_by parameters
        tickets = tickets.order_by('-created_at')
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(tickets, 10) # Show 10 tickets per page

    try:
        tickets = paginator.page(page)
    except PageNotAnInteger:
        tickets = paginator.page(1)
    except EmptyPage:
        tickets = paginator.page(paginator.num_pages)
    
    clients = Client.objects.all()
    technicians = User.objects.filter(role='employee')
    
    return render(request, 'adminportal/tickets.html', {
        'tickets': tickets,
        'clients': clients,
        'technicians': technicians,
    })

def edit_ticket(request):
    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        ticket = get_object_or_404(Ticket, id=ticket_id)
        ticket.title = request.POST.get('title')
        ticket.description = request.POST.get('description')
        ticket.priority = request.POST.get('priority')
        ticket.status = request.POST.get('status')
        ticket.deadline = request.POST.get('deadline')
        tech_id = request.POST.get('technician')
        if tech_id:
            ticket.technician = get_object_or_404(User, id=tech_id)
        else:
            ticket.technician = None
        client_id = request.POST.get('client')
        if client_id:
            ticket.client = get_object_or_404(Client, id=client_id)
        ticket.save()
        messages.success(request, "Ticket updated successfully.")
    return redirect('adminportal:tickets')

def delete_ticket(request):
    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        if not ticket_id or not ticket_id.isdigit():
            messages.error(request, "Invalid or missing ticket ID.")
            return redirect('adminportal:tickets')
        ticket = get_object_or_404(Ticket, id=int(ticket_id))
        ticket.delete()
        messages.success(request, "Ticket deleted successfully.")
    return redirect('adminportal:tickets')

def create_ticket(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority')
        status = request.POST.get('status')
        deadline = request.POST.get('deadline')
        client_id = request.POST.get('client')
        technician_id = request.POST.get('technician')
        ticket = Ticket(
            title=title,
            description=description,
            priority=priority,
            status=status,
            deadline=deadline if deadline else None,
            client=get_object_or_404(Client, id=client_id),
            creator=request.user
        )
        if technician_id:
            ticket.technician = get_object_or_404(User, id=technician_id)
        ticket.save()
        messages.success(request, "Ticket created successfully.")
    return redirect('adminportal:tickets')

@require_POST
def approve_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if ticket.status == 'pending_approval':
        ticket.status = 'completed'
        ticket.save()
        messages.success(request, "Ticket approved successfully.")
    else:
        messages.warning(request, "Only tickets pending approval can be approved.")
    return redirect('adminportal:tickets')

@require_POST
def reject_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    rejection_reason = request.POST.get('rejection_reason', 'No reason provided.')
    if ticket.status == 'pending_approval':
        ticket.status = 'pending'
        ticket.save()
        if ticket.technician:
            Notification.objects.create(
                user=ticket.technician,
                content=f"Ticket #{ticket.id} was rejected. Reason: {rejection_reason}"
            )
        messages.warning(request, "Ticket has been rejected and returned to the technician.")
    else:
        messages.error(request, "Only tickets pending approval can be rejected.")
    return redirect('adminportal:tickets')

def update_ticket(request):
    if request.method == "POST":
        ticket_id = request.POST.get("ticket_id")
        ticket = get_object_or_404(Ticket, id=ticket_id)
        
        # Update ticket fields
        ticket.title = request.POST.get("title")
        ticket.description = request.POST.get("description")
        ticket.priority = request.POST.get("priority")
        ticket.deadline = request.POST.get("deadline")
        
        # Handle technician assignment
        technician_id = request.POST.get("technician")
        if technician_id:
            try:
                ticket.technician = get_object_or_404(User, id=technician_id, role='employee')
            except:
                ticket.technician = None
        else:
            ticket.technician = None
            
        ticket.save()
        
        # Check if this is an AJAX request (for Save & Keep Editing)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or "keep_editing" in request.POST:
            # Return JSON response for AJAX requests
            return JsonResponse({
                'success': True,
                'message': 'Ticket updated successfully!',
                'ticket_id': ticket.id
            })
        else:
            # Show success message for regular form submission
            messages.success(request, "Ticket updated successfully.")
            # Regular save - close modal and return to list
            return redirect('adminportal:tickets')
    else:
        return redirect('adminportal:tickets')

from django.contrib.auth import update_session_auth_hash
from .forms import ChangePasswordForm

@user_passes_test(is_admin)
def profile_settings(request):
    user = request.user
    if request.method == 'POST':
        form = ChangePasswordForm(user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('adminportal:profile_settings')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = ChangePasswordForm(user)

    completed_tickets = Ticket.objects.filter(creator=user, status='completed').count()
    pending_tickets = Ticket.objects.filter(creator=user, status='pending').count()
    
    context = {
        'user': user,
        'form': form,
        'completed_tickets': completed_tickets,
        'pending_tickets': pending_tickets,
        'user_tickets': Ticket.objects.filter(Q(creator=user) | Q(technician=user)).order_by('-created_at'),
    }
    return render(request, 'adminportal/profile_settings.html', context)

def global_search(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        tickets = Ticket.objects.filter(
            Q(title__icontains=query) | Q(client__name__icontains=query)
        )[:5]
        for t in tickets:
            results.append({
                'type': 'Ticket',
                'label': f"{t.title} (#{t.id})",
                'url': f"/admin/tickets/{t.id}/"
            })
        clients = Client.objects.filter(
            Q(name__icontains=query) | Q(email__icontains=query)
        )[:5]
        for c in clients:
            results.append({
                'type': 'Client',
                'label': c.name,
                'url': f"/admin/clients/{c.id}/"
            })
        employees = User.objects.filter(
            Q(name__icontains=query) | Q(email__icontains=query),
            role='employee'
        )[:5]
        for e in employees:
            results.append({
                'type': 'Employee',
                'label': e.name,
                'url': f"/admin/employees/{e.id}/"
            })
    return JsonResponse({'results': results})

def search_all(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'tickets': [], 'clients': [], 'employees': []})
    tickets = Ticket.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))[:5]
    clients = Client.objects.filter(Q(name__icontains=query) | Q(email__icontains=query))[:5]
    employees = User.objects.filter(
        Q(name__icontains=query) | Q(email__icontains=query), role='employee'
    )[:5]
    return JsonResponse({
        'tickets': [{'id': t.id, 'title': t.title} for t in tickets],
        'clients': [{'id': c.id, 'name': c.name} for c in clients],
        'employees': [{'id': e.id, 'name': e.name} for e in employees]
    })

@user_passes_test(is_admin)
@login_required
def settings_view(request):
    return render(request, 'adminportal/settings.html')

@user_passes_test(is_admin)
@require_POST
def bulk_delete_tickets(request):
    """
    Handle bulk deletion of selected tickets.
    Expects a list of ticket IDs in the POST data.
    """
    ticket_ids = request.POST.getlist('ticket_ids')
    
    if not ticket_ids:
        messages.error(request, "No tickets selected for deletion.")
        return redirect('adminportal:tickets')
    
    try:
        # Convert string IDs to integers and validate
        valid_ids = []
        for ticket_id in ticket_ids:
            if ticket_id.isdigit():
                valid_ids.append(int(ticket_id))
        
        if not valid_ids:
            messages.error(request, "Invalid ticket IDs provided.")
            return redirect('adminportal:tickets')
        
        # Get tickets that exist and delete them
        tickets_to_delete = Ticket.objects.filter(id__in=valid_ids)
        deleted_count = tickets_to_delete.count()
        
        if deleted_count == 0:
            messages.warning(request, "No valid tickets found to delete.")
        else:
            tickets_to_delete.delete()
            messages.success(request, f"Successfully deleted {deleted_count} ticket(s).")
            
    except Exception as e:
        messages.error(request, f"An error occurred while deleting tickets: {str(e)}")
    
    return redirect('adminportal:tickets')

@user_passes_test(is_admin)
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'adminportal/notifications.html', {'notifications': notifications})

@user_passes_test(is_admin)
def messages_view(request):
    from core.models import MessageThread, Message
    threads = MessageThread.objects.filter(participants=request.user)
    sent_messages = Message.objects.filter(sender=request.user, thread__isnull=False).order_by('-created_at')
    received_messages = Message.objects.filter(thread__in=threads, thread__isnull=False).exclude(sender=request.user).order_by('-created_at')
    all_messages = Message.objects.filter(thread__in=threads, thread__isnull=False).order_by('-created_at')
    return render(request, 'adminportal/messages.html', {
        'threads': threads,
        'sent_messages': sent_messages,
        'received_messages': received_messages,
        'all_messages': all_messages,
    })

@user_passes_test(is_admin)
def emails_view(request):
    from core.models import EmailLog
    emails = EmailLog.objects.all().order_by('-sent_at')
    return render(request, 'adminportal/emails.html', {'emails': emails})

@user_passes_test(is_admin)
@require_POST
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('adminportal:notifications')

@user_passes_test(is_admin)
@require_POST
def mark_all_messages_read(request):
    from core.models import MessageThread, Message
    threads = MessageThread.objects.filter(participants=request.user)
    Message.objects.filter(thread__in=threads, is_read=False).update(is_read=True)
    return redirect('adminportal:messages')

@user_passes_test(is_admin)
@require_POST
def delete_all_notifications(request):
    Notification.objects.filter(user=request.user).delete()
    return redirect('adminportal:notifications')

@user_passes_test(is_admin)
@require_POST
def delete_selected_messages(request):
    from core.models import Message
    ids = request.POST.getlist('selected_messages')
    if ids:
        Message.objects.filter(id__in=ids).delete()
    return redirect('adminportal:messages')

@user_passes_test(is_admin)
def compose_message(request):
    from core.models import MessageThread, Message
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient')
        content = request.POST.get('content')
        if recipient_id and content:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            recipient = User.objects.get(id=recipient_id)
            thread, created = MessageThread.objects.get_or_create()
            thread.participants.add(request.user, recipient)
            Message.objects.create(thread=thread, sender=request.user, content=content)
            return redirect('adminportal:messages')
    from django.contrib.auth import get_user_model
    User = get_user_model()
    employees = User.objects.filter(role='employee').exclude(id=request.user.id)
    return render(request, 'adminportal/compose_message.html', {'employees': employees})

@user_passes_test(is_admin)
def message_thread(request, thread_id):
    from core.models import MessageThread, Message
    thread = MessageThread.objects.get(id=thread_id)
    messages = Message.objects.filter(thread=thread).order_by('created_at')
    participants = thread.participants.exclude(id=request.user.id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(thread=thread, sender=request.user, content=content)
            return redirect('adminportal:message_thread', thread_id=thread.id)
    if request.GET.get('modal') == '1':
        from django.template.loader import render_to_string
        html = render_to_string('adminportal/message_thread_modal.html', {
            'thread': thread,
            'messages': messages,
            'participants': participants,
            'request': request,
        })
        from django.http import HttpResponse
        return HttpResponse(html)
    return render(request, 'adminportal/message_thread.html', {
        'thread': thread,
        'messages': messages,
        'participants': participants,
    })

@user_passes_test(is_admin)
@require_POST
def mark_notification_read(request, notification_id):
    from core.models import Notification
    notif = Notification.objects.get(id=notification_id, user=request.user)
    notif.is_read = True
    notif.save()
    return redirect('adminportal:notifications')

@user_passes_test(is_admin)
@require_POST
def delete_notification(request, notification_id):
    from core.models import Notification
    notif = Notification.objects.get(id=notification_id, user=request.user)
    notif.delete()
    return redirect('adminportal:notifications')
