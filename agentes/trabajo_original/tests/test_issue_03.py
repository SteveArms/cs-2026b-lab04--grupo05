from datetime import datetime, timedelta
from uuid import uuid4
import pytest

from votacion.estados import Eleccion, Opcion
from votacion.servicio import ServicioVotacion

INICIO = datetime(2026, 11, 20, 8, 0)
FIN = datetime(2026, 11, 20, 16, 0)


def test_cerrar_mesa_antes_de_la_hora_de_fin_debe_fallar():
    """ISSUE-03: No se debe permitir cerrar la mesa antes de la hora oficial de fin."""
    servicio = ServicioVotacion()
    eleccion = Eleccion(nombre="Eleccion Delegados", fin=FIN)
    op_a = Opcion(id=uuid4(), etiqueta="Lista 1")
    op_b = Opcion(id=uuid4(), etiqueta="Lista 2")
    eleccion.opciones = [op_a, op_b]
    servicio.abrir(eleccion)

    # Intento de cierre a las 14:00 (2 horas antes del fin oficial de las 16:00)
    hora_prematura = FIN - timedelta(hours=2)

    with pytest.raises(ValueError, match="Aún no culmina la ventana de votación"):
        servicio.cerrar_mesa(eleccion, ahora=hora_prematura)

    # La elección debe permanecer ABIERTA
    assert eleccion.estado == "ABIERTA"
