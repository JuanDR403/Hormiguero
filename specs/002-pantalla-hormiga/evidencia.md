# Evidencia 002 · Pantalla de gasto hormiga

## Incidencias del arnés

### Coordinador, lectura del código (paso 1)
- `git ls-files gastos/tests specs templates static config` rechazado: `PreToolUse:Bash hook error: [python "$CLAUDE_PROJECT_DIR/.claude/hooks/limitar_agente.py" coordinador]: coordinador solo puede ejecutar: git status; git diff; git log; git fetch; git pull; git switch; git add; git commit.`
- Se usó `git log --stat` para listar los archivos de pruebas y plantillas, y Read para leerlos.

### Coordinador, aprobación (paso 2)
- El desarrollador aprobó la spec, el plan y las tareas con las cuatro propuestas del coordinador y un ajuste: `require_safe` en lugar de `require_GET` (acepta HEAD; POST sigue en 405). Se editaron CA14, las decisiones de `spec.md` y el plan (prueba nueva `test_head_esta_permitido`) antes del commit `0a68eba docs: spec 002 pantalla-hormiga`.
- `git fetch` y `git pull --ff-only` funcionaron (`Ya está actualizado.`); la rama `feat/pantalla-hormiga` sale de `main` en `71a0209`. El commit con la línea `Co-Authored-By` funcionó a la primera.

### Probador, T1: entorno
- Según el probador, `python manage.py test` literal falla con `ModuleNotFoundError: No module named 'django'` (el venv no está activo y el hook no deja activarlo). Usó `.venv/bin/python manage.py test ...`, que el hook aceptó. Hay que tenerlo en cuenta en los encargos siguientes y en el arnés (los agentes y `AGENTS.md` dicen `python manage.py test`).
- La herramienta Bash truncó el medio de la salida (~7.800 caracteres), así que el primer informe no trae la salida completa. Se volvió a encargar al probador que la ejecutara con `-v 2` (ver «Rojo, segunda ejecución»).

## Rojo (T1)

### Informe del probador, primera ejecución

```
ESTADO: rojo confirmado (21 de 22 pruebas nuevas fallan por falta de código; 1 pasa a propósito, ver abajo)

ARCHIVOS:
- Creado: /home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_vista_hormiga.py (clase VistaHormigaTests, TestCase, 22 pruebas con los nombres exactos de la tabla del plan; no añadí ninguna extra). No toqué nada más.

EVIDENCIA:
Nota importante sobre los comandos: `python manage.py test` literal falla en este entorno con `ModuleNotFoundError: No module named 'django'` (el venv no está activo y el hook no deja activarlo). Ejecuté `.venv/bin/python manage.py test ...`, que el hook sí aceptó. Si T2 y T3 usan `python` a secas, tendrán el mismo problema.

La salida literal y completa NO me la pude traer: la herramienta Bash trunca el medio de la salida (~7.800 caracteres) en ambos comandos. Lo que sigue es lo que sí se vio íntegro y lo que se deduce.

Comando 1: `.venv/bin/python manage.py test gastos.tests.test_vista_hormiga`
- Cabecera literal: `Creating test database for alias 'default'...` y la línea de progreso `FF.FEEEEFEEFFFEFFFFEEE`
- Cierre literal: `Ran 22 tests in 12.691s` / `FAILED (failures=11, errors=10)` / `Found 22 test(s).` / `System check identified no issues (0 silenced).`
- Pasa 1 de 22 (el tercer punto de la línea de progreso).

Comando 2: `.venv/bin/python manage.py test`
- Línea de progreso literal: `.....................................................FF.FEEEEFEEFFFEFFFFEEE.........................................................` Es decir, 53 pruebas existentes en verde antes, las 22 nuevas con el mismo patrón de arriba y 57 existentes en verde después.
- Cierre literal: `Ran 132 tests in 29.199s` / `FAILED (failures=11, errors=10)`. Con las 22 nuevas son 110 existentes, todas en verde. Todos los fallos están en `test_vista_hormiga`.

Por qué falla cada prueba (la URL /hormiga/ no existe, así que responde 404):
- FAIL con `404 != 302` o `404 != 405`:
  - test_sin_sesion_redirige_al_login (esperaba 302 hacia /login/?next=/hormiga/)
  - test_post_no_esta_permitido (esperaba 405)
- FAIL con `404 != 200` (assertContains, assertEqual del status o assertTemplateUsed):
  - test_con_sesion_usa_la_plantilla_hormiga
  - test_la_pagina_muestra_el_grupo
  - test_sin_gastos_muestra_el_aviso
  - test_gastos_que_no_llegan_a_n_muestran_el_aviso
  - test_muestra_el_criterio_con_los_valores_por_defecto
  - test_el_criterio_cambia_con_settings
  - test_tabla_accesible_y_un_solo_h1
  - test_head_esta_permitido
- FAIL por aserción sobre el enlace, porque base.html aún no lo tiene: test_encabezado_tiene_enlace_a_hormiga_con_sesion
- ERROR `KeyError: 'grupos'` (la respuesta 404 no trae contexto):
  - test_tres_tintos_forman_un_grupo_en_el_contexto
  - test_no_muestra_gastos_hormiga_de_otro_usuario
  - test_gastos_de_dos_usuarios_no_se_suman
  - test_usa_n_de_settings
  - test_usa_umbral_de_settings
  - test_gasto_de_hace_treinta_dias_cuenta
  - test_gasto_de_hace_treinta_y_un_dias_no_cuenta
  - test_gasto_de_hoy_cuenta
  - test_grupos_en_el_orden_de_la_regla
  - test_grupo_sin_descripcion_se_muestra_como_sin_descripcion
- Pasa sin código nuevo: test_encabezado_sin_sesion_no_tiene_enlace_a_hormiga. Es una guarda de regresión de CA12 («sin sesión no aparece»), válida pero no fallaba antes. Si el coordinador la quiere estrictamente roja, habría que quitarla.

No pude asignar con certeza cada nombre a «FAIL» o «ERROR» en las pruebas cuyo cuerpo quedó en la parte truncada. La clasificación de arriba sale del cuerpo de cada prueba y de los tracebacks que sí vi (todos de la forma 404 != X o KeyError 'grupos'). Ningún fallo es de la propia prueba: ninguno es ImportError, NameError ni error de sintaxis.

Detalles de diseño:
- El formato de monto es `$12.000`, con punto como separador, porque `LANGUAGE_CODE = "es-co"` y lista.html usa `${{ gasto.monto|floatformat:"0g" }}`. test_vista_gastos.py no comprueba montos en el HTML.
- La prueba del enlace del encabezado exige el marcado `<a href="/hormiga/">Gasto hormiga</a>` (con espacios en blanco opcionales), tal como lo fija el plan. Si el frontend añade atributos al `<a>`, esa aserción fallará.
- `test_la_pagina_muestra_el_grupo` comprueba el «3» con la expresión regular `>\s*3\s*</td>`. Acopla a que la celda de «Veces» sea un `<td>` con solo el número.
- `test_tabla_accesible_y_un_solo_h1` exige exactamente 1 `<h1` y 4 `<th scope="col"` (Descripción, Categoría, Veces, Total).
- `test_grupos_en_el_orden_de_la_regla` busca «tinto» y «pan» como subcadenas del HTML completo. Si el encabezado, el criterio o la descripción de la página contienen «pan» antes de la tabla, la prueba daría un falso resultado. Con el texto de la spec no ocurre.

NECESITA DE OTRO AGENTE: nada para escribir las pruebas. Para T2 y T3:
- T2 (implementador-backend) debe crear la vista, la ruta y las claves de contexto `grupos` (con `categoria_nombre`), `umbral`, `n` y `dias`, como dice el plan.
- T3 (implementador-frontend) debe crear `templates/gastos/hormiga.html` y el enlace en `templates/base.html`.

PREGUNTAS PARA EL DESARROLLADOR: ninguna.
```

### Informe del probador, segunda ejecución (`-v 2`, sin cambios en archivos)

```
ESTADO: rojo confirmado
ARCHIVOS: ninguno (no se modificó nada)

EVIDENCIA:
Comandos ejecutados:
1. `.venv/bin/python manage.py test gastos.tests.test_vista_hormiga -v 2`. Cierre: `Ran 22 tests in 12.609s` / `FAILED (failures=11, errors=10)`.
2. Tres ejecuciones con `-k` para recuperar las líneas que la salida truncó.
3. `.venv/bin/python manage.py test`. Cierre: `Ran 132 tests in 29.181s` / `FAILED (failures=11, errors=10)`.

Los 132 - 22 = 110 tests restantes pasan. Los 11 fallos y 10 errores del total son los mismos 11 y 10 del archivo de la vista, así que los únicos rojos están en test_vista_hormiga.

Tabla (clase `VistaHormigaTests`; la línea de error es la última del traceback):

| prueba | resultado | línea literal del error |
|---|---|---|
| test_con_sesion_usa_la_plantilla_hormiga | FAIL | AssertionError: 404 != 200 |
| test_el_criterio_cambia_con_settings | FAIL | AssertionError: 404 != 200 : Couldn't retrieve content: Response code was 404 (expected 200) |
| test_encabezado_sin_sesion_no_tiene_enlace_a_hormiga | ok | (pasa sin código nuevo, ver observación) |
| test_encabezado_tiene_enlace_a_hormiga_con_sesion | FAIL | AssertionError: Regex didn't match: '<a href="/hormiga/">\\s*Gasto hormiga\\s*</a>' not found in '...' (el HTML de /gastos/ solo trae `<a href="/gastos/">Mis gastos</a>` en el `<nav>`) |
| test_gasto_de_hace_treinta_dias_cuenta | ERROR | KeyError: 'grupos' |
| test_gasto_de_hace_treinta_y_un_dias_no_cuenta | ERROR | KeyError: 'grupos' |
| test_gasto_de_hoy_cuenta | ERROR | KeyError: 'grupos' |
| test_gastos_de_dos_usuarios_no_se_suman | ERROR | KeyError: 'grupos' |
| test_gastos_que_no_llegan_a_n_muestran_el_aviso | FAIL | AssertionError: 404 != 200 : Couldn't retrieve content: Response code was 404 (expected 200) |
| test_grupo_sin_descripcion_se_muestra_como_sin_descripcion | ERROR | KeyError: 'grupos' |
| test_grupos_en_el_orden_de_la_regla | ERROR | KeyError: 'grupos' |
| test_head_esta_permitido | FAIL | AssertionError: 404 != 200 |
| test_la_pagina_muestra_el_grupo | FAIL | AssertionError: 404 != 200 : Couldn't retrieve content: Response code was 404 (expected 200) |
| test_muestra_el_criterio_con_los_valores_por_defecto | FAIL | AssertionError: 404 != 200 : Couldn't retrieve content: Response code was 404 (expected 200) |
| test_no_muestra_gastos_hormiga_de_otro_usuario | ERROR | KeyError: 'grupos' |
| test_post_no_esta_permitido | FAIL | AssertionError: 404 != 405 |
| test_sin_gastos_muestra_el_aviso | FAIL | AssertionError: 404 != 200 : Couldn't retrieve content: Response code was 404 (expected 200) |
| test_sin_sesion_redirige_al_login | FAIL | AssertionError: 404 != 302 : Response didn't redirect as expected: Response code was 404 (expected 302) |
| test_tabla_accesible_y_un_solo_h1 | FAIL | AssertionError: 404 != 200 : Couldn't retrieve content: Response code was 404 (expected 200) |
| test_tres_tintos_forman_un_grupo_en_el_contexto | ERROR | KeyError: 'grupos' |
| test_usa_n_de_settings | ERROR | KeyError: 'grupos' |
| test_usa_umbral_de_settings | ERROR | KeyError: 'grupos' |

Resumen: 21 en rojo (11 FAIL y 10 ERROR) y 1 ok. Los FAIL son 404 porque la URL /hormiga/ no existe, salvo el del enlace del encabezado, que falla porque el encabezado no tiene el enlace. Los ERROR son `KeyError: 'grupos'`: la respuesta es un 404 y no tiene ese dato en el contexto. Ninguno falla por un error de la propia prueba.

Observación: `test_encabezado_sin_sesion_no_tiene_enlace_a_hormiga` pasa sin código nuevo. Es una prueba negativa de regresión: comprueba que el encabezado sin sesión no tenga el enlace, y hoy no lo tiene. Es el único de los 22 que pasa en rojo, y es esperado. Si se quiere que todas fallen por falta de código, habría que cambiarla.

NECESITA DE OTRO AGENTE: nada
PREGUNTAS PARA EL DESARROLLADOR: ninguna
```

Nota: la tabla del plan tenía 22 pruebas tras añadir `test_head_esta_permitido`; el probador escribió las 22 con los nombres del plan. El informe no trae las 22 líneas `... ok|FAIL|ERROR` de `-v 2` copiadas, pero sí la línea literal de error de cada prueba.

**Decisión del coordinador:** se mantiene `test_encabezado_sin_sesion_no_tiene_enlace_a_hormiga` aunque pase sin código nuevo. Protege la parte «sin sesión no aparece» de CA12 frente a un enlace puesto fuera del `{% if user.is_authenticated %}`, y su pareja `test_encabezado_tiene_enlace_a_hormiga_con_sesion` sí está en rojo. Las restricciones de marcado que señala el probador (enlace sin atributos extra, celda «Veces» con solo el número, 4 `th`) se le pasan al implementador-frontend en su encargo.

## Verde parcial (T2, backend)

### Informe del implementador-backend

```
ESTADO: verde parcial, como lo prevé el plan. T2 está hecha y solo fallan las pruebas que esperan la plantilla de T3.

ARCHIVOS:
- /home/jdrickxd/Documentos/Proyecto_Integrador/gastos/views.py: imports de `settings`, `require_safe` y `VENTANA_DIAS`/`detectar_gasto_hormiga`, y la vista `hormiga` con `@login_required` y `@require_safe`.
- /home/jdrickxd/Documentos/Proyecto_Integrador/gastos/urls.py: `path("hormiga/", views.hormiga, name="hormiga")`.

EVIDENCIA:
- `.venv/bin/python manage.py check`: `System check identified no issues (0 silenced).`
- `.venv/bin/python manage.py makemigrations --check --dry-run`: `No changes detected`.
- `.venv/bin/python manage.py test gastos.tests.test_vista_hormiga -v 2`: la salida se truncó. Muestra los 22 resultados, pero la línea `Ran/FAILED` final se perdió. Conté 3 ok, 1 FAIL y 18 ERROR, que suman 22.
- `.venv/bin/python manage.py test`: la salida también se truncó y no pude leer las líneas finales literales (`Ran ...`, `FAILED ...`). La línea de puntos fue `.....................................................EE.FEEEEEEEEEEE.E.EEEE.........................................................`. Contando, son unas 132 pruebas, con las 19 fallas dentro de test_vista_hormiga.
- `.venv/bin/python manage.py test gastos -p "test_[!v]*.py"` corre los módulos cuyo nombre no empieza por `v`. Ese patrón también deja fuera cualquier otro `test_v*.py`. Salida: `Ran 90 tests in 5.521s` / `OK`.
- Un `cat >> views.py <<EOF` con heredoc fue rechazado por el hook ("Un solo comando por llamada"). Hice esa edición con Edit.

| prueba | resultado | línea literal del error |
|---|---|---|
| test_con_sesion_usa_la_plantilla_hormiga | ERROR | django.template.exceptions.TemplateDoesNotExist: gastos/hormiga.html |
| test_el_criterio_cambia_con_settings | ERROR | TemplateDoesNotExist: gastos/hormiga.html |
| test_encabezado_sin_sesion_no_tiene_enlace_a_hormiga | ok | |
| test_encabezado_tiene_enlace_a_hormiga_con_sesion | FAIL | AssertionError: Regex didn't match: '<a href="/hormiga/">\\s*Gasto hormiga\\s*</a>' not found in '...' |
| test_gasto_de_hace_treinta_dias_cuenta | ERROR | TemplateDoesNotExist: gastos/hormiga.html |
| test_gasto_de_hace_treinta_y_un_dias_no_cuenta | ERROR | TemplateDoesNotExist: gastos/hormiga.html |
| test_gasto_de_hoy_cuenta | ERROR | TemplateDoesNotExist: gastos/hormiga.html |
| test_gastos_de_dos_usuarios_no_se_suman | ERROR | TemplateDoesNotExist: gastos/hormiga.html |
| test_gastos_que_no_llegan_a_n_muestran_el_aviso | ERROR | django.template.exceptions.TemplateDoesNotExist: gastos/hormiga.html |
| test_grupo_sin_descripcion_se_muestra_como_sin_descripcion | ERROR | TemplateDoesNotExist: gastos/hormiga.html |
| test_grupos_en_el_orden_de_la_regla | ERROR | django.template.exceptions.TemplateDoesNotExist: gastos/hormiga.html |
| test_head_esta_permitido | ERROR | TemplateDoesNotExist: gastos/hormiga.html |
| test_la_pagina_muestra_el_grupo | ERROR | TemplateDoesNotExist: gastos/hormiga.html |
| test_muestra_el_criterio_con_los_valores_por_defecto | ERROR | TemplateDoesNotExist: gastos/hormiga.html |
| test_no_muestra_gastos_hormiga_de_otro_usuario | ERROR | TemplateDoesNotExist: gastos/hormiga.html |
| test_post_no_esta_permitido | ok | |
| test_sin_gastos_muestra_el_aviso | ERROR | TemplateDoesNotExist: gastos/hormiga.html |
| test_sin_sesion_redirige_al_login | ok | |
| test_tabla_accesible_y_un_solo_h1 | ERROR | TemplateDoesNotExist: gastos/hormiga.html |
| test_tres_tintos_forman_un_grupo_en_el_contexto | ERROR | TemplateDoesNotExist: gastos/hormiga.html |
| test_usa_n_de_settings | ERROR | TemplateDoesNotExist: gastos/hormiga.html |
| test_usa_umbral_de_settings | ERROR | TemplateDoesNotExist: gastos/hormiga.html |

Las líneas de los errores marcadas con `TemplateDoesNotExist: gastos/hormiga.html` sin prefijo las inferí por el patrón. Del listado -v 2 sé que son ERROR, y los tracebacks que vi terminan todos así, pero parte del texto se truncó. La causa de todos los ERROR es la plantilla faltante (T3), no un fallo del código de la vista.

NECESITA DE OTRO AGENTE: implementador-frontend (T3) debe crear `templates/gastos/hormiga.html` y añadir el enlace «Gasto hormiga» en el `<nav>` de `templates/base.html`. Con eso deberían pasar las 19 pruebas pendientes, incluida `test_head_esta_permitido`.

PREGUNTAS PARA EL DESARROLLADOR: ninguna.
```

**Notas del coordinador:**
- El estado coincide con el intermedio previsto en el plan: pasan CA1 (`test_sin_sesion_redirige_al_login`), el POST de CA14 y la guarda de CA12 sin sesión; el resto espera la plantilla.
- La evidencia de la suite completa no es literal: el cierre `Ran/FAILED` se truncó. La línea de progreso literal muestra los E/F solo en el bloque de `test_vista_hormiga`. El patrón `test_[!v]*.py` deja fuera también `test_vista_gastos.py`, así que `Ran 90 ... OK` no cubre ese módulo. Se exige la suite completa con cierre literal en T3.
- El hook rechazó un heredoc (`cat >> views.py <<EOF`) del implementador-backend; usó Edit. El hook funcionó como se esperaba.
- El coordinador revisó el `git diff`: solo cambian `gastos/views.py` y `gastos/urls.py`, y la vista sigue el plan (`login_required`, `require_safe`, filtro por `request.user`, `settings` leído en cada petición, `categoria_nombre` con `Gasto.Categoria(...).label`, `dias = VENTANA_DIAS`).

## Verde (T3, frontend)

### Informe del implementador-frontend

```
ESTADO: verde

ARCHIVOS:
- /home/jdrickxd/Documentos/Proyecto_Integrador/templates/gastos/hormiga.html (nuevo)
- /home/jdrickxd/Documentos/Proyecto_Integrador/templates/base.html (enlace `<a href="{% url 'hormiga' %}">Gasto hormiga</a>` dentro del nav, después de «Mis gastos», dentro de `{% if user.is_authenticated %}`)
- static/estilos.css no se tocó.

Detalle: hormiga.html tiene un solo h1, el texto del criterio con variables, una section.bloque con h2 (para aria-labelledby, igual que lista.html), una tabla con caption y 4 th scope="col", y el aviso exacto cuando no hay grupos. No hay formulario, sumas ni comparaciones. El texto fijo no contiene «pan». El caption no afirma ningún orden, porque no lo verifiqué en la vista.

EVIDENCIA:
`.venv/bin/python manage.py test gastos.tests.test_vista_hormiga -v 2`: las 22 pruebas dicen `... ok`:
test_con_sesion_usa_la_plantilla_hormiga, test_el_criterio_cambia_con_settings, test_encabezado_sin_sesion_no_tiene_enlace_a_hormiga, test_encabezado_tiene_enlace_a_hormiga_con_sesion, test_gasto_de_hace_treinta_dias_cuenta, test_gasto_de_hace_treinta_y_un_dias_no_cuenta, test_gasto_de_hoy_cuenta, test_gastos_de_dos_usuarios_no_se_suman, test_gastos_que_no_llegan_a_n_muestran_el_aviso, test_grupo_sin_descripcion_se_muestra_como_sin_descripcion, test_grupos_en_el_orden_de_la_regla, test_head_esta_permitido, test_la_pagina_muestra_el_grupo, test_muestra_el_criterio_con_los_valores_por_defecto, test_no_muestra_gastos_hormiga_de_otro_usuario, test_post_no_esta_permitido, test_sin_gastos_muestra_el_aviso, test_sin_sesion_redirige_al_login, test_tabla_accesible_y_un_solo_h1, test_tres_tintos_forman_un_grupo_en_el_contexto, test_usa_n_de_settings, test_usa_umbral_de_settings
Cierre:
    Ran 22 tests in 12.470s

    OK
`.venv/bin/python manage.py test -v 0`:
    Ran 132 tests in 29.252s

    OK
    System check identified no issues (0 silenced).
No se ejecutó curl; no comprobé si el servidor estaba encendido.

NECESITA DE OTRO AGENTE: nada

PREGUNTAS PARA EL DESARROLLADOR: ninguna
```

**Notas del coordinador:**
- `-v 0` resolvió el truncado: la suite completa da un cierre literal `Ran 132 tests ... OK`. Conviene usarlo por defecto en los encargos.
- El coordinador leyó `templates/gastos/hormiga.html` y el diff de `base.html`: el enlace está dentro del `if user.is_authenticated` y la plantilla solo muestra variables, sin cálculos.
- Pendiente para el desarrollador: la revisión manual con `runserver` que pide el plan (el frontend no ejecutó curl). Tampoco hay salida de cobertura: el hook de los agentes no permite `coverage`. *(Corrección: el revisor sí pudo ejecutar `coverage`; ver abajo.)*

## Revisión (T4), primera vuelta

### Informe del revisor

```
ESTADO: con hallazgos (no hay ninguno bloqueante ni importante, solo tres menores)

La rama se puede fusionar. Los 14 criterios tienen prueba y las pruebas comprueban de verdad lo que dicen. Las tres cosas de abajo se pueden arreglar después.

HALLAZGOS:

1. /home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_vista_hormiga.py:16 y 121-132 · menor (baja) · Las pruebas dependen del reloj si se ejecutan justo a medianoche. `self.hoy` se calcula en `setUp`, y la vista vuelve a llamar a `timezone.localdate()` cuando atiende la petición. Si en Bogotá cambia el día entre esos dos momentos, pasa lo siguiente:
   - `test_gasto_de_hace_treinta_dias_cuenta` falla sin motivo, porque para la vista el gasto queda en `hoy − 31`.
   - `test_gasto_de_hace_treinta_y_un_dias_no_cuenta` pasa sin estar probando nada.
   - Por qué importa: la regla de `.claude/rules/pruebas.md` se cumple a la letra (fechas relativas a `localdate()`), pero el límite del día 30/31, que es justo lo que pide CA8, puede fallar de forma intermitente.
   - Arreglo propuesto: fijar el día con `mock.patch("gastos.views.timezone.localdate", return_value=...)` en las pruebas de CA8, o en toda la clase.
   - Corrige: probador.

2. /home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_vista_hormiga.py:167 · menor (baja) · La aserción «30 días» de CA11 se cumple también con el aviso de que no hay grupos. La prueba no crea gastos, así que la página muestra «No se detectaron gastos hormiga en los últimos 30 días.» (hormiga.html:36). Si alguien quitara `{{ dias }}` del texto del criterio (hormiga.html:7), la prueba seguiría pasando.
   - Arreglo propuesto: comprobar la frase completa del criterio, «en los últimos 30 días.» junto con «3 o más veces», o crear 3 gastos para que no salga el aviso.
   - Corrige: probador.

3. /home/jdrickxd/Documentos/Proyecto_Integrador/gastos/views.py:72 · menor (baja) · `Gasto.Categoria(grupo["categoria"]).label` lanza `ValueError`, y la página responde 500, si en la base hay un gasto cuya categoría no está entre las opciones. Puede pasar con datos cargados por el admin o por migración, o si se retira una categoría en el futuro.
   - Arreglo propuesto: usar `dict(Gasto.Categoria.choices).get(codigo, codigo)`.
   - Hoy no se puede reproducir por la interfaz, porque el formulario valida la categoría.
   - Corrige: implementador-backend.

Lo que revisé a fondo y está bien (no son hallazgos):
- **Prueba de orden de CA9 (líneas 141-151):** sí distingue los casos. Pan se crea primero y va primero en orden alfabético, así que si la vista ordenara por inserción o por nombre, la prueba fallaría. Antes de la tabla no aparece «tinto» ni «pan» en ningún otro sitio (lo comprobé contra base.html). Lo único frágil: si un día se añade un texto con «pan» al encabezado, por ejemplo «<span», la prueba fallaría aunque el código esté bien, pero nunca pasaría estando mal.
- **Regex `>\s*3\s*</td>` (línea 68):** con un solo grupo, solo coincide con la celda Veces. El «3» del texto del criterio no está dentro de un `<td>`. Está bien.
- **Aislamiento (CA4 y CA5):** CA4 comprueba que `grupos == []` y que no aparecen los gastos de Beto. CA5 (2 gastos de Ana y 1 de Beto) fallaría si la vista no filtrara por `request.user`. Las dos son pruebas sólidas.
- **Vista:**
  - Tiene `@login_required` por fuera y `@require_safe` por dentro. Un POST anónimo redirige al login (302); un POST con sesión responde 405.
  - Filtra por `request.user`, lee `settings` en cada petición y usa `timezone.localdate()`.
  - No hay reglas de negocio en la vista, y `categoria_nombre` es solo para mostrar, como decía el plan.
- **Plantilla:**
  - Hereda de base.html y tiene un solo `<h1>`, con `<h2>` debajo.
  - Tiene `<caption>`, 4 `<th scope="col">` y la clase `.numero` con `tabular-nums`.
  - Usa `floatformat:"0g"` y `default:"Sin descripción"`, y no hace cálculos.
  - Los textos están en español y no tiene formularios, así que no necesita `csrf_token`.
- **Web Interface Guidelines** (las bajé con WebFetch):
  - templates/gastos/hormiga.html: pasa.
  - templates/base.html: pasa. Detalle sin severidad: el `<nav>` no marca `aria-current="page"` en el enlace de la página actual, pero eso ya pasaba antes de esta rama con «Mis gastos».
- **Commits:** el `test:` (fefcca3) va antes de los dos `feat:`.

DIFERENCIAS CON LA SPEC:
- Todos los criterios CA1–CA14 tienen prueba. Los archivos cambiados son exactamente los del plan; `static/estilos.css` no se tocó, y el plan lo dejaba opcional.
- La regla, el modelo, las migraciones, settings y requirements no cambian.
- Pendiente: `specs/002-pantalla-hormiga/tareas.md` está modificado sin commit y `specs/002-pantalla-hormiga/evidencia.md` está sin seguimiento. Hay que hacer commit de los dos antes del PR.

EVIDENCIA:
- `git diff main...HEAD --stat`: 8 archivos, 411 líneas añadidas y 1 borrada. Son las pruebas, urls.py, views.py, base.html, hormiga.html y la spec, el plan y las tareas.
- `git log --oneline main..HEAD`: 0a68eba docs, fefcca3 test, 5ba5a9b feat backend, 0a284e2 feat frontend.
- `.venv/bin/python manage.py test -v 0`: «Ran 132 tests in 29.358s — OK».
- `.venv/bin/python manage.py check`: «System check identified no issues (0 silenced).»
- `.venv/bin/python manage.py makemigrations --check --dry-run`: «No changes detected».
- `.venv/bin/coverage run --source=gastos manage.py test -v 0`: 132 pruebas, todas OK.
- `.venv/bin/coverage report`: TOTAL 99 %, con gastos/views.py al 100 %, gastos/urls.py al 100 % y gastos/models.py al 95 % (falta la línea 35, que viene de antes).
- Dos comandos `grep` sobre settings.py y estilos.css los bloqueó el hook (no admite barras invertidas). Leí esos archivos con Read: TIME_ZONE es America/Bogota y USE_TZ es True.

PREGUNTAS PARA EL DESARROLLADOR:
- ¿Se acepta el riesgo de medianoche (hallazgo 1), dado que la norma solo pide fechas relativas a `localdate()`, o se fija el día con `mock.patch` en las pruebas de vista que dependen del límite de 30 días?
```

### Qué se hizo con cada hallazgo
- **Hallazgo 1 (reloj a medianoche):** se corrige. Se encarga al probador (T5). La pregunta del revisor la resuelve el coordinador sin escalarla al desarrollador, porque `.claude/rules/pruebas.md` ya admite `mock.patch` («fechas relativas a `timezone.localdate()` o `mock.patch`»): fijar el día no cambia el alcance.
- **Hallazgo 2 («30 días» ambiguo en CA11):** se corrige. Se encarga al probador (T5).
- **Hallazgo 3 (`ValueError` con categoría desconocida):** se corrige con TDD. Se añade CA15 a `spec.md` y su prueba al plan, porque cambia el comportamiento esperado de la página. Primero el probador escribe la prueba en rojo (T5), después el implementador-backend la corrige (T6).
- **`aria-current` en el `<nav>`:** se descarta en esta spec. El revisor no le da gravedad y ya faltaba antes de la rama, con «Mis gastos». Queda como posible mejora aparte.
- **Commit de `tareas.md` y `evidencia.md`:** se hará en el cierre (`docs:`), como indica la skill.

## Corrección de la revisión, vuelta 1

### T5 · informe del probador

```
ESTADO: rojo confirmado

ARCHIVOS: /home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_vista_hormiga.py (único modificado)

EVIDENCIA:
Comando: `.venv/bin/python manage.py test gastos.tests.test_vista_hormiga -v 2`
- La salida salió completa, sin truncar, y no hizo falta `-k`.
- Resultado literal: 22 pruebas con `... ok` y 1 con `... ERROR`.
- `test_categoria_desconocida_muestra_el_codigo (gastos.tests.test_vista_hormiga.VistaHormigaTests.test_categoria_desconocida_muestra_el_codigo) ... ERROR`
- Las 22 pruebas en verde son las anteriores. Incluyen `test_gasto_de_hace_treinta_dias_cuenta`, `test_gasto_de_hace_treinta_y_un_dias_no_cuenta`, `test_gasto_de_hoy_cuenta`, `test_muestra_el_criterio_con_los_valores_por_defecto` y `test_el_criterio_cambia_con_settings`.
- Cierre literal: `Ran 23 tests in 13.216s` y `FAILED (errors=1)`.
- Error literal de la prueba en rojo, en `gastos/views.py` línea 72, función `hormiga`: `grupo["categoria_nombre"] = Gasto.Categoria(grupo["categoria"]).label` y `ValueError: 'antigua' is not a valid Gasto.Categoria`.
- Es el rojo esperado: falta el código de la vista, no hay un error de la prueba.

Comando: `.venv/bin/python manage.py test -v 0`
- Es la única prueba en rojo: el mismo `ValueError: 'antigua' is not a valid Gasto.Categoria`.
- Cierre literal: `Ran 133 tests in 30.004s` y `FAILED (errors=1)`.

Cambios por hallazgo y cómo se comprueba que detectan el fallo (razonado, sin tocar vista ni plantilla):
1. Hallazgo 1. En `setUp`, `self.hoy = timezone.localdate()` se calcula una vez. Después se hace `mock.patch("gastos.views.timezone.localdate", return_value=self.hoy)` con `start()` y `addCleanup(parche.stop)`, para toda la clase.
   - La vista ya no lee el reloj: recibe exactamente `self.hoy`.
   - Si la suite cruza la medianoche, la prueba y la vista siguen usando el mismo día. Los límites de 30 y 31 días no se desplazan, y no hay fallo ni acierto en falso.
   - Detecta el fallo porque la vista queda anclada al día de la prueba. Antes, un `localdate()` distinto en la vista movía la ventana un día.
   - El parche funciona: las 22 pruebas anteriores siguen en verde con la vista real.
2. Hallazgo 2. Las dos pruebas del criterio comprueban ahora la frase completa.
   - `Compras de hasta $10.000 que se repiten 3 o más veces en los últimos 30 días.`
   - `Compras de hasta $5.000 que se repiten 4 o más veces en los últimos 30 días.`
   - Si se quita `{{ dias }}` del párrafo del criterio, la frase queda como «...en los últimos  días.». `assertContains` ya no la encuentra, aunque el aviso de «sin grupos» siga mostrando «30 días».
   - Lo mismo ocurre con `{{ umbral }}` o `{{ n }}`.
   - Se quitaron las aserciones sueltas `$10.000`, `3 o más veces` y `30 días`, que quedaban cubiertas por la frase completa. Se conservan las aserciones del contexto (`umbral`, `n`, `dias`).
3. Hallazgo 3 (CA15). Se añadió `test_categoria_desconocida_muestra_el_codigo` con 3 gastos de Ana, `categoria="antigua"`, bajo el umbral y dentro de la ventana. Espera 200, un grupo, y `categoria_nombre == "antigua"`.
   - Hoy falla con el `ValueError` de arriba.
   - Quedó ubicada antes del bloque `# CA10`, no tras CA14. Es un detalle de orden en el archivo y no afecta nada.

Nota de entorno: `python manage.py test` a secas falla con `ModuleNotFoundError: No module named 'django'`. Se usó `.venv/bin/python`, como se indicó. Un `grep` por Bash fue rechazado por el hook, así que no pude releer la vista con grep. Solo vi la línea 72 en el traceback.

NECESITA DE OTRO AGENTE: implementador-backend. Debe corregir `gastos/views.py` línea 72 para que una categoría fuera de `Gasto.Categoria` use el código tal cual como `categoria_nombre`. Por ejemplo, `Gasto.Categoria(valor).label` con un try/except del `ValueError`, o un diccionario con `.get(codigo, codigo)`. Eso pone la prueba en verde.

PREGUNTAS PARA EL DESARROLLADOR: ninguna
```

**Nota del coordinador:** `mock.patch("gastos.views.timezone.localdate")` parchea la función en el módulo `django.utils.timezone`, que comparten la vista y las pruebas. Como el valor sale de `self.hoy`, ambos ven el mismo día, que era lo que se buscaba.

### T6 · informe del implementador-backend

```
ESTADO: verde
ARCHIVOS: /home/jdrickxd/Documentos/Proyecto_Integrador/gastos/views.py (vista `hormiga`: `nombres_categoria = dict(Gasto.Categoria.choices)` calculado una vez fuera del bucle; `grupo["categoria_nombre"] = nombres_categoria.get(grupo["categoria"], grupo["categoria"])`). No se cambió nada más.
EVIDENCIA:
`.venv/bin/python manage.py test gastos.tests.test_vista_hormiga -v 2` (las 23 líneas de resultado; la primera sale pegada a la salida de la migración sessions.0001):
test_categoria_desconocida_muestra_el_codigo ... ok
test_con_sesion_usa_la_plantilla_hormiga ... ok
test_el_criterio_cambia_con_settings ... ok
test_encabezado_sin_sesion_no_tiene_enlace_a_hormiga ... ok
test_encabezado_tiene_enlace_a_hormiga_con_sesion ... ok
test_gasto_de_hace_treinta_dias_cuenta ... ok
test_gasto_de_hace_treinta_y_un_dias_no_cuenta ... ok
test_gasto_de_hoy_cuenta ... ok
test_gastos_de_dos_usuarios_no_se_suman ... ok
test_gastos_que_no_llegan_a_n_muestran_el_aviso ... ok
test_grupo_sin_descripcion_se_muestra_como_sin_descripcion ... ok
test_grupos_en_el_orden_de_la_regla ... ok
test_head_esta_permitido ... ok
test_la_pagina_muestra_el_grupo ... ok
test_muestra_el_criterio_con_los_valores_por_defecto ... ok
test_no_muestra_gastos_hormiga_de_otro_usuario ... ok
test_post_no_esta_permitido ... ok
test_sin_gastos_muestra_el_aviso ... ok
test_sin_sesion_redirige_al_login ... ok
test_tabla_accesible_y_un_solo_h1 ... ok
test_tres_tintos_forman_un_grupo_en_el_contexto ... ok
test_usa_n_de_settings ... ok
test_usa_umbral_de_settings ... ok
Cierre: "Ran 23 tests in 13.330s" / "OK"
(Los nombres aparecen sin la ruta completa del módulo para abreviar.)

`.venv/bin/python manage.py test -v 0`: "Ran 133 tests in 30.562s" / "OK"
`.venv/bin/python manage.py check`: "System check identified no issues (0 silenced)." (no imprime Ran/OK porque no ejecuta pruebas)
NECESITA DE OTRO AGENTE: nada
PREGUNTAS PARA EL DESARROLLADOR: ninguna
```

El coordinador revisó el `git diff` (solo la vista `hormiga`, el cambio de una línea a `.get(codigo, codigo)` con el diccionario fuera del bucle). Commits de la vuelta: `0dda970 test:` y `a0759c9 fix:`.

## Revisión (T4), segunda vuelta

### Informe del revisor

```
ESTADO: con hallazgos (uno nuevo, de severidad baja; los tres de la vuelta 1 quedaron corregidos)

## Hallazgos de la vuelta 1

1. **CA8 dependía del reloj a medianoche: corregido.** En `/home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_vista_hormiga.py:18-21`, `self.hoy` se calcula una vez y `timezone.localdate` queda parcheado para que devuelva justo ese valor. Los gastos se crean con `self.hoy` y la vista le pasa a la regla el mismo `self.hoy` parcheado. Aunque la medianoche caiga en mitad de la prueba, los dos lados siguen comparando el mismo día. Los límites siguen cubiertos: `hoy−30` entra, `hoy−31` no y `hoy` entra (líneas 126-142).

2. **En CA11, el aviso cumplía la aserción «30 días»: corregido.** Las líneas 179-182 y 190-193 comprueban ahora la frase entera, que empieza por «Compras de hasta $…». El aviso de la línea 36 de `templates/gastos/hormiga.html` no la contiene, así que ya no puede dar un falso positivo. El 30 sale de `{{ dias }}` en la plantilla (línea 7) y la prueba exige `context["dias"] == 30`.

3. **`Gasto.Categoria(...)` lanzaba ValueError: corregido.** En `/home/jdrickxd/Documentos/Proyecto_Integrador/gastos/views.py:71-76` ahora se usa `dict(Gasto.Categoria.choices).get(codigo, codigo)`. Con una categoría conocida el resultado no cambia: CA3 sigue exigiendo «Alimentación» (líneas 63 y 71 de la prueba). El commit `test:` (0dda970) va antes que el `fix:` (a0759c9).

## El mock.patch aplicado a toda la clase

- El destino `"gastos.views.timezone.localdate"` en realidad parchea el atributo del módulo `django.utils.timezone`. Mientras corre cada prueba, el parche vale para todo el proceso, no solo para la vista. No oculta nada:
  - devuelve la fecha real de ese momento;
  - en `gastos/` solo lo llaman las vistas, sin argumentos (`lista_gastos`, línea 44, y `hormiga`, línea 69);
  - la regla recibe `hoy` como parámetro;
  - el modelo no consulta el reloj.

  Es más amplio de lo que sugiere el nombre del destino, pero es inofensivo.
- Todas las pruebas de la clase tienen aserciones propias. Ninguna se limita a comprobar el mock: no hay ninguna `assert_called`, y los resultados se comprueban en el contexto y en el HTML.
- Hay un punto débil, que va como hallazgo nuevo 1: el parche devuelve la fecha real en lugar de una fija.

## CA15

Tiene prueba: `test_categoria_desconocida_muestra_el_codigo` (líneas 160-165) comprueba el 200, que hay un grupo y que `categoria_nombre == "antigua"`. La vista lo cumple (views.py:74-76), y la plantilla muestra `{{ grupo.categoria_nombre }}` sin traducir nada (hormiga.html:27). Según el commit 0dda970, la prueba se vio en rojo antes de la corrección.

## HALLAZGOS NUEVOS

1. `/home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_vista_hormiga.py:19` · **baja** · El parche usa `return_value=self.hoy`, es decir, la fecha real.
   - **Qué pasa:** si la vista cambiara `timezone.localdate()` por `datetime.date.today()` (zona del sistema en vez de `TIME_ZONE`), las pruebas de CA8 seguirían pasando casi siempre. Solo fallarían en las horas en que la fecha UTC o la del sistema no coincide con la de Bogotá. El fallo quedaría como una prueba intermitente, no como un rojo fiable.
   - **Corrección propuesta:** parchear con una fecha fija y alejada de hoy (p. ej. `date(2025, 1, 15)`) y calcular `self.hoy` a partir de ella. Así CA8 demostraría de forma determinista que la vista usa `timezone.localdate()`.
   - **Rol que corrige:** probador.

No apareció ningún otro problema. Desde la vuelta 1 no cambió nada en `templates/` (`git diff 0a284e2..HEAD` solo toca `gastos/`), así que no volví a aplicar `web-design-guidelines`. Las observaciones de la vuelta 1 siguen valiendo, y `aria-current` queda fuera de esta spec, como se decidió.

## DIFERENCIAS CON LA SPEC

- `spec.md` (CA15), `plan.md` («Ajustes tras la revisión») y `tareas.md` tienen cambios sin commit, y `evidencia.md` no está en git. Hay que hacer commit antes del PR.
- El texto de CA11 en `spec.md` (línea 41) todavía enumera fragmentos sueltos («$10.000», «3 o más veces», «30 días»), mientras que la prueba exige la frase completa. La prueba es más estricta que el criterio, así que no hay contradicción; si se quiere, se puede alinear el texto.
- Archivos fuera del plan: ninguno. Los del diff contra `main` coinciden con los del plan, más las carpetas de specs, y no se tocó `static/estilos.css`. `requirements.txt`, las migraciones, `db.sqlite3` y `.env` no aparecen en el diff.

## EVIDENCIA

`git diff main...HEAD --stat`
 gastos/tests/test_vista_hormiga.py   | 235 +++++++++++++++++++++++++++++++++++
 gastos/urls.py                       |   1 +
 gastos/views.py                      |  29 ++++-
 specs/002-pantalla-hormiga/plan.md   |  63 ++++++++++
 specs/002-pantalla-hormiga/spec.md   |  59 +++++++++
 specs/002-pantalla-hormiga/tareas.md |   6 +
 templates/base.html                  |   1 +
 templates/gastos/hormiga.html        |  39 ++++++
 8 files changed, 432 insertions(+), 1 deletion(-)

`git log --oneline main..HEAD`
a0759c9 fix: categoría desconocida se muestra con su código en /hormiga/ (spec 002, hallazgo 3)
0dda970 test: pruebas de la revisión de la pantalla hormiga (spec 002, CA15 en rojo)
0a284e2 feat: plantilla de gasto hormiga y enlace en el encabezado (spec 002)
5ba5a9b feat: vista y ruta de la pantalla de gasto hormiga (spec 002)
fefcca3 test: pruebas de la pantalla de gasto hormiga (spec 002, rojo)
0a68eba docs: spec 002 pantalla-hormiga

`.venv/bin/python manage.py test -v 0`
----------------------------------------------------------------------
Ran 133 tests in 30.420s

OK
System check identified no issues (0 silenced).

`.venv/bin/python manage.py check`
System check identified no issues (0 silenced).

`.venv/bin/python manage.py makemigrations --check --dry-run`
No changes detected

`.venv/bin/coverage run --source=gastos manage.py test -v 0`
----------------------------------------------------------------------
Ran 133 tests in 30.281s

OK
System check identified no issues (0 silenced).

`.venv/bin/coverage report`
Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
gastos/__init__.py              0      0   100%
gastos/admin.py                 1      0   100%
gastos/apps.py                  3      0   100%
gastos/forms.py                60      0   100%
gastos/models.py               21      1    95%   35
gastos/reglas/__init__.py       0      0   100%
gastos/reglas/gastos.py         7      0   100%
gastos/reglas/hormiga.py       19      0   100%
gastos/reglas/usuarios.py       2      0   100%
gastos/urls.py                  5      0   100%
gastos/views.py                52      0   100%
---------------------------------------------------------
TOTAL                         170      1    99%

También ejecuté `git diff 0a284e2..HEAD -- gastos/`, `git diff main...HEAD -- templates/base.html gastos/urls.py`, `git status` y `git diff`; sus resultados están resumidos arriba. El hook bloqueó un `git grep` que no está en la lista de comandos permitidos; para esa comprobación leí los archivos directamente.

## PREGUNTAS PARA EL DESARROLLADOR

- ¿Se corrige el hallazgo nuevo 1 (fecha fija en el parche) en esta spec o se acepta como está? Las pruebas pasan y el riesgo es bajo.
- ¿Se ajusta el texto de CA11 en `spec.md` a la frase completa que exige la prueba?
```

### Qué se hizo con cada punto de la vuelta 2
- **Hallazgos 1–3 de la vuelta 1:** confirmados como corregidos.
- **Hallazgo nuevo 1 (parche con la fecha real):** se corrige en la segunda y última vuelta permitida (T7, probador). Lo decide el coordinador sin escalarlo: es un ajuste de las pruebas que no cambia el alcance, y `.claude/rules/pruebas.md` admite `mock.patch`.
- **Texto de CA11:** lo corrige el coordinador en `spec.md` (está en `specs/`); ahora cita la frase completa.

## Corrección de la revisión, vuelta 2

### T7 · informe del probador

```
ESTADO: rojo confirmado no aplica; es una corrección de una prueba ya en verde. Las 23 pruebas siguen en verde con la fecha fija.

ARCHIVOS: /home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_vista_hormiga.py. Cambios:
- `setUp` ahora usa `self.hoy = date(2025, 1, 15)` en lugar de `timezone.localdate()`. El comentario explica el motivo.
- El parche `gastos.views.timezone.localdate` no cambió, pero ahora devuelve esa fecha fija.
- El import pasó de `from datetime import timedelta` a `from datetime import date, timedelta`.
- Quité `from django.utils import timezone`, que ya no se usaba. El parche lo referencia solo como cadena.
- No toqué la vista ni ninguna otra prueba.

EVIDENCIA:
1. `.venv/bin/python manage.py test gastos.tests.test_vista_hormiga -v 2`
Las 23 líneas, todas terminan en `ok`:
- test_categoria_desconocida_muestra_el_codigo
- test_con_sesion_usa_la_plantilla_hormiga
- test_el_criterio_cambia_con_settings
- test_encabezado_sin_sesion_no_tiene_enlace_a_hormiga
- test_encabezado_tiene_enlace_a_hormiga_con_sesion
- test_gasto_de_hace_treinta_dias_cuenta
- test_gasto_de_hace_treinta_y_un_dias_no_cuenta
- test_gasto_de_hoy_cuenta
- test_gastos_de_dos_usuarios_no_se_suman
- test_gastos_que_no_llegan_a_n_muestran_el_aviso
- test_grupo_sin_descripcion_se_muestra_como_sin_descripcion
- test_grupos_en_el_orden_de_la_regla
- test_head_esta_permitido
- test_la_pagina_muestra_el_grupo
- test_muestra_el_criterio_con_los_valores_por_defecto
- test_no_muestra_gastos_hormiga_de_otro_usuario
- test_post_no_esta_permitido
- test_sin_gastos_muestra_el_aviso
- test_sin_sesion_redirige_al_login
- test_tabla_accesible_y_un_solo_h1
- test_tres_tintos_forman_un_grupo_en_el_contexto
- test_usa_n_de_settings
- test_usa_umbral_de_settings

Cierre literal:
    Ran 23 tests in 13.212s

    OK
    Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
     OK
    System check identified no issues (0 silenced).

2. `.venv/bin/python manage.py test -v 0`
    Ran 133 tests in 29.943s

    OK
    System check identified no issues (0 silenced).

Por qué ahora fallaría con `date.today()` (razonamiento, sin tocar la vista):
- `self.hoy` es 2025-01-15 y todos los gastos se crean con fechas relativas a él (`fecha=self.hoy` por defecto, o `self.hoy - timedelta(...)`).
- Hoy es 2026-11-14, a más de 300 días de esa fecha. Si la vista llamara a `date.today()`, el parche de `timezone.localdate` no tendría efecto sobre ella, y `detectar_gasto_hormiga` recibiría 2026-11-14 como `hoy`.
- Con esa fecha, la ventana de 30 días no incluiría ningún gasto de enero de 2025. Por eso fallarían las pruebas que esperan grupos:
  - `test_tres_tintos_forman_un_grupo_en_el_contexto`
  - `test_gasto_de_hace_treinta_dias_cuenta`
  - `test_gasto_de_hoy_cuenta`
  - `test_grupos_en_el_orden_de_la_regla`
  - `test_usa_n_de_settings`
  - `test_categoria_desconocida_muestra_el_codigo`
  - `test_la_pagina_muestra_el_grupo`
  - `test_grupo_sin_descripcion_se_muestra_como_sin_descripcion`
- Esto ya no depende de la hora del día, y el resultado no cambia según cuándo se ejecuten las pruebas.
- Las pruebas de CA8 que esperan ausencia de grupos (`test_gasto_de_hace_treinta_y_un_dias_no_cuenta`) pasarían con `date.today()`. Esto es esperable: ya se detectan por las que esperan presencia, en especial `test_gasto_de_hace_treinta_dias_cuenta` y `test_gasto_de_hoy_cuenta`, que son las que fijan el día de la vista.
- No ejecuté esta comprobación con la vista cambiada, como se pidió.

Ninguna otra prueba dependía de que `self.hoy` fuera la fecha real:
- Ninguna pasa por `FormularioGasto` ni hace POST de un gasto. El único POST es `test_post_no_esta_permitido`, que va a `/hormiga/`, responde 405 y no usa el formulario. Los gastos se crean con `Gasto.objects.create`, que no corre la validación de fecha futura. Además, 2025-01-15 es pasada, así que no sería rechazada.
- `test_encabezado_tiene_enlace_a_hormiga_con_sesion` pide `/gastos/`. Esa vista usa `timezone.localdate()` solo como `initial` del formulario, que el parche también cubre porque es el mismo objeto `timezone`. Las aserciones no miran la fecha.
- Las demás pruebas (`login`, plantilla, settings, criterio) no usan fechas.
- La suite completa (133 pruebas) sigue en verde.

NECESITA DE OTRO AGENTE: nada

PREGUNTAS PARA EL DESARROLLADOR: ninguna
```

**Nota del coordinador:** revisó el `git diff`: solo cambian `setUp` y los imports. Commit `3ee1384 test: fecha fija en el parche de localdate ...`. Con esta se agotan las dos vueltas de corrección. No se lanzó una tercera revisión: el cambio son 4 líneas de las pruebas, verificadas por el coordinador y con la suite en verde. Que el desarrollador lo valore en la revisión del pull request.

## Estado final
- Suite completa: `Ran 133 tests in 29.943s` / `OK` (T7).
- Cobertura (revisor, vuelta 2): `TOTAL 170 1 99%`; `gastos/views.py` al 100 %.
- `check` sin problemas; `makemigrations --check --dry-run`: `No changes detected`.
- Commits de la rama: `0a68eba docs`, `fefcca3 test`, `5ba5a9b feat`, `0a284e2 feat`, `0dda970 test`, `a0759c9 fix`, `3ee1384 test` y el `docs:` de cierre.
- Cambios de alcance durante la implementación: se añadió CA15 (hallazgo 3) y el texto de CA11 se alineó con la prueba (hallazgo 2 y vuelta 2). Ambos están anotados en `spec.md`.
- Pendiente del desarrollador:
  - la revisión manual con `runserver` (abrir `/hormiga/` con y sin gastos hormiga);
  - el push y el pull request;
  - el enlace al PR en este archivo: https://github.com/JuanDR403/Hormiguero/pull/10 (fusionado).

## Propuestas para ajustar el arnés
- Los agentes y `AGENTS.md` dicen `python manage.py test`, pero en esta sesión solo funciona `.venv/bin/python manage.py test`. Conviene documentarlo en los agentes o permitirlo explícitamente en el hook.
- La herramienta Bash trunca las salidas largas. Conviene recomendar `-v 0` para la suite completa y `-v 2` por módulo.
- El hook rechaza `git ls-files` y `git grep` del coordinador y del revisor, y los `grep` con barra invertida. Si se quieren permitir, hay que añadirlos a la lista.

### Incidencias del arnés en la revisión
- El hook rechazó dos `grep` del revisor porque llevaban barras invertidas; los archivos se leyeron con Read.
- `coverage` sí funcionó para el revisor (`.venv/bin/coverage ...`): TOTAL 99 %.
