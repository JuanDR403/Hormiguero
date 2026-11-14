---
paths:
  - "gastos/tests/**/*.py"
---

# Pruebas

- La prueba se escribe antes que el código y se ve fallar por el motivo correcto.
- Reglas puras: `SimpleTestCase` y `hoy` fijo. Vistas y modelos: `TestCase`.
- El nombre dice qué comprueba: `test_no_elimina_gasto_ajeno`, no `test_eliminar_2`.
- Casos límite siempre: el valor exacto del límite, uno por debajo y uno por encima.
- Usuarios de ejemplo (`ana@ejemplo.com`, `beto@ejemplo.com`) creados con `create_user`. Sin datos personales reales.
- Todo dato que pertenece a un usuario tiene una prueba de aislamiento.
- Una prueba no depende del reloj: fechas relativas a `timezone.localdate()` o `mock.patch`.
- No se cambia una prueba para que pase el código; si la prueba está mal, se explica en el commit.
