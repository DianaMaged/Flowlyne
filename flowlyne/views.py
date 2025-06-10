from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Avg, Count
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import check_password
from .serializers import (
    ServiceSerializer, ServiceCreateSerializer, CompanyRegistrationSerializer,
    CompanyLoginSerializer, CompanyListSerializer, CompanyDetailSerializer,
    ReviewSerializer, SubscriptionPlanSerializer, PaymentSerializer,
    CompanySubscriptionSerializer, AdvertisingSerializer, StatsSerializer,
    CategorySerializer
)
import json
import logging

from .models import Company, Service, Category, Admin, SubscriptionPlan, Review, Payment

logger = logging.getLogger(__name__)


# ================================
# FRONTEND VIEWS - SIMPLE AUTHENTICATION
# ================================

def index(request):
    """Home page"""
    logger.info(f"Index page accessed. User authenticated: {request.user.is_authenticated}")
    return render(request, 'index.html')


def services(request):
    """Services page"""
    logger.info(f"Services page accessed. User authenticated: {request.user.is_authenticated}")
    return render(request, 'services.html')


def register_view(request):
    """Register page"""
    logger.info(f"Register page accessed. User authenticated: {request.user.is_authenticated}")
    return render(request, 'register.html')


def login_view(request):
    """Login page"""
    if request.user.is_authenticated:
        return redirect('flowlyne:dashboard')

    logger.info(f"Login page accessed. User authenticated: {request.user.is_authenticated}")
    return render(request, 'login.html')

def logout_view(request):
    """Logout and redirect to home"""
    if request.user.is_authenticated:
        logger.info(f"User logout: {request.user.company_name}")
        logout(request)
    return redirect('flowlyne:index')


@login_required
def dashboard(request):
    """Dashboard page - requires authentication"""
    logger.info(f"Dashboard accessed by: {request.user.company_name}")
    return render(request, 'dashboard.html')


def about(request):
    """About page"""
    logger.info(f"About page accessed. User authenticated: {request.user.is_authenticated}")
    return render(request, 'about.html')


def plans(request):
    """Plans page"""
    logger.info(f"Plans page accessed. User authenticated: {request.user.is_authenticated}")
    return render(request, 'plans.html')


@login_required
def payment(request):
    """Payment page - requires authentication"""
    logger.info(f"Payment page accessed by: {request.user.company_name}")
    return render(request, 'payment.html')


@login_required
def offering_view(request):
    """Offering services page - requires authentication"""
    logger.info(f"Offering page accessed by: {request.user.company_name}")
    return render(request, 'offering.html')


def company_profile(request, company_id):
    """Company profile page"""
    logger.info(f"Company profile page accessed for company ID: {company_id}")
    return render(request, 'company_profile.html', {'company_id': company_id})


# ================================
# API VIEWS 
# ================================

@csrf_exempt
def api_login(request):
    """API Login endpoint - for JavaScript/AJAX requests"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    try:
        # Parse request data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST

        email = data.get('email', '').strip()
        password = data.get('password', '')

        logger.info(f"API Login attempt for email: {email}")

        if not email or not password:
            return JsonResponse({'error': 'Email and password are required'}, status=400)

        try:
            # Find company by email to get username
            company = Company.objects.get(email__iexact=email)
            logger.info(f"Found company: {company.company_name}, username: {company.username}")

            # Check if account is active
            if not company.is_active:
                logger.warning(f"Inactive account login attempt: {email}")
                return JsonResponse({'error': 'Account is disabled'}, status=400)

            # Authenticate using username
            user = authenticate(request, username=company.username, password=password)

            if user is not None:
                # Log them into Django session
                login(request, user)
                logger.info(f"API Login session created for: {user.company_name}")

                # Get or create auth token for API usage
                token, created = Token.objects.get_or_create(user=company)

                # Prepare company data for response
                company_data = {
                    'company_id': company.company_id,
                    'company_name': company.company_name,
                    'email': company.email,
                    'current_plan': company.current_plan,
                    'is_verified': company.is_verified
                }

                return JsonResponse({
                    'message': 'Login successful',
                    'company': company_data,
                    'token': token.key
                })
            else:
                logger.warning(f"Authentication failed for: {email}")
                return JsonResponse({'error': 'Invalid email or password'}, status=400)

        except Company.DoesNotExist:
            logger.warning(f"Login attempt for non-existent email: {email}")
            return JsonResponse({'error': 'Invalid email or password'}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
def api_register(request):
    """API Register endpoint - for JavaScript/AJAX requests"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST

        logger.info(f"Registration attempt for: {data.get('email')}")

        serializer = CompanyRegistrationSerializer(data=data)
        if serializer.is_valid():
            company = serializer.save()
            logger.info(f"Company registered successfully: {company.company_name}")

            # Prepare response data
            company_data = {
                'company_id': company.company_id,
                'company_name': company.company_name,
                'email': company.email,
                'current_plan': company.current_plan,
                'is_verified': company.is_verified
            }

            return JsonResponse({
                'message': 'Registration successful',
                'company': company_data
            }, status=201)
        else:
            logger.warning(f"Registration validation failed: {serializer.errors}")
            return JsonResponse({'error': serializer.errors}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


# API view to get companies
def api_companies(request):
    try:
        # Get query parameters
        search_query = request.GET.get('search', '').strip()
        category_filter = request.GET.get('category', '').strip()

        # Start with active companies
        companies = Company.objects.filter(is_active=True)

        # Apply category filter if provided
        if category_filter:
            companies = companies.filter(services__category__icontains=category_filter).distinct()
            logger.info(f"Category filter applied: {category_filter}, found {companies.count()} companies")

        # Apply search filter if provided
        if search_query:
            companies = companies.filter(
                Q(company_name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(city__icontains=search_query) |
                Q(country__icontains=search_query) |
                Q(services__category__icontains=search_query) |
                Q(services__service_name__icontains=search_query)
            ).distinct()
            logger.info(f"Search performed for: {search_query}, found {companies.count()} companies")

        # Order by verification status and creation date
        companies = companies.order_by('-is_verified', '-created_at')

        serializer = CompanyListSerializer(companies, many=True)
        return JsonResponse({'companies': serializer.data})

    except Exception as e:
        logger.error(f"Error fetching companies: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


# API view to get company details
def api_company_detail(request, company_id):
    try:
        # First check if company exists
        if not Company.objects.filter(company_id=company_id).exists():
            logger.warning(f"Company with ID {company_id} does not exist")
            return JsonResponse({'error': 'Company not found'}, status=404)

        # Get the company (removed is_active filter to be safe)
        company = get_object_or_404(Company, company_id=company_id)

        # Check if company is active
        if not company.is_active:
            logger.warning(f"Inactive company requested: {company.company_name} (ID: {company_id})")
            return JsonResponse({'error': 'Company not found'}, status=404)

        # Serialize the company data
        serializer = CompanyDetailSerializer(company)

        # Log successful profile view
        logger.info(f"Company profile viewed: {company.company_name} (ID: {company_id})")

        return JsonResponse({'company': serializer.data})

    except Exception as e:
        logger.error(f"Error fetching company details for ID {company_id}: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


# API view to get categories
def api_categories(request):
    try:
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return JsonResponse({'categories': serializer.data})
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


# API view to get dashboard stats
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_stats(request):
    try:
        company = request.user

        # Get company's services
        services = Service.objects.filter(company=company)

        # Calculate stats
        stats = {
            'total_services': services.count(),
            'active_services': services.count(),  # Same as total since no is_active field
            'total_reviews': Review.objects.filter(service__company=company).count(),
            'average_rating': Review.objects.filter(service__company=company).aggregate(
                avg_rating=Avg('rating')
            )['avg_rating'] or 0,
            'current_plan': company.current_plan,
            'is_verified': company.is_verified
        }

        return Response({'stats': stats})
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        return Response({'error': 'Internal server error'}, status=500)


# API view to send messages (contact form)
@csrf_exempt
def api_send_message(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    try:
        data = json.loads(request.body)
        # Here you would typically save the message to database
        # or send an email
        logger.info(f"Message received from {data.get('email')}")
        return JsonResponse({'message': 'Message sent successfully'})
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


# API view to get subscription plans
def api_subscription_plans(request):
    try:
        plans = SubscriptionPlan.objects.all()
        serializer = SubscriptionPlanSerializer(plans, many=True)
        return JsonResponse({'plans': serializer.data})
    except Exception as e:
        logger.error(f"Error fetching subscription plans: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


# API view to upgrade subscription
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_upgrade_subscription(request):
    try:
        plan_id = request.data.get('plan_id')
        if not plan_id:
            return Response({'error': 'Plan ID is required'}, status=400)

        plan = get_object_or_404(SubscriptionPlan, plan_id=plan_id)
        company = request.user

        # Update company's current plan
        company.current_plan = plan.plan_name
        company.save()

        # Create payment record
        Payment.objects.create(
            company=company,
            plan=plan,
            amount=plan.price,
            payment_method='credit_card',  # Default for now
            status='completed'
        )

        return Response({'message': 'Subscription upgraded successfully'})
    except Exception as e:
        logger.error(f"Error upgrading subscription: {str(e)}")
        return Response({'error': 'Internal server error'}, status=500)


# API view to get company's services
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_company_services(request):
    try:
        company = request.user
        services = Service.objects.filter(company=company)
        serializer = ServiceSerializer(services, many=True)
        return Response({'services': serializer.data})
    except Exception as e:
        logger.error(f"Error fetching company services: {str(e)}")
        return Response({'error': 'Internal server error'}, status=500)


# API view to create a new service
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_create_service(request):
    try:
        company = request.user
        data = request.data.copy()
        data['company'] = company.company_id

        serializer = ServiceCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Service created successfully', 'service': serializer.data}, status=201)
        else:
            return Response({'error': serializer.errors}, status=400)
    except Exception as e:
        logger.error(f"Error creating service: {str(e)}")
        return Response({'error': 'Internal server error'}, status=500)


# FIXED: API view to handle service details with GET, PUT, DELETE
@csrf_exempt
def api_service_detail(request, service_id):
    """Handle service detail operations: GET, PUT, DELETE"""
    try:
        # Get the service and check ownership if user is authenticated
        service = get_object_or_404(Service, service_id=service_id)
        
        # For PUT and DELETE, require authentication and ownership
        if request.method in ['PUT', 'DELETE']:
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            if service.company != request.user:
                return JsonResponse({'error': 'Permission denied'}, status=403)
        
        if request.method == 'GET':
            # Get service details
            serializer = ServiceSerializer(service)
            return JsonResponse({'service': serializer.data})
            
        elif request.method == 'PUT':
            # Update service
            try:
                data = json.loads(request.body)
                logger.info(f"Updating service {service_id} with data: {data}")
                
                # Update service fields
                if 'service_name' in data:
                    service.service_name = data['service_name']
                if 'service_description' in data:
                    service.service_description = data['service_description']
                if 'price' in data:
                    service.price = float(data['price'])
                if 'category' in data:
                    service.category = data['category']
                if 'duration' in data:
                    service.duration = data['duration']
                
                service.save()
                logger.info(f"Service {service_id} updated successfully")
                
                serializer = ServiceSerializer(service)
                return JsonResponse({
                    'message': 'Service updated successfully', 
                    'service': serializer.data
                })
                
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON format'}, status=400)
            except ValueError as e:
                return JsonResponse({'error': f'Invalid data format: {str(e)}'}, status=400)
                
        elif request.method == 'DELETE':
            # Delete service
            service_name = service.service_name
            service.delete()
            logger.info(f"Service '{service_name}' (ID: {service_id}) deleted successfully")
            return JsonResponse({'message': 'Service deleted successfully'})
            
    except Service.DoesNotExist:
        logger.warning(f"Service with ID {service_id} does not exist")
        return JsonResponse({'error': 'Service not found'}, status=404)
    except Exception as e:
        logger.error(f"Error handling service detail request: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


# API view to get all services (for public listing)
def api_all_services(request):
    try:
        services = Service.objects.all().select_related('company')

        # Filter by company if specified
        company_name = request.GET.get('company_name')
        if company_name:
            services = services.filter(company__company_name=company_name)

        serializer = ServiceSerializer(services, many=True)
        return JsonResponse({'services': serializer.data})
    except Exception as e:
        logger.error(f"Error fetching all services: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


# API view to get service categories
def api_service_categories(request):
    try:
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return JsonResponse({'categories': serializer.data})
    except Exception as e:
        logger.error(f"Error fetching service categories: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


def api_platform_stats(request):
    try:
        # Get platform-wide statistics
        stats = {
            'total_companies': Company.objects.filter(is_active=True).count(),
            'verified_companies': Company.objects.filter(is_active=True, is_verified=True).count(),
            'total_services': Service.objects.count(),
            'total_reviews': Review.objects.count(),
            'average_platform_rating': Review.objects.aggregate(
                avg_rating=Avg('rating')
            )['avg_rating'] or 4.5,
            'new_companies_this_month': Company.objects.filter(
                is_active=True,
                created_at__month=timezone.now().month,
                created_at__year=timezone.now().year
            ).count(),
        }

        logger.info(f"Platform stats requested: {stats}")
        return JsonResponse({'stats': stats})

    except Exception as e:
        logger.error(f"Error fetching platform stats: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)