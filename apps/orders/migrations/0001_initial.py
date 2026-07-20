from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CarProblemImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='problem_images/')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('problem_description', models.TextField()),
                ('customer_latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('customer_longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('customer_address', models.TextField(blank=True)),
                ('need_master_visit', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('ACCEPTED', 'Accepted'), ('ON_THE_WAY', 'On the way'), ('IN_PROGRESS', 'In progress'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled'), ('REJECTED', 'Rejected')], default='PENDING', max_length=30)),
                ('offered_price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('final_price', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
