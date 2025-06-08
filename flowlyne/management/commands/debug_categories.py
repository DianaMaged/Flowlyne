# flowlyne/management/commands/debug_categories.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from flowlyne.models import Company, Service, Category

Company = get_user_model()

class Command(BaseCommand):
    help = 'Debug service categories and filtering'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Debugging service categories and filtering...'))
        
        # Check companies and their services
        companies = Company.objects.filter(is_active=True)
        self.stdout.write(f'📊 Active companies: {companies.count()}')
        
        if companies.count() == 0:
            self.stdout.write(self.style.WARNING('⚠️  No active companies found'))
            return
        
        # Check services and categories
        services = Service.objects.all()
        self.stdout.write(f'🛍️  Total services: {services.count()}')
        
        # Get all unique service categories
        categories = set()
        for service in services:
            if service.category:
                categories.add(service.category)
        
        self.stdout.write(f'\n📋 Available service categories:')
        for category in sorted(categories):
            service_count = services.filter(category=category).count()
            company_count = companies.filter(services__category=category).distinct().count()
            self.stdout.write(f'  • {category}: {service_count} services, {company_count} companies')
        
        if not categories:
            self.stdout.write(self.style.WARNING('⚠️  No service categories found'))
            self.stdout.write('💡 Services might not have categories assigned')
        
        # Test the filtering for each category
        self.stdout.write(f'\n🔧 Testing filter functionality:')
        test_categories = ['Web Development', 'Mobile App Development', 'Digital Marketing', 'Graphic Design']
        
        for test_cat in test_categories:
            matching_companies = companies.filter(services__category__icontains=test_cat).distinct()
            self.stdout.write(f'  • "{test_cat}": {matching_companies.count()} companies')
            
            if matching_companies.exists():
                for company in matching_companies[:3]:  # Show first 3
                    self.stdout.write(f'    - {company.company_name}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Category debug complete!'))