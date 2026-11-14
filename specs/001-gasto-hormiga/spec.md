# Spec 001 · Regla de gasto hormiga

## Problema
El usuario no ve las compras pequeñas que repite seguido (el tinto, el pasaje, el snack) y que sumadas pesan en su presupuesto. Hace falta una regla que, a partir de sus gastos, detecte esos grupos de compras pequeñas repetidas para poder mostrarlos más adelante en `/hormiga/` y en el resumen.

## Alcance
- Incluye:
  - Una función pura `detectar_gasto_hormiga(gastos, umbral, n, hoy)` en `gastos/reglas/hormiga.py`, sin importar Django.
  - Dos constantes en `config/settings.py`: `GASTO_HORMIGA_UMBRAL = 10000` y `GASTO_HORMIGA_N = 3`.
  - Pruebas de la regla en `gastos/tests/`.
- No incluye:
  - Pantalla, vista, URL ni plantilla (`/hormiga/` es otra spec).
  - Cambios al modelo `Gasto` ni migraciones.
  - Filtrar por usuario: la función recibe ya los gastos de un solo usuario; el filtro lo hará la vista que la use.

## Definiciones
- **Gasto de entrada:** cualquier objeto con los atributos `monto` (entero o `Decimal` sin centavos), `fecha` (`date`), `categoria` (texto) y `descripcion` (texto, puede estar vacío). Sirve una instancia de `Gasto`.
- **Ventana:** desde `hoy − 30 días` hasta `hoy`, ambos incluidos (31 días calendario). Los gastos con fecha futura quedan fuera.
- **Bajo el umbral:** `monto ≤ umbral` (inclusivo).
- **Grupo:** clave `(categoria, descripcion normalizada)`. La descripción se normaliza quitando espacios al inicio y al final, colapsando espacios internos y pasando a minúsculas. Una descripción vacía es una clave válida (`""`): los gastos sin descripción de una misma categoría forman un grupo.
- **Gasto hormiga:** un grupo con `n` o más gastos dentro de la ventana y bajo el umbral.

## Resultado
Una lista de grupos; cada grupo es un diccionario con:
- `categoria`: la categoría del grupo.
- `descripcion`: la descripción normalizada.
- `cantidad`: número de gastos del grupo.
- `total`: suma de los montos del grupo (entero, pesos).

Orden: `cantidad` descendente, luego `total` descendente, luego `categoria` y `descripcion` ascendentes. Sin grupos, devuelve lista vacía.

## Criterios de aceptación
Salvo que se diga otra cosa: umbral 10.000, n 3, hoy = 2026-11-14.

- CA1. Dados 3 gastos de 4.000 en `alimentacion` con descripción «Tinto» dentro de la ventana, cuando se detecta, entonces se devuelve un grupo `alimentacion`/`tinto` con `cantidad` 3 y `total` 12.000.
- CA2. Dados solo 2 gastos de ese tipo (n − 1), entonces la lista es vacía.
- CA3. Dados 4 gastos de ese tipo (n + 1), entonces el grupo tiene `cantidad` 4.
- CA4. Un gasto con monto exactamente 10.000 cuenta; uno de 10.001 no cuenta; uno de 9.999 cuenta.
- CA5. Un gasto con fecha `hoy − 30` (2026-10-15) cuenta; uno con `hoy − 31` (2026-10-14) no cuenta; uno con fecha `hoy` cuenta.
- CA6. Un gasto con fecha futura (`hoy + 1`) no cuenta.
- CA7. «Tinto», « tinto » y «TINTO» de la misma categoría forman un solo grupo con descripción `tinto`.
- CA8. La misma descripción en dos categorías distintas forma dos grupos distintos; ninguno llega a n si cada uno tiene menos de n gastos.
- CA9. Tres gastos sin descripción de la misma categoría bajo el umbral forman un grupo con descripción `""`.
- CA10. Con varios grupos hormiga, el resultado sale ordenado por `cantidad` descendente y, a igualdad, por `total` descendente.
- CA11. Con una lista de gastos vacía, devuelve lista vacía.
- CA12. La regla respeta los parámetros: con n = 2 dos gastos bastan; con umbral 3.000 los gastos de 4.000 no cuentan.
- CA13. `config/settings.py` define `GASTO_HORMIGA_UMBRAL == 10000` y `GASTO_HORMIGA_N == 3`.
- CA14. `gastos/reglas/hormiga.py` no importa Django (lo cubre la prueba de arquitectura existente).
- CA15. La función acepta instancias de `Gasto` con montos `Decimal` y devuelve `total` como entero.

## Decisiones tomadas
Respondidas por el desarrollador el 2026-11-14:
- Agrupación: por categoría + descripción.
- Umbral: inclusivo (`monto ≤ umbral`).
- Ventana: `hoy − 30` a `hoy` (31 días, ambos incluidos).
- Valores por defecto: umbral 10.000, N 3.

Respondida por el desarrollador el 2026-11-14, después de la revisión:
- La entrada se supone válida: `n ≥ 1` (llega de `settings.py`) y montos sin centavos (los impide el modelo con `decimal_places=0`). La regla no los valida. Con `n ≤ 0` devuelve todos los grupos con al menos una compra, y un monto con centavos se recorta con `int()`.

Propuestas por el coordinador, pendientes de aprobación junto con la spec:
- La descripción se normaliza (recorte, espacios internos colapsados, minúsculas) y la vacía forma grupo propio.
- Los gastos con fecha futura se excluyen.
- Formato y orden del resultado descritos arriba.
