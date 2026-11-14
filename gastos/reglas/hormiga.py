"""Regla de gasto hormiga: compras pequeñas que se repiten en 30 días."""

from collections import defaultdict
from datetime import timedelta

VENTANA_DIAS = 30


def _normalizar(descripcion):
    return " ".join((descripcion or "").split()).lower()


def detectar_gasto_hormiga(gastos, umbral, n, hoy):
    """Devuelve los grupos (categoria, descripcion) con n o más compras pequeñas.

    Cuenta gastos con fecha entre hoy - 30 días y hoy (ambos incluidos) y
    monto menor o igual al umbral. Cada grupo es un dict con categoria,
    descripcion (normalizada), cantidad y total (int).
    """
    desde = hoy - timedelta(days=VENTANA_DIAS)
    grupos = defaultdict(lambda: [0, 0])
    for gasto in gastos:
        if not (desde <= gasto.fecha <= hoy):
            continue
        if gasto.monto > umbral:
            continue
        clave = (gasto.categoria, _normalizar(gasto.descripcion))
        grupos[clave][0] += 1
        grupos[clave][1] += int(gasto.monto)

    resultado = [
        {
            "categoria": categoria,
            "descripcion": descripcion,
            "cantidad": cantidad,
            "total": total,
        }
        for (categoria, descripcion), (cantidad, total) in grupos.items()
        if cantidad >= n
    ]
    resultado.sort(
        key=lambda g: (-g["cantidad"], -g["total"], g["categoria"], g["descripcion"])
    )
    return resultado
