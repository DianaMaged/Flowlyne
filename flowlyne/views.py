from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
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
    CompanyProfileUpdateSerializer, ReviewSerializer, SubscriptionPlanSerializer, 
    PaymentSerializer, CompanySubscriptionSerializer, AdvertisingSerializer, 
    StatsSerializer, CategorySerializer
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

def plans(request):
    """Plans page"""
    logger.info(f"Plans page accessed. User authenticated: {request.user.is_authenticated}")
    return render(request, 'plans.html')

def payment(request):
    """Payment page"""
    logger.info(f"Payment page accessed. User authenticated: {request.user.is_authenticated}")
    return render(request, 'payment.html')

def offering_view(request):
    """Offering management page - authentication handled on frontend"""
    logger.info(f"Offering page accessed. User authenticated: {request.user.is_authenticated}")
    return render(request, 'offering.html')

def register_view(request):
    """Handle company registration"""
    if request.method == 'POST':
        try:
            # Get form data
            data = {
                'company_name': request.POST.get('company_name'),
                'email': request.POST.get('email'),
                'password': request.POST.get('password'),
                'description': request.POST.get('description'),
                'company_address': request.POST.get('company_address'),
                'phone_number': request.POST.get('phone_number'),
                'city': request.POST.get('city', 'Cairo'),
                'country': request.POST.get('country', 'Egypt')
            }
            
            # Validate required fields
            if not all([data['company_name'], data['email'], data['password']]):
                return render(request, 'register.html', {
                    'error': 'Please fill in all required fields.',
                    'form_data': request.POST
                })
            
            # Use serializer for validation and creation
            serializer = CompanyRegistrationSerializer(data=data)
            if serializer.is_valid():
                company = serializer.save()
                logger.info(f"Company registered successfully: {company.company_name}")
                
                # Login the user immediately after registration
                user = authenticate(username=company.username, password=data['password'])
                if user:
                    login(request, user)
                    logger.info(f"User logged in after registration: {user.company_name}")
                    return redirect('flowlyne:dashboard')
                
                return redirect('flowlyne:login')
            else:
                errors = serializer.errors
                error_message = next(iter(errors.values()))[0] if errors else 'Registration failed.'
                return render(request, 'register.html', {
                    'error': error_message,
                    'form_data': request.POST
                })
                
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return render(request, 'register.html', {
                'error': 'An error occurred during registration. Please try again.',
                'form_data': request.POST
            })
    
    # GET request - show the form
    return render(request, 'register.html')

def login_view(request):
    """Handle company login"""
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
            
            logger.info(f"Login attempt for email: {email}")
            
            if not email or not password:
                return render(request, 'login.html', {
                    'error': 'Please provide both email and password.',
                    'form_data': request.POST
                })
            
            # Use serializer for validation
            serializer = CompanyLoginSerializer(data={'email': email, 'password': password})
            if serializer.is_valid():
                user = serializer.validated_data['user']
                login(request, user)
                logger.info(f"User logged in successfully: {user.company_name}")
                return redirect('flowlyne:dashboard')
            else:
                errors = serializer.errors
                error_message = next(iter(errors.values()))[0] if errors else 'Invalid credentials.'
                return render(request, 'login.html', {
                    'error': error_message,
                    'form_data': request.POST
                })
                
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return render(request, 'login.html', {
                'error': 'An error occurred during login. Please try again.',
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

def dashboard(request):
    """Dashboard - authentication handled on frontend"""
    logger.info(f"Dashboard accessed. User authenticated: {request.user.is_authenticated}")
    return render(request, 'dashboard.html')

def about(request):
    """About page"""
    logger.info(f"About page accessed. User authenticated: {request.user.is_authenticated}")
    return render(request, 'about.html')

def plans(request):
    """Plans page"""
    logger.info(f"Plans page accessed. User authenticated: {request.user.is_authenticated}")
    return render(request, 'plans.html')

# ================================
# API ENDPOINTS - FOR FRONTEND AJAX CALLS
# ================================

@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    """API endpoint for company registration"""
    try:
        serializer = CompanyRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            company = serializer.save()
            return Response({
                'success': True,
                'message': 'Company registered successfully',
                'company': {
                    'company_id': company.company_id,
                    'company_name': company.company_name,
                    'email': company.email
                }
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"API Registration error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """API endpoint for company login"""
    try:
        serializer = CompanyLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'success': True,
                'token': token.key,
                'company': {
                    'company_id': user.company_id,
                    'company_name': user.company_name,
                    'email': user.email,
                    'city': user.city,
                    'country': user.country,
                    'description': user.description,
                    'phone_number': user.phone_number,
                    'website': '',  # Add if you have this field
                    'is_verified': user.is_verified,
                    'current_plan': user.current_plan,
                    'created_at': user.created_at.isoformat()
                }
            })
        else:
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"API Login error: {str(e)}")
        return Response({
            'success': False,
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_company_profile(request):
    """API endpoint to get current company profile"""
    try:
        company = request.user
        serializer = CompanyDetailSerializer(company)
        return Response({
            'success': True,
            'company': serializer.data
        })
    except Exception as e:
        logger.error(f"Error fetching company profile: {str(e)}")
        return Response({
            'success': False,
            'message': 'Error fetching profile'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def api_update_company_profile(request):
    """API endpoint to update company profile"""
    try:
        company = request.user
        serializer = CompanyProfileUpdateSerializer(company, data=request.data, partial=True)
        
        if serializer.is_valid():
            updated_company = serializer.save()
            logger.info(f"Company profile updated: {updated_company.company_name}")
            
            # Return updated profile data
            return Response({
                'success': True,
                'message': 'Profile updated successfully',
                'company': {
                    'company_id': updated_company.company_id,
                    'company_name': updated_company.company_name,
                    'email': updated_company.email,
                    'description': updated_company.description,
                    'company_address': updated_company.company_address,
                    'phone_number': updated_company.phone_number,
                    'city': updated_company.city,
                    'country': updated_company.country,
                    'is_verified': updated_company.is_verified,
                    'current_plan': updated_company.current_plan,
                    'created_at': updated_company.created_at.isoformat(),
                    'updated_at': updated_company.updated_at.isoformat()
                }
            })
        else:
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error updating company profile: {str(e)}")
        return Response({
            'success': False,
            'message': 'Error updating profile'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ===== EXISTING API ENDPOINTS =====

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

# Global stats for platform
def api_platform_stats(request):
    try:
        stats = {
            'total_companies': Company.objects.filter(is_active=True).count(),
            'verified_companies': Company.objects.filter(is_verified=True, is_active=True).count(),
            'total_departments': Category.objects.count(),  # Keep as total_departments for frontend compatibility
            'total_services': Service.objects.count()
        }
        return JsonResponse(stats)
    except Exception as e:
        logger.error(f"Error fetching platform stats: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

# Message sending (placeholder)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_send_message(request):
    # This is a placeholder for future messaging functionality
    return Response({
        'message': 'Message functionality will be implemented in future updates',
        'success': True
    })

# Subscription management endpoints
@api_view(['GET'])
@permission_classes([AllowAny])
def api_subscription_plans(request):
    try:
        # Remove is_active filter
        plans = SubscriptionPlan.objects.all()
        serializer = SubscriptionPlanSerializer(plans, many=True)
        return Response({'plans': serializer.data})
    except Exception as e:
        logger.error(f"Error fetching subscription plans: {str(e)}")
        return Response({'error': 'Internal server error'}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_upgrade_subscription(request):
    # This is a placeholder for future subscription upgrade functionality
    return Response({
        'message': 'Subscription upgrade functionality will be implemented in future updates',
        'success': True
    })

# Company services management
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_create_service(request):
    try:
        # Add company to the data
        data = request.data.copy()
        data['company'] = request.user.company_id
        
        serializer = ServiceCreateSerializer(data=data)
        if serializer.is_valid():
            service = serializer.save()
            response_serializer = ServiceSerializer(service)
            return Response({
                'success': True,
                'service': response_serializer.data,
                'message': 'Service created successfully'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error creating service: {str(e)}")
        return Response({
            'success': False,
            'message': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def api_service_detail(request, service_id):
    try:
        service = get_object_or_404(Service, service_id=service_id, company=request.user)
        
        if request.method == 'GET':
            serializer = ServiceSerializer(service)
            return Response(serializer.data)
        
        elif request.method == 'PUT':
            serializer = ServiceCreateSerializer(service, data=request.data, partial=True)
            if serializer.is_valid():
                service = serializer.save()
                response_serializer = ServiceSerializer(service)
                return Response({
                    'success': True,
                    'service': response_serializer.data,
                    'message': 'Service updated successfully'
                })
            else:
                return Response({
                    'success': False,
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            service.delete()
            return Response({
                'success': True,
                'message': 'Service deleted successfully'
            })
            
    except Exception as e:
        logger.error(f"Error in service detail: {str(e)}")
        return Response({
            'success': False,
            'message': 'Service not found or access denied'
        }, status=status.HTTP_404_NOT_FOUND)

# All services endpoint (for services page)
@api_view(['GET'])
@permission_classes([AllowAny])
def api_all_services(request):
    try:
        # Get search parameters
        search = request.GET.get('search', '')
        category = request.GET.get('category', '')
        city = request.GET.get('city', '')
        
        # Base queryset - remove is_active filter from Service
        services = Service.objects.select_related('company')
        
        # Apply filters
        if search:
            services = services.filter(
                Q(service_name__icontains=search) |
                Q(service_description__icontains=search) |
                Q(company__company_name__icontains=search)
            )
        
        if category:
            services = services.filter(category__icontains=category)
        
        if city:
            services = services.filter(company__city__icontains=city)
        
        # Only show services from active companies
        services = services.filter(company__is_active=True)
        
        serializer = ServiceSerializer(services, many=True)
        return Response({'services': serializer.data})
    except Exception as e:
        logger.error(f"Error fetching all services: {str(e)}")
        return Response({'error': 'Internal server error'}, status=500)

# Service categories endpoint
@api_view(['GET'])
@permission_classes([AllowAny])
def api_service_categories(request):
    try:
        # Get unique categories from services
        categories = Service.objects.values_list('category', flat=True).distinct()
        categories = [cat for cat in categories if cat]  # Remove empty categories
        return Response({'categories': categories})
    except Exception as e:
        logger.error(f"Error fetching service categories: {str(e)}")
        return Response({'error': 'Internal server error'}, status=500)