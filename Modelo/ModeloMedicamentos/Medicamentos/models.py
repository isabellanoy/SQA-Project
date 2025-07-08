from django.db import models
from Modelo.ModeloLaboratorio.Laboratorios.models import Laboratorios

# Create your models here.
class Medicamento(models.Model):
    nombre_comercial = models.CharField(max_length=100, verbose_name="Nombre Comercial")
    nombre_farmacologico = models.CharField(max_length=100, verbose_name="Nombre Farmacológico")
    componentes = models.TextField(verbose_name="Componentes")
    laboratorio=models.ForeignKey(Laboratorios, on_delete=models.CASCADE, default=1)

    class Meta:
        verbose_name = "Medicamento"
        verbose_name_plural = "Medicamentos"
        ordering = ['nombre_comercial']
    
    def __str__(self):
        return f"{self.nombre_comercial} ({self.laboratorio.nombre})"