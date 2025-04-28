from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet,ServiceViewSet,RendezVousViewSet, TarificationViewSet
from .views import register, login_view

router = DefaultRouter()

router.register(r'clients', ClientViewSet)
router.register(r'services',ServiceViewSet)
router.register(r'rendezvous', RendezVousViewSet)
router.register(r'tarifications', TarificationViewSet)

urlpatterns =[
    path('',include(router.urls)),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
]