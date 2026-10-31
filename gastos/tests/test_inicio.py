from django.test import TestCase


class InicioTests(TestCase):
    def test_inicio_responde(self):
        respuesta = self.client.get("/")
        self.assertEqual(respuesta.status_code, 200)