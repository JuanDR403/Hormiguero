from datetime import date, timedelta
from decimal import Decimal

from django.test import SimpleTestCase

from gastos.reglas.gastos import validar_gasto

HOY = date(2026, 11, 5)
AYER = HOY - timedelta(days=1)
MANANA = HOY + timedelta(days=1)


class ValidarGastoMontoTests(SimpleTestCase):
    def test_monto_cero_es_invalido(self):
        self.assertIn("monto", validar_gasto(Decimal("0"), HOY, HOY))

    def test_monto_negativo_es_invalido(self):
        self.assertIn("monto", validar_gasto(Decimal("-1"), HOY, HOY))

    def test_monto_vacio_es_invalido(self):
        self.assertIn("monto", validar_gasto(None, HOY, HOY))

    def test_monto_minimo_es_valido(self):
        self.assertNotIn("monto", validar_gasto(Decimal("1"), HOY, HOY))

    def test_monto_normal_es_valido(self):
        self.assertNotIn("monto", validar_gasto(Decimal("25000"), HOY, HOY))


class ValidarGastoFechaTests(SimpleTestCase):
    def test_fecha_de_hoy_es_valida(self):
        self.assertNotIn("fecha", validar_gasto(Decimal("1"), HOY, HOY))

    def test_fecha_pasada_es_valida(self):
        self.assertNotIn("fecha", validar_gasto(Decimal("1"), AYER, HOY))

    def test_fecha_de_manana_es_invalida(self):
        self.assertIn("fecha", validar_gasto(Decimal("1"), MANANA, HOY))

    def test_fecha_vacia_es_invalida(self):
        self.assertIn("fecha", validar_gasto(Decimal("1"), None, HOY))


class ValidarGastoCompletoTests(SimpleTestCase):
    def test_gasto_valido_no_tiene_errores(self):
        self.assertEqual(validar_gasto(Decimal("3500"), AYER, HOY), {})

    def test_reporta_ambos_errores_a_la_vez(self):
        self.assertEqual(
            validar_gasto(Decimal("0"), MANANA, HOY),
            {
                "monto": "El monto debe ser mayor que cero.",
                "fecha": "La fecha no puede ser futura.",
            },
        )
