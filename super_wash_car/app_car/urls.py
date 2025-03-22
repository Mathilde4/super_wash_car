from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet,ServiceViewSet,RendezVousViewSet

router = DefaultRouter()

router.register(r'clients', ClientViewSet,basename='clients')
router.register(r'services',ServiceViewSet, basename='services')
router.register(r'rendezvous', RendezVousViewSet,basename='rendezvous')

urlpatterns =[
    path('',include(router.urls)),
]