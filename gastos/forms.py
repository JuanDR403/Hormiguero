from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .reglas.usuarios import normalizar_correo

Usuario = get_user_model()
# El correo se guarda como username, que admite hasta 150 caracteres.
LONGITUD_MAXIMA_CORREO = 150


class FormularioIngreso(AuthenticationForm):
    username = forms.EmailField(
        label="Correo electrónico",
        max_length=LONGITUD_MAXIMA_CORREO,
        widget=forms.EmailInput(attrs={"autofocus": True, "autocomplete": "email"}),
    )
    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )
    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "El correo o la contraseña son incorrectos.",
    }

    def clean_username(self):
        return normalizar_correo(self.cleaned_data["username"])


class FormularioRegistro(forms.Form):
    nombre_completo = forms.CharField(
        label="Nombre completo",
        max_length=150,
        widget=forms.TextInput(attrs={"autofocus": True, "autocomplete": "name"}),
    )
    correo = forms.EmailField(
        label="Correo electrónico",
        max_length=LONGITUD_MAXIMA_CORREO,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    contrasena = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    confirmar_contrasena = forms.CharField(
        label="Confirmar contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def clean_correo(self):
        correo = normalizar_correo(self.cleaned_data["correo"])
        if Usuario.objects.filter(username=correo).exists():
            raise ValidationError("Ya existe una cuenta con este correo.")
        return correo

    def clean(self):
        datos = super().clean()
        contrasena = datos.get("contrasena")
        confirmacion = datos.get("confirmar_contrasena")

        if contrasena and confirmacion and contrasena != confirmacion:
            self.add_error("confirmar_contrasena", "Las contraseñas no coinciden.")
        elif contrasena:
            correo = datos.get("correo", "")
            candidato = Usuario(
                username=correo,
                email=correo,
                first_name=datos.get("nombre_completo", ""),
            )
            try:
                validate_password(contrasena, candidato)
            except ValidationError as error:
                self.add_error("contrasena", error)
        return datos

    def save(self):
        return Usuario.objects.create_user(
            username=self.cleaned_data["correo"],
            email=self.cleaned_data["correo"],
            password=self.cleaned_data["contrasena"],
            first_name=self.cleaned_data["nombre_completo"],
        )
