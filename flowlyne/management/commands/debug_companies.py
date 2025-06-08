# flowlyne/management/commands/debug_companies.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from flowlyne.models import Company, Service, Review

Company = get_user_model()

class Command(BaseCommand):
    help = 'Debug companies in the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Debugging companies in database...'))
        
        # Check total companies
        total_companies = Company.objects.count()
        self.stdout.write(f'📊 Total companies: {total_companies}')
        
        if total_companies == 0:
            self.stdout.write(self.style.WARNING('⚠️  No companies found in database'))
            self.stdout.write('💡 Run: python manage.py populate_new_schema to add demo data')
            return
        
        # List all companies
        self.stdout.write('\n📋 All companies:')
        for company in Company.objects.all()[:10]:  # Limit to first 10
            self.stdout.write(f'  ID: {company.company_id} | Name: {company.company_name} | Active: {company.is_active}')
        
        if total_companies > 10:
            self.stdout.write(f'  ... and {total_companies - 10} more companies')
        
        # Check services
        total_services = Service.objects.count()
        self.stdout.write(f'\n🛍️  Total services: {total_services}')
        
        # Check reviews
        total_reviews = Review.objects.count()
        self.stdout.write(f'⭐ Total reviews: {total_reviews}')
        
        # Test company ID 1 specifically
        try:
            company_1 = Company.objects.get(company_id=1)
            self.stdout.write(f'\n✅ Company ID 1 exists: {company_1.company_name}')
            self.stdout.write(f'   Active: {company_1.is_active}')
            self.stdout.write(f'   Services: {company_1.services.count()}')
        except Company.DoesNotExist:
            self.stdout.write(f'\n❌ Company ID 1 does not exist')
            
        self.stdout.write(self.style.SUCCESS('\n✅ Debug complete!'))