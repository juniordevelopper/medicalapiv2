from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from .models import *

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
        read_only_fields = ('email', 'status', 'is_active_account', 'is_deleted', 'is_blocked')

class UserListSerializer(serializers.ModelSerializer):
    hospital_name = serializers.SerializerMethodField()
    departments = serializers.SerializerMethodField()
    role = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = CustomUser
        fields = '__all__'
        # fields = ['id', 'email', 'fullname', 'phone', 'status', 'role', 'is_active', 'is_blocked', 'is_deleted', 'hospital_name', 'created_at']
    
    def get_departments(self, obj):
        if hasattr(obj, 'doctor_profile') and obj.doctor_profile.departments:
            return [{'id': d.id, 'name': d.name} for d in obj.doctor_profile.departments.all()]
        return []

    def get_hospital_name(self, obj):
        hospital = None

        # Doctor
        if hasattr(obj, 'doctor_profile') and obj.doctor_profile.hospital:
            hospital = obj.doctor_profile.hospital

        # Reception
        elif hasattr(obj, 'reception_profile') and obj.reception_profile.hospital:
            hospital = obj.reception_profile.hospital

        # Director
        elif hasattr(obj, 'managed_hospital'):
            hospital = obj.managed_hospital

        if hospital:
            return {'id': hospital.id, 'name': hospital.name}
        return None

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


class DirectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'fullname', 'email']


class DirectorCandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email']




# Profil yangilash uchun asosiy serializer
class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['fullname', 'phone', 'bio', 'profile']
        extra_kwargs = {
            'fullname': {'required': False},
            'phone': {'required': False},
            'bio': {'required': False},
            'profile': {'required': False}
        }

# Doktor uchun qo'shimcha ma'lumotlar serializeri
class DoctorProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['description', 'tajriba', 'department']
        extra_kwargs = {
            'description': {'required': False},
            'tajriba': {'required': False},
            'department': {'required': False}
        }

# Reception uchun qo'shimcha ma'lumotlar serializeri
class ReceptionProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reception
        fields = ['hospital']
        extra_kwargs = {
            'hospital': {'required': False}
        }

# To'liq profil ma'lumotlarini ko'rish uchun serializer
class ProfileDetailSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='get_status_display', read_only=True)
    doctor_details = serializers.SerializerMethodField()
    reception_details = serializers.SerializerMethodField()
    hospital_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'username', 'fullname', 'phone', 
            'bio', 'profile', 'status', 'role', 'created_at',
            'doctor_details', 'reception_details', 'hospital_name'
        ]
    
    def get_doctor_details(self, obj):
        if hasattr(obj, 'doctor_profile') and obj.doctor_profile:
            doctor = obj.doctor_profile
            return {
                'description': doctor.description,
                'tajriba': doctor.tajriba,
                'hospital': doctor.hospital.name if doctor.hospital else None,
                'department': doctor.department.name if doctor.department else None
            }
        return None
    
    def get_reception_details(self, obj):
        if hasattr(obj, 'reception_profile') and obj.reception_profile:
            reception = obj.reception_profile
            return {
                'hospital': reception.hospital.name if reception.hospital else None
            }
        return None
    
    def get_hospital_name(self, obj):
        if obj.is_director and hasattr(obj, 'managed_hospital'):
            return obj.managed_hospital.name
        return None

class DoctorListSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_fullname = serializers.CharField(source='user.fullname', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    user_status = serializers.IntegerField(source='user.status', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)
    
    class Meta:
        model = Doctor
        fields = [
            'id', 'user', 'user_email', 'user_fullname', 'user_phone', 'user_status',
            'description', 'hospital', 'hospital_name', 'department', 
            'department_name', 'tajriba', 'created_at'
        ]

class DoctorCreateUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True, required=False)
    
    class Meta:
        model = Doctor
        fields = ['user', 'email', 'description', 'hospital', 'department', 'tajriba']
        extra_kwargs = {
            'user': {'required': False}
        }
    
    def validate(self, data):
        request = self.context.get('request')
        hospital = request.user.managed_hospital if request else None
        
        # Agar user berilmagan bo'lsa, email orqali topish
        if not data.get('user') and data.get('email'):
            try:
                user = CustomUser.objects.get(email=data['email'])
                data['user'] = user
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError({"email": "Bunday email bilan foydalanuvchi topilmadi"})
        
        # User statusini tekshirish
        if data.get('user'):
            if data['user'].status != 0:  # Faqat User (0) bo'lganlar doctor bo'lishi mumkin
                raise serializers.ValidationError({"user": "Bu foydalanuvchi allaqachon boshqa rolga ega"})
        
        # Hospitalni tekshirish
        if hospital:
            data['hospital'] = hospital
        
        return data
    
    def create(self, validated_data):
        user = validated_data.get('user')
        if user:
            user.status = 2  # Doctor
            user.save()
        
        return super().create(validated_data)

# ==================== RECEPTION SERIALIZERS ====================

class ReceptionListSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_fullname = serializers.CharField(source='user.fullname', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    user_status = serializers.IntegerField(source='user.status', read_only=True)
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)
    
    class Meta:
        model = Reception
        fields = [
            'id', 'user', 'user_email', 'user_fullname', 'user_phone', 'user_status',
            'hospital', 'hospital_name', 'created_at'
        ]

class ReceptionCreateUpdateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True, required=False)
    
    class Meta:
        model = Reception
        fields = ['user', 'email', 'hospital']
        extra_kwargs = {
            'user': {'required': False},
            'hospital': {'required': False}
        }
    
    def validate(self, data):
        request = self.context.get('request')
        hospital = request.user.managed_hospital if request else None
        
        # Agar user berilmagan bo'lsa, email orqali topish
        if not data.get('user') and data.get('email'):
            try:
                user = CustomUser.objects.get(email=data['email'])
                data['user'] = user
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError({"email": "Bunday email bilan foydalanuvchi topilmadi"})
        
        # User statusini tekshirish
        if data.get('user'):
            if data['user'].status != 0:  # Faqat User (0) bo'lganlar reception bo'lishi mumkin
                raise serializers.ValidationError({"user": "Bu foydalanuvchi allaqachon boshqa rolga ega"})
        
        # Hospitalni o'rnatish
        if hospital:
            data['hospital'] = hospital
        
        return data
    
    def create(self, validated_data):
        user = validated_data.get('user')
        if user:
            user.status = 1  # Reception
            user.save()
        
        return super().create(validated_data)


# Reception serializers (Director paneli uchun)
class DirectorReceptionListSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_fullname = serializers.CharField(source='user.fullname', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    user_profile = serializers.ImageField(source='user.profile', read_only=True)
    user_status = serializers.IntegerField(source='user.status', read_only=True)
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)
    created_date = serializers.DateTimeField(source='created_at', format='%d.%m.%Y')
    
    class Meta:
        model = Reception
        fields = [
            'id', 'user', 'user_email', 'user_fullname', 'user_phone', 
            'user_profile', 'user_status', 'hospital', 'hospital_name',
            'created_at', 'created_date'
        ]

class DirectorReceptionCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    
    class Meta:
        model = Reception
        fields = ['email', 'hospital']
    
    def validate_email(self, value):
        # Email orqali userni topish
        try:
            user = CustomUser.objects.get(email=value)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Bu email bilan foydalanuvchi topilmadi")
        
        # User statusini tekshirish
        if user.status != 0:
            raise serializers.ValidationError("Bu foydalanuvchi allaqachon boshqa rolga ega")
        
        # User allaqachon reception emasligini tekshirish
        if hasattr(user, 'reception_profile'):
            raise serializers.ValidationError("Bu foydalanuvchi allaqachon reception")
        
        return value
    
    def create(self, validated_data):
        email = validated_data.pop('email')
        hospital = validated_data.pop('hospital')
        
        # Userni olish
        user = CustomUser.objects.get(email=email)
        
        # Reception yaratish
        reception = Reception.objects.create(
            user=user,
            hospital=hospital
        )
        
        # User statusini yangilash
        user.status = 1  # Reception
        user.save()
        
        return reception

class DirectorReceptionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reception
        fields = ['hospital']  # Reception faqat hospitalini o'zgartirishi mumkin


# Reception list uchun serializer
class ReceptionListSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_fullname = serializers.CharField(source='user.fullname', read_only=True)
    user_phone = serializers.CharField(source='user.phone', read_only=True)
    user_profile = serializers.ImageField(source='user.profile', read_only=True)
    user_status = serializers.IntegerField(source='user.status', read_only=True)
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)
    created_date = serializers.DateTimeField(source='created_at', format='%d.%m.%Y')
    
    class Meta:
        model = Reception
        fields = [
            'id', 'user', 'user_email', 'user_fullname', 'user_phone', 
            'user_profile', 'user_status', 'hospital', 'hospital_name',
            'created_at', 'created_date'
        ]

# Reception yaratish uchun serializer
class ReceptionCreateSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Reception
        fields = ['user_id']
    
    def validate_user_id(self, value):
        try:
            user = CustomUser.objects.get(id=value)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Foydalanuvchi topilmadi")
        
        # Status tekshirish (faqat 0 bo'lganlar)
        if user.status != 0:
            raise serializers.ValidationError("Bu foydalanuvchi allaqachon boshqa rolga ega")
        
        # Reception profili mavjud emasligini tekshirish
        if hasattr(user, 'reception_profile'):
            raise serializers.ValidationError("Bu foydalanuvchi allaqachon reception")
        
        return value
    
    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        hospital = self.context.get('hospital')  # View dan hospital keladi
        
        user = CustomUser.objects.get(id=user_id)
        
        # Reception yaratish
        reception = Reception.objects.create(
            user=user,
            hospital=hospital
        )
        
        # User statusini yangilash (0 -> 1)
        user.status = 1  # Reception
        user.save()
        
        return reception

# Reception nomzodlari uchun serializer
class ReceptionCandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'fullname', 'phone']