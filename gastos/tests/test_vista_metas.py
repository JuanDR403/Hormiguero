import re
from datetime import date
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from gastos.models import Meta

Usuario = get_user_model()
URL_METAS = "/metas/"
HOY = date(2026, 11, 14)


def url_eliminar(meta):
    return reverse("eliminar_meta", args=[meta.pk])


class BaseMetasTests(TestCase):
    def setUp(self):
        parche = mock.patch("django.utils.timezone.localdate", return_value=HOY)
        parche.start()
        self.addCleanup(parche.stop)
        self.ana = Usuario.objects.create_user("ana@ejemplo.com", password="clave-de-ejemplo-1")
        self.beto = Usuario.objects.create_user("beto@ejemplo.com", password="clave-de-ejemplo-2")

    def crear_meta(self, usuario, **campos):
        datos = {
            "nombre": "Portátil",
            "precio": 1_000_000,
            "ahorrado": 0,
            "fecha_limite": date(2027, 2, 1),
            **campos,
        }
        return Meta.objects.create(usuario=usuario, **datos)

    def datos_formulario(self, **cambios):
        return {
            "nombre": "Portátil",
            "precio": "1200000",
            "ahorrado": "200000",
            "fecha_limite": "2027-04-30",
            **cambios,
        }


class SesionYAislamientoTests(BaseMetasTests):
    # CA4
    def test_sin_sesion_get_redirige_al_login(self):
        respuesta = self.client.get(URL_METAS)
        self.assertRedirects(respuesta, f"/login/?next={URL_METAS}")

    def test_sin_sesion_post_redirige_y_no_crea(self):
        respuesta = self.client.post(URL_METAS, self.datos_formulario())
        self.assertRedirects(respuesta, f"/login/?next={URL_METAS}")
        self.assertFalse(Meta.objects.exists())

    def test_sin_sesion_no_elimina(self):
        meta = self.crear_meta(self.ana)
        respuesta = self.client.post(url_eliminar(meta))
        self.assertRedirects(respuesta, f"/login/?next={url_eliminar(meta)}")
        self.assertTrue(Meta.objects.filter(pk=meta.pk).exists())

    # CA5
    def test_con_sesion_responde_200_con_la_plantilla(self):
        self.client.force_login(self.ana)
        respuesta = self.client.get(URL_METAS)
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "gastos/metas.html")

    def test_url_lista_metas_es_metas(self):
        self.assertEqual(reverse("lista_metas"), URL_METAS)

    # CA6
    def test_lista_solo_metas_propias(self):
        propia = self.crear_meta(self.ana, nombre="Bicicleta de Ana")
        self.crear_meta(self.beto, nombre="Consola de Beto")
        self.client.force_login(self.ana)

        respuesta = self.client.get(URL_METAS)

        self.assertEqual(list(respuesta.context["metas"]), [propia])
        self.assertContains(respuesta, "Bicicleta de Ana")
        self.assertNotContains(respuesta, "Consola de Beto")

    # CA11
    def test_sin_metas_propias_muestra_aviso_y_no_tabla(self):
        self.crear_meta(self.beto)
        self.client.force_login(self.ana)
        respuesta = self.client.get(URL_METAS)
        self.assertContains(respuesta, "Aún no tienes metas de ahorro.")
        self.assertNotContains(respuesta, "<table")


class ListaMetasTests(BaseMetasTests):
    # CA7
    def test_lista_ordenada_por_fecha_limite_ascendente(self):
        lejana = self.crear_meta(self.ana, fecha_limite=date(2027, 8, 1))
        cercana = self.crear_meta(self.ana, fecha_limite=date(2026, 12, 1))
        self.client.force_login(self.ana)
        respuesta = self.client.get(URL_METAS)
        self.assertEqual(list(respuesta.context["metas"]), [cercana, lejana])

    def test_misma_fecha_limite_se_ordena_por_creacion(self):
        primera = self.crear_meta(self.ana, nombre="Primera")
        segunda = self.crear_meta(self.ana, nombre="Segunda")
        self.client.force_login(self.ana)
        respuesta = self.client.get(URL_METAS)
        self.assertEqual(list(respuesta.context["metas"]), [primera, segunda])

    # CA8
    def test_meta_en_curso_trae_valores_calculados(self):
        self.crear_meta(self.ana)
        self.client.force_login(self.ana)
        respuesta = self.client.get(URL_METAS)
        meta = respuesta.context["metas"][0]
        self.assertEqual(meta.cuota, 333_334)
        self.assertEqual(meta.falta, 1_000_000)
        self.assertEqual(meta.meses, 3)
        self.assertEqual(meta.estado, "en_curso")
        self.assertEqual(meta.estado_nombre, "En curso")

    def test_pagina_muestra_los_valores_de_la_meta_en_curso(self):
        self.crear_meta(self.ana)
        self.client.force_login(self.ana)
        respuesta = self.client.get(URL_METAS)
        self.assertContains(respuesta, "$333.334")
        self.assertContains(respuesta, "$1.000.000")
        self.assertContains(respuesta, '<td class="numero">3</td>', html=True)
        self.assertContains(respuesta, "En curso")

    # CA9
    def test_meta_cumplida_tiene_cuota_y_falta_cero(self):
        self.crear_meta(self.ana, precio=500_000, ahorrado=500_000)
        self.client.force_login(self.ana)
        respuesta = self.client.get(URL_METAS)
        meta = respuesta.context["metas"][0]
        self.assertEqual(meta.cuota, 0)
        self.assertEqual(meta.falta, 0)
        self.assertEqual(meta.estado, "cumplida")
        self.assertEqual(meta.estado_nombre, "Cumplida")
        self.assertContains(respuesta, "Cumplida")
        self.assertContains(respuesta, "$0")

    # CA10
    def test_meta_vencida_cobra_todo_lo_que_falta(self):
        self.crear_meta(
            self.ana, precio=500_000, ahorrado=100_000, fecha_limite=date(2026, 10, 1)
        )
        self.client.force_login(self.ana)
        respuesta = self.client.get(URL_METAS)
        meta = respuesta.context["metas"][0]
        self.assertEqual(meta.cuota, 400_000)
        self.assertEqual(meta.meses, 0)
        self.assertEqual(meta.estado, "vencida")
        self.assertEqual(meta.estado_nombre, "Vencida")
        self.assertContains(respuesta, "Vencida")
        self.assertContains(respuesta, "$400.000")

    def test_meta_con_fecha_limite_hoy_sigue_en_curso(self):
        self.crear_meta(self.ana, precio=500_000, ahorrado=100_000, fecha_limite=HOY)
        self.client.force_login(self.ana)
        respuesta = self.client.get(URL_METAS)
        self.assertEqual(respuesta.context["metas"][0].estado, "en_curso")

    def test_meta_con_fecha_limite_ayer_sin_cumplir_es_vencida(self):
        self.crear_meta(
            self.ana, precio=500_000, ahorrado=499_999, fecha_limite=date(2026, 11, 13)
        )
        self.client.force_login(self.ana)
        respuesta = self.client.get(URL_METAS)
        self.assertEqual(respuesta.context["metas"][0].estado, "vencida")


class CrearMetaTests(BaseMetasTests):
    # CA12
    def test_crear_meta_asigna_usuario_redirige_y_avisa(self):
        self.client.force_login(self.ana)
        respuesta = self.client.post(URL_METAS, self.datos_formulario(), follow=True)
        self.assertRedirects(respuesta, URL_METAS)
        meta = Meta.objects.get()
        self.assertEqual(meta.usuario, self.ana)
        self.assertEqual(meta.nombre, "Portátil")
        self.assertEqual(meta.precio, 1_200_000)
        self.assertEqual(meta.ahorrado, 200_000)
        self.assertEqual(meta.fecha_limite, date(2027, 4, 30))
        self.assertContains(respuesta, "Meta creada.")

    # CA13
    def test_crear_ignora_usuario_enviado(self):
        self.client.force_login(self.ana)
        self.client.post(URL_METAS, self.datos_formulario(usuario=self.beto.pk))
        self.assertEqual(Meta.objects.get().usuario, self.ana)

    # CA14
    def test_precio_minimo_de_un_peso_es_valido(self):
        self.client.force_login(self.ana)
        respuesta = self.client.post(URL_METAS, self.datos_formulario(precio="1", ahorrado="0"))
        self.assertRedirects(respuesta, URL_METAS)
        self.assertEqual(Meta.objects.get().precio, 1)

    def test_ahorrado_cero_es_valido(self):
        self.client.force_login(self.ana)
        respuesta = self.client.post(URL_METAS, self.datos_formulario(ahorrado="0"))
        self.assertRedirects(respuesta, URL_METAS)
        self.assertEqual(Meta.objects.get().ahorrado, 0)

    def test_ahorrado_mayor_que_el_precio_es_valido(self):
        self.client.force_login(self.ana)
        respuesta = self.client.post(
            URL_METAS, self.datos_formulario(precio="100", ahorrado="500")
        )
        self.assertRedirects(respuesta, URL_METAS)
        self.assertEqual(Meta.objects.get().ahorrado, 500)

    def test_fecha_limite_de_hoy_es_valida(self):
        self.client.force_login(self.ana)
        respuesta = self.client.post(URL_METAS, self.datos_formulario(fecha_limite="2026-11-14"))
        self.assertRedirects(respuesta, URL_METAS)
        self.assertEqual(Meta.objects.get().fecha_limite, HOY)

    def test_nombre_de_100_caracteres_es_valido(self):
        self.client.force_login(self.ana)
        respuesta = self.client.post(URL_METAS, self.datos_formulario(nombre="a" * 100))
        self.assertRedirects(respuesta, URL_METAS)
        self.assertEqual(len(Meta.objects.get().nombre), 100)

    # CA15
    def assert_no_guarda(self, campo, mensaje=None, **cambios):
        self.client.force_login(self.ana)
        respuesta = self.client.post(URL_METAS, self.datos_formulario(**cambios))
        self.assertEqual(respuesta.status_code, 200)
        errores = respuesta.context["formulario"].errors
        self.assertEqual(list(errores.keys()), [campo])
        self.assertEqual(len(errores[campo]), 1)
        if mensaje is not None:
            self.assertEqual(errores[campo], [mensaje])
            self.assertContains(respuesta, mensaje)
        self.assertContains(respuesta, f'aria-describedby="id_{campo}_error"')
        self.assertFalse(Meta.objects.exists())
        return respuesta

    def obligatorio(self, campo):
        from gastos.forms import FormularioMeta

        return str(FormularioMeta().fields[campo].error_messages["required"])

    def test_nombre_vacio_no_guarda(self):
        self.assert_no_guarda("nombre", self.obligatorio("nombre"), nombre="")

    def test_nombre_solo_espacios_no_guarda(self):
        self.assert_no_guarda("nombre", self.obligatorio("nombre"), nombre="   ")

    def test_nombre_de_101_caracteres_no_guarda(self):
        respuesta = self.assert_no_guarda("nombre", nombre="a" * 101)
        mensaje = respuesta.context["formulario"].errors["nombre"][0]
        self.assertIn("100", mensaje)
        self.assertIn("101", mensaje)

    def test_precio_vacio_no_guarda(self):
        self.assert_no_guarda("precio", self.obligatorio("precio"), precio="")

    def test_ahorrado_vacio_no_guarda(self):
        self.assert_no_guarda("ahorrado", self.obligatorio("ahorrado"), ahorrado="")

    def test_fecha_limite_vacia_no_guarda(self):
        self.assert_no_guarda(
            "fecha_limite", self.obligatorio("fecha_limite"), fecha_limite=""
        )

    def test_precio_cero_no_guarda(self):
        self.assert_no_guarda("precio", "El precio debe ser mayor que cero.", precio="0")

    def test_precio_negativo_no_guarda(self):
        self.assert_no_guarda("precio", "El precio debe ser mayor que cero.", precio="-1")

    def test_ahorrado_negativo_no_guarda(self):
        self.assert_no_guarda("ahorrado", "Lo ahorrado no puede ser negativo.", ahorrado="-1")

    def test_fecha_limite_ayer_no_guarda(self):
        self.assert_no_guarda(
            "fecha_limite", "La fecha límite no puede ser pasada.", fecha_limite="2026-11-13"
        )

    def test_precio_con_centavos_no_guarda(self):
        self.assert_no_guarda(
            "precio", "El precio debe ser en pesos enteros, sin centavos.", precio="1500.50"
        )

    def test_ahorrado_con_centavos_no_guarda(self):
        self.assert_no_guarda(
            "ahorrado",
            "Lo ahorrado debe ser en pesos enteros, sin centavos.",
            ahorrado="1500.50",
        )

    def test_formulario_invalido_conserva_los_datos(self):
        respuesta = self.assert_no_guarda("precio", precio="0", nombre="Bicicleta")
        self.assertContains(respuesta, "Bicicleta")
        self.assertContains(respuesta, "200000")
        self.assertContains(respuesta, "2027-04-30")

    # CA16
    def test_formulario_vacio_tiene_ahorrado_en_cero_y_sin_usuario(self):
        from gastos.forms import FormularioMeta

        formulario = FormularioMeta()
        self.assertNotIn("usuario", formulario.fields)
        self.assertEqual(formulario.fields["ahorrado"].initial, 0)

    def test_pagina_muestra_ahorrado_con_cero_inicial(self):
        self.client.force_login(self.ana)
        respuesta = self.client.get(URL_METAS)
        formulario = respuesta.context["formulario"]
        self.assertEqual(formulario["ahorrado"].value(), 0)
        self.assertIsNone(formulario["fecha_limite"].value())
        contenido = respuesta.content.decode()
        self.assertRegex(
            contenido, r'<input[^>]*name="ahorrado"[^>]*value="0"|<input[^>]*value="0"[^>]*name="ahorrado"'
        )
        self.assertRegex(contenido, r'<input[^>]*id="id_ahorrado"[^>]*value="0"|<input[^>]*value="0"[^>]*id="id_ahorrado"')
        self.assertContains(respuesta, 'id="id_fecha_limite"')
        self.assertContains(respuesta, 'type="date"')
        entrada_fecha = re.search(r'<input[^>]*id="id_fecha_limite"[^>]*>', contenido).group(0)
        self.assertNotIn("value=", entrada_fecha)


class EliminarMetaTests(BaseMetasTests):
    # CA17
    def test_eliminar_meta_propia(self):
        meta = self.crear_meta(self.ana)
        self.client.force_login(self.ana)
        respuesta = self.client.post(url_eliminar(meta), follow=True)
        self.assertRedirects(respuesta, URL_METAS)
        self.assertFalse(Meta.objects.filter(pk=meta.pk).exists())
        self.assertContains(respuesta, "Meta eliminada.")

    # CA18
    def test_no_elimina_meta_ajena(self):
        ajena = self.crear_meta(self.beto)
        self.client.force_login(self.ana)
        respuesta = self.client.post(url_eliminar(ajena))
        self.assertEqual(respuesta.status_code, 404)
        self.assertTrue(Meta.objects.filter(pk=ajena.pk).exists())

    def test_eliminar_meta_inexistente_da_404(self):
        self.client.force_login(self.ana)
        respuesta = self.client.post(reverse("eliminar_meta", args=[9999]))
        self.assertEqual(respuesta.status_code, 404)

    # CA19
    def test_eliminar_por_get_no_permitido(self):
        meta = self.crear_meta(self.ana)
        self.client.force_login(self.ana)
        respuesta = self.client.get(url_eliminar(meta))
        self.assertEqual(respuesta.status_code, 405)
        self.assertTrue(Meta.objects.filter(pk=meta.pk).exists())


class PaginaYEncabezadoTests(BaseMetasTests):
    # CA20
    def test_pagina_tiene_un_solo_h1(self):
        self.client.force_login(self.ana)
        respuesta = self.client.get(URL_METAS)
        self.assertContains(respuesta, "<h1", count=1)
        self.assertContains(respuesta, "Metas de ahorro")

    def test_tabla_usa_encabezados_con_scope(self):
        self.crear_meta(self.ana)
        self.client.force_login(self.ana)
        respuesta = self.client.get(URL_METAS)
        self.assertContains(respuesta, '<th scope="col"')
        for columna in (
            "Nombre", "Precio", "Ahorrado", "Falta", "Fecha límite",
            "Meses restantes", "Cuota mensual", "Estado", "Acciones",
        ):
            with self.subTest(columna=columna):
                self.assertContains(respuesta, columna)

    def test_pagina_con_una_meta_tiene_tres_tokens_csrf(self):
        self.crear_meta(self.ana)
        self.client.force_login(self.ana)
        respuesta = self.client.get(URL_METAS)
        # Formulario de crear, formulario de eliminar y cierre de sesión.
        self.assertContains(respuesta, "csrfmiddlewaretoken", count=3)

    def test_boton_eliminar_nombra_la_meta(self):
        self.crear_meta(self.ana, nombre="Portátil")
        self.client.force_login(self.ana)
        respuesta = self.client.get(URL_METAS)
        self.assertContains(respuesta, 'aria-label="Eliminar meta Portátil"')

    def test_pagina_hereda_de_la_base(self):
        self.client.force_login(self.ana)
        respuesta = self.client.get(URL_METAS)
        self.assertContains(respuesta, 'lang="es"')
        self.assertContains(respuesta, 'name="viewport"')
        self.assertContains(respuesta, "<main")

    # CA21
    def test_con_sesion_el_encabezado_enlaza_a_metas(self):
        self.client.force_login(self.ana)
        respuesta = self.client.get("/gastos/")
        self.assertContains(respuesta, 'href="/metas/"')
        self.assertContains(respuesta, "Metas de ahorro")

    def test_sin_sesion_el_encabezado_no_enlaza_a_metas(self):
        # "/" hereda de templates/base.html; "/login/" no, y no probaría nada.
        respuesta = self.client.get("/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "base.html")
        self.assertContains(respuesta, 'class="encabezado"')
        self.assertContains(respuesta, '<a class="marca" href="/"')
        self.assertNotContains(respuesta, 'href="/metas/"')
        self.assertNotContains(respuesta, "Metas de ahorro")

    def test_nombre_con_caracteres_especiales_sale_escapado_en_aria_label(self):
        self.crear_meta(self.ana, nombre='Viaje "Cali" <2027> & más')
        self.client.force_login(self.ana)
        respuesta = self.client.get(URL_METAS)
        self.assertContains(
            respuesta,
            'aria-label="Eliminar meta Viaje &quot;Cali&quot; &lt;2027&gt; &amp; más"',
        )
        self.assertNotContains(respuesta, "<2027>")
        self.assertNotContains(respuesta, 'Viaje "Cali"')
