"""
M1 «Calibre» — el juego de módulo.

No se juega a saber la respuesta: se juega a **saber cuánto sabes**. En cada
ronda se elige alternativa y se declara confianza, y decir «Seguro» y fallar
cuesta puntos. El marcador puede bajar.

Por qué esta mecánica y no otra: cada distractor del banco está escrito para
sonar razonable. Calibre castiga exactamente esa trampa, que es la misma que el
contenido enseña a evitar — confundir *suena bien* con *corresponde*.

Tres reglas que lo mantienen inofensivo para el invariante:

1. **Se alimenta solo del quiz formativo**, nunca del banco de la evaluación. El
   juego muestra la respuesta correcta para dar feedback, y la del banco no puede
   salir del servidor jamás.
2. **El XP es lúdico** (S-04): no mueve el escalón ni acerca a una medalla.
3. **El puntaje lo calcula el servidor**, penalización incluida. Si lo propusiera
   el cliente, la apuesta sería decorativa.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from .eventos import registrar_evento

# La asimetría es el corazón del diseño: arriesgar paga más de lo que rinde ir a
# lo seguro, pero equivocarse arriesgando duele de verdad.
PUNTOS = {
    (True, True): 60,     # dijo "Seguro" y acertó
    (True, False): -40,   # dijo "Seguro" y falló
    (False, True): 25,    # dijo "Creo" y acertó
    (False, False): 0,    # dijo "Creo" y falló
}
BONO_CALIBRADO = 50


@dataclass(frozen=True)
class ResultadoCalibre:
    total: int
    aciertos: int
    seguros: int
    seguros_acertados: int
    puntos: int
    bono_calibrado: bool
    xp_otorgado: int
    ya_jugado_hoy: bool


def puntuar_calibre(conn, *, colaborador_id: UUID, modulo_id: UUID,
                    respuestas: list[dict]) -> ResultadoCalibre:
    """
    `respuestas`: [{item_id, indice_elegido, seguro}]. El orden no altera el
    puntaje —acá no hay racha— pero se conserva por trazabilidad.
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

    puntos = 0
    aciertos = seguros = seguros_acertados = 0

    for r in respuestas:
        if r["item_id"] not in correctas:
            continue                      # ítem ajeno al módulo: se ignora
        acerto = correctas[r["item_id"]] == r["indice_elegido"]
        seguro = bool(r["seguro"])

        puntos += PUNTOS[(seguro, acerto)]
        aciertos += acerto
        seguros += seguro
        seguros_acertados += seguro and acerto

    # Se premia la calibración, no el volumen: acertar todo lo que declaraste
    # seguro. Ir siempre a "Creo" no la gana.
    bono = seguros > 0 and seguros == seguros_acertados
    if bono:
        puntos += BONO_CALIBRADO

    # El marcador puede quedar negativo en pantalla —esa es la tensión— pero el
    # XP no: nunca se resta XP ya ganado. El castigo es no ganar, no perder.
    xp = max(0, puntos)

    evento = registrar_evento(
        conn,
        colaborador_id=colaborador_id,
        tipo="calibre_jugado",
        origen_tipo="juego",
        origen_id=modulo_id,
        xp=xp,
        clase_xp="ludico",
        clave_idempotencia=f"calibre:{colaborador_id}:{modulo_id}:{date.today().isoformat()}",
    )

    return ResultadoCalibre(
        total=len(correctas),
        aciertos=aciertos,
        seguros=seguros,
        seguros_acertados=seguros_acertados,
        puntos=puntos,
        bono_calibrado=bono,
        xp_otorgado=xp if evento else 0,
        ya_jugado_hoy=evento is None,
    )
