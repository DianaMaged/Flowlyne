from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from datetime import timedelta

class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email

class CompanyManager(BaseUserManager):
    def create_user(self, email, company_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, company_name=company_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, company_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, company_name, password, **extra_fields)

class Company(AbstractBaseUser, PermissionsMixin):
    company_id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    company_address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    logo = models.CharField(max_length=500, blank=True, null=True)
    certification = models.CharField(max_length=500, blank=True, null=True)
    city = models.CharField(max_length=100, default='Cairo')
    country = models.CharField(max_length=100, default='Egypt')
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    current_plan = models.CharField(max_length=50, default='basic')
    admin = models.ForeignKey(Admin, on_delete=models.SET_NULL, null=True, blank=True, db_column='admin_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CompanyManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['company_name']

    class Meta:
        db_table = 'company'

    def __str__(self):
        return self.company_name

class Service(models.Model):
    service_id = models.AutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='services', db_column='company_id')
    service_name = models.CharField(max_length=255)
    service_description = models.TextField()
    
    # FIXED: Add missing fields that the frontend expects
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    category = models.CharField(max_length=100, default='Other')
    duration = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'service'

    def __str__(self):
        return f"{self.service_name} - {self.company.company_name}"

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=255)
    category_description = models.TextField(blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='categories', null=True, blank=True, db_column='service_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'category'
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.category_name

class SubscriptionPlan(models.Model):
    plan_id = models.AutoField(primary_key=True)
    plan_name = models.CharField(max_length=100)
    price_egp = models.DecimalField(max_digits=10, decimal_places=2)
    search_ranking = models.CharField(max_length=200)
    plan_duration = models.DurationField(default=timedelta(days=30))
    portfolio_view = models.CharField(max_length=200)
    portfolio_upload_per_month = models.CharField(max_length=100)
    comments_view = models.CharField(max_length=200)
    commission_discount = models.CharField(max_length=200)
    business_insights = models.CharField(max_length=200)
    support_level = models.CharField(max_length=100)
    featured_on_homepage = models.BooleanField(default=False)
    priority_support = models.BooleanField(default=False)
    advanced_analytics = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='subscription_plans', db_column='admin_id')
    payment = models.ForeignKey('Payment', on_delete=models.CASCADE, related_name='subscription_plans', db_column='payment_id')

    class Meta:
        db_table = 'subscriptionplan'

    def __str__(self):
        return self.plan_name

class Advertising(models.Model):
    adv_id = models.AutoField(primary_key=True)
    image = models.CharField(max_length=500, blank=True, null=True)
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

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=200)
    content = models.TextField()
    project_type = models.CharField(max_length=100, blank=True)
    project_duration = models.DurationField(default=timedelta(days=30))
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

class CompanySubscription(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, db_column='company_id')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, db_column='plan_id')
    
    class Meta:
        db_table = 'companysubscription'
        constraints = [
            models.UniqueConstraint(fields=['company', 'plan'], name='unique_company_plan')
        ]
    
    def __str__(self):
        return f"{self.company.company_name} - {self.plan.plan_name}"