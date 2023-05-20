import uuid

from django.db import models
from django.db.models import JSONField
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.conf import settings
from django.utils.crypto import get_random_string


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False)
    brand = models.OneToOneField('Brand', on_delete=models.CASCADE, null=False, blank=False)
    address = models.CharField(max_length=100, null=True, default='', blank=True)


def qr_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'brand/qr_{0}.png'.format(str(instance.uuid))

class Brand(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True)
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    main_address = models.CharField(max_length=100)
    email = models.CharField(max_length=30)
    active = models.BooleanField(default=False)
    qr = models.ImageField(upload_to=qr_directory_path, blank=True, null=True)   

    class Meta:
        db_table = 'brand'

    def __repr__(self):
        return "{} {}".format(self.__class__.__name__, self.id)

    def save_qr_code(self):
        pass


class Category(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=45)
    brand = models.ForeignKey(Brand, models.DO_NOTHING, related_name='categories')
    icon = models.CharField(max_length=15)
    default = models.BooleanField(default=False)
    # active = models.BooleanField(default=True, null=False)
    priority = models.IntegerField(null=False, default=1)
    active = models.BooleanField(default=True)

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
    ingredients = models.JSONField(default=list, blank=True, null=True)
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
    dishes = models.ManyToManyField(Dish, through='AdditionalOrder', related_name='orders')
    order_placed_at = models.DateTimeField(blank=False, null=False)
    order_delivered_at = models.DateTimeField(blank=True, null=True)
    ws_code = models.CharField(max_length=50, unique=True)
    status = models.IntegerField(default=ORDER_PLACED, choices=ORDER_CHOICES)
    brand = models.ForeignKey(Brand, related_name='orders', on_delete=models.DO_NOTHING)
    amount = models.FloatField(default=0.0)
    order_collection_code = models.CharField(max_length=10, unique=True, null=True, blank=True)

    def set_random_ws(self):
        self.ws_code = get_random_string(length=50)

    def set_order_collection_code(self):
        self.order_collection_code = f'ES{self.id+1}'


class AdditionalOrder(models.Model):
    order = models.ForeignKey(Order, null=False, blank=False, db_column="order", on_delete=models.CASCADE, related_name="quantitats")
    dish = models.ForeignKey(Dish, null=False, blank=False, db_column="dish", on_delete=models.CASCADE, related_name="quantitats")
    quantity = models.IntegerField(null=False, blank=False, default=1)
    exclude_ingredients = models.JSONField(max_length=200, null=True, blank=True, default=list)

    class Meta:
        db_table = "additional_order"
        unique_together = ('order', 'dish')


class Register(models.Model):
    token = models.UUIDField(default=uuid.uuid4)
    email = models.EmailField()
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('token', 'email',)

# class Review(models.Model):
#     pass