# Generated by Django 3.2.19 on 2023-07-02 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('panel', '0008_alter_dish_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='email',
            field=models.CharField(max_length=300),
        ),
        migrations.AlterField(
            model_name='brand',
            name='main_address',
            field=models.CharField(max_length=300),
        ),
        migrations.AlterField(
            model_name='brand',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='brand',
            name='phone_number',
            field=models.CharField(max_length=9),
        ),
        migrations.AlterField(
            model_name='category',
            name='icon',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='dish',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='order',
            name='ws_code',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='profile',
            name='address',
            field=models.CharField(blank=True, default='', max_length=300, null=True),
        ),
    ]
