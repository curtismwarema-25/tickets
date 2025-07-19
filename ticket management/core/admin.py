from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from .models import User, Client, Ticket, Notification, Message



from .models import (
    User, Client, Ticket, Notification, Message
)

# --- Custom User Admin ---
class CustomUserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'username', 'role', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_staff', 'is_superuser')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('username', 'first_name', 'last_name')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Role info'), {'fields': ('role',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role', 'is_staff', 'is_superuser'),
        }),
    )

    search_fields = ('email', 'username')
    ordering = ('email',)



# --- Ticket Admin with Notification + Email ---
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'status', 'technician')

    def save_model(self, request, obj, form, change):
        is_new_assignment = False

        # Check if technician has changed
        if change:
            old_obj = Ticket.objects.get(pk=obj.pk)
            if old_obj.technician != obj.technician and obj.technician:
                is_new_assignment = True
        elif obj.technician:
            is_new_assignment = True

        # Set the creator for new tickets
        if not obj.pk:
            obj.created_by = request.user

        # Save the model
        super().save_model(request, obj, form, change)

        # Notify technician and send email if preferences allow
        if is_new_assignment and obj.technician:
            # Create an in-app notification
            Notification.objects.create(
                user=obj.technician,
                content=f"You have been assigned to Ticket #{obj.id}: '{obj.title}'"
            )

            # ✅ Respect technician’s email settings
            if (
                obj.technician.email_notifications_enabled and
                obj.technician.notify_on_assignment
            ):
                try:
                    send_mail(
                        subject="New Ticket Assignment",
                        message=f"You have been assigned to Ticket #{obj.id}: '{obj.title}'.\n\nPlease log in to view the details.",
                        from_email="manzonjogu91@gmail.com",
                        recipient_list=[obj.technician.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    self.message_user(request, f"Email sending failed: {e}", level='error')


# Register everything
admin.site.register(User, CustomUserAdmin)
admin.site.register(Client)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(Notification)
admin.site.register(Message)