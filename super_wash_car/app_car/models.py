from django.db import models
from django.contrib.auth.models import User



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
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date = models.DateTimeField()
    type_vehicule = models.CharField(max_length=50, choices=TYPE_VEHICULE_CHOICES, default='inconnu')
    rappel_envoye = models.BooleanField(default=False)
    tarification = models.ForeignKey(Tarification, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.date
