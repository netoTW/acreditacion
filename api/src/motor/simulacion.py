"""
El motor de simulación de D1 Gestión. Un solo modelo, dos consumidores.

Vive acá y no junto al contenido porque lo usan **el juego y el validador**: el
validador comprueba que cada escenario sea resoluble simulándolo de verdad, y si
hubiera dos simuladores —uno para validar y otro para jugar— podrían separarse y
el validador terminaría aprobando escenarios que el juego no puede ganar.

Las reglas son PÚBLICAS: desgaste, efecto, umbral, retardo y la regla encadenada
viajan al cliente. Que el jugador pueda calcular no le quita nada al juego —el
presupuesto sigue sin alcanzar para todo— y le quita la parte que no enseña
nada, que es adivinar la aritmética. Lo que no viaja es la solución de ejemplo.
"""
from __future__ import annotations


def simular(escenario: dict, asignaciones: list[dict]) -> list[dict]:
    """
    Corre el período completo y devuelve el estado turno a turno.

    Cada turno, en este orden:

    1. **Desgaste.** Lo que no se atiende baja solo. Es el supuesto que hace que
       no decidir también sea una decisión.
    2. **Llegadas.** Lo invertido hace `retardo` turnos aterriza recién ahora. Lo
       que se siembra en el último turno de decisión se ve en el cierre, y por
       eso invertir tarde en el indicador visible no alcanza.
    3. **La regla encadenada.** Un frente puede estar limitado por otro: no se
       puede documentar lo que el sistema no registra. El exceso por sobre el
       techo **se pierde**, no se acumula esperando que el habilitador suba.
    """
    frentes = {f["clave"]: f for f in escenario["frentes"]}
    valor = {k: float(f["inicial"]) for k, f in frentes.items()}
    regla = escenario.get("regla")
    retardo = escenario["retardo"]

    historia = []
    for turno in range(1, escenario["turnos"] + 1):
        for clave, f in frentes.items():
            valor[clave] -= f["desgaste"]

        origen = turno - retardo                    # el turno de decisión que aterriza
        if 1 <= origen <= len(asignaciones):
            for clave, unidades in (asignaciones[origen - 1] or {}).items():
                if clave in frentes:
                    valor[clave] += unidades * frentes[clave]["efecto"]

        for clave in valor:
            valor[clave] = max(0.0, min(100.0, valor[clave]))

        techo = None
        if regla:
            techo = regla["base"] + regla["factor"] * valor[regla["habilitador"]]
            valor[regla["frente"]] = min(valor[regla["frente"]], techo)

        historia.append({
            "turno": turno,
            "valores": {k: round(v, 1) for k, v in valor.items()},
            "techo": round(techo, 1) if techo is not None else None,
            "llegadas": dict(asignaciones[origen - 1]) if 1 <= origen <= len(asignaciones) else {},
        })

    return historia


def evaluar(escenario: dict, historia: list[dict]) -> dict:
    """El cierre: qué frentes llegaron sobre su umbral en el último turno."""
    finales = historia[-1]["valores"] if historia else {}
    detalle = []
    for f in escenario["frentes"]:
        valor = finales.get(f["clave"], 0.0)
        detalle.append({
            "clave": f["clave"],
            "nombre": f["nombre"],
            "valor_final": valor,
            "umbral": f["umbral"],
            "en_pie": valor >= f["umbral"],
        })
    return {
        "frentes": detalle,
        "en_pie": sum(1 for d in detalle if d["en_pie"]),
        "total": len(detalle),
    }
