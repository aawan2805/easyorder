# Generated by Django 3.2.19 on 2023-05-23 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0004_alter_additionalorder_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='dish',
            name='deleted',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]