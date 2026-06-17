from django.test import TestCase
from .models import Medicamento
from Modelo.ModeloLaboratorio.Laboratorios.models import Laboratorios


class MedicamentoModelTest(TestCase):

    def setUp(self):
        self.laboratorio = Laboratorios.objects.create(
            nombre='Genfar',
            direccion='Zona Industrial 1'
        )
        self.medicamento = Medicamento.objects.create(
            nombre_comercial='Aspirina',
            nombre_farmacologico='Acido Acetilsalicilico',
            componentes='Acido acetilsalicilico 500mg',
            laboratorio=self.laboratorio
        )

    def test_crear_medicamento(self):
        """Se crea un medicamento con todos sus campos correctamente."""
        self.assertEqual(self.medicamento.nombre_comercial, 'Aspirina')
        self.assertEqual(self.medicamento.nombre_farmacologico, 'Acido Acetilsalicilico')
        self.assertEqual(self.medicamento.componentes, 'Acido acetilsalicilico 500mg')
        self.assertEqual(self.medicamento.laboratorio, self.laboratorio)

    def test_str_medicamento(self):
        """__str__ retorna 'NombreComercial (NombreLaboratorio)'."""
        esperado = 'Aspirina (Genfar)'
        self.assertEqual(str(self.medicamento), esperado)

    def test_cascade_delete(self):
        """Al eliminar el laboratorio, el medicamento asociado también se elimina."""
        self.laboratorio.delete()
        self.assertEqual(Medicamento.objects.filter(pk=self.medicamento.pk).count(), 0)

    def test_ordenamiento_default(self):
        """Los medicamentos se ordenan por nombre_comercial por defecto."""
        Medicamento.objects.create(
            nombre_comercial='Amoxicilina',
            nombre_farmacologico='Amoxicilina',
            componentes='Amoxicilina 500mg',
            laboratorio=self.laboratorio
        )
        medicamentos = list(Medicamento.objects.all())
        self.assertEqual(medicamentos[0].nombre_comercial, 'Amoxicilina')
        self.assertEqual(medicamentos[1].nombre_comercial, 'Aspirina')

    def test_nombre_comercial_max_length(self):
        """El campo nombre_comercial tiene un max_length de 100 caracteres."""
        max_length = Medicamento._meta.get_field('nombre_comercial').max_length
        self.assertEqual(max_length, 100)

    def test_medicamento_persiste_en_bd(self):
        """El medicamento creado en setUp se encuentra en la base de datos."""
        medicamento_db = Medicamento.objects.get(pk=self.medicamento.pk)
        self.assertEqual(medicamento_db.nombre_comercial, 'Aspirina')

    def test_laboratorio_fk(self):
        """El campo laboratorio es una ForeignKey al modelo Laboratorios."""
        field = Medicamento._meta.get_field('laboratorio')
        self.assertEqual(field.related_model, Laboratorios)


# ---------------------------------------------------------------------------
# MedicamentoForm
# ---------------------------------------------------------------------------

from .forms import MedicamentoForm


class MedicamentoFormTest(TestCase):

    def setUp(self):
        self.laboratorio = Laboratorios.objects.create(
            nombre='Lab Form',
            direccion='Calle Test'
        )

    def _datos_validos(self, **kwargs):
        base = {
            'nombre_comercial': 'Paracetamol',
            'nombre_farmacologico': 'Acetaminofen',
            'componentes': 'Acetaminofen 500mg',
            'laboratorio': self.laboratorio.pk,
        }
        base.update(kwargs)
        return base

    def test_form_valido(self):
        """Formulario válido con todos los campos completos."""
        form = MedicamentoForm(data=self._datos_validos())
        self.assertTrue(form.is_valid())

    def test_form_sin_nombre_comercial(self):
        """Formulario inválido si falta nombre_comercial."""
        form = MedicamentoForm(data=self._datos_validos(nombre_comercial=''))
        self.assertFalse(form.is_valid())
        self.assertIn('nombre_comercial', form.errors)

    def test_form_sin_nombre_farmacologico(self):
        """Formulario inválido si falta nombre_farmacologico."""
        form = MedicamentoForm(data=self._datos_validos(nombre_farmacologico=''))
        self.assertFalse(form.is_valid())
        self.assertIn('nombre_farmacologico', form.errors)

    def test_form_sin_componentes(self):
        """Formulario inválido si falta componentes."""
        form = MedicamentoForm(data=self._datos_validos(componentes=''))
        self.assertFalse(form.is_valid())
        self.assertIn('componentes', form.errors)

    def test_form_sin_laboratorio(self):
        """Formulario inválido si no se selecciona laboratorio."""
        datos = self._datos_validos()
        datos.pop('laboratorio')
        form = MedicamentoForm(data=datos)
        self.assertFalse(form.is_valid())
        self.assertIn('laboratorio', form.errors)

    def test_form_laboratorio_inexistente(self):
        """Formulario inválido si el laboratorio no existe en la BD."""
        form = MedicamentoForm(data=self._datos_validos(laboratorio=9999))
        self.assertFalse(form.is_valid())
        self.assertIn('laboratorio', form.errors)

    def test_form_nombre_comercial_max_length(self):
        """Formulario inválido si nombre_comercial supera 100 caracteres."""
        form = MedicamentoForm(data=self._datos_validos(nombre_comercial='A' * 101))
        self.assertFalse(form.is_valid())
        self.assertIn('nombre_comercial', form.errors)

    def test_form_guarda_instancia(self):
        """form.save() crea un registro de Medicamento en la base de datos."""
        form = MedicamentoForm(data=self._datos_validos())
        self.assertTrue(form.is_valid())
        med = form.save()
        self.assertEqual(med.nombre_comercial, 'Paracetamol')
        self.assertTrue(Medicamento.objects.filter(nombre_comercial='Paracetamol').exists())

    def test_form_actualiza_instancia(self):
        """form.save() con instance actualiza el medicamento existente."""
        med = Medicamento.objects.create(
            nombre_comercial='Viejo',
            nombre_farmacologico='Viejo Farm',
            componentes='Comp viejo',
            laboratorio=self.laboratorio
        )
        form = MedicamentoForm(
            data=self._datos_validos(nombre_comercial='Nuevo'),
            instance=med
        )
        self.assertTrue(form.is_valid())
        form.save()
        med.refresh_from_db()
        self.assertEqual(med.nombre_comercial, 'Nuevo')
