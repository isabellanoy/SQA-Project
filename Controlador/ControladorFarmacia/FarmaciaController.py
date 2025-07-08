from django.shortcuts import render, redirect
from Modelo.ModeloFarmacia.Farmacias.models import Farmacia
from Modelo.ModeloFarmacia.Farmacias.forms import FarmaciaForm
from Modelo.ModeloLaboratorio.Laboratorios.models import Laboratorios
from Modelo.ModeloMedicamentos.Medicamentos.models import Medicamento
from django.shortcuts import get_object_or_404

def registrar_farmacia(request):
    if request.method == 'POST':
        form = FarmaciaForm(request.POST)
        if form.is_valid():
            # ⬇ Aquí seguimos la estructura orientada a objetos:
            farmacia = form.save(commit=False)  # Crea una instancia de Farmacia
            farmacia.save()                     # Guarda la instancia en la base de datos
            form.save_m2m()                     # Guarda la relación ManyToMany con Laboratorios
            return redirect('lista_farmacias')
    else:
        form = FarmaciaForm()
    
    return render(request, 'registro_farm.html', {'form': form})

def lista_farm(request):
    orden = request.GET.get('orden')

    if orden == 'alfabetico':
        farmacias = Farmacia.objects.order_by('nombre')
    elif orden == 'reciente':
        farmacias = Farmacia.objects.order_by('-id')
    elif orden == 'laboratorio':
        farmacias = Farmacia.objects.order_by('laboratorios__nombre')
    else:
        farmacias = Farmacia.objects.all()

    laboratorios = Laboratorios.objects.all()
    medicamentos = Medicamento.objects.all()
    
    return render(request, 'lista_farm.html', {
        'farmacias': farmacias,
        'laboratorios': laboratorios,
        'medicamentos': medicamentos
    })

def modificar_farmacia(request, id):
    farmacia = get_object_or_404(Farmacia, pk=id)
    
    if request.method == 'POST':
        form = FarmaciaForm(request.POST, instance=farmacia)
        if form.is_valid():
            farmacia = form.save(commit=False)
            farmacia.save()
            form.save_m2m()
            return redirect('lista_farmacias')
    else:
        form = FarmaciaForm(instance=farmacia)
    
    return render(request, 'modificar_farmacia.html', {'form': form})