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
| [coordinador](.claude/agents/coordinador.md) | opus | `specs/` | git local (`status`, `diff`, `log`, `switch`, `add`, `commit`) |
| [probador](.claude/agents/probador.md) | sonnet | `gastos/tests/` | `manage.py test` |
| [implementador-backend](.claude/agents/implementador-backend.md) | sonnet | `gastos/` (sin `tests/` ni `migrations/`) y `config/settings.py` | `manage.py test`, `check`, `makemigrations` |
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

Cambios observados al ejecutar las specs: **pendiente**. Se completa con lo que quede anotado en el `evidencia.md` de cada spec.

## Specs

| Spec | Carpeta | Pull request |
|---|---|---|
| Pendiente | | |

## Calidad y su evidencia

| Mecanismo | Cómo funciona | Dónde está la evidencia |
|---|---|---|
| CI en cada pull request | [ci.yml](.github/workflows/ci.yml) ejecuta `check`, `makemigrations --check` y las pruebas. | Pestaña [Actions](https://github.com/JuanDR403/Hormiguero/actions) y los checks de cada PR. |
| Cobertura mínima del 80 % | `coverage report` falla por debajo del umbral de [.coveragerc](.coveragerc). | Resumen del job en Actions. |
| TDD visible en el historial | El `probador` no puede escribir código y el implementador no puede escribir pruebas. El commit `test:` va antes del `feat:`. | Historial de cada rama y la salida en rojo de cada `evidencia.md`. |
| Revisión con hallazgos | El `revisor` reporta `archivo:línea`; cada hallazgo se corrige o se descarta con motivo. Otro integrante aprueba el PR. | `evidencia.md` de cada spec y la conversación del PR. |

Lo que estos controles no ven: un requisito mal entendido en la spec, pruebas débiles que sí cubren las líneas (no usamos mutation testing) y la experiencia real en el navegador, que revisa una persona con `runserver`.