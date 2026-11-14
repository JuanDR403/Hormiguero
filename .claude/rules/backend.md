---
paths:
  - "gastos/**/*.py"
  - "config/**/*.py"
---

# Backend

- Las reglas de negocio son funciones puras en `gastos/reglas/`. Esos archivos no importan Django; si dependen de la fecha, reciben `hoy` como parámetro.
- Las vistas llaman a las reglas y no repiten cálculos de negocio.
- Toda vista del dominio lleva `login_required` y filtra por `request.user`. Un dato ajeno responde 404.
- Las acciones que cambian datos solo aceptan POST (`require_POST`).
- Los formularios del dominio no incluyen el campo `usuario`: lo asigna la vista.
- Los montos son pesos enteros: `DecimalField(decimal_places=0)` o enteros; nunca `float`.
- Las migraciones se generan con `makemigrations`; no se edita una ya aplicada.
- El umbral y el N del gasto hormiga son constantes de `config/settings.py`.
- Nombres del dominio en español y `snake_case`.
