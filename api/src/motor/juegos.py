"""
Qué juego lleva cada dimensión.

El modelo de AIEP pide que **cada dimensión tenga el suyo, distinto**. Este mapa es
el registro: agregar un juego es una línea acá más su motor, y la pantalla del bloque
deja de mostrar el hueco «en construcción» sola.

Vive aparte del motor de cada juego a propósito: el bloque necesita saber QUÉ juego
le toca sin importar cómo funciona, y los endpoints necesitan verificar que el juego
que se pide es el de esa dimensión y no otro.
"""
from __future__ import annotations


class JuegoNoCorresponde(Exception):
    """Se pidió un juego en una dimensión que no es la suya."""


JUEGOS = {
    "CALIDAD": {
        "clave": "linea_tiempo",
        "nombre": "Línea de tiempo del proceso",
        "descripcion": "Ordena los hitos reales de la autoevaluación y la acreditación",
    },
    # Fase 2, pendientes: GESTION, DOCENCIA, VCM, ICI.
}


def juego_de(codigo_dimension: str) -> dict | None:
    return JUEGOS.get(codigo_dimension)


def exigir(codigo_dimension: str, clave: str) -> None:
    """El juego de una dimensión no se juega desde otra."""
    juego = JUEGOS.get(codigo_dimension)
    if juego is None or juego["clave"] != clave:
        raise JuegoNoCorresponde(
            f"«{clave}» no es el juego de esta dimensión"
        )
