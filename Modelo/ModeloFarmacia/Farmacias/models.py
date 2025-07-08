from django.db import models
from Modelo.ModeloLaboratorio.Laboratorios.models import Laboratorios

class Farmacia(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=100)
    laboratorios = models.ManyToManyField(Laboratorios, related_name='farmacias')
    
    def __str__(self):
        return self.nombre