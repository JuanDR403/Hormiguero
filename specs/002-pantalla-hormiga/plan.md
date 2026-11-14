# Plan 002 · Pantalla de gasto hormiga

## Decisiones técnicas
- **Regla:** se reutiliza `detectar_gasto_hormiga(gastos, umbral, n, hoy)` y `VENTANA_DIAS` de `gastos/reglas/hormiga.py` sin cambios.
- **Vista** `hormiga(request)` en `gastos/views.py`, con `@login_required` y `@require_safe` (GET y HEAD):
  - `gastos = Gasto.objects.filter(usuario=request.user)`; la ventana y el umbral los aplica la regla, la vista no los repite.
  - `grupos = detectar_gasto_hormiga(gastos, settings.GASTO_HORMIGA_UMBRAL, settings.GASTO_HORMIGA_N, timezone.localdate())`.
  - A cada grupo le añade `categoria_nombre = Gasto.Categoria(grupo["categoria"]).label` (traducción de presentación, no regla de negocio).
  - Contexto: `grupos`, `umbral` (`settings.GASTO_HORMIGA_UMBRAL`), `n` (`settings.GASTO_HORMIGA_N`), `dias` (`VENTANA_DIAS`).
  - Lee `settings` en cada petición (`from django.conf import settings`), para que `override_settings` funcione en las pruebas.
- **URL** `path("hormiga/", views.hormiga, name="hormiga")` en `gastos/urls.py`.
- **Plantilla** `templates/gastos/hormiga.html`, hereda de `base.html`, con la misma estructura que `gastos/lista.html` (`section.bloque`, `div.tabla-desplazable`, `<caption>`, `th.numero` para Veces y Total). Montos con `floatformat:"0g"`; descripción con `default:"Sin descripción"`. Sin sumas ni comparaciones.
- **Encabezado:** en `templates/base.html` se añade `<a href="{% url 'hormiga' %}">Gasto hormiga</a>` dentro del `<nav>` existente, después de «Mis gastos».
- **Estilos:** se reutilizan los de `static/estilos.css`; solo se añaden si hace falta.
- **Estado intermedio esperado:** el implementador-backend no puede escribir en `templates/`. Tras T2, las pruebas de `/hormiga/` que renderizan la página fallarán con `TemplateDoesNotExist: gastos/hormiga.html` (y las del enlace del encabezado, por aserción); deben pasar CA1, el `POST` de CA14 y el resto de la suite (el `HEAD` de CA14 renderiza, así que también espera a T3). Tras T3 todo queda en verde.

## Archivos
- Nuevos:
  - `gastos/tests/test_vista_hormiga.py`
  - `templates/gastos/hormiga.html`
- Modificados:
  - `gastos/views.py` (vista `hormiga`)
  - `gastos/urls.py` (ruta `hormiga/`)
  - `templates/base.html` (enlace en el `<nav>`)
  - `static/estilos.css` (solo si hace falta)
- No se tocan: `gastos/reglas/hormiga.py`, `gastos/models.py`, `gastos/forms.py`, migraciones, `config/settings.py`, pruebas existentes.

## Pruebas
Archivo `gastos/tests/test_vista_hormiga.py`, con `TestCase`. Usuarios `ana@ejemplo.com` y `beto@ejemplo.com` con `create_user`; fechas relativas a `timezone.localdate()`. Gastos de ejemplo: 4.000, `alimentacion`, «Tinto».

| Prueba | Criterio | Comprueba |
|---|---|---|
| `test_sin_sesion_redirige_al_login` | CA1 | redirección a `/login/?next=/hormiga/` |
| `test_con_sesion_usa_la_plantilla_hormiga` | CA2 | 200 y `gastos/hormiga.html` |
| `test_tres_tintos_forman_un_grupo_en_el_contexto` | CA3 | grupo con descripción, categoría, `categoria_nombre`, cantidad 3 y total 12000 |
| `test_la_pagina_muestra_el_grupo` | CA3 | «tinto», «Alimentación», «3» y «$12.000» en el HTML |
| `test_no_muestra_gastos_hormiga_de_otro_usuario` | CA4 | Beto con 3, Ana ve `grupos == []` y el aviso |
| `test_gastos_de_dos_usuarios_no_se_suman` | CA5 | 2 de Ana + 1 de Beto: ninguno ve grupo |
| `test_sin_gastos_muestra_el_aviso` | CA6 | aviso y sin `<table>` |
| `test_gastos_que_no_llegan_a_n_muestran_el_aviso` | CA6 | 2 gastos: aviso |
| `test_usa_n_de_settings` | CA7 | `GASTO_HORMIGA_N=2`: dos bastan |
| `test_usa_umbral_de_settings` | CA7 | `GASTO_HORMIGA_UMBRAL=3000`: 4000 no cuenta |
| `test_gasto_de_hace_treinta_dias_cuenta` | CA8 | `hoy − 30` dentro |
| `test_gasto_de_hace_treinta_y_un_dias_no_cuenta` | CA8 | `hoy − 31` fuera |
| `test_gasto_de_hoy_cuenta` | CA8 | `hoy` dentro |
| `test_grupos_en_el_orden_de_la_regla` | CA9 | grupo de 4 antes que el de 3, en contexto y en el HTML |
| `test_grupo_sin_descripcion_se_muestra_como_sin_descripcion` | CA10 | «Sin descripción» |
| `test_muestra_el_criterio_con_los_valores_por_defecto` | CA11 | «$10.000», «3 o más veces», «30 días»; contexto `umbral`, `n`, `dias` |
| `test_el_criterio_cambia_con_settings` | CA11 | «$5.000», «4 o más veces» |
| `test_encabezado_tiene_enlace_a_hormiga_con_sesion` | CA12 | enlace `/hormiga/` «Gasto hormiga» en `/gastos/` |
| `test_encabezado_sin_sesion_no_tiene_enlace_a_hormiga` | CA12 | sin enlace en `/login/` |
| `test_tabla_accesible_y_un_solo_h1` | CA13 | `<th scope="col">` y un `<h1>` |
| `test_head_esta_permitido` | CA14 | `HEAD` con sesión responde 200 |
| `test_post_no_esta_permitido` | CA14 | 405 y gastos intactos |
| `test_categoria_desconocida_muestra_el_codigo` | CA15 (revisión, hallazgo 3) | 200 y `categoria_nombre` igual al código |

Ajustes tras la revisión: las pruebas de CA8 fijan el día con `mock.patch("gastos.views.timezone.localdate")` (hallazgo 1), y la de CA11 comprueba la frase completa del criterio (hallazgo 2). En la vista, `categoria_nombre` sale de `dict(Gasto.Categoria.choices).get(codigo, codigo)`.

## Verificación
```bash
python manage.py test gastos.tests.test_vista_hormiga   # rojo antes de T2; tras T2 solo fallan las que renderizan; verde tras T3
python manage.py test                                    # todo en verde al final
python manage.py check
coverage run manage.py test && coverage report           # gastos/ ≥ 80 %
```
Revisión manual: `python manage.py runserver`, entrar con un usuario de ejemplo y abrir `/hormiga/` con y sin gastos hormiga.
