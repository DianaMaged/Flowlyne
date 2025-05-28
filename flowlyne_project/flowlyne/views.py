# flowlyne/views.py - COMPLETE FIXED VERSION

from django.shortcuts import render, get_object_or_404
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
import json
import logging

from .models import Company, Department, CompanyDepartment

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

# ================================
# API VIEWS - FIXED VERSIONS
# ================================

@csrf_exempt
def api_login(request):
    """FIXED Login company"""
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
                    'id': str(company.id),
                    'company_name': company.company_name,
                    'email': company.email,
                    'description': company.description or '',
                    'company_address': company.company_address or '',
                    'phone_number': company.phone_number or '',
                    'city': company.city,
                    'country': company.country,
                    'website': company.website or '',
                    'is_verified': company.is_verified,
                    'current_plan': getattr(company, 'current_plan', 'basic'),
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
    """FIXED Register a new company"""
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
        
        # Create company
        company = Company.objects.create_user(
            email=data['email'],
            company_name=data['company_name'],
            password=data['password'],
            company_address=data.get('company_address', ''),
            phone_number=data.get('phone_number', ''),
            description=data.get('description', ''),
            website=data.get('website', ''),
            city=data.get('city', 'Cairo'),
            country=data.get('country', 'Egypt'),
            current_plan='basic'
        )
        
        # Handle departments
        departments = data.get('departments', [])
        if isinstance(departments, str):
            departments = [departments]  # Handle single department as string
            
        if departments:
            for dept_name in departments:
                try:
                    department, created = Department.objects.get_or_create(
                        name=dept_name,
                        defaults={'icon': '🏢', 'description': f'{dept_name} services'}
                    )
                    CompanyDepartment.objects.create(
                        company=company,
                        department=department,
                        is_primary=len(departments) == 1
                    )
                except Exception as e:
                    logger.warning(f"Could not add department {dept_name}: {e}")
        
        # Create auth token
        token, created = Token.objects.get_or_create(user=company)
        
        # Return company data
        company_data = {
            'id': str(company.id),
            'company_name': company.company_name,
            'email': company.email,
            'description': company.description,
            'company_address': company.company_address,
            'phone_number': company.phone_number,
            'city': company.city,
            'country': company.country,
            'website': company.website,
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
    """Get all companies - FIXED VERSION"""
    try:
        companies = Company.objects.filter(is_active=True).prefetch_related('departments__department')
        
        # Add search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            companies = companies.filter(
                Q(company_name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(departments__department__name__icontains=search_query) |
                Q(city__icontains=search_query)
            ).distinct()
        
        # Add department filter
        department = request.GET.get('department', '')
        if department:
            companies = companies.filter(departments__department__name=department)
        
        companies_data = []
        for company in companies:
            # Get primary department
            primary_dept = company.departments.filter(is_primary=True).first()
            if not primary_dept:
                primary_dept = company.departments.first()
            
            company_info = {
                'id': str(company.id),
                'company_name': company.company_name,
                'email': company.email,
                'description': company.description,
                'city': company.city,
                'country': company.country,
                'website': company.website,
                'is_verified': company.is_verified,
                'logo': company.logo.url if company.logo else None,
                'rating': 4.5,  # Mock rating for demo
                'review_count': 12,  # Mock review count
                'primary_department': primary_dept.department.name if primary_dept else None,
                'departments': [
                    {
                        'name': cd.department.name,
                        'icon': cd.department.icon,
                        'is_primary': cd.is_primary,
                    }
                    for cd in company.departments.all()
                ],
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
        company = get_object_or_404(Company, id=company_id)
        
        company_data = {
            'id': str(company.id),
            'company_name': company.company_name,
            'email': company.email,
            'description': company.description,
            'company_address': company.company_address,
            'phone_number': company.phone_number,
            'website': company.website,
            'city': company.city,
            'country': company.country,
            'is_verified': company.is_verified,
            'logo': company.logo.url if company.logo else None,
            'portfolio': company.portfolio.url if company.portfolio else None,
            'certifications': company.certifications.url if company.certifications else None,
            'rating': 4.5,  # Mock rating
            'review_count': 12,  # Mock review count
            'departments': [
                {
                    'name': cd.department.name,
                    'icon': cd.department.icon,
                    'is_primary': cd.is_primary,
                }
                for cd in company.departments.all()
            ],
            'created_at': company.created_at.isoformat()
        }
        
        return JsonResponse(company_data)
        
    except Exception as e:
        logger.error(f"Company detail error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def api_departments(request):
    """Get all available departments"""
    try:
        departments = Department.objects.filter(is_active=True).order_by('name')
        departments_data = [
            {
                'id': dept.id,
                'name': dept.name,
                'description': dept.description,
                'icon': dept.icon
            }
            for dept in departments
        ]
        return JsonResponse(departments_data, safe=False)
    except Exception as e:
        logger.error(f"Departments error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def api_stats(request):
    """Get platform statistics"""
    try:
        stats = {
            'total_companies': Company.objects.filter(is_active=True).count(),
            'verified_companies': Company.objects.filter(is_active=True, is_verified=True).count(),
            'total_departments': Department.objects.filter(is_active=True).count(),
            'total_messages': 0,  # Placeholder
        }
        return JsonResponse(stats)
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def api_send_message(request):
    """Send message to another company"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    try:
        # Parse request data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
            
        receiver_id = data.get('receiver_id')
        subject = data.get('subject')
        message = data.get('message')
        
        if not receiver_id or not message:
            return JsonResponse({'error': 'Receiver ID and message are required'}, status=400)
        
        receiver = get_object_or_404(Company, id=receiver_id)
        
        # In a real app, you'd create a Message model and save this
        # For now, just return success
        return JsonResponse({
            'message': 'Message sent successfully',
            'id': 'demo-message-id',
            'receiver': receiver.company_name
        }, status=201)
        
    except Exception as e:
        logger.error(f"Send message error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def api_subscription_plans(request):
    """Get all available subscription plans"""
    try:
        plans = [
            {
                'id': 1,
                'name': 'basic',
                'display_name': 'Basic Plan (Free)',
                'price_egp': 0,
                'price_period': 'month',
                'features': [
                    '🏢 Standard listing in search results',
                    '📝 Basic company profile',
                    '📧 Email support',
                    '📤 5 project uploads during signup',
                    '💸 10% commission on projects'
                ]
            },
            {
                'id': 2,
                'name': 'standard',
                'display_name': 'Standard Plan',
                'price_egp': 200,
                'price_period': 'month',
                'features': [
                    '⬆️ Higher ranking in search results',
                    '📁 Full portfolio display',
                    '📤 Upload 5 new projects/month',
                    '💬 View & respond to comments',
                    '💰 8% commission (2% discount)',
                    '📊 Engagement analytics',
                    '🎧 Priority support'
                ]
            },
            {
                'id': 3,
                'name': 'premium',
                'display_name': 'Premium Plan',
                'price_egp': 500,
                'price_period': 'month',
                'features': [
                    '🔝 Top placement + Featured on homepage',
                    '🌟 Advanced portfolio with priority exposure',
                    '📤 Upload 10 new projects/month',
                    '⭐ Highlight top reviews + Reply to comments',
                    '💎 5% commission (5% discount)',
                    '📈 Full analytics with client trends',
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
        # Parse request data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
            
        plan_type = data.get('plan_type')
        if not plan_type:
            return JsonResponse({'error': 'Plan type required'}, status=400)
        
        # Validate plan type
        valid_plans = ['basic', 'standard', 'premium']
        if plan_type not in valid_plans:
            return JsonResponse({'error': f'Invalid plan type. Must be one of: {valid_plans}'}, status=400)
        
        # For demo purposes, we'll just return success
        # In a real app, you would:
        # 1. Authenticate the user
        # 2. Update their subscription
        # 3. Process payment
        
        return JsonResponse({
            'message': f'Successfully upgraded to {plan_type} plan',
            'new_plan': plan_type,
            'status': 'active'
        })
        
    except Exception as e:
        logger.error(f"Upgrade subscription error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)