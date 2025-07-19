from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('accounts/login/', views.user_login, name='account_login'),  # Add Django's default admin login URL
    path('logout/', views.user_logout, name='logout'),
]
