from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Company, Department, CompanyDepartment

@admin.register(Company)
class CompanyAdmin(UserAdmin):
    list_display = ['company_name', 'email', 'city', 'is_verified', 'is_active', 'created_at']
    list_filter = ['is_verified', 'is_active', 'city', 'country']
    search_fields = ['company_name', 'email', 'description']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Company Information', {
            'fields': ('company_name', 'description', 'website')
        }),
        ('Contact Information', {
            'fields': ('company_address', 'phone_number', 'city', 'country')
        }),
        ('Media Files', {
            'fields': ('logo', 'portfolio', 'certifications'),
            'classes': ('collapse',)
        }),
        ('Verification', {
            'fields': ('is_verified',)
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'company_name', 'password1', 'password2'),
        }),
    )

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'is_active', 'company_count']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def company_count(self, obj):
        return obj.companydepartment_set.count()
    company_count.short_description = 'Companies'

@admin.register(CompanyDepartment)
class CompanyDepartmentAdmin(admin.ModelAdmin):
    list_display = ['company', 'department', 'is_primary']
    list_filter = ['is_primary', 'department']
    search_fields = ['company__company_name', 'department__name']

# Customize admin site
admin.site.site_header = "Flowlyne Administration"
admin.site.site_title = "Flowlyne Admin"
admin.site.index_title = "Welcome to Flowlyne Administration"