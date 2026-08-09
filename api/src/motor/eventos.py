"""
Registro de eventos de gamificación.

`evento_gamificacion` es append-only y es la ÚNICA fuente de XP. Nada de XP,
escalón, ranking ni completitud se guarda a mano: todo se deriva de acá
(CLAUDE.md §4.2, §4.3 · ADR-005).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from uuid import UUID

ClaseXP = Literal["acreditable", "ludico"]
OrigenTipo = Literal["modulo", "evaluacion", "medalla", "juego"]

# Tope diario de XP lúdico por colaborador (S-05). Sin esto, "jugar de nuevo"
# es infinito y el ranking pierde sentido.
TOPE_DIARIO_XP_LUDICO = 200


@dataclass(frozen=True)
class Estado:
    xp_acreditable: int
    xp_total: int
    escalon: str
    insignias: int


def registrar_evento(
    conn,
    *,
    colaborador_id: UUID,
    tipo: str,
    origen_tipo: OrigenTipo,
    origen_id: UUID,
    xp: int,
    clase_xp: ClaseXP,
    clave_idempotencia: str,
) -> UUID | None:
    """
    Registra un evento. Devuelve su id, o None si la clave ya existía.

    La idempotencia NO se consulta antes de insertar: se delega en el índice
    único de `clave_idempotencia`. Consultar-y-después-insertar deja una ventana
    de carrera por la que pasan dos eventos de XP para el mismo hecho (S-13).
    """
    if xp < 0:
        raise ValueError("el XP nunca es negativo (CLAUDE.md §4.2)")

    if clase_xp == "acreditable" and origen_tipo == "juego":
        raise ValueError(
            "un juego no puede producir XP acreditable (S-04): "
            "el escalón y la completitud solo derivan de módulos y evaluaciones aprobadas"
        )

    if clase_xp == "ludico" and xp > 0:
        xp = min(xp, _xp_ludico_disponible_hoy(conn, colaborador_id))
        if xp == 0:
            return None

    fila = conn.execute(
        """
        INSERT INTO evento_gamificacion
              (colaborador_id, tipo, origen_tipo, origen_id, xp, clase_xp, clave_idempotencia)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (clave_idempotencia) DO NOTHING
        RETURNING id
        """,
        (colaborador_id, tipo, origen_tipo, origen_id, xp, clase_xp, clave_idempotencia),
    ).fetchone()

    return fila[0] if fila else None


def _xp_ludico_disponible_hoy(conn, colaborador_id: UUID) -> int:
    gastado = conn.execute(
        """
        SELECT COALESCE(SUM(xp), 0)
          FROM evento_gamificacion
         WHERE colaborador_id = %s
           AND clase_xp = 'ludico'
           AND ocurrido_en >= date_trunc('day', now())
        """,
        (colaborador_id,),
    ).fetchone()[0]
    return max(0, TOPE_DIARIO_XP_LUDICO - int(gastado))


def estado(conn, colaborador_id: UUID) -> Estado:
    """Lee el estado DERIVADO. No hay columnas `xp` ni `nivel` que consultar."""
    fila = conn.execute(
        """
        SELECT xp_acreditable, xp_total, escalon, insignias
          FROM estado_colaborador
         WHERE colaborador_id = %s
        """,
        (colaborador_id,),
    ).fetchone()
    if fila is None:
        raise LookupError("colaborador inexistente")
    return Estado(xp_acreditable=int(fila[0]), xp_total=int(fila[1]),
                  escalon=fila[2], insignias=int(fila[3]))
