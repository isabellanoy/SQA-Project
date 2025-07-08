from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from Modelo.ModeloMedicamentos.Medicamentos.forms import MedicamentoForm
from Modelo.ModeloMedicamentos.Medicamentos.models import Medicamento

def registrar_medicamento(request):
    if request.method == 'POST':
        form = MedicamentoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_medicamentos')
    else:
        form = MedicamentoForm()
    
    return render(request, 'registro.html', {'form': form})

def lista_medicamentos(request):
    medicamentos = Medicamento.objects.all()
    return render(request, 'lista.html', {'medicamentos': medicamentos})

def editar_medicamento(request, id):
    medicamento = get_object_or_404(Medicamento, pk=id)
    if request.method == 'POST':
        form = MedicamentoForm(request.POST, instance=medicamento)
        if form.is_valid():
            form.save()
            return redirect('lista_medicamentos')
    else:
        form = MedicamentoForm(instance=medicamento)
    
    return render(request, 'editar_medicamento.html', {'form': form, 'medicamento': medicamento})

def eliminar_medicamento(request, id):
    medicamento = get_object_or_404(Medicamento, pk=id)
    if request.method == 'POST':
        medicamento.delete()
        messages.success(request, 'Medicamento eliminado correctamente')
        return redirect('lista_medicamentos')
    
    return render(request, 'confirmar_eliminar.html', {'medicamento': medicamento})