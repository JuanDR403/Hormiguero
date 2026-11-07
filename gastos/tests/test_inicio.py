from django.contrib.auth import get_user_model
from django.test import TestCase

Usuario = get_user_model()


class InicioTests(TestCase):
    def test_inicio_responde(self):
        respuesta = self.client.get("/")
        self.assertEqual(respuesta.status_code, 200)

    def test_inicio_usa_la_plantilla_base(self):
        respuesta = self.client.get("/")
        self.assertTemplateUsed(respuesta, "base.html")
        self.assertContains(respuesta, 'name="viewport"')
        self.assertContains(respuesta, "<main")

    def test_con_sesion_enlaza_a_gastos(self):
        usuario = Usuario.objects.create_user("ana@ejemplo.com", first_name="Ana")
        self.client.force_login(usuario)
        respuesta = self.client.get("/")
        self.assertContains(respuesta, 'href="/gastos/"')

    def test_sin_sesion_no_enlaza_a_gastos(self):
        respuesta = self.client.get("/")
        self.assertNotContains(respuesta, 'href="/gastos/"')
