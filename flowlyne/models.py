from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from datetime import timedelta


class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admin'

    def __str__(self):
        return self.email


class CompanyManager(BaseUserManager):
    def create_user(self, email, company_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        # Use email as username for simplicity
        user = self.model(
            email=email, 
            username=email,  # Set username to email
            company_name=company_name, 
            **extra_fields
        )
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
    username = models.CharField(max_length=255, unique=True)  # Username field
    company_address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    logo = models.CharField(max_length=500, blank=True, null=True)
    certification = models.CharField(max_length=500, blank=True, null=True)
    city = models.CharField(max_length=100, default='Cairo')
    country = models.CharField(max_length=100, default='Egypt')
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)  # Keep this one - it's required for Django auth
    is_staff = models.BooleanField(default=False)
    current_plan = models.CharField(max_length=50, default='basic')
    admin = models.ForeignKey(Admin, on_delete=models.SET_NULL, null=True, blank=True, db_column='admin_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CompanyManager()

    USERNAME_FIELD = 'username'  # Use username as the login field
    REQUIRED_FIELDS = ['email', 'company_name']  # Required when creating superuser

    class Meta:
        db_table = 'company'

    def __str__(self):
        return self.company_name

    def save(self, *args, **kwargs):
        # Automatically set username to email if not provided
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)


class Service(models.Model):
    service_id = models.AutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='services', db_column='company_id')
    service_name = models.CharField(max_length=255)
    service_description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    category = models.CharField(max_length=100, default='Other')
    duration = models.CharField(max_length=100, blank=True, null=True)
    # Removed is_active field - not in your database
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
    # Removed is_active field - not in your database
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
    support_level = models.CharField(max_length=100)
    # Removed is_active field - not in your database
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'subscription_plan'

    def __str__(self):
        return self.plan_name

    @property
    def price(self):
        return self.price_egp


class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reviews', db_column='service_id')
    reviewer_name = models.CharField(max_length=255)
    reviewer_email = models.EmailField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'review'

    def __str__(self):
        return f"Review for {self.service.service_name} by {self.reviewer_name}"


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='payments', db_column='company_id')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='payments', db_column='plan_id')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='pending')
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment'

    def __str__(self):
        return f"Payment {self.payment_id} - {self.company.company_name}"


class CompanySubscription(models.Model):
    subscription_id = models.AutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='subscriptions', db_column='company_id')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='subscriptions', db_column='plan_id')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)  # Keep this if it exists in your DB
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'company_subscription'

    def __str__(self):
        return f"{self.company.company_name} - {self.plan.plan_name}"


class Advertising(models.Model):
    adv_id = models.AutoField(primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='advertisements', db_column='company_id')
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.CharField(max_length=500, blank=True, null=True)
    target_audience = models.CharField(max_length=255)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    # Removed is_active field - not in your database
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'advertising'

    def __str__(self):
        return f"{self.title} - {self.company.company_name}"