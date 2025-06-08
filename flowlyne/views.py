from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Avg, Count
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
    """Handle company registration via form"""
    if request.method == 'POST':
        # Get form data
        company_name = request.POST.get('company_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        description = request.POST.get('description', '').strip()
        
        logger.info(f"Registration attempt: {company_name} ({email})")
        
        # Validation
        if not all([company_name, email, password]):
            logger.warning("Registration failed: Missing required fields")
            return render(request, 'register.html', {
                'error': 'Company name, email and password are required',
                'form_data': request.POST
            })
        
        # Check if email exists
        if Company.objects.filter(email__iexact=email).exists():
            logger.warning(f"Registration failed: Email already exists - {email}")
            return render(request, 'register.html', {
                'error': 'A company with this email already exists',
                'form_data': request.POST
            })
        
        try:
            # Create company - username will be set to email automatically
            company = Company.objects.create_user(
                email=email,
                password=password,
                company_name=company_name,
                description=description,
                city='Cairo',
                country='Egypt'
            )
            
            logger.info(f"Company created successfully: {company.company_name} (username: {company.username})")
            
            # Log them in using username (which is their email)
            user = authenticate(request, username=company.username, password=password)
            if user is not None:
                login(request, user)
                logger.info(f"User logged in after registration: {user.company_name}")
                return redirect('flowlyne:dashboard')
            else:
                logger.error("Failed to authenticate user after registration")
                return render(request, 'login.html', {
                    'success': 'Registration successful! Please log in.',
                })
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return render(request, 'register.html', {
                'error': 'Registration failed. Please try again.',
                'form_data': request.POST
            })
    
    # GET request - show the form
    return render(request, 'register.html')

def login_view(request):
    """Handle company login via form"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        logger.info(f"Login attempt for: {email}")
        
        if not email or not password:
            logger.warning("Login failed: Missing email or password")
            return render(request, 'login.html', {
                'error': 'Email and password are required',
                'form_data': request.POST
            })
        
        try:
            # Find company by email to get their username
            company = Company.objects.get(email__iexact=email)
            logger.info(f"Found company: {company.company_name}, username: {company.username}, Active: {company.is_active}")
            
            if not company.is_active:
                logger.warning(f"Login failed: Account disabled - {email}")
                return render(request, 'login.html', {
                    'error': 'Your account has been disabled',
                    'form_data': request.POST
                })
            
            # Authenticate using username (which is the email)
            user = authenticate(request, username=company.username, password=password)
            logger.info(f"Authentication result: {user is not None}")
            
            if user is not None:
                login(request, user)
                logger.info(f"Login successful for: {user.company_name}")
                logger.info(f"Session key after login: {request.session.session_key}")
                
                return redirect('flowlyne:dashboard')
            else:
                logger.warning(f"Authentication failed for: {email}")
                return render(request, 'login.html', {
                    'error': 'Invalid email or password',
                    'form_data': request.POST
                })
                
        except Company.DoesNotExist:
            logger.warning(f"Login attempt for non-existent email: {email}")
            return render(request, 'login.html', {
                'error': 'Invalid email or password',
                'form_data': request.POST
            })
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return render(request, 'login.html', {
                'error': 'Login failed. Please try again.',
                'form_data': request.POST
            })
            
    # GET request - show the form
    return render(request, 'login.html')

def logout_view(request):
    """Handle logout"""
    if request.user.is_authenticated:
        logger.info(f"Logging out user: {request.user.company_name}")
    logout(request)
    logger.info("User logged out successfully")
    return redirect('flowlyne:index')

@login_required
def dashboard(request):
    """Dashboard - requires authentication"""
    logger.info(f"Dashboard accessed by: {request.user.company_name if request.user.is_authenticated else 'Anonymous'}")
    logger.info(f"Session key: {request.session.session_key}")
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
                    'id': company.company_id,
                    'company_name': company.company_name,
                    'email': company.email,
                    'description': company.description or '',
                    'company_address': company.company_address or '',
                    'phone_number': company.phone_number or '',
                    'city': company.city,
                    'country': company.country,
                    'is_verified': company.is_verified,
                    'current_plan': company.current_plan,
                    'created_at': company.created_at.isoformat()
                }
                
                logger.info(f"API Login successful for: {company.company_name}")
                
                return JsonResponse({
                    'message': 'Login successful',
                    'company': company_data,
                    'token': token.key
                })
            else:
                logger.warning(f"Invalid password for: {email}")
                return JsonResponse({'error': 'Invalid email or password'}, status=400)
                
        except Company.DoesNotExist:
            logger.warning(f"API Login attempt for non-existent email: {email}")
            return JsonResponse({'error': 'Invalid email or password'}, status=400)
            
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"API Login error: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

@csrf_exempt 
def api_register(request):
    """Register a new company"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    try:
        # Parse request data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
            
        company_name = data.get('company_name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        description = data.get('description', '').strip()
        
        logger.info(f"API Registration attempt for: {company_name} ({email})")
        
        # Validation
        if not all([company_name, email, password]):
            return JsonResponse({'error': 'Company name, email and password are required'}, status=400)
        
        # Check if email already exists
        if Company.objects.filter(email__iexact=email).exists():
            logger.warning(f"API Registration attempt with existing email: {email}")
            return JsonResponse({'error': 'A company with this email already exists'}, status=400)
        
        # Create the company
        company = Company.objects.create_user(
            email=email,
            password=password,
            company_name=company_name,
            description=description,
            city='Cairo',  # Default for now
            country='Egypt'  # Default for now
        )
        
        # Log them into Django session using username
        user = authenticate(request, username=company.username, password=password)
        if user is not None:
            login(request, user)
            logger.info(f"API Registration session created for: {user.company_name}")
        
        # Create auth token
        token, created = Token.objects.get_or_create(user=company)
        
        # Prepare response data
        company_data = {
            'id': company.company_id,
            'company_name': company.company_name,
            'email': company.email,
            'description': company.description or '',
            'company_address': company.company_address or '',
            'phone_number': company.phone_number or '',
            'city': company.city,
            'country': company.country,
            'is_verified': company.is_verified,
            'current_plan': company.current_plan,
            'created_at': company.created_at.isoformat()
        }
        
        logger.info(f"API Registration successful for: {company.company_name}")
        
        return JsonResponse({
            'message': 'Registration successful',
            'company': company_data,
            'token': token.key
        }, status=201)
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"API Registration error: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

# ================================
# API VIEWS - UPDATED TO REMOVE is_active FILTERS
# ================================

# API view to get all companies (for services page)
def api_companies(request):
    try:
        # Remove is_active filter since the field doesn't exist
        companies = Company.objects.filter(is_active=True)  # Keep this one - it exists in Company
        serializer = CompanyListSerializer(companies, many=True)
        return JsonResponse({'companies': serializer.data})
    except Exception as e:
        logger.error(f"Error fetching companies: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

# API view to get company details
def api_company_detail(request, company_id):
    try:
        company = get_object_or_404(Company, company_id=company_id, is_active=True)
        serializer = CompanyDetailSerializer(company)
        return JsonResponse({'company': serializer.data})
    except Exception as e:
        logger.error(f"Error fetching company details: {str(e)}")
        return JsonResponse({'error': 'Company not found'}, status=404)

# API view to get categories
def api_categories(request):
    try:
        # Remove is_active filter
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
        
        # Get company's services - remove is_active filter
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
        # Remove is_active filter
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
        # Remove is_active filter
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

# API view to get service details
def api_service_detail(request, service_id):
    try:
        # Remove is_active filter
        service = get_object_or_404(Service, service_id=service_id)
        serializer = ServiceSerializer(service)
        return JsonResponse({'service': serializer.data})
    except Exception as e:
        logger.error(f"Error fetching service details: {str(e)}")
        return JsonResponse({'error': 'Service not found'}, status=404)

# API view to get all services (for public listing)
def api_all_services(request):
    try:
        # Remove is_active filter
        services = Service.objects.all().select_related('company')
        serializer = ServiceSerializer(services, many=True)
        return JsonResponse({'services': serializer.data})
    except Exception as e:
        logger.error(f"Error fetching all services: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

# API view to get service categories
def api_service_categories(request):
    try:
        # Remove is_active filter
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return JsonResponse({'categories': serializer.data})
    except Exception as e:
        logger.error(f"Error fetching service categories: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)