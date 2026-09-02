# Generated manually to preserve existing Category and FoodItem data.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('image', models.ImageField(blank=True, null=True, upload_to='menu_images/')),
                ('category', models.CharField(max_length=50)),
                ('is_available', models.BooleanField(default=True)),
            ],
        ),
    ]
