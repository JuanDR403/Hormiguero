import ast
from pathlib import Path

from django.test import SimpleTestCase

CARPETA_REGLAS = Path(__file__).resolve().parent.parent / "reglas"


def modulos_importados(archivo):
    arbol = ast.parse(archivo.read_text(encoding="utf-8"))
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            for alias in nodo.names:
                yield alias.name
        elif isinstance(nodo, ast.ImportFrom):
            yield "." * nodo.level + (nodo.module or "")


class ReglasPurasTests(SimpleTestCase):
    def test_hay_reglas_que_revisar(self):
        self.assertTrue(list(CARPETA_REGLAS.glob("*.py")))

    def test_las_reglas_no_importan_django_ni_el_resto_de_la_app(self):
        for archivo in sorted(CARPETA_REGLAS.glob("*.py")):
            for modulo in modulos_importados(archivo):
                with self.subTest(archivo=archivo.name, modulo=modulo):
                    self.assertFalse(
                        modulo == "django" or modulo.startswith("django."),
                        f"{archivo.name} importa {modulo}: las reglas no usan Django.",
                    )
                    self.assertFalse(
                        modulo.startswith("gastos") and "reglas" not in modulo,
                        f"{archivo.name} importa {modulo}: las reglas no usan la app.",
                    )
                    self.assertFalse(
                        modulo.startswith(".."),
                        f"{archivo.name} importa {modulo}: las reglas no salen de reglas/.",
                    )
