from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import RendezVous
from django.contrib.auth.models import User
from .models import UserProfile

# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)

@receiver(post_save, sender=RendezVous)
def envoyer_rappel_rendezvous(sender,instance,created, **kwargs):
    if created and not instance.rappel_envoye:
        send_mail(
            'Rappel de rendez-vous',
            f"Bonjour {instance.client.user.username}, n'oubliez pas votre rendez-vous pour le service '{instance.service.nom}' le {instance.date}. ",
            'super.car.wash@gmail.com',
            [instance.client.user.email],
            fail_silently=False,
        )
        instance.rappel_envoye =True
        instance.save()