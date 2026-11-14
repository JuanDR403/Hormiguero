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
import re
import sys

TEST = "python manage.py test"
CHECK = "python manage.py check"
MIGRACIONES_CHECK = "python manage.py makemigrations --check"
GIT_LECTURA = ("git status", "git diff", "git log", "git ls-files")
COBERTURA = ("coverage run", "coverage report")

# escribe: prefijos de ruta permitidos. no_escribe: excepciones dentro de ellos.
# bash: prefijos de comando permitidos.
ROLES = {
    "coordinador": {
        "escribe": ("specs/",),
        "no_escribe": (),
        "bash": GIT_LECTURA
        + ("git fetch", "git pull", "git switch", "git add", "git commit"),
    },
    "probador": {
        "escribe": ("gastos/tests/",),
        "no_escribe": (),
        "bash": (TEST,),
    },
    "implementador-backend": {
        "escribe": ("gastos/", "config/settings.py"),
        "no_escribe": ("gastos/tests/", "gastos/migrations/"),
        "bash": (TEST, CHECK, "python manage.py makemigrations") + COBERTURA,
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
        + (TEST, CHECK, MIGRACIONES_CHECK) + COBERTURA,
    },
}

# Con esto se encadenan o redirigen comandos; ningún agente lo necesita.
PROHIBIDO_EN_BASH = (";", "&", "|", ">", "<")
# Esto ejecuta otro comando incluso dentro de comillas dobles.
SUSTITUCION = ("`", "$(")
TEXTO_ENTRE_COMILLAS = re.compile(r"'[^']*'|\"[^\"]*\"")


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
        original = (entrada.get("command") or "").strip()
        if any(simbolo in original for simbolo in SUSTITUCION):
            return "No se permite ejecutar un comando dentro de otro."
        # Con una barra invertida se escapa una comilla y lo que parece texto
        # entre comillas deja de serlo. Sin barras, las comillas son simples
        # de leer: se abren y se cierran, sin escapes.
        if "\\" in original:
            return "No se permite la barra invertida en los comandos."
        # El texto entre comillas (un mensaje de commit) puede llevar saltos
        # de línea y símbolos como < y >; fuera de las comillas, no.
        sin_comillas = TEXTO_ENTRE_COMILLAS.sub("''", original)
        if "'" in sin_comillas.replace("''", "") or '"' in sin_comillas:
            return "Comillas sin cerrar en el comando."
        if "\n" in sin_comillas:
            return "Un solo comando por llamada."
        if any(simbolo in sin_comillas for simbolo in PROHIBIDO_EN_BASH):
            return "No se permite encadenar ni redirigir comandos."
        comando = " ".join(original.split())
        if comando.startswith(".venv/bin/"):
            comando = comando[len(".venv/bin/"):]
        if comando.startswith("git push") or " --force" in comando:
            return "Ningún agente hace push ni fuerza cambios."
        if not any(comando.startswith(p) for p in reglas["bash"]):
            permitido = "; ".join(reglas["bash"])
            return f"{rol} solo puede ejecutar: {permitido}."
        return None

    return None


def decidir(rol, datos, raiz):
    """Motivo del rechazo de una llamada completa, o None si se permite."""
    herramienta = datos.get("tool_name", "")
    # El hook de un agente abierto con `claude --agent` sigue activo mientras
    # trabajan sus subagentes. Si quien llama es otro agente con perfil, lo
    # juzga su propio hook. Si no tiene perfil, nadie más lo va a juzgar: no
    # puede escribir ni ejecutar nada.
    quien_llama = datos.get("agent_type")
    if quien_llama and quien_llama != rol:
        if quien_llama in ROLES:
            return None
        if herramienta in ("Edit", "Write", "NotebookEdit", "Bash"):
            return f"El agente {quien_llama} no tiene perfil de permisos."
        return None
    return motivo_de_rechazo(rol, herramienta, datos.get("tool_input") or {}, raiz)


def main():
    rol = sys.argv[1] if len(sys.argv) > 1 else ""
    datos = json.load(sys.stdin)
    raiz = os.environ.get("CLAUDE_PROJECT_DIR") or datos.get("cwd") or os.getcwd()
    motivo = decidir(rol, datos, raiz)
    if motivo:
        print(motivo, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
