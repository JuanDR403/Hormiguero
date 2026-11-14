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
