"""
Pruebas de Integración — ProyectoSoftwareFinal

A diferencia de las pruebas unitarias, estas pruebas verifican que múltiples
componentes (modelo + formulario + controlador + base de datos) funcionan
correctamente juntos, simulando flujos reales de usuario de principio a fin.

No se usa ningún mock: todas las operaciones tocan la base de datos en memoria
y pasan por la pila completa de Django (URL → vista → modelo → BD → respuesta).
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from Modelo.ModeloLaboratorio.Laboratorios.models import Laboratorios
from Modelo.ModeloMedicamentos.Medicamentos.models import Medicamento
from Modelo.ModeloFarmacia.Farmacias.models import Farmacia


# ---------------------------------------------------------------------------
# Flujo completo de Medicamento
# ---------------------------------------------------------------------------

class MedicamentoCRUDIntegrationTest(TestCase):
    """
    Verifica el ciclo completo Crear → Listar → Editar → Eliminar de un
    Medicamento, pasando por las vistas reales en cada paso.
    """

    def setUp(self):
        self.laboratorio = Laboratorios.objects.create(
            nombre='Lab Integración',
            direccion='Calle Test 1'
        )

    def test_ciclo_completo_medicamento(self):
        """Crear → verificar en lista → editar → verificar cambio → eliminar → verificar ausencia."""

        # 1. Registrar medicamento vía POST
        response = self.client.post(reverse('registrar_medicamento'), {
            'nombre_comercial': 'Aspirina',
            'nombre_farmacologico': 'Acido Acetilsalicilico',
            'componentes': 'Acido acetilsalicilico 500mg',
            'laboratorio': self.laboratorio.pk,
        })
        self.assertRedirects(response, reverse('lista_medicamentos'))

        # 2. Verificar que el medicamento existe en BD
        self.assertTrue(Medicamento.objects.filter(nombre_comercial='Aspirina').exists())
        medicamento = Medicamento.objects.get(nombre_comercial='Aspirina')

        # 3. Verificar que aparece en la lista (GET)
        response = self.client.get(reverse('lista_medicamentos'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(medicamento, response.context['medicamentos'])

        # 4. Editar el medicamento vía POST
        response = self.client.post(
            reverse('editar_medicamento', args=[medicamento.pk]), {
                'nombre_comercial': 'Aspirina Forte',
                'nombre_farmacologico': 'Acido Acetilsalicilico',
                'componentes': 'Acido acetilsalicilico 1000mg',
                'laboratorio': self.laboratorio.pk,
            }
        )
        self.assertRedirects(response, reverse('lista_medicamentos'))

        # 5. Verificar que el cambio se guardó en BD
        medicamento.refresh_from_db()
        self.assertEqual(medicamento.nombre_comercial, 'Aspirina Forte')
        self.assertEqual(medicamento.componentes, 'Acido acetilsalicilico 1000mg')

        # 6. Eliminar el medicamento vía POST
        response = self.client.post(
            reverse('eliminar_medicamento', args=[medicamento.pk])
        )
        self.assertRedirects(response, reverse('lista_medicamentos'))

        # 7. Verificar que ya no existe en BD ni en la lista
        self.assertFalse(Medicamento.objects.filter(pk=medicamento.pk).exists())
        response = self.client.get(reverse('lista_medicamentos'))
        self.assertNotIn(medicamento, response.context['medicamentos'])

    def test_registrar_medicamento_invalido_no_persiste(self):
        """Un POST inválido no debe crear ningún medicamento en la BD."""
        count_antes = Medicamento.objects.count()
        self.client.post(reverse('registrar_medicamento'), {
            'nombre_comercial': '',   # campo requerido vacío
            'nombre_farmacologico': '',
            'componentes': '',
        })
        self.assertEqual(Medicamento.objects.count(), count_antes)


# ---------------------------------------------------------------------------
# Flujo completo de Laboratorio
# ---------------------------------------------------------------------------

class LaboratorioCRUDIntegrationTest(TestCase):
    """
    Verifica el ciclo Crear → Modificar de Laboratorio, y que el historial
    refleja correctamente los medicamentos y farmacias asociados.
    """

    def test_ciclo_completo_laboratorio(self):
        """Crear laboratorio vía POST → modificar → verificar cambio en BD."""

        # 1. Crear laboratorio vía POST
        response = self.client.post(reverse('crear_labs'), {
            'nombre': 'Bayer',
            'direccion': 'Av. Principal 100',
        })
        self.assertRedirects(response, '/labs/', fetch_redirect_response=False)
        self.assertTrue(Laboratorios.objects.filter(nombre='Bayer').exists())
        lab = Laboratorios.objects.get(nombre='Bayer')

        # 2. Verificar que aparece en la lista de laboratorios (GET)
        response = self.client.get(reverse('labs'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(lab, response.context['laboratorio'])

        # 3. Modificar el laboratorio vía POST
        response = self.client.post(
            reverse('modificar_labs', args=[lab.pk]), {
                'nombre': 'Bayer Colombia',
                'direccion': 'Av. Principal 200',
            }
        )
        self.assertRedirects(response, reverse('labs'))

        # 4. Verificar el cambio en BD
        lab.refresh_from_db()
        self.assertEqual(lab.nombre, 'Bayer Colombia')
        self.assertEqual(lab.direccion, 'Av. Principal 200')

    def test_historial_refleja_medicamentos_y_farmacias(self):
        """
        El historial de un laboratorio debe mostrar todos sus medicamentos
        y farmacias asociados creados de forma independiente.
        """
        lab = Laboratorios.objects.create(nombre='Pfizer', direccion='Zona Norte')

        # Crear medicamento asociado al laboratorio
        med = Medicamento.objects.create(
            nombre_comercial='Ibuprofeno',
            nombre_farmacologico='Ibuprofeno',
            componentes='Ibuprofeno 400mg',
            laboratorio=lab
        )

        # Crear farmacia asociada al laboratorio
        farmacia = Farmacia.objects.create(nombre='Farmacia Norte', direccion='Calle 1')
        farmacia.laboratorios.add(lab)

        # Consultar el historial vía GET
        response = self.client.get(reverse('historial_labs', args=[lab.pk]))
        self.assertEqual(response.status_code, 200)

        # Verificar que el contexto contiene el medicamento y la farmacia
        self.assertIn(med, response.context['medicamentos'])
        self.assertIn(farmacia, response.context['farmacias'])

    def test_historial_laboratorio_sin_asociaciones(self):
        """El historial de un laboratorio nuevo muestra listas vacías."""
        lab = Laboratorios.objects.create(nombre='Lab Nuevo', direccion='Calle 5')
        response = self.client.get(reverse('historial_labs', args=[lab.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['medicamentos'].count(), 0)
        self.assertEqual(response.context['farmacias'].count(), 0)


# ---------------------------------------------------------------------------
# Flujo completo de Farmacia
# ---------------------------------------------------------------------------

class FarmaciaCRUDIntegrationTest(TestCase):
    """
    Verifica el ciclo Crear → Listar (con distintos órdenes) → Modificar
    de Farmacia, incluyendo la relación ManyToMany con Laboratorios.
    """

    def setUp(self):
        self.lab1 = Laboratorios.objects.create(nombre='Novartis', direccion='Sector A')
        self.lab2 = Laboratorios.objects.create(nombre='Roche', direccion='Sector B')

    def test_ciclo_completo_farmacia(self):
        """Registrar farmacia vía POST → verificar en lista → modificar → verificar cambio."""

        # 1. Registrar farmacia vía POST
        response = self.client.post(reverse('agregar_farmacia'), {
            'nombre': 'Droguería Central',
            'direccion': 'Calle 10',
            'laboratorios': [self.lab1.pk],
        })
        self.assertRedirects(response, reverse('lista_farmacias'))

        # 2. Verificar en BD con relación M2M correcta
        self.assertTrue(Farmacia.objects.filter(nombre='Droguería Central').exists())
        farmacia = Farmacia.objects.get(nombre='Droguería Central')
        self.assertIn(self.lab1, farmacia.laboratorios.all())

        # 3. Verificar que aparece en la lista (GET)
        response = self.client.get(reverse('lista_farmacias'))
        self.assertIn(farmacia, response.context['farmacias'])

        # 4. Modificar la farmacia (cambiar nombre y agregar segundo laboratorio)
        response = self.client.post(
            reverse('modificar_farmacia', args=[farmacia.pk]), {
                'nombre': 'Droguería Norte',
                'direccion': 'Calle 20',
                'laboratorios': [self.lab1.pk, self.lab2.pk],
            }
        )
        self.assertRedirects(response, reverse('lista_farmacias'))

        # 5. Verificar cambios en BD
        farmacia.refresh_from_db()
        self.assertEqual(farmacia.nombre, 'Droguería Norte')
        self.assertEqual(farmacia.laboratorios.count(), 2)
        self.assertIn(self.lab2, farmacia.laboratorios.all())

    def test_lista_farmacias_tres_ordenes(self):
        """
        La lista de farmacias debe ordenarse correctamente con los tres
        parámetros de orden disponibles.
        """
        Farmacia.objects.create(nombre='Zebra Farmacia', direccion='Dir Z')
        Farmacia.objects.create(nombre='Alfa Farmacia', direccion='Dir A')
        Farmacia.objects.create(nombre='Medio Farmacia', direccion='Dir M')

        # Orden alfabético: primera debe ser 'Alfa Farmacia'
        response = self.client.get(reverse('lista_farmacias') + '?orden=alfabetico')
        farmacias = list(response.context['farmacias'])
        self.assertEqual(farmacias[0].nombre, 'Alfa Farmacia')
        self.assertEqual(farmacias[-1].nombre, 'Zebra Farmacia')

        # Orden reciente: primera debe ser la última creada
        ultima = Farmacia.objects.order_by('-id').first()
        response = self.client.get(reverse('lista_farmacias') + '?orden=reciente')
        farmacias = list(response.context['farmacias'])
        self.assertEqual(farmacias[0].pk, ultima.pk)

        # Sin orden: retorna todas las farmacias
        response = self.client.get(reverse('lista_farmacias'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['farmacias']), 3)


# ---------------------------------------------------------------------------
# Relaciones entre entidades
# ---------------------------------------------------------------------------

class RelacionesEntidadesIntegrationTest(TestCase):
    """
    Verifica que las relaciones entre Laboratorio, Medicamento y Farmacia
    se comportan correctamente de extremo a extremo.
    """

    def test_eliminacion_laboratorio_elimina_medicamentos_en_cascada(self):
        """
        Al eliminar un laboratorio desde la BD, sus medicamentos deben
        eliminarse automáticamente (on_delete=CASCADE) y no aparecer en lista.
        """
        lab = Laboratorios.objects.create(nombre='Lab Cascada', direccion='Calle 1')
        med1 = Medicamento.objects.create(
            nombre_comercial='MedA', nombre_farmacologico='FarmA',
            componentes='CompA', laboratorio=lab
        )
        med2 = Medicamento.objects.create(
            nombre_comercial='MedB', nombre_farmacologico='FarmB',
            componentes='CompB', laboratorio=lab
        )

        # Verificar que los medicamentos aparecen en la lista
        response = self.client.get(reverse('lista_medicamentos'))
        self.assertIn(med1, response.context['medicamentos'])
        self.assertIn(med2, response.context['medicamentos'])

        # Eliminar el laboratorio (CASCADE)
        lab.delete()

        # Verificar que los medicamentos ya no existen en BD
        self.assertFalse(Medicamento.objects.filter(pk=med1.pk).exists())
        self.assertFalse(Medicamento.objects.filter(pk=med2.pk).exists())

        # Verificar que la lista de medicamentos está vacía
        response = self.client.get(reverse('lista_medicamentos'))
        self.assertEqual(response.context['medicamentos'].count(), 0)

    def test_farmacia_visible_en_historial_de_sus_laboratorios(self):
        """
        Una farmacia asociada a dos laboratorios debe aparecer en el
        historial de ambos.
        """
        lab1 = Laboratorios.objects.create(nombre='Lab X', direccion='Dir X')
        lab2 = Laboratorios.objects.create(nombre='Lab Y', direccion='Dir Y')

        farmacia = Farmacia.objects.create(nombre='Farmacia Doble', direccion='Centro')
        farmacia.laboratorios.add(lab1, lab2)

        # Historial de lab1
        response = self.client.get(reverse('historial_labs', args=[lab1.pk]))
        self.assertIn(farmacia, response.context['farmacias'])

        # Historial de lab2
        response = self.client.get(reverse('historial_labs', args=[lab2.pk]))
        self.assertIn(farmacia, response.context['farmacias'])

    def test_lista_farmacias_incluye_contexto_completo(self):
        """
        La vista de lista de farmacias debe entregar laboratorios y
        medicamentos en el contexto (usados para filtros en el template).
        """
        lab = Laboratorios.objects.create(nombre='Lab Contexto', direccion='Av. 1')
        Medicamento.objects.create(
            nombre_comercial='MedContexto', nombre_farmacologico='Farm',
            componentes='Comp', laboratorio=lab
        )
        farmacia = Farmacia.objects.create(nombre='Farm Contexto', direccion='Calle 2')
        farmacia.laboratorios.add(lab)

        response = self.client.get(reverse('lista_farmacias'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(lab, response.context['laboratorios'])
        self.assertIn(farmacia, response.context['farmacias'])


# ---------------------------------------------------------------------------
# Flujo de autenticación
# ---------------------------------------------------------------------------

class AutenticacionIntegrationTest(TestCase):
    """
    Verifica el flujo completo de inicio de sesión, acceso a páginas
    protegidas y cierre de sesión.
    """

    def setUp(self):
        self.usuario = User.objects.create_user(
            username='integracion_user',
            password='clave_segura_123'
        )

    def test_flujo_signin_perfiles_signout(self):
        """
        Iniciar sesión → acceder a perfiles → cerrar sesión → verificar
        que la sesión fue destruida.
        """
        # 1. Iniciar sesión vía POST
        response = self.client.post(reverse('signin'), {
            'username': 'integracion_user',
            'password': 'clave_segura_123',
        })
        self.assertRedirects(response, reverse('perfiles'))

        # 2. Acceder a la página de perfiles (sesión activa)
        response = self.client.get(reverse('perfiles'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.usuario, response.context['users'])

        # 3. Cerrar sesión
        response = self.client.get(reverse('signout'))
        self.assertRedirects(response, reverse('home'))

        # 4. Verificar que la sesión fue destruida (usuario anónimo)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_credenciales_invalidas_no_autentican(self):
        """
        Un POST con contraseña incorrecta no debe iniciar sesión
        ni redirigir a perfiles.
        """
        response = self.client.post(reverse('signin'), {
            'username': 'integracion_user',
            'password': 'clave_incorrecta',
        })
        # Debe quedarse en la página de signin con error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usuario o contraseña incorrectas')
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_multiples_usuarios_visibles_en_perfiles(self):
        """
        Todos los usuarios registrados deben aparecer en la vista de perfiles.
        """
        User.objects.create_user(username='usuario2', password='clave2')
        User.objects.create_user(username='usuario3', password='clave3')

        response = self.client.get(reverse('perfiles'))
        self.assertEqual(response.status_code, 200)
        # El contexto debe incluir todos los usuarios (el de setUp + los 2 nuevos)
        self.assertEqual(response.context['users'].count(), 3)
