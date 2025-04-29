from rest_framework import serializers
from .models import Client, Service, RendezVous, Tarification,UserProfile
from django.contrib.auth.models import User



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user', 'role']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data)
        user_profile = UserProfile.objects.create(user=user, **validated_data)
        return user_profile

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data.get('email', '')
        )
        user.set_password(validated_data['password'])
        user.save()

        # Assigner un rôle par défaut de 'client' lors de la création d'un utilisateur
        user_profile = UserProfile.objects.create(user=user, role='client')
        
        return user
        
# Serializer pour les clients
class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['nom', 'description']  # Vous pouvez ajouter plus de champs si nécessaire


# Serializer pour les tarifications
class TarificationSerializer(serializers.ModelSerializer):
    service = serializers.SlugRelatedField(
        queryset=Service.objects.all(),
        slug_field='nom'
    )

    class Meta:
        model = Tarification
        fields = ['id', 'service', 'type_vehicule', 'prix']


# Serializer pour les rendez-vous
class RendezVousSerializer(serializers.ModelSerializer):
    tarification = TarificationSerializer(read_only=True)

    class Meta:
        model = RendezVous
        fields = '__all__'
