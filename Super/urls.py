"""
URL configuration for Super project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Controlador.ControladorUsuario import PerfilController
from Controlador.ControladorMedicamentos import MedicamentoController
from Controlador.ControladorFarmacia import FarmaciaController
from Controlador.ControladorLaboratorio import LaboratorioController

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', PerfilController.home, name='home'),
    path('signup/', PerfilController.signup, name='signup'),
    path('perfiles/', PerfilController.perfiles, name='perfiles'),
    path('logout/', PerfilController.signout, name='signout'),
    path('signin/', PerfilController.signin, name='signin'),
    path('registrar/', MedicamentoController.registrar_medicamento, name='registrar_medicamento'),
    path('lista/', MedicamentoController.lista_medicamentos, name='lista_medicamentos'),
    path('editar/<int:id>/',  MedicamentoController.editar_medicamento, name='editar_medicamento'),
    path('eliminar/<int:id>/', MedicamentoController.eliminar_medicamento, name='eliminar_medicamento'),
    path('labs/', LaboratorioController.labs, name='labs'),
    path('crear_labs/', LaboratorioController.crear_labs, name='crear_labs'),
    path('modificar_labs/<int:id>/', LaboratorioController.modificar_labs, name='modificar_labs'),
    path('ver_historial/<int:id>/', LaboratorioController.ver_historial, name='historial_labs'),
    path('farmacias/modificar/<int:id>/', FarmaciaController.modificar_farmacia, name='modificar_farmacia'),
    path('registro_farm/', FarmaciaController.registrar_farmacia, name='agregar_farmacia'),
    path('lista_farm/', FarmaciaController.lista_farm, name='lista_farmacias'),
]
