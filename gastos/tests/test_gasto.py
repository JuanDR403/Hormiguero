from datetime import date, timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from gastos.forms import FormularioGasto
from gastos.models import Gasto

Usuario = get_user_model()
HOY = date(2026, 11, 5)
MENSAJE_CENTAVOS = "El monto debe ser en pesos enteros, sin centavos."


def datos_gasto(**cambios):
    return {
        "monto": "3500",
        "fecha": HOY.isoformat(),
        "categoria": Gasto.Categoria.ALIMENTACION,
        "descripcion": "Empanada",
        **cambios,
    }


class GastoModeloTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user("ana@ejemplo.com")

    def test_base_de_datos_rechaza_monto_cero(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Gasto.objects.create(usuario=self.usuario, monto=0, fecha=HOY)

    def test_lista_primero_lo_mas_reciente(self):
        viejo = Gasto.objects.create(usuario=self.usuario, monto=1, fecha=HOY - timedelta(days=2))
        nuevo = Gasto.objects.create(usuario=self.usuario, monto=1, fecha=HOY)
        mismo_dia = Gasto.objects.create(usuario=self.usuario, monto=1, fecha=HOY)
        self.assertEqual(list(Gasto.objects.all()), [mismo_dia, nuevo, viejo])

    def test_categoria_por_defecto_es_otros(self):
        gasto = Gasto.objects.create(usuario=self.usuario, monto=1, fecha=HOY)
        self.assertEqual(gasto.categoria, Gasto.Categoria.OTROS)


class FormularioGastoTests(TestCase):
    def formulario(self, **cambios):
        return FormularioGasto(datos_gasto(**cambios), hoy=HOY)

    def test_datos_validos(self):
        self.assertTrue(self.formulario().is_valid())

    def test_fecha_futura(self):
        formulario = self.formulario(fecha=(HOY + timedelta(days=1)).isoformat())
        self.assertFalse(formulario.is_valid())
        self.assertEqual(formulario.errors["fecha"], ["La fecha no puede ser futura."])

    def test_monto_cero(self):
        formulario = self.formulario(monto="0")
        self.assertFalse(formulario.is_valid())
        self.assertEqual(formulario.errors["monto"], ["El monto debe ser mayor que cero."])

    def test_monto_negativo(self):
        formulario = self.formulario(monto="-500")
        self.assertFalse(formulario.is_valid())
        self.assertEqual(formulario.errors["monto"], ["El monto debe ser mayor que cero."])

    def test_monto_con_centavos(self):
        for monto in ("1500.50", "0.5"):
            with self.subTest(monto=monto):
                formulario = self.formulario(monto=monto)
                self.assertFalse(formulario.is_valid())
                self.assertEqual(formulario.errors["monto"], [MENSAJE_CENTAVOS])

    def test_monto_vacio_muestra_un_solo_error(self):
        formulario = self.formulario(monto="")
        self.assertFalse(formulario.is_valid())
        self.assertEqual(len(formulario.errors["monto"]), 1)

    def test_ignora_usuario_enviado_en_los_datos(self):
        otro = Usuario.objects.create_user("intruso@ejemplo.com")
        formulario = self.formulario(usuario=otro.pk)
        self.assertTrue(formulario.is_valid())
        self.assertNotIn("usuario", formulario.cleaned_data)

    def test_sin_hoy_usa_la_fecha_local(self):
        with mock.patch("django.utils.timezone.localdate", return_value=HOY - timedelta(days=1)):
            formulario = FormularioGasto(datos_gasto())
        self.assertFalse(formulario.is_valid())
        self.assertIn("fecha", formulario.errors)
