from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from flowlyne.models import Admin

Company = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser for Flowlyne with proper admin relationship'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email for the superuser')
        parser.add_argument('--company_name', type=str, help='Company name for the superuser')
        parser.add_argument('--password', type=str, help='Password for the superuser')

    def handle(self, *args, **options):
        email = options.get('email')
        company_name = options.get('company_name')
        password = options.get('password')

        # Prompt for input if not provided
        if not email:
            email = input('Email: ')
        if not company_name:
            company_name = input('Company name: ')
        if not password:
            import getpass
            password = getpass.getpass('Password: ')

        # Check if user already exists
        if Company.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.ERROR(f'User with email {email} already exists!')
            )
            return

        try:
            # Create or get default admin
            admin, created = Admin.objects.get_or_create(
                email='admin@flowlyne.com',
                defaults={'password': 'admin123'}
            )

            if created:
                self.stdout.write(f'Created default admin: {admin.email}')

            # Create superuser
            superuser = Company.objects.create_superuser(
                email=email,
                company_name=company_name,
                password=password,
                admin=admin
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'Superuser {superuser.email} created successfully!'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {str(e)}')
            )