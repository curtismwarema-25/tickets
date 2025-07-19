from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings


# Custom User Manager
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra_fields)

#add bio data user
# Custom User Model
# Custom User Model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
  # if you have a custom manager

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('employee', 'Employee'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    username = models.CharField(max_length=150, unique=False, blank=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    specialization = models.CharField(max_length=100, blank=True, null=True)  # ✅ new
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    # NEW FIELDS: Email Preferences
    email_notifications_enabled = models.BooleanField(default=False)
    notify_on_assignment = models.BooleanField(default=False)
    notify_on_completion = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    

    def __str__(self):
        return f"{self.email} ({self.role})"


class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    company = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),                # Ticket created but not worked on
        ('pending_approval', 'Pending Approval'),  # Technician completed and submitted
        ('completed', 'Completed'),            # Admin approved the solution
        ('rejected', 'Rejected'),              # Admin rejected the solution
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='created_tickets',
        on_delete=models.CASCADE
    )
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='assigned_tickets',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    deadline = models.DateTimeField(null=True, blank=True)
    
    # UPDATED HERE
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    issue_description = models.TextField(null=True, blank=True)
    solution = models.TextField(null=True, blank=True)
    signoff_attachment = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# Notification Model
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    content = models.TextField()
    url = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification for {self.user.email}'


# Message Thread Model
class MessageThread(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message Thread between {", ".join([p.email for p in self.participants.all()])}'


# Message Model
class Message(models.Model):
    thread = models.ForeignKey('MessageThread', on_delete=models.CASCADE, null=True, blank=True)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Message from {self.sender.email}'


# Email Log Model
class EmailLog(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    recipients = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=32, default='sent')

    def __str__(self):
        return f'EmailLog: {self.subject} to {self.recipients}'

class EmailNotificationSetting(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='email_notification_setting')
    enabled = models.BooleanField(default=True)
    notify_on_assignment = models.BooleanField(default=True)
    notify_on_completion = models.BooleanField(default=True)
    notify_on_status_change = models.BooleanField(default=True)
    notify_on_approval = models.BooleanField(default=True)
    notify_on_rejection = models.BooleanField(default=True)
    notify_on_reassignment = models.BooleanField(default=True)
    notify_on_employee_status = models.BooleanField(default=True)

    def __str__(self):
        return f"EmailNotificationSetting for {self.user.email}"

class SystemSetting(models.Model):
    system_name = models.CharField(max_length=100, default="Ticket Management System")
    system_logo = models.ImageField(upload_to="system_logos/", null=True, blank=True)
    theme = models.CharField(max_length=10, choices=[('light','Light'),('dark','Dark'),('auto','Auto')], default='light')
    default_priority = models.CharField(max_length=10, choices=Ticket.PRIORITY_CHOICES, default='medium')
    default_status = models.CharField(max_length=20, choices=Ticket.STATUS_CHOICES, default='pending')
    working_hours = models.CharField(max_length=30, default="09:00 - 17:00")
    timezone = models.CharField(max_length=50, default="UTC")
    date_format = models.CharField(max_length=20, default="d/m/Y")
    language = models.CharField(max_length=10, default="en")
    notification_method = models.CharField(max_length=20, choices=[('email','Email'),('sms','SMS'),('push','Push Notification')], default='email')
    password_policy = models.CharField(max_length=20, choices=[('standard','Standard'),('strong','Strong'),('custom','Custom')], default='standard')
    maintenance_mode = models.BooleanField(default=False)

    def __str__(self):
        return self.system_name

