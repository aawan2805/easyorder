# Generated by Django 3.2.19 on 2023-05-23 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0005_dish_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='deleted',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]