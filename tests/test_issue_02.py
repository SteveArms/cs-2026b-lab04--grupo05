from datetime import datetime
from uuid import uuid4
import pytest

from votacion.estados import Eleccion, Opcion
from votacion.externos import ProveedorIdentidadSDK
from votacion.servicio import ServicioVotacion, Votante

INICIO = datetime(2026, 11, 20, 8, 0)
FIN = datetime(2026, 11, 20, 16, 0)


def test_conteo_votos_validos_no_debe_incluir_blancos_ni_nulos():
    """ISSUE-02: Los votos en blanco y nulos no deben sumarse a candidatos en el escrutinio."""
    tokens = {f"tok-{i}": f"v_{i}@unsa.edu.pe" for i in range(25)}
    idp = ProveedorIdentidadSDK(tokens=tokens)
    servicio = ServicioVotacion(idp=idp)

    eleccion = Eleccion(nombre="Eleccion General", fin=FIN)
    lista_a = Opcion(id=uuid4(), etiqueta="Lista A")
    lista_b = Opcion(id=uuid4(), etiqueta="Lista B")
    blanco = Opcion(id=uuid4(), etiqueta="Voto en Blanco")
    nulo = Opcion(id=uuid4(), etiqueta="Voto Nulo")
    eleccion.opciones = [lista_a, lista_b, blanco, nulo]
    servicio.abrir(eleccion)

    # 10 votos para Lista A
    for i in range(10):
        v = Votante(correo=f"v_{i}@unsa.edu.pe", habilitado=True)
        servicio.emitir_voto(v, eleccion, lista_a.id, "OIDC", f"tok-{i}")

    # 8 votos para Lista B
    for i in range(10, 18):
        v = Votante(correo=f"v_{i}@unsa.edu.pe", habilitado=True)
        servicio.emitir_voto(v, eleccion, lista_b.id, "OIDC", f"tok-{i}")

    # 5 votos en blanco
    for i in range(18, 23):
        v = Votante(correo=f"v_{i}@unsa.edu.pe", habilitado=True)
        servicio.emitir_voto(v, eleccion, blanco.id, "OIDC", f"tok-{i}")

    # 2 votos nulos
    for i in range(23, 25):
        v = Votante(correo=f"v_{i}@unsa.edu.pe", habilitado=True)
        servicio.emitir_voto(v, eleccion, nulo.id, "OIDC", f"tok-{i}")

    # Cómputo de votos válidos
    validos = servicio.computar_votos_validos(eleccion)

    # El resultado debe tener exactamente los votos de candidatos legítimos
    assert validos == {
        "Lista A": 10,
        "Lista B": 8,
    }, f"Conteo erróneo de votos válidos: {validos}"
