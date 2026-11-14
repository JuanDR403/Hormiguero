# Evidencia 003 · Metas de ahorro (backend)

## Incidencias del proceso
- Al preparar la spec, el hook rechazó `git ls-files gastos specs config` del coordinador («coordinador solo puede ejecutar: git status; git diff; git log; git fetch; git pull; git switch; git add; git commit»). Los archivos se listaron con `git log --name-only`. Posible ajuste: permitir `git ls-files` al coordinador.
- Los tres archivos de la spec se escribieron en `main` sin commit; la rama `feat/metas-ahorro` se creó después de la aprobación y el commit `docs: spec 003 metas-ahorro` se hizo ya en la rama.

## T1 · probador · rojo
Archivos: `gastos/tests/test_regla_metas.py` (28 pruebas: 5 de meses restantes, 10 de cuota, 13 de validación) y `gastos/tests/test_modelo_meta.py` (5 pruebas). En total son 33. El informe del probador decía «30 en total» y «25 pruebas de reglas»: el coordinador leyó los archivos y contó 28 + 5, que coincide con la tabla del plan.

Nota del probador: «`test_falta_un_peso_da_cuota_uno` usa precio 100.001, ahorrado 100.000 y límite 2027-02-01 (3 meses), que es mi lectura de CA8 porque la spec no da cifras.»

`python manage.py test gastos.tests.test_regla_metas gastos.tests.test_modelo_meta`:
```
EE
======================================================================
ERROR: test_regla_metas (unittest.loader._FailedTest.test_regla_metas)
----------------------------------------------------------------------
ImportError: Failed to import test module: test_regla_metas
Traceback (most recent call last):
  File "/usr/lib/python3.14/unittest/loader.py", line 141, in loadTestsFromName
    module = __import__(module_name)
  File "/home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_regla_metas.py", line 6, in <module>
    from gastos.reglas.metas import (
    ...<3 lines>...
    )
ModuleNotFoundError: No module named 'gastos.reglas.metas'


======================================================================
ERROR: test_modelo_meta (unittest.loader._FailedTest.test_modelo_meta)
----------------------------------------------------------------------
ImportError: Failed to import test module: test_modelo_meta
Traceback (most recent call last):
  File "/usr/lib/python3.14/unittest/loader.py", line 141, in loadTestsFromName
    module = __import__(module_name)
  File "/home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_modelo_meta.py", line 8, in <module>
    from gastos.models import Meta
ImportError: cannot import name 'Meta' from 'gastos.models' (/home/jdrickxd/Documentos/Proyecto_Integrador/gastos/models.py)


----------------------------------------------------------------------
Ran 2 tests in 0.005s

FAILED (errors=2)
Found 2 test(s).
System check identified no issues (0 silenced).
```

`python manage.py test`:
```
Creating test database for alias 'default'...
EE.....................................................................................................................................
======================================================================
ERROR: gastos.tests.test_modelo_meta (unittest.loader._FailedTest.gastos.tests.test_modelo_meta)
----------------------------------------------------------------------
ImportError: Failed to import test module: gastos.tests.test_modelo_meta
Traceback (most recent call last):
  File "/usr/lib/python3.14/unittest/loader.py", line 433, in _find_test_path
    module = self._get_module_from_name(name)
  File "/usr/lib/python3.14/unittest/loader.py", line 374, in _get_module_from_name
    __import__(name)
    ~~~~~~~~~~^^^^^^
  File "/home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_modelo_meta.py", line 8, in <module>
    from gastos.models import Meta
ImportError: cannot import name 'Meta' from 'gastos.models' (/home/jdrickxd/Documentos/Proyecto_Integrador/gastos/models.py)


======================================================================
ERROR: gastos.tests.test_regla_metas (unittest.loader._FailedTest.gastos.tests.test_regla_metas)
----------------------------------------------------------------------
ImportError: Failed to import test module: gastos.tests.test_regla_metas
Traceback (most recent call last):
  File "/usr/lib/python3.14/unittest/loader.py", line 433, in _find_test_path
    module = self._get_module_from_name(name)
  File "/usr/lib/python3.14/unittest/loader.py", line 374, in _get_module_from_name
    __import__(name)
    ~~~~~~~~~~^^^^^^
  File "/home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_regla_metas.py", line 6, in <module>
    from gastos.reglas.metas import (
    ...<3 lines>...
    )
ModuleNotFoundError: No module named 'gastos.reglas.metas'


----------------------------------------------------------------------
Ran 135 tests in 46.166s

FAILED (errors=2)
Destroying test database for alias 'default'...
Found 135 test(s).
System check identified no issues (0 silenced).
```

Motivo de cada fallo (según el probador):
- `test_regla_metas`: `ModuleNotFoundError` porque no existe `gastos/reglas/metas.py`. Era lo esperado, y falla el módulo entero.
- `test_modelo_meta`: `ImportError` porque `Meta` no existe en `gastos.models`. Era lo esperado, y falla el módulo entero.
- Las 133 pruebas previas pasan. Como los módulos no llegan a importarse, todavía no se ha ejecutado ninguna aserción. Esto se aceptó como rojo por el motivo correcto: falta el código de producción.

Commit: `d88b6e6 test: pruebas de la regla de cuota y del modelo Meta (spec 003, rojo)`.

## T2 · implementador-backend · verde
Archivos:
- Nuevo `gastos/reglas/metas.py`, con `meses_restantes`, `calcular_cuota_mensual` y `validar_meta`. Usa solo aritmética entera y no importa Django.
- `gastos/models.py`: se añade el modelo `Meta` y `Gasto` queda igual.
- `gastos/migrations/0002_meta.py`: generada con `makemigrations gastos`.

`python manage.py test gastos.tests.test_regla_metas gastos.tests.test_modelo_meta`:
```
Creating test database for alias 'default'...
.................................
----------------------------------------------------------------------
Ran 33 tests in 0.873s

OK
Destroying test database for alias 'default'...
Found 33 test(s).
System check identified no issues (0 silenced).
```

`python manage.py makemigrations --check --dry-run`:
```
No changes detected
```

`python manage.py test`:
```
Creating test database for alias 'default'...
......................................................................................................................................................................
----------------------------------------------------------------------
Ran 166 tests in 44.442s

OK
Destroying test database for alias 'default'...
Found 166 test(s).
System check identified no issues (0 silenced).
```

`python manage.py check`:
```
System check identified no issues (0 silenced).
```

Cobertura, según el informe literal del implementador: «`coverage run manage.py test && coverage report`: no se pudo ejecutar. El hook de `implementador-backend` solo permite `python manage.py test`, `check` y `makemigrations`, y rechazó `coverage run manage.py test` con este mensaje: "implementador-backend solo puede ejecutar: python manage.py test; python manage.py check; python manage.py makemigrations."»

**Incidencia del arnés (repetida de la spec 001):** T2 pide «confirmar verde y cobertura», pero el perfil del implementador-backend no permite `coverage`. Como en la spec 001, se le encarga al revisor, cuyo perfil sí lo permite. Para ajustar el sistema: quitar la cobertura de T2 en las tareas o dar `coverage` al implementador-backend.

Recuento: 133 + 33 = 166, todas en verde. La spec no tiene pantalla, así que no se encarga al `implementador-frontend`.

Commit: `6d8bda8 feat: modelo Meta y reglas de cuota mensual y validación de metas (spec 003)`.

## T3 · revisor · primera vuelta
Informe literal del revisor:

```
ESTADO: con hallazgos. Ninguno es bloqueante. La rama cumple CA1–CA20 y todo está en verde: 166 pruebas, `check` sin problemas, sin migraciones pendientes y 99 % de cobertura en `gastos/`. Los hallazgos son huecos menores en las pruebas que dejan pasar algunas mutaciones.

HALLAZGOS:
1. `/home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_modelo_meta.py:38` · menor · Afecta a CA18. La prueba solo confirma que la base de datos rechaza precio 0. Ninguna prueba guarda una `Meta` con precio 1, y el precio más bajo usado en el archivo es 1000. Por eso una restricción mal escrita como `Q(precio__gt=999)` en `gastos/models.py:53` pasaría todas las pruebas. `.claude/rules/pruebas.md` pide probar el valor exacto del límite y el de al lado. Corrige: probador (agregar una prueba que guarde precio 1).
2. `/home/jdrickxd/Documentos/Proyecto_Integrador/gastos/models.py:64-65` · sugerencia · `Meta.__str__` está en el plan pero ninguna prueba lo usa: `coverage report` marca la línea 65 como no cubierta, así que cualquier cambio en el texto pasaría las pruebas. No es un criterio de la spec. Corrige: probador, si se quiere cubrir.
3. `/home/jdrickxd/Documentos/Proyecto_Integrador/gastos/models.py:50` · sugerencia · Ninguna prueba comprueba `ordering = ["fecha_limite", "id"]`. `test_usuario_solo_ve_sus_metas` crea una sola meta por usuario, así que quitar o invertir el orden pasaría las pruebas. Tampoco es un criterio, pero la futura pantalla `/metas/` dependerá de ese orden. Corrige: probador, aquí o en la spec de `/metas/`.

Revisado sin problemas:
- **Meses restantes:** `gastos/reglas/metas.py:1-3` usa exactamente la fórmula de la spec y del plan, con `max(0, …)`. El cambio de año (CA3) y la fecha pasada (CA4) tienen prueba. Las alternativas que miran el día (por ejemplo, días // 30, o restar 1 si el día límite es menor que el día de hoy) las detectan CA1 (2027-02-10 → 3) y CA2 (2026-12-01 → 1). Que hoy sea diciembre con límite en enero, o los días 29–31, no tienen prueba propia. No hace falta: la fórmula no usa el día y ya hay pruebas que detectan cualquier versión que lo use.
- **Cuota:** `metas.py:6-13` usa solo aritmética entera (`-(-falta // meses)`) y no usa `float` ni `math.ceil`. Las mutaciones típicas fallan:
  - `falta // meses + 1` falla en CA7.
  - Quitar el caso `meses == 0` da `ZeroDivisionError` en CA10.
  - Quitar `max(0, …)` falla en CA4.
  - Cambiar `falta <= 0` por `< 0` da el mismo resultado, así que no importa.
  - Los dos casos de división pedidos están cubiertos: falta exacta (CA7) y no exacta (CA6, CA8).
  - Con `Decimal` devuelve `int` (CA11, con `assertIs(type(...), int)`).
  - Una prueba no puede distinguir una versión con `float`: con 12 dígitos, `math.ceil(falta / meses)` da el mismo resultado. Lo de «no usa float» de CA11 se comprobó leyendo el código.
- **Validación:** `metas.py:16-26` sigue el estilo de `validar_gasto`. Las mutaciones de límite fallan: `precio < 0`, `ahorrado <= 0`, `fecha_limite <= hoy`, y tratar como error un ahorrado mayor que el precio. Las pruebas comprueban la clave del error, no el mensaje, igual que las de `validar_gasto`.
- **Arquitectura:** `metas.py` no importa nada, y CA20 lo cubre `test_arquitectura.py`, que recorre todo `gastos/reglas/`. Los montos son `DecimalField(decimal_places=0)`.
- **Modelo y migración:**
  - El modelo y la migración `0002_meta.py` coinciden con el plan: campos, `related_name="metas"`, `CASCADE`, las dos `CheckConstraint` y `ahorrado` con 0 por defecto.
  - La migración la generó `makemigrations` y `0001_initial.py` no se tocó.
  - `makemigrations --check` responde «No changes detected».
- **Pruebas:**
  - Las reglas usan `SimpleTestCase` y el modelo `TestCase`.
  - Las reglas reciben `HOY` fijo y ninguna prueba depende del reloj.
  - Los usuarios de ejemplo se crean con `create_user`.
  - El aislamiento entre usuarios y el borrado en cascada tienen prueba (CA19).
- **Historial:** el commit `test:` (d88b6e6) va antes del `feat:` (6d8bda8). El rojo quedó registrado en `evidencia.md` y falló por el motivo correcto: faltaba el módulo o el modelo.
- **Archivos:** no aparecen `db.sqlite3`, `.env` ni `requirements.txt`. No se tocaron vistas, URLs, formularios, admin, settings, plantillas ni archivos estáticos. Como no hay plantillas en el diff, no apliqué `web-design-guidelines`.

DIFERENCIAS CON LA SPEC:
- Todos los criterios CA1–CA20 tienen prueba, y los nombres coinciden con la tabla del plan.
- No hay archivos fuera del plan.
- Proceso: `specs/003-metas-ahorro/evidencia.md` no está en ningún commit (aparece en `git status` como archivo sin seguimiento). Las casillas T1–T3 de `tareas.md` siguen sin marcar. Lo resuelve el coordinador.

EVIDENCIA:
`python manage.py test`
    Creating test database for alias 'default'...
    ......................................................................................................................................................................
    ----------------------------------------------------------------------
    Ran 166 tests in 44.277s

    OK
    Destroying test database for alias 'default'...
    Found 166 test(s).
    System check identified no issues (0 silenced).

`python manage.py check`
    System check identified no issues (0 silenced).

`python manage.py makemigrations --check --dry-run`
    No changes detected

`coverage run --source=gastos manage.py test`
    Creating test database for alias 'default'...
    ......................................................................................................................................................................
    ----------------------------------------------------------------------
    Ran 166 tests in 44.980s

    OK
    Destroying test database for alias 'default'...
    Found 166 test(s).
    System check identified no issues (0 silenced).

`coverage report`
    Name                        Stmts   Miss  Cover   Missing
    ---------------------------------------------------------
    gastos/__init__.py              0      0   100%
    gastos/admin.py                 1      0   100%
    gastos/apps.py                  3      0   100%
    gastos/forms.py                60      0   100%
    gastos/models.py               33      2    94%   35, 65
    gastos/reglas/__init__.py       0      0   100%
    gastos/reglas/gastos.py         7      0   100%
    gastos/reglas/hormiga.py       19      0   100%
    gastos/reglas/metas.py         22      0   100%
    gastos/reglas/usuarios.py       2      0   100%
    gastos/urls.py                  5      0   100%
    gastos/views.py                52      0   100%
    ---------------------------------------------------------
    TOTAL                         204      2    99%

La cobertura es de 99 %, por encima del mínimo de 80 %. La línea 35 es el `__str__` de `Gasto`, que ya existía; la 65 es el `__str__` de `Meta`.

`git status`: rama `feat/metas-ahorro`; único archivo sin seguimiento: `specs/003-metas-ahorro/evidencia.md`.

Rechazos del hook: ninguno.

NECESITA DE OTRO AGENTE:
- probador: hallazgo 1 (prueba de que la base de datos acepta precio 1). Si se decide cubrirlos, también los hallazgos 2 y 3.
- coordinador: hacer commit de `evidencia.md`, marcar las tareas y anotar en la evidencia que la cobertura la ejecutó el revisor.

PREGUNTAS PARA EL DESARROLLADOR:
1. `validar_meta` (`gastos/reglas/metas.py:20` y `:22`) acepta montos con centavos, como `Decimal("0.5")` o `Decimal("100.7")`. Además, `calcular_cuota_mensual` (`metas.py:7`) los recorta en silencio con `int()`: precio 0,5 con ahorrado 0 da cuota 0, como si la meta estuviera cumplida. ¿Está bien dejar que el rechazo de centavos lo haga el formulario de `/metas/` (`decimal_places=0`) o debe hacerlo la regla?
2. `validar_meta` (`metas.py:18`) acepta nombres de más de 100 caracteres, y SQLite no aplica el `max_length=100` del modelo. ¿Lo controlará el formulario de `/metas/` o debe validarlo la regla?
```

(Las salidas internas se sangraron con cuatro espacios para no romper el bloque de código.)

**Cobertura confirmada por el revisor:** 99 % en `gastos/`, 100 % en `metas.py`, con 166 pruebas. Con esto se cierra la incidencia de cobertura de T2.

### Decisiones del desarrollador (AskUserQuestion, 2026-11-14)
- Pruebas sugeridas (hallazgos 1, 2 y 3): «Las tres».
- Centavos (pregunta 1): «El formulario de /metas/».
- Longitud del nombre (pregunta 2): «El formulario de /metas/».

### Trato de cada hallazgo
| # | Gravedad | Trato | Detalle |
|---|---|---|---|
| 1 | menor | Encargado al probador (vuelta 1) | `test_base_de_datos_acepta_precio_uno` |
| 2 | sugerencia | Encargado al probador (vuelta 1) | `test_str_muestra_nombre_y_precio` |
| 3 | sugerencia | Encargado al probador (vuelta 1) | `test_metas_se_ordenan_por_fecha_limite` |
| P1 | pregunta | **Descartado: se deja como está** | Decisión del desarrollador. Lo resolverá el formulario de `/metas/`. Anotado en `spec.md` (Decisiones tomadas). |
| P2 | pregunta | **Descartado: se deja como está** | Decisión del desarrollador. Lo resolverá el formulario de `/metas/`. Anotado en `spec.md` (Decisiones tomadas). |

### Vuelta de corrección 1 · probador (hallazgos 1, 2 y 3)
Informe literal del probador:

```
ESTADO: verde esperado (pruebas de regresión sobre código existente; no aplica rojo)
ARCHIVOS: /home/jdrickxd/Documentos/Proyecto_Integrador/gastos/tests/test_modelo_meta.py (solo se añadieron pruebas a MetaModeloTests; las existentes no se tocaron; sin commits).

PRUEBAS AÑADIDAS
1. test_base_de_datos_acepta_precio_uno: crea una Meta de ana con precio=1, hace refresh_from_db y comprueba que el precio es Decimal("1").
2. test_str_muestra_nombre_y_precio: Meta «Portátil» con Decimal("1500000"), refresh_from_db, y str(meta) == "Portátil · $1500000".
3. test_metas_se_ordenan_por_fecha_limite: crea en este orden Junio (2027-06-30), Enero (2027-01-31), Marzo (2027-03-31) y Enero bis (2027-01-31, creada después). Espera list(ana.metas.all()) == [enero, enero_bis, marzo, junio]. El orden de creación difiere del esperado.

EVIDENCIA
$ python manage.py test gastos.tests.test_modelo_meta
Creating test database for alias 'default'...
........
----------------------------------------------------------------------
Ran 8 tests in 0.784s

OK
Destroying test database for alias 'default'...
Found 8 test(s).
System check identified no issues (0 silenced).

$ python manage.py test
Creating test database for alias 'default'...
.........................................................................................................................................................................
----------------------------------------------------------------------
Ran 169 tests in 30.330s

OK
Destroying test database for alias 'default'...
Found 169 test(s).
System check identified no issues (0 silenced).

Las tres pruebas pasan a la primera, como se esperaba, porque el código ya existe. No comprobé que fallen ante un mutante, por ejemplo precio__gt=999 o un orden distinto en Meta.Meta. Si el revisor lo quiere, hay que hacerlo con un cambio temporal en producción, y yo no puedo tocar ese código.

Rechazos del hook: ninguno.

NECESITA DE OTRO AGENTE: nada
PREGUNTAS PARA EL DESARROLLADOR: ninguna
```

Commit: `e596bb2 test: pruebas de regresión de la revisión del modelo Meta (spec 003)`. Los hallazgos 1, 2 y 3 quedan **corregidos**. Recuento: 166 + 3 = 169, todas en verde.

**Orden alterado:** las tres pruebas de regresión no tienen fase roja porque cubren código que ya existía. No se comprobó que fallen ante un mutante: el probador no puede tocar producción, y el revisor tiene solo lectura. Por la forma de las pruebas, la de precio 1 haría fallar `precio__gt=999` y la del orden haría fallar cualquier otro `ordering`.

## Cierre
- Tareas T1, T2 y T3 marcadas en `tareas.md`.
- Hubo una sola vuelta de corrección. No se pidió una segunda revisión porque la vuelta solo añadió pruebas a `test_modelo_meta.py`, sin tocar producción. El revisor no ha visto el commit `e596bb2`: queda para la revisión del pull request por otro integrante.
- Cobertura: la midió el revisor en la T3 (99 % en `gastos/`, 100 % en `metas.py`, con 166 pruebas). No se volvió a medir con 169. Con la prueba del `__str__` de `Meta` debería cubrirse la línea 65 de `models.py`. La medirá el CI en el pull request.
- Pull request: lo abre el desarrollador (pendiente de enlace).
