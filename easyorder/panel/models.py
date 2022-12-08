from django.db import models
from django.db.models import JSONField
import uuid


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
    return 'dishes/{0}/{1}.png'.format(str(instance.branch.uuid), str(instance.uuid))

# Create your models here.
class Dish(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=150)
    price = models.FloatField()
    category = models.ForeignKey(Category, models.DO_NOTHING, related_name='dishes')
    ingredients = JSONField(default=list, blank=True)
    brand = models.ForeignKey(Brand, models.DO_NOTHING, related_name='dishes')
    photo = models.ImageField(upload_to=dishes_directory_path, blank=True, null=True)
    tags = JSONField(default=list, blank=True) # Para advertencias (alergicos, etc...)
    active = models.BooleanField(default=True, blank=False, null=False)

    class Meta:
        db_table = 'dish'
        ordering = ['name']

    def __str__(self):
        return self.name

    def __repr__(self):
        return "{} - {}".format(self.__class__.__name__, self.uuid)

