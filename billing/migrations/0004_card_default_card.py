# Generated by Django 2.0.3 on 2018-04-17 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0003_card'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='default_card',
            field=models.BooleanField(default=True),
        ),
    ]
