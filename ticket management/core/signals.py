# core/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Ticket, Client, User, Notification
from core.utils.email_utils import send_notification_email

@receiver(post_save, sender=Ticket)
def ticket_post_save(sender, instance, created, **kwargs):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    admins = User.objects.filter(role='admin')
    # New Ticket Created
    if created:
        for admin in admins:
            Notification.objects.create(
                user=admin,
                content=f"New Ticket Created: {instance.title}",
                url=f"/admin/tickets/{instance.id}/"
            )
        if instance.technician:
            Notification.objects.create(
                user=instance.technician,
                content=f"New Ticket Assigned: {instance.title}",
                url=f"/admin/tickets/{instance.id}/"
            )
        Notification.objects.create(
            user=instance.creator,
            content=f"Ticket Created: {instance.title}",
            url=f"/admin/tickets/{instance.id}/"
        )
    # Ticket Updated: Status Change or Completion
    else:
        old_ticket = Ticket.objects.get(pk=instance.pk)
        if old_ticket.status != instance.status:
            Notification.objects.create(
                user=instance.creator,
                content=f"Ticket Status Changed: {instance.title} ({old_ticket.status} → {instance.status})",
                url=f"/admin/tickets/{instance.id}/"
            )
        if instance.status == "approved":
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    content=f"Ticket Approved: {instance.title}",
                    url=f"/admin/tickets/{instance.id}/"
                )
        if instance.status == "rejected":
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    content=f"Ticket Rejected: {instance.title}",
                    url=f"/admin/tickets/{instance.id}/"
                )
        if old_ticket.technician != instance.technician:
            Notification.objects.create(
                user=instance.technician,
                content=f"Ticket Reassigned: {instance.title}",
                url=f"/admin/tickets/{instance.id}/"
            )

@receiver(post_save, sender=Client)
def client_post_save(sender, instance, created, **kwargs):
    if created:
        # Try to associate with the latest admin user if possible
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin_user = User.objects.filter(role='admin').order_by('-id').first()
        Notification.objects.create(
            user=admin_user if admin_user else None,
            content=f"New Client Added: {instance.name}",
            url=f"/admin/clients/{instance.id}/"
        )

@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    if created and instance.role == 'employee':
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admins = User.objects.filter(role='admin')
        for admin in admins:
            Notification.objects.create(
                user=admin,
                content=f"New Employee Created: {instance.username}",
                url=f"/admin/employees/{instance.id}/"
            )
    elif not created and instance.status == "inactive":
        Notification.objects.create(
            user=instance,
            content=f"Employee Status Toggled Inactive: {instance.username}",
            url=f"/admin/employees/{instance.id}/"
        )
