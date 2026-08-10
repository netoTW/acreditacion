"""
Generador de Contenido, Validador e Integrador.

    generar()  →  validar()  →  integrar()

Nada que no pase el validador se integra (CLAUDE.md §9.3).
"""
from .generador import generar, generar_todo
from .integrador import integrar
from .validador import Resultado, validar, validar_lote

__all__ = ["generar", "generar_todo", "validar", "validar_lote", "Resultado", "integrar"]
