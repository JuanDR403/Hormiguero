# Plan 004 · Pantalla de metas de ahorro

## Decisiones técnicas
- **Reglas** (`gastos/reglas/metas.py`, sin Django):
  - `calcular_falta(precio, ahorrado)` → `max(0, int(precio) − int(ahorrado))`.
  - `estado_meta(precio, ahorrado, fecha_limite, hoy)` → `"cumplida"`, `"vencida"` o `"en_curso"` según la spec.
  - Se reutilizan sin cambios `meses_restantes`, `calcular_cuota_mensual` y `validar_meta`.
- **Formulario** `FormularioMeta(forms.ModelForm)` en `gastos/forms.py`, mismo patrón que `FormularioGasto`:
  - `fields = ["nombre", "precio", "ahorrado", "fecha_limite"]`; etiquetas «Nombre», «Precio», «Ahorrado», «Fecha límite».
  - `fecha_limite` con `DateInput(attrs={"type": "date"})`; `ahorrado` con `initial=0` y obligatorio.
  - `error_messages` de `max_decimal_places` para precio y ahorrado con los textos de la spec.
  - `__init__(..., hoy=None)` con `timezone.localdate()` por defecto; `clean()` llama a `validar_meta` y solo añade el error si el campo no falló antes.
- **Vistas** en `gastos/views.py`:
  - `lista_metas` con `login_required`. En `POST` valida, asigna `usuario = request.user`, guarda, mensaje «Meta creada.» y redirige a `lista_metas`. Lista `Meta.objects.filter(usuario=request.user)` y a cada meta le añade `cuota`, `falta`, `meses`, `estado` y `estado_nombre` con las reglas y `hoy = timezone.localdate()`. El nombre legible sale de un diccionario en la vista (`NOMBRES_ESTADO`), no de la plantilla.
  - `eliminar_meta` con `login_required` y `require_POST`; `get_object_or_404(Meta, pk=pk, usuario=request.user)`; mensaje «Meta eliminada.»; redirige a `lista_metas`.
- **URLs** en `gastos/urls.py`: `metas/` (`lista_metas`) y `metas/<int:pk>/eliminar/` (`eliminar_meta`).
- **Plantilla** `templates/gastos/metas.html`, calcada de `templates/gastos/lista.html`: hereda de `base.html`, reutiliza `autenticacion/_campo.html`, tabla dentro de `.tabla-desplazable`, columnas numéricas con clase `numero`, `aria-label` «Eliminar meta {{ meta.nombre }}». Se reutilizan los estilos de `static/estilos.css`; si hace falta algo para el estado, se añade ahí.
- **Encabezado**: enlace «Metas de ahorro» en `templates/base.html`, después de «Gasto hormiga».
- **Fecha en las pruebas de vistas**: `mock.patch("django.utils.timezone.localdate", return_value=date(2026, 11, 14))`, que afecta a la vista y al formulario porque ambos usan `timezone.localdate()`.

## Archivos
- Nuevos:
  - `gastos/tests/test_vista_metas.py`
  - `gastos/tests/test_formulario_meta.py` (opcional: puede ir dentro de `test_vista_metas.py`)
  - `templates/gastos/metas.html`
- Modificados:
  - `gastos/reglas/metas.py` (dos funciones nuevas)
  - `gastos/tests/test_regla_metas.py` (pruebas de las dos funciones nuevas)
  - `gastos/forms.py`, `gastos/views.py`, `gastos/urls.py`
  - `templates/base.html` (enlace)
  - `static/estilos.css` (solo si hace falta)
- No se tocan: `gastos/models.py`, `gastos/migrations/`, `gastos/admin.py`, las reglas existentes, `config/settings.py`, `requirements.txt`.

## Pruebas
| Prueba | Criterio | Comprueba |
|---|---|---|
| `test_regla_metas.py` · falta | CA1 | resta, límite 0, nunca negativa, `Decimal` → `int` |
| `test_regla_metas.py` · estado | CA2 | cumplida, vencida (ayer), en curso (hoy y futura) |
| `test_arquitectura.py` (existente) | CA3 | la regla no importa Django |
| `test_vista_metas.py` · sesión | CA4, CA5 | redirección al login en GET, POST y eliminar; 200 y plantilla |
| `test_vista_metas.py` · aislamiento | CA6, CA11 | solo metas propias; aviso sin metas |
| `test_vista_metas.py` · orden | CA7 | fecha límite ascendente, luego id |
| `test_vista_metas.py` · datos de la fila | CA8, CA9, CA10 | atributos del contexto y textos de la página |
| `test_vista_metas.py` · crear | CA12, CA13, CA14 | guarda con usuario de la sesión, ignora `usuario`, límites válidos |
| `test_vista_metas.py` · inválidos | CA15, CA16 | un error por campo, `aria-describedby`, nada guardado, valor inicial |
| `test_vista_metas.py` · eliminar | CA17, CA18, CA19 | propia, ajena/inexistente 404, GET 405 |
| `test_vista_metas.py` · página | CA20, CA21 | un `<h1>`, `th scope`, 3 `csrfmiddlewaretoken`, `aria-label`, enlace del encabezado |

## Verificación
```bash
python manage.py test
coverage run manage.py test && coverage report    # gastos/ ≥ 80 %
python manage.py runserver                         # abrir /metas/ con sesión
```
Resultado esperado: todas las pruebas en verde (las existentes y las nuevas) y cobertura de `gastos/` ≥ 80 %.
