from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Department, Hospital, HospitalImage
from .serializers import DepartmentSerializer, HospitalSerializer
from accounts.permissions import IsAdminUser

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all().order_by('name')
    serializer_class = DepartmentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsAdminUser()]

class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.all().order_by('-created_at')
    serializer_class = HospitalSerializer
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['location', 'departments']
    search_fields = ['name', 'address']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsAdminUser()]

    def perform_create(self, serializer):
        hospital = serializer.save()
        images = self.request.FILES.getlist('uploaded_images')
        for image in images:
            HospitalImage.objects.create(hospital=hospital, image=image)

    def perform_update(self, serializer):
        hospital = serializer.save()
        hospital.images.all().delete()
        images = self.request.FILES.getlist('uploaded_images')
        for image in images:
            HospitalImage.objects.create(hospital=hospital, image=image)
