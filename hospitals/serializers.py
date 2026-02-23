from rest_framework import serializers
from .models import Department, Hospital, HospitalImage
from locations.serializers import LocationNameSerializer
from accounts.models import Director, CustomUser
from accounts.serializers import DirectorShortSerializer

# -------------------------------------------------------------------------
# DepartmentSerializer
# -------------------------------------------------------------------------
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']

class DepartmentNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']


# -------------------------------------------------------------------------
                            # HospitalImageSerializer
# -------------------------------------------------------------------------
class HospitalImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalImage
        fields = ['id', 'image']

# -------------------------------------------------------------------------
                            # HospitalSerializer
# -------------------------------------------------------------------------
class HospitalSerializer(serializers.ModelSerializer):
    director = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(status=0),
        write_only=True,
        required=False,
        allow_null=True
    )
    location_detail = LocationNameSerializer(source='location', read_only=True)
    departments_detail = DepartmentNameSerializer(source='departments', many=True, read_only=True)
    director_detail = DirectorShortSerializer(source='director', read_only=True)
    images_detail = HospitalImageSerializer(source='images', many=True, read_only=True)

    class Meta:
        model = Hospital
        fields = [
            'id', 'name', 'address', 'director', 'director_detail', 
            'location', 'location_detail', 'departments', 'images_detail', 
            'departments_detail', 'description', 'created_at', 'updated_at'
        ]

    def validate_director(self, user_obj):
        if user_obj:
            if user_obj.status in [0, 3]:
                if user_obj.status != 3:
                    user_obj.status = 3
                    user_obj.save()
                director_profile, created = Director.objects.get_or_create(user=user_obj)
                return director_profile
            raise serializers.ValidationError("Faqat foydalanuvchi Direktor qilib tayinlanishi mumkin.")
        return user_obj

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.director:
            representation['director'] = instance.director.user.id
        return representation
