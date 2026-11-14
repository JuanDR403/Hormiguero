# Plan 005 · Resumen

## Decisiones técnicas
- **Regla** `gastos/reglas/resumen.py` (sin Django), mismo estilo que `gastos/reglas/hormiga.py`:
  - `resumir_mes(gastos, hoy)`: recibe un iterable de objetos con `fecha`, `categoria` y `monto`. Filtra `hoy.replace(day=1) <= fecha <= hoy`, suma con `int(monto)`, agrupa por `categoria` y ordena con `key=lambda c: (-c["total"], c["categoria"])`. Devuelve `{"total": int, "por_categoria": [...]}`.
- **Vista** `inicio` en `gastos/views.py`:
  - Sin sesión: `render(request, "inicio.html")`, igual que hoy.
  - Con sesión: `hoy = timezone.localdate()`; `gastos = Gasto.objects.filter(usuario=request.user)`; `resumen = resumir_mes(gastos, hoy)`; a cada categoría le añade `categoria_nombre` con `dict(Gasto.Categoria.choices).get(codigo, codigo)` (mismo patrón que `hormiga`); `grupos = detectar_gasto_hormiga(gastos, settings.GASTO_HORMIGA_UMBRAL, settings.GASTO_HORMIGA_N, hoy)`.
  - Contexto con sesión: `hoy`, `total_mes`, `por_categoria`, `cantidad_hormiga` (= `len(grupos)`) y `dias` (= `VENTANA_DIAS`).
  - No se cambia la URL ni los decoradores (la vista sigue siendo pública).
- **Plantilla** `templates/inicio.html`:
  - `{% block titulo %}`: «Resumen» con sesión, «Inicio» sin sesión.
  - Rama sin sesión: el contenido actual tal cual (`<h1>Hormiguero</h1>`, descripción y enlaces de acceso).
  - Rama con sesión: `<h1>Resumen</h1>`, saludo, aviso (`{% if cantidad_hormiga %}` con `pluralize` para «gasto/gastos») y enlace «Ver gasto hormiga»; sección «Total de {{ hoy|date:"F \d\e Y" }}» con `${{ total_mes|floatformat:"0g" }}`; sección «Por categoría» con tabla en `.tabla-desplazable` (columnas Categoría y Total, clase `numero`) o el aviso sin gastos.
  - Se reutilizan las clases de `static/estilos.css` (`bloque`, `tabla-desplazable`, `numero`); si el aviso necesita estilo, se añade ahí.
- **Fecha en las pruebas de la vista**: `mock.patch("gastos.views.timezone.localdate", return_value=date(2026, 11, 14))`, como en `test_vista_hormiga.py`.

## Archivos
- Nuevos:
  - `gastos/reglas/resumen.py`
  - `gastos/tests/test_regla_resumen.py`
  - `gastos/tests/test_vista_resumen.py`
- Modificados:
  - `gastos/views.py` (vista `inicio`)
  - `templates/inicio.html`
  - `static/estilos.css` (solo si hace falta)
- No se tocan: `gastos/models.py`, `gastos/migrations/`, `gastos/reglas/hormiga.py`, las demás reglas, `gastos/urls.py`, `gastos/forms.py`, `config/settings.py`, `templates/base.html`, `requirements.txt`, `gastos/tests/test_inicio.py`.

## Pruebas
| Prueba | Criterio | Comprueba |
|---|---|---|
| `test_regla_resumen.py` · periodo | CA1, CA2, CA3 | día 1 y hoy cuentan; mes anterior, futuro y otro año no; hoy = día 1 |
| `test_regla_resumen.py` · vacío | CA4 | total 0 y lista vacía |
| `test_regla_resumen.py` · categorías | CA5, CA6 | suma por categoría, orden por total, empate por código, solo categorías del mes |
| `test_regla_resumen.py` · tipos | CA7 | `Decimal` → `int` |
| `test_arquitectura.py` (existente) | CA8 | la regla no importa Django |
| `test_inicio.py` (existente) y `test_vista_resumen.py` · sin sesión | CA9 | página igual, sin `total_mes` |
| `test_vista_resumen.py` · con sesión | CA10, CA11 | plantilla, `<h1>`, saludo, total y mes |
| `test_vista_resumen.py` · aislamiento | CA12 | gastos de Beto no cuentan |
| `test_vista_resumen.py` · categorías | CA13, CA14, CA15 | contexto, orden en la página, código desconocido, aviso sin gastos |
| `test_vista_resumen.py` · hormiga | CA16, CA17, CA18, CA19 | cantidad, singular y plural, enlace, ventana de 30 días, sin aviso, settings |
| `test_vista_resumen.py` · página | CA20 | `th scope`, 1 `csrfmiddlewaretoken` |

## Verificación
```bash
python manage.py test
coverage run manage.py test && coverage report    # gastos/ ≥ 80 %
python manage.py runserver                         # abrir / con y sin sesión
```
Resultado esperado: todas las pruebas en verde (las existentes y las nuevas) y cobertura de `gastos/` ≥ 80 %.

Estado intermedio tras el backend: las pruebas que buscan textos del resumen en la página fallan hasta que el frontend cambia `inicio.html`; las de contexto ya pasan.
