# Generated by Django 3.2.18 on 2023-04-02 16:57

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0010_category_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Register',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField(default=uuid.uuid4)),
                ('email', models.EmailField(max_length=254)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'unique_together': {('token', 'email')},
            },
        ),
    ]
