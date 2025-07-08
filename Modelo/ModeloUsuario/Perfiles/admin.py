from django.contrib import admin
from Modelo.ModeloMedicamentos.Medicamentos.models import Medicamento
from Modelo.ModeloLaboratorio.Laboratorios.models import Laboratorios
from Modelo.ModeloFarmacia.Farmacias.models import Farmacia

# Register your models here.
admin.site.register(Medicamento)
admin.site.register(Laboratorios)
admin.site.register(Farmacia)