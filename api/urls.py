from django.urls import path, include, re_path
from dj_rest_auth.registration.views import VerifyEmailView, ConfirmEmailView
from rest_framework.routers import DefaultRouter

from locations.views import LocationViewSet
from hospitals.views import HospitalViewSet, DepartmentViewSet
from accounts.views import *

router = DefaultRouter()
router.register(r'locations', LocationViewSet, basename='locations')
router.register(r'departments', DepartmentViewSet, basename='departments')
router.register(r'hospitals', HospitalViewSet, basename='hospitals')
router.register(r'users', UserManagementViewSet, basename='users-manage')
router.register(r'director/doctors', DirectorDoctorViewSet, basename='director-doctor')
router.register(r'director/queues', DirectorQueueViewSet, basename='director-queue')
router.register(r'director/receptions', DirectorReceptionViewSet, basename='director-reception')

urlpatterns = [
    # 1. Standart Auth (Login, Logout, User details)
    path('auth/', include('dj_rest_auth.urls')),
    
    # 2. Registration va Email tasdiqlash
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    re_path(r'^account-confirm-email/(?P<key>[-:\w]+)/$', ConfirmEmailView.as_view(), name='account_confirm_email'),
    path('auth/registration/verify-email/', VerifyEmailView.as_view(), name='rest_verify_email'),
    path('auth/resend-verification/', ResendVerificationView.as_view(), name='resend_verification'),

    # 3. Parol va Usernameni tiklash (Custom endpoints)
    path('auth/password-recovery/', PasswordRecoveryView.as_view(), name='password_recovery'),
    path('auth/username-recovery/', UsernameRecoveryView.as_view(), name='username_recovery'),
    path('auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # 4. Barcha Router URL'lari (Locations, Hospitals, etc.)
    path('', include(router.urls)),

    path('auth/all-users/', AllUserListView.as_view(), name='all_users_list'),
    path('director-candidates/', DirectorCandidateListView.as_view(), name='director-candidates'),

    path('dashboard/stats/', DashboardStatsAPIView.as_view()),

    # YANGI PROFIL URL'LARI
    path('profile/', MyProfileDetailView.as_view(), name='profile-detail'),
    path('profile/update/', MyProfileUpdateView.as_view(), name='profile-update'),
    path('profile/doctor/update/', MyDoctorProfileUpdateView.as_view(), name='doctor-profile-update'),
    path('profile/reception/update/', MyReceptionProfileUpdateView.as_view(), name='reception-profile-update'),
]