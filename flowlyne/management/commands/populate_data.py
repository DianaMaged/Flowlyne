from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from flowlyne.models import Department, Company, CompanyDepartment

Company = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with initial data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate database...'))
        
        # Create departments
        departments_data = [
            {'name': 'Web Development', 'icon': '💻', 'description': 'Website and web application development'},
            {'name': 'Mobile App Development', 'icon': '📱', 'description': 'iOS and Android mobile applications'},
            {'name': 'Digital Marketing', 'icon': '📈', 'description': 'SEO, social media, and online marketing'},
            {'name': 'Graphic Design', 'icon': '🎨', 'description': 'Logo design, branding, and visual content'},
            {'name': 'Business Consulting', 'icon': '🎯', 'description': 'Strategy, operations, and management consulting'},
            {'name': 'Accounting & Finance', 'icon': '💰', 'description': 'Bookkeeping, financial planning, and tax services'},
        ]
        
        for dept_data in departments_data:
            department, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={'icon': dept_data['icon'], 'description': dept_data['description']}
            )
            if created:
                self.stdout.write(f'  ✓ Created department: {department.name}')
        
        # Create demo companies
        demo_companies = [
            {
                'company_name': 'TechSolutions Egypt',
                'email': 'info@techsolutions.eg',
                'password': 'demo123456',
                'description': 'Leading web development company in Egypt.',
                'company_address': '123 Tahrir Square, Cairo, Egypt',
                'phone_number': '+20-100-123-4567',
                'city': 'Cairo',
                'is_verified': True,
                'departments': ['Web Development']
            },
            {
                'company_name': 'Creative Studio Alexandria',
                'email': 'hello@creativestudio.alex',
                'password': 'demo123456',
                'description': 'Award-winning design agency in Alexandria.',
                'company_address': '456 Corniche Road, Alexandria, Egypt',
                'phone_number': '+20-101-234-5678',
                'city': 'Alexandria',
                'is_verified': True,
                'departments': ['Graphic Design']
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
                self.stdout.write(f'  ✓ Created company: {company.company_name}')
                
                for dept_name in departments_list:
                    try:
                        department = Department.objects.get(name=dept_name)
                        CompanyDepartment.objects.get_or_create(
                            company=company, department=department,
                            defaults={'is_primary': True}
                        )
                    except Department.DoesNotExist:
                        pass
        
        self.stdout.write(self.style.SUCCESS('✅ Database populated successfully!'))
        self.stdout.write('Demo login: info@techsolutions.eg / demo123456')