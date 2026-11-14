# Plan 001 · Regla de gasto hormiga

## Decisiones técnicas
- **Regla pura** en `gastos/reglas/hormiga.py`: `detectar_gasto_hormiga(gastos, umbral, n, hoy)`. Solo usa la biblioteca estándar (`datetime.timedelta`, `collections`). No importa Django ni `settings`: el umbral y N llegan como parámetros. Esto la mantiene probable con `SimpleTestCase` y `hoy` fijo.
- Lee los atributos `monto`, `fecha`, `categoria` y `descripcion` por duck typing; no conoce el modelo.
- `total` se devuelve con `int(...)` para que un `Decimal` sin centavos salga como entero. Nunca `float`.
- **Constantes** `GASTO_HORMIGA_UMBRAL = 10000` y `GASTO_HORMIGA_N = 3` en `config/settings.py`, junto a un comentario breve. La vista futura de `/hormiga/` las leerá y se las pasará a la regla.
- Sin modelo, vista, URL, plantilla ni migración.
- Se reutiliza la prueba de arquitectura existente (`test_arquitectura.py`), que ya recorre todos los archivos de `gastos/reglas/`.

## Archivos
- Nuevos:
  - `gastos/reglas/hormiga.py`
  - `gastos/tests/test_regla_hormiga.py`
- Modificados:
  - `config/settings.py` (dos constantes)
- No se tocan: `gastos/models.py`, `gastos/views.py`, `gastos/urls.py`, `gastos/forms.py`, migraciones, `templates/`, `static/`, `gastos/tests/test_arquitectura.py`.

## Pruebas
Archivo `gastos/tests/test_regla_hormiga.py`. Reglas con `SimpleTestCase` y `hoy = date(2026, 11, 14)`; los gastos de entrada son objetos simples (`types.SimpleNamespace`) salvo en CA15. CA13 y CA15 usan `TestCase`/`settings` de Django.

| Prueba | Criterio | Comprueba |
|---|---|---|
| `test_tres_compras_pequenas_iguales_forman_grupo` | CA1 | grupo `alimentacion`/`tinto`, cantidad 3, total 12000 |
| `test_dos_compras_no_alcanzan_n` | CA2 | lista vacía con n − 1 |
| `test_cuatro_compras_cuentan_todas` | CA3 | cantidad 4 con n + 1 |
| `test_monto_igual_al_umbral_cuenta` | CA4 | 10000 cuenta |
| `test_monto_un_peso_sobre_el_umbral_no_cuenta` | CA4 | 10001 no cuenta |
| `test_monto_un_peso_bajo_el_umbral_cuenta` | CA4 | 9999 cuenta |
| `test_gasto_de_hace_treinta_dias_cuenta` | CA5 | 2026-10-15 cuenta |
| `test_gasto_de_hace_treinta_y_un_dias_no_cuenta` | CA5 | 2026-10-14 no cuenta |
| `test_gasto_de_hoy_cuenta` | CA5 | hoy cuenta |
| `test_gasto_futuro_no_cuenta` | CA6 | hoy + 1 no cuenta |
| `test_descripcion_se_normaliza` | CA7 | «Tinto», « tinto », «TINTO» → un grupo `tinto` |
| `test_espacios_internos_se_colapsan` | Definiciones (grupo) | «tinto  grande» y variantes → un grupo `tinto grande` |
| `test_un_gasto_sobre_el_umbral_no_se_suma_al_grupo` | CA4, Definiciones | 3 × 4000 + 1 × 10001 → cantidad 3, total 12000 |
| `test_misma_descripcion_en_otra_categoria_es_otro_grupo` | CA8 | dos categorías no se suman |
| `test_gastos_sin_descripcion_forman_grupo` | CA9 | descripción `""` |
| `test_grupos_ordenados_por_cantidad_y_total` | CA10 | orden del resultado |
| `test_empate_se_resuelve_por_categoria_y_descripcion` | Resultado (orden) | empate en cantidad y total → categoría y descripción ascendentes |
| `test_sin_gastos_devuelve_lista_vacia` | CA11 | `[]` |
| `test_n_es_parametro` | CA12 | n = 2 basta con dos |
| `test_umbral_es_parametro` | CA12 | umbral 3000 excluye 4000 |
| `test_constantes_en_settings` | CA13 | `GASTO_HORMIGA_UMBRAL == 10000`, `GASTO_HORMIGA_N == 3` |
| (existente) `test_las_reglas_no_importan_django_ni_el_resto_de_la_app` | CA14 | `hormiga.py` sin Django |
| `test_acepta_instancias_de_gasto_con_decimal` | CA15 | `Gasto` guardado de `ana@ejemplo.com`, `total` es `int` |

## Verificación
```bash
python manage.py test gastos.tests.test_regla_hormiga   # rojo antes de T2, verde después
python manage.py test                                    # todo en verde
coverage run manage.py test && coverage report           # gastos/ ≥ 80 %
```
