from rest_framework import viewsets, permissions
from .models import Location
from .serializers import LocationSerializer
from .permissions import IsAdminUserStatus

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all().order_by('name')
    serializer_class = LocationSerializer

    def get_permissions(self):
        # list va retrieve (ko'rish) hamma kirgan foydalanuvchilar uchun
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        # create, update, partial_update, destroy faqat Admin uchun
        else:
            permission_classes = [IsAdminUserStatus]
        return [permission() for permission in permission_classes]
