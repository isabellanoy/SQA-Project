from django.test import TestCase
from .models import Farmacia
from Modelo.ModeloLaboratorio.Laboratorios.models import Laboratorios


class FarmaciaModelTest(TestCase):

    def setUp(self):
        self.laboratorio1 = Laboratorios.objects.create(
            nombre='Novartis',
            direccion='Av. Principal 10'
        )
        self.laboratorio2 = Laboratorios.objects.create(
            nombre='Sanofi',
            direccion='Calle 50'
        )
        self.farmacia = Farmacia.objects.create(
            nombre='Farmacia Central',
            direccion='Centro Comercial 1'
        )

    def test_crear_farmacia(self):
        """Se crea una farmacia con nombre y dirección correctos."""
        self.assertEqual(self.farmacia.nombre, 'Farmacia Central')
        self.assertEqual(self.farmacia.direccion, 'Centro Comercial 1')

    def test_str_farmacia(self):
        """__str__ retorna el nombre de la farmacia."""
        self.assertEqual(str(self.farmacia), 'Farmacia Central')

    def test_relacion_many_to_many_un_laboratorio(self):
        """Una farmacia puede asociarse con un laboratorio."""
        self.farmacia.laboratorios.add(self.laboratorio1)
        self.assertIn(self.laboratorio1, self.farmacia.laboratorios.all())

    def test_relacion_many_to_many_multiples_laboratorios(self):
        """Una farmacia puede asociarse con múltiples laboratorios."""
        self.farmacia.laboratorios.add(self.laboratorio1, self.laboratorio2)
        self.assertEqual(self.farmacia.laboratorios.count(), 2)

    def test_farmacia_sin_laboratorios(self):
        """Una farmacia puede existir sin laboratorios asignados."""
        self.assertEqual(self.farmacia.laboratorios.count(), 0)

    def test_relacion_inversa_laboratorio_farmacias(self):
        """Desde un laboratorio se puede acceder a sus farmacias (related_name)."""
        self.farmacia.laboratorios.add(self.laboratorio1)
        self.assertIn(self.farmacia, self.laboratorio1.farmacias.all())

    def test_nombre_max_length(self):
        """El campo nombre tiene un max_length de 100 caracteres."""
        max_length = Farmacia._meta.get_field('nombre').max_length
        self.assertEqual(max_length, 100)

    def test_farmacia_persiste_en_bd(self):
        """La farmacia creada en setUp se encuentra en la base de datos."""
        farmacia_db = Farmacia.objects.get(pk=self.farmacia.pk)
        self.assertEqual(farmacia_db.nombre, 'Farmacia Central')


# ---------------------------------------------------------------------------
# FarmaciaForm
# ---------------------------------------------------------------------------

from .forms import FarmaciaForm


class FarmaciaFormTest(TestCase):

    def setUp(self):
        self.lab1 = Laboratorios.objects.create(nombre='Lab A', direccion='Dir A')
        self.lab2 = Laboratorios.objects.create(nombre='Lab B', direccion='Dir B')

    def _datos_validos(self, **kwargs):
        base = {
            'nombre': 'Farmacia Test',
            'direccion': 'Calle 10',
            'laboratorios': [self.lab1.pk],
        }
        base.update(kwargs)
        return base

    def test_form_valido_con_laboratorio(self):
        """Formulario válido con nombre, dirección y al menos un laboratorio."""
        form = FarmaciaForm(data=self._datos_validos())
        self.assertTrue(form.is_valid())

    def test_form_valido_sin_laboratorios(self):
        """FarmaciaForm requiere al menos un laboratorio (campo requerido por Django)."""
        form = FarmaciaForm(data={'nombre': 'Farmacia Sin Lab', 'direccion': 'Calle 1'})
        self.assertFalse(form.is_valid())
        self.assertIn('laboratorios', form.errors)

    def test_form_valido_multiples_laboratorios(self):
        """Formulario válido con múltiples laboratorios seleccionados."""
        form = FarmaciaForm(data=self._datos_validos(
            laboratorios=[self.lab1.pk, self.lab2.pk]
        ))
        self.assertTrue(form.is_valid())

    def test_form_sin_nombre(self):
        """Formulario inválido si falta el nombre."""
        form = FarmaciaForm(data=self._datos_validos(nombre=''))
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)

    def test_form_sin_direccion(self):
        """Formulario inválido si falta la dirección."""
        form = FarmaciaForm(data=self._datos_validos(direccion=''))
        self.assertFalse(form.is_valid())
        self.assertIn('direccion', form.errors)

    def test_form_nombre_max_length(self):
        """Formulario inválido si nombre supera 100 caracteres."""
        form = FarmaciaForm(data=self._datos_validos(nombre='X' * 101))
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)

    def test_form_laboratorio_inexistente(self):
        """Formulario inválido si se referencia un laboratorio que no existe."""
        form = FarmaciaForm(data=self._datos_validos(laboratorios=[9999]))
        self.assertFalse(form.is_valid())
        self.assertIn('laboratorios', form.errors)

    def test_form_guarda_instancia(self):
        """form.save() + save_m2m() crea farmacia con sus laboratorios."""
        form = FarmaciaForm(data=self._datos_validos())
        self.assertTrue(form.is_valid())
        farmacia = form.save(commit=False)
        farmacia.save()
        form.save_m2m()
        self.assertTrue(Farmacia.objects.filter(nombre='Farmacia Test').exists())
        self.assertIn(self.lab1, farmacia.laboratorios.all())

    def test_form_actualiza_instancia(self):
        """form.save() con instance actualiza la farmacia existente."""
        farmacia = Farmacia.objects.create(nombre='Vieja', direccion='Dir vieja')
        form = FarmaciaForm(
            data=self._datos_validos(nombre='Nueva', direccion='Dir nueva'),
            instance=farmacia
        )
        self.assertTrue(form.is_valid())
        form.save()
        farmacia.refresh_from_db()
        self.assertEqual(farmacia.nombre, 'Nueva')
