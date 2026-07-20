from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MasterProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255)),
                ('experience_years', models.PositiveIntegerField(default=0)),
                ('bio', models.TextField(blank=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('can_visit_customer', models.BooleanField(default=False)),
                ('average_rating', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ('total_reviews', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Workshop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('region', models.CharField(max_length=100)),
                ('district', models.CharField(max_length=100)),
                ('address', models.TextField()),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('open_time', models.TimeField(blank=True, null=True)),
                ('close_time', models.TimeField(blank=True, null=True)),
            ],
        ),
    ]
