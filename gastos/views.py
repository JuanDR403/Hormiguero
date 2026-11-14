from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST, require_safe

from .forms import FormularioGasto, FormularioRegistro
from .models import Gasto
from .reglas.hormiga import VENTANA_DIAS, detectar_gasto_hormiga


def inicio(request):
    return render(request, "inicio.html")


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
