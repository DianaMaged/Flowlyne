from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Avg, Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
import json

from .models import Company, Department, CompanyDepartment

# Frontend views
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

# API Views

@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    """Register a new company"""
    try:
        data = request.data
        
        # Validate required fields
        required_fields = ['company_name', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return Response({'error': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if email already exists
        if Company.objects.filter(email=data['email']).exists():
            return Response({'error': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)
        
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
            current_plan='basic'  # Add this line - all new users start with basic plan
        )
        
        # Handle file uploads if present
        if 'logo' in request.FILES:
            company.logo = request.FILES['logo']
        if 'portfolio' in request.FILES:
            company.portfolio = request.FILES['portfolio']
        if 'certifications' in request.FILES:
            company.certifications = request.FILES['certifications']
        
        company.save()
        
        # Add departments
        departments = data.get('departments', [])
        if departments:
            for dept_name in departments:
                try:
                    department = Department.objects.get(name=dept_name)
                    CompanyDepartment.objects.create(
                        company=company,
                        department=department,
                        is_primary=len(departments) == 1
                    )
                except Department.DoesNotExist:
                    pass
        
        # Create auth token
        token, created = Token.objects.get_or_create(user=company)
        
        # Return company data
        company_data = {
            'id': str(company.id),
            'company_name': company.company_name,
            'email': company.email,
            'description': company.description,
            'city': company.city,
            'country': company.country,
            'is_verified': company.is_verified,
            'created_at': company.created_at.isoformat()
        }
        
        return Response({
            'message': 'Company registered successfully',
            'company': company_data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """Login company"""
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({'error': 'Email and password required'}, status=status.HTTP_400_BAD_REQUEST)
        
        company = authenticate(request, username=email, password=password)
        
        if company:
            login(request, company)
            
            # Get or create auth token
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
                'created_at': company.created_at.isoformat()
            }
            
            return Response({
                'message': 'Login successful',
                'company': company_data,
                'token': token.key
            })
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def api_companies(request):
    """Get all companies (service providers)"""
    try:
        companies = Company.objects.filter(is_active=True).prefetch_related('departments__department')
        
        # Add search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            companies = companies.filter(
                Q(company_name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(departments__department__name__icontains=search_query)
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
        companies_data.sort(key=lambda x: (x['is_verified'], x['company_name']), reverse=True)
        
        return Response(companies_data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
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
        
        return Response(company_data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
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
        return Response(departments_data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def api_stats(request):
    """Get platform statistics"""
    try:
        stats = {
            'total_companies': Company.objects.filter(is_active=True).count(),
            'verified_companies': Company.objects.filter(is_active=True, is_verified=True).count(),
            'total_departments': Department.objects.filter(is_active=True).count(),
            'total_messages': 0,  # Placeholder
        }
        return Response(stats)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_send_message(request):
    """Send message to another company"""
    try:
        receiver_id = request.data.get('receiver_id')
        subject = request.data.get('subject')
        message = request.data.get('message')
        
        if not receiver_id or not message:
            return Response({'error': 'Receiver ID and message are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        receiver = get_object_or_404(Company, id=receiver_id)
        
        # In a real app, you'd create a Message model and save this
        # For now, just return success
        
        return Response({
            'message': 'Message sent successfully',
            'id': 'demo-message-id'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

def plans(request):
    return render(request, 'plans.html')

@api_view(['GET'])
@permission_classes([AllowAny])
def api_subscription_plans(request):
    """Get all available subscription plans"""
    try:
        # For demo purposes, return static data
        # In a real app, this would query the SubscriptionPlan model
        plans = [
            {
                'id': 1,
                'name': 'basic',
                'display_name': 'Basic Plan (Free)',
                'price_egp': 0,
                'features': [
                    'Standard listing',
                    'Basic profile',
                    'Email support',
                    '5 project uploads'
                ]
            },
            {
                'id': 2,
                'name': 'standard',
                'display_name': 'Standard Plan',
                'price_egp': 200,
                'features': [
                    'Higher search ranking',
                    'Portfolio showcase',
                    'Priority support',
                    'Analytics dashboard'
                ]
            },
            {
                'id': 3,
                'name': 'premium',
                'display_name': 'Premium Plan',
                'price_egp': 500,
                'features': [
                    'Top placement',
                    'Featured on homepage',
                    'Advanced analytics',
                    'Dedicated support'
                ]
            }
        ]
        return Response(plans)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_upgrade_subscription(request):
    """Upgrade user's subscription plan"""
    try:
        plan_type = request.data.get('plan_type')
        if not plan_type:
            return Response({'error': 'Plan type required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # In a real app, this would:
        # 1. Process payment
        # 2. Update user's subscription in database
        # 3. Send confirmation email
        
        # For demo purposes, just return success
        return Response({
            'message': f'Successfully upgraded to {plan_type} plan',
            'plan_type': plan_type,
            'status': 'active'
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
def payment(request):
    """Payment page for subscription upgrades"""
    return render(request, 'payment.html')