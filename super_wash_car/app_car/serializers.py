from rest_framework import serializers
from .models import Client, Service, RendezVous, Tarification, UserProfile
from django.contrib.auth.models import User



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
        # le profil est créé automatiquement via le signal
        return user
    
class UserProfileSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserProfile
        fields = ['role']

        
class UserNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ClientSerializer(serializers.ModelSerializer):
    user = UserNestedSerializer(read_only=True)

    class Meta:
        model = Client
        fields = ['id', 'points_fidelite', 'user']

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id','nom', 'description']  # Vous pouvez ajouter plus de champs si nécessaire


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
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())
    username = serializers.SerializerMethodField(read_only=True)
    laveur = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(userprofile__role='laveur'), required=False)
    

    

    class Meta:
        model = RendezVous
        fields = '__all__'  # ou liste tous les champs explicitement
        read_only_fields = ['client', 'tarification', 'status', 'username']


    def get_username(self, obj):
        return obj.client.user.username
    
    def update(self, instance, validated_data):
        laveur = validated_data.get('laveur', None)
        if laveur:
            instance.laveur = laveur
            if instance.status == 'en_attente':
                instance.status = 'en_cours'
        return super().update(instance, validated_data)