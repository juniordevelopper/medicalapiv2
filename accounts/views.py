from rest_framework import viewsets, status, views, filters, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
import random
import string
import uuid

from .serializers import UserDetailSerializer, DirectorCandidateSerializer
from .permissions import IsAdminUser

User = get_user_model()

# -------------------------------------------------------------------------
# Admin uchun Foydalanuvchilarni Boshqarish (CRUD + Filter)
# -------------------------------------------------------------------------
class UserManagementViewSet(viewsets.ModelViewSet):
    """
    Adminlar uchun: Ro'yxatni ko'rish, qidirish va filtrlash.
    Oldingi AllUserListView o'rnini ham bosadi.
    """
    queryset = User.objects.filter(is_deleted=False).order_by('-created_at')
    serializer_class = UserDetailSerializer
    permission_classes = [IsAdminUser]

    # Backend filtrlash tizimi
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    
    # Siz so'ragan barcha filterlar: 
    # status (rol), is_active_account (tasdiqlash), is_blocked (blok)
    filterset_fields = ['status', 'is_active_account', 'is_blocked']
    
    # Ism, Email va Telefon bo'yicha qidiruv
    search_fields = ['fullname', 'email', 'phone', 'username']


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