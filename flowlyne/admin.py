from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Company, Service, Category, Admin, SubscriptionPlan, Review, Payment, CompanySubscription, Advertising

@admin.register(Admin)
class AdminModelAdmin(admin.ModelAdmin):
    list_display = ['admin_id', 'email', 'created_at']
    search_fields = ['email']
    ordering = ['admin_id']
    readonly_fields = ['admin_id', 'created_at']

@admin.register(Company)
class CompanyAdmin(UserAdmin):
    list_display = ['company_id', 'company_name', 'email', 'username', 'city', 'is_verified', 'is_active', 'created_at']
    list_filter = ['is_verified', 'is_active', 'city', 'country', 'current_plan']
    search_fields = ['company_name', 'email', 'username', 'description']
    ordering = ['-created_at']
    readonly_fields = ['company_id', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Company Information', {
            'fields': ('company_name', 'description')
        }),
        ('Contact Information', {
            'fields': ('company_address', 'phone_number', 'city', 'country')
        }),
        ('Media Files', {
            'fields': ('logo', 'certification'),
            'classes': ('collapse',)
        }),
        ('Verification & Subscription', {
            'fields': ('is_verified', 'current_plan')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
            'classes': ('collapse',)
        }),
        ('Admin Relations', {
            'fields': ('admin',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('company_id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'company_name', 'password1', 'password2'),
        }),
    )

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['service_id', 'service_name', 'company', 'price', 'category', 'created_at']
    list_filter = ['category', 'created_at', 'company']
    search_fields = ['service_name', 'service_description', 'company__company_name']
    ordering = ['-created_at']
    readonly_fields = ['service_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Service Information', {
            'fields': ('service_name', 'service_description', 'price', 'category', 'duration')
        }),
        ('Relations', {
            'fields': ('company',)
        }),
        ('Timestamps', {
            'fields': ('service_id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_id', 'category_name', 'service', 'created_at']
    list_filter = ['created_at', 'service']
    search_fields = ['category_name', 'category_description']
    ordering = ['-created_at']
    readonly_fields = ['category_id', 'created_at']
    
    fieldsets = (
        ('Category Information', {
            'fields': ('category_name', 'category_description')
        }),
        ('Relations', {
            'fields': ('service',)
        }),
        ('Timestamps', {
            'fields': ('category_id', 'created_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    # Fixed to use actual database field names from your Review model
    list_display = ['review_id', 'service', 'client_name', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['client_name', 'client_email', 'review_text', 'service__service_name']
    ordering = ['-created_at']
    readonly_fields = ['review_id', 'created_at']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('client_name', 'client_email', 'review_text', 'rating')
        }),
        ('Relations', {
            'fields': ('service',)
        }),
        ('Timestamps', {
            'fields': ('review_id', 'created_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # Fixed to use actual fields from your Payment model
    list_display = ['payment_id', 'payment_method', 'is_active', 'start_date', 'end_date', 'created_at']
    list_filter = ['is_active', 'payment_method', 'created_at']
    search_fields = ['payment_method']
    ordering = ['-created_at']
    readonly_fields = ['payment_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_method', 'is_active')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date', 'last_payment_date', 'next_payment_date')
        }),
        ('Relations', {
            'fields': ('adv',)
        }),
        ('Timestamps', {
            'fields': ('payment_id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    # Fixed to use actual fields from your SubscriptionPlan model
    list_display = ['plan_id', 'plan_name', 'price', 'duration_days', 'created_at']
    list_filter = ['created_at']
    search_fields = ['plan_name', 'description']
    ordering = ['price']
    readonly_fields = ['plan_id', 'created_at']
    
    fieldsets = (
        ('Plan Information', {
            'fields': ('plan_name', 'description', 'price', 'duration_days')
        }),
        ('Features', {
            'fields': ('features',)
        }),
        ('Timestamps', {
            'fields': ('plan_id', 'created_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(CompanySubscription)
class CompanySubscriptionAdmin(admin.ModelAdmin):
    list_display = ['subscription_id', 'company', 'plan', 'is_active', 'start_date', 'end_date']
    list_filter = ['is_active', 'plan', 'start_date', 'end_date']
    search_fields = ['company__company_name', 'plan__plan_name']
    ordering = ['-start_date']
    readonly_fields = ['subscription_id', 'created_at']
    
    fieldsets = (
        ('Subscription Information', {
            'fields': ('company', 'plan', 'payment', 'is_active')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date')
        }),
        ('Timestamps', {
            'fields': ('subscription_id', 'created_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Advertising)
class AdvertisingAdmin(admin.ModelAdmin):
    # Fixed to use actual fields from your Advertising model
    list_display = ['adv_id', 'admin', 'price', 'start_date', 'end_date']
    list_filter = ['start_date', 'end_date', 'admin']
    search_fields = ['admin__email']
    ordering = ['-start_date']
    readonly_fields = ['adv_id']
    
    fieldsets = (
        ('Advertisement Information', {
            'fields': ('image', 'price')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date')
        }),
        ('Relations', {
            'fields': ('admin',)
        }),
        ('Timestamps', {
            'fields': ('adv_id',),
            'classes': ('collapse',)
        }),
    )

# Customize admin site
admin.site.site_header = "Flowlyne Administration"
admin.site.site_title = "Flowlyne Admin"
admin.site.index_title = "Welcome to Flowlyne Administration"