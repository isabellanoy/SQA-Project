from django.test import TestCase
from django.contrib.auth.models import User


class UsuarioModelTest(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username='testuser',
            password='password123'
        )

    def test_crear_usuario(self):
        """Se crea un usuario con username y contraseña correctos."""
        self.assertEqual(self.usuario.username, 'testuser')
        self.assertTrue(self.usuario.check_password('password123'))

    def test_contrasena_hasheada(self):
        """La contraseña se almacena hasheada, no en texto plano."""
        self.assertNotEqual(self.usuario.password, 'password123')

    def test_usuario_persiste_en_bd(self):
        """El usuario creado en setUp se encuentra en la base de datos."""
        usuario_db = User.objects.get(username='testuser')
        self.assertEqual(usuario_db.username, 'testuser')

    def test_username_unico(self):
        """No se pueden crear dos usuarios con el mismo username."""
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            User.objects.create_user(username='testuser', password='otrapass')

    def test_str_usuario(self):
        """__str__ del User retorna el username."""
        self.assertEqual(str(self.usuario), 'testuser')

    def test_usuario_activo_por_defecto(self):
        """Un usuario creado con create_user está activo por defecto."""
        self.assertTrue(self.usuario.is_active)

    def test_usuario_no_es_staff_por_defecto(self):
        """Un usuario creado con create_user no es staff por defecto."""
        self.assertFalse(self.usuario.is_staff)
