---
name: django-reglas-y-pruebas
description: Use when adding or changing business rules, models or tests in the Hormiguero backend (gastos/reglas, gastos/models.py, gastos/tests). Guides writing pure rule functions, user-owned data and their tests.
---

# Reglas de negocio y pruebas en Hormiguero

## Cuándo usarla
Al crear o modificar reglas, modelos o pruebas del backend: validación de gastos, gasto hormiga, cuota de ahorro o datos que pertenecen a un usuario.

## Pasos
1. Escribe la regla como función pura en `gastos/reglas/` (sin importar Django, vistas ni plantillas). Si depende de la fecha, recibe `hoy` como parámetro; no leas la hora del sistema dentro de la regla.
2. Escribe primero las pruebas en `gastos/tests/`, incluyendo casos límite:
   - monto cero y monto negativo
   - fecha de hoy, ayer y mañana
   - el límite exacto del umbral y de N repeticiones
   - la meta sin meses restantes o ya cumplida
3. Los montos son pesos colombianos enteros, sin centavos.
4. Si el modelo es del dominio (gasto, meta), agrega la relación con el usuario y una prueba que demuestre que un usuario no ve ni modifica los datos de otro.
5. Conecta la regla con el formulario, la vista o el modelo solo después de que las pruebas pasen.
6. Ejecuta `python manage.py test` y no des la tarea por terminada si algo falla.

## Reglas de negocio vigentes
- Un gasto requiere monto mayor que cero y fecha no futura.
- Gasto hormiga: compras bajo un umbral configurable que se repiten N veces en 30 días.
- Cuota de ahorro: (precio − ahorrado) ÷ meses restantes, redondeada hacia arriba.
- Las vistas del dominio exigen sesión iniciada y filtran por el usuario actual.

## Límites
- No modifiques migraciones ya aplicadas ni `db.sqlite3`.
- No pongas lógica de negocio en las vistas o en las plantillas.
- Usa solo datos de ejemplo.