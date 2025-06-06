# flowlyne/management/commands/populate_new_schema.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from flowlyne.models import Admin, Company, Service, Category, Review, Payment, SubscriptionPlan, CompanySubscription, Advertising
from django.utils import timezone
from datetime import timedelta
import random

Company = get_user_model()

class Command(BaseCommand):
    help = 'Populate Flowlyne database with demo data for new schema'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting Flowlyne database population with new schema...'))
        
        # Create admin first
        self.create_admin()
        
        # Create a dummy payment record first (required for subscription plans)
        self.create_dummy_payment()
        
        # Create subscription plans
        self.create_subscription_plans()
        
        # Create demo companies
        self.create_demo_companies()
        
        # Create services and categories
        self.create_services_and_categories()
        
        # Create sample reviews
        self.create_sample_reviews()
        
        # Create advertisements
        self.create_advertisements()
        
        self.stdout.write(self.style.SUCCESS('✅ Database populated successfully!'))
        self.stdout.write('🔑 Demo login credentials:')
        self.stdout.write('   Email: info@techsolutions.eg | Password: demo123456')
        self.stdout.write('   Email: hello@creativestudio.alex | Password: demo123456')
        self.stdout.write('   Email: contact@digitalagency.cairo | Password: demo123456')
    
    def create_admin(self):
        """Create default admin"""
        self.stdout.write('👤 Creating admin...')
        
        admin, created = Admin.objects.get_or_create(
            email='admin@flowlyne.com',
            defaults={'password': 'admin123'}
        )
        
        if created:
            self.stdout.write(f'  ✅ Created admin: {admin.email}')
        else:
            self.stdout.write(f'  ✓ Admin already exists: {admin.email}')
        
        self.admin = admin
    
    def create_dummy_payment(self):
        """Create a dummy payment record for subscription plans"""
        self.stdout.write('💳 Creating dummy payment...')
        
        # We need a company first for the payment, so create a temporary one
        dummy_company, created = Company.objects.get_or_create(
            email='dummy@flowlyne.com',
            defaults={
                'username': 'dummy@flowlyne.com',
                'company_name': 'Dummy Company',
                'password': 'dummy123',
                'admin': self.admin
            }
        )
        
        # Create dummy payment
        self.dummy_payment, created = Payment.objects.get_or_create(
            payment_id=1,
            defaults={
                'start_date': timezone.now(),
                'end_date': timezone.now() + timedelta(days=30),
                'is_active': True,
                'payment_method': 'dummy',
                'company': dummy_company
            }
        )
        
        if created:
            self.stdout.write(f'  ✅ Created dummy payment: {self.dummy_payment.payment_id}')
    
    def create_subscription_plans(self):
        """Create subscription plans"""
        self.stdout.write('📋 Creating subscription plans...')
        
        plans_data = [
            {
                'plan_name': 'Basic Plan (Free)',
                'price_egp': 0.00,
                'search_ranking': 'Standard listing in search results',
                'plan_duration': timedelta(days=30),
                'portfolio_view': 'Basic company profile only',
                'portfolio_upload_per_month': '0 uploads per month',
                'comments_view': 'Cannot view or respond to comments',
                'commission_discount': '10% commission (standard rate)',
                'business_insights': 'Basic statistics only',
                'support_level': 'Email support',
                'featured_on_homepage': False,
                'priority_support': False,
                'advanced_analytics': False,
            },
            {
                'plan_name': 'Standard Plan',
                'price_egp': 200.00,
                'search_ranking': 'Higher ranking in search results',
                'plan_duration': timedelta(days=30),
                'portfolio_view': 'Full portfolio display',
                'portfolio_upload_per_month': '5 uploads per month',
                'comments_view': 'View and respond to all comments',
                'commission_discount': '8% commission (2% discount)',
                'business_insights': 'Engagement analytics and insights',
                'support_level': 'Priority email and chat support',
                'featured_on_homepage': False,
                'priority_support': True,
                'advanced_analytics': True,
            },
            {
                'plan_name': 'Premium Plan',
                'price_egp': 500.00,
                'search_ranking': 'Top-tier placement in search results',
                'plan_duration': timedelta(days=30),
                'portfolio_view': 'Advanced portfolio with priority exposure',
                'portfolio_upload_per_month': '10 uploads per month',
                'comments_view': 'Highlight top reviews and respond to comments',
                'commission_discount': '5% commission (5% discount)',
                'business_insights': 'Full analytics with client behavior trends',
                'support_level': 'Dedicated account manager',
                'featured_on_homepage': True,
                'priority_support': True,
                'advanced_analytics': True,
            }
        ]
        
        for plan_data in plans_data:
            plan, created = SubscriptionPlan.objects.get_or_create(
                plan_name=plan_data['plan_name'],
                defaults={
                    **plan_data,
                    'admin': self.admin,
                    'payment': self.dummy_payment,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created plan: {plan.plan_name}')
    
    def create_demo_companies(self):
        """Create demo companies"""
        self.stdout.write('🏢 Creating demo companies...')
        
        demo_companies = [
            {
                'company_name': 'TechSolutions Egypt',
                'email': 'info@techsolutions.eg',
                'password': 'demo123456',
                'description': 'Leading web development company in Egypt specializing in modern, scalable web applications.',
                'company_address': '123 Tahrir Square, Downtown, Cairo, Egypt',
                'phone_number': '+20-100-123-4567',
                'city': 'Cairo',
                'is_verified': True,
                'current_plan': 'basic',
            },
            {
                'company_name': 'Creative Studio Alexandria',
                'email': 'hello@creativestudio.alex',
                'password': 'demo123456',
                'description': 'Award-winning design agency providing comprehensive branding and visual identity solutions.',
                'company_address': '456 Corniche Road, Alexandria, Egypt',
                'phone_number': '+20-101-234-5678',
                'city': 'Alexandria',
                'is_verified': True,
                'current_plan': 'basic',
            },
            {
                'company_name': 'Digital Marketing Agency Cairo',
                'email': 'contact@digitalagency.cairo',
                'password': 'demo123456',
                'description': 'Full-service digital marketing agency helping Egyptian businesses grow online.',
                'company_address': '789 Zamalek District, Cairo, Egypt',
                'phone_number': '+20-102-345-6789',
                'city': 'Cairo',
                'is_verified': True,
                'current_plan': 'basic',
            },
            {
                'company_name': 'FinanceExpert Consultancy',
                'email': 'info@financeexpert.com.eg',
                'password': 'demo123456',
                'description': 'Professional accounting and financial consulting services for Egyptian businesses.',
                'company_address': '321 New Cairo, Cairo, Egypt',
                'phone_number': '+20-103-456-7890',
                'city': 'Cairo',
                'is_verified': False,
                'current_plan': 'basic',
            }
        ]
        
        self.companies = []
        for company_data in demo_companies:
            company, created = Company.objects.get_or_create(
                email=company_data['email'],
                defaults={
                    'username': company_data['email'],
                    'admin': self.admin,
                    **company_data
                }
            )
            
            if created:
                company.set_password(company_data['password'])
                company.save()
                self.stdout.write(f'  ✅ Created company: {company.company_name}')
            else:
                self.stdout.write(f'  ✓ Company already exists: {company.company_name}')
            
            self.companies.append(company)
    
    def create_services_and_categories(self):
        """Create services and categories"""
        self.stdout.write('🎯 Creating services and categories...')
        
        services_data = [
            {
                'company_index': 0,  # TechSolutions
                'service_name': 'Web Development',
                'service_description': 'Custom web applications using React, Django, and modern technologies',
                'categories': [
                    {'name': 'Frontend Development', 'description': 'React, Vue.js, Angular development'},
                    {'name': 'Backend Development', 'description': 'Django, Flask, Node.js development'},
                    {'name': 'E-commerce', 'description': 'Online store development'}
                ]
            },
            {
                'company_index': 0,  # TechSolutions
                'service_name': 'Mobile App Development',
                'service_description': 'Native and cross-platform mobile applications for iOS and Android',
                'categories': [
                    {'name': 'iOS Development', 'description': 'Native iOS applications'},
                    {'name': 'Android Development', 'description': 'Native Android applications'},
                    {'name': 'Cross-platform', 'description': 'React Native, Flutter apps'}
                ]
            },
            {
                'company_index': 1,  # Creative Studio
                'service_name': 'Graphic Design',
                'service_description': 'Professional branding and visual identity design services',
                'categories': [
                    {'name': 'Logo Design', 'description': 'Professional logo creation'},
                    {'name': 'Branding', 'description': 'Complete brand identity packages'},
                    {'name': 'Print Design', 'description': 'Brochures, flyers, business cards'}
                ]
            },
            {
                'company_index': 1,  # Creative Studio
                'service_name': 'UI/UX Design',
                'service_description': 'User interface and user experience design for web and mobile',
                'categories': [
                    {'name': 'Web UI Design', 'description': 'Website user interface design'},
                    {'name': 'Mobile UI Design', 'description': 'Mobile app interface design'},
                    {'name': 'UX Research', 'description': 'User experience research and testing'}
                ]
            },
            {
                'company_index': 2,  # Digital Marketing
                'service_name': 'Digital Marketing',
                'service_description': 'Comprehensive digital marketing strategies and campaigns',
                'categories': [
                    {'name': 'SEO', 'description': 'Search engine optimization'},
                    {'name': 'Social Media Marketing', 'description': 'Facebook, Instagram, LinkedIn marketing'},
                    {'name': 'PPC Advertising', 'description': 'Google Ads, Facebook Ads management'}
                ]
            },
            {
                'company_index': 3,  # FinanceExpert
                'service_name': 'Accounting & Finance',
                'service_description': 'Professional accounting and financial consulting services',
                'categories': [
                    {'name': 'Bookkeeping', 'description': 'Daily financial record keeping'},
                    {'name': 'Tax Services', 'description': 'Tax preparation and filing'},
                    {'name': 'Financial Consulting', 'description': 'Business financial advice'}
                ]
            }
        ]
        
        self.services = []
        for service_data in services_data:
            company = self.companies[service_data['company_index']]
            
            service, created = Service.objects.get_or_create(
                service_name=service_data['service_name'],
                company=company,
                defaults={
                    'service_description': service_data['service_description'],
                    'admin': self.admin
                }
            )
            
            if created:
                self.stdout.write(f'  ✅ Created service: {service.service_name} for {company.company_name}')
                
                # Create categories for this service
                for cat_data in service_data['categories']:
                    category, cat_created = Category.objects.get_or_create(
                        category_name=cat_data['name'],
                        service=service,
                        defaults={
                            'category_description': cat_data['description'],
                            'admin': self.admin
                        }
                    )
                    if cat_created:
                        self.stdout.write(f'    ✓ Created category: {category.category_name}')
            
            self.services.append(service)
    
    def create_sample_reviews(self):
        """Create sample reviews"""
        self.stdout.write('⭐ Creating sample reviews...')
        
        if len(self.companies) < 2 or len(self.services) < 2:
            return
        
        sample_reviews = [
            {
                'rating': 5,
                'title': 'Exceptional Web Development Work',
                'content': 'TechSolutions delivered an outstanding website that exceeded our expectations.',
                'project_type': 'Website Development',
                'project_duration': timedelta(days=60),
                'would_recommend': True,
                'is_verified': True,
                'company': self.companies[0],  # TechSolutions
                'service': self.services[0] if len(self.services) > 0 else None
            },
            {
                'rating': 5,
                'title': 'Professional Design Services',
                'content': 'Creative Studio created amazing branding materials for our business.',
                'project_type': 'Brand Identity',
                'project_duration': timedelta(days=30),
                'would_recommend': True,
                'is_verified': True,
                'company': self.companies[1],  # Creative Studio
                'service': self.services[1] if len(self.services) > 1 else self.services[0]
            }
        ]
        
        for review_data in sample_reviews:
            if review_data['service']:  # Only create if service exists
                review, created = Review.objects.get_or_create(
                    title=review_data['title'],
                    company=review_data['company'],
                    defaults={
                        **review_data,
                        'admin': self.admin
                    }
                )
                if created:
                    self.stdout.write(f'  ✓ Created review: {review.title}')
    
    def create_advertisements(self):
        """Create sample advertisements"""
        self.stdout.write('📢 Creating advertisements...')
        
        ads_data = [
            {
                'image': '/static/images/ad1.jpg',
                'price': 1000.00,
                'start_date': timezone.now(),
                'end_date': timezone.now() + timedelta(days=30)
            },
            {
                'image': '/static/images/ad2.jpg',
                'price': 1500.00,
                'start_date': timezone.now(),
                'end_date': timezone.now() + timedelta(days=30)
            }
        ]
        
        for ad_data in ads_data:
            ad, created = Advertising.objects.get_or_create(
                image=ad_data['image'],
                defaults={
                    **ad_data,
                    'admin': self.admin
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created advertisement: {ad.image}')

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset existing data before populating',
        )