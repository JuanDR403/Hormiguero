def meses_restantes(fecha_limite, hoy):
    meses = (fecha_limite.year * 12 + fecha_limite.month) - (hoy.year * 12 + hoy.month)
    return max(0, meses)


def calcular_cuota_mensual(precio, ahorrado, fecha_limite, hoy):
    falta = int(precio) - int(ahorrado)
    if falta <= 0:
        return 0
    meses = meses_restantes(fecha_limite, hoy)
    if meses == 0:
        return falta
    return -(-falta // meses)


def calcular_falta(precio, ahorrado):
    return max(0, int(precio) - int(ahorrado))


def estado_meta(precio, ahorrado, fecha_limite, hoy):
    if int(ahorrado) >= int(precio):
        return "cumplida"
    if fecha_limite < hoy:
        return "vencida"
    return "en_curso"


def validar_meta(nombre, precio, ahorrado, fecha_limite, hoy):
    errores = {}
    if nombre is None or not nombre.strip():
        errores["nombre"] = "El nombre es obligatorio."
    if precio is None or precio <= 0:
        errores["precio"] = "El precio debe ser mayor que cero."
    if ahorrado is None or ahorrado < 0:
        errores["ahorrado"] = "Lo ahorrado no puede ser negativo."
    if fecha_limite is None or fecha_limite < hoy:
        errores["fecha_limite"] = "La fecha límite no puede ser pasada."
    return errores
