from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from .models import CustomUser, Director, Doctor, Reception

class UserDetailSerializer(serializers.ModelSerializer):
    is_patient = serializers.BooleanField(read_only=True)
    is_reception = serializers.BooleanField(read_only=True)
    is_doctor = serializers.BooleanField(read_only=True)
    is_director = serializers.BooleanField(read_only=True)
    is_admin_user = serializers.BooleanField(read_only=True)
    check_active = serializers.BooleanField(read_only=True)
    check_blocked = serializers.BooleanField(read_only=True)
    hospital_name = serializers.CharField(source='director_profile.managed_hospital.name', read_only=True)
    assigned_at = serializers.DateTimeField(source='director_profile.created_at', read_only=True)

    class Meta:
        model = CustomUser
        fields = ('__all__')
        # fields = (
        #     'id', 'email', 'username', 'fullname', 'status', 'phone', 
        #     'bio', 'profile', 'is_active_account', 'is_deleted', 'is_blocked',
        #     'is_patient', 'is_reception', 'is_doctor', 'is_director', 
        #     'is_admin_user', 'check_active', 'check_blocked',
        #     'hospital_name', 'assigned_at', 'created_at', 'updated_at', 'last_login'
        # )
        read_only_fields = ('email', 'status', 'is_active_account', 'is_deleted', 'is_blocked')

class CustomRegisterSerializer(RegisterSerializer):
    fullname = serializers.CharField(max_length=255, required=True)
    phone = serializers.CharField(max_length=20, required=True)

    def get_cleaned_data(self):
        # Bu metod dj-rest-auth uchun ma'lumotlarni tozalab beradi
        data = super().get_cleaned_data()
        data['fullname'] = self.validated_data.get('fullname', '')
        data['phone'] = self.validated_data.get('phone', '')
        return data

    def save(self, request):
        # dj-rest-auth save metodi requestni qabul qiladi
        user = super().save(request)
        user.fullname = self.cleaned_data.get('fullname')
        user.phone = self.cleaned_data.get('phone')
        user.is_active_account = False
        user.status = 0 # Default bemor roli
        user.save()
        return user

class DirectorShortSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(source='user.fullname', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Director
        fields = ['id', 'fullname', 'email']


class DirectorCandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email']