# Hormiguero

Gestor de gastos personales con detección de gasto hormiga y metas de ahorro. Proyecto integrador del Diplomado en Ingeniería de Software con IA y Sistemas Agénticos (FET). Un solo repositorio con backend y frontend.

**Stack:** Python 3, Django, SQLite, plantillas de Django con HTML, CSS y JavaScript sencillo (sin frameworks de JavaScript).

## Comandos

```bash
python -m venv .venv
source .venv/bin/activate    # fish: .venv/bin/activate.fish · PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
python manage.py test
```

Al agregar una dependencia: `pip freeze > requirements.txt`.

## Organización del código

- `config/`: configuración de Django.
- `gastos/`: backend.
  - `models.py`, `views.py`, `urls.py`, `forms.py`
  - `reglas/`: reglas de negocio como funciones puras de Python (sin importar Django).
  - `tests/`: pruebas.
- `templates/` y `static/`: frontend. `templates/autenticacion/` y `static/autenticacion.css` son las pantallas de acceso; `static/hormigas.js` es una animación decorativa con botón de pausa.

**Dependencias:** las vistas llaman a `reglas/`; `reglas/` no importa Django ni las vistas; las plantillas solo muestran datos.

## Estado y pantallas previstas

Existen el esqueleto, la autenticación (inicio de sesión, registro y cierre de sesión con `django.contrib.auth`) y la página de inicio, que muestra el saludo si hay sesión. Aún no hay modelos de dominio. Se construye en este orden:

1. **Gastos** (`/gastos/`): lista, formulario para crear y eliminar.
2. **Gasto hormiga** (`/hormiga/`): compras pequeñas repetidas detectadas.
3. **Metas de ahorro** (`/metas/`): lista, formulario y cuota mensual calculada.
4. **Resumen**: total del mes, total por categoría y aviso de gasto hormiga. Reemplazará la página de inicio.

Decisiones de alcance: lista y formulario en la misma página; sin pantalla de edición (solo crear, listar y eliminar); umbral y N como constantes en `settings.py`; autenticación mínima (sin recuperación de contraseña, verificación de correo ni perfiles); la IA no es una pantalla.

## Reglas de negocio (backend)

- Un gasto requiere monto mayor que cero y fecha no futura.
- **Gasto hormiga:** compras bajo un umbral configurable que se repiten N veces en 30 días.
- **Cuota de ahorro:** (precio − ahorrado) ÷ meses restantes, redondeada hacia arriba.
- Cada gasto y cada meta pertenece a un usuario. Un usuario solo ve y modifica los suyos, y las vistas del dominio exigen sesión iniciada.
- El correo electrónico es el nombre de usuario: no puede repetirse y se normaliza (sin espacios y en minúsculas) antes de guardarse.
- Si se agrega un consejo con IA, el código calcula los números y la IA solo los explica; debe poder simularse en las pruebas.

## Convenciones

- `snake_case`; nombres del dominio en español (`gasto`, `meta`, `categoria`); textos de la interfaz en español.
- Toda regla nueva lleva pruebas en `gastos/tests/`, incluidos casos límite.
- Ramas `feat/<tema>`, `fix/<tema>`, `chore/<tema>`. Nunca se sube directo a `main`: pull request revisado por otro integrante.
- Commits con el formato `tipo: descripción` (`feat:`, `fix:`, `test:`, `docs:`, `chore:`).

## Backend y frontend

- **Backend** (`gastos/`): modelos, vistas, URLs, formularios y reglas de negocio. Se prueba con `python manage.py test`. No lleva código de presentación.
- **Frontend** (`templates/`, `static/`): las plantillas heredan de una plantilla base. Se revisa abriendo la página con `runserver`. No lleva lógica de negocio. Los formularios llevan `{% csrf_token %}`.

## Lo que el agente no debe hacer

- Subir claves, tokens ni `.env` (las variables van en `.env.example`).
- Editar `db.sqlite3` ni borrar o reescribir a mano migraciones ya aplicadas.
- Agregar dependencias sin avisar y sin actualizar `requirements.txt`.
- Poner reglas de negocio en vistas o plantillas.
- Guardar contraseñas a mano: se usan `create_user` y los validadores de contraseña de Django.
- Usar datos personales reales; solo datos de ejemplo.
- Hacer push a `main` ni fusionar sin pull request.