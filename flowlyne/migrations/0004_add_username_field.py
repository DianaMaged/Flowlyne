from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('flowlyne', '0003_alter_company_options_remove_category_admin_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='username',
            field=models.CharField(max_length=255, unique=True, default='temp_user'),
            preserve_default=False,
        ),
    ]