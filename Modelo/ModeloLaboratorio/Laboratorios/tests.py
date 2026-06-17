from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Laboratorios


class LaboratorioModelTest(TestCase):

    def setUp(self):
        self.laboratorio = Laboratorios.objects.create(
            nombre='Bayer',
            direccion='Calle 123'
        )

    def test_crear_laboratorio(self):
        """Se crea un laboratorio con nombre y dirección correctos."""
        self.assertEqual(self.laboratorio.nombre, 'Bayer')
        self.assertEqual(self.laboratorio.direccion, 'Calle 123')

    def test_str_laboratorio(self):
        """__str__ retorna el nombre del laboratorio."""
        self.assertEqual(str(self.laboratorio), 'Bayer')

    def test_nombre_max_length(self):
        """El campo nombre tiene un max_length de 100 caracteres."""
        max_length = Laboratorios._meta.get_field('nombre').max_length
        self.assertEqual(max_length, 100)

    def test_direccion_max_length(self):
        """El campo direccion tiene un max_length de 100 caracteres."""
        max_length = Laboratorios._meta.get_field('direccion').max_length
        self.assertEqual(max_length, 100)

    def test_laboratorio_persiste_en_bd(self):
        """El laboratorio creado en setUp se encuentra en la base de datos."""
        laboratorio_db = Laboratorios.objects.get(pk=self.laboratorio.pk)
        self.assertEqual(laboratorio_db.nombre, 'Bayer')

    def test_crear_multiples_laboratorios(self):
        """Se pueden crear múltiples laboratorios sin conflicto."""
        Laboratorios.objects.create(nombre='Pfizer', direccion='Av. 456')
        Laboratorios.objects.create(nombre='Roche', direccion='Carrera 789')
        self.assertEqual(Laboratorios.objects.count(), 3)


# ---------------------------------------------------------------------------
# NuevoLaboratorio form
# ---------------------------------------------------------------------------

from .forms import NuevoLaboratorio


class NuevoLaboratorioFormTest(TestCase):

    def test_form_valido(self):
        """Formulario válido con nombre y dirección correctos."""
        form = NuevoLaboratorio(data={'nombre': 'Genfar', 'direccion': 'Calle 10'})
        self.assertTrue(form.is_valid())

    def test_form_nombre_vacio(self):
        """Formulario inválido si el nombre está vacío."""
        form = NuevoLaboratorio(data={'nombre': '', 'direccion': 'Calle 10'})
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)

    def test_form_direccion_vacia(self):
        """Formulario inválido si la dirección está vacía."""
        form = NuevoLaboratorio(data={'nombre': 'Genfar', 'direccion': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('direccion', form.errors)

    def test_form_ambos_campos_vacios(self):
        """Formulario inválido si nombre y dirección están vacíos."""
        form = NuevoLaboratorio(data={'nombre': '', 'direccion': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 2)

    def test_form_nombre_excede_longitud(self):
        """Formulario inválido si el nombre supera 200 caracteres."""
        form = NuevoLaboratorio(data={'nombre': 'A' * 201, 'direccion': 'Calle 10'})
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)

    def test_form_direccion_excede_longitud(self):
        """Formulario inválido si la dirección supera 200 caracteres."""
        form = NuevoLaboratorio(data={'nombre': 'Genfar', 'direccion': 'B' * 201})
        self.assertFalse(form.is_valid())
        self.assertIn('direccion', form.errors)

    def test_form_guarda_instancia(self):
        """form.save() crea un registro en la base de datos."""
        form = NuevoLaboratorio(data={'nombre': 'Roche', 'direccion': 'Av. 1'})
        self.assertTrue(form.is_valid())
        lab = form.save()
        self.assertEqual(lab.nombre, 'Roche')
        self.assertTrue(Laboratorios.objects.filter(nombre='Roche').exists())

    def test_form_actualiza_instancia(self):
        """form.save() con instance actualiza el registro existente."""
        lab = Laboratorios.objects.create(nombre='Viejo Nombre', direccion='Calle 1')
        form = NuevoLaboratorio(
            data={'nombre': 'Nuevo Nombre', 'direccion': 'Calle 2'},
            instance=lab
        )
        self.assertTrue(form.is_valid())
        form.save()
        lab.refresh_from_db()
        self.assertEqual(lab.nombre, 'Nuevo Nombre')
