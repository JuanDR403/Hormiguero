from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .forms import FormularioIngreso

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="autenticacion/login.html",
            authentication_form=FormularioIngreso,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("registro/", views.registro, name="registro"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
