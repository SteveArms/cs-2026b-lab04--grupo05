from datetime import datetime
from uuid import uuid4
import pytest

from votacion.estados import Eleccion, Opcion
from votacion.externos import ProveedorIdentidadSDK
from votacion.servicio import ServicioVotacion, Votante

INICIO = datetime(2026, 11, 20, 8, 0)
FIN = datetime(2026, 11, 20, 16, 0)


def test_doble_voto_con_diferencia_de_mayusculas_y_espacios():
    """ISSUE-01: No debe permitirse emitir doble voto al variar mayúsculas o espacios en el código."""
    idp = ProveedorIdentidadSDK(tokens={"tok-alumno": "alumno@unsa.edu.pe"})
    servicio = ServicioVotacion(idp=idp)
    eleccion = Eleccion(nombre="Eleccion Delegados", fin=FIN)
    op_a = Opcion(id=uuid4(), etiqueta="Lista A")
    op_b = Opcion(id=uuid4(), etiqueta="Lista B")
    eleccion.opciones = [op_a, op_b]
    servicio.abrir(eleccion)

    v1 = Votante(correo="alumno@unsa.edu.pe", codigo="20221234a", habilitado=True)
    v2 = Votante(correo="alumno@unsa.edu.pe", codigo=" 20221234A ", habilitado=True)

    # Primer voto exitoso
    codigo = servicio.emitir_voto(v1, eleccion, op_a.id, "OIDC", "tok-alumno")
    assert codigo is not None
    assert len(servicio.urna) == 1

    # Segundo voto con el mismo código pero con espacios y mayúsculas debe ser rechazado
    with pytest.raises(ValueError, match="Ya emitiste tu voto"):
        servicio.emitir_voto(v2, eleccion, op_b.id, "OIDC", "tok-alumno")
