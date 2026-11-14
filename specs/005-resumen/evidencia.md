# Evidencia 005 · Resumen

## Rojo (probador, T1 y T2)

Informe del probador, copiado tal cual:

```
ESTADO: rojo confirmado

ARCHIVOS (nuevos; no toqué nada más):
- /home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_regla_resumen.py
- /home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_vista_resumen.py

EVIDENCIA

1. `python manage.py test gastos.tests.test_regla_resumen`
ImportError: cannot import name 'resumen' from 'gastos.reglas' (/home/jdrickxd/Documentos/Proyecto_Integrador/gastos/reglas/__init__.py)
Ran 1 test in 0.000s
FAILED (errors=1)

El módulo `gastos/reglas/resumen.py` no existe, así que `from gastos.reglas import resumen` da `ImportError`, no `AttributeError`. Es un `ImportError` solo de este módulo de pruebas: las demás pruebas se cargan bien. Cuando el módulo exista, las 10 pruebas de la regla fallarán por `AttributeError: ... resumir_mes` hasta que se implemente la función. No pude ver ese segundo estado sin crear código de producción.

2. `python manage.py test gastos.tests.test_vista_resumen`
Ran 18 tests in 9.056s
FAILED (failures=3, errors=13)

- 13 errores: `KeyError` en el contexto (`'total_mes'`, `'por_categoria'`, `'cantidad_hormiga'`, `'hoy'`). La vista `inicio` aún no calcula el resumen.
- 3 fallos `AssertionError`: la plantilla actual muestra `<h1>Hormiguero</h1>` y no «Resumen». Faltan «Transporte», `<th scope="col"` y los demás textos del resumen.
- 2 pruebas pasan ya, y es válido: `test_sin_sesion_conserva_la_pagina_de_acceso` y `test_sin_sesion_el_contexto_no_trae_total_mes`. Son CA9, que pide que la página sin sesión siga igual. Funcionan como guarda de regresión para el cambio de la vista.

3. `python manage.py test` completo
Ran 252 tests in 58.814s
FAILED (failures=3, errors=14)

Los 17 problemas son 1 `ImportError` del módulo de la regla y los 16 de la vista. No hay otros fallos.

`python manage.py test gastos.tests.test_inicio gastos.tests.test_arquitectura`
Ran 6 tests in 0.017s
OK

Las pruebas existentes siguen en verde. CA8 queda cubierta por `test_arquitectura.py`, que revisa las reglas sin importar Django. Para `resumen.py` solo se aplicará cuando el archivo exista.

Pruebas nuevas y criterio que cubre cada una

`test_regla_resumen.py` (`SimpleTestCase`, hoy = 2026-11-14):
- `test_cuenta_dia_uno_y_hoy_pero_no_el_ultimo_dia_del_mes_anterior`: CA1.
- `test_no_cuenta_gasto_posterior_a_hoy`: CA2 (fecha futura).
- `test_no_cuenta_el_mismo_mes_de_otro_anio`: CA2 (otro año).
- `test_hoy_primero_de_mes_solo_cuenta_ese_dia`: CA3 (hoy = 2026-12-01).
- `test_sin_gastos_total_cero_y_lista_vacia`: CA4.
- `test_sin_gastos_del_mes_total_cero_y_lista_vacia`: CA4.
- `test_suma_por_categoria_ordena_por_total_y_omite_otro_mes`: CA5.
- `test_empate_se_ordena_por_codigo_ascendente`: CA6.
- `test_acepta_decimal_y_devuelve_enteros`: CA7.
- `test_total_cero_es_entero`: CA7.

`test_vista_resumen.py` (`TestCase`):
- `test_sin_sesion_conserva_la_pagina_de_acceso`: CA9.
- `test_sin_sesion_el_contexto_no_trae_total_mes`: CA9.
- `test_con_sesion_usa_inicio_con_h1_resumen_y_saludo`: CA10.
- `test_total_del_mes_en_contexto_y_en_la_pagina`: CA11.
- `test_el_contexto_trae_hoy_y_dias`: contexto `hoy` y `dias` (plan).
- `test_gastos_de_otro_usuario_no_cuentan`: CA12, aislamiento de total, categorías, hormiga y textos.
- `test_por_categoria_en_el_contexto_en_el_orden_de_la_regla`: CA13.
- `test_la_pagina_muestra_categorias_en_orden_y_sin_salud`: CA13.
- `test_categoria_desconocida_muestra_el_codigo`: CA14.
- `test_sin_gastos_en_el_mes_muestra_cero_y_el_aviso`: CA15.
- `test_solo_gastos_de_otro_mes_cuenta_como_sin_gastos`: CA15.
- `test_tres_tintos_muestran_aviso_singular_y_enlace`: CA16.
- `test_dos_grupos_muestran_aviso_plural`: CA16.
- `test_aviso_usa_ventana_de_30_dias_y_no_el_mes`: CA17.
- `test_sin_gasto_hormiga_no_hay_aviso_ni_enlace`: CA18.
- `test_usa_n_de_settings`: CA19 (`GASTO_HORMIGA_N=2`).
- `test_usa_umbral_de_settings`: CA19 (`GASTO_HORMIGA_UMBRAL=3000`).
- `test_tabla_accesible_un_csrf_y_un_h1`: CA20.

Notas
- El saludo «Hola, Ana.» ya aparece en la plantilla actual, así que no es lo que hace fallar CA10. Esa prueba falla por el `<h1>`.
- En `test_el_contexto_trae_hoy_y_dias` comprobé que `dias` vale 30 (el valor de `VENTANA_DIAS`).
- No hice commits.

NECESITA DE OTRO AGENTE: nada. Los pasos siguientes son T3 y T4 (implementador-backend) y T5 (implementador-frontend).

PREGUNTAS PARA EL DESARROLLADOR: ninguna
```

Nota del coordinador: el rojo de la regla es un `ImportError` del módulo de pruebas (el archivo `resumen.py` no existe), no un `AttributeError` por función. Se acepta: el fallo es por falta de código y no afecta la carga de las demás pruebas.

## Verde del backend (implementador-backend, T3 y T4)

Informe del implementador-backend, copiado tal cual:

```
ESTADO: verde para el backend (T3 y T4). Los 9 fallos que quedan son solo de plantilla, como se esperaba. Falta T5 (frontend).

ARCHIVOS
- Nuevo: /home/jdrickxd/Documentos/Proyecto_Integrador/gastos/reglas/resumen.py
- Modificado: /home/jdrickxd/Documentos/Proyecto_Integrador/gastos/views.py (solo la vista `inicio` y el import de `resumir_mes`)

EVIDENCIA
1. `python manage.py test gastos.tests.test_regla_resumen`:
..........
Ran 10 tests in 0.001s
OK
Found 10 test(s).
System check identified no issues (0 silenced).

`python manage.py test gastos.tests.test_arquitectura`:
..
Ran 2 tests in 0.002s
OK

2. `python manage.py test gastos.tests.test_vista_resumen`: `Ran 18 tests`, `FAILED (failures=9)`. Aprueban 9: ventana de 30 días, categoría desconocida, contexto con `hoy` y `dias`, aislamiento entre usuarios, orden de `por_categoria` en el contexto, sin gasto hormiga, las dos de sin sesión y el umbral de settings.

Fallan 9, todas porque `templates/inicio.html` sigue siendo la plantilla vieja (`<h1>Hormiguero</h1>`, título «Inicio», «Ver mis gastos»):
- `test_con_sesion_usa_inicio_con_h1_resumen_y_saludo`: falta `<h1>Resumen</h1>`.
- `test_total_del_mes_en_contexto_y_en_la_pagina`: el contexto da 25000, pero falta «$25.000» y «noviembre de 2026» en el HTML.
- `test_la_pagina_muestra_categorias_en_orden_y_sin_salud`: falta la tabla con «Transporte», «Alimentación» y los montos.
- `test_sin_gastos_en_el_mes_muestra_cero_y_el_aviso`: faltan «$0» y «No tienes gastos registrados este mes.».
- `test_solo_gastos_de_otro_mes_cuenta_como_sin_gastos`: falta el aviso de que no hay gastos este mes. No leí el cuerpo de esta prueba, así que el motivo exacto lo deduzco del nombre y de la plantilla vieja.
- `test_tabla_accesible_un_csrf_y_un_h1`: faltan los `<th scope="col">` y el `<h1>` Resumen.
- `test_tres_tintos_muestran_aviso_singular_y_enlace`: falta «Detectamos 1 gasto hormiga…» y el enlace.
- `test_dos_grupos_muestran_aviso_plural`: falta «Detectamos 2 gastos hormiga…».
- `test_usa_n_de_settings`: falta «Detectamos 1 gasto hormiga» en el HTML (el cálculo con N=2 sí llega al contexto).

Para el último caso, la salida truncada solo me dejó ver el fallo de HTML en las pruebas de aviso, tabla y h1. En las demás deduzco el motivo por el nombre.

3. `python manage.py test` completo: `Ran 261 tests in 58.667s`, `FAILED (failures=9)`. Son las mismas 9 de arriba, todas en `test_vista_resumen`. Ninguna prueba existente se rompió, incluida `test_inicio.py`.
`python manage.py check`: `System check identified no issues (0 silenced).`
No ejecuté `makemigrations --check` ni `coverage`. No toqué modelos, y esos dos pasos tienen más sentido cuando el frontend esté verde.

4. Diff resumido
- `gastos/reglas/resumen.py` (nuevo, sin importar Django): `resumir_mes(gastos, hoy)` filtra `hoy.replace(day=1) <= fecha <= hoy`. Suma con `int(monto)` y agrupa por categoría. Ordena con `key=(-total, categoria)`. Devuelve `{"total": int, "por_categoria": [{"categoria", "total"}]}`.
- `gastos/views.py`: sin sesión devuelve `render(request, "inicio.html")` sin contexto extra. Con sesión usa `hoy = timezone.localdate()`, gastos filtrados por `request.user`, `resumir_mes` y `categoria_nombre` con `dict(Gasto.Categoria.choices).get(codigo, codigo)`. Calcula `detectar_gasto_hormiga` con los settings. El contexto trae `hoy`, `total_mes`, `por_categoria`, `cantidad_hormiga` (= `len(grupos)`) y `dias` (= `VENTANA_DIAS`). No cambié URLs ni otras vistas.

NECESITA DE OTRO AGENTE: implementador-frontend debe reescribir `templates/inicio.html` (T5), con las dos ramas del plan:
- Con sesión: título «Resumen», `<h1>Resumen</h1>`, saludo y aviso hormiga con `pluralize` y enlace a `/hormiga/`.
- Total: «Total de {{ hoy|date:"F \d\e Y" }}» con `${{ total_mes|floatformat:"0g" }}`.
- «Por categoría»: tabla con `<th scope="col">` y `categoria_nombre`, o «No tienes gastos registrados este mes.».
- Sin sesión: el contenido actual.
Con eso deben pasar las 9 pruebas que fallan. No creo que ninguna prueba esté mal.

PREGUNTAS PARA EL DESARROLLADOR: ninguna
```

Nota del coordinador: revisé `git diff gastos/views.py` y `gastos/reglas/resumen.py`; solo cambian la vista `inicio` y la regla nueva, dentro del alcance del plan. El estado intermedio (9 fallos de plantilla) es el previsto en `plan.md`.

## Verde del frontend (implementador-frontend, T5)

Informe del implementador-frontend, copiado tal cual:

````
ESTADO: verde para las pruebas. Falta la evidencia de cobertura, que no pude generar porque el hook de permisos bloquea `coverage`.

ARCHIVOS:
- Modifiqué `/home/jdrickxd/Documentos/Proyecto_Integrador/templates/inicio.html`.
- No toqué `static/estilos.css`. El aviso usa `<p class="aviso-hormiga">`, una clase que no tiene regla en el CSS. Si no se quiere esa clase, se quita sin efecto visual.

EVIDENCIA:
1. `python manage.py test gastos.tests.test_vista_resumen gastos.tests.test_inicio`:
Creating test database for alias 'default'...
......................
----------------------------------------------------------------------
Ran 22 tests in 8.703s

OK
Destroying test database for alias 'default'...
Found 22 test(s).
System check identified no issues (0 silenced).

2. `python manage.py test`:
Creating test database for alias 'default'...
.....................................................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 261 tests in 58.974s

OK
Destroying test database for alias 'default'...
Found 261 test(s).
System check identified no issues (0 silenced).

3. Cobertura: `coverage run manage.py test` falló con este error del hook: «implementador-frontend solo puede ejecutar: python manage.py test; curl -s http://localhost:8000/; curl -s http://127.0.0.1:8000/». No ejecuté `coverage report` y no intenté rodear el hook. No hay porcentaje de `gastos/`. Esta tarea solo cambió una plantilla, así que la cobertura de `gastos/` no debería variar respecto al backend ya hecho.

4. Contenido final de `templates/inicio.html`:
{% extends "base.html" %}

{% block titulo %}{% if user.is_authenticated %}Resumen{% else %}Inicio{% endif %}{% endblock %}

{% block contenido %}
  {% if user.is_authenticated %}
    <h1>Resumen</h1>
    <p>Hola, {{ user.first_name }}.</p>
    {% if cantidad_hormiga %}
      <p class="aviso-hormiga">Detectamos {{ cantidad_hormiga }} gasto{{ cantidad_hormiga|pluralize }} hormiga en los últimos {{ dias }} días.
        <a href="{% url 'hormiga' %}">Ver gasto hormiga</a></p>
    {% endif %}

    <section class="bloque" aria-labelledby="titulo-total">
      <h2 id="titulo-total">Total de {{ hoy|date:"F \d\e Y" }}</h2>
      <p class="numero">${{ total_mes|floatformat:"0g" }}</p>
    </section>

    <section class="bloque" aria-labelledby="titulo-categorias">
      <h2 id="titulo-categorias">Por categoría</h2>
      {% if por_categoria %}
        <div class="tabla-desplazable">
          <table>
            <caption>Total del mes por categoría. Montos en pesos colombianos.</caption>
            <thead>
              <tr>
                <th scope="col">Categoría</th>
                <th scope="col" class="numero">Total</th>
              </tr>
            </thead>
            <tbody>
              {% for fila in por_categoria %}
                <tr>
                  <td>{{ fila.categoria_nombre }}</td>
                  <td class="numero">${{ fila.total|floatformat:"0g" }}</td>
                </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      {% else %}
        <p>No tienes gastos registrados este mes.</p>
      {% endif %}
    </section>
  {% else %}
    <h1>Hormiguero</h1>
    <p>Gestor de gastos personales con metas de ahorro.</p>
    <p><a href="{% url 'login' %}">Iniciar sesión</a> · <a href="{% url 'registro' %}">Crear cuenta</a></p>
  {% endif %}
{% endblock %}

NECESITA DE OTRO AGENTE: alguien con permiso para ejecutar `coverage` (el coordinador o el probador) debe correr `coverage run manage.py test` y luego `coverage report`, y confirmar que `gastos/` llega al 80 % como mínimo.

PREGUNTAS PARA EL DESARROLLADOR: ninguna.
````

Nota del coordinador (para ajustar el sistema): el hook rechazó `coverage run manage.py test` al implementador-frontend. El coordinador tampoco puede ejecutarlo (solo git). Se encarga la medición al revisor junto con la revisión; si su hook también la rechaza, queda para el desarrollador o para el CI del pull request. Pedí la cobertura al frontend sin comprobar antes sus permisos: en próximas specs se pide al rol que puede ejecutarla.

## Revisión (revisor, T6), vuelta 1

Informe del revisor, copiado tal cual:

````
ESTADO: con hallazgos. Ninguno es bloqueante: la regla, la vista, el aislamiento y la arquitectura están bien. Los hallazgos son pruebas que no cubren del todo lo que dice la spec y dos detalles visuales.

HALLAZGOS (están en orden de gravedad. En la escala de la skill, «importante» es media y «menor» es baja):

1. Importante (media). `/home/jdrickxd/Documentos/Proyecto_Integrador/templates/inicio.html:16`: `<p class="numero">` reutiliza `.numero` de `static/estilos.css:45`, que trae `text-align: right`. Por eso el total («$25.000») sale pegado al borde derecho del `<main>` (hasta 60rem) y queda lejos de su `<h2>` «Total de noviembre de 2026», que está a la izquierda. En escritorio el dato principal del resumen se ve desconectado de su título. `.numero` está pensada para celdas de tabla. Ninguna prueba lo detecta. Lo corrige: implementador-frontend (una clase propia o quitar `numero` del `<p>`).

2. Menor (baja). `/home/jdrickxd/Documentos/Proyecto_Integrador/templates/inicio.html:10`: la clase `aviso-hormiga` no tiene regla en `static/estilos.css`. El aviso se ve igual que el saludo de la línea 8: un párrafo normal, sin color, borde ni fondo. No es un problema de accesibilidad, porque el texto y el enlace son claros y salen en el HTML del servidor. Pero el aviso es el mensaje principal de la funcionalidad y se pierde entre los demás párrafos. El plan (`plan.md:15`) lo permitía: «si el aviso necesita estilo, se añade ahí». O se acepta así, o se le da un estilo parecido a `.mensajes`. Si no se le da estilo, la clase sobra. Lo corrige: implementador-frontend, si el desarrollador decide darle estilo (ver preguntas).

3. Menor (baja). `/home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_vista_resumen.py:75-81` (CA10): la spec pide el título de pestaña «Resumen» con sesión (`spec.md:27`) e «Inicio» sin sesión, y ninguna prueba lo comprueba. Si `{% block titulo %}` de `inicio.html:3` volviera a «Inicio» fijo, todas las pruebas seguirían en verde. Falta algo como `assertContains(respuesta, "<title>Resumen · Hormiguero</title>")`. Lo corrige: probador.

4. Menor (baja). `/home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_vista_resumen.py:61-68` (CA9): con la plantilla actual, «Iniciar sesión» y «Crear cuenta» solo salen en `inicio.html` (el encabezado de `base.html` no muestra nada sin sesión), así que esa parte sí prueba algo. Lo que no se comprueba es el resto de la página «idéntica» sin sesión: `<h1>Hormiguero</h1>` y «Gestor de gastos personales con metas de ahorro.» (`inicio.html:46-47`). Si se borraran, ninguna prueba fallaría. Lo comparé a mano con `main` y el HTML sin sesión es el mismo; solo cambian los espacios. Lo corrige: probador.

5. Menor (baja). `/home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_vista_resumen.py:136-140` (CA14): solo comprueba `categoria_nombre == "antigua"` en el contexto, no que la página lo muestre. Si en `inicio.html:34` se pusiera `{{ fila.categoria }}` o una cadena vacía, la prueba no lo notaría. La spec lo redacta sobre el contexto, así que cumple la letra del criterio, pero no la intención («se muestra»). Lo corrige: probador.

6. Menor (baja). `/home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_vista_resumen.py:126-132` (CA13): comprueba que «Transporte» va antes que «Alimentación» y que los montos aparecen. No comprueba que «Hogar» vaya en tercer lugar ni que cada monto esté en la fila de su categoría. Si la plantilla pusiera los montos en otro orden, la prueba seguiría en verde. El orden completo sí se comprueba en el contexto (líneas 115-124). Lo corrige: probador.

7. Menor (baja). `/home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_vista_resumen.py:90` (CA11): `.lower()` sobre el HTML esconde un posible «Noviembre» con mayúscula, aunque la spec pide «noviembre de 2026». Con `es-co`, Django da hoy «noviembre», así que no falla. Es una aserción más débil de lo necesario. Lo corrige: probador.

Revisé y no encontré hallazgos en:
- **Aislamiento:** `views.py:32` filtra por `request.user`. CA12 crea gastos de Beto del mes, de varias categorías y con un grupo hormiga, y comprueba que no cambian `total_mes`, `por_categoria`, `cantidad_hormiga` ni los textos de Ana. `inicio` no lleva `login_required` porque la spec lo pide así. No hay formularios ni acciones que cambien datos.
- **Arquitectura:** `gastos/reglas/resumen.py` no importa nada. `test_arquitectura.py` recorre `reglas/*.py`, así que CA8 la cubre. La plantilla no suma, no compara con el umbral ni redondea: `{% if cantidad_hormiga %}` y `pluralize` solo deciden qué se muestra.
- **Montos:** `int(gasto.monto)`, ningún `float`. CA7 comprueba `type(...) is int`.
- **Fechas:** la regla usa `hoy` fijo y la vista `mock.patch("gastos.views.timezone.localdate")`. Están cubiertos el día 1, hoy, el día 31 del mes anterior, una fecha futura, el mismo mes de otro año, hoy = día 1 (CA3) y la ventana de 30 días frente al mes (CA17). Los días 30 y 31 de la ventana hormiga ya los prueba `test_regla_hormiga.py`; esta spec no cambia esa regla.
- **Base de datos:** no hay migraciones nuevas ni modificadas, y `db.sqlite3` y `.env` no están en el diff.
- **Historial:** el commit `test:` (ac812a7) va antes de los `feat:` (fb8ec5f y 73e7ec8).
- **Accesibilidad y textos (web-design-guidelines):** un solo `<h1>`; `<th scope="col">` ×2; `<caption>`; secciones con `aria-labelledby`; enlace «Ver gasto hormiga» con texto claro; textos en español; montos con `floatformat:"0g"`; tabla dentro de `.tabla-desplazable`; con 0 gastos sale un mensaje en lugar de la tabla. Un solo `csrfmiddlewaretoken`, el del cierre de sesión.

DIFERENCIAS CON LA SPEC:
- Los archivos cambiados son los del plan. `static/estilos.css` no se tocó (el plan decía «solo si hace falta»; ver hallazgos 1 y 2). `requirements.txt`, `settings.py`, `base.html`, `test_inicio.py` y `hormiga.py` no cambiaron.
- Hay requisitos de «Lo que muestra la página» sin prueba, aunque no son criterios numerados: el título de la pestaña (hallazgo 3) y que se quitó «Ver mis gastos» (la plantilla sí lo quita).
- Todos los criterios de CA1 a CA20 tienen al menos una prueba que fallaría con la plantilla vieja o con la regla mal hecha. Las salvedades son CA14, CA13 y CA11 (hallazgos 5, 6 y 7) y CA9, que comprueba la página sin sesión solo en parte (hallazgo 4).

EVIDENCIA (cada comando en una llamada; el hook no rechazó ninguno):
1. `python manage.py test`:
Creating test database for alias 'default'...
.....................................................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 261 tests in 58.692s

OK
Destroying test database for alias 'default'...
Found 261 test(s).
System check identified no issues (0 silenced).

2. `coverage run manage.py test`: `Ran 261 tests in 58.551s` / `OK` / `System check identified no issues (0 silenced).`
3. `coverage report`:
Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
gastos/__init__.py              0      0   100%
gastos/admin.py                 1      0   100%
gastos/apps.py                  3      0   100%
gastos/forms.py                80      0   100%
gastos/models.py               33      1    97%   35
gastos/reglas/__init__.py       0      0   100%
gastos/reglas/gastos.py         7      0   100%
gastos/reglas/hormiga.py       19      0   100%
gastos/reglas/hormiga.py ...
gastos/reglas/metas.py         30      0   100%
gastos/reglas/resumen.py       13      0   100%
gastos/reglas/usuarios.py       2      0   100%
gastos/urls.py                  5      0   100%
gastos/views.py                92      0   100%
---------------------------------------------------------
TOTAL                         285      1    99%

(Corrección: la línea «gastos/reglas/hormiga.py ...» no es de la salida, se me coló al copiarla. La salida real tiene una sola fila de `hormiga.py`, con 19 0 100%.) La cobertura de `gastos/` es del 99 %, por encima del 80 % mínimo. El informe solo lista `gastos/`, así que la configuración de coverage del proyecto ya limita la medición a esa carpeta.
4. `python manage.py makemigrations --check --dry-run`: `No changes detected`.
5. `git diff main...HEAD --stat`: 8 archivos y 547 líneas añadidas. Son los 5 de código y pruebas más `spec.md`, `plan.md` y `tareas.md`. `evidencia.md` todavía no está en git.

PREGUNTAS PARA EL DESARROLLADOR:
- ¿El aviso de gasto hormiga necesita destacarse visualmente con una regla `.aviso-hormiga` en `static/estilos.css`, o se acepta como párrafo normal? Si se acepta, ¿se quita la clase, que no tiene regla?
- `gastos/tests/test_inicio.py:18-22` (`test_con_sesion_enlaza_a_gastos`) ahora pasa solo por el enlace «Mis gastos» de la navegación de `base.html`, porque «Ver mis gastos» se quitó de `inicio.html` como pedía la spec. Sigue siendo válida, pero ya no prueba el contenido de `inicio.html`. ¿Se deja así? La spec pide no tocar `test_inicio.py`.
- La vista carga todos los gastos del usuario y la regla filtra el mes en Python, como dice el plan. Para el alcance del proyecto está bien. ¿Se acepta, o se prefiere filtrar las fechas en la consulta?

NECESITA DE OTRO AGENTE:
- probador: hallazgos 3 a 7.
- implementador-frontend: hallazgo 1, y el 2 según lo que decida el desarrollador.
````

Nota del coordinador: la cobertura la midió el revisor (su hook sí lo permite): 99 % en `gastos/`. Queda resuelta la medición que el hook rechazó al frontend.

### Decisiones del desarrollador sobre las preguntas del revisor (2026-11-14)
- Aviso de gasto hormiga: darle estilo con `.aviso-hormiga` en `static/estilos.css` (hallazgo 2 → se corrige).
- `test_con_sesion_enlaza_a_gastos` de `test_inicio.py`: se deja sin tocar.
- Filtrado del mes en Python (no en la consulta): se acepta como está.

Se anotaron en `spec.md` («Respondidas por el desarrollador… después de la revisión»).

### Qué se hizo con cada hallazgo
| # | Gravedad | Rol | Resultado |
|---|---|---|---|
| 1 | media | implementador-frontend | Corregido: `<p class="total-mes">` con estilo propio alineado a la izquierda. |
| 2 | baja | implementador-frontend | Corregido por decisión del desarrollador: regla `.aviso-hormiga` en `static/estilos.css`. |
| 3 | baja | probador | Corrección encargada (título de pestaña). |
| 4 | baja | probador | Corrección encargada (página sin sesión completa). |
| 5 | baja | probador | Corrección encargada (`antigua` en la página). |
| 6 | baja | probador | Corrección encargada (orden y montos por fila). |
| 7 | baja | probador | Corrección encargada (sin `.lower()`). |

El probador y el implementador-frontend trabajaron en paralelo sobre archivos distintos (`test_vista_resumen.py` frente a `inicio.html` y `estilos.css`).

### Corrección del frontend (hallazgos 1 y 2)

Informe del implementador-frontend, copiado tal cual:

````
ESTADO: verde

ARCHIVOS:
- /home/jdrickxd/Documentos/Proyecto_Integrador/templates/inicio.html
- /home/jdrickxd/Documentos/Proyecto_Integrador/static/estilos.css

EVIDENCIA:
Salida de `python manage.py test`:
Creating test database for alias 'default'...
.....(puntos)
----------------------------------------------------------------------
Ran 261 tests in 59.231s

OK
Destroying test database for alias 'default'...
Found 261 test(s).
System check identified no issues (0 silenced).

No hubo fallos en test_vista_resumen.

No pude sacar `git diff` real, porque mi hook solo permite `python manage.py test` y `curl`. Lo siguiente son los cambios exactos que apliqué:

templates/inicio.html (línea 16):
-      <p class="numero">${{ total_mes|floatformat:"0g" }}</p>
+      <p class="total-mes">${{ total_mes|floatformat:"0g" }}</p>

La celda `<td class="numero">` y el `<th class="numero">` de la tabla no cambian.

static/estilos.css (se agregó antes de `.bloque`, el resto queda igual):
+.aviso-hormiga {
+  padding: 0.75rem 1rem;
+  background: #fffbeb;
+  color: #3b2300;
+  border: 1px solid #f5c26b;
+  border-left: 6px solid #B45309;
+  border-radius: 0.25rem;
+}
+.aviso-hormiga a { color: #7c2d12; font-weight: bold; }
+
 .bloque { margin-block: 1.5rem; }
+
+.total-mes { margin: 0; font-size: 2rem; font-weight: bold; text-align: left; font-variant-numeric: tabular-nums; }

- Contraste: el texto #3b2300 sobre #fffbeb y el enlace #7c2d12 sobre #fffbeb pasan AA con holgura. Lo estimé a ojo y no lo medí con una herramienta.
- Foco: el enlace sigue visible y conserva el `:focus-visible` global, que usa un contorno de 3px en #D97706.
- No toqué textos, estructura, `<title>`, `<h1>`, `<h2>` ni el orden de los elementos.
- No hice commits.

NECESITA DE OTRO AGENTE: nada

PREGUNTAS PARA EL DESARROLLADOR: ninguna
````

Nota del coordinador: el frontend no pudo sacar el diff (su hook no admite git). Lo comprobé con `git diff templates/inicio.html static/estilos.css` y coincide con lo informado. El contraste se estimó sin herramienta; queda para la vuelta 2 del revisor.

### Refuerzo de pruebas (probador, hallazgos 3 a 7)

Informe del probador, copiado tal cual:

````
ESTADO: bloqueado. Una prueba falla por un defecto real de la plantilla (hallazgo 7). Las demás pasan.

ARCHIVOS: /home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_vista_resumen.py (único archivo tocado).

EVIDENCIA:
`python manage.py test gastos.tests.test_vista_resumen`: `Ran 22 tests in 10.846s`, `FAILED (failures=1)`.
`python manage.py test` (completo): `Ran 265 tests in 61.062s`, `FAILED (failures=1)`.
Es el mismo fallo en las dos ejecuciones:
FAIL: test_total_del_mes_en_contexto_y_en_la_pagina
  File ".../test_vista_resumen.py", line 104
    self.assertIn("noviembre de 2026", respuesta.content.decode())
AssertionError: 'noviembre de 2026' not found in '... <h2 id="titulo-total">Total de Noviembre de 2026</h2> ...

- **Qué falla:** la plantilla renderiza «Noviembre de 2026» con N mayúscula. El `.lower()` anterior ocultaba esto. La spec (sección «Lo que muestra la página» y CA11) pide «noviembre de 2026» en minúsculas, así que la prueba está bien y el defecto es del código.
- **Segunda ejecución:** repetí el comando y falló igual, así que no es una plantilla a medio editar. En el HTML ya aparece `class="total-mes"`, o sea que el otro agente ya cambió esa clase.
- **No toqué la plantilla** (no puedo). No debilité la aserción.

Pruebas nuevas o modificadas y por qué no son vacuas:
- **Hallazgo 3**
  - `test_con_sesion_el_titulo_de_la_pestana_es_resumen`: exige `<title>Resumen · Hormiguero</title>`. Falla si se cambia el bloque `titulo` de `inicio.html` o el sufijo de `base.html`.
  - `test_sin_sesion_el_titulo_de_la_pestana_es_inicio`: exige `<title>Inicio · Hormiguero</title>`. Falla si la rama `else` del título cambia o se vuelve igual en ambos casos.
- **Hallazgo 4**: `test_sin_sesion_muestra_h1_hormiguero_y_descripcion` exige `<h1>Hormiguero</h1>` y «Gestor de gastos personales con metas de ahorro.». Falla si se altera el bloque sin sesión de la plantilla.
- **Hallazgo 5**: `test_categoria_desconocida_muestra_el_codigo` añade `assertRegex` con `<td>\s*antigua\s*</td>`. Falla si la plantilla no pinta `categoria_nombre` en la celda, por ejemplo si pintara `categoria` o dejara la celda vacía.
- **Hallazgo 6**
  - `test_la_pagina_muestra_categorias_en_orden_y_sin_salud`: ahora exige también «Hogar» y el orden Alimentación antes que Hogar. Falla si la plantilla reordena filas, por ejemplo con `|dictsort`.
  - `test_cada_monto_va_en_la_fila_de_su_categoria` (nueva): usa `subTest` y una regex por fila `<td>Cat</td><td ...>$monto</td>` para Transporte $15.000, Alimentación $10.000 y Hogar $2.000. Falla si montos y nombres quedan desemparejados, o si se cambia el formato `floatformat:"0g"` o las etiquetas de celda.
- **Hallazgo 7**: `test_total_del_mes_en_contexto_y_en_la_pagina` ya no usa `.lower()` y exige «noviembre de 2026» exacto. Hoy está en rojo porque la plantilla pone «Noviembre».

NECESITA DE OTRO AGENTE: implementador-frontend. En `templates/inicio.html`, línea 15, el `<h2>` debe dar «noviembre» en minúsculas: `{{ hoy|date:"F \d\e Y"|lower }}`. Así queda «Total de noviembre de 2026», como pide la spec. La prueba no necesita cambios.

PREGUNTAS PARA EL DESARROLLADOR: ninguna.
````

Nota del coordinador: el hallazgo 7 destapó un defecto real. El revisor y el probador de la vuelta inicial suponían que `date:"F"` en es-co da «noviembre»; da «Noviembre». La prueba se dejó en rojo y se hizo commit así (`test: reforzar pruebas del resumen tras la revisión`), y se encargó la corrección al implementador-frontend (`|lower`), que cuenta como parte de la vuelta 1. Aprendizaje: una aserción con `.lower()` puede ocultar justo el detalle que pide la spec.

### Corrección del mes en minúsculas (implementador-frontend, hallazgo 7)

Informe del implementador-frontend, copiado tal cual:

````
ESTADO: verde

ARCHIVOS: /home/jdrickxd/Documentos/Proyecto_Integrador/templates/inicio.html (solo línea 15). Sin commits.

CAMBIO (línea 15):
Antes:   <h2 id="titulo-total">Total de {{ hoy|date:"F \d\e Y" }}</h2>
Después: <h2 id="titulo-total">Total de {{ hoy|date:"F \d\e Y"|lower }}</h2>

EVIDENCIA:
1. python manage.py test gastos.tests.test_vista_resumen
Creating test database for alias 'default'...
......................
----------------------------------------------------------------------
Ran 22 tests in 10.862s

OK
Destroying test database for alias 'default'...
Found 22 test(s).
System check identified no issues (0 silenced).

2. python manage.py test
Creating test database for alias 'default'...
(265 puntos, todos pasan)
----------------------------------------------------------------------
Ran 265 tests in 61.210s

OK
Destroying test database for alias 'default'...
Found 265 test(s).
System check identified no issues (0 silenced).

NECESITA DE OTRO AGENTE: nada
PREGUNTAS PARA EL DESARROLLADOR: ninguna
````

Nota del coordinador: comprobé `git diff templates/inicio.html`; solo cambia esa línea.

### Estado final de los hallazgos de la vuelta 1
| # | Resultado |
|---|---|
| 1 | Corregido (`fix: estilo del total del mes y del aviso…`). |
| 2 | Corregido por decisión del desarrollador (mismo commit). |
| 3 | Corregido: pruebas del título de la pestaña con y sin sesión. |
| 4 | Corregido: prueba del `<h1>` y la descripción sin sesión. |
| 5 | Corregido: «antigua» comprobado en la celda. |
| 6 | Corregido: orden completo y monto por fila. |
| 7 | Corregido: la prueba destapó «Noviembre» con mayúscula; se añadió `|lower` en la plantilla (`fix: mes en minúsculas…`). |
| Pregunta test_inicio | Descartado por decisión del desarrollador: se deja sin tocar. |
| Pregunta consulta | Descartado por decisión del desarrollador: se acepta el filtrado en Python. |

## Revisión (revisor, T6), vuelta 2

Informe del revisor, copiado tal cual:

````
ESTADO: sin hallazgos

Revisé la vuelta 2 de la spec 005 en `feat/resumen`, sin modificar archivos. No encontré hallazgos nuevos: los hallazgos 1 a 7 están bien resueltos, las pruebas nuevas no son vacuas, el contraste del aviso pasa AA y la página sin sesión no cambió.

HALLAZGOS: ninguno nuevo.

**Comprobación de los hallazgos 1 a 7**
1. `/home/jdrickxd/Documentos/Proyecto_Integrador/templates/inicio.html:16` usa `<p class="total-mes">`. La regla está en `/home/jdrickxd/Documentos/Proyecto_Integrador/static/estilos.css:43` y alinea el total a la izquierda. `.numero` sigue solo en `<th>` y `<td>` (líneas 28 y 35). Resuelto.
2. La regla `.aviso-hormiga` está en `estilos.css:31-39` y la clase se usa en `inicio.html:10`. Resuelto, según la decisión del desarrollador.
3. Las pruebas `test_con_sesion_el_titulo_de_la_pestana_es_resumen` (línea 93) y `test_sin_sesion_el_titulo_de_la_pestana_es_inicio` (línea 75) piden el `<title>` exacto en cada rama. Si las dos ramas del bloque `titulo` dieran el mismo texto, fallaría una de ellas. No son vacuas.
4. `test_sin_sesion_muestra_h1_hormiguero_y_descripcion` (línea 70) pide `<h1>Hormiguero</h1>` y la descripción literal. Ese texto solo existe en `inicio.html:46-47`, así que la prueba falla si se borra. No es vacua.
5. En la línea 171, `<td>\s*antigua\s*</td>` falla si la celda pinta otra cosa o queda vacía. No es vacua.
6. La línea 147 comprueba el orden completo de las tres categorías. `test_cada_monto_va_en_la_fila_de_su_categoria` (líneas 150-162) busca, en cada fila, la celda del nombre seguida de la de su monto, así que falla si se desemparejan. No es vacua.
7. La línea 104 ya no usa `.lower()`. Además, el probador vio esta prueba en rojo antes del `|lower` de `inicio.html:15` (porque la página decía «Noviembre»), lo que demuestra que no es vacua.

**Contraste WCAG AA de `.aviso-hormiga`** (luminancia relativa con linealización sRGB; razón = (L1 + 0,05) / (L2 + 0,05))
- Fondo `#fffbeb`: R 1,0000, G 0,9647, B 0,8308. L = 0,2126·1 + 0,7152·0,9647 + 0,0722·0,8308 = **0,9625**.
- Texto `#3b2300`: R 0,0437, G 0,0168, B 0. L = 0,0093 + 0,0120 + 0 = **0,0213**.
  - Razón: 1,0125 / 0,0713 = **14,2:1**. Pasa 4,5:1 (y también AAA, 7:1).
- Enlace `#7c2d12`: R 0,2016, G 0,0262, B 0,0060. L = 0,0429 + 0,0188 + 0,0004 = **0,0621**.
  - Razón: 1,0125 / 0,1121 = **9,0:1**. Pasa 4,5:1 (y también AAA).
- Foco del enlace: la regla global `:focus-visible { outline: 3px solid #D97706; outline-offset: 2px; }` (`estilos.css:5`) sigue en pie. `.aviso-hormiga a` no anula `outline`.
  - `#D97706` tiene L = 0,2796. Contra `#fffbeb` da 1,0125 / 0,3296 = **3,07:1**, que pasa el mínimo de 3:1 para indicadores que no son texto (WCAG 1.4.11), aunque con poco margen.
  - El contorno queda dentro del aviso, que tiene 0,75rem y 1rem de relleno, así que se dibuja sobre `#fffbeb`.
  - El enlace conserva el subrayado, así que no depende solo del color para distinguirse.
- Bordes `#f5c26b` y `#B45309`: son decorativos. El aviso ya se entiende por su texto, así que no se les exige contraste.

**Pautas de diseño web** (`inicio.html` y `estilos.css`): no hay hallazgos. Hay un solo `<h1>` y los encabezados van en orden. El total usa `tabular-nums`. Los `<h2>` tienen `text-wrap: balance`. No hay `transition: all` ni contornos quitados. Los textos están en español.

**Alcance y regresiones**
- `git diff 73e7ec8..HEAD` solo toca `inicio.html`, `estilos.css` y `test_vista_resumen.py`, como se encargó. No hay cambios en `views.py`, en las reglas, en `base.html`, en `requirements.txt` ni en las migraciones.
- La rama sin sesión de `inicio.html` (líneas 45-49) no cambió. Las 4 pruebas de CA9 pasan.
- El commit `test:` (cd7bd31) va antes del `fix:` de la plantilla (92d4c51).

DIFERENCIAS CON LA SPEC: ninguna.
- Los archivos cambiados respecto de `main` son los del plan, y el plan permitía tocar `estilos.css`.
- `specs/005-resumen/spec.md` (las decisiones tras la vuelta 1) y `specs/005-resumen/evidencia.md` todavía no tienen commit. Hay que incluirlos antes del pull request.

EVIDENCIA (cada comando en su propia llamada):
1. `python manage.py test`:
Creating test database for alias 'default'...
.........................................................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 265 tests in 60.946s

OK
Destroying test database for alias 'default'...
Found 265 test(s).
System check identified no issues (0 silenced).

2. `coverage run manage.py test`:
Ran 265 tests in 60.358s

OK
Found 265 test(s).
System check identified no issues (0 silenced).

3. `coverage report`:
Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
gastos/__init__.py              0      0   100%
gastos/admin.py                 1      0   100%
gastos/apps.py                  3      0   100%
gastos/forms.py                80      0   100%
gastos/models.py               33      1    97%   35
gastos/reglas/__init__.py       0      0   100%
gastos/reglas/gastos.py         7      0   100%
gastos/reglas/hormiga.py       19      0   100%
gastos/reglas/metas.py         30      0   100%
gastos/reglas/resumen.py       13      0   100%
gastos/reglas/usuarios.py       2      0   100%
gastos/urls.py                  5      0   100%
gastos/views.py                92      0   100%
---------------------------------------------------------
TOTAL                         285      1    99%

La cobertura de `gastos/` es del 99 %, por encima del mínimo del 80 %.

4. `python manage.py makemigrations --check --dry-run`: `No changes detected`.
5. `git diff main...HEAD --stat`: 9 archivos, 588 inserciones y 5 eliminaciones. Son los del plan.

PREGUNTAS PARA EL DESARROLLADOR:
- El contorno de foco `#D97706` sobre el fondo del aviso queda en 3,07:1. Pasa el mínimo de 3:1, pero con muy poco margen. ¿Se acepta así, o se prefiere un tono más oscuro (por ejemplo `#B45309`)? Ese contorno es global y lo usa todo el sitio, así que el cambio iría fuera de esta spec.
````

Nota del coordinador: la pregunta del contorno de foco no bloquea esta spec. Cumple WCAG 1.4.11 y el cambio sería global, fuera del alcance de la 005. Queda como pendiente para que el desarrollador decida si abre una spec aparte. No se cambió nada.

## Notas para ajustar el sistema
- **Hook:** rechazó `coverage run manage.py test` al implementador-frontend (solo admite `python manage.py test` y `curl`). La cobertura la midió el revisor. En próximas specs, la cobertura se pide al revisor o al probador desde el principio.
- **Hook:** el implementador-frontend tampoco puede ejecutar `git diff`; el coordinador comprobó cada diff del frontend con git antes de su commit.
- **Orden:** en la vuelta 1, el probador y el implementador-frontend trabajaron en paralelo sobre archivos distintos. La prueba reforzada del hallazgo 7 destapó un defecto de plantilla, así que hubo un encargo extra al frontend (`|lower`) dentro de la misma vuelta. Commits en orden: `fix:` estilos → `test:` refuerzo (con una prueba en rojo) → `fix:` mes.
- **Supuesto erróneo:** la spec, el plan y la primera prueba suponían que `date:"F"` en es-co da «noviembre». Da «Noviembre». El `.lower()` de la prueba lo ocultaba.

## Pruebas finales
- `python manage.py test`: `Ran 265 tests ... OK` (vuelta 2 del revisor).
- Cobertura de `gastos/`: 99 %.
- `makemigrations --check --dry-run`: `No changes detected`.

## Pull request
https://github.com/JuanDR403/Hormiguero/pull/14 (fusionado).
