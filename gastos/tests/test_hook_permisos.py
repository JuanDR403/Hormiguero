import importlib.util
import re
from pathlib import Path

from django.test import SimpleTestCase

RAIZ = Path(__file__).resolve().parent.parent.parent
RUTA_HOOK = RAIZ / ".claude" / "hooks" / "limitar_agente.py"
CARPETA_AGENTES = RAIZ / ".claude" / "agents"

especificacion = importlib.util.spec_from_file_location("limitar_agente", RUTA_HOOK)
hook = importlib.util.module_from_spec(especificacion)
especificacion.loader.exec_module(hook)


def bash(rol, comando, quien_llama=None):
    datos = {"tool_name": "Bash", "tool_input": {"command": comando}}
    if quien_llama:
        datos["agent_type"] = quien_llama
    return hook.decidir(rol, datos, str(RAIZ))


def escribir(rol, ruta, quien_llama=None):
    datos = {"tool_name": "Write", "tool_input": {"file_path": ruta}}
    if quien_llama:
        datos["agent_type"] = quien_llama
    return hook.decidir(rol, datos, str(RAIZ))


class CarpetasPorRolTests(SimpleTestCase):
    def test_probador_solo_escribe_pruebas(self):
        self.assertIsNone(escribir("probador", "gastos/tests/test_x.py"))
        self.assertIsNotNone(escribir("probador", "gastos/reglas/x.py"))

    def test_backend_no_escribe_pruebas_ni_migraciones(self):
        self.assertIsNone(escribir("implementador-backend", "gastos/views.py"))
        self.assertIsNone(escribir("implementador-backend", "config/settings.py"))
        self.assertIsNotNone(escribir("implementador-backend", "gastos/tests/test_x.py"))
        self.assertIsNotNone(
            escribir("implementador-backend", "gastos/migrations/0001_initial.py")
        )

    def test_frontend_no_escribe_en_gastos_ni_saliendo_con_puntos(self):
        self.assertIsNone(escribir("implementador-frontend", "templates/x.html"))
        self.assertIsNotNone(escribir("implementador-frontend", "gastos/views.py"))
        self.assertIsNotNone(
            escribir("implementador-frontend", "templates/../gastos/views.py")
        )

    def test_revisor_no_escribe_nada(self):
        self.assertIsNotNone(escribir("revisor", "specs/001-x/spec.md"))

    def test_coordinador_solo_escribe_specs(self):
        self.assertIsNone(escribir("coordinador", "specs/001-x/spec.md"))
        self.assertIsNotNone(escribir("coordinador", ".claude/hooks/limitar_agente.py"))

    def test_ruta_absoluta_fuera_del_proyecto_se_rechaza(self):
        self.assertIsNotNone(escribir("probador", "/tmp/test_x.py"))


class ComandosPorRolTests(SimpleTestCase):
    def test_cada_rol_ejecuta_solo_lo_suyo(self):
        self.assertIsNone(bash("probador", "python manage.py test gastos.tests"))
        self.assertIsNotNone(bash("probador", "git status"))
        self.assertIsNone(bash("revisor", "coverage report"))
        self.assertIsNone(bash("implementador-backend", "coverage run manage.py test"))
        self.assertIsNone(bash("implementador-backend", "coverage report"))
        self.assertIsNotNone(bash("probador", "coverage report"))
        self.assertIsNone(bash("coordinador", "git ls-files gastos"))
        self.assertIsNone(bash("revisor", "git ls-files"))
        self.assertIsNotNone(bash("probador", "git ls-files"))
        self.assertIsNone(bash("coordinador", "git pull --ff-only"))
        self.assertIsNotNone(bash("coordinador", "python manage.py test"))

    def test_nadie_hace_push(self):
        for rol in hook.ROLES:
            with self.subTest(rol=rol):
                self.assertIsNotNone(bash(rol, "git push origin main"))

    def test_no_se_encadena_ni_se_redirige(self):
        for comando in (
            "git status ; rm -rf gastos",
            "git status && rm -rf gastos",
            "git status | sh",
            "git log > salida.txt",
            "git status\nrm -rf gastos",
            "git commit -m $(rm -rf gastos)",
            "git commit -m `rm -rf gastos`",
            'git commit -m "x $(rm -rf gastos)"',
        ):
            with self.subTest(comando=comando):
                self.assertIsNotNone(bash("coordinador", comando))

    def test_comilla_escapada_no_esconde_un_segundo_comando(self):
        for comando in (
            "git status \\' ; rm -rf gastos ; \\'",
            'git status \\" ; rm -rf gastos ; \\"',
            "git commit -m 'a\\' ; rm -rf gastos ; echo 'b'",
        ):
            with self.subTest(comando=comando):
                self.assertIsNotNone(bash("coordinador", comando))

    def test_comillas_sin_cerrar_se_rechazan(self):
        self.assertIsNotNone(bash("coordinador", "git commit -m 'sin cerrar"))
        self.assertIsNotNone(bash("coordinador", 'git commit -m "sin cerrar'))

    def test_mensaje_de_commit_admite_saltos_y_correo(self):
        mensaje = 'git commit -m "docs: spec 001\n\nCo-Authored-By: Ana <ana@ejemplo.com>"'
        self.assertIsNone(bash("coordinador", mensaje))
        self.assertIsNone(bash("coordinador", "git commit -m 'fix: a; b' -m 'c > d'"))


class QuienLlamaTests(SimpleTestCase):
    def test_el_hook_de_otro_agente_con_perfil_no_juzga(self):
        self.assertIsNone(bash("coordinador", "python manage.py test", "probador"))

    def test_el_hook_propio_si_juzga(self):
        self.assertIsNotNone(bash("probador", "git status", "probador"))
        self.assertIsNotNone(bash("coordinador", "python manage.py test", "coordinador"))

    def test_agente_sin_perfil_no_escribe_ni_ejecuta(self):
        self.assertIsNotNone(bash("coordinador", "git status", "general-purpose"))
        self.assertIsNotNone(escribir("coordinador", "specs/x.md", "general-purpose"))

    def test_rol_desconocido_se_rechaza(self):
        self.assertIsNotNone(bash("inventado", "git status"))


class AgentesDeclaranSuHookTests(SimpleTestCase):
    def test_cada_agente_tiene_perfil_y_llama_al_hook_con_su_nombre(self):
        archivos = sorted(CARPETA_AGENTES.glob("*.md"))
        self.assertEqual({a.stem for a in archivos}, set(hook.ROLES))
        for archivo in archivos:
            with self.subTest(agente=archivo.stem):
                texto = archivo.read_text(encoding="utf-8")
                self.assertIn('matcher: "Edit|Write|Bash"', texto)
                roles = re.findall(r"limitar_agente\.py\" ([\w-]+)'", texto)
                self.assertEqual(roles, [archivo.stem])
