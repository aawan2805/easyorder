from panel.models import *
from rest_framework import serializers


class PlatosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = '__all__'
