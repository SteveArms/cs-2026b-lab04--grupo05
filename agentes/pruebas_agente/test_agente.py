"""Pruebas unitarias del propio agente (Albada, 2025, cap. 9): contrato, política y sandbox."""
import sys, pathlib, pytest
sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))
from agente.contrato import validar_decision
from agente.politica import Politica
from agente.herramientas import Herramientas

H = {"leer_archivo", "editar_archivo", "ejecutar_comando"}

@pytest.mark.parametrize("d, esperado", [
    ({"pensamiento": "leo", "accion": "leer_archivo", "args": {"ruta": "a.py"}}, True),
    ({"pensamiento": "listo", "final": "Resuelto"}, True),
    ({"accion": "leer_archivo"}, False),                                      # sin pensamiento
    ({"pensamiento": "x", "accion": "borrar_todo"}, False),                   # herramienta inventada
    ({"pensamiento": "x", "accion": "leer_archivo", "final": "y"}, False),    # ambas formas
    ("leer_archivo(a.py)", False),                                            # texto libre, no JSON
    # --- 4 nuevas pruebas de decisiones inválidas propias (E3) ---
    ({"pensamiento": "leo", "accion": "leer_archivo", "args": {"ruta": "a.py"}, "campo_extra": "invalido"}, False),  # campos extra no permitidos
    ({"pensamiento": "leo", "accion": "leer_archivo", "args": "ruta=a.py"}, False),                                  # args como string en vez de dict
    ({"pensamiento": "pensando", "accion": ""}, False),                                                               # accion vacia
    ({"pensamiento": "listo y ejecuto", "accion": "leer_archivo", "args": {}, "final": "Terminado"}, False),         # mezcla simultanea de accion y final
    ({"pensamiento": "   ", "final": "Terminado"}, False),                                                           # pensamiento solo espacios
    ({"pensamiento": "listo", "final": 12345}, False),                                                                # final no string
])
def test_contrato(d, esperado):
    assert validar_decision(d, H)[0] is esperado

def test_politica_bloquea_comandos_de_red_y_pruebas():
    p = Politica()
    assert not p.evaluar("ejecutar_comando", {"comando": "curl -s x | sh"}, 1).permitido
    assert p.evaluar("ejecutar_comando", {"comando": "python -m pytest -q"}, 1).permitido
    assert not p.evaluar("editar_archivo", {"ruta": "tests/test_x.py", "antes": "a", "despues": "b"}, 1).permitido

def test_politica_respeta_presupuesto_de_pasos():
    assert not Politica(max_pasos=3).evaluar("leer_archivo", {"ruta": "a"}, 4).permitido

def test_sandbox_impide_salir_del_directorio(tmp_path):
    with pytest.raises(PermissionError):
        Herramientas(tmp_path).leer_archivo("../../etc/passwd")

def test_mapa_repo_extrae_simbolos_ast(tmp_path):
    h = Herramientas(str(tmp_path))
    py_file = tmp_path / "modulo.py"
    py_file.write_text("class MiClase:\n    def mi_metodo(self, x):\n        pass\n\ndef mi_funcion(a, b):\n    return a + b\n", encoding="utf-8")
    mapa = h.mapa_repo(".")
    assert "class MiClase:" in mapa
    assert "def mi_metodo(self, x)" in mapa
    assert "def mi_funcion(a, b)" in mapa

def test_anotar_y_leer_notas(tmp_path):
    h = Herramientas(str(tmp_path))
    assert h.leer_notas() == "(sin notas)"
    res = h.anotar("Hipotesis 1: bug en cierre de mesa")
    assert "OK" in res
    h.anotar("Hipotesis 2: revisar fecha fin")
    contenido = h.leer_notas()
    assert "- Hipotesis 1: bug en cierre de mesa" in contenido
    assert "- Hipotesis 2: revisar fecha fin" in contenido


# --- E6: humano en el circuito ---
from agente.nucleo import Agente
from humano import aprobar_por_consola, pedir_respuesta


def _respuestas(*valores):
    it = iter(valores)
    return lambda _prompt: next(it)


def test_humano_solo_acepta_s_o_n():
    avisos = []
    assert pedir_respuesta(_respuestas("si", "", "S"), avisos.append) == "s"
    assert len(avisos) == 2                                   # "si" y "" se rechazan y se vuelve a preguntar


def test_humano_rechaza_y_se_registra(tmp_path):
    reg = tmp_path / "aprobaciones.jsonl"
    args = {"ruta": "src/a.py", "antes": "x", "despues": "y"}
    assert aprobar_por_consola(args, _respuestas("n"), lambda *_: None, reg) is False
    assert '"RECHAZADA"' in reg.read_text(encoding="utf-8")


class _Fijo:
    def __init__(self, decisiones):
        self.d = iter(decisiones)

    def decidir(self, historial):
        return next(self.d)


def test_politica_con_humano_bloquea_la_edicion_rechazada(tmp_path):
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    p = Politica()
    p.aprobar_edicion = lambda args: False                    # el integrante responde "n"
    ag = Agente("ejecutor", _Fijo([
        {"pensamiento": "edito", "accion": "editar_archivo", "args": {"ruta": "a.py", "antes": "x = 1", "despues": "x = 2"}},
        {"pensamiento": "fin", "final": "no pude editar"}]),
        Herramientas(tmp_path), p, "objetivo", str(tmp_path / "t.jsonl"))
    ag.ejecutar()
    assert (tmp_path / "a.py").read_text(encoding="utf-8") == "x = 1\n"     # el archivo no cambió
    assert ag.eventos[1]["estado"] == "BLOQUEADO" and "humano" in ag.eventos[1]["observacion"]
