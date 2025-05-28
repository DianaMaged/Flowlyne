from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid

class CompanyManager(BaseUserManager):
    """Custom manager for Company model"""
    
    def create_user(self, email, company_name, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        if not company_name:
            raise ValueError('Company name is required')
            
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=email,  # Use email as username
            company_name=company_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, company_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        return self.create_user(email, company_name, password, **extra_fields)

class Company(AbstractUser):
    """Custom User model representing a Company"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic company information
    company_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    
    # Contact information
    company_address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=17, blank=True)
    
    # Company details
    description = models.TextField(help_text="Describe your company and what you do", blank=True)
    website = models.URLField(blank=True, null=True)
    
    # Verification and media
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    portfolio = models.FileField(upload_to='company_portfolios/', blank=True, null=True)
    certifications = models.FileField(upload_to='company_certifications/', blank=True, null=True)
    
    # Verification status
    is_verified = models.BooleanField(default=False)
    
    # Location
    city = models.CharField(max_length=100, default="Cairo")
    country = models.CharField(max_length=100, default="Egypt")

    # Subscription Plan (FIXED - removed duplicate)
    current_plan = models.CharField(
        max_length=20, 
        default='basic', 
        choices=[
            ('basic', 'Basic Plan (Free)'),
            ('standard', 'Standard Plan'),
            ('premium', 'Premium Plan')
        ],
        help_text="Current subscription plan"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Use email as username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['company_name']
    
    # Use custom manager
    objects = CompanyManager()
    
    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
    
    def __str__(self):
        return self.company_name

class Department(models.Model):
    """Service departments/categories"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, help_text="Emoji icon for the department")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.icon} {self.name}"

class CompanyDepartment(models.Model):
    """Many-to-many relationship between companies and departments"""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='departments')
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['company', 'department']
    
    def __str__(self):
        return f"{self.company.company_name} - {self.department.name}"

class SubscriptionPlan(models.Model):
    """Subscription plans available on the platform"""
    PLAN_CHOICES = [
        ('basic', 'Basic Plan (Free)'),
        ('standard', 'Standard Plan'),
        ('premium', 'Premium Plan'),
    ]
    
    name = models.CharField(max_length=20, choices=PLAN_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    price_egp = models.DecimalField(max_digits=10, decimal_places=2)
    price_period = models.CharField(max_length=20, default='month')
    
    # Features
    search_ranking = models.CharField(max_length=200)
    portfolio_view = models.CharField(max_length=200)
    portfolio_uploads_per_month = models.IntegerField()
    comments_view = models.CharField(max_length=200)
    commission_discount = models.CharField(max_length=200)
    business_insights = models.CharField(max_length=200)
    support_level = models.CharField(max_length=200)
    
    # Additional benefits
    featured_on_homepage = models.BooleanField(default=False)
    priority_support = models.BooleanField(default=False)
    advanced_analytics = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['price_egp']
    
    def __str__(self):
        return f"{self.display_name} - EGP {self.price_egp}/{self.price_period}"

class CompanySubscription(models.Model):
    """Company's current subscription"""
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    
    # Subscription details
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    auto_renewal = models.BooleanField(default=True)
    
    # Payment tracking
    last_payment_date = models.DateTimeField(null=True, blank=True)
    next_payment_date = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.company.company_name} - {self.plan.display_name}"
    
    @property
    def is_expired(self):
        if not self.end_date:
            return False
        from django.utils import timezone
        return timezone.now() > self.end_date

# Add additional models for messaging system
class Message(models.Model):
    """Messages between companies"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='received_messages')
    
    subject = models.CharField(max_length=200)
    content = models.TextField()
    
    is_read = models.BooleanField(default=False)
    replied_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sender.company_name} → {self.receiver.company_name}: {self.subject}"

class CompanyReview(models.Model):
    """Reviews for companies"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reviewer = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='given_reviews')
    reviewed_company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='received_reviews')
    
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    # Project details
    project_type = models.CharField(max_length=100, blank=True)
    project_duration = models.CharField(max_length=50, blank=True)
    project_budget_range = models.CharField(max_length=50, blank=True)
    
    would_recommend = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)  # For verified project reviews
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['reviewer', 'reviewed_company']  # One review per company pair
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.reviewer.company_name} → {self.reviewed_company.company_name} ({self.rating}★)"