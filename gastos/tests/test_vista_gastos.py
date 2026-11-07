from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from gastos.models import Gasto

Usuario = get_user_model()
URL_GASTOS = "/gastos/"
MENSAJE_CENTAVOS = "El monto debe ser en pesos enteros, sin centavos."


def url_eliminar(gasto):
    return reverse("eliminar_gasto", args=[gasto.pk])


class VistaGastosTests(TestCase):
    def setUp(self):
        self.hoy = timezone.localdate()
        self.ana = Usuario.objects.create_user("ana@ejemplo.com", password="clave-de-ejemplo-1")
        self.beto = Usuario.objects.create_user("beto@ejemplo.com", password="clave-de-ejemplo-2")

    def crear_gasto(self, usuario, **campos):
        datos = {"monto": 3500, "fecha": self.hoy, "descripcion": "Empanada", **campos}
        return Gasto.objects.create(usuario=usuario, **datos)

    def datos_formulario(self, **cambios):
        return {
            "monto": "3500",
            "fecha": self.hoy.isoformat(),
            "categoria": Gasto.Categoria.ALIMENTACION,
            "descripcion": "Empanada",
            **cambios,
        }

    # Sesión obligatoria

    def test_sin_sesion_redirige_al_login(self):
        respuesta = self.client.get(URL_GASTOS)
        self.assertRedirects(respuesta, f"/login/?next={URL_GASTOS}")

    def test_sin_sesion_no_crea(self):
        respuesta = self.client.post(URL_GASTOS, self.datos_formulario())
        self.assertRedirects(respuesta, f"/login/?next={URL_GASTOS}")
        self.assertFalse(Gasto.objects.exists())

    def test_sin_sesion_no_elimina(self):
        gasto = self.crear_gasto(self.ana)
        respuesta = self.client.post(url_eliminar(gasto))
        self.assertRedirects(respuesta, f"/login/?next={url_eliminar(gasto)}")
        self.assertTrue(Gasto.objects.filter(pk=gasto.pk).exists())

    # Lista

    def test_lista_solo_gastos_propios(self):
        propio = self.crear_gasto(self.ana, descripcion="Tinto de Ana")
        self.crear_gasto(self.beto, descripcion="Galletas de Beto")
        self.client.force_login(self.ana)

        respuesta = self.client.get(URL_GASTOS)

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(list(respuesta.context["gastos"]), [propio])
        self.assertContains(respuesta, "Tinto de Ana")
        self.assertNotContains(respuesta, "Galletas de Beto")

    def test_lista_del_mas_reciente_al_mas_antiguo(self):
        viejo = self.crear_gasto(self.ana, fecha=self.hoy - timedelta(days=3))
        nuevo = self.crear_gasto(self.ana, fecha=self.hoy)
        mismo_dia = self.crear_gasto(self.ana, fecha=self.hoy)
        self.client.force_login(self.ana)

        respuesta = self.client.get(URL_GASTOS)

        self.assertEqual(list(respuesta.context["gastos"]), [mismo_dia, nuevo, viejo])

    def test_lista_vacia_muestra_aviso(self):
        self.crear_gasto(self.beto)
        self.client.force_login(self.ana)
        respuesta = self.client.get(URL_GASTOS)
        self.assertContains(respuesta, "Aún no tienes gastos registrados.")

    def test_pagina_tiene_csrf_y_estructura_accesible(self):
        self.crear_gasto(self.ana)
        self.client.force_login(self.ana)
        respuesta = self.client.get(URL_GASTOS)
        self.assertContains(respuesta, 'lang="es"')
        self.assertContains(respuesta, 'name="viewport"')
        self.assertContains(respuesta, "<main")
        # Formulario de registro y formulario de eliminar.
        self.assertContains(respuesta, "csrfmiddlewaretoken", count=3)

    # Crear

    def test_crear_gasto_asigna_usuario_y_redirige(self):
        self.client.force_login(self.ana)
        respuesta = self.client.post(URL_GASTOS, self.datos_formulario())
        self.assertRedirects(respuesta, URL_GASTOS)
        gasto = Gasto.objects.get()
        self.assertEqual(gasto.usuario, self.ana)
        self.assertEqual(gasto.monto, 3500)
        self.assertEqual(gasto.descripcion, "Empanada")

    def test_crear_ignora_usuario_enviado(self):
        self.client.force_login(self.ana)
        self.client.post(URL_GASTOS, self.datos_formulario(usuario=self.beto.pk))
        self.assertEqual(Gasto.objects.get().usuario, self.ana)

    def test_fecha_de_hoy_y_de_ayer_son_validas(self):
        self.client.force_login(self.ana)
        for fecha in (self.hoy, self.hoy - timedelta(days=1)):
            with self.subTest(fecha=fecha):
                respuesta = self.client.post(URL_GASTOS, self.datos_formulario(fecha=fecha.isoformat()))
                self.assertRedirects(respuesta, URL_GASTOS)
        self.assertEqual(Gasto.objects.filter(usuario=self.ana).count(), 2)

    def test_monto_minimo_de_un_peso_es_valido(self):
        self.client.force_login(self.ana)
        respuesta = self.client.post(URL_GASTOS, self.datos_formulario(monto="1"))
        self.assertRedirects(respuesta, URL_GASTOS)

    # Datos inválidos

    def assert_no_guarda(self, campo, mensaje, **cambios):
        self.client.force_login(self.ana)
        respuesta = self.client.post(URL_GASTOS, self.datos_formulario(**cambios))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context["formulario"].errors[campo], [mensaje])
        self.assertContains(respuesta, mensaje)
        self.assertFalse(Gasto.objects.exists())

    def test_error_queda_enlazado_al_campo(self):
        self.client.force_login(self.ana)
        respuesta = self.client.post(URL_GASTOS, self.datos_formulario(monto="0"))
        self.assertContains(respuesta, 'aria-describedby="id_monto_error"')
        self.assertContains(respuesta, 'id="id_monto_error"')

    def test_monto_cero_no_guarda(self):
        self.assert_no_guarda("monto", "El monto debe ser mayor que cero.", monto="0")

    def test_monto_negativo_no_guarda(self):
        self.assert_no_guarda("monto", "El monto debe ser mayor que cero.", monto="-500")

    def test_fecha_futura_no_guarda(self):
        manana = (self.hoy + timedelta(days=1)).isoformat()
        self.assert_no_guarda("fecha", "La fecha no puede ser futura.", fecha=manana)

    def test_monto_con_centavos_no_guarda(self):
        self.assert_no_guarda("monto", MENSAJE_CENTAVOS, monto="1500.50")

    # Eliminar

    def test_eliminar_gasto_propio(self):
        gasto = self.crear_gasto(self.ana)
        self.client.force_login(self.ana)
        respuesta = self.client.post(url_eliminar(gasto))
        self.assertRedirects(respuesta, URL_GASTOS)
        self.assertFalse(Gasto.objects.filter(pk=gasto.pk).exists())

    def test_no_elimina_gasto_ajeno(self):
        ajeno = self.crear_gasto(self.beto)
        self.client.force_login(self.ana)
        respuesta = self.client.post(url_eliminar(ajeno))
        self.assertEqual(respuesta.status_code, 404)
        self.assertTrue(Gasto.objects.filter(pk=ajeno.pk).exists())

    def test_eliminar_gasto_inexistente_da_404(self):
        self.client.force_login(self.ana)
        respuesta = self.client.post(reverse("eliminar_gasto", args=[9999]))
        self.assertEqual(respuesta.status_code, 404)

    def test_eliminar_por_get_no_permitido(self):
        gasto = self.crear_gasto(self.ana)
        self.client.force_login(self.ana)
        respuesta = self.client.get(url_eliminar(gasto))
        self.assertEqual(respuesta.status_code, 405)
        self.assertTrue(Gasto.objects.filter(pk=gasto.pk).exists())
