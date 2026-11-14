# Spec 005 · Resumen

## Problema
Al entrar, el usuario con sesión solo ve un saludo y un enlace. Para saber cuánto lleva gastado en el mes, en qué se le va el dinero y si tiene gasto hormiga, tiene que ir a varias pantallas. La página de inicio (`/`) debe pasar a ser un resumen con el total del mes, el total por categoría y un aviso de gasto hormiga. Sin sesión, la página sigue igual.

## Alcance
- Incluye:
  - Regla pura nueva `resumir_mes(gastos, hoy)` en `gastos/reglas/resumen.py`.
  - Cambio de la vista `inicio` (misma URL `/` y mismo nombre `inicio`): con sesión calcula el resumen; sin sesión no cambia.
  - Cambio de `templates/inicio.html`: bloque con sesión (resumen) y bloque sin sesión (igual que hoy).
  - Pruebas de la regla y de la vista en `gastos/tests/`.
- No incluye:
  - Metas de ahorro en el resumen.
  - Elegir otro mes ni comparar con meses anteriores.
  - Gráficas ni JavaScript.
  - Cambios a `detectar_gasto_hormiga`, al modelo `Gasto`, migraciones, `settings.py` ni `base.html`.
  - Cambios a la página sin sesión.

## Definiciones
- **Mes**: el mes calendario de `hoy`, del día 1 hasta `hoy`, ambos incluidos. Un gasto con fecha posterior a `hoy` no cuenta (no debería existir, porque la fecha no puede ser futura).
- **`resumir_mes(gastos, hoy)`** devuelve un `dict`:
  - `total`: suma (`int`) de los montos de los gastos del mes.
  - `por_categoria`: lista de `dict` con `categoria` (código) y `total` (`int`), solo de las categorías con gastos en el mes, de mayor a menor total; si hay empate, por código ascendente.
- **Aviso de gasto hormiga**: cantidad de grupos que devuelve `detectar_gasto_hormiga` con el umbral y el N de `settings.py` y su ventana de 30 días (no el mes). Si es 0, no hay aviso.

## Lo que muestra la página con sesión
- Título de la pestaña «Resumen».
- Un `<h1>` «Resumen» y el saludo «Hola, {nombre}.».
- Si hay gasto hormiga: «Detectamos 1 gasto hormiga en los últimos 30 días.» (o «Detectamos N gastos hormiga…» si son varios) y un enlace «Ver gasto hormiga» a `/hormiga/`. Sin gasto hormiga, ni el texto ni el enlace.
- Una sección «Total de {mes} de {año}» (p. ej. «Total de noviembre de 2026») con el total en pesos (`floatformat:"0g"`, p. ej. `$25.000`; sin gastos, `$0`).
- Una sección «Por categoría»:
  - Con gastos en el mes: tabla con columnas Categoría y Total, una fila por categoría en el orden de la regla, con el nombre legible de la categoría.
  - Sin gastos en el mes: «No tienes gastos registrados este mes.» y ninguna tabla.
- Sin formularios propios (solo el de cerrar sesión del encabezado).

## Criterios de aceptación
Salvo que se diga otra cosa: usuarios `ana@ejemplo.com` (nombre «Ana») y `beto@ejemplo.com`, hoy = 2026-11-14 (en la vista, fijado con `mock.patch`), umbral 10.000 y N 3.

Regla `resumir_mes`:
- CA1. Periodo: con gastos el 2026-11-01 (5.000), el 2026-11-14 (20.000) y el 2026-10-31 (100.000), `total` es 25.000: el día 1 y hoy cuentan; el último día del mes anterior no.
- CA2. Un gasto del 2026-11-15 (posterior a hoy) y uno del 2025-11-10 (mismo mes de otro año) no cuentan.
- CA3. Con hoy = 2026-12-01, solo cuentan los gastos de ese día.
- CA4. Sin gastos (o sin gastos del mes): `total` 0 y `por_categoria` `[]`.
- CA5. Por categoría: alimentación 4.000 + 6.000, transporte 15.000, hogar 2.000 y salud 50.000 del 2026-10-20 → `por_categoria` = transporte 15.000, alimentación 10.000, hogar 2.000; salud no aparece.
- CA6. Empate: alimentación 5.000 y transporte 5.000 → alimentación primero (código ascendente).
- CA7. Acepta montos `Decimal` sin centavos y devuelve `int` en `total` y en cada `total` de categoría.
- CA8. `gastos/reglas/resumen.py` no importa Django (prueba de arquitectura existente).

Sin sesión:
- CA9. `GET /` responde 200 con `inicio.html`, muestra los enlaces «Iniciar sesión» y «Crear cuenta», no muestra «Resumen» y el contexto no trae `total_mes`. Las pruebas actuales de `test_inicio.py` siguen pasando sin cambios.

Con sesión:
- CA10. `GET /` responde 200 con `inicio.html`, un solo `<h1>` con «Resumen» y el saludo «Hola, Ana.».
- CA11. Con los gastos de CA1 (de Ana): contexto `total_mes` = 25.000; la página muestra «$25.000» y «noviembre de 2026».
- CA12. Aislamiento: los gastos de Beto (del mes y hormiga) no cambian `total_mes`, `por_categoria` ni `cantidad_hormiga` de Ana, y sus categorías no aparecen.
- CA13. Con los gastos de CA5: contexto `por_categoria` con `categoria`, `categoria_nombre` y `total` en el orden de la regla; la página muestra «Transporte» antes que «Alimentación» y «$15.000», «$10.000», «$2.000»; no muestra «Salud».
- CA14. Un gasto con categoría que no está entre las opciones (`antigua`) se muestra con el código tal cual en `categoria_nombre`.
- CA15. Sin gastos en el mes: `total_mes` 0, la página muestra «$0» y «No tienes gastos registrados este mes.» y no hay `<table`.
- CA16. Gasto hormiga: 3 «Tinto» de 4.000 de Ana en la ventana → `cantidad_hormiga` 1, la página muestra «Detectamos 1 gasto hormiga en los últimos 30 días.» y un enlace `<a href="/hormiga/">Ver gasto hormiga</a>`. Con dos grupos (3 «Tinto» y 3 «Pan») → «Detectamos 2 gastos hormiga en los últimos 30 días.».
- CA17. La ventana del aviso es de 30 días, no el mes: 3 «Tinto» del 2026-10-20 dan `cantidad_hormiga` 1 y no suman en `total_mes` (0).
- CA18. Sin gasto hormiga (2 «Tinto»): `cantidad_hormiga` 0 y la página no contiene «Detectamos» ni «Ver gasto hormiga».
- CA19. Usa `GASTO_HORMIGA_UMBRAL` y `GASTO_HORMIGA_N` de settings: con `N=2`, 2 «Tinto» dan aviso; con umbral 3.000, 3 «Tinto» de 4.000 no.
- CA20. Accesibilidad: la tabla usa `<th scope="col">` (2) y la página tiene 1 `csrfmiddlewaretoken` (el de cerrar sesión).

## Decisiones tomadas
Respondidas por el desarrollador el 2026-11-14:
- El «total del mes» es el mes calendario: del día 1 hasta hoy.
- El total por categoría es del mismo mes, solo de las categorías con gastos, de mayor a menor total.
- El aviso de gasto hormiga muestra la cantidad de grupos y un enlace a `/hormiga/`; si no hay, no se muestra nada.
- El resumen no incluye metas de ahorro.

Propuestas por el coordinador y aprobadas por el desarrollador junto con la spec el 2026-11-14:
- Empate en el total por categoría: por código de categoría ascendente, para que el orden sea fijo.
- El aviso usa la ventana de 30 días de la regla de gasto hormiga, no el mes calendario, para que coincida con `/hormiga/`.
- Se mantiene el saludo «Hola, {nombre}.» bajo el `<h1>` «Resumen»; el enlace «Ver mis gastos» se quita porque ya está en el encabezado.
- El nombre del mes sale del filtro `date` de Django en español (`LANGUAGE_CODE = "es-co"`); la vista pasa `hoy` y la plantilla solo lo formatea.
