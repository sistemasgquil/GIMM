from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Socio
from .serializers import SocioSerializer


class SocioListCreateAPIView(generics.ListCreateAPIView):

    queryset = Socio.objects.all().order_by('-id')

    serializer_class = SocioSerializer

    permission_classes = [IsAuthenticated]


class SocioDetailAPIView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Socio.objects.all()

    serializer_class = SocioSerializer

    permission_classes = [IsAuthenticated]