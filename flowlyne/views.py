from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
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
from django.shortcuts import get_object_or_404
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
# FRONTEND VIEWS
# ================================

def index(request):
    return render(request, 'index.html')

def services(request):
    return render(request, 'services.html')

def register_view(request):
    return render(request, 'register.html')

def login_view(request):
    return render(request, 'login.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def about(request):
    return render(request, 'about.html')

def plans(request):
    return render(request, 'plans.html')

def payment(request):
    return render(request, 'payment.html')

def offering_view(request):
    """Offering services page - authentication handled by frontend"""
    return render(request, 'offering.html')

# ================================
# API VIEWS - UPDATED FOR NEW SCHEMA
# ================================

@csrf_exempt
def api_login(request):
    """Login company"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    try:
        # Parse request data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
            
        email = data.get('email')
        password = data.get('password')
        
        logger.info(f"Login attempt for email: {email}")
        
        if not email or not password:
            return JsonResponse({'error': 'Email and password are required'}, status=400)
        
        # Find company by email
        try:
            company = Company.objects.get(email__iexact=email, is_active=True)
        except Company.DoesNotExist:
            logger.warning(f"Company not found: {email}")
            return JsonResponse({'error': 'Invalid email or password'}, status=401)
        
        # Check password
        if not company.check_password(password):
            logger.warning(f"Invalid password for: {email}")
            return JsonResponse({'error': 'Invalid email or password'}, status=401)
        
        # Get or create auth token
        token, created = Token.objects.get_or_create(user=company)
        
        # Return success response
        company_data = {
            'id': company.company_id,
            'company_name': company.company_name,
            'email': company.email,
            'description': company.description,
            'company_address': company.company_address,
            'phone_number': company.phone_number,
            'city': company.city,
            'country': company.country,
            'is_verified': company.is_verified,
            'current_plan': company.current_plan,
            'created_at': company.created_at.isoformat()
        }
        
        logger.info(f"Successful login for: {email}")
        
        return JsonResponse({
            'message': 'Login successful',
            'company': company_data,
            'token': token.key
        })
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
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
            
        logger.info(f"Registration data received: {list(data.keys())}")
        
        # Validate required fields
        required_fields = ['company_name', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'error': f'{field} is required'}, status=400)
        
        # Check if email already exists
        if Company.objects.filter(email__iexact=data['email']).exists():
            return JsonResponse({'error': 'Email already registered'}, status=400)
        
        # Get or create default admin (for now, create a default admin)
        admin, created = Admin.objects.get_or_create(
            email='admin@flowlyne.com',
            defaults={'password': 'admin123'}  # In production, this should be hashed
        )
        
        # Create company
        company = Company.objects.create_user(
            email=data['email'],
            company_name=data['company_name'],
            password=data['password'],
            company_address=data.get('company_address', ''),
            phone_number=data.get('phone_number', ''),
            description=data.get('description', ''),
            city=data.get('city', 'Cairo'),
            country=data.get('country', 'Egypt'),
            current_plan='basic',
            admin=admin
        )
        
        # Create auth token
        token, created = Token.objects.get_or_create(user=company)
        
        # Return company data
        company_data = {
            'id': company.company_id,
            'company_name': company.company_name,
            'email': company.email,
            'description': company.description,
            'company_address': company.company_address,
            'phone_number': company.phone_number,
            'city': company.city,
            'country': company.country,
            'is_verified': company.is_verified,
            'current_plan': company.current_plan,
            'created_at': company.created_at.isoformat()
        }
        
        logger.info(f"Company registered: {company.company_name}")
        
        return JsonResponse({
            'message': 'Company registered successfully',
            'company': company_data,
            'token': token.key
        }, status=201)
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def api_companies(request):
    """Get all companies"""
    try:
        companies = Company.objects.filter(is_active=True).select_related('admin')
        
        # Add search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            companies = companies.filter(
                Q(company_name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(city__icontains=search_query)
            ).distinct()
        
        companies_data = []
        for company in companies:
            company_info = {
                'id': company.company_id,
                'company_name': company.company_name,
                'email': company.email,
                'description': company.description,
                'city': company.city,
                'country': company.country,
                'is_verified': company.is_verified,
                'logo': company.logo if company.logo else None,
                'rating': 4.5,  # Mock rating for demo
                'review_count': company.received_reviews.count(),
                'services_count': company.services.count(),
                'created_at': company.created_at.isoformat()
            }
            companies_data.append(company_info)
        
        # Sort by verification status and name
        companies_data.sort(key=lambda x: (not x['is_verified'], x['company_name']))
        
        return JsonResponse(companies_data, safe=False)
        
    except Exception as e:
        logger.error(f"Companies API error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def api_company_detail(request, company_id):
    """Get company details"""
    try:
        company = get_object_or_404(Company, company_id=company_id, is_active=True)
        
        # Get company services
        services = company.services.all()
        services_data = []
        for service in services:
            service_info = {
                'id': service.service_id,
                'service_name': service.service_name,
                'service_description': service.service_description,
                'categories': [
                    {
                        'id': cat.category_id,
                        'name': cat.category_name,
                        'description': cat.category_description
                    }
                    for cat in service.categories.all()
                ]
            }
            services_data.append(service_info)
        
        company_data = {
            'id': company.company_id,
            'company_name': company.company_name,
            'email': company.email,
            'description': company.description,
            'company_address': company.company_address,
            'phone_number': company.phone_number,
            'city': company.city,
            'country': company.country,
            'is_verified': company.is_verified,
            'current_plan': company.current_plan,
            'services': services_data,
            'created_at': company.created_at.isoformat()
        }
        
        return JsonResponse(company_data)
        
    except Exception as e:
        logger.error(f"Company detail error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def api_categories(request):
    """Get all categories"""
    try:
        categories = Category.objects.all()
        categories_data = [
            {
                'id': cat.category_id,
                'name': cat.category_name,
                'description': cat.category_description
            }
            for cat in categories
        ]
        return JsonResponse(categories_data, safe=False)
    except Exception as e:
        logger.error(f"Categories error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt  # FIXED: Add CSRF exemption for API endpoint
def api_send_message(request):
    """Send message to company"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        # Here you would typically save the message to database
        # For now, just return success
        return JsonResponse({'message': 'Message sent successfully'})
    except Exception as e:
        logger.error(f"Send message error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def api_subscription_plans(request):
    """Get subscription plans"""
    try:
        plans = SubscriptionPlan.objects.filter(is_active=True)
        plans_data = [
            {
                'id': plan.plan_id,
                'plan_name': plan.plan_name,
                'price': float(plan.price),
                'duration_months': plan.duration_months,
                'features': plan.features,
                'is_popular': plan.is_popular
            }
            for plan in plans
        ]
        return JsonResponse(plans_data, safe=False)
    except Exception as e:
        logger.error(f"Subscription plans error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt  # FIXED: Add CSRF exemption
def api_upgrade_subscription(request):
    """Upgrade subscription"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        # Here you would handle subscription upgrade logic
        return JsonResponse({'message': 'Subscription upgraded successfully'})
    except Exception as e:
        logger.error(f"Upgrade subscription error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

# FIXED: Proper authentication for service endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_company_services(request):
    """Get all services for the current user's company"""
    try:
        company = request.user
        services = Service.objects.filter(company=company)
        
        services_data = []
        for service in services:
            service_info = {
                'id': service.service_id,
                'service_name': service.service_name,
                'service_description': service.service_description,
                'price': float(service.price) if hasattr(service, 'price') else 0.0,  # FIXED: Add price field
                'category': getattr(service, 'category', 'Other'),  # FIXED: Add category field
                'duration': getattr(service, 'duration', None),  # FIXED: Add duration field
                'categories': [
                    {
                        'id': cat.category_id,
                        'name': cat.category_name,
                        'description': cat.category_description
                    }
                    for cat in service.categories.all()
                ]
            }
            services_data.append(service_info)
        
        return Response({
            'services': services_data,
            'count': services.count()
        })
        
    except Exception as e:
        logger.error(f"Company services error: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_create_service(request):
    """Create a new service for the current user's company"""
    try:
        company = request.user
        data = request.data
        
        logger.info(f"Creating service for company: {company.company_name}")
        logger.info(f"Service data: {data}")
        
        # FIXED: Map frontend fields to backend fields
        service = Service.objects.create(
            company=company,
            service_name=data.get('service_name', data.get('title', '')),
            service_description=data.get('service_description', data.get('description', ''))
        )
        
        # FIXED: Add additional fields if they exist in your model
        if hasattr(service, 'price'):
            service.price = data.get('price', 0.0)
        if hasattr(service, 'category'):
            service.category = data.get('category', 'Other')
        if hasattr(service, 'duration'):
            service.duration = data.get('duration', None)
        
        service.save()
        
        # Create categories if provided
        categories_data = data.get('categories', [])
        if isinstance(categories_data, list):
            for cat_data in categories_data:
                if isinstance(cat_data, dict):
                    category, created = Category.objects.get_or_create(
                        category_name=cat_data.get('name', ''),
                        defaults={
                            'category_description': cat_data.get('description', ''),
                            'service': service
                        }
                    )
                    service.categories.add(category)
        
        # Return created service data
        service_data = {
            'id': service.service_id,
            'service_name': service.service_name,
            'service_description': service.service_description,
            'price': getattr(service, 'price', 0.0),
            'category': getattr(service, 'category', 'Other'),
            'duration': getattr(service, 'duration', None),
            'categories': [
                {
                    'id': cat.category_id,
                    'name': cat.category_name,
                    'description': cat.category_description
                }
                for cat in service.categories.all()
            ]
        }
        
        logger.info(f"Service created successfully: {service.service_name}")
        
        return Response(service_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Create service error: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def api_service_detail(request, service_id):
    """Get, update, or delete a specific service"""
    try:
        # FIXED: Ensure user can only access their own services
        service = get_object_or_404(
            Service, 
            service_id=service_id, 
            company=request.user
        )
        
        if request.method == 'GET':
            service_data = {
                'id': service.service_id,
                'service_name': service.service_name,
                'service_description': service.service_description,
                'price': getattr(service, 'price', 0.0),
                'category': getattr(service, 'category', 'Other'),
                'duration': getattr(service, 'duration', None),
                'categories': [
                    {
                        'id': cat.category_id,
                        'name': cat.category_name,
                        'description': cat.category_description
                    }
                    for cat in service.categories.all()
                ]
            }
            return Response(service_data)
            
        elif request.method == 'PUT':
            data = request.data
            
            # Update service fields
            service.service_name = data.get('service_name', data.get('title', service.service_name))
            service.service_description = data.get('service_description', data.get('description', service.service_description))
            
            # Update additional fields if they exist
            if hasattr(service, 'price'):
                service.price = data.get('price', getattr(service, 'price', 0.0))
            if hasattr(service, 'category'):
                service.category = data.get('category', getattr(service, 'category', 'Other'))
            if hasattr(service, 'duration'):
                service.duration = data.get('duration', getattr(service, 'duration', None))
            
            service.save()
            
            # Return updated service data
            service_data = {
                'id': service.service_id,
                'service_name': service.service_name,
                'service_description': service.service_description,
                'price': getattr(service, 'price', 0.0),
                'category': getattr(service, 'category', 'Other'),
                'duration': getattr(service, 'duration', None),
            }
            
            return Response(service_data)
            
        elif request.method == 'DELETE':
            service.delete()
            return Response({'message': 'Service deleted successfully'})
        
    except Exception as e:
        logger.error(f"Service detail error: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def api_all_services(request):
    """Get all services (public endpoint)"""
    try:
        services = Service.objects.select_related('company').all()
        
        # Add search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            services = services.filter(
                Q(service_name__icontains=search_query) |
                Q(service_description__icontains=search_query)
            ).distinct()
        
        services_data = []
        for service in services:
            service_info = {
                'id': service.service_id,
                'service_name': service.service_name,
                'service_description': service.service_description,
                'price': getattr(service, 'price', 0.0),
                'category': getattr(service, 'category', 'Other'),
                'duration': getattr(service, 'duration', None),
                'company': {
                    'id': service.company.company_id,
                    'name': service.company.company_name,
                    'city': service.company.city,
                    'is_verified': service.company.is_verified
                },
                'categories': [
                    {
                        'id': cat.category_id,
                        'name': cat.category_name,
                        'description': cat.category_description
                    }
                    for cat in service.categories.all()
                ]
            }
            services_data.append(service_info)
        
        return Response({
            'services': services_data,
            'count': services.count()
        })
        
    except Exception as e:
        logger.error(f"All services error: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def api_service_categories(request):
    """Get all service categories"""
    try:
        categories = Category.objects.all()
        
        categories_data = [
            {
                'id': category.category_id,
                'name': category.category_name,
                'description': category.category_description,
                'service_id': category.service.service_id if category.service else None,
                'service_name': category.service.service_name if category.service else None,
            }
            for category in categories
        ]
        
        return Response({
            'categories': categories_data,
            'count': categories.count()
        })
        
    except Exception as e:
        logger.error(f"Service categories error: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def api_stats(request):
    """Get platform statistics"""
    try:
        stats = {
            'total_companies': Company.objects.filter(is_active=True).count(),
            'verified_companies': Company.objects.filter(is_active=True, is_verified=True).count(),
            'total_services': Service.objects.count(),
            'total_categories': Category.objects.count(),
            'total_reviews': Review.objects.count(),
        }
        return JsonResponse(stats)
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)