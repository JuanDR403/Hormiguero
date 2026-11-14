# Spec 003 · Metas de ahorro (backend)

## Problema
El usuario quiere ahorrar para algo concreto (un portátil, un viaje) antes de una fecha y no sabe cuánto apartar cada mes. Hace falta guardar sus metas y una regla que calcule la cuota mensual, para mostrarla más adelante en `/metas/` y en el resumen.

## Alcance
- Incluye:
  - Modelo `Meta` en `gastos/models.py` (nombre, precio, ahorrado, fecha límite, usuario) y su migración generada con `makemigrations`.
  - Reglas puras en `gastos/reglas/metas.py`, sin importar Django:
    - `meses_restantes(fecha_limite, hoy)`
    - `calcular_cuota_mensual(precio, ahorrado, fecha_limite, hoy)`
    - `validar_meta(nombre, precio, ahorrado, fecha_limite, hoy)`
  - Pruebas en `gastos/tests/`.
- No incluye:
  - Pantalla, vista, URL, formulario ni plantilla (`/metas/` es otra spec).
  - Registro en el admin.
  - Editar una meta ni sumar abonos a `ahorrado`.

## Definiciones
- **Meses restantes:** meses de calendario entre el mes de `hoy` y el mes de `fecha_limite`, sin mirar el día: `(año_límite·12 + mes_límite) − (año_hoy·12 + mes_hoy)`. Si sale negativo, es 0. Una fecha límite en el mes actual da 0.
- **Falta:** `precio − ahorrado`.
- **Meta cumplida:** `ahorrado ≥ precio`.
- **Cuota mensual** (entero, pesos):
  - Meta cumplida → `0`, sin importar la fecha.
  - Meses restantes = 0 y falta dinero → `falta` (hay que juntarlo ya).
  - En otro caso → `falta ÷ meses restantes`, redondeada hacia arriba.
- **Validación** (`validar_meta`): devuelve un diccionario `campo → mensaje`, vacío si todo es válido, igual que `validar_gasto`. Campos: `nombre`, `precio`, `ahorrado`, `fecha_limite`.

## Criterios de aceptación
Salvo que se diga otra cosa: hoy = 2026-11-14.

Meses restantes:
- CA1. Con fecha límite 2027-02-10, `meses_restantes` es 3 (el día no cuenta).
- CA2. Con fecha límite 2026-11-30 (mismo mes), es 0; con 2026-12-01, es 1.
- CA3. Con fecha límite 2027-01-15 (cambio de año), es 2.
- CA4. Con fecha límite pasada (2026-10-01), es 0, no negativo.

Cuota mensual:
- CA5. Precio 1.200.000, ahorrado 200.000, límite 2027-04-30 (5 meses) → cuota 200.000.
- CA6. Precio 1.000.000, ahorrado 0, límite 2027-02-01 (3 meses) → cuota 333.334 (hacia arriba).
- CA7. Precio 900.000, ahorrado 0, límite 2027-02-01 → cuota 300.000 (división exacta, sin sumar 1).
- CA8. Falta 1 peso con 3 meses → cuota 1.
- CA9. Meta cumplida con ahorrado = precio → cuota 0; con ahorrado > precio → cuota 0 (nunca negativa); cumplida y con fecha pasada → cuota 0.
- CA10. Sin meses restantes y faltando dinero: límite en el mes actual (2026-11-30), precio 500.000, ahorrado 100.000 → cuota 400.000; con límite pasado (2026-10-01) → también 400.000.
- CA11. La cuota acepta `Decimal` sin centavos en precio y ahorrado y devuelve `int`. No usa `float`.

Validación:
- CA12. Nombre vacío o solo espacios → error en `nombre`; «Portátil» es válido.
- CA13. Precio 0 → error; precio 1 → válido; precio `None` → error.
- CA14. Ahorrado −1 → error; ahorrado 0 → válido; ahorrado mayor que el precio → válido; ahorrado `None` → error.
- CA15. Fecha límite ayer (2026-11-13) → error; hoy (2026-11-14) → válida; `None` → error.
- CA16. Una meta con todos los datos válidos devuelve `{}`.

Modelo:
- CA17. Una `Meta` de `ana@ejemplo.com` se guarda con nombre, precio, ahorrado y fecha límite; `ahorrado` vale 0 por defecto.
- CA18. La base de datos rechaza precio 0 y ahorrado negativo (`CheckConstraint`, `IntegrityError`).
- CA19. Aislamiento: `ana.metas` no incluye las metas de `beto@ejemplo.com`; al borrar a un usuario se borran sus metas.
- CA20. `gastos/reglas/metas.py` no importa Django (lo cubre la prueba de arquitectura existente).

## Decisiones tomadas
Respondidas por el desarrollador el 2026-11-14:
- Meses restantes: meses de calendario, sin mirar el día; el mes actual da 0.
- Sin meses restantes y faltando dinero: la cuota es todo lo que falta.
- Validación completa: nombre no vacío, precio > 0, ahorrado ≥ 0 (puede superar el precio), fecha límite hoy o después.
- Meta cumplida: cuota 0.

Propuestas por el coordinador y aprobadas por el desarrollador junto con la spec el 2026-11-14:
- La regla de cuota no valida la entrada (la valida `validar_meta` y el modelo); una fecha pasada solo se trata para que la cuota de metas viejas no falle.
- `ahorrado` tiene valor por defecto 0.
- Sin admin ni formulario en esta spec.
