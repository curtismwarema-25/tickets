from django.urls import path
from . import views

app_name = 'adminportal'

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    
    path('clients/', views.clients_view, name='clients'),
    path('clients/add/', views.add_client, name='add_client'),
    path('clients/edit/', views.edit_client, name='edit_client'),
    path('clients/delete/<int:client_id>/', views.delete_client, name='delete_client'),
    
    path('employees/', views.employees_view, name='employees'),
    path('add-employee/', views.add_employee, name='add_employee'),
    path('delete-employee/<int:employee_id>/', views.delete_employee, name='delete_employee'),
    path('edit-employee/', views.edit_employee, name='edit_employee'),
    path('toggle-employee-status/<int:employee_id>/', views.toggle_employee_status, name='toggle_employee_status'),
    
    path('tickets/', views.tickets_view, name='tickets'),
    path('tickets/edit/', views.edit_ticket, name='edit_ticket'),
    path('tickets/delete/', views.delete_ticket, name='delete_ticket'),
    path('tickets/create/', views.create_ticket, name='create_ticket'),
    path('tickets/approve/<int:ticket_id>/', views.approve_ticket, name='approve_ticket'),
    path('tickets/reject/<int:ticket_id>/', views.reject_ticket, name='reject_ticket'),
    path('tickets/update/', views.update_ticket, name='update_ticket'),
    
    path('tickets/bulk-delete/', views.bulk_delete_tickets, name='bulk_delete_tickets'),
    
    path('profile-settings/', views.profile_settings, name='profile_settings'),
    path('settings/', views.settings_view, name='settings'),
    
    path('search/', views.global_search, name='global_search'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('messages/', views.messages_view, name='messages'),
    path('emails/', views.emails_view, name='emails'),
    path('mark_all_notifications_read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('mark_all_messages_read/', views.mark_all_messages_read, name='mark_all_messages_read'),
    path('delete_all_notifications/', views.delete_all_notifications, name='delete_all_notifications'),
    path('delete_selected_messages/', views.delete_selected_messages, name='delete_selected_messages'),
    path('compose_message/', views.compose_message, name='compose_message'),
    path('message_thread/<int:thread_id>/', views.message_thread, name='message_thread'),
    path('mark_notification_read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('delete_notification/<int:notification_id>/', views.delete_notification, name='delete_notification'),
]
