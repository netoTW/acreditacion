"""
Quiz formativo — la mecánica de juego dentro del módulo.

Se juega distinto a la evaluación final, a propósito (S-07): feedback inmediato,
racha visible y XP con multiplicador. Es para aprender, no para acreditar.

Dos decisiones que lo mantienen inofensivo para el invariante:

1. **El XP del quiz es lúdico**, nunca acreditable (S-04). Así jugar no mueve el
   escalón ni acerca a nadie a una medalla. La base lo impone: hay un CHECK que
   prohíbe `clase_xp='acreditable'` con `origen_tipo='juego'`.
2. **El puntaje lo calcula el servidor** a partir de las respuestas, no lo informa
   el cliente. Si el cliente propusiera su propio XP, el tope diario y la racha
   serían decorativos.

Y se paga una vez al día por módulo: repetir el quiz es práctica, no una fuente.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from .eventos import registrar_evento

XP_BASE = 20          # mismos números que la trivia de la cáscara
XP_POR_RACHA = 10


@dataclass(frozen=True)
class ResultadoQuiz:
    total: int
    aciertos: int
    mejor_racha: int
    xp_otorgado: int
    ya_jugado_hoy: bool
    detalle: list[dict]


def puntuar_quiz(conn, *, colaborador_id: UUID, modulo_id: UUID,
                 respuestas: list[dict]) -> ResultadoQuiz:
    """
    `respuestas` viene EN EL ORDEN EN QUE SE CONTESTÓ: la racha depende del orden.
    """
    correctas = {
        f[0]: f[1]
        for f in conn.execute(
            "SELECT id, indice_correcta FROM item_quiz_formativo WHERE modulo_id = %s",
            (modulo_id,),
        ).fetchall()
    }
    if not correctas:
        raise LookupError("ese módulo no tiene quiz formativo")

    racha = 0
    mejor_racha = 0
    aciertos = 0
    xp = 0
    detalle: list[dict] = []

    for r in respuestas:
        item_id = r["item_id"]
        if item_id not in correctas:
            continue                      # ítem que no es de este módulo: se ignora
        acerto = correctas[item_id] == r["indice_elegido"]
        if acerto:
            racha += 1
            mejor_racha = max(mejor_racha, racha)
            aciertos += 1
            xp += XP_BASE + racha * XP_POR_RACHA
        else:
            racha = 0
        detalle.append({"item_id": item_id, "acerto": acerto, "racha": racha})

    # Una vez al día por módulo. Repetirlo sirve para practicar, no para sumar.
    evento = registrar_evento(
        conn,
        colaborador_id=colaborador_id,
        tipo="quiz_formativo_jugado",
        origen_tipo="juego",
        origen_id=modulo_id,
        xp=xp,
        clase_xp="ludico",
        clave_idempotencia=f"quiz:{colaborador_id}:{modulo_id}:{date.today().isoformat()}",
    )

    return ResultadoQuiz(
        total=len(correctas),
        aciertos=aciertos,
        mejor_racha=mejor_racha,
        # registrar_evento devuelve None si ya se pagó hoy o si el tope diario de
        # XP lúdico está agotado (S-05).
        xp_otorgado=xp if evento else 0,
        ya_jugado_hoy=evento is None,
        detalle=detalle,
    )
