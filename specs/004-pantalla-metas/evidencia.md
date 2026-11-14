# Evidencia 004 · Pantalla de metas de ahorro

## Rojo (probador, T1 y T2)

Informe del probador, copiado tal cual:

```
ESTADO: rojo confirmado

ARCHIVOS:
- gastos/tests/test_regla_metas.py (modificado). Añadí `from gastos.reglas import metas` y las clases `CalcularFaltaTests` y `EstadoMetaTests`. Los imports existentes quedan igual.
- gastos/tests/test_vista_metas.py (nuevo). Usa `TestCase`, parchea `django.utils.timezone.localdate` a 2026-11-14 en `setUp` y crea a ana y beto con `create_user`.

EVIDENCIA:
La salida completa de `python manage.py test` no cabe en la herramienta. El 20 012 caracteres del medio se truncaron, y no pude redirigir a un archivo porque el hook solo admite un comando por llamada. Por eso la salida real va por módulo.

1. Comando: `python manage.py test`. El resultado de la suite completa aparecía truncado y no mostró el resumen final. Se veía esta línea de progreso, con 83 puntos iniciales (las pruebas existentes, que pasan) y luego F y E de las pruebas nuevas: `....................................................................................FFFFEFFFFEFFFFFFFFFEEEEEEEEEEEFFFFFF.FFEFFEFE..............................................EEEEEEE..........EEEEEEEE.............................`
2. Comando: `python manage.py test gastos.tests.test_arquitectura`. Salida: `Ran 2 tests ... OK`. Esto confirma CA3: la prueba existente sigue en pie y no la dupliqué.
3. Comando: `python manage.py test gastos.tests.test_regla_metas`. Salida: `Ran 43 tests ... FAILED (errors=15)`. Los 15 errores son todos las pruebas nuevas, con `AttributeError: module 'gastos.reglas.metas' has no attribute 'calcular_falta'` (7 pruebas) o `'estado_meta'` (8 pruebas). Las 28 pruebas anteriores de ese archivo siguen pasando.
4. Comando: `python manage.py test gastos.tests.test_vista_metas.PaginaYEncabezadoTests gastos.tests.test_vista_metas.SesionYAislamientoTests`. Salida: `Ran 14 tests ... FAILED (failures=10, errors=3)`. Pasa 1 prueba, `test_sin_sesion_el_encabezado_no_enlaza_a_metas`, porque es una aserción negativa y hoy no hay enlace. Es esperada y no es inválida: comprueba que no aparece y evita regresiones cuando se agregue el enlace.
5. Comando: `python manage.py test gastos.tests.test_vista_metas --failfast`. La primera prueba que falla es `test_ahorrado_cero_es_valido`, con `AssertionError: 404 != 302` en `assertRedirects`.
6. Desde `test_vista_metas.py` también se comprobó, en la ejecución completa, `ImportError: cannot import name 'FormularioMeta' from 'gastos.forms'`, que es el motivo de `test_formulario_vacio_tiene_ahorrado_en_cero_y_sin_usuario` (CA16).

Motivos de fallo, todos por falta de código:
- `AttributeError` por `calcular_falta` o `estado_meta` ausentes (pruebas nuevas de `test_regla_metas.py`).
- `404` en `/metas/` porque no existe la URL ni la vista. Es el motivo de casi todas las pruebas de sesión, lista, crear y página, que fallan con `AssertionError: 404 != 302` o `404 != 200`.
- `NoReverseMatch` para `lista_metas` y `eliminar_meta`: `test_url_lista_metas_es_metas`, todas las de eliminar y `test_sin_sesion_no_elimina`.
- `KeyError: 'metas'` en `test_lista_solo_metas_propias`, porque la respuesta 404 no trae contexto.
- `ImportError` por `FormularioMeta` ausente (CA16).
- `AssertionError` por falta de `href="/metas/"` en el encabezado (CA21). Es la única prueba de `PaginaYEncabezadoTests` cuyo motivo no es el 404.
- Las pruebas de renderizado de la plantilla pasarán de 404 a `TemplateDoesNotExist` cuando exista la vista y falte `metas.html`, como prevé la spec.

Pruebas nuevas y criterio que cubren:
- test_regla_metas.py
  - CalcularFaltaTests (CA1): resta de 1.200.000 menos 200.000, falta de 1 peso, ahorrado igual al precio, uno por encima, muy por encima, `Decimal` que devuelve `int`, y `Decimal` cumplida que devuelve `int` 0.
  - EstadoMetaTests (CA2): `cumplida` en tres casos (ahorrado igual al precio, mayor con fecha pasada, igual con fecha de ayer), `vencida` (falta 1 peso y fecha ayer), `en_curso` con fecha hoy, mañana y 2027-02-01, y aceptar `Decimal`.
- test_vista_metas.py
  - SesionYAislamientoTests
    - CA4: GET sin sesión, POST sin sesión (no crea) y eliminar sin sesión (no borra).
    - CA5: 200 con plantilla `gastos/metas.html`, y `reverse("lista_metas") == "/metas/"`.
    - CA6: solo metas propias en el contexto y en la página.
    - CA11: aviso sin metas y sin `<table`.
  - ListaMetasTests
    - CA7: orden por fecha límite y por creación.
    - CA8: atributos del contexto y textos de la página (`$333.334`, `$1.000.000`, `3`, `En curso`).
    - CA9: meta cumplida.
    - CA10: meta vencida.
    - También cubre el límite de estado: fecha límite hoy es `en_curso`, y ayer sin cumplir es `vencida`.
  - CrearMetaTests
    - CA12: crear con usuario de la sesión, redirección y mensaje «Meta creada.».
    - CA13: ignora `usuario` en el POST.
    - CA14: precio 1, ahorrado 0, ahorrado mayor que el precio, fecha límite hoy y nombre de 100 caracteres.
    - CA15: nombre vacío, nombre de solo espacios y nombre de 101 caracteres. Precio 0 y precio negativo. Ahorrado −1. Fecha límite ayer. Precio y ahorrado con centavos. Cada una comprueba que solo ese campo tiene error, que es uno solo, el texto exacto cuando la spec lo fija, `aria-describedby`, y que no guarda. Hay una prueba aparte de que el formulario conserva los datos.
    - CA16: formulario sin `usuario` y con `ahorrado` inicial 0, más la página con `name="ahorrado"`, `value="0"` y `type="date"`.
  - EliminarMetaTests
    - CA17: eliminar la propia con mensaje «Meta eliminada.».
    - CA18: meta ajena y meta inexistente dan 404, y la ajena sigue existiendo.
    - CA19: GET da 405 y la meta sigue existiendo.
  - PaginaYEncabezadoTests
    - CA20: un solo `<h1`, `<th scope="col"` con las 9 columnas, 3 `csrfmiddlewaretoken` con una meta, `aria-label="Eliminar meta Portátil"`, y herencia de la base (`lang`, `viewport`, `<main`).
    - CA21: enlace `href="/metas/"` en `/gastos/` con sesión, y ausente en `/login/` sin sesión.

NECESITA DE OTRO AGENTE: nada.

PREGUNTAS PARA EL DESARROLLADOR: ninguna bloqueante. Dos supuestos que los implementadores deben respetar, porque la spec no los fija:
- Las pruebas leen el formulario del contexto como `respuesta.context["formulario"]`, igual que la vista de gastos.
- `test_pagina_muestra_los_valores_de_la_meta_en_curso` comprueba el 3 de «Meses restantes» con la expresión regular `>\s*3\s*<`, es decir, el 3 como único contenido de una celda.
```

### Notas del coordinador sobre el rojo
- **Salida truncada:** la salida completa de `python manage.py test` superó el límite de la herramienta y el hook no permite redirigirla a un archivo (un comando por llamada). El rojo se acreditó por módulo. Ajuste sugerido al arnés: permitir `python manage.py test ... 2>&1 | tail -n 40` o la redirección a un archivo del scratchpad.
- Los dos supuestos del probador (`context["formulario"]` y el 3 como único contenido de una celda) se pasan como requisitos a los implementadores.

## Verde del backend (implementador-backend, T3 y T4)

Informe del implementador-backend, copiado tal cual:

```
ESTADO: verde para lo que me corresponde. La spec 004 sigue incompleta en el backend porque falta la plantilla y el enlace del encabezado, que son del frontend.

ARCHIVOS (los cuatro permitidos):
- gastos/reglas/metas.py: añadí `calcular_falta(precio, ahorrado)` y `estado_meta(precio, ahorrado, fecha_limite, hoy)`. Son funciones puras, sin Django ni float.
- gastos/forms.py: añadí `FormularioMeta`, con los campos, etiquetas, widget de fecha y mensajes de centavos pedidos. `ahorrado` es obligatorio con valor inicial 0. `__init__(..., hoy=None)` usa `timezone.localdate()` por defecto. `clean()` llama a `validar_meta` y solo añade el error de un campo si ese campo no había fallado antes.
- gastos/views.py: añadí `NOMBRES_ESTADO`, `lista_metas` y `eliminar_meta`, como los describiste.
- gastos/urls.py: añadí `metas/` (`lista_metas`) y `metas/<int:pk>/eliminar/` (`eliminar_meta`).

EVIDENCIA:
- `python manage.py test gastos.tests.test_regla_metas` da `Ran 43 tests in 0.002s`, `OK`.
- `python manage.py test gastos.tests.test_vista_metas` da `Ran 45 tests`, `FAILED`. La salida completa se trunca en la herramienta, así que solo tengo el patrón de resultados: `EEEE.EEEE.EEEEEEEEE.E..EEEEEEEEEFEEE.EEEE....`. Son 44 errores y fallos, y 5 pruebas pasan: `test_crear_ignora_usuario_enviado`, `test_formulario_vacio_tiene_ahorrado_en_cero_y_sin_usuario`, `test_eliminar_meta_inexistente_da_404`, `test_eliminar_por_get_no_permitido` y `test_no_elimina_meta_ajena`.
- Las clases `ListaMetasTests` (8 pruebas) y `EliminarMetaTests` (5 pruebas, ejecutadas con una prueba de `ListaMetasTests`) dieron todas el mismo error. Las ejecuté por separado con la salida completa: `Ran 8 tests ... FAILED (errors=8)` y `Ran 5 tests ... FAILED (errors=2)`. Todos los errores son `TemplateDoesNotExist: gastos/metas.html`.
- Suite previa: `python manage.py test gastos.tests.test_vista_gastos gastos.tests.test_vista_hormiga gastos.tests.test_arquitectura gastos.tests.test_modelo_meta gastos.tests.test_autenticacion gastos.tests.test_inicio gastos.tests.test_gasto gastos.tests.test_reglas_gastos gastos.tests.test_regla_hormiga gastos.tests.test_hook_permisos` da `Ran 141 tests in 32.665s`, `OK`.
- `python manage.py check` da `System check identified no issues (0 silenced).`
- No ejecuté `makemigrations --check` ni `coverage`: no toqué modelos y la cobertura queda para el cierre, cuando exista la plantilla.

PRUEBAS QUE SIGUEN FALLANDO (todas en `gastos/tests/test_vista_metas.py`, 40 con `TemplateDoesNotExist` y 1 por el enlace):
- Casi todo `CrearMetaTests` falla por `TemplateDoesNotExist`. El motivo es que el redirect o el reenvío con errores renderiza la página, o que la prueba pide la página directamente. Es el caso de las pruebas de ahorrado, fecha límite, nombre, precio, `test_crear_meta_asigna_usuario_redirige_y_avisa`, `test_formulario_invalido_conserva_los_datos` y `test_pagina_muestra_ahorrado_con_cero_inicial`.
- `ListaMetasTests`: las 8 fallan por `TemplateDoesNotExist`.
- `EliminarMetaTests.test_eliminar_meta_propia`: `TemplateDoesNotExist` al seguir la redirección.
- `PaginaYEncabezadoTests`: los 6 con `TemplateDoesNotExist` son `test_pagina_tiene_un_solo_h1`, `test_tabla_usa_encabezados_con_scope`, `test_pagina_con_una_meta_tiene_tres_tokens_csrf`, `test_boton_eliminar_nombra_la_meta`, `test_pagina_hereda_de_la_base` y probablemente una más.
- `PaginaYEncabezadoTests.test_con_sesion_el_encabezado_enlaza_a_metas` (CA21) es la única `FAIL`. No encuentra `href="/metas/"` en el encabezado de `templates/base.html`. Lo confirmé ejecutándola sola.
- No pude listar nombre por nombre los últimos 4 puntos del patrón (`....`). Parecen ser pruebas posteriores que no renderizan `metas.html`, como `test_sin_sesion_el_encabezado_no_enlaza_a_metas`.

NECESITA DE OTRO AGENTE: implementador-frontend debe crear `templates/gastos/metas.html` y añadir en `templates/base.html` el enlace `href="/metas/"` con el texto «Metas de ahorro», solo con sesión. La plantilla debe cumplir lo que piden las pruebas:
- un solo `<h1>` y «Metas de ahorro»;
- `<th scope="col">` para Nombre, Precio, Ahorrado, Falta, Fecha límite, Meses restantes, Cuota mensual, Estado y Acciones;
- `aria-label="Eliminar meta <nombre>"`;
- 3 tokens csrf con una meta (crear, eliminar y cerrar sesión);
- el campo `ahorrado` con `value="0"` y `type="date"` para la fecha.
Cuando exista, hay que volver a correr toda la suite, `makemigrations --check --dry-run` y `coverage`.

PREGUNTAS PARA EL DESARROLLADOR: ninguna. Una nota: el hook rechazó un `ls` mío, así que lo único que leí fueron los archivos con Read.
```

### Notas del coordinador sobre el verde del backend
- Revisé el diff (`git diff`): solo cambian los cuatro archivos permitidos y coincide con el plan.
- `NECESITA DE OTRO AGENTE` se resuelve encargando T5 al implementador-frontend.
- El hook rechazó un `ls` del implementador-backend; no afectó al trabajo (usó Read). Segunda vez que la salida de la suite se trunca: refuerza el ajuste sugerido arriba.

## Verde del frontend (implementador-frontend, T5)

Informe del implementador-frontend, copiado tal cual:

```
ESTADO: verde

ARCHIVOS:
- templates/gastos/metas.html (nuevo). Hereda de base.html y tiene un solo h1. Tiene la sección «Nueva meta» con el formulario POST, csrf_token, errores generales, los 4 campos con `_campo.html` y el botón «Guardar meta». La sección «Mis metas» tiene la tabla con caption, `th scope="col"` y columnas numéricas con clase `numero`. `meta.meses` es el único contenido de su celda. El estado va en `<span class="estado estado-{{ meta.estado }}">{{ meta.estado_nombre }}</span>`. El botón Eliminar lleva `aria-label="Eliminar meta {{ meta.nombre }}"`. Si no hay metas, muestra «Aún no tienes metas de ahorro.» y no hay tabla. No tiene lógica.
- templates/base.html: enlace «Metas de ahorro» (`lista_metas`) en el `<nav>`, después de «Gasto hormiga».
- static/estilos.css: `.estado` en negrita y `.estado-vencida` en #B42318. Ese rojo es el mismo de `.error`. El texto del estado ya se muestra, así que no depende solo del color. Usé «vencida» porque `estado_meta` en `gastos/reglas/metas.py` devuelve cumplida, vencida o en_curso.

EVIDENCIA:
- `python manage.py test gastos.tests.test_vista_metas`: Found 45 test(s). `Ran 45 tests in 30.138s` OK.
- `python manage.py test` (completo): Found 229 test(s). `Ran 229 tests in 61.577s` OK. System check sin problemas.
- No ejecuté `coverage run`, `coverage report` ni `makemigrations --check --dry-run`. El hook de mi agente solo permite `python manage.py test` y `curl -s` a localhost. Tampoco hice curl, porque no sé si el servidor estaba encendido.
- Un `grep` mío fue rechazado por el hook (el comando llevaba una barra invertida). Leí el archivo con Read en su lugar.

NECESITA DE OTRO AGENTE: nada. Quien tenga permisos debe ejecutar la cobertura (mínimo 80 % en `gastos/`) y `makemigrations --check --dry-run`.

PREGUNTAS PARA EL DESARROLLADOR: ninguna.
```

### Notas del coordinador sobre el verde del frontend
- Revisé el diff y la plantilla nueva: solo cambian los tres archivos permitidos; la plantilla no tiene lógica y sigue el patrón de `lista.html`.
- El hook del implementador-frontend no permite `coverage` ni `makemigrations --check`, y el del coordinador solo permite git. Se pide al revisor que los ejecute; si tampoco puede, los ejecuta el desarrollador (y los corre la CI en el pull request).
- El hook rechazó un `grep` con barra invertida del implementador-frontend; usó Read.

## Revisión (revisor, T6)

Informe del revisor, copiado tal cual:

```
ESTADO: con hallazgos

El código cumple la spec 004. Solo hay un hallazgo serio: la prueba de CA21 «sin sesión» no prueba lo que dice. Lo demás es de severidad baja.

HALLAZGOS:

1. `gastos/tests/test_vista_metas.py:378-382` · alta (prueba que no prueba) · rol: **probador**
   - **Qué pasa:** `test_sin_sesion_el_encabezado_no_enlaza_a_metas` pide `/login/`. Esa página extiende `autenticacion/base.html`, no `templates/base.html`, así que nunca muestra el encabezado con la navegación.
   - **Con qué entrada falla:** si en `templates/base.html:18` se quita el `{% if user.is_authenticated %}` y el enlace «Metas de ahorro» queda visible para todos, la prueba sigue en verde.
   - **Qué incumple:** CA21 dice «sin sesión no aparece» en las páginas que heredan de `base.html`.
   - **Propuesta:** pedir `/` (`inicio.html` sí extiende `base.html`) sin sesión y comprobar que no está `href="/metas/"`.

2. `gastos/tests/test_vista_metas.py:129` · baja · rol: **probador**
   - **Qué pasa:** `assertRegex(..., r">\s*3\s*<")` es una aserción débil para «la página muestra 3» (CA8). Cualquier elemento cuyo texto sea `3` la cumple.
   - **Propuesta:** buscar `<td class="numero">3</td>`.

3. `gastos/tests/test_vista_metas.py:291-296` · baja · rol: **probador**
   - **Qué pasa:** `assertContains(respuesta, 'value="0"')` no está atado al campo `ahorrado` (CA16).
   - **Propuesta:** comprobar el `<input>` completo de `id_ahorrado`. La spec también pide que la fecha límite esté vacía al principio, y ninguna prueba lo comprueba.

4. `gastos/tests/test_vista_metas.py:358-362` · baja · rol: **probador**
   - **Qué pasa:** el `aria-label` solo se prueba con «Portátil». No hay caso con `"`, `<` o `&` en `meta.nombre`.
   - El escape automático de Django lo cubre hoy (`templates/gastos/metas.html:56` no usa `|safe`), pero ninguna prueba lo protege si alguien lo cambia.

5. `gastos/tests/test_vista_metas.py:242-249` · baja · rol: **probador**
   - Faltan casos:
     - nombre vacío y nombre de 101 caracteres solo comprueban el campo, no el mensaje;
     - no hay casos de `ahorrado` vacío (la decisión «ahorrado es obligatorio» no tiene prueba), precio vacío ni fecha límite vacía;
     - `test_ahorrado_cero_es_valido` (línea 202) no comprueba el valor guardado.

6. `gastos/forms.py:43` · baja · rol: **implementador-backend**
   - `self.fields["ahorrado"].required = True` es redundante: el campo del modelo no tiene `blank=True`, así que ya es obligatorio. No hace daño. Si se mantiene como intención explícita, que lo cubra la prueba del punto 5.

7. `templates/gastos/metas.html:54-57` · baja · rol: **implementador-frontend** (decisión del desarrollador)
   - **Qué pasa:** «Eliminar» borra sin confirmar ni deshacer. La regla de web-design-guidelines dice: «Destructive actions need confirmation or an undo window».
   - Es coherente con `lista.html` y la spec excluye JavaScript, así que lo dejo también en preguntas.

8. `gastos/forms.py:32` · baja · rol: **implementador-backend**
   - Los campos no llevan `autocomplete="off"`, que la guía pide en campos que no son de acceso. Lo mismo pasa en `FormularioGasto`: es coherente con el código actual, pero no con la guía.

**Sin hallazgos en estos apartados:**
- **Datos de cada usuario:**
  - `login_required` en las dos vistas;
  - `Meta.objects.filter(usuario=request.user)` en `gastos/views.py`;
  - `get_object_or_404(Meta, pk=pk, usuario=request.user)` y `require_POST` al eliminar;
  - `usuario` no está en `fields`;
  - hay pruebas de 404 en ajena e inexistente, de 405 por GET y de que el `usuario` enviado se ignora.
- **Arquitectura:**
  - `gastos/reglas/metas.py` no importa Django; lo comprueba `test_arquitectura.py`, que recorre todo `reglas/`;
  - no hay `float`: todo usa `int()` sobre `Decimal`;
  - la vista solo llama a las reglas, y `NOMBRES_ESTADO` está en la vista como pide el plan;
  - la plantilla no calcula nada.
- **Base de datos:** no hay migraciones nuevas ni modificadas; `db.sqlite3` y `.env` no están en el diff.
- **Plantilla:**
  - hereda de `base.html` y usa `_campo.html`;
  - lleva `csrf_token` en los dos formularios;
  - tiene un solo `<h1>`, `th scope="col"`, `caption` y `.tabla-desplazable`;
  - las columnas numéricas usan `tabular-nums` y los montos `floatformat:"0g"`;
  - las fechas van en `<time datetime>`, el foco visible está en `estilos.css`, los textos están en español y está el estado vacío;
  - el rojo `#B42318` sobre blanco tiene buen contraste, y el estado va también como texto, no solo como color.
- **Reloj:** el `mock.patch` de `django.utils.timezone.localdate` se arranca en `setUp` y se detiene con `self.addCleanup(parche.stop)`. Las reglas se prueban con `HOY = date(2026, 11, 14)` fijo. Están los casos límite: fecha hoy y ayer, falta de 1 peso, ahorrado igual al precio y 1 peso por encima, nombre de 100 y 101 caracteres, precio 1.
- **Decisión «vencida cuenta el día»:** se cumple. `fecha_limite < hoy`, y la vista lo prueba con 2026-11-13, que es del mismo mes.
- **Historial:** el commit `test:` (d99f8b2) va antes de los dos `feat:`.

DIFERENCIAS CON LA SPEC:
- CA21, mitad «sin sesión»: no tiene una prueba válida (hallazgo 1).
- Ningún archivo fuera del plan y `requirements.txt` sin cambios. El archivo opcional `test_formulario_meta.py` no se creó; CA16 está en `test_vista_metas.py`, como el plan permite.
- `specs/004-pantalla-metas/tareas.md` tiene T1–T6 sin marcar y `specs/004-pantalla-metas/evidencia.md` está sin seguimiento en git. Hay que completarlos y hacer commit antes del PR.

EVIDENCIA (pude ejecutar los cuatro comandos):
- `git diff main...HEAD --stat`: 12 archivos, 767 inserciones y 3 borrados. Son los del plan más los tres de la spec.
- `python manage.py test`: `Ran 229 tests in 64.746s` · `OK`
- `python manage.py check`: `System check identified no issues (0 silenced).`
- `python manage.py makemigrations --check --dry-run`: `No changes detected`
- `coverage run --source=gastos manage.py test`: `Ran 229 tests in 60.922s` · `OK`. Usé `--source=gastos` como indica la skill.
- `coverage report`, las líneas que importan:
    gastos/forms.py          80   0  100%
    gastos/models.py         33   1   97%   35
    gastos/reglas/metas.py   30   0  100%
    gastos/urls.py            5   0  100%
    gastos/views.py          81   0  100%
    TOTAL                   261   1   99%
  99 % de cobertura, por encima del mínimo de 80 %.

El hook me rechazó `git grep` (no está en mi lista de comandos); ese dato lo saqué leyendo los archivos con Read. Revisé las plantillas con web-design-guidelines: solo salen los hallazgos 7 y 8.

NECESITA DE OTRO AGENTE:
- **probador:** hallazgo 1 (debe corregirse antes del PR) y hallazgos 2 a 5.
- **implementador-backend:** hallazgos 6 y 8 (opcionales).
- **coordinador:** marcar `tareas.md` y hacer commit de `evidencia.md`.

PREGUNTAS PARA EL DESARROLLADOR:
- ¿Se acepta que «Eliminar» borre sin confirmación (igual que en gastos), o se quiere confirmación o deshacer? La guía lo pide; la spec excluye JavaScript, así que haría falta un paso intermedio en el servidor.
- ¿Se agrega `autocomplete="off"` a los formularios del dominio (gastos y metas) en una spec aparte, para que sigan siendo coherentes entre sí?
```

### Qué se hizo con cada hallazgo
| # | Gravedad | Decisión | Motivo |
|---|---|---|---|
| 1 | alta | **Corregido** por el probador (vuelta 1) | La prueba ahora pide `/`, que hereda de `base.html`, y comprueba que el encabezado está y el enlace no. |
| 2 | baja | **Corregido** por el probador | `assertContains('<td class="numero">3</td>', html=True)`. |
| 3 | baja | **Corregido** por el probador | Valor inicial de `ahorrado` atado a su `<input>`; `fecha_limite` vacía al principio. |
| 4 | baja | **Corregido** por el probador | Prueba nueva del escape del `aria-label` con `"`, `<` y `&`. |
| 5 | baja | **Corregido** por el probador | Mensajes de obligatorio y de longitud; `precio`, `ahorrado` y `fecha_limite` vacíos; valor guardado de `ahorrado` 0. |
| 6 | baja | **Descartado** (coordinador) | La línea redundante deja explícita la decisión aprobada «ahorrado es obligatorio» y ahora la cubre `test_ahorrado_vacio_no_guarda`. No se toca código para evitar un `fix:` sin efecto. |
| 7 | baja | **Descartado** (desarrollador, 2026-11-14) | Se acepta que «Eliminar» borre sin confirmación, igual que en `/gastos/`. |
| 8 | baja | **Aplazado a otra spec** (desarrollador, 2026-11-14) | `autocomplete="off"` se tratará en una spec aparte para los formularios de gastos y de metas a la vez, para que sigan siendo coherentes. |

## Corrección de la revisión (probador, vuelta 1)

Informe del probador, copiado tal cual:

```
ESTADO: rojo confirmado no aplica; son pruebas de regresión y todas pasan (verde). Los 5 hallazgos están corregidos.

ARCHIVOS: gastos/tests/test_vista_metas.py (único archivo tocado; no hice commits).

CAMBIOS POR HALLAZGO
1. (CA21) `test_sin_sesion_el_encabezado_no_enlaza_a_metas` ahora pide `/` sin sesión. Comprueba 200, `assertTemplateUsed "base.html"`, `class="encabezado"` y `<a class="marca" href="/"`. Luego comprueba que NO aparecen `href="/metas/"` ni "Metas de ahorro".
2. (CA8) `test_pagina_muestra_los_valores_de_la_meta_en_curso` sustituye el `assertRegex` por `assertContains(respuesta, '<td class="numero">3</td>', html=True)`.
3. (CA16) `test_pagina_muestra_ahorrado_con_cero_inicial` comprueba lo siguiente:
   - `context["formulario"]["ahorrado"].value() == 0`.
   - `fecha_limite.value()` es `None`.
   - El `<input>` con `id="id_ahorrado"` y `name="ahorrado"` lleva `value="0"` (regex sobre el input).
   - El input `id_fecha_limite` existe, es `type="date"` y su etiqueta no contiene `value=`.
   - Añadí `import re` al archivo.
4. (CA20) Prueba nueva `test_nombre_con_caracteres_especiales_sale_escapado_en_aria_label`. Usa el nombre `Viaje "Cali" <2027> & más`. Comprueba `aria-label="Eliminar meta Viaje &quot;Cali&quot; &lt;2027&gt; &amp; más"` y que `<2027>` y `Viaje "Cali"` no aparecen sin escapar.
5. (CA14/CA15)
   - Nuevo auxiliar `obligatorio(campo)`, que toma el mensaje real de `FormularioMeta().fields[campo].error_messages["required"]`. No fija texto, aunque `LANGUAGE_CODE` es `es-co`.
   - `test_nombre_vacio_no_guarda` y `test_nombre_solo_espacios_no_guarda` ahora comprueban ese mensaje en el formulario y en la página.
   - `test_nombre_de_101_caracteres_no_guarda` comprueba que el mensaje de error contiene "100" y "101" (longitud máxima de Django).
   - Pruebas nuevas: `test_precio_vacio_no_guarda`, `test_ahorrado_vacio_no_guarda` y `test_fecha_limite_vacia_no_guarda`. Cada una comprueba un único error, en su campo, con el mensaje de obligatorio, y que no se guarda nada.
   - `test_ahorrado_cero_es_valido` comprueba además que `Meta.objects.get().ahorrado == 0`.

EVIDENCIA
- `python manage.py test gastos.tests.test_vista_metas` dio: `Ran 49 tests in 32.819s` / `OK`.
- `python manage.py test` dio: `Ran 233 tests in 67.216s` / `OK`, sin sistema de avisos (`System check identified no issues`).
- No falla ninguna prueba nueva, así que no hay defecto aparente en el código.
- No pude ver que las pruebas fallen ante un defecto simulado, porque no puedo tocar el código de la aplicación.

NECESITA DE OTRO AGENTE: nada.

PREGUNTAS PARA EL DESARROLLADOR: ninguna.
```

### Notas del coordinador sobre la corrección
- Revisé el diff de la corrección (`git diff`): solo cambia `gastos/tests/test_vista_metas.py` y cada cambio corresponde a un hallazgo. Commit `test:` (1ab8d76), no `fix:`, porque no cambió código de la aplicación.
- Una sola vuelta de corrección; no quedan hallazgos abiertos. No se pidió una segunda revisión completa: los cambios son solo de pruebas y los verifiqué en el diff.
- Las pruebas de regresión no se vieron fallar ante un defecto simulado (el probador no puede tocar el código). El hallazgo 1 explica con qué cambio habría fallado la prueba nueva.

## Resultado final
- `python manage.py test`: `Ran 233 tests` · `OK` (probador, tras la corrección).
- Cobertura: 99 % en `gastos/` (revisor, antes de la corrección; la corrección solo añade pruebas).
- `makemigrations --check --dry-run`: `No changes detected` (revisor).

## Incidencias del arnés (para ajustarlo)
1. La salida completa de `python manage.py test` se trunca en la herramienta y los hooks no permiten redirigirla ni filtrarla con `tail` (probador e implementador-backend). Propuesta: permitir `python manage.py test ... 2>&1 | tail -n 40` o la redirección a un archivo temporal.
2. El hook del implementador-frontend no permite `coverage` ni `makemigrations --check`; los ejecutó el revisor.
3. Rechazos menores: `ls` (implementador-backend), `grep` con barra invertida (implementador-frontend), `git grep` (revisor). Todos se sortearon con Read.

## Pull request
https://github.com/JuanDR403/Hormiguero/pull/13 (fusionado).
