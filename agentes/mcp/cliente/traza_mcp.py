"""Mide la traza JSONL del espía y genera una secuencia Mermaid."""
import argparse
import json
from collections import defaultdict
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]


def leer_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def emparejar(eventos):
    pendientes = {}
    for evento in eventos:
        msg = evento['msg']
        if 'id' not in msg:
            continue
        if evento['dir'] == 'host->servidor' and 'method' in msg:
            pendientes[msg['id']] = evento
        elif evento['dir'] == 'servidor->host' and msg['id'] in pendientes:
            yield pendientes.pop(msg['id']), evento


def catalogo(eventos):
    for solicitud, respuesta in emparejar(eventos):
        if solicitud['msg']['method'] == 'tools/list':
            return respuesta['msg']['result']['tools']
    raise ValueError('La traza no contiene una respuesta tools/list')


def secuencia(pares, aprobaciones):
    lineas = ['sequenceDiagram', '    participant U as Revisor', '    participant H as Analista',
              '    participant S as VotoEPIS']
    for solicitud, respuesta in pares:
        msg = solicitud['msg']
        metodo = msg['method']
        params = msg.get('params', {})
        nombre = params.get('name')
        args = params.get('arguments', {})
        if any(a['accion'] == nombre and a['args'] == args and a['decision'] == 'APROBADA'
               for a in aprobaciones):
            lineas.extend(['    H->>U: Solicita aprobación de escritura', '    U-->>H: Aprueba la observación'])
        detalle = ' '.join(filter(None, (nombre, args.get('eleccion_id'), params.get('uri'))))
        lineas.append(f'    H->>S: {metodo} {detalle}'.rstrip())
        cuerpo = respuesta['msg']
        resultado = cuerpo.get('result', {})
        datos = resultado.get('structuredContent', {})
        resumen = 'Respuesta'
        if 'error' in cuerpo:
            resumen = 'Error JSON-RPC'
        elif resultado.get('isError'):
            resumen = 'Error de herramienta. El agente corrige el argumento.'
        elif metodo == 'tools/list':
            resumen = f"{len(resultado['tools'])} herramientas"
        elif 'participacion' in datos:
            resumen = f"{datos['estado']}. Participación {datos['participacion']}"
        elif nombre == 'registrar_observacion':
            resumen = 'Observación creada'
        lineas.append(f'    S-->>H: {resumen}')
    return '\n'.join(lineas) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('traza', type=Path, nargs='?', default=LAB / 'trazas/mcp_trafico.jsonl')
    parser.add_argument('--aprobaciones', type=Path, default=LAB / 'trazas/aprobaciones_mcp.jsonl')
    parser.add_argument('--diagrama', type=Path)
    args = parser.parse_args()
    eventos = leer_jsonl(args.traza)
    pares = list(emparejar(eventos))
    latencias = defaultdict(list)
    for solicitud, respuesta in pares:
        latencias[solicitud['msg']['method']].append(respuesta['t_ms'] - solicitud['t_ms'])
    print(f"Mensajes: {len(eventos)} | Bytes: {sum(e['bytes'] for e in eventos)}")
    print(f"Errores de herramienta: {sum(bool(e['msg'].get('result', {}).get('isError')) for e in eventos)}")
    print(f"Errores JSON-RPC: {sum('error' in e['msg'] for e in eventos)}")
    for metodo, tiempos in latencias.items():
        print(f"{metodo} ({len(tiempos)}): {', '.join(f'{t:.2f}' for t in tiempos)} ms")
    if args.diagrama:
        args.diagrama.write_text(secuencia(pares, leer_jsonl(args.aprobaciones)), encoding='utf-8')


if __name__ == '__main__':
    main()
