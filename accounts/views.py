from rest_framework import viewsets, status, views, filters, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q
import random
import string
import uuid
from rest_framework.views import APIView
from datetime import date
from rest_framework.parsers import MultiPartParser, FormParser

from .serializers import *
from appointments.serializers import *
from .permissions import *
from hospitals.models import *
from rest_framework.decorators import action

User = get_user_model()

# -------------------------------------------------------------------------
# Admin uchun Foydalanuvchilarni Boshqarish (CRUD + Filter)
# -------------------------------------------------------------------------
class UserManagementViewSet(viewsets.ModelViewSet):
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    filterset_fields = ['status', 'is_blocked', 'is_deleted', 'is_active']
    search_fields = ['fullname', 'email', 'phone']

    def get_queryset(self):
        queryset = User.objects.all().select_related(
            'doctor_profile__hospital',
            'reception_profile__hospital',
            'managed_hospital'
        ).order_by('-created_at')
        hospital_id = self.request.query_params.get('hospital')
        if hospital_id:
            queryset = queryset.filter(
                Q(doctor_profile__hospital_id=hospital_id) |
                Q(reception_profile__hospital_id=hospital_id) |
                Q(managed_hospital__id=hospital_id)
            )
        return queryset


# -------------------------------------------------------------------------
# Parolni tiklash va Email tasdiqlash (O'z holicha qoldi)
# -------------------------------------------------------------------------
class PasswordRecoveryView(views.APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            otp = ''.join(random.choices(string.digits, k=6))
            user.otp_code = otp
            user.save()
            send_mail('Tasdiqlash kodi', f'Kod: {otp}', settings.DEFAULT_FROM_EMAIL, [user.email])
            return Response({"detail": "Kod yuborildi."}, status=status.HTTP_200_OK)
        return Response({"error": "Topilmadi."}, status=status.HTTP_404_NOT_FOUND)

class PasswordResetConfirmView(views.APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email'); otp = request.data.get('otp'); new_pass = request.data.get('new_password')
        user = User.objects.filter(email=email, otp_code=otp).first()
        if user:
            user.set_password(new_pass); user.otp_code = None; user.save()
            return Response({"detail": "Parol yangilandi."}, status=status.HTTP_200_OK)
        return Response({"error": "Xato."}, status=status.HTTP_400_BAD_REQUEST)

class UsernameRecoveryView(views.APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        return Response({"username": user.username} if user else {"error": "Topilmadi"}, 
                        status=status.HTTP_200_OK if user else status.HTTP_404_NOT_FOUND)

class ResendVerificationView(views.APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if not user: return Response({"error": "Topilmadi"}, status=404)
        if user.is_active_account: return Response({"detail": "Faol"}, status=400)
        
        token = str(uuid.uuid4())
        user.verification_token = token; user.save()
        send_mail('Tasdiqlash', f'Token: {token}', settings.DEFAULT_FROM_EMAIL, [user.email])
        return Response({"detail": "Yuborildi."}, status=200)
        
class AllUserListView(views.APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # Faqat kerakli ma'lumotlarni yuboramiz (Email va Ism)
        users = User.objects.filter(is_deleted=False).values('id', 'email', 'fullname')
        return Response(users, status=status.HTTP_200_OK)

class DirectorCandidateListView(generics.ListAPIView):
    serializer_class = DirectorCandidateSerializer
    permission_classes = [IsAdminUser]
    def get_queryset(self):
        return User.objects.filter(status=0, is_active=True, is_deleted=False).order_by('email')



class DashboardStatsAPIView(APIView):

    def get(self, request):
        today = date.today()

        data = {
            "total_users": User.objects.count(),
            "total_doctors": User.objects.filter(status=2).count(),
            "total_receptions": User.objects.filter(status=1).count(),
            "total_directors": User.objects.filter(status=3).count(),
            "total_admins": User.objects.filter(status=4).count(),
            "total_hospitals": Hospital.objects.count(),
            "total_departments": Department.objects.count(),
            "today_registered": User.objects.filter(date_joined__date=today).count(),
        }

        return Response(data)




# Faqat o'z profilini ko'rish uchun
class MyProfileDetailView(generics.RetrieveAPIView):
    serializer_class = ProfileDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user

# Asosiy profil ma'lumotlarini yangilash (fullname, phone, bio, profile)
class MyProfileUpdateView(generics.UpdateAPIView):
    serializer_class = ProfileUpdateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Rolga qarab qo'shimcha ma'lumotlarni yangilash
        user = instance
        role_update_response = None
        
        if user.is_doctor and hasattr(user, 'doctor_profile'):
            doctor_serializer = DoctorProfileUpdateSerializer(
                user.doctor_profile, 
                data=request.data, 
                partial=True
            )
            if doctor_serializer.is_valid():
                doctor_serializer.save()
                role_update_response = doctor_serializer.data
        
        elif user.is_reception and hasattr(user, 'reception_profile'):
            reception_serializer = ReceptionProfileUpdateSerializer(
                user.reception_profile, 
                data=request.data, 
                partial=True
            )
            if reception_serializer.is_valid():
                reception_serializer.save()
                role_update_response = reception_serializer.data
        
        # Javob qaytarish
        response_data = {
            'user': serializer.data,
            'role_specific': role_update_response
        }
        return Response(response_data, status=status.HTTP_200_OK)

# Doktor uchun qo'shimcha ma'lumotlarni yangilash
class MyDoctorProfileUpdateView(generics.UpdateAPIView):
    serializer_class = DoctorProfileUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        user = self.request.user
        if not user.is_doctor:
            raise PermissionError("Siz doktor emassiz")
        
        # Agar doktor profili mavjud bo'lmasa, yaratish
        doctor, created = Doctor.objects.get_or_create(user=user)
        return doctor
    
    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except PermissionError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

# Reception uchun qo'shimcha ma'lumotlarni yangilash
class MyReceptionProfileUpdateView(generics.UpdateAPIView):
    serializer_class = ReceptionProfileUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        user = self.request.user
        if not user.is_reception:
            raise PermissionError("Siz reception emassiz")
        
        # Agar reception profili mavjud bo'lmasa, yaratish
        reception, created = Reception.objects.get_or_create(user=user)
        return reception
    
    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except PermissionError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)


class DirectorDoctorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsDirector, IsDirectorOfHospital]
    
    def get_queryset(self):
        user = self.request.user
        hospital = user.managed_hospital
        
        # Faqat shu shifoxonadagi doktorlar
        return Doctor.objects.filter(
            hospital=hospital,
            user__is_deleted=False
        ).select_related('user', 'hospital', 'department').order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DoctorCreateUpdateSerializer
        return DoctorListSerializer
    
    def perform_destroy(self, instance):
        # Doktorni o'chirish (aslida statusni 0 ga qaytarish)
        user = instance.user
        user.status = 0  # User
        user.save()
        instance.delete()

# ==================== RECEPTION VIEWS ====================

class DirectorReceptionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsDirector, IsDirectorOfHospital]
    
    def get_queryset(self):
        user = self.request.user
        hospital = user.managed_hospital
        
        # Faqat shu shifoxonadagi receptionlar
        return Reception.objects.filter(
            hospital=hospital,
            user__is_deleted=False
        ).select_related('user', 'hospital').order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ReceptionCreateUpdateSerializer
        return ReceptionListSerializer
    
    def perform_destroy(self, instance):
        # Receptionni o'chirish (aslida statusni 0 ga qaytarish)
        user = instance.user
        user.status = 0  # User
        user.save()
        instance.delete()

# ==================== QUEUE VIEWS ====================

class DirectorQueueViewSet(viewsets.ModelViewSet):
    permission_classes = [IsDirector, IsDirectorOfHospital]
    serializer_class = QueueListSerializer
    
    def get_queryset(self):
        user = self.request.user
        hospital = user.managed_hospital
        
        # Shu shifoxonadagi doktorlarning navbatlari
        return Queue.objects.filter(
            doctor__hospital=hospital
        ).select_related(
            'doctor', 'doctor__user', 'doctor__department',
            'user', 'reception'
        ).order_by('-date', 'number')
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Bugungi navbatlar"""
        hospital = request.user.managed_hospital
        today_queues = self.get_queryset().filter(date=date.today())
        
        # Doktor bo'yicha guruhlash
        doctors_data = []
        for doctor in Doctor.objects.filter(hospital=hospital):
            doctor_queues = today_queues.filter(doctor=doctor)
            doctors_data.append({
                'doctor_id': doctor.id,
                'doctor_name': doctor.user.fullname,
                'department': doctor.department.name if doctor.department else None,
                'total': doctor_queues.count(),
                'waiting': doctor_queues.filter(status=0).count(),
                'called': doctor_queues.filter(status=1).count(),
                'done': doctor_queues.filter(status=2).count(),
                'queues': QueueListSerializer(doctor_queues, many=True).data
            })
        
        return Response({
            'date': date.today(),
            'total': today_queues.count(),
            'doctors': doctors_data
        })
    
    @action(detail=False, methods=['get'])
    def by_date(self, request):
        """Berilgan sanadagi navbatlar"""
        queue_date = request.query_params.get('date')
        if not queue_date:
            return Response({'error': 'Date parameter required'}, status=400)
        
        queues = self.get_queryset().filter(date=queue_date)
        serializer = self.get_serializer(queues, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Navbat statusini yangilash"""
        queue = self.get_object()
        serializer = QueueUpdateSerializer(queue, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(QueueListSerializer(queue).data)
        return Response(serializer.errors, status=400)

# ==================== DASHBOARD VIEWS ====================

class DirectorDashboardView(generics.GenericAPIView):
    permission_classes = [IsDirector]
    
    def get(self, request):
        hospital = request.user.managed_hospital
        today = date.today()
        
        # Doktorlar statistikasi
        total_doctors = Doctor.objects.filter(hospital=hospital).count()
        
        # Receptionlar statistikasi
        total_receptions = Reception.objects.filter(hospital=hospital).count()
        
        # Bugungi navbatlar
        today_queues = Queue.objects.filter(
            doctor__hospital=hospital,
            date=today
        )
        
        # Haftalik navbatlar
        week_ago = today - timedelta(days=7)
        weekly_queues = Queue.objects.filter(
            doctor__hospital=hospital,
            date__gte=week_ago
        )
        
        data = {
            'hospital_name': hospital.name,
            'stats': {
                'total_doctors': total_doctors,
                'total_receptions': total_receptions,
                'today_queues': today_queues.count(),
                'weekly_queues': weekly_queues.count(),
                'waiting_queues': today_queues.filter(status=0).count(),
                'completed_queues': today_queues.filter(status=2).count(),
            },
            'recent_queues': QueueListSerializer(
                today_queues.order_by('-created_at')[:10], 
                many=True
            ).data
        }
        
        return Response(data)

# ==================== CANDIDATES VIEWS ====================

class DirectorCandidatesView(generics.ListAPIView):
    permission_classes = [IsDirector]
    
    def get(self, request):
        hospital = request.user.managed_hospital
        
        # Doktor bo'lishi mumkin bo'lgan userlar
        doctor_candidates = CustomUser.objects.filter(
            status=0,  # User
            is_active=True,
            is_deleted=False
        ).exclude(
            doctor_profile__isnull=False
        ).values('id', 'email', 'fullname', 'phone')
        
        # Reception bo'lishi mumkin bo'lgan userlar
        reception_candidates = CustomUser.objects.filter(
            status=0,  # User
            is_active=True,
            is_deleted=False
        ).exclude(
            reception_profile__isnull=False
        ).values('id', 'email', 'fullname', 'phone')
        
        return Response({
            'doctor_candidates': doctor_candidates,
            'reception_candidates': reception_candidates
        })


class DirectorReceptionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsDirector]
    
    def get_queryset(self):
        # Faqat director o'z shifoxonasidagi receptionlarni ko'radi
        user = self.request.user
        hospital = user.managed_hospital
        
        return Reception.objects.filter(
            hospital=hospital,
            user__is_deleted=False
        ).select_related('user', 'hospital').order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DirectorReceptionCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return DirectorReceptionUpdateSerializer
        return DirectorReceptionListSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Hospitalni director shifoxonasiga o'rnatish
        hospital = request.user.managed_hospital
        serializer.validated_data['hospital'] = hospital
        
        reception = serializer.save()
        
        # Javobni list serializer formatida qaytarish
        response_serializer = DirectorReceptionListSerializer(reception)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Hospitalni director shifoxonasiga o'rnatish
        hospital = request.user.managed_hospital
        request.data['hospital'] = hospital.id
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Javobni list serializer formatida qaytarish
        response_serializer = DirectorReceptionListSerializer(instance)
        return Response(response_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        reception = self.get_object()
        user = reception.user
        
        # User statusini 0 ga qaytarish
        user.status = 0  # User
        user.save()
        
        # Receptionni o'chirish
        reception.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def candidates(self, request):
        """Reception bo'lishi mumkin bo'lgan userlar"""
        hospital = request.user.managed_hospital
        
        candidates = CustomUser.objects.filter(
            status=0,  # User
            is_active=True,
            is_deleted=False
        ).exclude(
            reception_profile__isnull=False  # Reception bo'lmaganlar
        ).values('id', 'email', 'fullname', 'phone')
        
        return Response(candidates)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Receptionni aktiv/blok holatini o'zgartirish"""
        reception = self.get_object()
        user = reception.user
        
        user.is_blocked = not user.is_blocked
        user.save()
        
        return Response({
            'status': 'success',
            'is_blocked': user.is_blocked,
            'message': 'Bloklandi' if user.is_blocked else 'Faollashtirildi'
        })

class DirectorReceptionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsDirector]
    
    def get_queryset(self):
        # Faqat director o'z shifoxonasidagi receptionlarni ko'radi
        user = self.request.user
        hospital = user.managed_hospital
        
        return Reception.objects.filter(
            hospital=hospital,
            user__is_deleted=False
        ).select_related('user', 'hospital').order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReceptionCreateSerializer
        return ReceptionListSerializer
    
    def create(self, request, *args, **kwargs):
        # Hospitalni director shifoxonasiga o'rnatish
        hospital = request.user.managed_hospital
        
        serializer = self.get_serializer(
            data=request.data,
            context={'hospital': hospital}
        )
        serializer.is_valid(raise_exception=True)
        reception = serializer.save()
        
        # Javobni list serializer formatida qaytarish
        response_serializer = ReceptionListSerializer(reception)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """UPDATE METHOD IS NOT ALLOWED"""
        return Response(
            {"error": "Reception ma'lumotlarini tahrirlash mumkin emas"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def partial_update(self, request, *args, **kwargs):
        """PARTIAL UPDATE IS NOT ALLOWED"""
        return Response(
            {"error": "Reception ma'lumotlarini tahrirlash mumkin emas"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def destroy(self, request, *args, **kwargs):
        reception = self.get_object()
        user = reception.user
        
        # User statusini 0 ga qaytarish
        user.status = 0  # User
        user.save()
        
        # Receptionni o'chirish
        reception.delete()
        
        return Response(
            {"message": "Reception muvaffaqiyatli o'chirildi"},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def candidates(self, request):
        """Reception bo'lishi mumkin bo'lgan userlar (status=0)"""
        candidates = CustomUser.objects.filter(
            status=0,  # User
            is_active=True,
            is_deleted=False,
            reception_profile__isnull=True  # Reception bo'lmaganlar
        ).order_by('email')
        
        serializer = ReceptionCandidateSerializer(candidates, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_block(self, request, pk=None):
        """Receptionni bloklash/faollashtirish"""
        reception = self.get_object()
        user = reception.user
        
        user.is_blocked = not user.is_blocked
        user.save()
        
        return Response({
            'success': True,
            'is_blocked': user.is_blocked,
            'message': 'Bloklandi' if user.is_blocked else 'Faollashtirildi'
        })