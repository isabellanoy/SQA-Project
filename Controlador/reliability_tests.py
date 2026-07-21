from django.test import TestCase
from django.urls import reverse
from Modelo.ModeloLaboratorio.Laboratorios.models import Laboratorios
from Modelo.ModeloMedicamentos.Medicamentos.models import Medicamento
from Modelo.ModeloFarmacia.Farmacias.models import Farmacia
from django.contrib.auth.models import User

class ReliabilityFiabilityTests(TestCase):
    def setUp(self):
        # Crear usuario para simular sesión si es requerida por los endpoints
        self.user = User.objects.create_user(username='tester', password='password123')
        self.client.login(username='tester', password='password123')
        
        # Datos iniciales para pruebas que requieran de registros existentes
        self.laboratorio = Laboratorios.objects.create(nombre="Lab Inicial", direccion="Calle Verdadera 123")
        self.medicamento = Medicamento.objects.create(
            nombre_comercial="Medicina Base", 
            nombre_farmacologico="Base",
            componentes="Ninguno",
            laboratorio=self.laboratorio
        )
        self.farmacia = Farmacia.objects.create(nombre="Farmacia Centro", direccion="Calle Verdadera 123")

    def test_valores_limites_extremos_desbordamiento(self):
        """
        Fiabilidad: Evalúa tolerancia a fallos ante entradas extremadamente grandes.
        Se envía un payload donde un campo string excede el límite máximo por miles de caracteres.
        El sistema no debe retornar HTTP 500 bajo ninguna circunstancia.
        """
        payload = {
            'nombre': 'A' * 5000,  # String desbordado
            'direccion': 'B' * 5000,
        }
        response = self.client.post(reverse('crear_labs'), data=payload)
        # El sistema debe manejarlo sin error de servidor (ej. retornando el formulario de nuevo o código 400)
        self.assertNotEqual(response.status_code, 500, "El servidor colapsó con código 500 al recibir un string desbordado.")
        self.assertTrue(response.status_code in [200, 302, 400], f"Código de estado inesperado: {response.status_code}")

    def test_tipos_datos_inesperados_fuzzing(self):
        """
        Fiabilidad: Evalúa tolerancia a inyecciones y tipos de datos inesperados.
        Se envían emojis, scripts básicos y valores booleanos como diccionario anidado.
        El objetivo es asegurar que la capa de formularios sanitiza o rechaza los datos.
        """
        payload = {
            'nombre': 'Farmacia 💊 <script>alert("hack")</script>',
            'direccion': {'invalido': True}, # Enviar diccionario donde se espera string
            'telefono': [1, 2, 3] # Enviar lista donde se espera string/numérico
        }
        response = self.client.post(reverse('agregar_farmacia'), data=payload)
        
        self.assertNotEqual(response.status_code, 500, "El servidor retornó error 500 ante tipos de datos complejos en el POST.")
        # Usualmente Django lo renderiza nuevamente con errores
        self.assertTrue(response.status_code in [200, 400], "El sistema no manejó cŕectamente los tipos de datos anómalos.")

    def test_violacion_integridad_referencial(self):
        """
        Fiabilidad: Asegura que el sistema no colapse si recibe IDs de ForeignKeys malformados o inválidos.
        Intentando crear un medicamento con un ID de laboratorio tipo string no numérico.
        """
        payload = {
            'nombre_med': 'Paracetamol',
            'descripcion_med': 'Para el dolor de cabeza',
            'precio_med': 15.50,
            'laboratorio': 'un_string_que_no_es_id' # ForeignKey inválida
        }
        response = self.client.post(reverse('registrar_medicamento'), data=payload)
        
        self.assertNotEqual(response.status_code, 500, "Falló el sistema (Error 500) por violación de tipo en llave foránea (ValueError).")
        # El formulario debe detectar la falla en validación y retornar la página con errores
        self.assertIn(response.status_code, [200, 400], "La ruta no manejó el error de tipo de llave foránea.")

    def test_metodos_http_no_permitidos(self):
        """
        Fiabilidad: Integridad ante solicitudes inapropiadas.
        Se intenta acceder a rutas destructivas con métodos inadecuados o peticiones de solo lectura con mutaciones fallidas.
        En este caso una solicitud DELETE (si permitida) o GET normal hacia una ruta de eliminación directamente.
        """
        # Muchas veces GET en 'eliminar_medicamento' debe mostrar pantalla de confirmación, 
        # pero enviaremos POST a una vista que no espera payload o viceversa si es posible.
        
        # Enviar petición POST vacía a una ruta de solo lectura
        response_post = self.client.post(reverse('lista_medicamentos'), data={})
        # Dependiendo del controlador, puede regresar 200 (si lo trata como GET) o 405 (Method Not Allowed)
        self.assertNotEqual(response_post.status_code, 500, "Ruta de lectura colapsó al recibir una solicitud POST.")

        # Intentar enviar datos putheando form o usando metodos raros
        response_put = self.client.put(reverse('editar_medicamento', args=[self.medicamento.id]), data={'nombre_med': 'Test'})
        self.assertNotEqual(response_put.status_code, 500)

    def test_carga_util_incompleta_o_vacia(self):
        """
        Fiabilidad: Evalúa la capacidad del backend para manejar requests vacías o sin parámetros obligatorios.
        Esto puede causar KeyError en controladores no maduros.
        """
        # Petición a endpoint de creación totalmente vacía
        response_vacia = self.client.post(reverse('registrar_medicamento'), data={})
        
        self.assertNotEqual(response_vacia.status_code, 500, "El sistema colapsó (500) ante un QueryDict vacío, probable KeyError en el controlador.")
        # Debería retornar a la vista con formulario inválido (200) o un error de Bad Request (400)
        self.assertIn(response_vacia.status_code, [200, 400])