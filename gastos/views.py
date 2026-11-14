from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST, require_safe

from .forms import FormularioGasto, FormularioMeta, FormularioRegistro
from .models import Gasto, Meta
from .reglas.hormiga import VENTANA_DIAS, detectar_gasto_hormiga
from .reglas.metas import (
    calcular_cuota_mensual,
    calcular_falta,
    estado_meta,
    meses_restantes,
)
from .reglas.resumen import resumir_mes

NOMBRES_ESTADO = {
    "cumplida": "Cumplida",
    "vencida": "Vencida",
    "en_curso": "En curso",
}


def inicio(request):
    if not request.user.is_authenticated:
        return render(request, "inicio.html")

    hoy = timezone.localdate()
    gastos = Gasto.objects.filter(usuario=request.user)
    resumen = resumir_mes(gastos, hoy)
    nombres_categoria = dict(Gasto.Categoria.choices)
    for categoria in resumen["por_categoria"]:
        # Si el código no está entre las opciones, se muestra tal cual.
        categoria["categoria_nombre"] = nombres_categoria.get(
            categoria["categoria"], categoria["categoria"]
        )
    grupos = detectar_gasto_hormiga(
        gastos,
        settings.GASTO_HORMIGA_UMBRAL,
        settings.GASTO_HORMIGA_N,
        hoy,
    )
    contexto = {
        "hoy": hoy,
        "total_mes": resumen["total"],
        "por_categoria": resumen["por_categoria"],
        "cantidad_hormiga": len(grupos),
        "dias": VENTANA_DIAS,
    }
    return render(request, "inicio.html", contexto)


def registro(request):
    if request.user.is_authenticated:
        return redirect("inicio")

    if request.method == "POST":
        formulario = FormularioRegistro(request.POST)
        if formulario.is_valid():
            login(request, formulario.save())
            return redirect("inicio")
    else:
        formulario = FormularioRegistro()

    return render(request, "autenticacion/registro.html", {"formulario": formulario})


@login_required
def lista_gastos(request):
    if request.method == "POST":
        formulario = FormularioGasto(request.POST)
        if formulario.is_valid():
            gasto = formulario.save(commit=False)
            gasto.usuario = request.user
            gasto.save()
            messages.success(request, "Gasto registrado.")
            return redirect("lista_gastos")
    else:
        formulario = FormularioGasto(initial={"fecha": timezone.localdate()})

    # El orden (más reciente primero) viene del Meta del modelo.
    gastos = Gasto.objects.filter(usuario=request.user)
    return render(request, "gastos/lista.html", {"formulario": formulario, "gastos": gastos})


@login_required
@require_POST
def eliminar_gasto(request, pk):
    # Filtrar por usuario hace que un gasto ajeno dé 404, igual que uno inexistente.
    gasto = get_object_or_404(Gasto, pk=pk, usuario=request.user)
    gasto.delete()
    messages.success(request, "Gasto eliminado.")
    return redirect("lista_gastos")


@login_required
def lista_metas(request):
    if request.method == "POST":
        formulario = FormularioMeta(request.POST)
        if formulario.is_valid():
            meta = formulario.save(commit=False)
            meta.usuario = request.user
            meta.save()
            messages.success(request, "Meta creada.")
            return redirect("lista_metas")
    else:
        formulario = FormularioMeta()

    hoy = timezone.localdate()
    metas = list(Meta.objects.filter(usuario=request.user))
    for meta in metas:
        meta.cuota = calcular_cuota_mensual(meta.precio, meta.ahorrado, meta.fecha_limite, hoy)
        meta.falta = calcular_falta(meta.precio, meta.ahorrado)
        meta.meses = meses_restantes(meta.fecha_limite, hoy)
        meta.estado = estado_meta(meta.precio, meta.ahorrado, meta.fecha_limite, hoy)
        meta.estado_nombre = NOMBRES_ESTADO[meta.estado]
    return render(request, "gastos/metas.html", {"formulario": formulario, "metas": metas})


@login_required
@require_POST
def eliminar_meta(request, pk):
    meta = get_object_or_404(Meta, pk=pk, usuario=request.user)
    meta.delete()
    messages.success(request, "Meta eliminada.")
    return redirect("lista_metas")


@login_required
@require_safe
def hormiga(request):
    gastos = Gasto.objects.filter(usuario=request.user)
    grupos = detectar_gasto_hormiga(
        gastos,
        settings.GASTO_HORMIGA_UMBRAL,
        settings.GASTO_HORMIGA_N,
        timezone.localdate(),
    )
    nombres_categoria = dict(Gasto.Categoria.choices)
    for grupo in grupos:
        # Si el código no está entre las opciones, se muestra tal cual.
        grupo["categoria_nombre"] = nombres_categoria.get(
            grupo["categoria"], grupo["categoria"]
        )
    contexto = {
        "grupos": grupos,
        "umbral": settings.GASTO_HORMIGA_UMBRAL,
        "n": settings.GASTO_HORMIGA_N,
        "dias": VENTANA_DIAS,
    }
    return render(request, "gastos/hormiga.html", contexto)
