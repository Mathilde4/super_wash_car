from django.shortcuts import render
from rest_framework import viewsets, status, generics
from .models import Client, Service, RendezVous, Tarification,UserProfile
from .serializers import ClientSerializer, ServiceSerializer, RendezVousSerializer, TarificationSerializer, UserRegisterSerializer
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
from rest_framework.decorators import api_view
from django.db.models import Sum, Count
from django.utils.timezone import now
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        role = request.data.get('role', 'client')  # Rôle par défaut : client
        profile = UserProfile.objects.create(user=user, role=role)

        if role == 'client':
            Client.objects.create(user=user)  # Crée aussi le client

        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': role,
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
        role = UserProfile.objects.get(user=user).role  
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': role,
            },   
            'token': token.key,
        }, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Nom d\'utilisateur ou mot de passe incorrect'}, status=status.HTTP_400_BAD_REQUEST)
            


class CreateLaveurView(APIView):


    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email', '')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'username et password sont requis'}, status=400)

        user = User(username=username, email=email)
        user.set_password(password)
        user.save()

        UserProfile.objects.create(user=user, role='laveur')  # Attribue le rôle "laveur"

        return Response({'message': 'Laveur créé avec succès'})
    
@api_view(['GET'])

def liste_laveurs(request):
    laveurs = UserProfile.objects.filter(role='laveur').select_related('user')
    data = [
        {
            'id': laveur.user.id,
            'username': laveur.user.username,
            'email': laveur.user.email
        }
        for laveur in laveurs
    ]
    return Response(data)

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    # historique des rendez-vous
    # @action(detail=True, methods=['GET'])
    # def historique(self, request, pk=None):
    #     client = self.get_object()
    #     rendezvous = RendezVous.objects.filter(client=client)
    #     data = [
    #         {
    #             'service': rdv.service.nom,
    #             'date': rdv.date,
    #             'prix': rdv.tarification.prix if rdv.tarification else None
    #         } for rdv in rendezvous
    #     ]
    #     return Response(data)

    # lister les 5 clients les plus fidèles
    @action(detail=False, methods=['GET'])
    def top_fideles(self, request):
        top_clients = Client.objects.order_by('-points_fidelite')[:5]

        data = [
            {
                'nom': client.user.username,
                'points_fidelite': client.points_fidelite
            }
            for client in top_clients
        ]
        return Response(data)


# pour le service
class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all() 
    serializer_class = ServiceSerializer



# pour les tarifs
class TarificationViewSet(viewsets.ModelViewSet):
    queryset = Tarification.objects.all()
    serializer_class = TarificationSerializer


# pour le rendez-vous
class RendezVousViewSet(viewsets.ModelViewSet):
    queryset = RendezVous.objects.all()
    serializer_class = RendezVousSerializer


    def perform_create(self, serializer):
        user = self.request.user

        if not user.is_authenticated:
            raise ValidationError("Utilisateur non authentifié.")

        try:
            client = Client.objects.get(user=user)
        except Client.DoesNotExist:
            raise ValidationError("Client non trouvé pour cet utilisateur.")

        service = serializer.validated_data['service']
        type_vehicule = serializer.validated_data['type_vehicule']

        try:
            tarification = Tarification.objects.get(service=service, type_vehicule=type_vehicule)
        except Tarification.DoesNotExist:
            raise ValidationError(f"Aucune tarification définie pour le service '{service.nom}' et le type de véhicule '{type_vehicule}'.")

        # Création du rendez-vous avec le client connecté
        rendezvous = serializer.save(client=client, tarification=tarification, status='en_attente')

        # Ajout des points fidélité
        client.points_fidelite += 10
        client.save()



    # les créneaux disponibles
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

    # pour lister tous les créneaux pris
    @action(detail=False, methods=['GET'])
    def creneaux_pris(self, request):
        rendezvous = RendezVous.objects.order_by('date')

        creneaux_par_date = {}

        for rdv in rendezvous:
            date_str = rdv.date.date().isoformat()
            heure = rdv.date.strftime('%H:%M')

            if date_str not in creneaux_par_date:
                creneaux_par_date[date_str] = []

            creneaux_par_date[date_str].append({
                'heure': heure,
                'client': rdv.client.user.username,
                'service': rdv.service.nom,
                'prix': rdv.tarification.prix if rdv.tarification else None
            })

        return Response(creneaux_par_date)
    
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
            'nom': client.user.username,
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

class AssignLaveurView(APIView):

    def post(self, request, rendezvous_id):
        try:
            rendezvous = RendezVous.objects.get(id=rendezvous_id)
        except RendezVous.DoesNotExist:
            return Response({'error': 'Rendez-vous non trouvé'}, status=status.HTTP_404_NOT_FOUND)

        if rendezvous.status != 'en_attente':
            return Response({'error': 'Le rendez-vous est déjà en cours ou terminé'}, status=status.HTTP_400_BAD_REQUEST)

        # Assignation du laveur
        laveur_id = request.data.get('laveur_id')
        try:
            laveur = UserProfile.objects.get(id=laveur_id, role='laveur')
        except UserProfile.DoesNotExist:
            return Response({'error': 'Laveur non trouvé'}, status=status.HTTP_404_NOT_FOUND)

        # Mettre à jour le statut
        rendezvous.set_en_cours()

        return Response({'message': 'Laveur assigné avec succès'}, status=status.HTTP_200_OK)
    
class TerminerRendezVousView(APIView):

    def post(self, request, rendezvous_id):
        try:
            rendezvous = RendezVous.objects.get(id=rendezvous_id)
        except RendezVous.DoesNotExist:
            return Response({'error': 'Rendez-vous non trouvé'}, status=status.HTTP_404_NOT_FOUND)

        if rendezvous.status != 'en_cours':
            return Response({'error': 'Le rendez-vous n\'est pas en cours'}, status=status.HTTP_400_BAD_REQUEST)

        # Mettre à jour le statut
        rendezvous.set_terminer()

        return Response({'message': 'Rendez-vous terminé avec succès'}, status=status.HTTP_200_OK)