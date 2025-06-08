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
    # Removed 'is_active' from list_display and list_filter
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
    # Removed 'is_active' from list_display and list_filter
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
    list_display = ['review_id', 'service', 'reviewer_name', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['reviewer_name', 'reviewer_email', 'review_text', 'service__service_name']
    ordering = ['-created_at']
    readonly_fields = ['review_id', 'created_at']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('reviewer_name', 'reviewer_email', 'rating', 'review_text')
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
    list_display = ['payment_id', 'company', 'plan', 'amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['company__company_name', 'plan__plan_name', 'transaction_id']
    ordering = ['-created_at']
    readonly_fields = ['payment_id', 'created_at']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('amount', 'payment_method', 'status', 'transaction_id')
        }),
        ('Relations', {
            'fields': ('company', 'plan')
        }),
        ('Timestamps', {
            'fields': ('payment_id', 'created_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    # Removed 'is_active' from list_display and list_filter
    list_display = ['plan_id', 'plan_name', 'price_egp', 'created_at']
    list_filter = ['created_at']
    search_fields = ['plan_name', 'search_ranking', 'support_level']
    ordering = ['price_egp']
    readonly_fields = ['plan_id', 'created_at']
    
    fieldsets = (
        ('Plan Information', {
            'fields': ('plan_name', 'price_egp', 'plan_duration')
        }),
        ('Features', {
            'fields': ('search_ranking', 'support_level')
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
            'fields': ('company', 'plan', 'is_active')
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
    # Removed 'is_active' from list_display and list_filter
    list_display = ['adv_id', 'company', 'title', 'budget', 'start_date', 'end_date']
    list_filter = ['start_date', 'end_date']
    search_fields = ['title', 'description', 'company__company_name']
    ordering = ['-start_date']
    readonly_fields = ['adv_id', 'created_at']
    
    fieldsets = (
        ('Advertisement Information', {
            'fields': ('title', 'description', 'image', 'target_audience', 'budget')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date')
        }),
        ('Relations', {
            'fields': ('company',)
        }),
        ('Timestamps', {
            'fields': ('adv_id', 'created_at'),
            'classes': ('collapse',)
        }),
    )

# Customize admin site
admin.site.site_header = "Flowlyne Administration"
admin.site.site_title = "Flowlyne Admin"
admin.site.index_title = "Welcome to Flowlyne Administration"