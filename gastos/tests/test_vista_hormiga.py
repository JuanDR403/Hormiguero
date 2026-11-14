from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from gastos.models import Gasto

Usuario = get_user_model()
URL_HORMIGA = "/hormiga/"
AVISO_SIN_GRUPOS = "No se detectaron gastos hormiga en los últimos 30 días."


class VistaHormigaTests(TestCase):
    def setUp(self):
        self.hoy = timezone.localdate()
        self.ana = Usuario.objects.create_user("ana@ejemplo.com", password="clave-de-ejemplo-1")
        self.beto = Usuario.objects.create_user("beto@ejemplo.com", password="clave-de-ejemplo-2")

    def crear_gasto(self, usuario, **campos):
        datos = {
            "monto": 4000,
            "fecha": self.hoy,
            "categoria": Gasto.Categoria.ALIMENTACION,
            "descripcion": "Tinto",
            **campos,
        }
        return Gasto.objects.create(usuario=usuario, **datos)

    def crear_gastos(self, usuario, cantidad, **campos):
        for _ in range(cantidad):
            self.crear_gasto(usuario, **campos)

    def ver_como_ana(self):
        self.client.force_login(self.ana)
        return self.client.get(URL_HORMIGA)

    # CA1 y CA2

    def test_sin_sesion_redirige_al_login(self):
        respuesta = self.client.get(URL_HORMIGA)
        self.assertRedirects(respuesta, f"/login/?next={URL_HORMIGA}")

    def test_con_sesion_usa_la_plantilla_hormiga(self):
        respuesta = self.ver_como_ana()
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "gastos/hormiga.html")

    # CA3

    def test_tres_tintos_forman_un_grupo_en_el_contexto(self):
        self.crear_gastos(self.ana, 3)
        respuesta = self.ver_como_ana()
        self.assertEqual(len(respuesta.context["grupos"]), 1)
        grupo = respuesta.context["grupos"][0]
        self.assertEqual(grupo["descripcion"], "tinto")
        self.assertEqual(grupo["categoria"], "alimentacion")
        self.assertEqual(grupo["categoria_nombre"], "Alimentación")
        self.assertEqual(grupo["cantidad"], 3)
        self.assertEqual(grupo["total"], 12000)

    def test_la_pagina_muestra_el_grupo(self):
        self.crear_gastos(self.ana, 3)
        respuesta = self.ver_como_ana()
        self.assertContains(respuesta, "tinto")
        self.assertContains(respuesta, "Alimentación")
        self.assertContains(respuesta, "$12.000")
        self.assertRegex(respuesta.content.decode(), r">\s*3\s*</td>")

    # CA4 y CA5: aislamiento

    def test_no_muestra_gastos_hormiga_de_otro_usuario(self):
        self.crear_gastos(self.beto, 3, descripcion="Galletas de Beto")
        respuesta = self.ver_como_ana()
        self.assertEqual(list(respuesta.context["grupos"]), [])
        self.assertContains(respuesta, AVISO_SIN_GRUPOS)
        self.assertNotContains(respuesta, "galletas de beto")

    def test_gastos_de_dos_usuarios_no_se_suman(self):
        self.crear_gastos(self.ana, 2)
        self.crear_gastos(self.beto, 1)

        respuesta_ana = self.ver_como_ana()
        self.assertEqual(list(respuesta_ana.context["grupos"]), [])

        self.client.force_login(self.beto)
        respuesta_beto = self.client.get(URL_HORMIGA)
        self.assertEqual(list(respuesta_beto.context["grupos"]), [])

    # CA6

    def test_sin_gastos_muestra_el_aviso(self):
        respuesta = self.ver_como_ana()
        self.assertContains(respuesta, AVISO_SIN_GRUPOS)
        self.assertNotContains(respuesta, "<table")

    def test_gastos_que_no_llegan_a_n_muestran_el_aviso(self):
        self.crear_gastos(self.ana, 2)
        respuesta = self.ver_como_ana()
        self.assertContains(respuesta, AVISO_SIN_GRUPOS)
        self.assertNotContains(respuesta, "<table")

    # CA7

    @override_settings(GASTO_HORMIGA_N=2)
    def test_usa_n_de_settings(self):
        self.crear_gastos(self.ana, 2)
        respuesta = self.ver_como_ana()
        self.assertEqual(len(respuesta.context["grupos"]), 1)
        self.assertEqual(respuesta.context["grupos"][0]["cantidad"], 2)

    @override_settings(GASTO_HORMIGA_UMBRAL=3000)
    def test_usa_umbral_de_settings(self):
        self.crear_gastos(self.ana, 3)
        respuesta = self.ver_como_ana()
        self.assertEqual(list(respuesta.context["grupos"]), [])
        self.assertContains(respuesta, AVISO_SIN_GRUPOS)

    # CA8

    def test_gasto_de_hace_treinta_dias_cuenta(self):
        self.crear_gastos(self.ana, 2)
        self.crear_gasto(self.ana, fecha=self.hoy - timedelta(days=30))
        respuesta = self.ver_como_ana()
        self.assertEqual(len(respuesta.context["grupos"]), 1)
        self.assertEqual(respuesta.context["grupos"][0]["cantidad"], 3)

    def test_gasto_de_hace_treinta_y_un_dias_no_cuenta(self):
        self.crear_gastos(self.ana, 2)
        self.crear_gasto(self.ana, fecha=self.hoy - timedelta(days=31))
        respuesta = self.ver_como_ana()
        self.assertEqual(list(respuesta.context["grupos"]), [])

    def test_gasto_de_hoy_cuenta(self):
        self.crear_gastos(self.ana, 3, fecha=self.hoy)
        respuesta = self.ver_como_ana()
        self.assertEqual(len(respuesta.context["grupos"]), 1)

    # CA9

    def test_grupos_en_el_orden_de_la_regla(self):
        self.crear_gastos(self.ana, 3, descripcion="Pan")
        self.crear_gastos(self.ana, 4, descripcion="Tinto")
        respuesta = self.ver_como_ana()
        grupos = respuesta.context["grupos"]
        self.assertEqual([g["descripcion"] for g in grupos], ["tinto", "pan"])
        self.assertEqual([g["cantidad"] for g in grupos], [4, 3])
        html = respuesta.content.decode()
        self.assertIn("tinto", html)
        self.assertIn("pan", html)
        self.assertLess(html.index("tinto"), html.index("pan"))

    # CA10

    def test_grupo_sin_descripcion_se_muestra_como_sin_descripcion(self):
        self.crear_gastos(self.ana, 3, descripcion="")
        respuesta = self.ver_como_ana()
        self.assertEqual(len(respuesta.context["grupos"]), 1)
        self.assertContains(respuesta, "Sin descripción")

    # CA11

    def test_muestra_el_criterio_con_los_valores_por_defecto(self):
        respuesta = self.ver_como_ana()
        self.assertContains(respuesta, "$10.000")
        self.assertContains(respuesta, "3 o más veces")
        self.assertContains(respuesta, "30 días")
        self.assertEqual(respuesta.context["umbral"], 10000)
        self.assertEqual(respuesta.context["n"], 3)
        self.assertEqual(respuesta.context["dias"], 30)

    @override_settings(GASTO_HORMIGA_UMBRAL=5000, GASTO_HORMIGA_N=4)
    def test_el_criterio_cambia_con_settings(self):
        respuesta = self.ver_como_ana()
        self.assertContains(respuesta, "$5.000")
        self.assertContains(respuesta, "4 o más veces")
        self.assertEqual(respuesta.context["umbral"], 5000)
        self.assertEqual(respuesta.context["n"], 4)

    # CA12

    def test_encabezado_tiene_enlace_a_hormiga_con_sesion(self):
        self.client.force_login(self.ana)
        respuesta = self.client.get("/gastos/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertRegex(
            respuesta.content.decode(),
            r'<a href="/hormiga/">\s*Gasto hormiga\s*</a>',
        )

    def test_encabezado_sin_sesion_no_tiene_enlace_a_hormiga(self):
        respuesta = self.client.get("/login/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotContains(respuesta, 'href="/hormiga/"')
        self.assertNotContains(respuesta, "Gasto hormiga")

    # CA13

    def test_tabla_accesible_y_un_solo_h1(self):
        self.crear_gastos(self.ana, 3)
        respuesta = self.ver_como_ana()
        self.assertContains(respuesta, "<h1", count=1)
        self.assertContains(respuesta, "Gasto hormiga")
        self.assertContains(respuesta, '<th scope="col"', count=4)

    # CA14

    def test_head_esta_permitido(self):
        self.client.force_login(self.ana)
        respuesta = self.client.head(URL_HORMIGA)
        self.assertEqual(respuesta.status_code, 200)

    def test_post_no_esta_permitido(self):
        self.crear_gastos(self.ana, 3)
        self.client.force_login(self.ana)
        respuesta = self.client.post(URL_HORMIGA)
        self.assertEqual(respuesta.status_code, 405)
        self.assertEqual(Gasto.objects.filter(usuario=self.ana).count(), 3)
