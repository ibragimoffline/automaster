import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('masters', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='MasterService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('price_from', models.DecimalField(decimal_places=2, max_digits=12)),
                ('price_to', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('description', models.TextField(blank=True)),
                ('master', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='masters.masterprofile')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='master_services', to='services.servicecategory')),
            ],
        ),
    ]
