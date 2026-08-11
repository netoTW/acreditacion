"""
Juego de D1 Gestión — «El presupuesto de la acreditación».

La única mecánica con **estado que evoluciona**. Tres semestres de decisión, un
presupuesto que no alcanza para todo, y consecuencias que llegan dos semestres
después de haberlas sembrado.

Cómo se reparte el trabajo entre cliente y servidor, y por qué:

- **Las reglas son públicas.** Desgaste, efecto, umbral, retardo y la regla
  encadenada viajan al cliente, que puede proyectar lo que ya está comprometido.
  Ocultarlas no agregaría dificultad, agregaría adivinanza — y el presupuesto
  sigue sin alcanzar aunque se sepa la aritmética.
- **El resultado lo recalcula el servidor.** El cliente manda solo las tres
  asignaciones; acá se vuelve a correr la simulación entera desde el escenario
  guardado. Un cliente que mienta sobre los indicadores no gana nada, porque los
  indicadores no viajan de vuelta: viajan las decisiones.
- **La solución de ejemplo nunca sale.** Es del validador, no del juego.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from .eventos import registrar_evento
from .simulacion import evaluar, simular

PUNTOS_POR_FRENTE = 60
BONO_PERIODO_LIMPIO = 120

CLAVE = "gestion"


@dataclass(frozen=True)
class ResultadoGestion:
    frentes_en_pie: int
    frentes_totales: int
    periodo_limpio: bool
    cupos_usados: int
    cupos_disponibles: int
    puntos: int
    xp_otorgado: int
    ya_jugado_hoy: bool
    historia: list[dict]
    cierre: dict


def _dimension_del_bloque(conn, colaborador_id: UUID, bloque_ruta_id: UUID) -> str:
    fila = conn.execute(
        """
        SELECT d.codigo
          FROM bloque_ruta br
          JOIN ruta r              ON r.id  = br.ruta_id
          JOIN bloque_contenido bc ON bc.id = br.bloque_contenido_id
          JOIN dimension d         ON d.id  = bc.dimension_id
         WHERE br.id = %s AND r.colaborador_id = %s
        """,
        (bloque_ruta_id, colaborador_id),
    ).fetchone()
    if fila is None:
        raise LookupError("ese bloque no está en tu ruta")
    return fila[0]


def _escenario(conn, escenario_id=None) -> dict:
    if escenario_id is None:
        fila = conn.execute(
            """SELECT id, codigo, titulo, contexto, turnos, turnos_de_decision,
                      presupuesto, retardo, frentes, regla, cierre
                 FROM escenario_gestion ORDER BY random() LIMIT 1"""
        ).fetchone()
    else:
        fila = conn.execute(
            """SELECT id, codigo, titulo, contexto, turnos, turnos_de_decision,
                      presupuesto, retardo, frentes, regla, cierre
                 FROM escenario_gestion WHERE id = %s""",
            (escenario_id,),
        ).fetchone()
    if fila is None:
        raise LookupError("no hay escenarios de gestión cargados")

    return {
        "escenario_id": fila[0], "codigo": fila[1], "titulo": fila[2],
        "contexto": fila[3], "turnos": fila[4], "turnos_de_decision": fila[5],
        "presupuesto": fila[6], "retardo": fila[7], "frentes": fila[8],
        "regla": fila[9], "cierre": fila[10],
    }


def repartir(conn, *, colaborador_id: UUID, bloque_ruta_id: UUID) -> dict:
    """Un escenario con su modelo completo. Sin la solución de ejemplo."""
    from .juegos import exigir
    exigir(_dimension_del_bloque(conn, colaborador_id, bloque_ruta_id), CLAVE)
    return {"juego": CLAVE, **_escenario(conn)}


def cerrar_periodo(conn, *, colaborador_id: UUID, bloque_ruta_id: UUID,
                   escenario_id: UUID, asignaciones: list[dict]) -> ResultadoGestion:
    """
    Vuelve a correr el período completo desde el escenario guardado y puntúa.

    Se verifica el presupuesto turno por turno: gastar de más no es un error del
    cliente que se pueda ignorar, es la restricción entera del juego.
    """
    from .juegos import exigir
    exigir(_dimension_del_bloque(conn, colaborador_id, bloque_ruta_id), CLAVE)

    escenario = _escenario(conn, escenario_id)
    claves = {f["clave"] for f in escenario["frentes"]}

    if len(asignaciones) > escenario["turnos_de_decision"]:
        raise ValueError(
            f"el período tiene {escenario['turnos_de_decision']} turnos de decisión"
        )

    limpias = []
    usados = 0
    for i, turno in enumerate(asignaciones, start=1):
        reparto = {}
        for clave, unidades in (turno or {}).items():
            if clave not in claves:
                raise ValueError(f"el turno {i} invierte en «{clave}», que no es un frente")
            if not isinstance(unidades, int) or unidades < 0:
                raise ValueError(f"el turno {i} asigna una cantidad que no es un cupo entero")
            if unidades:
                reparto[clave] = unidades
        gastado = sum(reparto.values())
        if gastado > escenario["presupuesto"]:
            raise ValueError(
                f"el turno {i} gasta {gastado} cupos y el presupuesto es "
                f"{escenario['presupuesto']}"
            )
        usados += gastado
        limpias.append(reparto)

    historia = simular(escenario, limpias)
    cierre = evaluar(escenario, historia)

    limpio = cierre["en_pie"] == cierre["total"]
    puntos = cierre["en_pie"] * PUNTOS_POR_FRENTE + (BONO_PERIODO_LIMPIO if limpio else 0)

    evento = registrar_evento(
        conn,
        colaborador_id=colaborador_id,
        tipo="periodo_de_gestion_cerrado",
        origen_tipo="juego",             # obliga a que el XP sea lúdico (001)
        origen_id=bloque_ruta_id,
        xp=puntos,
        clase_xp="ludico",
        clave_idempotencia=f"gestion:{colaborador_id}:{bloque_ruta_id}:{date.today().isoformat()}",
    )

    return ResultadoGestion(
        frentes_en_pie=cierre["en_pie"],
        frentes_totales=cierre["total"],
        periodo_limpio=limpio,
        cupos_usados=usados,
        cupos_disponibles=escenario["presupuesto"] * escenario["turnos_de_decision"],
        puntos=puntos,
        xp_otorgado=puntos if evento else 0,
        ya_jugado_hoy=evento is None,
        historia=historia,
        cierre={**cierre, "texto": escenario["cierre"]},
    )
