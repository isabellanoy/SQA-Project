from django import forms
from .models import Laboratorios

class NuevoLaboratorio(forms.ModelForm):
    nombre = forms.CharField(label="ingrese nombre del laboratorio", max_length=200)
    direccion = forms.CharField(label="ingrese la direccion del laboratorio", max_length=200)

    class Meta:
        model = Laboratorios
        fields = ['nombre', 'direccion']