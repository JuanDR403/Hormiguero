from datetime import date
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from gastos.models import Gasto

Usuario = get_user_model()
URL_INICIO = "/"
AVISO_SIN_GASTOS = "No tienes gastos registrados este mes."
ENLACE_HORMIGA = r'<a href="/hormiga/">\s*Ver gasto hormiga\s*</a>'


class VistaResumenTests(TestCase):
    def setUp(self):
        self.hoy = date(2026, 11, 14)
        parche = mock.patch("gastos.views.timezone.localdate", return_value=self.hoy)
        parche.start()
        self.addCleanup(parche.stop)
        self.ana = Usuario.objects.create_user(
            "ana@ejemplo.com", password="clave-de-ejemplo-1", first_name="Ana"
        )
        self.beto = Usuario.objects.create_user(
            "beto@ejemplo.com", password="clave-de-ejemplo-2", first_name="Beto"
        )

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

    def gastos_ca1(self, usuario):
        self.crear_gasto(usuario, fecha=date(2026, 11, 1), monto=5000, descripcion="a")
        self.crear_gasto(usuario, fecha=date(2026, 11, 14), monto=20000, descripcion="b")
        self.crear_gasto(usuario, fecha=date(2026, 10, 31), monto=100000, descripcion="c")

    def gastos_ca5(self, usuario):
        self.crear_gasto(usuario, monto=4000, categoria="alimentacion", descripcion="a")
        self.crear_gasto(usuario, monto=6000, categoria="alimentacion", descripcion="b")
        self.crear_gasto(usuario, monto=15000, categoria="transporte", descripcion="c")
        self.crear_gasto(usuario, monto=2000, categoria="hogar", descripcion="d")
        self.crear_gasto(
            usuario, monto=50000, categoria="salud", fecha=date(2026, 10, 20), descripcion="e"
        )

    def ver_como_ana(self):
        self.client.force_login(self.ana)
        return self.client.get(URL_INICIO)

    # CA9

    def test_sin_sesion_conserva_la_pagina_de_acceso(self):
        respuesta = self.client.get(URL_INICIO)
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "inicio.html")
        self.assertContains(respuesta, "Iniciar sesión")
        self.assertContains(respuesta, "Crear cuenta")
        self.assertNotContains(respuesta, "Resumen")

    def test_sin_sesion_muestra_h1_hormiguero_y_descripcion(self):
        html = self.client.get(URL_INICIO).content.decode()
        self.assertIn("<h1>Hormiguero</h1>", html)
        self.assertIn("Gestor de gastos personales con metas de ahorro.", html)

    def test_sin_sesion_el_titulo_de_la_pestana_es_inicio(self):
        respuesta = self.client.get(URL_INICIO)
        self.assertContains(respuesta, "<title>Inicio · Hormiguero</title>", html=False)

    def test_sin_sesion_el_contexto_no_trae_total_mes(self):
        respuesta = self.client.get(URL_INICIO)
        self.assertNotIn("total_mes", respuesta.context)

    # CA10

    def test_con_sesion_usa_inicio_con_h1_resumen_y_saludo(self):
        respuesta = self.ver_como_ana()
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "inicio.html")
        self.assertContains(respuesta, "<h1", count=1)
        self.assertRegex(respuesta.content.decode(), r"<h1[^>]*>\s*Resumen\s*</h1>")
        self.assertContains(respuesta, "Hola, Ana.")

    def test_con_sesion_el_titulo_de_la_pestana_es_resumen(self):
        respuesta = self.ver_como_ana()
        self.assertContains(respuesta, "<title>Resumen · Hormiguero</title>", html=False)

    # CA11

    def test_total_del_mes_en_contexto_y_en_la_pagina(self):
        self.gastos_ca1(self.ana)
        respuesta = self.ver_como_ana()
        self.assertEqual(respuesta.context["total_mes"], 25000)
        self.assertContains(respuesta, "$25.000")
        self.assertIn("noviembre de 2026", respuesta.content.decode())

    def test_el_contexto_trae_hoy_y_dias(self):
        respuesta = self.ver_como_ana()
        self.assertEqual(respuesta.context["hoy"], self.hoy)
        self.assertEqual(respuesta.context["dias"], 30)

    # CA12

    def test_gastos_de_otro_usuario_no_cuentan(self):
        self.crear_gasto(self.ana, monto=1000, categoria="hogar", descripcion="Luz")
        self.gastos_ca5(self.beto)
        self.crear_gastos(self.beto, 3, descripcion="Galletas")
        respuesta = self.ver_como_ana()
        self.assertEqual(respuesta.context["total_mes"], 1000)
        self.assertEqual(
            [c["categoria"] for c in respuesta.context["por_categoria"]], ["hogar"]
        )
        self.assertEqual(respuesta.context["cantidad_hormiga"], 0)
        self.assertNotContains(respuesta, "Transporte")
        self.assertNotContains(respuesta, "Alimentación")
        self.assertNotContains(respuesta, "Detectamos")

    # CA13

    def test_por_categoria_en_el_contexto_en_el_orden_de_la_regla(self):
        self.gastos_ca5(self.ana)
        respuesta = self.ver_como_ana()
        self.assertEqual(
            list(respuesta.context["por_categoria"]),
            [
                {"categoria": "transporte", "categoria_nombre": "Transporte", "total": 15000},
                {"categoria": "alimentacion", "categoria_nombre": "Alimentación", "total": 10000},
                {"categoria": "hogar", "categoria_nombre": "Hogar", "total": 2000},
            ],
        )

    def test_la_pagina_muestra_categorias_en_orden_y_sin_salud(self):
        self.gastos_ca5(self.ana)
        html = self.ver_como_ana().content.decode()
        for texto in ("Transporte", "Alimentación", "Hogar", "$15.000", "$10.000", "$2.000"):
            self.assertIn(texto, html)
        self.assertLess(html.index("Transporte"), html.index("Alimentación"))
        self.assertLess(html.index("Alimentación"), html.index("Hogar"))
        self.assertNotIn("Salud", html)

    def test_cada_monto_va_en_la_fila_de_su_categoria(self):
        self.gastos_ca5(self.ana)
        html = self.ver_como_ana().content.decode()
        for nombre, monto in (
            ("Transporte", r"\$15\.000"),
            ("Alimentación", r"\$10\.000"),
            ("Hogar", r"\$2\.000"),
        ):
            with self.subTest(categoria=nombre):
                self.assertRegex(
                    html,
                    rf"<td>\s*{nombre}\s*</td>\s*<td[^>]*>\s*{monto}\s*</td>",
                )

    # CA14

    def test_categoria_desconocida_muestra_el_codigo(self):
        self.crear_gasto(self.ana, categoria="antigua")
        respuesta = self.ver_como_ana()
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context["por_categoria"][0]["categoria_nombre"], "antigua")
        self.assertRegex(respuesta.content.decode(), r"<td>\s*antigua\s*</td>")

    # CA15

    def test_sin_gastos_en_el_mes_muestra_cero_y_el_aviso(self):
        respuesta = self.ver_como_ana()
        self.assertEqual(respuesta.context["total_mes"], 0)
        self.assertContains(respuesta, "$0")
        self.assertContains(respuesta, AVISO_SIN_GASTOS)
        self.assertNotContains(respuesta, "<table")

    def test_solo_gastos_de_otro_mes_cuenta_como_sin_gastos(self):
        self.crear_gasto(self.ana, fecha=date(2026, 10, 31))
        respuesta = self.ver_como_ana()
        self.assertEqual(respuesta.context["total_mes"], 0)
        self.assertContains(respuesta, AVISO_SIN_GASTOS)

    # CA16

    def test_tres_tintos_muestran_aviso_singular_y_enlace(self):
        self.crear_gastos(self.ana, 3)
        respuesta = self.ver_como_ana()
        self.assertEqual(respuesta.context["cantidad_hormiga"], 1)
        self.assertContains(
            respuesta, "Detectamos 1 gasto hormiga en los últimos 30 días."
        )
        self.assertRegex(respuesta.content.decode(), ENLACE_HORMIGA)

    def test_dos_grupos_muestran_aviso_plural(self):
        self.crear_gastos(self.ana, 3, descripcion="Tinto")
        self.crear_gastos(self.ana, 3, descripcion="Pan")
        respuesta = self.ver_como_ana()
        self.assertEqual(respuesta.context["cantidad_hormiga"], 2)
        self.assertContains(
            respuesta, "Detectamos 2 gastos hormiga en los últimos 30 días."
        )

    # CA17

    def test_aviso_usa_ventana_de_30_dias_y_no_el_mes(self):
        self.crear_gastos(self.ana, 3, fecha=date(2026, 10, 20))
        respuesta = self.ver_como_ana()
        self.assertEqual(respuesta.context["cantidad_hormiga"], 1)
        self.assertEqual(respuesta.context["total_mes"], 0)

    # CA18

    def test_sin_gasto_hormiga_no_hay_aviso_ni_enlace(self):
        self.crear_gastos(self.ana, 2)
        respuesta = self.ver_como_ana()
        self.assertEqual(respuesta.context["cantidad_hormiga"], 0)
        self.assertNotContains(respuesta, "Detectamos")
        self.assertNotContains(respuesta, "Ver gasto hormiga")

    # CA19

    @override_settings(GASTO_HORMIGA_N=2)
    def test_usa_n_de_settings(self):
        self.crear_gastos(self.ana, 2)
        respuesta = self.ver_como_ana()
        self.assertEqual(respuesta.context["cantidad_hormiga"], 1)
        self.assertContains(respuesta, "Detectamos 1 gasto hormiga")

    @override_settings(GASTO_HORMIGA_UMBRAL=3000)
    def test_usa_umbral_de_settings(self):
        self.crear_gastos(self.ana, 3)
        respuesta = self.ver_como_ana()
        self.assertEqual(respuesta.context["cantidad_hormiga"], 0)
        self.assertNotContains(respuesta, "Detectamos")

    # CA20

    def test_tabla_accesible_un_csrf_y_un_h1(self):
        self.crear_gastos(self.ana, 1)
        respuesta = self.ver_como_ana()
        self.assertContains(respuesta, '<th scope="col"', count=2)
        self.assertContains(respuesta, "csrfmiddlewaretoken", count=1)
        self.assertContains(respuesta, "<h1", count=1)
