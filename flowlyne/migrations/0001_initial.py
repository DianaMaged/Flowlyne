# flowlyne/migrations/0001_initial.py

from django.db import migrations, models
import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from datetime import timedelta


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('admin_id', models.AutoField(primary_key=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('password', models.CharField(max_length=128)),
            ],
            options={
                'db_table': 'admin',
            },
        ),
        migrations.CreateModel(
            name='Company',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('company_id', models.AutoField(primary_key=True)),
                ('company_name', models.CharField(max_length=250)),
                ('company_address', models.CharField(blank=True, max_length=250)),
                ('phone_number', models.CharField(blank=True, max_length=20)),
                ('description', models.TextField(blank=True)),
                ('logo', models.CharField(blank=True, max_length=255)),
                ('certification', models.CharField(blank=True, max_length=255)),
                ('is_verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('current_plan', models.CharField(default='basic', max_length=20)),
                ('city', models.CharField(default='Cairo', max_length=100)),
                ('country', models.CharField(default='Egypt', max_length=100)),
                ('admin', models.ForeignKey(db_column='admin_id', on_delete=django.db.models.deletion.CASCADE, related_name='companies', to='flowlyne.admin')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Company',
                'verbose_name_plural': 'Companies',
                'db_table': 'company',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Advertising',
            fields=[
                ('adv_id', models.AutoField(primary_key=True)),
                ('image', models.CharField(max_length=255)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('admin', models.ForeignKey(db_column='admin_id', on_delete=django.db.models.deletion.CASCADE, related_name='advertisements', to='flowlyne.admin')),
            ],
            options={
                'db_table': 'advertising',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('payment_id', models.AutoField(primary_key=True)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('last_payment_date', models.DateTimeField(blank=True, null=True)),
                ('next_payment_date', models.DateTimeField(blank=True, null=True)),
                ('payment_method', models.CharField(blank=True, max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('adv', models.ForeignKey(blank=True, db_column='adv_id', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='flowlyne.advertising')),
                ('company', models.ForeignKey(db_column='company_id', on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='flowlyne.company')),
            ],
            options={
                'db_table': 'payment',
            },
        ),
        migrations.CreateModel(
            name='SubscriptionPlan',
            fields=[
                ('plan_id', models.AutoField(primary_key=True)),
                ('plan_name', models.CharField(max_length=100)),
                ('price_egp', models.DecimalField(decimal_places=2, max_digits=10)),
                ('search_ranking', models.CharField(max_length=200)),
                ('plan_duration', models.DurationField(default=timedelta(days=30))),
                ('portfolio_view', models.CharField(max_length=200)),
                ('portfolio_upload_per_month', models.CharField(max_length=100)),
                ('comments_view', models.CharField(max_length=200)),
                ('commission_discount', models.CharField(max_length=200)),
                ('business_insights', models.CharField(max_length=200)),
                ('support_level', models.CharField(max_length=200)),
                ('featured_on_homepage', models.BooleanField(default=False)),
                ('priority_support', models.BooleanField(default=False)),
                ('advanced_analytics', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('admin', models.ForeignKey(db_column='admin_id', on_delete=django.db.models.deletion.CASCADE, related_name='subscription_plans', to='flowlyne.admin')),
                ('payment', models.ForeignKey(db_column='payment_id', on_delete=django.db.models.deletion.CASCADE, related_name='subscription_plans', to='flowlyne.payment')),
            ],
            options={
                'db_table': 'subscriptionplan',
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('service_id', models.AutoField(primary_key=True)),
                ('service_name', models.CharField(max_length=200)),
                ('service_description', models.TextField()),
                ('admin', models.ForeignKey(db_column='admin_id', on_delete=django.db.models.deletion.CASCADE, related_name='services', to='flowlyne.admin')),
                ('company', models.ForeignKey(db_column='company_id', on_delete=django.db.models.deletion.CASCADE, related_name='services', to='flowlyne.company')),
            ],
            options={
                'db_table': 'service',
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('review_id', models.AutoField(primary_key=True)),
                ('rating', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('project_type', models.CharField(blank=True, max_length=100)),
                ('project_duration', models.DurationField(default=timedelta(days=30))),
                ('would_recommend', models.BooleanField(default=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('admin', models.ForeignKey(db_column='admin_id', on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='flowlyne.admin')),
                ('company', models.ForeignKey(db_column='company_id', on_delete=django.db.models.deletion.CASCADE, related_name='received_reviews', to='flowlyne.company')),
                ('service', models.ForeignKey(db_column='service_id', on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='flowlyne.service')),
            ],
            options={
                'db_table': 'review',
            },
        ),
        migrations.CreateModel(
            name='CompanySubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.ForeignKey(db_column='company_id', on_delete=django.db.models.deletion.CASCADE, to='flowlyne.company')),
                ('plan', models.ForeignKey(db_column='plan_id', on_delete=django.db.models.deletion.CASCADE, to='flowlyne.subscriptionplan')),
            ],
            options={
                'db_table': 'companysubscription',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('category_id', models.AutoField(primary_key=True)),
                ('category_name', models.CharField(max_length=100)),
                ('category_description', models.TextField(blank=True)),
                ('admin', models.ForeignKey(db_column='admin_id', on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='flowlyne.admin')),
                ('service', models.ForeignKey(db_column='service_id', on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='flowlyne.service')),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'db_table': 'category',
            },
        ),
        migrations.AddConstraint(
            model_name='companysubscription',
            constraint=models.UniqueConstraint(fields=('company', 'plan'), name='unique_company_plan'),
        ),
    ]