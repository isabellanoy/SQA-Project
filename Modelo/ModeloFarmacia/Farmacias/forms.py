from django import forms
from .models import Farmacia

class FarmaciaForm(forms.ModelForm):
    class Meta:
        model = Farmacia
        fields = '__all__'
#        widgets = {
#            'componentes': forms.Textarea(attrs={'rows': 3}),
#        }
#        labels = {
#            'nombre_comercial': 'Nombre Comercial del Medicamento',
#            'nombre_farmacologico': 'Nombre Farmacológico (DCI)',
#        }