from django.contrib.auth import get_user_model
from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse

from gastos.reglas.usuarios import normalizar_correo

Usuario = get_user_model()
CONTRASENA = "hormiga-segura-2026"


def datos_registro(**cambios):
    return {
        "nombre_completo": "Ana Pérez",
        "correo": "ana@ejemplo.com",
        "contrasena": CONTRASENA,
        "confirmar_contrasena": CONTRASENA,
        **cambios,
    }


class NormalizarCorreoTests(SimpleTestCase):
    def test_quita_espacios_y_mayusculas(self):
        self.assertEqual(normalizar_correo("  Ana@Ejemplo.COM "), "ana@ejemplo.com")

    def test_correo_ya_normalizado_no_cambia(self):
        self.assertEqual(normalizar_correo("ana@ejemplo.com"), "ana@ejemplo.com")


class RegistroTests(TestCase):
    def registrar(self, **cambios):
        return self.client.post(reverse("registro"), datos_registro(**cambios))

    def test_pagina_en_espanol(self):
        respuesta = self.client.get(reverse("registro"))
        self.assertContains(respuesta, "Crear cuenta")
        self.assertContains(respuesta, "Confirmar contraseña")

    def test_crea_usuario_e_inicia_sesion(self):
        respuesta = self.registrar(correo="Ana@Ejemplo.com")
        self.assertRedirects(respuesta, reverse("inicio"))

        usuario = Usuario.objects.get(username="ana@ejemplo.com")
        self.assertEqual(usuario.first_name, "Ana Pérez")
        self.assertTrue(usuario.check_password(CONTRASENA))
        self.assertNotEqual(usuario.password, CONTRASENA)
        self.assertFalse(usuario.is_staff)
        self.assertEqual(int(self.client.session["_auth_user_id"]), usuario.pk)

    def test_contrasenas_distintas(self):
        respuesta = self.registrar(confirmar_contrasena="otra-clave-2026")
        self.assertContains(respuesta, "Las contraseñas no coinciden.")
        self.assertFalse(Usuario.objects.exists())

    def test_correo_duplicado_sin_distinguir_mayusculas(self):
        Usuario.objects.create_user("ana@ejemplo.com", password=CONTRASENA)
        respuesta = self.registrar(correo="ANA@ejemplo.com")
        self.assertContains(respuesta, "Ya existe una cuenta con este correo.")
        self.assertEqual(Usuario.objects.count(), 1)

    def test_contrasena_debil_rechazada_en_espanol(self):
        respuesta = self.registrar(contrasena="123", confirmar_contrasena="123")
        self.assertContains(respuesta, "contraseña")
        self.assertTrue(respuesta.context["formulario"].errors["contrasena"])
        self.assertFalse(Usuario.objects.exists())

    def test_correo_invalido(self):
        self.registrar(correo="no-es-correo")
        self.assertFalse(Usuario.objects.exists())

    def test_usuario_autenticado_es_redirigido(self):
        self.client.force_login(Usuario.objects.create_user("ana@ejemplo.com"))
        self.assertRedirects(self.client.get(reverse("registro")), reverse("inicio"))


class IngresoTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            "ana@ejemplo.com", email="ana@ejemplo.com", password=CONTRASENA, first_name="Ana"
        )

    def ingresar(self, correo="ana@ejemplo.com", contrasena=CONTRASENA, **extra):
        return self.client.post(
            reverse("login"), {"username": correo, "password": contrasena, **extra}
        )

    def test_pagina_en_espanol(self):
        respuesta = self.client.get(reverse("login"))
        self.assertContains(respuesta, "Iniciar sesión")
        self.assertContains(respuesta, "¿Olvidaste tu contraseña?")
        self.assertContains(respuesta, reverse("registro"))

    def test_credenciales_correctas(self):
        self.assertRedirects(self.ingresar(), reverse("inicio"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_correo_sin_distinguir_mayusculas(self):
        self.assertRedirects(self.ingresar(correo="ANA@Ejemplo.com"), reverse("inicio"))

    def test_error_generico_con_contrasena_o_correo_incorrectos(self):
        mensaje = "El correo o la contraseña son incorrectos."
        self.assertContains(self.ingresar(contrasena="mala"), mensaje)
        self.assertContains(self.ingresar(correo="otra@ejemplo.com"), mensaje)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_no_redirige_a_sitios_externos(self):
        respuesta = self.ingresar(next="https://malicioso.example/")
        self.assertRedirects(respuesta, reverse("inicio"))

    def test_login_exige_token_csrf(self):
        cliente = Client(enforce_csrf_checks=True)
        respuesta = cliente.post(
            reverse("login"), {"username": "ana@ejemplo.com", "password": CONTRASENA}
        )
        self.assertEqual(respuesta.status_code, 403)

    def test_usuario_autenticado_es_redirigido(self):
        self.client.force_login(self.usuario)
        self.assertRedirects(self.client.get(reverse("login")), reverse("inicio"))

    def test_inicio_saluda_al_usuario(self):
        self.client.force_login(self.usuario)
        self.assertContains(self.client.get(reverse("inicio")), "Hola, Ana.")

    def test_cerrar_sesion(self):
        self.client.force_login(self.usuario)
        self.assertRedirects(self.client.post(reverse("logout")), reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_cerrar_sesion_no_acepta_get(self):
        self.client.force_login(self.usuario)
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)
