from django.shortcuts import render, redirect
from Modelo.ModeloMedicamentos.Medicamentos.forms import MedicamentoForm
from Modelo.ModeloMedicamentos.Medicamentos.models import Medicamento

# Create your views here.


def registrar_medicamento(request):
    if request.method == 'POST':
        form = MedicamentoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_medicamentos')  # Redirige a una vista de listado
    else:
        form = MedicamentoForm()
    
    return render(request, 'registro.html', {'form': form})

def lista_medicamentos(request):
    medicamentos = Medicamento.objects.all()
    return render(request, 'lista.html', {'medicamentos': medicamentos})