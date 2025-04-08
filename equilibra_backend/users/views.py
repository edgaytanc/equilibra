from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import UserRegisterSerializer, UserProfileSerializer
from django.contrib.auth.models import User

class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]  # Permite acceso sin autenticacion


class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]  

    def get_object(self):
        return self.request.user
