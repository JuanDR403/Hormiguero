# Plan 003 · Metas de ahorro (backend)

## Decisiones técnicas
- **Reglas puras** en `gastos/reglas/metas.py`. Solo biblioteca estándar; no importan Django ni `settings`. Reciben `hoy` como parámetro.
  - `meses_restantes(fecha_limite, hoy)`: `max(0, (fecha_limite.year * 12 + fecha_limite.month) - (hoy.year * 12 + hoy.month))`.
  - `calcular_cuota_mensual(precio, ahorrado, fecha_limite, hoy)`: `falta = int(precio) - int(ahorrado)`; si `falta <= 0` → 0; si meses = 0 → `falta`; si no, techo entero `-(-falta // meses)`. Aritmética entera, nunca `float` ni `math.ceil` sobre una división real.
  - `validar_meta(nombre, precio, ahorrado, fecha_limite, hoy)`: mismo estilo que `validar_gasto` (diccionario de errores, mensajes en español). La usará el formulario de la spec de `/metas/`.
- **Modelo** `Meta` en `gastos/models.py`, junto a `Gasto`:
  - `usuario = ForeignKey(AUTH_USER_MODEL, on_delete=CASCADE, related_name="metas")`
  - `nombre = CharField(max_length=100)`
  - `precio = DecimalField(max_digits=12, decimal_places=0)`
  - `ahorrado = DecimalField(max_digits=12, decimal_places=0, default=0)`
  - `fecha_limite = DateField()`
  - `creado = DateTimeField(auto_now_add=True)`
  - `class Meta`: `ordering = ["fecha_limite", "id"]`; `CheckConstraint` `meta_precio_positivo` (`precio > 0`) y `meta_ahorrado_no_negativo` (`ahorrado >= 0`).
  - `__str__`: `f"{self.nombre} · ${self.precio}"`.
  - Nota: el modelo se llama `Meta` y lleva su propia clase interna `Meta`; Django lo admite.
- **Migración** `0002_meta.py` generada con `python manage.py makemigrations gastos`. No se toca `0001_initial.py`.
- Se reutiliza `test_arquitectura.py`, que ya recorre `gastos/reglas/`.
- Sin vista, URL, formulario, plantilla ni admin.

## Archivos
- Nuevos:
  - `gastos/reglas/metas.py`
  - `gastos/migrations/0002_meta.py` (generada)
  - `gastos/tests/test_regla_metas.py`
  - `gastos/tests/test_modelo_meta.py`
- Modificados:
  - `gastos/models.py` (modelo `Meta`)
- No se tocan: `gastos/views.py`, `gastos/urls.py`, `gastos/forms.py`, `gastos/admin.py`, `gastos/migrations/0001_initial.py`, `config/settings.py`, `templates/`, `static/`, `gastos/tests/test_arquitectura.py`.

## Pruebas
`test_regla_metas.py`: `SimpleTestCase`, `HOY = date(2026, 11, 14)`. `test_modelo_meta.py`: `TestCase`, usuarios `ana@ejemplo.com` y `beto@ejemplo.com` con `create_user`.

| Prueba | Criterio | Comprueba |
|---|---|---|
| `test_meses_restantes_ignora_el_dia` | CA1 | 2027-02-10 → 3 |
| `test_mismo_mes_da_cero_meses` | CA2 | 2026-11-30 → 0 |
| `test_mes_siguiente_da_un_mes` | CA2 | 2026-12-01 → 1 |
| `test_meses_restantes_con_cambio_de_anio` | CA3 | 2027-01-15 → 2 |
| `test_fecha_pasada_da_cero_meses` | CA4 | 2026-10-01 → 0 |
| `test_cuota_divide_lo_que_falta_entre_los_meses` | CA5 | 200.000 |
| `test_cuota_se_redondea_hacia_arriba` | CA6 | 333.334 |
| `test_division_exacta_no_suma_un_peso` | CA7 | 300.000 |
| `test_falta_un_peso_da_cuota_uno` | CA8 | 1 |
| `test_meta_cumplida_exacta_da_cuota_cero` | CA9 | ahorrado = precio → 0 |
| `test_ahorrado_mayor_que_precio_da_cuota_cero` | CA9 | nunca negativa |
| `test_meta_cumplida_y_vencida_da_cuota_cero` | CA9 | fecha pasada → 0 |
| `test_sin_meses_en_el_mes_actual_cuota_es_lo_que_falta` | CA10 | 400.000 |
| `test_fecha_pasada_cuota_es_lo_que_falta` | CA10 | 400.000 |
| `test_cuota_acepta_decimal_y_devuelve_int` | CA11 | tipo `int` |
| `test_nombre_vacio_es_error` | CA12 | `""` y `"   "` |
| `test_nombre_valido` | CA12 | «Portátil» sin error |
| `test_precio_cero_es_error` | CA13 | 0 |
| `test_precio_uno_es_valido` | CA13 | 1 |
| `test_precio_none_es_error` | CA13 | `None` |
| `test_ahorrado_negativo_es_error` | CA14 | −1 |
| `test_ahorrado_cero_es_valido` | CA14 | 0 |
| `test_ahorrado_mayor_que_precio_es_valido` | CA14 | sin error |
| `test_ahorrado_none_es_error` | CA14 | `None` |
| `test_fecha_limite_ayer_es_error` | CA15 | 2026-11-13 |
| `test_fecha_limite_hoy_es_valida` | CA15 | 2026-11-14 |
| `test_fecha_limite_none_es_error` | CA15 | `None` |
| `test_meta_valida_no_tiene_errores` | CA16 | `{}` |
| `test_meta_se_guarda_con_sus_campos` | CA17 | campos y `ahorrado` por defecto 0 |
| `test_base_de_datos_rechaza_precio_cero` | CA18 | `IntegrityError` |
| `test_base_de_datos_rechaza_ahorrado_negativo` | CA18 | `IntegrityError` |
| `test_usuario_solo_ve_sus_metas` | CA19 | `ana.metas` sin las de beto |
| `test_borrar_usuario_borra_sus_metas` | CA19 | cascada |
| (existente) `test_las_reglas_no_importan_django_ni_el_resto_de_la_app` | CA20 | `metas.py` sin Django |

## Verificación
```bash
python manage.py test gastos.tests.test_regla_metas gastos.tests.test_modelo_meta   # rojo antes de T2, verde después
python manage.py makemigrations --check --dry-run                                   # sin cambios pendientes tras T2
python manage.py test                                                                # todo en verde
coverage run manage.py test && coverage report                                       # gastos/ ≥ 80 %
```
