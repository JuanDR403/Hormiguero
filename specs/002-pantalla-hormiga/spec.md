# Spec 002 · Pantalla de gasto hormiga

## Problema
La regla de la spec 001 ya detecta las compras pequeñas repetidas, pero el usuario no tiene dónde verlas. Hace falta una pantalla en `/hormiga/` que le muestre sus gastos hormiga: qué se repite, cuántas veces y cuánto suma, y que le explique con qué criterio se detectan.

## Alcance
- Incluye:
  - Vista `hormiga` en `gastos/views.py` con `login_required`, URL `/hormiga/` con nombre `hormiga`.
  - La vista llama a `detectar_gasto_hormiga` (spec 001) con los gastos del usuario con sesión, `settings.GASTO_HORMIGA_UMBRAL`, `settings.GASTO_HORMIGA_N` y `hoy = timezone.localdate()`.
  - Plantilla `templates/gastos/hormiga.html` que hereda de `base.html`: tabla de grupos, aviso si no hay ninguno y texto con el criterio de detección.
  - Enlace «Gasto hormiga» en el encabezado (`templates/base.html`), visible solo con sesión.
  - Pruebas de la vista y de la página en `gastos/tests/`.
- No incluye:
  - Cambios a la regla `detectar_gasto_hormiga`, al modelo `Gasto` ni migraciones.
  - Total general de todos los grupos (queda para la pantalla de Resumen).
  - Lista de los gastos individuales de cada grupo, filtros, cambio de umbral o de N desde la pantalla.
  - Formularios ni acciones que cambien datos.

## Lo que muestra la página
- Un `<h1>` «Gasto hormiga».
- El criterio con los valores de la configuración: «Compras de hasta $10.000 que se repiten 3 o más veces en los últimos 30 días.» (los números salen de `settings` y de la ventana de la regla, no se escriben en la plantilla).
- Con grupos: una tabla con columnas Descripción, Categoría, Veces y Total, una fila por grupo y en el orden que devuelve la regla.
  - Descripción: la normalizada de la regla; si es vacía, «Sin descripción».
  - Categoría: el nombre legible (`Alimentación`, no `alimentacion`).
  - Total: en pesos, con el mismo formato que `/gastos/` (`floatformat:"0g"`, p. ej. `$12.000`).
- Sin grupos: el aviso «No se detectaron gastos hormiga en los últimos 30 días.» y ninguna tabla.

## Criterios de aceptación
Salvo que se diga otra cosa: usuarios `ana@ejemplo.com` y `beto@ejemplo.com`, umbral 10.000, N 3, `hoy = timezone.localdate()` y fechas relativas a `hoy`.

- CA1. Sin sesión, `GET /hormiga/` redirige a `/login/?next=/hormiga/`.
- CA2. Con sesión, `GET /hormiga/` responde 200 con la plantilla `gastos/hormiga.html`.
- CA3. Dados 3 gastos de Ana de 4.000 en `alimentacion` con descripción «Tinto» dentro de la ventana, el contexto `grupos` tiene un grupo con `descripcion` `tinto`, `categoria` `alimentacion`, `categoria_nombre` `Alimentación`, `cantidad` 3 y `total` 12.000; la página muestra «tinto», «Alimentación», «3» y «$12.000».
- CA4. Aislamiento: si Beto tiene 3 gastos hormiga y Ana ninguno, Ana ve `grupos` vacío y el aviso; los gastos de Beto no aparecen.
- CA5. Aislamiento al sumar: 2 gastos «Tinto» de Ana y 1 de Beto no forman grupo para ninguno de los dos.
- CA6. Sin grupos hormiga (Ana sin gastos, o con gastos que no llegan a N), la página muestra «No se detectaron gastos hormiga en los últimos 30 días.» y no hay `<table>`.
- CA7. La vista usa las constantes: con `override_settings(GASTO_HORMIGA_N=2)` dos gastos bastan; con `override_settings(GASTO_HORMIGA_UMBRAL=3000)` los de 4.000 no cuentan.
- CA8. La vista usa la fecha de hoy: con 3 gastos, uno de ellos de `hoy − 30`, se forma el grupo; si ese es de `hoy − 31`, no se forma. Un gasto con fecha `hoy` cuenta.
- CA9. Con dos grupos (uno de 4 compras y otro de 3), `grupos` y las filas de la tabla salen en el orden de la regla: primero el de 4.
- CA10. Un grupo sin descripción se muestra como «Sin descripción».
- CA11. La página muestra el criterio con los valores de la configuración: con los valores por defecto contiene la frase «Compras de hasta $10.000 que se repiten 3 o más veces en los últimos 30 días.»; con `override_settings(GASTO_HORMIGA_UMBRAL=5000, GASTO_HORMIGA_N=4)`, «Compras de hasta $5.000 que se repiten 4 o más veces en los últimos 30 días.». El contexto trae `umbral`, `n` y `dias`. *(Texto alineado con la prueba tras la revisión, hallazgo 2.)*
- CA12. Con sesión, el encabezado de cualquier página que hereda de `base.html` (p. ej. `/gastos/`) tiene un enlace a `/hormiga/` con el texto «Gasto hormiga»; sin sesión no aparece.
- CA13. La tabla tiene encabezados `<th scope="col">` y la página un solo `<h1>`.
- CA14. `/hormiga/` solo acepta lectura: `HEAD` responde 200 y un `POST` responde 405 sin crear ni borrar gastos.
- CA15. Si un grupo tiene una categoría que no está entre las opciones de `Gasto.Categoria` (dato antiguo o cargado fuera del formulario), la página responde 200 y `categoria_nombre` es el código tal cual. *(Añadido tras la revisión, hallazgo 3.)*

## Decisiones tomadas
Respondidas por el desarrollador el 2026-11-14:
- Sin total general: solo el total de cada grupo. El total general queda para la pantalla de Resumen.
- La página explica el criterio con los valores de `settings` (umbral, N) y la ventana de 30 días.

Propuestas por el coordinador y aprobadas por el desarrollador el 2026-11-14:
- El nombre legible de la categoría lo añade la vista (`categoria_nombre`) a partir de `Gasto.Categoria`; la plantilla no traduce códigos.
- La ventana de días que muestra el texto sale de `VENTANA_DIAS` de `gastos/reglas/hormiga.py`, no se repite el 30 en la vista ni en la plantilla.
- La descripción se muestra tal como la normaliza la regla (en minúsculas).
- Texto del enlace del encabezado: «Gasto hormiga».
- Estado intermedio tras el backend: las pruebas que renderizan la plantilla fallan con `TemplateDoesNotExist` hasta que el frontend la crea.

Ajuste del desarrollador al aprobar (2026-11-14):
- La vista usa `require_safe` (acepta `GET` y `HEAD`) en lugar de `require_GET`; `POST` sigue dando 405.
