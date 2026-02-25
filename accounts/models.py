from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


# ----------------------------
# CustomUser
# ----------------------------
class CustomUser(AbstractUser):
    USER_STATUS = (
        (0, "User"),
        (1, "Reception"),
        (2, "Doctor"),
        (3, "Director"),
        (4, "Admin"),
    )
    
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    fullname = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)

    status = models.IntegerField(choices=USER_STATUS, default=0)
    is_deleted = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    
    last_email_sent = models.DateTimeField(null=True, blank=True)
    verification_token = models.CharField(max_length=100, null=True, blank=True)
    otp_code = models.CharField(max_length=6, null=True, blank=True)

    profile = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    @property
    def is_patient(self): 
        return self.status == 0
        
    @property
    def is_reception(self): 
        return self.status == 1
        
    @property
    def is_doctor(self): 
        return self.status == 2
        
    @property
    def is_director(self): 
        return self.status == 3
        
    @property
    def is_admin_user(self): 
        return self.status == 4

    @property
    def check_active(self):
        return self.is_deleted

    @property
    def check_blocked(self):
        return self.is_blocked

    def __str__(self):
        return f"{self.email} ({self.get_status_display()})"


# ----------------------------
# Doctor
# ----------------------------
class Doctor(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    description = models.TextField(blank=True, null=True)
    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctors'
    )
    department = models.ForeignKey(
        'hospitals.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctors'
    )
    tajriba = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Dr. {self.user.fullname or self.user.email}"


# ----------------------------
# Reception
# ----------------------------
class Reception(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reception_profile'
    )
    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.CASCADE,
        related_name='receptions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Reception: {self.user.fullname or self.user.email}"