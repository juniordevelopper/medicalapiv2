from rest_framework import serializers
from .models import *

class QueueListSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='user.fullname', read_only=True)
    patient_email = serializers.EmailField(source='user.email', read_only=True)
    patient_phone = serializers.CharField(source='user.phone', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.fullname', read_only=True)
    doctor_department = serializers.CharField(source='doctor.department.name', read_only=True)
    reception_name = serializers.CharField(source='reception.user.fullname', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Queue
        fields = [
            'id', 'doctor', 'doctor_name', 'doctor_department',
            'user', 'patient_name', 'patient_email', 'patient_phone',
            'reception', 'reception_name', 'number', 'date', 
            'status', 'status_display', 'created_at'
        ]

class QueueUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Queue
        fields = ['status']