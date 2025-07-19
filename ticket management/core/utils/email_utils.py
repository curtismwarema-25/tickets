# core/utils/email_utils.py

from django.core.mail import send_mail

def send_notification_email(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        None,  
        recipient_list,
        fail_silently=False,
    )


from core.models import EmailNotificationSetting

def get_email_settings():
    return EmailNotificationSetting.objects.first()