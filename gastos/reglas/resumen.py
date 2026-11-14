"""Resumen del mes: total y total por categoría (función pura, sin Django)."""


def resumir_mes(gastos, hoy):
    """Suma los gastos del mes calendario de `hoy` (del día 1 hasta hoy, inclusive).

    Devuelve {"total": int, "por_categoria": [{"categoria", "total"}, ...]},
    de mayor a menor total y, en empate, por código de categoría ascendente.
    """
    inicio = hoy.replace(day=1)
    total = 0
    totales = {}
    for gasto in gastos:
        if not (inicio <= gasto.fecha <= hoy):
            continue
        monto = int(gasto.monto)
        total += monto
        totales[gasto.categoria] = totales.get(gasto.categoria, 0) + monto

    por_categoria = [{"categoria": c, "total": t} for c, t in totales.items()]
    por_categoria.sort(key=lambda c: (-c["total"], c["categoria"]))
    return {"total": total, "por_categoria": por_categoria}
