# Generated by Django 2.0.3 on 2018-04-04 10:38

from django.db import migrations, models
import products.models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_auto_20180404_1509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(null=True, upload_to=products.models.upload_image_path),
        ),
    ]
