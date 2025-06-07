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
# FRONTEND VIEWS - MINIMAL CHANGES FOR AUTHENTICATION
# ================================

def index(request):
    return render(request, 'index.html')

def services(request):
    return render(request, 'services.html')

def register_view(request):
    # Handle both GET (show form) and POST (process registration)
    if request.method == 'POST':
        # Get form data
        company_name = request.POST.get('company_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        description = request.POST.get('description', '').strip()
        
        # Validation
        if not all([company_name, email, password]):
            # Return to form with error - your existing template will handle this
            return render(request, 'register.html', {
                'error': 'Company name, email and password are required',
                'form_data': request.POST
            })
        
        # Check if email exists
        if Company.objects.filter(email__iexact=email).exists():
            return render(request, 'register.html', {
                'error': 'A company with this email already exists',
                'form_data': request.POST
            })
        
        try:
            # Create company
            company = Company.objects.create_user(
                email=email,
                password=password,
                company_name=company_name,
                description=description,
                city='Cairo',
                country='Egypt'
            )
            
            # Log them in automatically
            login(request, company)
            
            # Redirect to dashboard (this will now work!)
            return redirect('flowlyne:dashboard')
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return render(request, 'register.html', {
                'error': 'Registration failed. Please try again.',
                'form_data': request.POST
            })
    
    # GET request - show the form
    return render(request, 'register.html')

def login_view(request):
    # Handle both GET (show form) and POST (process login)
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        if not email or not password:
            return render(request, 'login.html', {
                'error': 'Email and password are required',
                'form_data': request.POST
            })
        
        try:
            # Find company
            company = Company.objects.get(email__iexact=email)
            
            # Check if active
            if not company.is_active:
                return render(request, 'login.html', {
                    'error': 'Your account has been disabled',
                    'form_data': request.POST
                })
            
            # Authenticate
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                # Redirect to dashboard (this will now work!)
                return redirect('flowlyne:dashboard')
            else:
                return render(request, 'login.html', {
                    'error': 'Invalid email or password',
                    'form_data': request.POST
                })
                
        except Company.DoesNotExist:
            return render(request, 'login.html', {
                'error': 'Invalid email or password',
                'form_data': request.POST
            })
            
    # GET request - show the form
    return render(request, 'login.html')

def logout_view(request):
    """Simple logout that redirects to home"""
    logout(request)
    return redirect('flowlyne:index')

@login_required
def dashboard(request):
    """Dashboard - now requires authentication"""
    return render(request, 'dashboard.html')

def about(request):
    return render(request, 'about.html')

def plans(request):
    return render(request, 'plans.html')

@login_required  # Add protection
def payment(request):
    return render(request, 'payment.html')

@login_required  # Add protection
def offering_view(request):
    """Offering services page - now requires authentication"""
    return render(request, 'offering.html')

# ================================
# API VIEWS - KEEP ALL YOUR EXISTING ONES + KEY FIX
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
                # KEY FIX: ALSO log them into Django session
                login(request, company)
                
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
            
        company_name = data.get('company_name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        description = data.get('description', '').strip()
        
        logger.info(f"Registration attempt for: {company_name}")
        
        # Validation
        if not all([company_name, email, password]):
            return JsonResponse({'error': 'Company name, email and password are required'}, status=400)
        
        # Check if email already exists
        if Company.objects.filter(email__iexact=email).exists():
            logger.warning(f"Registration attempt with existing email: {email}")
            return JsonResponse({'error': 'A company with this email already exists'}, status=400)
        
        # Create new company
        company = Company.objects.create_user(
            email=email,
            password=password,
            company_name=company_name,
            description=description,
            city='Cairo',  # Default city
            country='Egypt'  # Default country
        )
        
        # KEY FIX: ALSO log them into Django session
        login(request, company)
        
        # Create auth token
        token = Token.objects.create(user=company)
        
        # Prepare response data
        company_data = {
            'id': company.company_id,
            'company_name': company.company_name,
            'email': company.email,
            'description': company.description or '',
            'city': company.city,
            'country': company.country,
            'is_verified': company.is_verified,
            'current_plan': company.current_plan,
            'created_at': company.created_at.isoformat()
        }
        
        logger.info(f"Registration successful for: {company.company_name}")
        
        return JsonResponse({
            'message': 'Registration successful',
            'company': company_data,
            'token': token.key
        }, status=201)
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

# ================================
# ALL YOUR EXISTING API FUNCTIONS - KEEP EXACTLY THE SAME
# ================================

@api_view(['GET'])
@permission_classes([AllowAny])
def api_companies(request):
    """Get list of all companies with their services"""
    try:
        companies = Company.objects.filter(is_active=True).prefetch_related('service_set')
        serializer = CompanyListSerializer(companies, many=True)
        return Response({'companies': serializer.data})
    except Exception as e:
        logger.error(f"Error fetching companies: {str(e)}")
        return Response({'error': 'Internal server error'}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def api_company_detail(request, company_id):
    """Get detailed information about a specific company"""
    try:
        company = get_object_or_404(Company, company_id=company_id, is_active=True)
        
        # Get services for this company
        services = Service.objects.filter(company=company)
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

@csrf_exempt
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

@csrf_exempt
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
        company = request.user
        
        service_name = request.data.get('service_name', '').strip()
        service_description = request.data.get('service_description', '').strip()
        
        if not service_name or not service_description:
            return Response(
                {'error': 'Service name and description are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the service
        service = Service.objects.create(
            company=company,
            service_name=service_name,
            service_description=service_description
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
        service = get_object_or_404(Service, service_id=service_id, company=request.user)
        
        if request.method == 'GET':
            service_data = {
                'id': service.service_id,
                'service_name': service.service_name,
                'service_description': service.service_description,
                'company_name': service.company.company_name
            }
            return Response({'service': service_data})
        
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