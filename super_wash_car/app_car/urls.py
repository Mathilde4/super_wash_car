from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet,ServiceViewSet,RendezVousViewSet, TarificationViewSet
from .views import register, login_view, CreateLaveurView, liste_laveurs, AssignLaveurView,TerminerRendezVousView
from . import views

router = DefaultRouter()

router.register(r'clients', ClientViewSet)
router.register(r'services',ServiceViewSet)
router.register(r'rendezvous', RendezVousViewSet)
router.register(r'tarifications', TarificationViewSet)

urlpatterns =[
    path('',include(router.urls)),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('laveur/', CreateLaveurView.as_view(), name='create_laveur'),
    path('laveurs/', liste_laveurs, name='liste-laveurs'),
    path('total_clients/', views.total_clients, name='total_clients'),
    path('total_rendezvous/', views.total_rendezvous, name='total_rendezvous'),
    path('rendezvous_aujourdhui/', views.rendezvous_aujourdhui, name='rendezvous_aujourdhui'),
    path('top_services/', views.top_services, name='top_services'),
    path('revenus_par_service/', views.revenus_par_service, name='revenus_par_service'),
    path('revenus_totaux/', views.revenus_totaux, name='revenus_totaux'),
    path('top_clients/', views.top_clients, name='top_clients'),
    path('clients_fideles/', views.clients_fideles, name='clients_fideles'),
    path('assigner_laveur/', AssignLaveurView.as_view(), name='assign_laveur'),
    path('terminer_rendezvous/', TerminerRendezVousView.as_view(), name='terminer_rendezvous'),
    ]