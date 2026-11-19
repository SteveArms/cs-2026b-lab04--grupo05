"""Herramientas del agente. Cada una es una función pequeña, con descripción y parámetros explícitos.
Todas operan DENTRO del directorio de trabajo (sandbox)."""
import pathlib, subprocess, re, sys


class Herramientas:
    def __init__(self, raiz: str):
        self.raiz = pathlib.Path(raiz).resolve()

    # --- utilidades ---
    def _ruta(self, ruta: str) -> pathlib.Path:
        p = (self.raiz / ruta).resolve()
        if self.raiz not in p.parents and p != self.raiz:
            raise PermissionError(f"Ruta fuera del sandbox: {ruta}")
        return p

    def catalogo(self) -> dict:
        """Descripción de las herramientas que se envía al modelo (como en un MCP server)."""
        return {
            "listar_archivos": "listar_archivos(carpeta='.'): lista los archivos .py y .md",
            "leer_archivo": "leer_archivo(ruta): devuelve el contenido con números de línea",
            "buscar": "buscar(patron): busca una expresión regular en los archivos .py",
            "ejecutar_pruebas": "ejecutar_pruebas(ruta=''): ejecuta pytest sobre el repositorio o una prueba específica",
            "editar_archivo": "editar_archivo(ruta, antes, despues): reemplaza un fragmento exacto (una sola vez)",
            "ver_cambios": "ver_cambios(): muestra el diff respecto de la versión de git en src/",
            "ejecutar_comando": "ejecutar_comando(comando): ejecuta un comando de shell (sujeto a la política)",
            "mapa_repo": "mapa_repo(carpeta='src'): extrae el mapa AST jerárquico de clases y funciones sin cuerpo",
            "anotar": "anotar(texto): agrega una nota de hipótesis a la memoria externa persistente",
            "leer_notas": "leer_notas(): devuelve las notas registradas en la memoria externa",
        }

    # --- herramientas ---
    def listar_archivos(self, carpeta="."):
        base = self._ruta(carpeta)
        return "\n".join(sorted(str(p.relative_to(self.raiz)) for p in base.rglob("*")
                                if p.suffix in (".py", ".md") and "__pycache__" not in p.parts))

    def leer_archivo(self, ruta):
        lineas = self._ruta(ruta).read_text(encoding="utf-8").splitlines()
        return "\n".join(f"{i:3d}| {l}" for i, l in enumerate(lineas, 1))

    def buscar(self, patron):
        rx, hallazgos = re.compile(patron), []
        for p in sorted(self.raiz.rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            for i, l in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                if rx.search(l):
                    hallazgos.append(f"{p.relative_to(self.raiz)}:{i}: {l.strip()}")
        return "\n".join(hallazgos) or "(sin resultados)"

    def ejecutar_pruebas(self, ruta=""):
        cmd = [sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider"]
        if ruta:
            p_rel = str(self._ruta(ruta).relative_to(self.raiz))
            cmd.append(p_rel)
        r = subprocess.run(cmd, cwd=self.raiz, capture_output=True, text=True, timeout=120)
        salida = (r.stdout + r.stderr).strip().splitlines()
        fallos = [l for l in salida if l.startswith(("FAILED", "E "))][:6]
        return "\n".join(fallos + salida[-1:])

    def editar_archivo(self, ruta, antes, despues):
        p = self._ruta(ruta)
        texto = p.read_text(encoding="utf-8")
        if texto.count(antes) != 1:
            return f"ERROR: el fragmento aparece {texto.count(antes)} veces; debe aparecer exactamente 1"
        p.write_text(texto.replace(antes, despues), encoding="utf-8")
        return f"OK: {ruta} modificado"

    def ver_cambios(self):
        r = subprocess.run(["git", "diff", "src/"], cwd=self.raiz, capture_output=True, text=True, timeout=30)
        return r.stdout.strip() or "(sin cambios)"

    def _ruta_libre(self, ruta):
        return (self.raiz / ruta).resolve()

    def ejecutar_comando(self, comando):
        r = subprocess.run(comando, shell=True, cwd=self.raiz, capture_output=True, text=True, timeout=60)
        return (r.stdout + r.stderr).strip()[-2000:]

    def mapa_repo(self, carpeta="src"):
        import ast
        base = self._ruta(carpeta)
        lineas = []
        for p in sorted(base.rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            try:
                tree = ast.parse(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            rel = str(p.relative_to(self.raiz))
            elementos = []
            for nodo in tree.body:
                if isinstance(nodo, ast.ClassDef):
                    elementos.append(f"  class {nodo.name}:")
                    for sub in nodo.body:
                        if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            args_str = ", ".join(a.arg for a in sub.args.args)
                            elementos.append(f"    def {sub.name}({args_str})")
                elif isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    args_str = ", ".join(a.arg for a in nodo.args.args)
                    elementos.append(f"  def {nodo.name}({args_str})")
            if elementos:
                lineas.append(f"{rel}:")
                lineas.extend(elementos)
        return "\n".join(lineas) if lineas else "(sin simbolos)"

    def anotar(self, texto: str) -> str:
        p = self._ruta("agentes/notas.md")
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(f"- {texto.strip()}\n")
        return "OK: nota guardada"

    def leer_notas(self) -> str:
        p = self._ruta("agentes/notas.md")
        if not p.exists():
            return "(sin notas)"
        return p.read_text(encoding="utf-8").strip() or "(sin notas)"
