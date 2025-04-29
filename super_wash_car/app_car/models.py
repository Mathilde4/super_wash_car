from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('client', 'Client'),
        ('admin', 'Admin'),
        ('laveur', 'Laveur'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Client(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=8,unique=True)
    points_fidelite = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nom

TYPE_VEHICULE_CHOICES = [
    ('voiture', 'Voiture'),
    ('moto', 'Moto'),
    ('camion', 'Camion'),
    ('camionnette', 'Camionnette'),
    ('utilitaire', 'Utilitaire'),
]

class Service(models.Model):
    nom = models.CharField(max_length=100)  # Le nom du service
    description = models.TextField(max_length=255)  # Une description du service
    
    def __str__(self):
        return self.nom


class Tarification(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    type_vehicule = models.CharField(max_length=50, choices=TYPE_VEHICULE_CHOICES)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.service.nom} - {self.type_vehicule} - {self.prix}Franc Cfa"

class RendezVous(models.Model):

    STATUT_CHOICES = [
        ('en attente', 'En attente'),
        ('assigné', 'Assigné à un laveur'),
        ('terminé', 'Terminé'),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date = models.DateTimeField()
    type_vehicule = models.CharField(max_length=50, choices=TYPE_VEHICULE_CHOICES, default='inconnu')
    rappel_envoye = models.BooleanField(default=False)
    tarification = models.ForeignKey(Tarification, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en attente')
    laveur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='rendezvous_laveur')

    def __str__(self):
        return f"Rendez-vous {self.service.nom} pour {self.client.nom} le {self.date.strftime('%Y-%m-%d %H:%M')}"
