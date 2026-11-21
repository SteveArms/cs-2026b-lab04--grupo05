"""Observabilidad: convierte las trazas JSONL en un diagrama de secuencia (Mermaid) y en métricas."""
import json, collections, pathlib, sys

ORDEN = ["planificador", "ejecutor", "revisor", "ejecutor_r2", "revisor_r2", "ejecutor_r3", "revisor_r3"]

def cargar(carpeta="trazas"):
    eventos = []
    for n in ORDEN:
        f = pathlib.Path(carpeta) / f"{n}.jsonl"
        if f.exists():
            ronda = int(n.split("_r")[1]) if "_r" in n else 1
            eventos += [dict(json.loads(l), ronda=ronda) for l in open(f, encoding="utf-8")]
    return eventos

def cargar_archivo(archivo_jsonl):
    return [dict(json.loads(l), ronda=1) for l in open(archivo_jsonl, encoding="utf-8")]

def resumir(e) -> str:
    obs, acc, args = e.get("observacion", ""), e.get("accion", ""), e.get("args", {})
    if acc == "leer_archivo": return f"contenido de {args.get('ruta', '').split('/')[-1]}"
    if acc == "buscar": return "sin resultados" if "sin resultados" in obs else f"{len(obs.splitlines())} coincidencia(s)"
    if acc == "ver_cambios": return f"diff de {len(obs.splitlines())} líneas"
    if acc == "ejecutar_comando" and args.get("comando", "").startswith("radon"): return "complejidad A"
    if acc == "editar_archivo" and obs.startswith("OK"): return "OK, archivo modificado"
    if acc == "mapa_repo": return "mapa AST de src/"
    if acc == "anotar": return "nota guardada"
    if acc == "leer_notas": return "lectura de notas"
    return (obs.strip().splitlines() or [""])[-1].replace(";", ",").replace("#", "N.")[:40]

def a_mermaid(eventos) -> str:
    alias = {"planificador": "PL", "ejecutor": "EJ", "revisor": "RV"}
    agentes_presentes = list(dict.fromkeys(e["agente"] for e in eventos if "agente" in e))
    l = ["sequenceDiagram", "    autonumber", "    actor U as Humano"]
    for ag in agentes_presentes:
        cod = alias.get(ag, ag[:2].upper())
        nombre_vis = "Planificador" if ag == "planificador" else ("Ejecutor" if ag == "ejecutor" else ("Revisor" if ag == "revisor" else ag.capitalize()))
        l.append(f"    participant {cod} as {nombre_vis}")
    l += ["    participant P as Política", "    participant H as Herramientas"]
    ronda_actual = 1
    for e in eventos:
        ag = e.get("agente", "ejecutor")
        cod = alias.get(ag, ag[:2].upper())
        ronda = e.get("ronda", 1)
        if ronda != ronda_actual:
            ronda_actual = ronda
            l.append(f"    Note over {cod},H: Ronda {ronda_actual} del bucle actor-crítico")
        if e["tipo"] == "objetivo":
            l.append(f"    U->>{cod}: objetivo: {e.get('texto', '')[:45]}...")
        elif e["tipo"] == "accion":
            if e.get("estado") == "CONTRATO_INVALIDO":
                l += [f"    {cod}-xP: Decisión inválida (sin 'args')", f"    P--x{cod}: ERROR DE CONTRATO (autocorrección)"]
            elif e.get("bloqueada"):
                l += [f"    {cod}-xP: {e['accion']}", f"    P--x{cod}: BLOQUEADO"]
            else:
                l += [f"    {cod}->>H: {e['accion']}", f"    H-->>{cod}: {resumir(e)}"]
        elif e["tipo"] == "final":
            l.append(f"    {cod}-->>U: {e.get('texto', '')[:50]}...")
    return "\n".join(l)

def metricas(eventos) -> dict:
    m = collections.defaultdict(collections.Counter)
    for e in eventos:
        if e.get("tipo") == "accion":
            m[e.get("agente", "ejecutor")]["bloqueadas" if e.get("bloqueada") else "permitidas"] += 1
            m[e.get("agente", "ejecutor")][e["accion"]] += 1
    return {k: dict(v) for k, v in m.items()}

if __name__ == "__main__":
    if len(sys.argv) > 2:
        entrada, salida = sys.argv[1], sys.argv[2]
        ev = cargar_archivo(entrada)
        pathlib.Path(salida).write_text(a_mermaid(ev), encoding="utf-8")
        print(f"Diagrama Mermaid generado en {salida}")
    else:
        ev = cargar()
        pathlib.Path("trazas/trayectoria.mmd").write_text(a_mermaid(ev), encoding="utf-8")
        print(json.dumps(metricas(ev), ensure_ascii=False, indent=1))
