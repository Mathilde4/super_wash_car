from django.shortcuts import render
from rest_framework import viewsets
from .models import Client,Service,RendezVous
from .serializers import ClientSerializer,ServiceSerializer,RendezVousSerializer

# pour le client

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


# pour le service

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

# pour le rendez-vous

class RendezVousViewSet(viewsets.ModelViewSet):
    queryset = RendezVous.objects.all()
    serializer_class = RendezVousSerializer
