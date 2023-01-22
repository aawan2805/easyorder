from django.db import models
from django.db.models import JSONField
import uuid
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.conf import settings

# class User(AbstractUser): # It is called panel_user in the database.
#     address = models.CharField(max_length=100, null=True, default='', blank=True)
#     brand = models.OneToOneField('Brand', on_delete=models.CASCADE, null=True, blank=True)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False)
    brand = models.OneToOneField('Brand', on_delete=models.CASCADE, null=False, blank=False)
    address = models.CharField(max_length=100, null=True, default='', blank=True)


class Brand(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    main_address = models.CharField(max_length=100)
    email = models.CharField(max_length=30)

    class Meta:
        db_table = 'brand'

    def __repr__(self):
        return "{} {}".format(self.__class__.__name__, self.id)


class Category(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=45)
    brand = models.ForeignKey(Brand, models.DO_NOTHING, related_name='categories')
    icon = models.CharField(max_length=15)
    default = models.BooleanField(default=False)
    # active = models.BooleanField(default=True, null=False)
    priority = models.IntegerField(null=False, default=1)

    class Meta:
        db_table = 'category'

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


def dishes_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'dishes/{0}/{1}.png'.format(str(instance.brand.uuid), str(instance.uuid))

# Create your models here.
class Dish(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=150)
    price = models.FloatField()
    category = models.ForeignKey(Category, models.DO_NOTHING, related_name='dishes')
    ingredients = models.CharField(max_length=100, default="", blank=True)
    brand = models.ForeignKey(Brand, models.DO_NOTHING, related_name='dishes')
    photo = models.ImageField(upload_to=dishes_directory_path, blank=True, null=True)
    tags = models.CharField(max_length=100, default="", blank=True) # Para advertencias (alergicos, etc...)
    active = models.BooleanField(default=True, blank=False, null=False)

    class Meta:
        db_table = 'dish'
        ordering = ['name']

    def __repr__(self):
        return "{} - {}".format(self.__class__.__name__, self.uuid)

    def get_photo(self):
        if self.photo:
            return self.photo.url
        else:
            return settings.STATIC_URL + 'img/default/meal.png'


ORDER_PLACED = 0
ORDER_ACCEPTED = 1
ORDER_PREPARING = 2
ORDER_PREPARED = 3
ORDER_DELIVERED = 4
ORDER_CHOICES = (
    (ORDER_PLACED, 0),
    (ORDER_ACCEPTED, 1),
    (ORDER_PREPARING, 2),
    (ORDER_PREPARED, 3),
    (ORDER_DELIVERED, 4),
)
class Order(models.Model):
    dishes = models.ManyToManyField(Dish, related_name='dishes')
    order_placed_at = models.DateTimeField(blank=False, null=False)
    order_delivered_at = models.DateTimeField(blank=True, null=True)
    ws_code = models.CharField(max_length=50) #unique=True)
    status = models.IntegerField(default=ORDER_PLACED, choices=ORDER_CHOICES)
    brand = models.ForeignKey(Brand, related_name='orders', on_delete=models.DO_NOTHING)
    amount = models.FloatField(default=0.0)

# class Review(models.Model):
#     pass