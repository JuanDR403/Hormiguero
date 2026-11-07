# Plan 2 · Página `/gastos/` (solicitud 2)

## Contexto

La solicitud 1 dejó en `main` el modelo `Gasto` (`gastos/models.py`, `ordering = ["-fecha", "-id"]`), la regla `validar_gasto` (`gastos/reglas/gastos.py`) y `FormularioGasto` (`gastos/forms.py`, sin campo `usuario`, valida centavos, monto > 0 y fecha no futura con `timezone.localdate()`). Falta la pantalla: un usuario con sesión debe ver sus gastos, registrar uno y eliminarlo. Además, la revisión con `web-design-guidelines` señaló que `inicio.html` no tiene viewport, `<main>` ni plantilla base.

**No se tocan:** `models.py`, migraciones, `forms.py`, `reglas/`. Sin JavaScript ni dependencias nuevas. Sin edición, filtros ni paginación.

## Paso 0 · Rama

```
git switch main && git pull && git switch -c feat/pagina-gastos
```
`skills-lock.json` (sin seguimiento en `main`) no se incluye en esta rama.

## Paso 1 · Plantilla base: `templates/base.html` (nuevo)

- `<html lang="es">`, `<meta charset="utf-8">`, `<meta name="viewport" content="width=device-width, initial-scale=1">`.
- `<title>{% block titulo %}{% endblock %} · Hormiguero</title>`, enlace a `static/estilos.css`.
- `<header>` con el nombre del sitio enlazado a `inicio`; si hay sesión, enlace «Mis gastos» y botón «Cerrar sesión» (form POST a `logout` con `{% csrf_token %}`).
- Mensajes de `django.contrib.messages` (ya instalado) en una región `role="status"`.
- `<main>{% block contenido %}{% endblock %}</main>`.
- `templates/autenticacion/base.html` **no se cambia** (las pantallas de acceso siguen con su propia base).

## Paso 2 · `templates/inicio.html` hereda de `base.html`

- Pasa a `{% extends "base.html" %}` con el mismo contenido dentro de `{% block contenido %}` (así gana viewport y `<main>`, que fue el hallazgo de la revisión).
- Para usuarios con sesión: saludo + enlace `<a href="{% url 'lista_gastos' %}">Ver mis gastos</a>`. El botón de cerrar sesión queda en el encabezado de la base.
- Sin sesión: enlaces a iniciar sesión y crear cuenta, igual que hoy.

## Paso 3 · Vistas: `gastos/views.py`

```python
@login_required
def lista_gastos(request):
    if request.method == "POST":
        formulario = FormularioGasto(request.POST)
        if formulario.is_valid():
            gasto = formulario.save(commit=False)
            gasto.usuario = request.user
            gasto.save()
            messages.success(request, "Gasto registrado.")
            return redirect("lista_gastos")
    else:
        formulario = FormularioGasto(initial={"fecha": timezone.localdate()})
    gastos = Gasto.objects.filter(usuario=request.user)  # orden del Meta: más reciente primero
    return render(request, "gastos/lista.html", {"formulario": formulario, "gastos": gastos})


@login_required
@require_POST
def eliminar_gasto(request, pk):
    gasto = get_object_or_404(Gasto, pk=pk, usuario=request.user)  # ajeno → 404
    gasto.delete()
    messages.success(request, "Gasto eliminado.")
    return redirect("lista_gastos")
```
- Sin reglas de negocio en la vista: la validación sigue en `FormularioGasto` → `validar_gasto`.
- Con datos inválidos se vuelve a mostrar la página (200) con los errores y lo escrito.
- GET a eliminar → 405 (por `require_POST`).

## Paso 4 · URLs: `gastos/urls.py`

```python
path("gastos/", views.lista_gastos, name="lista_gastos"),
path("gastos/<int:pk>/eliminar/", views.eliminar_gasto, name="eliminar_gasto"),
```
`LOGIN_URL = "login"` ya existe en `settings.py`, así que `login_required` redirige a `/login/?next=/gastos/`.

## Paso 5 · Plantilla: `templates/gastos/lista.html` (nuevo)

Hereda de `base.html`. Solo muestra datos:
- `<h1>Mis gastos</h1>`.
- **Formulario** `<section aria-labelledby>` con `<h2>Registrar gasto</h2>`, `method="post"`, `{% csrf_token %}`, `novalidate` (como las pantallas de acceso, para ver los errores del servidor); errores generales con `role="alert"`; cada campo con `{% include "autenticacion/_campo.html" %}` (reutiliza label + errores). Botón «Guardar gasto».
- **Lista** `<section>` con `<h2>Gastos registrados</h2>`:
  - Si no hay: «Aún no tienes gastos registrados.»
  - Si hay: `<table>` con `<caption>` y `<th scope="col">` Fecha, Descripción, Categoría, Monto, Acciones. Monto con `{{ gasto.monto|floatformat:"0g" }}` (separador de miles del locale `es-co`, sin filtros propios ni `humanize`). Categoría con `get_categoria_display`. Descripción vacía → «Sin descripción».
  - Cada fila: form POST a `eliminar_gasto` con `{% csrf_token %}` y botón «Eliminar» con `aria-label="Eliminar gasto {descripción o categoría} del {fecha}"`.
- Estilos mínimos en `static/estilos.css` (tabla legible, foco visible, ancho máximo en móvil con desplazamiento horizontal solo de la tabla). Sin JS.

## Paso 6 · Pruebas: `gastos/tests/test_vista_gastos.py` (nuevo)

Usuarios de ejemplo `ana@ejemplo.com` y `beto@ejemplo.com` con `create_user`; `self.client.force_login`. Fechas relativas a `timezone.localdate()` porque la vista no inyecta `hoy`.

| Prueba | Comprueba |
|---|---|
| `test_sin_sesion_redirige_al_login` | GET `/gastos/` → redirección a `/login/?next=/gastos/` |
| `test_sin_sesion_no_elimina` | POST eliminar sin sesión → redirige al login y el gasto sigue |
| `test_lista_solo_gastos_propios` | `context["gastos"]` tiene solo los de Ana; la descripción de Beto no aparece en el HTML |
| `test_lista_del_mas_reciente_al_mas_antiguo` | orden por fecha descendente (y por id en el mismo día) |
| `test_lista_vacia_muestra_aviso` | texto «Aún no tienes gastos registrados.» |
| `test_crear_gasto_asigna_usuario_y_redirige` | POST válido → 302 a `/gastos/`, 1 gasto con `usuario=ana` |
| `test_crear_ignora_usuario_enviado` | POST con `usuario=beto.pk` → el gasto queda de Ana |
| `test_monto_cero_no_guarda` | 200, error «El monto debe ser mayor que cero.», 0 gastos |
| `test_fecha_futura_no_guarda` | mañana → error «La fecha no puede ser futura.», 0 gastos |
| `test_monto_con_centavos_no_guarda` | `1500.50` → error de centavos, 0 gastos |
| `test_fecha_de_hoy_es_valida` | caso límite: hoy se guarda |
| `test_eliminar_gasto_propio` | POST → 302 a `/gastos/` y el gasto ya no existe |
| `test_no_elimina_gasto_ajeno` | Ana intenta eliminar el de Beto → 404 y el gasto sigue |
| `test_eliminar_por_get_no_permitido` | GET → 405 y el gasto sigue |
| `test_pagina_tiene_csrf_y_main` | respuesta contiene `csrfmiddlewaretoken`, `<main`, `lang="es"` y viewport |

En `gastos/tests/test_inicio.py` se agregan:
- `test_con_sesion_enlaza_a_gastos` (contiene `href="/gastos/"`).
- `test_sin_sesion_no_enlaza_a_gastos`.

## Paso 7 · Documentación

`AGENTS.md`, sección «Estado y pantallas previstas»: anotar que existen `templates/base.html` y la página `/gastos/` (lista, crear y eliminar).

## Commits sugeridos

1. `feat: plantilla base con viewport y main; inicio hereda de ella`
2. `feat: página de gastos con lista, registro y eliminación`
3. `test: vistas de gastos y enlace desde inicio`
4. `docs: estado de la página de gastos en AGENTS.md`

Luego push de `feat/pagina-gastos` y PR para revisión de otro integrante (no se fusiona).

## Verificación

1. `python manage.py test` → todo en verde (pruebas nuevas y las existentes de autenticación, gasto e inicio).
2. `python manage.py check` y `python manage.py makemigrations --check --dry-run` → sin migraciones nuevas (confirma que no se tocó el modelo).
3. `python manage.py runserver`: registrar usuario de ejemplo, entrar a `/gastos/` desde inicio, crear un gasto, probar monto 0 / fecha futura / centavos, eliminar; abrir `/gastos/` sin sesión; revisar en ancho de móvil.
4. Revisar `base.html`, `inicio.html` y `gastos/lista.html` con la skill `web-design-guidelines`.
