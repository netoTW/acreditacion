"""
Tipos del Generador de Contenido.

La unidad de generación es el par `(dimensión, nivel_estandar)` — ADR-003.
El conocimiento se escribe UNA VEZ por dimensión, en conceptos con `nivel_minimo`,
y el anidamiento de los estándares CNA (el nivel 3 incluye al 2 y el 2 al 1) hace
el resto: un bloque de nivel N usa todos los conceptos con `nivel_minimo <= N`.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Distractor:
    """Alternativa incorrecta con su razón. La razón se muestra en el quiz formativo."""
    texto: str
    por_que_no: str


@dataclass(frozen=True)
class Concepto:
    codigo: str
    nombre: str
    # Desde qué nivel de estándar aparece. Los de nivel_minimo 1 están en los tres
    # bloques de la dimensión; los de 3, solo en el más exigente.
    nivel_minimo: int

    # Microlearning: el párrafo que va al módulo.
    microlearning: str

    # Ítem de definición.
    definicion: str
    confusiones: tuple[Distractor, Distractor, Distractor]
    explicacion_definicion: str

    # Ítem de escenario aplicado.
    escenario: str
    accion_correcta: str
    acciones_incorrectas: tuple[Distractor, Distractor, Distractor]
    explicacion_escenario: str


@dataclass(frozen=True)
class Dimension:
    codigo: str
    nombre_oficial: str
    # Marco del que cuelga el contenido. Sale de la ruta institucional de AIEP,
    # no de una fuente normativa externa.
    encuadre: str
    conceptos: tuple[Concepto, ...]

    def para_nivel(self, nivel: int) -> list[Concepto]:
        return [c for c in self.conceptos if c.nivel_minimo <= nivel]
