from datetime import date
from decimal import Decimal

from django.test import SimpleTestCase

from gastos.reglas import metas
from gastos.reglas.metas import (
    calcular_cuota_mensual,
    meses_restantes,
    validar_meta,
)

HOY = date(2026, 11, 14)


class MesesRestantesTests(SimpleTestCase):
    def test_meses_restantes_ignora_el_dia(self):
        self.assertEqual(meses_restantes(date(2027, 2, 10), HOY), 3)

    def test_mismo_mes_da_cero_meses(self):
        self.assertEqual(meses_restantes(date(2026, 11, 30), HOY), 0)

    def test_mes_siguiente_da_un_mes(self):
        self.assertEqual(meses_restantes(date(2026, 12, 1), HOY), 1)

    def test_meses_restantes_con_cambio_de_anio(self):
        self.assertEqual(meses_restantes(date(2027, 1, 15), HOY), 2)

    def test_fecha_pasada_da_cero_meses(self):
        self.assertEqual(meses_restantes(date(2026, 10, 1), HOY), 0)


class CuotaMensualTests(SimpleTestCase):
    def test_cuota_divide_lo_que_falta_entre_los_meses(self):
        cuota = calcular_cuota_mensual(1_200_000, 200_000, date(2027, 4, 30), HOY)
        self.assertEqual(cuota, 200_000)

    def test_cuota_se_redondea_hacia_arriba(self):
        cuota = calcular_cuota_mensual(1_000_000, 0, date(2027, 2, 1), HOY)
        self.assertEqual(cuota, 333_334)

    def test_division_exacta_no_suma_un_peso(self):
        cuota = calcular_cuota_mensual(900_000, 0, date(2027, 2, 1), HOY)
        self.assertEqual(cuota, 300_000)

    def test_falta_un_peso_da_cuota_uno(self):
        cuota = calcular_cuota_mensual(100_001, 100_000, date(2027, 2, 1), HOY)
        self.assertEqual(cuota, 1)

    def test_meta_cumplida_exacta_da_cuota_cero(self):
        cuota = calcular_cuota_mensual(500_000, 500_000, date(2027, 2, 1), HOY)
        self.assertEqual(cuota, 0)

    def test_ahorrado_mayor_que_precio_da_cuota_cero(self):
        cuota = calcular_cuota_mensual(500_000, 600_000, date(2027, 2, 1), HOY)
        self.assertEqual(cuota, 0)

    def test_meta_cumplida_y_vencida_da_cuota_cero(self):
        cuota = calcular_cuota_mensual(500_000, 500_000, date(2026, 10, 1), HOY)
        self.assertEqual(cuota, 0)

    def test_sin_meses_en_el_mes_actual_cuota_es_lo_que_falta(self):
        cuota = calcular_cuota_mensual(500_000, 100_000, date(2026, 11, 30), HOY)
        self.assertEqual(cuota, 400_000)

    def test_fecha_pasada_cuota_es_lo_que_falta(self):
        cuota = calcular_cuota_mensual(500_000, 100_000, date(2026, 10, 1), HOY)
        self.assertEqual(cuota, 400_000)

    def test_cuota_acepta_decimal_y_devuelve_int(self):
        cuota = calcular_cuota_mensual(
            Decimal("1000000"), Decimal("0"), date(2027, 2, 1), HOY
        )
        self.assertIs(type(cuota), int)
        self.assertEqual(cuota, 333_334)


class ValidarMetaTests(SimpleTestCase):
    def validar(self, **cambios):
        datos = {
            "nombre": "Portátil",
            "precio": 1_000_000,
            "ahorrado": 0,
            "fecha_limite": date(2027, 2, 1),
        }
        datos.update(cambios)
        return validar_meta(hoy=HOY, **datos)

    def test_nombre_vacio_es_error(self):
        self.assertIn("nombre", self.validar(nombre=""))
        self.assertIn("nombre", self.validar(nombre="   "))

    def test_nombre_valido(self):
        self.assertNotIn("nombre", self.validar(nombre="Portátil"))

    def test_precio_cero_es_error(self):
        self.assertIn("precio", self.validar(precio=0))

    def test_precio_uno_es_valido(self):
        self.assertNotIn("precio", self.validar(precio=1))

    def test_precio_none_es_error(self):
        self.assertIn("precio", self.validar(precio=None))

    def test_ahorrado_negativo_es_error(self):
        self.assertIn("ahorrado", self.validar(ahorrado=-1))

    def test_ahorrado_cero_es_valido(self):
        self.assertNotIn("ahorrado", self.validar(ahorrado=0))

    def test_ahorrado_mayor_que_precio_es_valido(self):
        errores = self.validar(precio=100, ahorrado=500)
        self.assertNotIn("ahorrado", errores)

    def test_ahorrado_none_es_error(self):
        self.assertIn("ahorrado", self.validar(ahorrado=None))

    def test_fecha_limite_ayer_es_error(self):
        self.assertIn("fecha_limite", self.validar(fecha_limite=date(2026, 11, 13)))

    def test_fecha_limite_hoy_es_valida(self):
        self.assertNotIn("fecha_limite", self.validar(fecha_limite=HOY))

    def test_fecha_limite_none_es_error(self):
        self.assertIn("fecha_limite", self.validar(fecha_limite=None))

    def test_meta_valida_no_tiene_errores(self):
        self.assertEqual(self.validar(), {})


class CalcularFaltaTests(SimpleTestCase):
    def test_falta_es_precio_menos_ahorrado(self):
        self.assertEqual(metas.calcular_falta(1_200_000, 200_000), 1_000_000)

    def test_falta_un_peso_por_debajo_del_precio(self):
        self.assertEqual(metas.calcular_falta(100_000, 99_999), 1)

    def test_ahorrado_igual_al_precio_da_cero(self):
        self.assertEqual(metas.calcular_falta(500_000, 500_000), 0)

    def test_ahorrado_un_peso_sobre_el_precio_da_cero(self):
        self.assertEqual(metas.calcular_falta(500_000, 500_001), 0)

    def test_ahorrado_mayor_que_precio_nunca_es_negativa(self):
        self.assertEqual(metas.calcular_falta(500_000, 900_000), 0)

    def test_falta_acepta_decimal_y_devuelve_int(self):
        falta = metas.calcular_falta(Decimal("1200000"), Decimal("200000"))
        self.assertIs(type(falta), int)
        self.assertEqual(falta, 1_000_000)

    def test_falta_con_decimal_cumplida_devuelve_int_cero(self):
        falta = metas.calcular_falta(Decimal("100"), Decimal("200"))
        self.assertIs(type(falta), int)
        self.assertEqual(falta, 0)


class EstadoMetaTests(SimpleTestCase):
    def estado(self, precio, ahorrado, fecha_limite):
        return metas.estado_meta(precio, ahorrado, fecha_limite, HOY)

    def test_ahorrado_igual_al_precio_es_cumplida(self):
        self.assertEqual(self.estado(500_000, 500_000, date(2027, 2, 1)), "cumplida")

    def test_ahorrado_mayor_con_fecha_pasada_es_cumplida(self):
        self.assertEqual(self.estado(500_000, 600_000, date(2026, 10, 1)), "cumplida")

    def test_cumplida_con_fecha_de_ayer_es_cumplida(self):
        self.assertEqual(self.estado(500_000, 500_000, date(2026, 11, 13)), "cumplida")

    def test_falta_un_peso_y_fecha_ayer_es_vencida(self):
        self.assertEqual(self.estado(500_000, 499_999, date(2026, 11, 13)), "vencida")

    def test_falta_dinero_y_fecha_hoy_es_en_curso(self):
        self.assertEqual(self.estado(500_000, 100_000, HOY), "en_curso")

    def test_falta_dinero_y_fecha_manana_es_en_curso(self):
        self.assertEqual(self.estado(500_000, 100_000, date(2026, 11, 15)), "en_curso")

    def test_falta_dinero_y_fecha_futura_es_en_curso(self):
        self.assertEqual(self.estado(500_000, 100_000, date(2027, 2, 1)), "en_curso")

    def test_estado_acepta_decimal(self):
        estado = self.estado(Decimal("500000"), Decimal("100000"), date(2026, 11, 13))
        self.assertEqual(estado, "vencida")
