from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from django.test import SimpleTestCase

from gastos.reglas import resumen

HOY = date(2026, 11, 14)


def gasto(fecha, monto, categoria="alimentacion"):
    return SimpleNamespace(fecha=fecha, categoria=categoria, monto=monto)


class ResumirMesPeriodoTests(SimpleTestCase):
    # CA1
    def test_cuenta_dia_uno_y_hoy_pero_no_el_ultimo_dia_del_mes_anterior(self):
        gastos = [
            gasto(date(2026, 11, 1), 5000),
            gasto(date(2026, 11, 14), 20000),
            gasto(date(2026, 10, 31), 100000),
        ]
        self.assertEqual(resumen.resumir_mes(gastos, HOY)["total"], 25000)

    # CA2
    def test_no_cuenta_gasto_posterior_a_hoy(self):
        gastos = [gasto(date(2026, 11, 14), 1000), gasto(date(2026, 11, 15), 9000)]
        self.assertEqual(resumen.resumir_mes(gastos, HOY)["total"], 1000)

    def test_no_cuenta_el_mismo_mes_de_otro_anio(self):
        gastos = [gasto(date(2026, 11, 10), 1000), gasto(date(2025, 11, 10), 9000)]
        resultado = resumen.resumir_mes(gastos, HOY)
        self.assertEqual(resultado["total"], 1000)
        self.assertEqual(sum(c["total"] for c in resultado["por_categoria"]), 1000)

    # CA3
    def test_hoy_primero_de_mes_solo_cuenta_ese_dia(self):
        hoy = date(2026, 12, 1)
        gastos = [
            gasto(date(2026, 12, 1), 3000),
            gasto(date(2026, 11, 30), 7000),
            gasto(date(2026, 12, 2), 9000),
        ]
        self.assertEqual(resumen.resumir_mes(gastos, hoy)["total"], 3000)


class ResumirMesVacioTests(SimpleTestCase):
    # CA4
    def test_sin_gastos_total_cero_y_lista_vacia(self):
        self.assertEqual(resumen.resumir_mes([], HOY), {"total": 0, "por_categoria": []})

    def test_sin_gastos_del_mes_total_cero_y_lista_vacia(self):
        gastos = [gasto(date(2026, 10, 20), 5000), gasto(date(2026, 11, 20), 5000)]
        self.assertEqual(resumen.resumir_mes(gastos, HOY), {"total": 0, "por_categoria": []})


class ResumirMesCategoriasTests(SimpleTestCase):
    # CA5
    def test_suma_por_categoria_ordena_por_total_y_omite_otro_mes(self):
        gastos = [
            gasto(date(2026, 11, 2), 4000, "alimentacion"),
            gasto(date(2026, 11, 3), 6000, "alimentacion"),
            gasto(date(2026, 11, 4), 15000, "transporte"),
            gasto(date(2026, 11, 5), 2000, "hogar"),
            gasto(date(2026, 10, 20), 50000, "salud"),
        ]
        resultado = resumen.resumir_mes(gastos, HOY)
        self.assertEqual(
            resultado["por_categoria"],
            [
                {"categoria": "transporte", "total": 15000},
                {"categoria": "alimentacion", "total": 10000},
                {"categoria": "hogar", "total": 2000},
            ],
        )
        self.assertEqual(resultado["total"], 27000)

    # CA6
    def test_empate_se_ordena_por_codigo_ascendente(self):
        gastos = [
            gasto(date(2026, 11, 2), 5000, "transporte"),
            gasto(date(2026, 11, 3), 5000, "alimentacion"),
        ]
        codigos = [c["categoria"] for c in resumen.resumir_mes(gastos, HOY)["por_categoria"]]
        self.assertEqual(codigos, ["alimentacion", "transporte"])


class ResumirMesTiposTests(SimpleTestCase):
    # CA7
    def test_acepta_decimal_y_devuelve_enteros(self):
        gastos = [
            gasto(date(2026, 11, 2), Decimal("4000"), "alimentacion"),
            gasto(date(2026, 11, 3), Decimal("6000"), "alimentacion"),
        ]
        resultado = resumen.resumir_mes(gastos, HOY)
        self.assertEqual(resultado["total"], 10000)
        self.assertIs(type(resultado["total"]), int)
        self.assertEqual(resultado["por_categoria"][0]["total"], 10000)
        self.assertIs(type(resultado["por_categoria"][0]["total"]), int)

    def test_total_cero_es_entero(self):
        self.assertIs(type(resumen.resumir_mes([], HOY)["total"]), int)
