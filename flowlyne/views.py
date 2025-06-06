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
from .serializers import ServiceSerializer, ServiceCreateSerializer
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

@login_required
def offering_view(request):
    """Offering services page - requires authentication"""
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
            
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        logger.info(f"Login attempt for email: {email}")
        
        if not email or not password:
            return JsonResponse({'error': 'Email and password are required'}, status=400)
        
        try:
            # Find company by email (case-insensitive)
            company = Company.objects.get(email__iexact=email)
            logger.info(f"Found company: {company.company_name}")
            
            # Check if account is active
            if not company.is_active:
                logger.warning(f"Inactive account login attempt: {email}")
                return JsonResponse({'error': 'Account is disabled'}, status=400)
            
            # Check password using Django's built-in method
            if company.check_password(password):
                # Get or create auth token
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
                
                logger.info(f"Login successful for: {company.company_name}")
                
                return JsonResponse({
                    'message': 'Login successful',
                    'company': company_data,
                    'token': token.key
                })
            else:
                logger.warning(f"Invalid password for: {email}")
                return JsonResponse({'error': 'Invalid email or password'}, status=400)
                
        except Company.DoesNotExist:
            logger.warning(f"Login attempt for non-existent email: {email}")
            return JsonResponse({'error': 'Invalid email or password'}, status=400)
            
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
    """Get detailed company information"""
    try:
        company = get_object_or_404(Company, company_id=company_id)
        
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
            'logo': company.logo if company.logo else None,
            'certification': company.certification if company.certification else None,
            'rating': 4.5,  # Mock rating
            'review_count': company.received_reviews.count(),
            'services': [
                {
                    'id': service.service_id,
                    'name': service.service_name,
                    'description': service.service_description
                }
                for service in company.services.all()
            ],
            'created_at': company.created_at.isoformat()
        }
        
        return JsonResponse(company_data)
        
    except Exception as e:
        logger.error(f"Company detail error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def api_categories(request):
    """Get all available categories"""
    try:
        categories = Category.objects.all().select_related('service')
        categories_data = [
            {
                'id': cat.category_id,
                'name': cat.category_name,
                'description': cat.category_description,
                'service_name': cat.service.service_name if cat.service else None
            }
            for cat in categories
        ]
        return JsonResponse(categories_data, safe=False)
    except Exception as e:
        logger.error(f"Categories error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_company_services(request):
    """Get all services for the current user's company"""
    try:
        company = request.user
        services = Service.objects.filter(company=company)
        
        services_data = [
            {
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
            for service in services
        ]
        
        return Response({
            'services': services_data,
            'count': services.count()
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_create_service(request):
    """Create a new service for the current user's company"""
    try:
        service_name = request.data.get('service_name')
        service_description = request.data.get('service_description')
        
        if not service_name or not service_description:
            return Response({
                'error': 'Service name and description are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create default admin
        admin, created = Admin.objects.get_or_create(
            email='admin@flowlyne.com',
            defaults={'password': 'admin123'}
        )
        
        # Create service
        service = Service.objects.create(
            service_name=service_name,
            service_description=service_description,
            company=request.user,
            admin=admin
        )
        
        service_data = {
            'id': service.service_id,
            'service_name': service.service_name,
            'service_description': service.service_description,
            'company_name': service.company.company_name
        }
        
        return Response({
            'message': 'Service created successfully',
            'service': service_data
        }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def api_service_detail(request, service_id):
    """Get, update, or delete a specific service"""
    try:
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
                'company_name': service.company.company_name
            }
            return Response(service_data)
            
        elif request.method == 'PUT':
            service_name = request.data.get('service_name', service.service_name)
            service_description = request.data.get('service_description', service.service_description)
            
            service.service_name = service_name
            service.service_description = service_description
            service.save()
            
            service_data = {
                'id': service.service_id,
                'service_name': service.service_name,
                'service_description': service.service_description,
                'company_name': service.company.company_name
            }
            
            return Response({
                'message': 'Service updated successfully',
                'service': service_data
            })
                
        elif request.method == 'DELETE':
            service_name = service.service_name
            service.delete()
            return Response({
                'message': f'Service "{service_name}" deleted successfully'
            })
            
    except Service.DoesNotExist:
        return Response(
            {'error': 'Service not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def api_all_services(request):
    """Get all active services from all companies"""
    try:
        services = Service.objects.all().select_related('company')
        
        # Add search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            services = services.filter(
                Q(service_name__icontains=search_query) |
                Q(service_description__icontains=search_query) |
                Q(company__company_name__icontains=search_query)
            )
        
        services_data = [
            {
                'id': service.service_id,
                'service_name': service.service_name,
                'service_description': service.service_description,
                'company_name': service.company.company_name,
                'company_id': service.company.company_id,
                'company_verified': service.company.is_verified
            }
            for service in services
        ]
        
        return Response({
            'services': services_data,
            'count': services.count()
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def api_subscription_plans(request):
    """Get all available subscription plans"""
    try:
        plans = [
            {
                'id': 1,
                'name': 'basic',
                'display_name': 'Basic Plan (Free)',
                'price_egp': 0,
                'features': [
                    '🏢 Standard listing in search results',
                    '📝 Basic company profile',
                    '📧 Email support',
                    '📤 Basic service listings',
                    '💸 10% commission on projects'
                ]
            },
            {
                'id': 2,
                'name': 'standard',
                'display_name': 'Standard Plan',
                'price_egp': 200,
                'features': [
                    '⬆️ Higher ranking in search results',
                    '📁 Enhanced company profile',
                    '📤 Advanced service listings',
                    '💬 Priority customer support',
                    '💰 8% commission (2% discount)',
                    '📊 Basic analytics',
                    '🎧 Priority support'
                ]
            },
            {
                'id': 3,
                'name': 'premium',
                'display_name': 'Premium Plan',
                'price_egp': 500,
                'features': [
                    '🔝 Top placement + Featured listings',
                    '🌟 Premium company profile',
                    '📤 Unlimited service listings',
                    '⭐ Featured in search results',
                    '💎 5% commission (5% discount)',
                    '📈 Advanced analytics and insights',
                    '👨‍💼 Dedicated account manager'
                ]
            }
        ]
        return JsonResponse(plans, safe=False)
    except Exception as e:
        logger.error(f"Subscription plans error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def api_upgrade_subscription(request):
    """Upgrade user's subscription plan"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
            
        plan_type = data.get('plan_type')
        if not plan_type:
            return JsonResponse({'error': 'Plan type required'}, status=400)
        
        valid_plans = ['basic', 'standard', 'premium']
        if plan_type not in valid_plans:
            return JsonResponse({'error': f'Invalid plan type. Must be one of: {valid_plans}'}, status=400)
        
        return JsonResponse({
            'message': f'Successfully upgraded to {plan_type} plan',
            'new_plan': plan_type,
            'status': 'active'
        })
        
    except Exception as e:
        logger.error(f"Upgrade subscription error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def api_send_message(request):
    """Send message to another company"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
            
        receiver_id = data.get('receiver_id')
        subject = data.get('subject')
        message = data.get('message')
        
        if not receiver_id or not message:
            return JsonResponse({'error': 'Receiver ID and message are required'}, status=400)
        
        receiver = get_object_or_404(Company, company_id=receiver_id)
        
        return JsonResponse({
            'message': 'Message sent successfully',
            'id': 'demo-message-id',
            'receiver': receiver.company_name
        }, status=201)
        
    except Exception as e:
        logger.error(f"Send message error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)