# flowlyne/management/commands/populate_flowlyne.py - FIXED VERSION

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from flowlyne.models import Department, Company, CompanyDepartment, SubscriptionPlan, CompanyReview
from django.utils import timezone
import random

Company = get_user_model()

class Command(BaseCommand):
    help = 'Populate Flowlyne database with comprehensive demo data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting Flowlyne database population...'))
        
        # Create subscription plans
        self.create_subscription_plans()
        
        # Create departments
        self.create_departments()
        
        # Create demo companies - ALL START WITH BASIC PLAN
        self.create_demo_companies()
        
        # Create sample reviews
        self.create_sample_reviews()
        
        self.stdout.write(self.style.SUCCESS('✅ Database populated successfully!'))
        self.stdout.write('🔑 Demo login credentials (ALL start with Basic Plan):')
        self.stdout.write('   Email: info@techsolutions.eg | Password: demo123456 | Plan: BASIC')
        self.stdout.write('   Email: hello@creativestudio.alex | Password: demo123456 | Plan: BASIC')
        self.stdout.write('   Email: contact@digitalagency.cairo | Password: demo123456 | Plan: BASIC')
    
    def create_subscription_plans(self):
        """Create subscription plans"""
        self.stdout.write('📋 Creating subscription plans...')
        
        plans_data = [
            {
                'name': 'basic',
                'display_name': 'Basic Plan (Free)',
                'price_egp': 0.00,
                'price_period': 'month',
                'search_ranking': 'Standard listing in search results',
                'portfolio_view': 'Basic company profile only',
                'portfolio_uploads_per_month': 0,
                'comments_view': 'Cannot view or respond to comments',
                'commission_discount': '10% commission (standard rate)',
                'business_insights': 'Basic statistics only',
                'support_level': 'Email support',
                'featured_on_homepage': False,
                'priority_support': False,
                'advanced_analytics': False,
            },
            {
                'name': 'standard',
                'display_name': 'Standard Plan',
                'price_egp': 200.00,
                'price_period': 'month',
                'search_ranking': 'Higher ranking in search results',
                'portfolio_view': 'Full portfolio display',
                'portfolio_uploads_per_month': 5,
                'comments_view': 'View and respond to all comments',
                'commission_discount': '8% commission (2% discount)',
                'business_insights': 'Engagement analytics and insights',
                'support_level': 'Priority email and chat support',
                'featured_on_homepage': False,
                'priority_support': True,
                'advanced_analytics': True,
            },
            {
                'name': 'premium',
                'display_name': 'Premium Plan',
                'price_egp': 500.00,
                'price_period': 'month',
                'search_ranking': 'Top-tier placement in search results',
                'portfolio_view': 'Advanced portfolio with priority exposure',
                'portfolio_uploads_per_month': 10,
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
                name=plan_data['name'],
                defaults=plan_data
            )
            if created:
                self.stdout.write(f'  ✓ Created plan: {plan.display_name}')
    
    def create_departments(self):
        """Create service departments"""
        self.stdout.write('🏢 Creating service departments...')
        
        departments_data = [
            {'name': 'Web Development', 'icon': '💻', 'description': 'Full-stack web development, e-commerce, and web applications'},
            {'name': 'Mobile App Development', 'icon': '📱', 'description': 'iOS and Android native and cross-platform mobile applications'},
            {'name': 'Digital Marketing', 'icon': '📈', 'description': 'SEO, social media marketing, PPC, and digital advertising'},
            {'name': 'Graphic Design', 'icon': '🎨', 'description': 'Logo design, branding, print design, and visual identity'},
            {'name': 'Business Consulting', 'icon': '🎯', 'description': 'Strategy consulting, operations, and management advisory'},
            {'name': 'Accounting & Finance', 'icon': '💰', 'description': 'Bookkeeping, financial planning, tax services, and auditing'},
            {'name': 'Content Creation', 'icon': '✍️', 'description': 'Content writing, copywriting, and content marketing'},
            {'name': 'UI/UX Design', 'icon': '🖌️', 'description': 'User interface and user experience design'},
            {'name': 'Video Production', 'icon': '🎬', 'description': 'Video editing, animation, and multimedia production'},
            {'name': 'IT Support', 'icon': '🔧', 'description': 'Technical support, system administration, and IT consulting'},
        ]
        
        for dept_data in departments_data:
            department, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={'icon': dept_data['icon'], 'description': dept_data['description']}
            )
            if created:
                self.stdout.write(f'  ✓ Created department: {department.name}')
    
    def create_demo_companies(self):
        """Create comprehensive demo companies - ALL START WITH BASIC PLAN"""
        self.stdout.write('🏢 Creating demo companies (ALL starting with Basic Plan)...')
        
        demo_companies = [
            {
                'company_name': 'TechSolutions Egypt',
                'email': 'info@techsolutions.eg',
                'password': 'demo123456',
                'description': 'Leading web development company in Egypt specializing in modern, scalable web applications. We help businesses establish their digital presence with cutting-edge technology and innovative solutions.',
                'company_address': '123 Tahrir Square, Downtown, Cairo, Egypt',
                'phone_number': '+20-100-123-4567',
                'website': 'https://techsolutions.eg',
                'city': 'Cairo',
                'is_verified': True,
                'current_plan': 'basic',  # ✅ FIXED: Start with basic
                'departments': ['Web Development', 'Mobile App Development']
            },
            {
                'company_name': 'Creative Studio Alexandria',
                'email': 'hello@creativestudio.alex',
                'password': 'demo123456',
                'description': 'Award-winning design agency in Alexandria providing comprehensive branding and visual identity solutions. We transform businesses through powerful design and creative storytelling.',
                'company_address': '456 Corniche Road, Alexandria, Egypt',
                'phone_number': '+20-101-234-5678',
                'website': 'https://creativestudio.alex',
                'city': 'Alexandria',
                'is_verified': True,
                'current_plan': 'basic',  # ✅ FIXED: Start with basic
                'departments': ['Graphic Design', 'UI/UX Design']
            },
            {
                'company_name': 'Digital Marketing Agency Cairo',
                'email': 'contact@digitalagency.cairo',
                'password': 'demo123456',
                'description': 'Full-service digital marketing agency helping Egyptian businesses grow online. From SEO to social media, we deliver results-driven digital marketing strategies.',
                'company_address': '789 Zamalek District, Cairo, Egypt',
                'phone_number': '+20-102-345-6789',
                'website': 'https://digitalagency.cairo',
                'city': 'Cairo',
                'is_verified': True,
                'current_plan': 'basic',  # ✅ FIXED: Start with basic
                'departments': ['Digital Marketing', 'Content Creation']
            },
            {
                'company_name': 'FinanceExpert Consultancy',
                'email': 'info@financeexpert.com.eg',
                'password': 'demo123456',
                'description': 'Professional accounting and financial consulting services for Egyptian businesses. We provide comprehensive financial solutions including bookkeeping, tax planning, and business advisory.',
                'company_address': '321 New Cairo, Cairo, Egypt',
                'phone_number': '+20-103-456-7890',
                'website': 'https://financeexpert.com.eg',
                'city': 'Cairo',
                'is_verified': False,
                'current_plan': 'basic',  # ✅ FIXED: Start with basic
                'departments': ['Accounting & Finance', 'Business Consulting']
            },
            {
                'company_name': 'MediaPro Productions',
                'email': 'info@mediapro.eg',
                'password': 'demo123456',
                'description': 'Professional video production and multimedia services. We create compelling visual content for businesses, from corporate videos to social media content.',
                'company_address': '654 Maadi, Cairo, Egypt',
                'phone_number': '+20-104-567-8901',
                'city': 'Cairo',
                'is_verified': True,
                'current_plan': 'basic',  # ✅ FIXED: Start with basic
                'departments': ['Video Production', 'Content Creation']
            },
            {
                'company_name': 'TechSupport Solutions',
                'email': 'support@techsupport.eg',
                'password': 'demo123456',
                'description': 'Reliable IT support and technical services for businesses across Egypt. We provide 24/7 technical support, system administration, and IT consulting.',
                'company_address': '987 Heliopolis, Cairo, Egypt',
                'phone_number': '+20-105-678-9012',
                'city': 'Cairo',
                'is_verified': False,
                'current_plan': 'basic',  # ✅ FIXED: Start with basic
                'departments': ['IT Support']
            }
        ]
        
        for company_data in demo_companies:
            departments_list = company_data.pop('departments', [])
            
            company, created = Company.objects.get_or_create(
                email=company_data['email'],
                defaults={'username': company_data['email'], **company_data}
            )
            
            if created:
                company.set_password(company_data['password'])
                company.save()
                self.stdout.write(f'  ✅ Created company: {company.company_name} (Plan: {company.current_plan.upper()})')
                
                # Add departments
                for i, dept_name in enumerate(departments_list):
                    try:
                        department = Department.objects.get(name=dept_name)
                        CompanyDepartment.objects.get_or_create(
                            company=company, 
                            department=department,
                            defaults={'is_primary': i == 0}  # First department is primary
                        )
                    except Department.DoesNotExist:
                        pass
            else:
                # Update existing company to basic plan if needed
                if company.current_plan != 'basic':
                    old_plan = company.current_plan
                    company.current_plan = 'basic'
                    company.save()
                    self.stdout.write(f'  🔄 Updated {company.company_name}: {old_plan} → basic')
    
    def create_sample_reviews(self):
        """Create sample reviews for demo companies"""
        self.stdout.write('⭐ Creating sample reviews...')
        
        # Get companies for reviews
        companies = list(Company.objects.filter(is_verified=True))
        
        if len(companies) < 2:
            return
        
        sample_reviews = [
            {
                'reviewer': companies[0],
                'reviewed_company': companies[1],
                'rating': 5,
                'title': 'Exceptional Design Work',
                'content': 'Creative Studio Alexandria delivered outstanding branding work for our company. Their attention to detail and creative vision exceeded our expectations.',
                'project_type': 'Brand Identity Design',
                'project_duration': '3 months',
                'project_budget_range': 'EGP 50,000 - 100,000',
                'would_recommend': True,
                'is_verified': True
            },
            {
                'reviewer': companies[1],
                'reviewed_company': companies[0],
                'rating': 5,
                'title': 'Professional Web Development',
                'content': 'TechSolutions Egypt built our company website with great professionalism and technical expertise. The site is fast, responsive, and exactly what we needed.',
                'project_type': 'Website Development',
                'project_duration': '2 months',
                'project_budget_range': 'EGP 30,000 - 50,000',
                'would_recommend': True,
                'is_verified': True
            }
        ]
        
        if len(companies) >= 3:
            sample_reviews.extend([
                {
                    'reviewer': companies[2],
                    'reviewed_company': companies[0],
                    'rating': 4,
                    'title': 'Great Development Team',
                    'content': 'Working with TechSolutions was a positive experience. They delivered on time and provided good technical support throughout the project.',
                    'project_type': 'E-commerce Platform',
                    'project_duration': '4 months',
                    'project_budget_range': 'EGP 100,000+',
                    'would_recommend': True,
                    'is_verified': True
                },
                {
                    'reviewer': companies[0],
                    'reviewed_company': companies[2],
                    'rating': 5,
                    'title': 'Excellent Marketing Results',
                    'content': 'Digital Marketing Agency Cairo helped us increase our online visibility significantly. Our website traffic and leads have doubled since working with them.',
                    'project_type': 'Digital Marketing Campaign',
                    'project_duration': '6 months',
                    'project_budget_range': 'EGP 20,000 - 30,000',
                    'would_recommend': True,
                    'is_verified': True
                }
            ])
        
        for review_data in sample_reviews:
            review, created = CompanyReview.objects.get_or_create(
                reviewer=review_data['reviewer'],
                reviewed_company=review_data['reviewed_company'],
                defaults=review_data
            )
            if created:
                self.stdout.write(f'  ✓ Created review: {review.reviewer.company_name} → {review.reviewed_company.company_name}')

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset existing data before populating',
        )
        parser.add_argument(
            '--fix-plans',
            action='store_true',
            help='Fix all existing companies to start with basic plan',
        )
    
    def handle(self, *args, **options):
        if options.get('fix_plans'):
            self.fix_existing_plans()
            return
            
        # Continue with normal population...
        self.stdout.write(self.style.SUCCESS('🚀 Starting Flowlyne database population...'))
        # ... rest of the method
    
    def fix_existing_plans(self):
        """Fix all existing companies to have basic plan"""
        self.stdout.write(self.style.WARNING('🔧 Fixing existing company plans...'))
        
        companies = Company.objects.all()
        fixed_count = 0
        
        for company in companies:
            if company.current_plan != 'basic':
                old_plan = company.current_plan
                company.current_plan = 'basic'
                company.save()
                self.stdout.write(f'  🔄 Fixed {company.company_name}: {old_plan} → basic')
                fixed_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'✅ Fixed {fixed_count} companies to start with Basic Plan'))
