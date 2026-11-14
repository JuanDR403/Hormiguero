from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase

HOY = date(2026, 11, 14)
UMBRAL = 10000
N = 3


def detectar(gastos, umbral=UMBRAL, n=N, hoy=HOY):
    from gastos.reglas.hormiga import detectar_gasto_hormiga

    return detectar_gasto_hormiga(gastos, umbral, n, hoy)


def gasto(monto=4000, fecha=HOY, categoria="alimentacion", descripcion="Tinto"):
    return SimpleNamespace(
        monto=monto, fecha=fecha, categoria=categoria, descripcion=descripcion
    )


def tres(**kwargs):
    return [gasto(**kwargs) for _ in range(3)]


class DetectarGastoHormigaTests(SimpleTestCase):
    def test_tres_compras_pequenas_iguales_forman_grupo(self):
        resultado = detectar(tres())
        self.assertEqual(
            resultado,
            [{"categoria": "alimentacion", "descripcion": "tinto", "cantidad": 3, "total": 12000}],
        )

    def test_dos_compras_no_alcanzan_n(self):
        self.assertEqual(detectar([gasto(), gasto()]), [])

    def test_cuatro_compras_cuentan_todas(self):
        resultado = detectar([gasto() for _ in range(4)])
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["cantidad"], 4)
        self.assertEqual(resultado[0]["total"], 16000)

    def test_monto_igual_al_umbral_cuenta(self):
        resultado = detectar(tres(monto=10000))
        self.assertEqual(resultado[0]["cantidad"], 3)
        self.assertEqual(resultado[0]["total"], 30000)

    def test_monto_un_peso_sobre_el_umbral_no_cuenta(self):
        self.assertEqual(detectar(tres(monto=10001)), [])

    def test_monto_un_peso_bajo_el_umbral_cuenta(self):
        resultado = detectar(tres(monto=9999))
        self.assertEqual(resultado[0]["cantidad"], 3)
        self.assertEqual(resultado[0]["total"], 29997)

    def test_gasto_de_hace_treinta_dias_cuenta(self):
        gastos = [gasto(), gasto(), gasto(fecha=date(2026, 10, 15))]
        resultado = detectar(gastos)
        self.assertEqual(resultado[0]["cantidad"], 3)

    def test_gasto_de_hace_treinta_y_un_dias_no_cuenta(self):
        gastos = [gasto(), gasto(), gasto(fecha=date(2026, 10, 14))]
        self.assertEqual(detectar(gastos), [])

    def test_gasto_de_hoy_cuenta(self):
        gastos = [
            gasto(fecha=HOY - timedelta(days=2)),
            gasto(fecha=HOY - timedelta(days=1)),
            gasto(fecha=HOY),
        ]
        resultado = detectar(gastos)
        self.assertEqual(resultado[0]["cantidad"], 3)

    def test_gasto_futuro_no_cuenta(self):
        gastos = [gasto(), gasto(), gasto(fecha=HOY + timedelta(days=1))]
        self.assertEqual(detectar(gastos), [])

    def test_descripcion_se_normaliza(self):
        gastos = [gasto(descripcion="Tinto"), gasto(descripcion=" tinto "), gasto(descripcion="TINTO")]
        resultado = detectar(gastos)
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["descripcion"], "tinto")
        self.assertEqual(resultado[0]["cantidad"], 3)

    def test_espacios_internos_se_colapsan(self):
        gastos = [
            gasto(descripcion="tinto  grande"),
            gasto(descripcion="Tinto grande"),
            gasto(descripcion=" TINTO   grande "),
        ]
        resultado = detectar(gastos)
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["descripcion"], "tinto grande")
        self.assertEqual(resultado[0]["cantidad"], 3)

    def test_misma_descripcion_en_otra_categoria_es_otro_grupo(self):
        gastos = [
            gasto(categoria="alimentacion"),
            gasto(categoria="alimentacion"),
            gasto(categoria="otros"),
            gasto(categoria="otros"),
        ]
        self.assertEqual(detectar(gastos), [])

    def test_gastos_sin_descripcion_forman_grupo(self):
        resultado = detectar(tres(descripcion=""))
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["descripcion"], "")
        self.assertEqual(resultado[0]["cantidad"], 3)

    def test_un_gasto_sobre_el_umbral_no_se_suma_al_grupo(self):
        gastos = tres(monto=4000) + [gasto(monto=10001)]
        resultado = detectar(gastos)
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["cantidad"], 3)
        self.assertEqual(resultado[0]["total"], 12000)

    def test_grupos_ordenados_por_cantidad_y_total(self):
        gastos = (
            tres(descripcion="a", monto=1000)  # 3 x 1000 = 3000
            + tres(descripcion="b", monto=5000)  # 3 x 5000 = 15000
            + [gasto(descripcion="c", monto=100) for _ in range(4)]  # 4 x 100
        )
        resultado = detectar(gastos)
        self.assertEqual(
            [(g["descripcion"], g["cantidad"], g["total"]) for g in resultado],
            [("c", 4, 400), ("b", 3, 15000), ("a", 3, 3000)],
        )

    def test_empate_se_resuelve_por_categoria_y_descripcion(self):
        gastos = (
            tres(categoria="transporte", descripcion="bus")
            + tres(categoria="alimentacion", descripcion="tinto")
            + tres(categoria="alimentacion", descripcion="arepa")
        )
        resultado = detectar(gastos)
        self.assertEqual(
            [(g["categoria"], g["descripcion"]) for g in resultado],
            [("alimentacion", "arepa"), ("alimentacion", "tinto"), ("transporte", "bus")],
        )

    def test_sin_gastos_devuelve_lista_vacia(self):
        self.assertEqual(detectar([]), [])

    def test_n_es_parametro(self):
        resultado = detectar([gasto(), gasto()], n=2)
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["cantidad"], 2)

    def test_umbral_es_parametro(self):
        self.assertEqual(detectar(tres(monto=4000), umbral=3000), [])


class ConstantesHormigaTests(SimpleTestCase):
    def test_constantes_en_settings(self):
        self.assertEqual(settings.GASTO_HORMIGA_UMBRAL, 10000)
        self.assertEqual(settings.GASTO_HORMIGA_N, 3)


class HormigaConGastoGuardadoTests(TestCase):
    def test_acepta_instancias_de_gasto_con_decimal(self):
        from gastos.models import Gasto

        ana = get_user_model().objects.create_user(
            username="ana@ejemplo.com", email="ana@ejemplo.com", password="clave-de-ejemplo-123"
        )
        for _ in range(3):
            Gasto.objects.create(
                usuario=ana,
                monto=Decimal("4000"),
                fecha=HOY,
                categoria="alimentacion",
                descripcion="Tinto",
            )
        gastos = list(Gasto.objects.filter(usuario=ana))
        resultado = detectar(gastos)
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["total"], 12000)
        self.assertIs(type(resultado[0]["total"]), int)
