# Generated by Django 3.2.16 on 2023-01-22 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0006_auto_20230122_1600'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='amount',
            field=models.FloatField(default=0.0),
        ),
    ]