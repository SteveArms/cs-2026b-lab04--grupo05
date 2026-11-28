"""Datos FICTICIOS de VotoEPIS para el servidor MCP (Lab 11).

No se duplica la lógica de dominio: las elecciones se construyen y los votos se emiten con
el código real de src/votacion (ServicioVotacion, patrón State, Observer). Los votantes son
inventados (correos @votoepis.test) y se autentican con el OTP simulado del comité.
"""
from __future__ import annotations

import pathlib
import sys
from datetime import datetime

RAIZ = pathlib.Path(__file__).resolve().parents[3]            # raíz del repositorio
if str(RAIZ / "src") not in sys.path:
    sys.path.insert(0, str(RAIZ / "src"))

from votacion.estados import Eleccion, Opcion  # noqa: E402
from votacion.externos import OtpComiteSDK  # noqa: E402
from votacion.servicio import ServicioVotacion, Votante  # noqa: E402

REPARTO = {
    "d": {"Lista A": 46, "Lista B": 38, "Voto en Blanco": 10, "Voto Nulo": 6},
    "t": {"Lista Unidad": 17, "Lista Cambio": 14, "Lista Futuro": 6, "Voto en Blanco": 2, "Voto Nulo": 1},
}


def _votantes(prefijo: str) -> list[tuple[str, str, str]]:
    """(correo, código OTP, etiqueta votada) de cada votante ficticio."""
    filas, n = [], 0
    for etiqueta, cantidad in REPARTO[prefijo].items():
        for _ in range(cantidad):
            n += 1
            filas.append((f"{prefijo}{n:04d}@votoepis.test", f"otp-{prefijo}{n}", etiqueta))
    return filas


def _emitir(servicio: ServicioVotacion, eleccion: Eleccion, prefijo: str) -> None:
    for correo, otp, etiqueta in _votantes(prefijo):
        opcion = next(o for o in eleccion.opciones if o.etiqueta == etiqueta)
        servicio.emitir_voto(Votante(correo, codigo=correo.split("@")[0].upper()), eleccion, opcion.id, "OTP", otp)


def construir() -> tuple[ServicioVotacion, dict[str, Eleccion]]:
    """Devuelve el servicio y las elecciones indexadas por su código corto."""
    codigos_otp = {correo: otp for p in REPARTO for correo, otp, _ in _votantes(p)}
    servicio = ServicioVotacion(otp=OtpComiteSDK(codigos_otp))

    def opciones(*listas):
        return [Opcion(e) for e in (*listas, "Voto en Blanco", "Voto Nulo")]

    delegados = Eleccion("Delegados EPIS 2026", opciones("Lista A", "Lista B"), fin=datetime(2026, 11, 13, 16, 0))
    tercio = Eleccion("Tercio estudiantil 2026", opciones("Lista Unidad", "Lista Cambio", "Lista Futuro"),
                      fin=datetime(2026, 12, 4, 16, 0))
    etica = Eleccion("Comité de ética 2027", opciones("Lista Integridad", "Lista Transparencia"),
                     fin=datetime(2027, 3, 12, 16, 0))

    # Delegados: jornada completa -> PUBLICADA
    servicio.abrir(delegados)
    _emitir(servicio, delegados, "d")
    servicio.cerrar(delegados, datetime(2026, 11, 13, 16, 0))
    servicio.escrutar(delegados)
    servicio.firmar_acta(delegados)
    servicio.publicar(delegados)

    # Tercio: jornada en curso -> ABIERTA (el conteo NO se revela, ADR-002)
    servicio.abrir(tercio)
    _emitir(servicio, tercio, "t")

    # Ética: recién configurada -> CONFIGURADA
    return servicio, {"E-2026-DELEGADOS": delegados, "E-2026-TERCIO": tercio, "E-2027-ETICA": etica}
