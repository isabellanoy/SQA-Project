from django.db import models

# Create your models here.
class Laboratorios(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre