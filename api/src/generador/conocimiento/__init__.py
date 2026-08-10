"""
Base de conocimiento del Generador.

Una dimensión por archivo. Se escribe UNA VEZ por dimensión y el anidamiento de
los estándares CNA produce los tres niveles (ADR-003).

Todo esto es **contenido de prueba**: sirve para validar la máquina de
gamificación. En producción se reemplaza por el corpus que aporte AIEP, sin tocar
el generador ni el resto del sistema — ese es el swap de `fuente_de_contenido`.
"""
from .calidad import CALIDAD
from .docencia import DOCENCIA
from .gestion import GESTION
from .ici import ICI
from .vcm import VCM

# El orden es el de la fuente institucional.
DIMENSIONES = {
    "GESTION": GESTION,
    "DOCENCIA": DOCENCIA,
    "CALIDAD": CALIDAD,
    "VCM": VCM,
    "ICI": ICI,
}

__all__ = ["DIMENSIONES", "GESTION", "DOCENCIA", "CALIDAD", "VCM", "ICI"]
