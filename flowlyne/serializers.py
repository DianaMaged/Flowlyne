from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Company, Department, CompanyDepartment, SubscriptionPlan, CompanySubscription, Message, CompanyReview

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'icon']

class CompanyDepartmentSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    
    class Meta:
        model = CompanyDepartment
        fields = ['department', 'is_primary']

class CompanyRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    departments = serializers.ListField(
        child=serializers.CharField(), 
        write_only=True, 
        required=False
    )
    
    class Meta:
        model = Company
        fields = [
            'company_name', 'email', 'password', 'description',
            'company_address', 'phone_number', 'website', 
            'city', 'country', 'departments'
        ]
    
    def validate_email(self, value):
        if Company.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value
    
    def create(self, validated_data):
        departments_data = validated_data.pop('departments', [])
        password = validated_data.pop('password')
        
        # Create company
        company = Company.objects.create_user(
            password=password,
            current_plan='basic',
            **validated_data
        )
        
        # Add departments
        for dept_name in departments_data:
            try:
                department = Department.objects.get(name=dept_name)
                CompanyDepartment.objects.create(
                    company=company,
                    department=department,
                    is_primary=len(departments_data) == 1
                )
            except Department.DoesNotExist:
                pass
        
        return company

class CompanyLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            company = authenticate(username=email, password=password)
            if not company:
                raise serializers.ValidationError('Invalid credentials')
            if not company.is_active:
                raise serializers.ValidationError('Account is disabled')
            attrs['company'] = company
        else:
            raise serializers.ValidationError('Email and password required')
        
        return attrs

class CompanyListSerializer(serializers.ModelSerializer):
    departments = CompanyDepartmentSerializer(many=True, read_only=True)
    primary_department = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = [
            'id', 'company_name', 'description', 'city', 'country',
            'website', 'is_verified', 'logo_url', 'departments',
            'primary_department', 'rating', 'review_count', 'created_at'
        ]
    
    def get_primary_department(self, obj):
        primary = obj.departments.filter(is_primary=True).first()
        if not primary:
            primary = obj.departments.first()
        return primary.department.name if primary else None
    
    def get_rating(self, obj):
        # Calculate average rating from reviews
        reviews = obj.received_reviews.all()
        if reviews.exists():
            return round(reviews.aggregate(avg=serializers.models.Avg('rating'))['avg'], 1)
        return 4.5  # Default rating for demo
    
    def get_review_count(self, obj):
        return obj.received_reviews.count() or 12  # Demo fallback
    
    def get_logo_url(self, obj):
        if obj.logo:
            return obj.logo.url
        return None

class CompanyDetailSerializer(CompanyListSerializer):
    portfolio_url = serializers.SerializerMethodField()
    certifications_url = serializers.SerializerMethodField()
    recent_reviews = serializers.SerializerMethodField()
    
    class Meta(CompanyListSerializer.Meta):
        fields = CompanyListSerializer.Meta.fields + [
            'email', 'company_address', 'phone_number', 
            'portfolio_url', 'certifications_url', 'recent_reviews'
        ]
    
    def get_portfolio_url(self, obj):
        return obj.portfolio.url if obj.portfolio else None
    
    def get_certifications_url(self, obj):
        return obj.certifications.url if obj.certifications else None
    
    def get_recent_reviews(self, obj):
        recent_reviews = obj.received_reviews.filter(is_verified=True)[:3]
        return CompanyReviewSerializer(recent_reviews, many=True).data

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    features_list = serializers.SerializerMethodField()
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'display_name', 'price_egp', 'price_period',
            'search_ranking', 'portfolio_view', 'portfolio_uploads_per_month',
            'comments_view', 'commission_discount', 'business_insights',
            'support_level', 'featured_on_homepage', 'priority_support',
            'advanced_analytics', 'features_list'
        ]
    
    def get_features_list(self, obj):
        """Generate a list of features for frontend display"""
        features = []
        if obj.search_ranking:
            features.append(f"🔍 {obj.search_ranking}")
        if obj.portfolio_view:
            features.append(f"📁 {obj.portfolio_view}")
        if obj.portfolio_uploads_per_month:
            features.append(f"📤 {obj.portfolio_uploads_per_month} uploads/month")
        if obj.commission_discount:
            features.append(f"💰 {obj.commission_discount}")
        if obj.business_insights:
            features.append(f"📊 {obj.business_insights}")
        if obj.support_level:
            features.append(f"🎧 {obj.support_level}")
        if obj.featured_on_homepage:
            features.append("⭐ Featured on homepage")
        return features

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.company_name', read_only=True)
    receiver_name = serializers.CharField(source='receiver.company_name', read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'receiver', 'sender_name', 'receiver_name',
            'subject', 'content', 'is_read', 'replied_to', 
            'created_at', 'read_at'
        ]
        read_only_fields = ['sender', 'created_at']

class CompanyReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewer.company_name', read_only=True)
    reviewer_logo = serializers.SerializerMethodField()
    
    class Meta:
        model = CompanyReview
        fields = [
            'id', 'reviewer', 'reviewer_name', 'reviewer_logo',
            'rating', 'title', 'content', 'project_type',
            'project_duration', 'project_budget_range',
            'would_recommend', 'is_verified', 'created_at'
        ]
        read_only_fields = ['reviewer', 'created_at']
    
    def get_reviewer_logo(self, obj):
        return obj.reviewer.logo.url if obj.reviewer.logo else None

class CompanySubscriptionSerializer(serializers.ModelSerializer):
    plan_details = SubscriptionPlanSerializer(source='plan', read_only=True)
    days_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = CompanySubscription
        fields = [
            'id', 'plan', 'plan_details', 'start_date', 'end_date',
            'is_active', 'auto_renewal', 'last_payment_date',
            'next_payment_date', 'payment_method', 'days_remaining'
        ]
    
    def get_days_remaining(self, obj):
        if not obj.end_date:
            return None
        from django.utils import timezone
        remaining = (obj.end_date - timezone.now()).days
        return max(0, remaining)

class StatsSerializer(serializers.Serializer):
    total_companies = serializers.IntegerField()
    verified_companies = serializers.IntegerField()
    total_departments = serializers.IntegerField()
    total_messages = serializers.IntegerField()
    total_reviews = serializers.IntegerField()
    average_rating = serializers.FloatField()