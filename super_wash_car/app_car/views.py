from django.shortcuts import render
from rest_framework import viewsets, status
from .models import Client, Service, RendezVous, Tarification,UserProfile
from .serializers import ClientSerializer, ServiceSerializer, RendezVousSerializer, TarificationSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import F
from django.utils import timezone
from datetime import timedelta, datetime
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .serializers import UserRegisterSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.db.models import Sum, Count
from django.utils.timezone import now
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate
from .serializers import UserRegisterSerializer
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError

from .models import Client, Service, RendezVous, Tarification, UserProfile
from .serializers import (
    ClientSerializer,  
    RendezVousSerializer, 
    TarificationSerializer, 
    UserRegisterSerializer
)

# --------------------------
# Authentification
# --------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        
        # Création du profil client automatiquement (sécurisé)
        profile, created = UserProfile.objects.get_or_create(user=user, defaults={'role': 'client'})

        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': profile.role,
            },
            'token': token.key,
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)

    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        profile = UserProfile.objects.get(user=user)
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': profile.role,
            },
            'token': token.key,
        }, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Nom d\'utilisateur ou mot de passe incorrect'}, status=status.HTTP_400_BAD_REQUEST)

# --------------------------
# VueSet Client
# --------------------------

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    @action(detail=True, methods=['GET'])
    def historique(self, request, pk=None):
        client = self.get_object()
        rdvs = RendezVous.objects.filter(client=client)
        data = [
            {
                'service': rdv.service.nom,
                'date': rdv.date,
                'prix': rdv.tarification.prix if rdv.tarification else None,
                'etat': rdv.status,
            } for rdv in rdvs
        ]
        return Response(data)

    @action(detail=False, methods=['GET'])
    def top_fideles(self, request):
        top_clients = Client.objects.order_by('-points_fidelite')[:5]
        data = [
            {
                'nom': c.nom,
                'points_fidelite': c.points_fidelite
            }
            for c in top_clients
        ]
        return Response(data)

# --------------------------
# VueSet Service
# --------------------------

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

# --------------------------
# VueSet Tarification
# --------------------------

class TarificationViewSet(viewsets.ModelViewSet):
    queryset = Tarification.objects.all()
    serializer_class = TarificationSerializer

# --------------------------
# VueSet RendezVous (réservations)
# --------------------------

class RendezVousViewSet(viewsets.ModelViewSet):
    queryset = RendezVous.objects.all()
    serializer_class = RendezVousSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Le client connecté réserve
        profile = UserProfile.objects.get(user=self.request.user)
        if profile.role != 'client':
            raise ValidationError("Seuls les clients peuvent réserver.")

        # Trouver le client lié à ce profil
        client = get_object_or_404(Client, user=self.request.user)

        service = serializer.validated_data['service']
        type_vehicule = serializer.validated_data['type_vehicule']

        # Cherche la tarification
        try:
            tarification = Tarification.objects.get(service=service, type_vehicule=type_vehicule)
        except Tarification.DoesNotExist:
            raise ValidationError("Tarification indisponible pour ce service et type de véhicule.")

        serializer.save(client=client, tarification=tarification, status="en attente")

    # Liste des réservations en attente pour l'admin
    @action(detail=False, methods=['GET'])
    def en_attente(self, request):
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'admin':
            return Response({'error': 'Accès réservé à l\'administrateur'}, status=status.HTTP_403_FORBIDDEN)
        
        rdvs = RendezVous.objects.filter(laveur__isnull=True)
        serializer = self.get_serializer(rdvs, many=True)
        return Response(serializer.data)

    # Admin assigne un laveur
    @action(detail=True, methods=['POST'])
    def assigner_laveur(self, request, pk=None):
        rendezvous = self.get_object()
        laveur_id = request.data.get('laveur_id')

        laveur_profile = get_object_or_404(UserProfile, id=laveur_id, role='laveur')
        rendezvous.laveur = laveur_profile.user
        rendezvous.status = 'assigné'
        rendezvous.save()

        return Response({'message': 'Laveur assigné avec succès.'})

    # Le laveur termine un service
    @action(detail=True, methods=['POST'])
    def terminer(self, request, pk=None):
        rendezvous = self.get_object()
        profile = UserProfile.objects.get(user=request.user)

        if profile.role != 'laveur' or rendezvous.laveur != request.user:
            return Response({'error': 'Vous n\'êtes pas autorisé à terminer ce service.'}, status=status.HTTP_403_FORBIDDEN)
        
        rendezvous.status = 'terminé'
        rendezvous.save()

        # Ajouter des points de fidélité au client
        rendezvous.client.points_fidelite += 10
        rendezvous.client.save()

        return Response({'message': 'Service terminé. Points fidélité ajoutés.'})

    # Les créneaux disponibles
    @action(detail=False, methods=['GET'])
    def disponibilites(self, request):
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({'error': 'Veuillez fournir une date (format: YYYY-MM-DD)'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            date_choisie = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Format de date invalide. Utilisez YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)

        creneaux_possibles = [
            timezone.make_aware(datetime.combine(date_choisie, timezone.datetime.min.time()) + timedelta(hours=heure))
            for heure in range(9, 17)
        ]

        creneaux_pris = RendezVous.objects.filter(date__date=date_choisie).values_list('date', flat=True)

        creneaux_disponibles = [creneau.isoformat() for creneau in creneaux_possibles if creneau not in creneaux_pris]

        return Response({
            'date': date_str,
            'creneaux_disponibles': creneaux_disponibles
        })

    
@api_view(['GET'])
def total_clients(request):
    total = Client.objects.count()
    return Response({'total_clients': total})

@api_view(['GET'])
def total_rendezvous(request):
    total = RendezVous.objects.count()
    return Response({'total_rendezvous': total})

@api_view(['GET'])
def rendezvous_aujourdhui(request):
    today = now().date()
    count = RendezVous.objects.filter(date__date=today).count()
    return Response({'rendezvous_aujourdhui': count})

@api_view(['GET'])
def top_services(request):
    services = Service.objects.annotate(nb_rendezvous=Count('rendezvous')).order_by('-nb_rendezvous')[:5]
    data = [
        {
            'service': service.nom,
            'nombre_rendezvous': service.nb_rendezvous
        }
        for service in services
    ]
    return Response(data)

@api_view(['GET'])
def revenus_par_service(request):
    revenus = Tarification.objects.values('service__nom').annotate(total=Sum('prix')).order_by('-total')
    return Response(revenus)

@api_view(['GET'])
def revenus_totaux(request):
    total = RendezVous.objects.aggregate(total_revenu=Sum('tarification__prix'))
    return Response({'revenus_totaux': total['total_revenu']})

@api_view(['GET'])
def top_clients(request):
    clients = Client.objects.order_by('-points_fidelite')[:5]
    data = [
        {
            'nom': client.nom,
            'points_fidelite': client.points_fidelite
        }
        for client in clients
    ]
    return Response(data)

@api_view(['GET'])
def clients_fideles(request):
    seuil = int(request.query_params.get('seuil', 100)) 
    count = Client.objects.filter(points_fidelite__gte=seuil).count()
    return Response({'clients_fideles': count})
