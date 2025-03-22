from django.db import models
from django.contrib.auth.models import User

class Client(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telephone = models.CharField(max_length=8,unique=True)
    points_fidelite=models.PositiveIntegerField(default=0)


    def __str__(self):
        return self.nom


class Service(models.Model):
    nom =models.CharField(max_length=100)
    description = models.TextField(max_length=50)
    prix =models.DecimalField(max_digits=10,decimal_places=2)
    
    def __str__(self):
        return self.nom



class RendezVous(models.Model):
    Client = models.ForeignKey(Client,on_delete=models.CASCADE)
    service = models.ForeignKey(Service,on_delete=models.CASCADE)
    date = models.DateTimeField()
    rappel_envoye = models.BooleanField(default=False)

    def __str__(self):
        return self.date


