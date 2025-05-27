from django.urls import path
from . import views

app_name = 'flowlyne'

urlpatterns = [
    # Frontend views
    path('', views.index, name='index'),
    path('services/', views.services, name='services'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # API endpoints
    path('api/register/', views.api_register, name='api_register'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/companies/', views.api_companies, name='api_companies'),
    path('api/companies/<uuid:company_id>/', views.api_company_detail, name='api_company_detail'),
    path('api/departments/', views.api_departments, name='api_departments'),
    path('api/stats/', views.api_stats, name='api_stats'),
    path('api/messages/', views.api_send_message, name='api_send_message'),
]