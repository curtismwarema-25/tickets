from .models import Notification, Message, MessageThread, Ticket

def header_data(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
        unread_count = unread_notifications.count()
        threads = MessageThread.objects.filter(participants=request.user)
        messages = Message.objects.filter(thread__in=threads, is_read=False).exclude(sender=request.user).order_by('-created_at')[:5]
        
        # Ticket counts for sidebar
        user_tickets = Ticket.objects.filter(technician=request.user)
        total_tickets = user_tickets.count()
        open_tickets = user_tickets.filter(status='pending').count()
        my_tickets = user_tickets.count()  # Same as total since we're filtering by technician
        closed_tickets = user_tickets.filter(status='completed').count()
        
        # Overdue tickets
        from django.utils import timezone
        overdue_tickets = user_tickets.filter(
            deadline__lt=timezone.now().date(), 
            status__in=['pending', 'in_progress']
        ).count()
        
    else:
        notifications = []
        unread_notifications = []
        unread_count = 0
        messages = []
        total_tickets = 0
        open_tickets = 0
        my_tickets = 0
        closed_tickets = 0
        overdue_tickets = 0

    return {
        'header_notifications': notifications,
        'header_unread_notifications': unread_notifications,
        'header_unread_count': unread_count,
        'header_messages': messages,
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'my_tickets': my_tickets,
        'closed_tickets': closed_tickets,
        'overdue_tickets': overdue_tickets,
    }
