from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Company, Service, Category, Admin, SubscriptionPlan, Review, Payment, CompanySubscription, Advertising

@admin.register(Admin)
class AdminModelAdmin(admin.ModelAdmin):
    list_display = ['admin_id', 'email']
    search_fields = ['email']
    ordering = ['admin_id']

@admin.register(Company)
class CompanyAdmin(UserAdmin):
    list_display = ['company_id', 'company_name', 'email', 'city', 'is_verified', 'is_active', 'created_at']
    list_filter = ['is_verified', 'is_active', 'city', 'country', 'current_plan']
    search_fields = ['company_name', 'email', 'description']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
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
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'company_name', 'password1', 'password2', 'admin'),
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
    list_display = ['review_id', 'company', 'rating', 'title', 'is_verified', 'created_at']
    list_filter = ['rating', 'is_verified', 'would_recommend', 'created_at']
    search_fields = ['title', 'content', 'company__company_name']
    ordering = ['-created_at']
    readonly_fields = ['review_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('title', 'content', 'rating', 'project_type', 'project_duration')
        }),
        ('Verification', {
            'fields': ('would_recommend', 'is_verified')
        }),
        ('Relations', {
            'fields': ('company', 'service', 'admin')
        }),
        ('Timestamps', {
            'fields': ('review_id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'company', 'is_active', 'payment_method', 'created_at']
    list_filter = ['is_active', 'payment_method']
    search_fields = ['company__company_name', 'payment_method']
    ordering = ['-created_at']
    readonly_fields = ['payment_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('start_date', 'end_date', 'is_active', 'payment_method')
        }),
        ('Payment History', {
            'fields': ('last_payment_date', 'next_payment_date'),
            'classes': ('collapse',)
        }),
        ('Relations', {
            'fields': ('company', 'adv')
        }),
        ('Timestamps', {
            'fields': ('payment_id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['plan_id', 'plan_name', 'price_egp', 'is_active', 'created_at']
    list_filter = ['is_active', 'featured_on_homepage', 'priority_support', 'advanced_analytics']
    search_fields = ['plan_name', 'search_ranking']
    ordering = ['price_egp']
    readonly_fields = ['plan_id', 'created_at']
    
    fieldsets = (
        ('Plan Information', {
            'fields': ('plan_name', 'price_egp', 'plan_duration')
        }),
        ('Features', {
            'fields': (
                'search_ranking', 'portfolio_view', 'portfolio_upload_per_month',
                'comments_view', 'commission_discount', 'business_insights', 'support_level'
            )
        }),
        ('Premium Features', {
            'fields': ('featured_on_homepage', 'priority_support', 'advanced_analytics'),
            'classes': ('collapse',)
        }),
        ('Relations', {
            'fields': ('admin', 'payment')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('plan_id', 'created_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(CompanySubscription)
class CompanySubscriptionAdmin(admin.ModelAdmin):
    list_display = ['company', 'plan']
    list_filter = ['plan']
    search_fields = ['company__company_name', 'plan__plan_name']

@admin.register(Advertising)
class AdvertisingAdmin(admin.ModelAdmin):
    list_display = ['adv_id', 'price', 'start_date', 'end_date', 'admin']
    list_filter = ['admin', 'start_date', 'end_date']
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
        ('ID', {
            'fields': ('adv_id',),
            'classes': ('collapse',)
        }),
    )

# Customize admin site
admin.site.site_header = "Flowlyne Administration"
admin.site.site_title = "Flowlyne Admin"
admin.site.index_title = "Welcome to Flowlyne Administration"