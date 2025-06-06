from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Company, Service, Category, Admin, SubscriptionPlan, Review, Payment, CompanySubscription, Advertising

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['admin_id', 'email']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_id', 'category_name', 'category_description']

class ServiceSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Service
        fields = [
            'service_id', 'service_name', 'service_description',
            'company_name', 'categories'
        ]

class ServiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['service_name', 'service_description']
    
    def validate_service_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Service name cannot be empty")
        return value.strip()
    
    def validate_service_description(self, value):
        if not value.strip():
            raise serializers.ValidationError("Service description cannot be empty")
        return value.strip()

class CompanyRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = Company
        fields = [
            'company_name', 'email', 'password', 'description',
            'company_address', 'phone_number', 'city', 'country'
        ]
    
    def validate_email(self, value):
        if Company.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        
        # Get or create default admin
        admin, created = Admin.objects.get_or_create(
            email='admin@flowlyne.com',
            defaults={'password': 'admin123'}
        )
        
        # Create company
        company = Company.objects.create_user(
            password=password,
            current_plan='basic',
            admin=admin,
            **validated_data
        )
        
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
    services_count = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = [
            'company_id', 'company_name', 'description', 'city', 'country',
            'is_verified', 'logo', 'services_count', 'reviews_count', 'rating',
            'created_at'
        ]
    
    def get_services_count(self, obj):
        return obj.services.count()
    
    def get_reviews_count(self, obj):
        return obj.received_reviews.count()
    
    def get_rating(self, obj):
        reviews = obj.received_reviews.all()
        if reviews.exists():
            return round(reviews.aggregate(avg=serializers.models.Avg('rating'))['avg'], 1)
        return 4.5  # Default rating for demo

class CompanyDetailSerializer(CompanyListSerializer):
    services = ServiceSerializer(many=True, read_only=True)
    recent_reviews = serializers.SerializerMethodField()
    
    class Meta(CompanyListSerializer.Meta):
        fields = CompanyListSerializer.Meta.fields + [
            'email', 'company_address', 'phone_number', 
            'certification', 'services', 'recent_reviews'
        ]
    
    def get_recent_reviews(self, obj):
        recent_reviews = obj.received_reviews.filter(is_verified=True)[:3]
        return ReviewSerializer(recent_reviews, many=True).data

class ReviewSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    service_name = serializers.CharField(source='service.service_name', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'review_id', 'rating', 'title', 'content', 'project_type',
            'project_duration', 'would_recommend', 'is_verified',
            'created_at', 'company_name', 'service_name'
        ]

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    features_list = serializers.SerializerMethodField()
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'plan_id', 'plan_name', 'price_egp', 'search_ranking',
            'plan_duration', 'portfolio_view', 'portfolio_upload_per_month',
            'comments_view', 'commission_discount', 'business_insights',
            'support_level', 'featured_on_homepage', 'priority_support',
            'advanced_analytics', 'features_list'
        ]
    
    def get_features_list(self, obj):
        features = []
        if obj.search_ranking:
            features.append(f"🔍 {obj.search_ranking}")
        if obj.portfolio_view:
            features.append(f"📁 {obj.portfolio_view}")
        if obj.portfolio_upload_per_month:
            features.append(f"📤 {obj.portfolio_upload_per_month}")
        if obj.commission_discount:
            features.append(f"💰 {obj.commission_discount}")
        if obj.business_insights:
            features.append(f"📊 {obj.business_insights}")
        if obj.support_level:
            features.append(f"🎧 {obj.support_level}")
        if obj.featured_on_homepage:
            features.append("⭐ Featured on homepage")
        return features

class PaymentSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'payment_id', 'start_date', 'end_date', 'is_active',
            'last_payment_date', 'next_payment_date', 'payment_method',
            'created_at', 'updated_at', 'company_name'
        ]

class CompanySubscriptionSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    plan_name = serializers.CharField(source='plan.plan_name', read_only=True)
    plan_price = serializers.DecimalField(source='plan.price_egp', read_only=True, max_digits=10, decimal_places=2)
    
    class Meta:
        model = CompanySubscription
        fields = ['company_name', 'plan_name', 'plan_price']

class AdvertisingSerializer(serializers.ModelSerializer):
    admin_email = serializers.CharField(source='admin.email', read_only=True)
    
    class Meta:
        model = Advertising
        fields = [
            'adv_id', 'image', 'price', 'start_date', 'end_date', 'admin_email'
        ]

class StatsSerializer(serializers.Serializer):
    total_companies = serializers.IntegerField()
    verified_companies = serializers.IntegerField()
    total_services = serializers.IntegerField()
    total_categories = serializers.IntegerField()
    total_reviews = serializers.IntegerField()
    total_payments = serializers.IntegerField()
    average_rating = serializers.FloatField()