from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import FormularioRegistro


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
