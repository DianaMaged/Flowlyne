from django.urls import path
from . import views

app_name = 'flowlyne'

urlpatterns = [
    # Frontend views
    path('', views.index, name='index'),
    path('services/', views.services, name='services'),
    path('plans/', views.plans, name='plans'),
    path('payment/', views.payment, name='payment'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('offering/', views.offering_view, name='offering'),
    path('profile/<int:company_id>/', views.company_profile, name='company_profile'),
    
    # API endpoints
    path('api/register/', views.api_register, name='api_register'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/companies/', views.api_companies, name='api_companies'),
    path('api/companies/<int:company_id>/', views.api_company_detail, name='api_company_detail'),
    path('api/categories/', views.api_categories, name='api_categories'),
    path('api/stats/', views.api_stats, name='api_stats'),
    path('api/platform-stats/', views.api_platform_stats, name='api_platform_stats'),
    path('api/messages/', views.api_send_message, name='api_send_message'),
    path('api/subscription-plans/', views.api_subscription_plans, name='api_subscription_plans'),
    path('api/upgrade/', views.api_upgrade_subscription, name='api_upgrade_subscription'),
    path('api/services/', views.api_company_services, name='api_company_services'),
    path('api/services/create/', views.api_create_service, name='api_create_service'),
    path('api/services/<int:service_id>/', views.api_service_detail, name='api_service_detail'),
    path('api/services/all/', views.api_all_services, name='api_all_services'),
    path('api/services/categories/', views.api_service_categories, name='api_service_categories'),
]