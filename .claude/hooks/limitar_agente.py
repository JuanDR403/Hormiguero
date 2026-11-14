"""Hook PreToolUse: limita lo que cada agente puede escribir y ejecutar.

Uso (desde el encabezado de un agente):
    python "$CLAUDE_PROJECT_DIR/.claude/hooks/limitar_agente.py" <rol>

Lee por la entrada estándar el JSON que envía Claude Code. Si la acción no
está permitida para el rol, termina con código 2 y explica el motivo por la
salida de error; Claude Code bloquea la herramienta y le muestra el motivo
al agente.
"""

import json
import os
import sys

TEST = "python manage.py test"
CHECK = "python manage.py check"
MIGRACIONES_CHECK = "python manage.py makemigrations --check"
GIT_LECTURA = ("git status", "git diff", "git log")

# escribe: prefijos de ruta permitidos. no_escribe: excepciones dentro de ellos.
# bash: prefijos de comando permitidos.
ROLES = {
    "coordinador": {
        "escribe": ("specs/",),
        "no_escribe": (),
        "bash": GIT_LECTURA + ("git switch", "git add", "git commit"),
    },
    "probador": {
        "escribe": ("gastos/tests/",),
        "no_escribe": (),
        "bash": (TEST,),
    },
    "implementador-backend": {
        "escribe": ("gastos/", "config/settings.py"),
        "no_escribe": ("gastos/tests/", "gastos/migrations/"),
        "bash": (TEST, CHECK, "python manage.py makemigrations"),
    },
    "implementador-frontend": {
        "escribe": ("templates/", "static/"),
        "no_escribe": (),
        "bash": (
            TEST,
            "curl -s http://localhost:8000/",
            "curl -s http://127.0.0.1:8000/",
        ),
    },
    "revisor": {
        "escribe": (),
        "no_escribe": (),
        "bash": GIT_LECTURA
        + (TEST, CHECK, MIGRACIONES_CHECK, "coverage run", "coverage report"),
    },
}

# Con esto se encadenan o redirigen comandos; ningún agente lo necesita.
PROHIBIDO_EN_BASH = (";", "&", "|", ">", "<", "`", "$(", "\n")


def ruta_relativa(ruta, raiz):
    """Ruta relativa a la raíz del proyecto, con '/' y sin '..'."""
    absoluta = os.path.normpath(os.path.join(raiz, ruta))
    relativa = os.path.relpath(absoluta, raiz)
    return relativa.replace(os.sep, "/")


def motivo_de_rechazo(rol, herramienta, entrada, raiz):
    """Devuelve el motivo del rechazo, o None si la acción está permitida."""
    reglas = ROLES.get(rol)
    if reglas is None:
        return f"Rol desconocido: {rol}."

    if herramienta in ("Edit", "Write", "NotebookEdit"):
        ruta = entrada.get("file_path") or entrada.get("notebook_path") or ""
        relativa = ruta_relativa(ruta, raiz)
        if relativa.startswith(".."):
            return f"{rol} no puede escribir fuera del proyecto."
        if any(relativa.startswith(p) for p in reglas["no_escribe"]):
            return f"{rol} no puede escribir en {relativa}."
        if not any(relativa.startswith(p) for p in reglas["escribe"]):
            permitido = ", ".join(reglas["escribe"]) or "ninguna carpeta"
            return f"{rol} solo puede escribir en: {permitido}. Rechazado: {relativa}."
        return None

    if herramienta == "Bash":
        comando = " ".join((entrada.get("command") or "").split())
        if (entrada.get("command") or "").strip().count("\n"):
            return "Un solo comando por llamada."
        if any(simbolo in comando for simbolo in PROHIBIDO_EN_BASH):
            return "No se permite encadenar ni redirigir comandos."
        if comando.startswith(".venv/bin/"):
            comando = comando[len(".venv/bin/"):]
        if comando.startswith("git push") or " --force" in comando:
            return "Ningún agente hace push ni fuerza cambios."
        if not any(comando.startswith(p) for p in reglas["bash"]):
            permitido = "; ".join(reglas["bash"])
            return f"{rol} solo puede ejecutar: {permitido}."
        return None

    return None


def main():
    rol = sys.argv[1] if len(sys.argv) > 1 else ""
    datos = json.load(sys.stdin)
    raiz = os.environ.get("CLAUDE_PROJECT_DIR") or datos.get("cwd") or os.getcwd()
    motivo = motivo_de_rechazo(
        rol, datos.get("tool_name", ""), datos.get("tool_input") or {}, raiz
    )
    if motivo:
        print(motivo, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
