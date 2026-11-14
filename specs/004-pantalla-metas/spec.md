# Spec 004 · Pantalla de metas de ahorro

## Problema
La spec 003 dejó el modelo `Meta` y la regla de la cuota mensual, pero el usuario no tiene dónde crear sus metas ni ver cuánto debe apartar cada mes. Hace falta una pantalla en `/metas/` con la lista de sus metas, la cuota de cada una y un formulario para crear otras en la misma página, además de un botón para eliminarlas.

## Alcance
- Incluye:
  - Dos reglas puras nuevas en `gastos/reglas/metas.py`: `calcular_falta(precio, ahorrado)` y `estado_meta(precio, ahorrado, fecha_limite, hoy)`.
  - `FormularioMeta` en `gastos/forms.py` (nombre, precio, ahorrado, fecha límite), que valida con `validar_meta`.
  - Vista `lista_metas` (`GET` lista y formulario, `POST` crea) en `/metas/`, con nombre `lista_metas`.
  - Vista `eliminar_meta` (solo `POST`) en `/metas/<pk>/eliminar/`, con nombre `eliminar_meta`.
  - Plantilla `templates/gastos/metas.html`, que hereda de `base.html`.
  - Enlace «Metas de ahorro» en el encabezado (`templates/base.html`), visible solo con sesión.
  - Pruebas de las reglas nuevas, del formulario, de las vistas y de la página en `gastos/tests/`.
- No incluye:
  - Editar una meta ni sumar abonos a `ahorrado`.
  - Cambios al modelo `Meta`, migraciones ni el admin.
  - Cambios a `meses_restantes`, `calcular_cuota_mensual` ni `validar_meta`.
  - Totales de todas las metas (quedan para la pantalla de Resumen).
  - JavaScript.

## Definiciones
- **Falta** (`calcular_falta`): `precio − ahorrado`, entero; nunca negativo (si ahorrado ≥ precio, 0).
- **Estado** (`estado_meta`) devuelve un código:
  - `"cumplida"` si ahorrado ≥ precio (sin importar la fecha);
  - `"vencida"` si no está cumplida y `fecha_limite < hoy` (cuenta el día);
  - `"en_curso"` en otro caso (incluida una fecha límite igual a hoy).
- Nombres que se muestran: `cumplida` → «Cumplida», `vencida` → «Vencida», `en_curso` → «En curso».

## Lo que muestra la página
- Un `<h1>` «Metas de ahorro».
- Una sección «Nueva meta» con el formulario: Nombre, Precio, Ahorrado (con 0 de valor inicial) y Fecha límite (`type="date"`, vacía al principio). Botón «Guardar meta».
- Una sección «Mis metas»:
  - Con metas: una tabla con columnas Nombre, Precio, Ahorrado, Falta, Fecha límite, Meses restantes, Cuota mensual, Estado y Acciones. Una fila por meta, de la fecha límite más próxima a la más lejana (el orden del modelo). Los montos usan `floatformat:"0g"` (p. ej. `$1.200.000`). En Acciones, un botón «Eliminar» por fila.
  - Sin metas: el aviso «Aún no tienes metas de ahorro.» y ninguna tabla.

## Criterios de aceptación
Salvo que se diga otra cosa: usuarios `ana@ejemplo.com` y `beto@ejemplo.com`, y hoy = 2026-11-14 (en las vistas, fijado con `mock.patch`).

Reglas nuevas:
- CA1. `calcular_falta`: precio 1.200.000 y ahorrado 200.000 → 1.000.000; ahorrado = precio → 0; ahorrado > precio → 0 (nunca negativo). Acepta `Decimal` sin centavos y devuelve `int`.
- CA2. `estado_meta`: ahorrado = precio → `cumplida`; ahorrado > precio con fecha pasada → `cumplida`; falta 1 peso y fecha ayer (2026-11-13) → `vencida`; falta dinero y fecha hoy (2026-11-14) → `en_curso`; falta dinero y fecha 2027-02-01 → `en_curso`.
- CA3. `gastos/reglas/metas.py` sigue sin importar Django (prueba de arquitectura existente).

Sesión y aislamiento:
- CA4. Sin sesión, `GET /metas/` redirige a `/login/?next=/metas/`; un `POST /metas/` también redirige y no crea nada; un `POST` a eliminar redirige al login y no borra.
- CA5. Con sesión, `GET /metas/` responde 200 con la plantilla `gastos/metas.html`.
- CA6. Aislamiento: Ana solo ve sus metas en el contexto `metas` y en la página; la meta de Beto no aparece.

Lista:
- CA7. Las metas salen ordenadas por fecha límite ascendente; con la misma fecha, por orden de creación.
- CA8. Cada meta del contexto trae `cuota`, `falta`, `meses`, `estado` y `estado_nombre` calculados con las reglas y hoy = 2026-11-14. Precio 1.000.000, ahorrado 0, límite 2027-02-01 → `cuota` 333.334, `falta` 1.000.000, `meses` 3, `estado` `en_curso`, `estado_nombre` «En curso»; la página muestra «$333.334», «$1.000.000», «3» y «En curso».
- CA9. Una meta cumplida (precio 500.000, ahorrado 500.000) tiene `cuota` 0, `falta` 0 y muestra «Cumplida» y «$0».
- CA10. Una meta vencida (precio 500.000, ahorrado 100.000, límite 2026-10-01) tiene `cuota` 400.000, `meses` 0 y muestra «Vencida» y «$400.000».
- CA11. Sin metas propias (aunque Beto tenga), la página muestra «Aún no tienes metas de ahorro.» y no hay `<table>`.

Crear:
- CA12. Un `POST` válido (nombre «Portátil», precio 1.200.000, ahorrado 200.000, límite 2027-04-30) crea la meta de Ana, redirige a `/metas/` y muestra el mensaje «Meta creada.».
- CA13. Un campo `usuario` enviado en el `POST` se ignora: la meta queda de Ana.
- CA14. Límites que sí guardan: precio 1, ahorrado 0, ahorrado mayor que el precio, fecha límite hoy.
- CA15. Datos inválidos: responde 200, no guarda nada, muestra el error junto al campo (`aria-describedby="id_<campo>_error"`) y el formulario conserva los datos. Un error por campo, sin repetir:
  - nombre vacío o solo espacios → error en `nombre` (el formulario recorta los espacios, así que es el de campo obligatorio de Django);
  - nombre de 101 caracteres → error de longitud; de 100, válido;
  - precio 0 → «El precio debe ser mayor que cero.»;
  - ahorrado −1 → «Lo ahorrado no puede ser negativo.»;
  - fecha límite ayer → «La fecha límite no puede ser pasada.»;
  - precio con centavos (`1500.50`) → «El precio debe ser en pesos enteros, sin centavos.»; ahorrado con centavos → «Lo ahorrado debe ser en pesos enteros, sin centavos.».
- CA16. El formulario vacío trae `ahorrado` con valor inicial 0 y no tiene campo `usuario`.

Eliminar:
- CA17. Ana elimina su meta con `POST`: se borra, redirige a `/metas/` y muestra «Meta eliminada.».
- CA18. Una meta de Beto o una inexistente → 404 y la de Beto sigue existiendo.
- CA19. `GET` a la URL de eliminar → 405 y la meta sigue existiendo.

Página y encabezado:
- CA20. La página tiene un solo `<h1>`, la tabla usa `<th scope="col">`, cada formulario lleva `csrf_token` (con una meta: 3 en la página, contando el de cerrar sesión) y cada botón «Eliminar» tiene un `aria-label` con el nombre de la meta.
- CA21. Con sesión, el encabezado de cualquier página que hereda de `base.html` tiene un enlace a `/metas/` con el texto «Metas de ahorro»; sin sesión no aparece.

## Decisiones tomadas
Respondidas por el desarrollador el 2026-11-14:
- La tabla muestra, además de Nombre, Precio, Ahorrado, Fecha límite y Cuota mensual, las columnas «Falta» y «Meses restantes».
- Columna «Estado» con «Cumplida», «Vencida» o «En curso». La vista lo obtiene de las reglas; la plantilla solo lo muestra.

Propuestas por el coordinador y aprobadas por el desarrollador junto con la spec el 2026-11-14:
- **Vencida cuenta el día** (`fecha_limite < hoy`), no el mes. En la pregunta se dijo «un mes anterior al actual»; con el día, una meta con límite el 5 de noviembre se ve «Vencida» el 14 y no «En curso». Su cuota sigue siendo todo lo que falta.
- `calcular_falta` y `estado_meta` son reglas puras nuevas en `gastos/reglas/metas.py`, para que la vista no haga cálculos de negocio.
- La vista añade a cada meta los atributos `cuota`, `falta`, `meses`, `estado` y `estado_nombre`; la plantilla no calcula nada.
- `ahorrado` es obligatorio en el formulario, con 0 de valor inicial.
- El formulario aplica el límite de 100 caracteres del nombre (decisión de la spec 003) y rechaza centavos con mensaje propio.
- Mensajes «Meta creada.» y «Meta eliminada.»; texto del enlace «Metas de ahorro».
- Estado intermedio tras el backend: las pruebas que renderizan la plantilla fallan con `TemplateDoesNotExist` hasta que el frontend la crea.

Respondidas por el desarrollador el 2026-11-14, después de la revisión:
- «Eliminar» borra sin confirmación ni deshacer, igual que en `/gastos/`.
- `autocomplete="off"` en los formularios del dominio queda para una spec aparte que trate gastos y metas a la vez.
