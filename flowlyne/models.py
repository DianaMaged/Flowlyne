from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from datetime import timedelta

class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)  # Changed from Email to email
    password = models.CharField(max_length=128)
    
    class Meta:
        db_table = 'admin'
    
    def __str__(self):
        return self.email

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
    company_id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=250)
    company_address = models.CharField(max_length=250, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)  # Changed from varchar to specific length
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    logo = models.CharField(max_length=255, blank=True)  # Store file path as varchar
    date_joined = models.DateTimeField(auto_now_add=True)
    certification = models.CharField(max_length=255, blank=True)  # Store file path as varchar
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    current_plan = models.CharField(max_length=20, default='basic')  # Changed from choices
    city = models.CharField(max_length=100, default="Cairo")
    country = models.CharField(max_length=100, default="Egypt")
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='companies', db_column='admin_id')
    
    # Use email as username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['company_name']
    
    objects = CompanyManager()
    
    class Meta:
        db_table = 'company'
        verbose_name = "Company"
        verbose_name_plural = "Companies"
    
    def __str__(self):
        return self.company_name

class Service(models.Model):
    service_id = models.AutoField(primary_key=True)
    service_name = models.CharField(max_length=200)
    service_description = models.TextField()  # Changed from varchar to text
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='services', db_column='admin_id')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='services', db_column='company_id')
    
    class Meta:
        db_table = 'service'
    
    def __str__(self):
        return f"{self.company.company_name} - {self.service_name}"

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100)
    category_description = models.TextField(blank=True)
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='categories', db_column='admin_id')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='categories', db_column='service_id')
    
    class Meta:
        db_table = 'category'
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.category_name

class Advertising(models.Model):
    adv_id = models.AutoField(primary_key=True)
    image = models.CharField(max_length=255)  # Store file path as varchar
    price = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='advertisements', db_column='admin_id')
    
    class Meta:
        db_table = 'advertising'
    
    def __str__(self):
        return f"Ad {self.adv_id} - {self.price}"

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    last_payment_date = models.DateTimeField(null=True, blank=True)
    next_payment_date = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='payments', db_column='company_id')
    adv = models.ForeignKey(Advertising, on_delete=models.CASCADE, related_name='payments', null=True, blank=True, db_column='adv_id')
    
    class Meta:
        db_table = 'payment'
    
    def __str__(self):
        return f"Payment {self.payment_id} - {self.company.company_name}"

class SubscriptionPlan(models.Model):
    plan_id = models.AutoField(primary_key=True)
    plan_name = models.CharField(max_length=100)
    price_egp = models.DecimalField(max_digits=10, decimal_places=2)
    search_ranking = models.CharField(max_length=200)
    plan_duration = models.DurationField(default=timedelta(days=30))  # Changed from timestamp to duration
    portfolio_view = models.CharField(max_length=200)
    portfolio_upload_per_month = models.CharField(max_length=100)
    comments_view = models.CharField(max_length=200)
    commission_discount = models.CharField(max_length=200)
    business_insights = models.CharField(max_length=200)
    support_level = models.CharField(max_length=200)  # Fixed typo from varcher
    featured_on_homepage = models.BooleanField(default=False)
    priority_support = models.BooleanField(default=False)  # Fixed typo from pirority_support
    advanced_analytics = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='subscription_plans', db_column='admin_id')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='subscription_plans', db_column='payment_id')
    
    class Meta:
        db_table = 'subscriptionplan'
    
    def __str__(self):
        return f"{self.plan_name} - {self.price_egp} EGP"

class CompanySubscription(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, db_column='company_id')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, db_column='plan_id')
    
    class Meta:
        db_table = 'companysubscription'
        unique_together = ['company', 'plan']
    
    def __str__(self):
        return f"{self.company.company_name} - {self.plan.plan_name}"

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=200)
    content = models.TextField()
    project_type = models.CharField(max_length=100, blank=True)
    project_duration = models.DurationField(default=timedelta(days=30))  # Changed from timestamp to duration
    would_recommend = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='reviews', db_column='admin_id')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='received_reviews', db_column='company_id')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews', db_column='service_id')
    
    class Meta:
        db_table = 'review'
    
    def __str__(self):
        return f"Review {self.review_id} - {self.company.company_name} ({self.rating}★)"