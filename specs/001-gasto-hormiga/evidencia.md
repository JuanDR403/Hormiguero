# Evidencia 001 · Regla de gasto hormiga

## Incidencias del arnés

### Coordinador, lectura del código (paso 1)
- `ls ... && cat ...` rechazado: `PreToolUse:Bash hook error: [python "$CLAUDE_PROJECT_DIR/.claude/hooks/limitar_agente.py" coordinador]: No se permite encadenar ni redirigir comandos.`
- `git ls-files` rechazado: `coordinador solo puede ejecutar: git status; git diff; git log; git switch; git add; git commit.`
- Se leyeron los archivos con Read.

### Coordinador, rama y commit (paso 3)
- No se pudo actualizar `main` antes de crear la rama, porque `git fetch` y `git pull` no están permitidos. La rama `feat/gasto-hormiga` sale del `main` local en `c283859`.
- El commit con la línea `Co-Authored-By: ... <noreply@anthropic.com>` fue rechazado dos veces:
  - con salto de línea en el mensaje: `Un solo comando por llamada.`
  - con `-m` separados: `No se permite encadenar ni redirigir comandos.`, porque `<` y `>` están en `PROHIBIDO_EN_BASH`.
- El commit `319a97a docs: spec 001 gasto-hormiga` se hizo sin la línea de atribución.

### Probador, T1 (paso 4): bloqueado
Informe literal del probador:

```
ESTADO: bloqueado
ARCHIVOS: ninguno. No se creó `/home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_regla_hormiga.py`.
EVIDENCIA: Leí la spec, el plan, las tareas, `.claude/rules/pruebas.md` y `gastos/models.py`. Después intenté escribir el archivo con Write y el hook rechazó la operación:
`PreToolUse:Write hook error: [python "$CLAUDE_PROJECT_DIR/.claude/hooks/limitar_agente.py" coordinador]: coordinador solo puede escribir en: specs/. Rechazado: gastos/tests/test_regla_hormiga.py.`
También rechazó `python manage.py test`: `coordinador solo puede ejecutar: git status; git diff; git log; git switch; git add; git commit.`
No hay salida de `python manage.py test` ni pruebas ejecutadas, así que el rojo no está confirmado.
NECESITA DE OTRO AGENTE: Nada de otro agente. El problema es de la sesión. El hook `.claude/hooks/limitar_agente.py` se está ejecutando con el perfil `coordinador` (el argumento está en el comando del hook) cuando yo soy `probador`. Ese perfil solo permite escribir en `specs/` y ejecutar comandos git. Hay que lanzar el probador con el perfil correcto (escritura en `gastos/tests/` y `python manage.py test`) o corregir la configuración del hook. No intenté saltarme el hook.
PREGUNTAS PARA EL DESARROLLADOR: ¿Corriges la configuración del hook, o relanzas la tarea T1 con el perfil `probador`? Con eso aplicado escribo el archivo y confirmo el rojo.
```

El probador propuso tres pruebas extra: `test_espacios_internos_se_colapsan`, `test_un_gasto_sobre_el_umbral_no_se_suma_al_grupo` y `test_empate_se_resuelve_por_categoria_y_descripcion`.

**Diagnóstico del coordinador:** la sesión se abrió con `claude --agent coordinador`. El hook `PreToolUse` del encabezado de `coordinador.md` queda activo para toda la sesión, también para los subagentes. Por eso cada herramienta del probador pasa primero por `limitar_agente.py coordinador`, que la rechaza, aunque también corra su propio hook `probador`. Pasará lo mismo con `implementador-backend`, `implementador-frontend` y `revisor`.

Corregirlo le toca al desarrollador: está fuera de `specs/` y el coordinador no puede ni debe tocar el hook.

**Estado:** T1 sin hacer y sin rojo. No se avanza a T2.

### Resolución de la incidencia
- El desarrollador corrigió el hook en el commit `1e0bb86 fix: el hook de permisos solo juzga al agente al que pertenece` (rama `feat/gasto-hormiga`). Según el mensaje del commit: el hook usa `agent_type` y solo juzga las llamadas de su propio agente; el coordinador puede usar `git fetch` y `git pull`, y el mensaje de un commit entre comillas admite saltos de línea y los símbolos `<` y `>`.
- Archivos tocados por la corrección: `.claude/agents/{coordinador,implementador-backend,implementador-frontend,probador,revisor}.md`, `.claude/hooks/limitar_agente.py`, `README.md`.
- Al comprobar la corrección, el hook rechazó `git show --stat 1e0bb86` al coordinador (`coordinador solo puede ejecutar: git status; git diff; git log; git fetch; git pull; git switch; git add; git commit.`). Es lo esperado: se usó `git log -1 --stat` en su lugar.
- **Incidencia resuelta.** T1 se vuelve a encargar al probador (2026-11-14), incluidas sus tres pruebas extra, que se añadieron a la tabla de `plan.md` por derivar de la spec (Definiciones y Resultado) sin cambiar su alcance.

## T1 · probador · rojo (segundo intento, 2026-11-14)
Informe literal del probador:

```
ESTADO: rojo confirmado

ARCHIVOS: creado /home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_regla_hormiga.py. No toqué nada más.

PRUEBAS ESCRITAS (22). La función se importa dentro de cada prueba con el helper `detectar()`.
- CA1: test_tres_compras_pequenas_iguales_forman_grupo
- CA2: test_dos_compras_no_alcanzan_n
- CA3: test_cuatro_compras_cuentan_todas
- CA4: test_monto_igual_al_umbral_cuenta, test_monto_un_peso_sobre_el_umbral_no_cuenta, test_monto_un_peso_bajo_el_umbral_cuenta
- CA5: test_gasto_de_hace_treinta_dias_cuenta, test_gasto_de_hace_treinta_y_un_dias_no_cuenta, test_gasto_de_hoy_cuenta
- CA6: test_gasto_futuro_no_cuenta
- CA7: test_descripcion_se_normaliza
- CA8: test_misma_descripcion_en_otra_categoria_es_otro_grupo
- CA9: test_gastos_sin_descripcion_forman_grupo
- CA10: test_grupos_ordenados_por_cantidad_y_total
- CA11: test_sin_gastos_devuelve_lista_vacia
- CA12: test_n_es_parametro, test_umbral_es_parametro
- CA13: test_constantes_en_settings (clase ConstantesHormigaTests, SimpleTestCase, lee django.conf.settings)
- CA15: test_acepta_instancias_de_gasto_con_decimal (TestCase, ana@ejemplo.com con create_user, 3 Gasto guardados con Decimal("4000"), comprueba total == 12000 y `type(total) is int`)
- Extra: test_espacios_internos_se_colapsan
- Extra: test_un_gasto_sobre_el_umbral_no_se_suma_al_grupo (3 de 4.000 más uno de 10.001: cantidad 3, total 12.000)
- Extra: test_empate_se_resuelve_por_categoria_y_descripcion (alimentacion/arepa, alimentacion/tinto, transporte/bus)
- CA14 no se toca: lo cubre la prueba de arquitectura existente.

EVIDENCIA:
Comandos: `python manage.py test gastos.tests.test_regla_hormiga` y `python manage.py test`. La herramienta truncó la salida larga (unos 7.000 caracteres en medio de cada una), así que no puedo entregarla literal y completa. Lo que sigue es lo visible, sin resumir lo que se vio.

Comando 1, cabecera y cierre:
    Creating test database for alias 'default'...
    EEEEEEEEEEEEEEEEEEEEEE
    ...
    Ran 22 tests in 0.441s
    FAILED (errors=22)
    Destroying test database for alias 'default'...
    Found 22 test(s).
    System check identified no issues (0 silenced).

Comando 2, cabecera y cierre:
    Creating test database for alias 'default'...
    ................................E........................EEEEEEEEEEEEEEEEEEEEE...........
    ...
    Ran 89 tests in 25.483s
    FAILED (errors=22)

Las 67 pruebas restantes pasan, incluida la de arquitectura. Los 22 errores son exactamente mis 22 pruebas.

Motivo de cada fallo:
- 21 pruebas fallan con `ModuleNotFoundError: No module named 'gastos.reglas.hormiga'`. Son las 20 de `DetectarGastoHormigaTests` más test_acepta_instancias_de_gasto_con_decimal. En esta última el Gasto y el usuario se crean bien; falla en la línea `detectar(gastos)`.
- test_constantes_en_settings falla con `AttributeError: 'Settings' object has no attribute 'GASTO_HORMIGA_UMBRAL'`, o sea, por la ausencia de las constantes, como se pedía.
- Ningún fallo es un error de sintaxis o de importación de la propia prueba.

Los tracebacks de varias pruebas quedaron dentro del tramo truncado (por ejemplo test_espacios_internos_se_colapsan y las de CA4/CA5), pero el recuento (22 errores, 22 pruebas) y los tracebacks visibles muestran la misma causa. Si hace falta la salida íntegra, hay que ejecutar los comandos fuera de esta herramienta.

NECESITA DE OTRO AGENTE:
- implementador-backend (T2): crear gastos/reglas/hormiga.py con detectar_gasto_hormiga(gastos, umbral, n, hoy), y agregar GASTO_HORMIGA_UMBRAL = 10000 y GASTO_HORMIGA_N = 3 en config/settings.py.
- Un intento de `ls` por Bash fue rechazado por el hook: "probador solo puede ejecutar: python manage.py test." No bloquea nada.

PREGUNTAS PARA EL DESARROLLADOR: ninguna.
```

(Los bloques de salida internos se sangraron con cuatro espacios para no romper el bloque de código; el contenido es el del informe.)

**Valoración del coordinador:** rojo aceptado. Son 22 pruebas con 22 errores, y las 67 pruebas que ya había siguen en verde. Los motivos visibles son la falta del módulo `gastos.reglas.hormiga` y de las constantes, es decir, lo que pide T2.

**Incidencias del arnés en T1:**
- La herramienta de Bash del subagente trunca la salida larga de `python manage.py test` (unos 7.000 caracteres en medio). No se pudo copiar la salida íntegra del rojo. Para ajustar el sistema: pedir a los subagentes `python manage.py test ... 2>&1 | tail`, que hoy prohíbe el hook, o permitirles escribir la salida en un archivo de evidencia.
- El hook rechazó `ls` al probador: `probador solo puede ejecutar: python manage.py test.` No bloqueó nada.

## T2 · implementador-backend · verde (2026-11-14)
Informe literal del implementador-backend:

```
ESTADO: verde

ARCHIVOS:
- /home/jdrickxd/Documentos/Proyecto_Integrador/gastos/reglas/hormiga.py (nuevo): detectar_gasto_hormiga(gastos, umbral, n, hoy). Solo importa collections y datetime.
- /home/jdrickxd/Documentos/Proyecto_Integrador/config/settings.py: GASTO_HORMIGA_UMBRAL = 10000 y GASTO_HORMIGA_N = 3, con un comentario breve, después de LOGOUT_REDIRECT_URL.

EVIDENCIA:
- `python manage.py test gastos.tests.test_regla_hormiga`
  Creating test database for alias 'default'...
  ......................
  Ran 22 tests in 0.406s
  OK
  Destroying test database for alias 'default'...
  Found 22 test(s).
  System check identified no issues (0 silenced).
- `python manage.py test`
  Creating test database for alias 'default'...
  .........................................................................................
  Ran 89 tests in 24.845s
  OK
  Destroying test database for alias 'default'...
  Found 89 test(s).
  System check identified no issues (0 silenced).
- `python manage.py check`: System check identified no issues (0 silenced).
- `python manage.py makemigrations --check --dry-run`: No changes detected

COBERTURA: el hook rechazó `coverage run manage.py test`. No pude correr `coverage report`. Mensaje literal:
"PreToolUse:Bash hook error: [python "$CLAUDE_PROJECT_DIR/.claude/hooks/limitar_agente.py" implementador-backend]: implementador-backend solo puede ejecutar: python manage.py test; python manage.py check; python manage.py makemigrations."

OTROS RECHAZOS DEL HOOK: un `grep` sobre settings.py, con el mismo mensaje literal. Leí el archivo con Read.

NECESITA DE OTRO AGENTE: alguien con permiso para ejecutar `coverage run manage.py test` y `coverage report` (coordinador o revisor), para confirmar gastos/ al 80 % o más. No modifiqué pruebas, modelos, vistas, URLs, formularios, migraciones ni plantillas, y no hice commits.

PREGUNTAS PARA EL DESARROLLADOR: ninguna
```

Commit: `241d312 feat: regla detectar_gasto_hormiga y constantes de umbral y N (spec 001)`. La spec no tiene pantalla, así que no se encarga a `implementador-frontend`.

**Incidencias del arnés en T2:**
- Ningún agente tiene permiso para ejecutar `coverage`: no está en la lista del implementador-backend, ni en la del coordinador (solo git). T2 pide «confirmar verde y cobertura», pero la cobertura queda sin confirmar en local. El coordinador no la ejecuta ni pide a otro agente que se salte el hook. Se pregunta al revisor si su perfil lo permite y, si no, la confirman el desarrollador o el CI (`.github/workflows/ci.yml`) en el pull request.
- El hook rechazó un `grep` al implementador-backend. No bloqueó nada.

## T3 · revisor · primera vuelta (2026-11-14)
Informe literal del revisor:

```
ESTADO: con hallazgos

La regla y sus pruebas cumplen la spec. No encontré ningún error en `gastos/reglas/hormiga.py`. Los hallazgos de gravedad bloqueante y menor están en los archivos del arnés (`.claude/`, README) que entraron en la rama con el commit 1e0bb86, que el plan no incluye. Ninguno de los cuatro roles puede corregirlos: le tocan al desarrollador.

HALLAZGOS:

1. /home/jdrickxd/Documentos/Proyecto_Integrador/.claude/hooks/limitar_agente.py:62 y :96 · bloqueante (severidad alta) · Cualquier agente puede saltarse el hook con una comilla escapada. La regex `'[^']*'|"[^"]*"` no tiene en cuenta `\'`. Ejemplo: `git status \' ; rm -rf gastos ; \'`. El hook toma `' ; rm -rf gastos ; \'` como texto entre comillas y lo cambia por `''`, así que no ve los `;`. El comando empieza por `git status` y se acepta. Bash, en cambio, lee `\'` como una comilla literal y ejecuta `rm`. Sirve con cualquier prefijo permitido y para todos los roles. No lo ejecuté: es un análisis del código. Afecta la frontera de permisos del arnés y la norma de AGENTS.md "un hook rechaza lo demás". Lo corrige el desarrollador, porque ningún rol escribe en `.claude/`. Una opción es rechazar `\` fuera de las comillas, o separar el comando con `shlex` en lugar de usar una regex.

2. /home/jdrickxd/Documentos/Proyecto_Integrador/.claude/hooks/limitar_agente.py:121-123 · menor (severidad media) · Si `agent_type` llega y no coincide con el rol, el hook termina sin juzgar nada. Un subagente sin hook propio que se lance desde la sesión `claude --agent coordinador` (por ejemplo `general-purpose` o `Explore`, si el coordinador puede invocarlos) trabajaría sin ninguna restricción. Antes de este cambio el hook del coordinador lo limitaba. Afecta el aislamiento de permisos del arnés. Lo corrige el desarrollador. Una opción es saltar el juicio solo cuando `agent_type` sea uno de los roles de `ROLES` que tienen hook propio.

3. Commit 1e0bb86 (`.claude/agents/*.md`, `.claude/hooks/limitar_agente.py`, `README.md`) · menor (severidad media) · Archivos fuera del plan. La sección "Archivos" de `specs/001-gasto-hormiga/plan.md` solo nombra `hormiga.py`, `test_regla_hormiga.py` y `settings.py`. Contradice la skill de revisión ("Los archivos cambiados son los del plan") y la convención de ramas `fix/<tema>` y `chore/<tema>`. Decide el desarrollador: mover el commit a una rama `fix/hook-agentes` con su propio PR, o que el coordinador lo agregue al plan como cambio justificado.

4. /home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_regla_hormiga.py:109-113 · sugerencia (severidad baja) · Ninguna prueba usa `descripcion=None`. La regla lo admite (`hormiga.py:10`, `(descripcion or "")`), pero si alguien quita el `or ""` ninguna prueba falla. Con el modelo actual no pasa (`blank=True`, no `null=True`), y la spec solo habla de "vacío". El criterio afectado es CA9 (robustez del tipo de entrada). Lo corrige el probador.

5. /home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_regla_hormiga.py:89-98 · sugerencia (severidad baja) · El colapso de espacios internos solo se prueba con espacios normales. La implementación con `split()` también colapsa tabuladores, saltos de línea y espacios no separables, pero ninguna prueba lo fija. Un cambio a `split(" ")` pasaría las pruebas y rompería la normalización con `"tinto\tgrande"`. Afecta la definición de "Grupo" en la spec. Lo corrige el probador.

6. /home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_regla_hormiga.py:100-107 · sugerencia (severidad baja) · La prueba de CA8 solo comprueba 2 + 2 → `[]`. La primera parte de CA8, "forma dos grupos distintos", no se comprueba en positivo: falta un caso 3 + 3 que espere dos grupos con su `categoria`. La prueba actual sí detecta una implementación que agrupe solo por descripción (4 ≥ 3), así que no pasa por casualidad, pero no cubre CA8 completo. Lo corrige el probador.

Lo que revisé sin encontrar problemas:
- **Django:** `hormiga.py` solo importa `collections` y `datetime`, y CA14 lo cubre `test_arquitectura.py`.
- **Ventana:** `desde <= fecha <= hoy` (línea 23). Incluye `hoy − 30` y `hoy`, y deja fuera las fechas futuras. Las pruebas de hoy−30, hoy−31, hoy y hoy+1 fallarían con un límite mal puesto.
- **Umbral:** se descarta con `monto > umbral`, así que es inclusivo. Se prueban 9.999, 10.000 y 10.001.
- **Normalización:** `" ".join(split()).lower()`.
- **Total:** se acumula como `int(monto)` empezando en 0, nunca `float`. CA15 comprueba `type(...) is int` con `Gasto` guardado y `Decimal`.
- **Orden:** clave `(-cantidad, -total, categoria, descripcion)`. En las dos pruebas de orden, los datos se cargan en un orden distinto al esperado, así que no pasan por el orden de entrada.
- **Parámetros y datos de prueba:** `hoy` fijo y sin reloj. `n` y `umbral` llegan como parámetros. Las constantes están en `settings.py`. El usuario de ejemplo `ana@ejemplo.com` se crea con `create_user`.
- **Historial:** el commit `test:` (caaf3ed) va antes que el `feat:` (241d312).
- **Base de datos y alcance:** no hay migraciones, `db.sqlite3`, `.env`, cambios en `requirements.txt` ni plantillas. Por eso no apliqué `web-design-guidelines`.
- **Nombres:** en español y `snake_case`.

DIFERENCIAS CON LA SPEC:
- Archivos fuera del plan: `.claude/agents/coordinador.md`, `implementador-backend.md`, `implementador-frontend.md`, `probador.md`, `revisor.md`, `.claude/hooks/limitar_agente.py` y `README.md` (hallazgo 3).
- CA8 está cubierto solo en parte (hallazgo 6). Los demás criterios, de CA1 a CA15, tienen prueba.
- Hay cambios sin commit en `specs/001-gasto-hormiga/evidencia.md` y `tareas.md` según `git status`. Hay que confirmarlos antes del PR.

EVIDENCIA (salida literal):

`python manage.py test`
    Creating test database for alias 'default'...
    .........................................................................................
    ----------------------------------------------------------------------
    Ran 89 tests in 24.534s

    OK
    Destroying test database for alias 'default'...
    Found 89 test(s).
    System check identified no issues (0 silenced).

`python manage.py check`
    System check identified no issues (0 silenced).

`python manage.py makemigrations --check --dry-run`
    No changes detected

`coverage run --source=gastos manage.py test`
    Ran 89 tests in 24.975s

    OK

`coverage report`
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
    gastos/views.py                40      0   100%
    ---------------------------------------------------------
    TOTAL                         158      1    99%

Cobertura de `gastos/`: 99 %, por encima del mínimo de 80 %. `hormiga.py` está al 100 %.

Rechazos del hook: ninguno. Todos los comandos se aceptaron.

NECESITA DE OTRO AGENTE:
- Desarrollador: hallazgos 1, 2 y 3.
- Probador: hallazgos 4, 5 y 6 (sugerencias, no bloquean).
- Implementador-backend: nada.

PREGUNTAS PARA EL DESARROLLADOR:
1. Con `n ≤ 0`, la línea `hormiga.py:38` (`if cantidad >= n`) devuelve todos los grupos que tengan al menos una compra. ¿Está bien así, o la regla debería rechazar `n < 1` con un error? La spec no lo dice.
2. `hormiga.py:29` hace `int(gasto.monto)`, que recorta en silencio un monto con centavos, por ejemplo `Decimal("4000.7")` → 4000. El modelo lo impide (`decimal_places=0`) y la spec define la entrada como "sin centavos". ¿Basta con eso o la regla debería validarlo?
3. ¿Puede el coordinador lanzar subagentes que no estén en `.claude/agents/`, como `general-purpose` o `Explore`? Si puede, el hallazgo 2 es explotable en la práctica.
4. ¿Los cambios del arnés (commit 1e0bb86) se quedan en esta rama o se separan en su propio PR?
```

(Los bloques de salida internos se sangraron con cuatro espacios para no romper el bloque de código.)

**Cobertura confirmada por el revisor:** `gastos/` al 99 %, `hormiga.py` al 100 %. Queda cerrada la incidencia de cobertura de T2: el perfil del revisor sí permite `coverage`.

**Respuesta del coordinador a la pregunta 3 del revisor:** en esta sesión, el coordinador solo tiene disponibles `implementador-backend`, `implementador-frontend`, `probador` y `revisor`, y el general-purpose no está disponible. Aun así el hallazgo 2 sigue siendo válido como defensa en profundidad.

**El desarrollador también confirmó la cobertura** (mensaje del 2026-11-14): «99 % en gastos/ y 100 % en gastos/reglas/hormiga.py, con 89 pruebas en verde. El revisor tiene permitidos coverage run y coverage report.»

### Decisiones del desarrollador (AskUserQuestion, 2026-11-14)
- Hook (hallazgos 1 y 2): «Lo arreglo antes del PR».
- Commit 1e0bb86 fuera del plan (hallazgo 3): «Dejarlo y justificarlo».
- Pruebas sugeridas (hallazgos 4, 5 y 6): «Sí, las tres».
- Entradas fuera de lo normal, `n ≤ 0` y centavos (preguntas 1 y 2 del revisor): «Dejarlo como está».

### Trato de cada hallazgo
| # | Gravedad | Trato | Detalle |
|---|---|---|---|
| 1 | bloqueante | **Corregido por el desarrollador** | Commit `2f2fd3c fix: el hook rechaza comillas escapadas y agentes sin perfil`. Según el desarrollador: el hook rechaza la barra invertida y las comillas sin cerrar, hay 17 pruebas nuevas en `gastos/tests/test_hook_permisos.py` y la suite completa pasa con 106 pruebas. Archivos: `.claude/hooks/limitar_agente.py`, `README.md`, `gastos/tests/test_hook_permisos.py`. |
| 2 | menor | **Corregido por el desarrollador** | Mismo commit `2f2fd3c`: un agente sin perfil no puede escribir ni ejecutar. |
| 3 | menor | **Aceptado y justificado** | El commit 1e0bb86 se queda en la rama, y también 2f2fd3c. Los dos aparecen en `plan.md` («Cambios del arnés en esta rama») y se mencionan en la descripción del PR. |
| 4 | sugerencia | Encargado al probador (vuelta 1) | `test_descripcion_none_se_trata_como_vacia` |
| 5 | sugerencia | Encargado al probador (vuelta 1) | `test_espacios_en_blanco_de_cualquier_tipo_se_colapsan` |
| 6 | sugerencia | Encargado al probador (vuelta 1) | `test_misma_descripcion_en_dos_categorias_forma_dos_grupos` |
| P1, P2 | pregunta | **Descartado: se deja como está** | Decisión del desarrollador. Se anota en `spec.md` (Decisiones tomadas) que la entrada se supone válida. |
| P3 | pregunta | Respondida por el coordinador | Ver arriba. |
| P4 | pregunta | Respondida por el desarrollador | Es la misma decisión del hallazgo 3. |

### Vuelta de corrección 1 · probador (hallazgos 4, 5 y 6)
Informe literal del probador:

```
ESTADO: verde desde el inicio (pruebas de regresión, sin fase roja). No toqué la regla.

ARCHIVOS: /home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_regla_hormiga.py (solo se añadieron pruebas en DetectarGastoHormigaTests, antes de test_sin_gastos_devuelve_lista_vacia; las existentes no se modificaron).

PRUEBAS AÑADIDAS (4; las dos primeras cubren el punto 1 pedido)
1. test_descripcion_none_se_trata_como_vacia (CA9): tres gastos con descripcion=None dan un grupo {alimentacion, descripcion "", cantidad 3, total 12000}.
2. test_descripcion_none_y_vacia_forman_un_solo_grupo (CA9, mezcla): None, "" y None dan un solo grupo con descripcion "" y cantidad 3.
3. test_espacios_en_blanco_de_cualquier_tipo_se_colapsan (Definiciones/Grupo): "tinto\tgrande", "tinto\ngrande" y "tinto  grande" dan un solo grupo "tinto grande" con cantidad 3.
4. test_misma_descripcion_en_dos_categorias_forma_dos_grupos (CA8 en positivo): tres «Tinto» en alimentacion y tres en transporte dan exactamente dos grupos, cada uno con su categoria, descripcion "tinto", cantidad 3 y total 12000, en orden alimentacion y luego transporte (desempate por categoria).

EVIDENCIA
`python manage.py test gastos.tests.test_regla_hormiga`:
Creating test database for alias 'default'...
..........................
Ran 26 tests in 0.391s
OK
Destroying test database for alias 'default'...
Found 26 test(s).
System check identified no issues (0 silenced).

`python manage.py test`:
Creating test database for alias 'default'...
(110 puntos, todos verdes)
Ran 110 tests in 24.421s
OK
Destroying test database for alias 'default'...
Found 110 test(s).
System check identified no issues (0 silenced).

Rechazos del hook: ninguno.

NECESITA DE OTRO AGENTE: nada.

PREGUNTAS PARA EL DESARROLLADOR: ninguna. Una nota: añadí la mezcla None y "" como prueba separada (la 2) en vez de meterla en la 1, para que cada nombre diga una sola cosa. Por eso son 4 pruebas nuevas (22 a 26), no 3.
```

Commit: `d68d23a test: pruebas de regresión de la revisión de la regla hormiga (spec 001)`. Los hallazgos 4, 5 y 6 quedan **corregidos**. El probador añadió una cuarta prueba que no se le pidió (la mezcla de `None` y `""`), que estaba incluida en el punto 1 del encargo. Se acepta y se añade a `plan.md`.

Recuento: 106 pruebas tras `2f2fd3c` (según el desarrollador) + 4 = 110, todas en verde.

## Cierre
- Tareas T1, T2 y T3 marcadas en `tareas.md`.
- No se pidió una segunda vuelta al revisor. El desarrollador indicó seguir con las pruebas extra y el cierre. Por eso el revisor no ha revisado los commits `2f2fd3c` (hook) y `d68d23a` (pruebas de regresión). Queda para la revisión del pull request por otro integrante.
- Cobertura: última medición, la de la T3 (99 % en `gastos/`, 100 % en `hormiga.py`, con 89 pruebas). No se volvió a medir con 110 pruebas, porque solo se añadieron pruebas. La medirá el CI en el pull request.

**Orden alterado:** el commit 2f2fd3c del desarrollador entró en la rama durante la revisión, después del `feat:` y antes de cerrar. Modifica `gastos/tests/`, que es terreno del probador. Lo hizo el desarrollador, no un subagente.
