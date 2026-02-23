from rest_framework import serializers
from .models import Location

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class LocationNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'name']