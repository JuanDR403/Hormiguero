# Hormiguero

Gestor de gastos personales con detección de gasto hormiga y metas de ahorro.

## Estructura
- `gastos/`: backend (modelos, vistas, reglas de negocio y pruebas)
- `templates/` y `static/`: frontend
- `config/`: configuración de Django

## Instalación
```bash
python -m venv .venv
source .venv/bin/activate        # fish: source .venv/bin/activate.fish
                                 # PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Abrir http://127.0.0.1:8000

## Pruebas
```bash
python manage.py test
coverage run manage.py test && coverage report   # mínimo 80 % en gastos/
```

# El arnés

El arnés es lo que rodea a Claude Code para que trabaje bien en este proyecto: lo que lee al iniciar, lo que carga cuando lo necesita, los agentes que ejecutan el trabajo, el flujo que siguen y los controles que revisan lo que producen. El equipo usa **Claude Code**.

## Piezas y dónde están

| Pieza | Dónde | Qué hace |
|---|---|---|
| Memoria | [AGENTS.md](AGENTS.md) (la importa [CLAUDE.md](CLAUDE.md)) | Comandos, organización, reglas de negocio, convenciones y lo que el agente no debe hacer. Se lee en cada sesión. |
| Normas por tipo de archivo | [.claude/rules/](.claude/rules/) | `backend.md`, `pruebas.md` y `frontend.md`. Cada una se carga solo cuando el agente trabaja con archivos de esas rutas. |
| Skills | [.claude/skills/](.claude/skills/) | Cuatro procedimientos que el agente carga cuando los necesita. |
| Agentes | [.claude/agents/](.claude/agents/) | Un coordinador y cuatro subagentes, cada uno con sus herramientas, su modelo y sus carpetas. |
| Permisos | [.claude/hooks/limitar_agente.py](.claude/hooks/limitar_agente.py) | Rechaza las escrituras y los comandos que no le corresponden a cada agente. |
| Specs | [specs/](specs/) | Una carpeta por funcionalidad: especificación, plan, tareas y evidencia. |
| Calidad | [.github/workflows/ci.yml](.github/workflows/ci.yml), [.coveragerc](.coveragerc) | Pruebas y cobertura mínima en cada pull request. |

No usamos Spec Kit, así que no hay `constitution.md`. Los principios no negociables están en AGENTS.md, en «Reglas de negocio» y «Lo que el agente no debe hacer».

## Para qué usamos cada skill

| Skill | Problema que resuelve | Cuándo se invoca |
|---|---|---|
| [django-reglas-y-pruebas](.claude/skills/django-reglas-y-pruebas/SKILL.md) (propia) | Sin un procedimiento, nada asegura que la regla quede fuera de la vista ni que se prueben los casos límite. La skill fija el orden: regla pura, pruebas con límites, aislamiento por usuario. | La cargan el `probador` y el `implementador-backend` al tocar reglas, modelos o pruebas. |
| [sdd-hormiguero](.claude/skills/sdd-hormiguero/SKILL.md) (propia) | No usamos Spec Kit, así que hace falta una estructura propia y siempre igual. La skill define la carpeta, los cuatro archivos y el orden de los commits. | La carga el `coordinador` al empezar o retomar una spec. |
| [revision-hormiguero](.claude/skills/revision-hormiguero/SKILL.md) (propia) | Las pruebas en verde no muestran pruebas débiles, consultas sin filtrar por usuario ni diferencias con la spec. La skill es la lista de revisión. | La carga el `revisor` antes de cada pull request. También sirve a quien revisa el PR. |
| [web-design-guidelines](.claude/skills/web-design-guidelines/SKILL.md) (de terceros) | Accesibilidad y diseño de las plantillas: etiquetas, foco, contraste, estructura. | La carga el `revisor` cuando el cambio toca plantillas. |

`web-design-guidelines` viene de Vercel. Su `SKILL.md` no trae scripts: descarga un documento de reglas con WebFetch y revisa los archivos que se le indican. Su origen está registrado en [skills-lock.json](skills-lock.json).

## Cómo se usa

1. Abrir el coordinador en la raíz del repositorio, con el entorno virtual activo:
   ```bash
   claude --agent coordinador
   ```
2. Describir la funcionalidad. El coordinador escribe `specs/NNN-tema/spec.md`, `plan.md` y `tareas.md`, y pregunta lo que no puede decidir.
3. El desarrollador aprueba la spec. Sin aprobación no se escribe código.
4. El coordinador crea la rama y encarga, en este orden:
   1. `probador`: pruebas en rojo.
   2. `implementador-backend`: código hasta el verde.
   3. `implementador-frontend`: plantillas, si la spec tiene pantalla.
   4. `revisor`: revisión del diff. Como máximo dos vueltas de corrección; después pregunta.
5. El coordinador deja la evidencia en `specs/NNN-tema/evidencia.md` y entrega el texto del pull request.
6. El desarrollador hace el push y abre el pull request. Otro integrante lo revisa y se fusiona con el CI en verde.

Ningún agente hace push ni fusiona.

## Los agentes

| Agente | Modelo | Escribe en | Ejecuta |
|---|---|---|---|
| [coordinador](.claude/agents/coordinador.md) | opus | `specs/` | git sin push (`status`, `diff`, `log`, `ls-files`, `fetch`, `pull`, `switch`, `add`, `commit`) |
| [probador](.claude/agents/probador.md) | sonnet | `gastos/tests/` | `manage.py test` |
| [implementador-backend](.claude/agents/implementador-backend.md) | sonnet | `gastos/` (sin `tests/` ni `migrations/`) y `config/settings.py` | `manage.py test`, `check`, `makemigrations`, `coverage` |
| [implementador-frontend](.claude/agents/implementador-frontend.md) | sonnet | `templates/`, `static/` | `manage.py test`, `curl` a `localhost:8000` |
| [revisor](.claude/agents/revisor.md) | opus | nada | `manage.py test`, `check`, `makemigrations --check`, `coverage`, git de lectura |

El campo `tools` de cada agente dice qué herramientas tiene. El hook `PreToolUse` de su encabezado dice en qué carpetas y con qué comandos puede usarlas.

### Qué cambió respecto del taller y por qué

Cambios hechos al pasar del diseño a los archivos:

| Cambio | En el taller | Ahora | Por qué |
|---|---|---|---|
| El coordinador escribe | No tenía `Edit` ni `Write`; el plan lo escribía el modo plan | Escribe solo en `specs/` | El proyecto integrador pide especificación, plan y tareas en el repositorio. Un solo archivo de plan ya no alcanza. |
| El coordinador usa git | No tenía `Bash` | Solo git local, sin push | Para que el TDD se vea en el historial, el commit de las pruebas va antes que el del código. Sin git, el desarrollador tendría que interrumpir en cada fase. |
| `config/settings.py` | El backend solo escribía en `gastos/` | También en `config/settings.py` | El umbral y el N del gasto hormiga son constantes de `settings.py`. |
| Migraciones | «Migraciones nuevas» permitidas | No escribe en `gastos/migrations/`; las genera `makemigrations` | Es más simple de comprobar en el hook y cubre también la regla de no editar migraciones aplicadas. |
| Skill del revisor | Solo `web-design-guidelines` | Además `revision-hormiguero` | La lista de revisión estaba dentro de la descripción del agente; como skill la puede usar también la persona que revisa el PR. |
| Skill de diseño en el frontend | El `implementador-frontend` usaba `web-design-guidelines` | Solo la usa el `revisor` | La skill necesita WebFetch para descargar sus reglas y el implementador no tiene esa herramienta. Sus normas de accesibilidad están en `.claude/rules/frontend.md`. |
| Reglas sin Django | Un paso del CI | La prueba `gastos/tests/test_arquitectura.py` | Como prueba corre también en local, antes del PR. |

Cambios observados al ejecutar las specs:

| Spec | Qué observamos | Qué cambió |
|---|---|---|
| 001 | El `probador` no pudo escribir pruebas ni ejecutarlas: lo rechazaba el hook del coordinador. Al abrir la sesión con `claude --agent coordinador`, su hook sigue activo mientras trabajan los subagentes. | El hook lee el campo `agent_type` que envía Claude Code y solo juzga las llamadas del agente al que pertenece. |
| 001 | El coordinador no pudo actualizar `main` antes de crear la rama. | Se le permiten `git fetch` y `git pull`. Sigue sin poder hacer push. |
| 001 | El hook rechazó el commit con la línea `Co-Authored-By: ... <correo>`, por los símbolos `<` y `>` y por el salto de línea del mensaje. | El hook ya no revisa esos símbolos dentro del texto entre comillas. Fuera de las comillas siguen prohibidos, igual que `$(` y las comillas invertidas en cualquier parte. |
| 001 | Los agentes anteponían `cd <carpeta> &&` a los comandos y el hook lo rechazaba por encadenar. | Las instrucciones de cada agente dicen que ejecute un comando por llamada, sin `cd`. |
| 001 | El `revisor` encontró que el hook se podía saltar con una comilla escapada (`git status \' ; otro comando ; \'`) y que un subagente sin perfil quedaba sin restricciones. | El hook rechaza la barra invertida y las comillas sin cerrar, y un agente sin perfil no puede escribir ni ejecutar. Lo cubren las pruebas de `gastos/tests/test_hook_permisos.py`. |
| 001 a 003 | El coordinador intentó `git ls-files` en cada spec para listar los archivos y el hook lo rechazó. | Se permite `git ls-files` al coordinador y al revisor: solo lee. |
| 001 y 003 | La tarea del `implementador-backend` pedía confirmar la cobertura, pero no podía ejecutar `coverage`; la medía después el `revisor`. | El `implementador-backend` puede ejecutar `coverage run` y `coverage report`, y cierra su tarea con la cobertura medida. |
| 002 y 004 | La herramienta corta la salida larga de `python manage.py test` y el hook no deja filtrarla con `tail` ni redirigirla. | No se cambió el hook: permitir tuberías abre la puerta a encadenar comandos. Los agentes ejecutan las pruebas por módulo. |
| 004 y 005 | El `implementador-frontend` no puede ejecutar `coverage` ni `git diff`. | No se cambió: la cobertura la mide el `revisor` y el coordinador comprueba el diff del frontend antes de cada commit. Desde la spec 005 el coordinador pide la cobertura al `revisor` desde el principio. |
| 005 | El `probador` y el `implementador-frontend` trabajaron a la vez en la vuelta de corrección, sobre archivos distintos, sin estorbarse. | Nada: las carpetas separadas lo permiten. |

El detalle está en el `evidencia.md` de cada spec, en la parte de incidencias o notas del arnés.

## Specs

| Spec | Qué construye | Especificación, plan, tareas y evidencia | Pull request | CI del pull request |
|---|---|---|---|---|
| 001 | Regla de gasto hormiga (backend) | [specs/001-gasto-hormiga/](specs/001-gasto-hormiga/) | [#9](https://github.com/JuanDR403/Hormiguero/pull/9) | [en verde](https://github.com/JuanDR403/Hormiguero/actions/runs/43600869332) |
| 002 | Pantalla `/hormiga/` | [specs/002-pantalla-hormiga/](specs/002-pantalla-hormiga/) | [#10](https://github.com/JuanDR403/Hormiguero/pull/10) | [en verde](https://github.com/JuanDR403/Hormiguero/actions/runs/43611356058) |
| 003 | Modelo `Meta` y cuota mensual (backend) | [specs/003-metas-ahorro/](specs/003-metas-ahorro/) | [#11](https://github.com/JuanDR403/Hormiguero/pull/11) | [en verde](https://github.com/JuanDR403/Hormiguero/actions/runs/43615045495) |
| 004 | Pantalla `/metas/` | [specs/004-pantalla-metas/](specs/004-pantalla-metas/) | [#13](https://github.com/JuanDR403/Hormiguero/pull/13) | [en verde](https://github.com/JuanDR403/Hormiguero/actions/runs/43618900192) |
| 005 | Resumen del mes en la página de inicio | [specs/005-resumen/](specs/005-resumen/) | [#14](https://github.com/JuanDR403/Hormiguero/pull/14) | [en verde](https://github.com/JuanDR403/Hormiguero/actions/runs/43625804908) |

Los cambios del arnés que no cabían en una spec tienen su propio pull request: [#8](https://github.com/JuanDR403/Hormiguero/pull/8) (arnés inicial) y [#12](https://github.com/JuanDR403/Hormiguero/pull/12) (permisos).

## Calidad y su evidencia

| Mecanismo | Cómo funciona | Dónde está la evidencia |
|---|---|---|
| CI en cada pull request | [ci.yml](.github/workflows/ci.yml) ejecuta `check`, `makemigrations --check` y las pruebas. | Pestaña [Actions](https://github.com/JuanDR403/Hormiguero/actions): 14 ejecuciones, todas en verde. El enlace de cada spec está en la tabla de specs. |
| Cobertura mínima del 80 % | `coverage report` falla por debajo del umbral de [.coveragerc](.coveragerc). | Resumen de cobertura de cada ejecución en Actions. En `main`: 99 % con 265 pruebas. |
| TDD visible en el historial | El `probador` no puede escribir código y el implementador no puede escribir pruebas. El commit `test:` va antes del `feat:`. | Historial de cada pull request (por ejemplo, en [#11](https://github.com/JuanDR403/Hormiguero/pull/11/commits) el commit `test:` en rojo va antes del `feat:`) y la salida en rojo copiada en cada `evidencia.md`. |
| Revisión con hallazgos | El `revisor` reporta `archivo:línea`; cada hallazgo se corrige o se descarta con motivo. Máximo dos vueltas. | Sección de revisión de cada `evidencia.md`. Ejemplos: en la [001](specs/001-gasto-hormiga/evidencia.md) encontró cómo saltarse el hook de permisos; en la [002](specs/002-pantalla-hormiga/evidencia.md), un error con una categoría desconocida; en la [005](specs/005-resumen/evidencia.md), una prueba que ocultaba «Noviembre» con mayúscula. |
| Pruebas del propio arnés | `gastos/tests/test_hook_permisos.py` comprueba los permisos de cada agente y `test_arquitectura.py`, que las reglas no importan Django. | Corren en el CI con el resto de las pruebas. |

Lo que estos controles no ven: un requisito mal entendido en la spec (en la 005, la spec y la primera prueba suponían lo mismo sobre el nombre del mes y las dos estaban equivocadas), pruebas débiles que sí cubren las líneas (no usamos mutation testing) y la experiencia real en el navegador, que revisa una persona con `runserver`.