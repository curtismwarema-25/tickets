app_name = 'employeeportal'



from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('clients/', views.employee_clients, name='employee_clients'),
    path('tickets/', views.employee_tickets, name='employee_tickets'),
    path('tickets/create/', views.employee_create_ticket, name='employee_create_ticket'),
    path('ticket/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('ticket/<int:pk>/json/', views.ticket_detail_json, name='ticket_detail_json'),
    path('ticket/complete/', views.complete_ticket, name='complete_ticket'),
    path('notifications/', views.notifications_view, name='employee_notifications'),
    path('messages/', views.messages_view, name='employee_messages'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/email/', views.email_notification_settings, name='email_settings'),
    path('settings/', views.settings_view, name='settings'),
   
]
