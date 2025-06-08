from rest_framework import serializers
from django.contrib.auth import authenticate
from django.db.models import Avg
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
    category_name = serializers.CharField(source='category', read_only=True)  # Simple string field
    
    class Meta:
        model = Service
        fields = [
            'service_id', 'service_name', 'service_description', 'price', 
            'category', 'category_name', 'duration', 'company_name', 'created_at'
        ]

class ServiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['service_name', 'service_description', 'price', 'category', 'duration', 'company']
    
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
        
        # Create company using the manager method
        company = Company.objects.create_user(
            email=validated_data['email'],
            password=password,
            company_name=validated_data['company_name'],
            description=validated_data.get('description', ''),
            company_address=validated_data.get('company_address', ''),
            phone_number=validated_data.get('phone_number', ''),
            city=validated_data.get('city', 'Cairo'),
            country=validated_data.get('country', 'Egypt')
        )
        
        return company

class CompanyLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            try:
                company = Company.objects.get(email__iexact=email)
                # Use username for authentication
                user = authenticate(username=company.username, password=password)
                if not user:
                    raise serializers.ValidationError('Invalid credentials')
                if not user.is_active:
                    raise serializers.ValidationError('Account is disabled')
                attrs['company'] = user
            except Company.DoesNotExist:
                raise serializers.ValidationError('Invalid credentials')
        else:
            raise serializers.ValidationError('Email and password required')
        
        return attrs

# Fixed ReviewSerializer to match actual database schema
class ReviewSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.service_name', read_only=True)
    company_name = serializers.CharField(source='service.company.company_name', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'review_id', 'rating', 'title', 'content', 'project_type',
            'project_duration', 'would_recommend', 'is_verified',
            'created_at', 'service_name', 'company_name'
        ]

class CompanyListSerializer(serializers.ModelSerializer):
    services_count = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    primary_department = serializers.SerializerMethodField()
    departments = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = [
            'company_id', 'company_name', 'description', 'city', 'country',
            'is_verified', 'services_count', 'reviews_count', 'rating',
            'primary_department', 'departments', 'created_at'
        ]
    
    def get_services_count(self, obj):
        return obj.services.count()
    
    def get_reviews_count(self, obj):
        # Get reviews through services - using correct field names
        return Review.objects.filter(service__company=obj).count()
    
    def get_rating(self, obj):
        # Get reviews through services - using correct field names
        reviews = Review.objects.filter(service__company=obj)
        if reviews.exists():
            return round(reviews.aggregate(avg=Avg('rating'))['avg'], 1)
        return 4.5  # Default rating for demo
    
    def get_primary_department(self, obj):
        # Get the most common service category as primary department
        services = obj.services.all()
        if services.exists():
            # Get the first service's category as primary
            return services.first().category
        return None
    
    def get_departments(self, obj):
        # Get all unique service categories for this company
        services = obj.services.all()
        if services.exists():
            categories = list(set([service.category for service in services if service.category]))
            return [{'name': cat, 'is_primary': i == 0} for i, cat in enumerate(categories)]
        return []

class CompanyDetailSerializer(CompanyListSerializer):
    services = ServiceSerializer(many=True, read_only=True)
    recent_reviews = serializers.SerializerMethodField()
    
    class Meta(CompanyListSerializer.Meta):
        fields = CompanyListSerializer.Meta.fields + [
            'email', 'company_address', 'phone_number', 
            'services', 'recent_reviews'
        ]
    
    def get_recent_reviews(self, obj):
        # Get recent reviews through services - limit to 3 most recent
        try:
            recent_reviews = Review.objects.filter(service__company=obj).order_by('-created_at')[:3]
            return ReviewSerializer(recent_reviews, many=True).data
        except Exception as e:
            # Return empty list if there's any error
            return []

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'plan_id', 'plan_name', 'price_egp', 'search_ranking',
            'plan_duration', 'support_level', 'created_at'
        ]
    
    @property 
    def price(self):
        return self.price_egp

class PaymentSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    plan_name = serializers.CharField(source='plan.plan_name', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'payment_id', 'amount', 'payment_method', 'status', 'transaction_id',
            'created_at', 'company_name', 'plan_name'
        ]

class CompanySubscriptionSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    plan_name = serializers.CharField(source='plan.plan_name', read_only=True)
    plan_price = serializers.DecimalField(source='plan.price_egp', read_only=True, max_digits=10, decimal_places=2)
    
    class Meta:
        model = CompanySubscription
        fields = ['company_name', 'plan_name', 'plan_price', 'is_active', 'start_date', 'end_date']

class AdvertisingSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    
    class Meta:
        model = Advertising
        fields = [
            'adv_id', 'title', 'description', 'image', 'target_audience', 
            'budget', 'start_date', 'end_date', 'company_name', 'created_at'
        ]

class StatsSerializer(serializers.Serializer):
    total_companies = serializers.IntegerField()
    verified_companies = serializers.IntegerField()
    total_services = serializers.IntegerField()
    total_categories = serializers.IntegerField()
    total_reviews = serializers.IntegerField()
    total_payments = serializers.IntegerField()
    average_rating = serializers.FloatField()