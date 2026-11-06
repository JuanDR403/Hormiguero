def validar_gasto(monto, fecha, hoy):
    errores = {}
    if monto is None or monto <= 0:
        errores["monto"] = "El monto debe ser mayor que cero."
    if fecha is None or fecha > hoy:
        errores["fecha"] = "La fecha no puede ser futura."
    return errores
