# Generated by Django 2.0.3 on 2018-04-04 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_product_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.FileField(null=True, upload_to='products/'),
        ),
    ]
