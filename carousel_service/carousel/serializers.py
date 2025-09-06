from rest_framework import serializers
from .models import FeaturedEvent

class FeaturedEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeaturedEvent
        fields = '__all__'

