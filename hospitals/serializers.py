from rest_framework import serializers
from .models import Department, Hospital, HospitalImage
from locations.serializers import LocationNameSerializer
from accounts.serializers import DirectorSerializer
from accounts.models import CustomUser

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
    director_detail = DirectorSerializer(source='director', read_only=True)
    location_detail = LocationNameSerializer(source='location', read_only=True)
    departments_detail = DepartmentNameSerializer(source='departments', many=True, read_only=True)
    images_detail = HospitalImageSerializer(source='images', many=True, read_only=True)

    class Meta:
        model = Hospital
        # fields = [
        #     'id', 'name', 'address', 'director', 'director_detail',
        #     'location', 'location_detail', 'departments', 'images_detail', 
        #     'departments_detail', 'description', 'created_at', 'updated_at'
        # ]
        fields = '__all__'
    

    def create(self, validated_data):
        director = validated_data.pop('director', None)
        hospital = super().create(validated_data)
        
        if director:
            # Directorni shifoxonaga tayinlash
            hospital.director = director
            hospital.save()
            
            # Director statusini yangilash
            director.status = 3
            director.save()
        return hospital

    def update(self, instance, validated_data):
        new_director = validated_data.pop('director', None)
        old_director = instance.director

        instance = super().update(instance, validated_data)

        # Director o‘zgargan bo‘lsa
        if new_director and new_director != old_director:
            instance.director = new_director
            instance.save()

            # Yangi direktor statusini 3 qilamiz
            new_director.status = 3
            new_director.save()

            # Eski direktor bo‘lsa, statusini 0 qilamiz
            if old_director:
                old_director.status = 0
                old_director.save()
        return instance