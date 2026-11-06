# Plan 1 · Regla de validación de gastos (solicitud 1, backend)

## Contexto

Hormiguero aún no tiene modelos de dominio: solo autenticación (PR #1) y la página de inicio. La primera regla de negocio de AGENTS.md es **"un gasto requiere monto mayor que cero y fecha no futura"**. Esta solicitud crea el modelo `Gasto` y esa regla, con sus pruebas, para que la solicitud 2 (frontend) construya la página `/gastos/` sobre ella.

Decisiones ya tomadas:
- Solo backend: regla pura, modelo, migración, formulario y pruebas. Vista, URL y plantilla de `/gastos/` quedan para la solicitud 2.
- Montos en pesos colombianos **enteros, sin centavos**: el mínimo válido es 1.
- La rama parte de `main` después de fusionar `chore/memoria-y-skills`.

## Paso 0 · Requisito previo (lo hace el equipo, no el agente)

1. En `chore/memoria-y-skills`, commit de `skills-lock.json` (`chore: registrar origen de la skill web-design-guidelines`) y push.
2. Abrir el PR de `chore/memoria-y-skills`, que otro integrante lo revise y fusionarlo en `main`.
3. Luego el agente ejecuta (igual en fish y PowerShell):
   ```
   git switch main
   git pull
   git switch -c feat/solicitud-1
   ```

## Paso 1 · Regla pura: `gastos/reglas/gastos.py` (nuevo)

Sin importar Django, igual que `gastos/reglas/usuarios.py`.

```python
def validar_gasto(monto, fecha, hoy):
    errores = {}
    if monto is None or monto <= 0:
        errores["monto"] = "El monto debe ser mayor que cero."
    if fecha is None or fecha > hoy:
        errores["fecha"] = "La fecha no puede ser futura."
    return errores
```

- `hoy` es un parámetro para que la función sea pura y las pruebas no dependan del reloj.
- Devuelve `{campo: mensaje}` (vacío si es válido), así se muestran ambos errores a la vez.

## Paso 2 · Modelo `Gasto`: `gastos/models.py`

```python
class Gasto(models.Model):
    class Categoria(models.TextChoices):
        ALIMENTACION = "alimentacion", "Alimentación"
        TRANSPORTE = "transporte", "Transporte"
        HOGAR = "hogar", "Hogar"
        ENTRETENIMIENTO = "entretenimiento", "Entretenimiento"
        SALUD = "salud", "Salud"
        OTROS = "otros", "Otros"

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="gastos")
    monto = models.DecimalField(max_digits=12, decimal_places=0)
    fecha = models.DateField()
    categoria = models.CharField(max_length=20, choices=Categoria, default=Categoria.OTROS)
    descripcion = models.CharField(max_length=200, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-id"]
        constraints = [
            models.CheckConstraint(condition=models.Q(monto__gt=0), name="gasto_monto_positivo"),
        ]
```

- Se incluye `categoria`, porque el resumen por categoría la necesita, para no crear otra migración enseguida.
- `CheckConstraint` es la segunda defensa en la base de datos. La fecha no futura no va como restricción porque "hoy" cambia cada día.
- Se agrega `__str__` con descripción y monto.

## Paso 3 · Migración

`python manage.py makemigrations gastos` genera `gastos/migrations/0001_initial.py`. Luego `python manage.py migrate`. Nada se escribe a mano.

## Paso 4 · Formulario: `gastos/forms.py`

Se agrega `FormularioGasto(forms.ModelForm)` junto a los formularios de autenticación existentes:

- Campos `monto`, `fecha`, `categoria` y `descripcion`. `usuario` no se incluye: lo asignará la vista desde `request.user`.
- Etiquetas en español; `fecha` con `DateInput(attrs={"type": "date"})`.
- `error_messages` de `monto`: `max_decimal_places` → "El monto debe ser en pesos enteros, sin centavos."
- `__init__(self, *args, hoy=None, **kwargs)` guarda `hoy`, y si no llega usa `timezone.localdate()`, la fecha de Bogotá según `TIME_ZONE`.
- `clean()` llama a `validar_gasto(datos.get("monto"), datos.get("fecha"), self.hoy)` y hace `add_error` solo en los campos que no tengan ya un error, para no duplicar mensajes cuando el campo falló antes, por ejemplo con decimales.

## Paso 5 · Pruebas: `gastos/tests/`

**`test_reglas_gastos.py`** (`SimpleTestCase`, `hoy` fijo):
- Monto: `0`, `-1` y `None` son inválidos; `1` (mínimo) y `25000` son válidos.
- Fecha: `hoy` es válida (límite), ayer es válida, `hoy + 1 día` es inválida y `None` es inválida.
- Monto y fecha inválidos a la vez dan los dos errores; un gasto válido devuelve `{}`.

**`test_gasto.py`** (`TestCase`):
- Modelo: `Gasto.objects.create(..., monto=0)` lanza `IntegrityError`; `ordering` lista primero lo más reciente.
- Formulario:
  - Datos válidos con `hoy` inyectado son válidos.
  - Fecha futura → error en `fecha`; monto `0` → error en `monto`, en español.
  - `1500.50` y `0.5` se rechazan con el mensaje de pesos enteros, que aparece una sola vez.
  - `usuario` en los datos se ignora (no está en `fields`).
  - Sin `hoy` usa `timezone.localdate()`: se prueba con `mock.patch` de `django.utils.timezone.localdate`.

## Paso 6 · Documentación

- `AGENTS.md`, sección de reglas de negocio: agregar "Los montos son pesos colombianos enteros (sin centavos)."
- Copiar este plan, sin editarlo, a `plan-1-grupo9.md` en la raíz del repositorio.

## Paso 7 · Commit y PR

- Commits: `feat: modelo Gasto y regla de monto y fecha` (código, migración y pruebas) y `docs: plan 1 y montos sin centavos en AGENTS.md`.
- `git push -u origin feat/solicitud-1`. `gh` no está instalado, así que el agente entrega el título y la descripción del PR para pegarlos en GitHub. Lo revisa otro integrante antes de fusionar.

## Archivos

- Nuevos: `gastos/reglas/gastos.py`, `gastos/migrations/0001_initial.py`, `gastos/tests/test_reglas_gastos.py`, `gastos/tests/test_gasto.py`, `plan-1-grupo9.md`.
- Modificados: `gastos/models.py`, `gastos/forms.py`, `AGENTS.md`.
- Sin cambios: vistas, URLs, plantillas, `settings.py` y `requirements.txt` (sin dependencias nuevas).

## Verificación

```
python manage.py test
python manage.py makemigrations --check --dry-run
python manage.py check
python manage.py migrate
```

Esperado: las 20 pruebas actuales y las nuevas pasan, no faltan migraciones, `check` no reporta problemas y `migrate` aplica `gastos.0001_initial`. Además, `git status` no muestra `db.sqlite3` ni `.env`.
