from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from django.contrib.auth.models import User
from django.db import IntegrityError

from Modelo.ModeloLaboratorio.Laboratorios.models import Laboratorios
from Modelo.ModeloMedicamentos.Medicamentos.models import Medicamento
from Modelo.ModeloFarmacia.Farmacias.models import Farmacia


# ---------------------------------------------------------------------------
# PerfilController
# ---------------------------------------------------------------------------

class PerfilControllerTest(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username='usuarioexistente',
            password='clave1234'
        )

    def test_home_get(self):
        """GET / retorna 200."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_signup_get(self):
        """GET /signup/ retorna 200 con el formulario."""
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('formUser', response.context)

    def test_signup_post_contrasenas_no_coinciden(self):
        """POST en /signup/ con contraseñas distintas muestra error."""
        response = self.client.post(reverse('signup'), {
            'username': 'nuevo',
            'password1': 'clave1234',
            'password2': 'clave_diferente',
            'alergia': 'ninguna',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'contraseñas no coinciden')

    @patch('Controlador.ControladorUsuario.PerfilController.User.objects.create_user')
    def test_signup_post_exitoso(self, mock_create):
        """POST en /signup/ con datos válidos crea usuario y redirige."""
        # self.usuario se crea en setUp, ANTES de que el mock esté activo
        mock_create.return_value = self.usuario
        response = self.client.post(reverse('signup'), {
            'username': 'nuevousuario',
            'password1': 'clave1234',
            'password2': 'clave1234',
            'alergia': 'ninguna',
        })
        self.assertRedirects(response, reverse('perfiles'))

    @patch('Controlador.ControladorUsuario.PerfilController.User.objects.create_user')
    def test_signup_post_usuario_duplicado(self, mock_create):
        """POST en /signup/ con usuario existente muestra error."""
        mock_create.side_effect = IntegrityError
        response = self.client.post(reverse('signup'), {
            'username': 'usuarioexistente',
            'password1': 'clave1234',
            'password2': 'clave1234',
            'alergia': 'ninguna',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'usuario ya existe')

    def test_perfiles_get(self):
        """GET /perfiles/ retorna 200 con lista de usuarios."""
        response = self.client.get(reverse('perfiles'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('users', response.context)

    def test_signin_get(self):
        """GET /signin/ retorna 200 con el formulario de autenticación."""
        response = self.client.get(reverse('signin'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_signin_post_credenciales_validas(self):
        """POST en /signin/ con credenciales correctas redirige a /perfiles/."""
        response = self.client.post(reverse('signin'), {
            'username': 'usuarioexistente',
            'password': 'clave1234',
        })
        self.assertRedirects(response, reverse('perfiles'))

    def test_signin_post_credenciales_invalidas(self):
        """POST en /signin/ con credenciales incorrectas muestra error."""
        response = self.client.post(reverse('signin'), {
            'username': 'usuarioexistente',
            'password': 'clave_incorrecta',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usuario o contraseña incorrectas')

    def test_signout(self):
        """GET /logout/ cierra sesión y redirige a /."""
        self.client.login(username='usuarioexistente', password='clave1234')
        response = self.client.get(reverse('signout'))
        self.assertRedirects(response, reverse('home'))


# ---------------------------------------------------------------------------
# MedicamentoController
# ---------------------------------------------------------------------------

class MedicamentoControllerTest(TestCase):

    def setUp(self):
        self.laboratorio = Laboratorios.objects.create(
            nombre='Lab Prueba',
            direccion='Calle 99'
        )
        self.medicamento = Medicamento.objects.create(
            nombre_comercial='Ibuprofeno',
            nombre_farmacologico='Ibuprofeno',
            componentes='Ibuprofeno 400mg',
            laboratorio=self.laboratorio
        )

    def test_lista_medicamentos_get(self):
        """GET /lista/ retorna 200 con la lista de medicamentos en el contexto."""
        response = self.client.get(reverse('lista_medicamentos'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('medicamentos', response.context)

    def test_registrar_medicamento_get(self):
        """GET /registrar/ retorna 200 con el formulario vacío."""
        response = self.client.get(reverse('registrar_medicamento'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_registrar_medicamento_post_valido(self):
        """POST válido en /registrar/ crea medicamento y redirige a la lista."""
        data = {
            'nombre_comercial': 'Nuevo Med',
            'nombre_farmacologico': 'Nuevo Farmacologico',
            'componentes': 'Componente X 500mg',
            'laboratorio': self.laboratorio.pk,
        }
        response = self.client.post(reverse('registrar_medicamento'), data)
        self.assertRedirects(response, reverse('lista_medicamentos'))
        self.assertTrue(Medicamento.objects.filter(nombre_comercial='Nuevo Med').exists())

    def test_registrar_medicamento_post_invalido(self):
        """POST sin datos en /registrar/ muestra el formulario con errores."""
        response = self.client.post(reverse('registrar_medicamento'), {})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_editar_medicamento_get(self):
        """GET /editar/<id>/ retorna 200 con el medicamento precargado."""
        response = self.client.get(
            reverse('editar_medicamento', args=[self.medicamento.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('medicamento', response.context)

    def test_editar_medicamento_get_404(self):
        """GET /editar/<id_inexistente>/ retorna 404."""
        response = self.client.get(
            reverse('editar_medicamento', args=[9999])
        )
        self.assertEqual(response.status_code, 404)

    def test_editar_medicamento_post_valido(self):
        """POST válido en /editar/<id>/ actualiza medicamento y redirige."""
        data = {
            'nombre_comercial': 'Ibuprofeno Modificado',
            'nombre_farmacologico': 'Ibuprofeno',
            'componentes': 'Ibuprofeno 600mg',
            'laboratorio': self.laboratorio.pk,
        }
        response = self.client.post(
            reverse('editar_medicamento', args=[self.medicamento.pk]), data
        )
        self.assertRedirects(response, reverse('lista_medicamentos'))
        self.medicamento.refresh_from_db()
        self.assertEqual(self.medicamento.nombre_comercial, 'Ibuprofeno Modificado')

    def test_eliminar_medicamento_get(self):
        """GET /eliminar/<id>/ retorna 200 con la página de confirmación."""
        response = self.client.get(
            reverse('eliminar_medicamento', args=[self.medicamento.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('medicamento', response.context)

    def test_eliminar_medicamento_post(self):
        """POST en /eliminar/<id>/ elimina el medicamento y redirige."""
        response = self.client.post(
            reverse('eliminar_medicamento', args=[self.medicamento.pk])
        )
        self.assertRedirects(response, reverse('lista_medicamentos'))
        self.assertFalse(
            Medicamento.objects.filter(pk=self.medicamento.pk).exists()
        )


# ---------------------------------------------------------------------------
# LaboratorioController
# ---------------------------------------------------------------------------

class LaboratorioControllerTest(TestCase):

    def setUp(self):
        self.laboratorio = Laboratorios.objects.create(
            nombre='Lab Central',
            direccion='Av. Central 5'
        )

    def test_labs_get(self):
        """GET /labs/ retorna 200 con la lista de laboratorios en el contexto."""
        response = self.client.get(reverse('labs'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('laboratorio', response.context)

    def test_crear_labs_get(self):
        """GET /crear_labs/ retorna 200 con el formulario vacío."""
        response = self.client.get(reverse('crear_labs'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_crear_labs_post_valido(self):
        """POST válido en /crear_labs/ crea laboratorio y redirige a /labs/."""
        data = {'nombre': 'Nuevo Lab', 'direccion': 'Calle 200'}
        response = self.client.post(reverse('crear_labs'), data)
        self.assertRedirects(response, '/labs/', fetch_redirect_response=False)
        self.assertTrue(Laboratorios.objects.filter(nombre='Nuevo Lab').exists())

    def test_modificar_labs_get(self):
        """GET /modificar_labs/<id>/ retorna 200 con el formulario precargado."""
        response = self.client.get(
            reverse('modificar_labs', args=[self.laboratorio.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_modificar_labs_get_404(self):
        """GET /modificar_labs/<id_inexistente>/ retorna 404."""
        response = self.client.get(reverse('modificar_labs', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_modificar_labs_post_valido(self):
        """POST válido en /modificar_labs/<id>/ actualiza y redirige a labs."""
        data = {'nombre': 'Lab Modificado', 'direccion': 'Nueva Dirección 10'}
        response = self.client.post(
            reverse('modificar_labs', args=[self.laboratorio.pk]), data
        )
        self.assertRedirects(response, reverse('labs'))
        self.laboratorio.refresh_from_db()
        self.assertEqual(self.laboratorio.nombre, 'Lab Modificado')

    def test_ver_historial(self):
        """GET /ver_historial/<id>/ retorna 200 con medicamentos y farmacias."""
        response = self.client.get(
            reverse('historial_labs', args=[self.laboratorio.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('laboratorio', response.context)
        self.assertIn('medicamentos', response.context)
        self.assertIn('farmacias', response.context)

    def test_ver_historial_404(self):
        """GET /ver_historial/<id_inexistente>/ retorna 404."""
        response = self.client.get(reverse('historial_labs', args=[9999]))
        self.assertEqual(response.status_code, 404)


# ---------------------------------------------------------------------------
# FarmaciaController
# ---------------------------------------------------------------------------

class FarmaciaControllerTest(TestCase):

    def setUp(self):
        self.laboratorio = Laboratorios.objects.create(
            nombre='Lab Farmacia',
            direccion='Sector Norte'
        )
        self.farmacia = Farmacia.objects.create(
            nombre='Droguería Central',
            direccion='Calle 45'
        )
        self.farmacia.laboratorios.add(self.laboratorio)

    def test_lista_farmacias_get(self):
        """GET /lista_farm/ retorna 200 con farmacias, laboratorios y medicamentos."""
        response = self.client.get(reverse('lista_farmacias'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('farmacias', response.context)
        self.assertIn('laboratorios', response.context)
        self.assertIn('medicamentos', response.context)

    def test_lista_farmacias_orden_alfabetico(self):
        """GET /lista_farm/?orden=alfabetico ordena farmacias por nombre."""
        Farmacia.objects.create(nombre='AAA Farmacia', direccion='Calle 1')
        response = self.client.get(
            reverse('lista_farmacias') + '?orden=alfabetico'
        )
        self.assertEqual(response.status_code, 200)
        farmacias = list(response.context['farmacias'])
        self.assertEqual(farmacias[0].nombre, 'AAA Farmacia')

    def test_lista_farmacias_orden_reciente(self):
        """GET /lista_farm/?orden=reciente ordena farmacias por -id."""
        farmacia_nueva = Farmacia.objects.create(nombre='Última Farmacia', direccion='Calle 99')
        response = self.client.get(
            reverse('lista_farmacias') + '?orden=reciente'
        )
        self.assertEqual(response.status_code, 200)
        farmacias = list(response.context['farmacias'])
        self.assertEqual(farmacias[0].pk, farmacia_nueva.pk)

    def test_registrar_farmacia_get(self):
        """GET /registro_farm/ retorna 200 con el formulario vacío."""
        response = self.client.get(reverse('agregar_farmacia'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_registrar_farmacia_post_valido(self):
        """POST válido en /registro_farm/ crea farmacia y redirige a la lista."""
        data = {
            'nombre': 'Nueva Farmacia',
            'direccion': 'Carrera 10',
            'laboratorios': [self.laboratorio.pk],
        }
        response = self.client.post(reverse('agregar_farmacia'), data)
        self.assertRedirects(response, reverse('lista_farmacias'))
        self.assertTrue(Farmacia.objects.filter(nombre='Nueva Farmacia').exists())

    def test_registrar_farmacia_post_invalido(self):
        """POST sin datos en /registro_farm/ muestra el formulario con errores."""
        response = self.client.post(reverse('agregar_farmacia'), {})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_modificar_farmacia_get(self):
        """GET /farmacias/modificar/<id>/ retorna 200 con el formulario precargado."""
        response = self.client.get(
            reverse('modificar_farmacia', args=[self.farmacia.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_modificar_farmacia_get_404(self):
        """GET /farmacias/modificar/<id_inexistente>/ retorna 404."""
        response = self.client.get(
            reverse('modificar_farmacia', args=[9999])
        )
        self.assertEqual(response.status_code, 404)

    def test_modificar_farmacia_post_valido(self):
        """POST válido en /farmacias/modificar/<id>/ actualiza farmacia y redirige."""
        data = {
            'nombre': 'Droguería Modificada',
            'direccion': 'Nueva Dirección',
            'laboratorios': [self.laboratorio.pk],
        }
        response = self.client.post(
            reverse('modificar_farmacia', args=[self.farmacia.pk]), data
        )
        self.assertRedirects(response, reverse('lista_farmacias'))
        self.farmacia.refresh_from_db()
        self.assertEqual(self.farmacia.nombre, 'Droguería Modificada')
