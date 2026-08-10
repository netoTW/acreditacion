"""
Generador de Contenido.

    (dimensión, nivel_estandar, fuente_de_contenido) → bloque de contenido completo

Determinista: la misma entrada produce la misma salida, así el contenido es
revisable y diffeable. Nada de aleatoriedad en la generación; barajar es cosa del
intento, no del banco.

**El swap a producción está acá:** `fuente_de_contenido` es `{modo:'prueba'}` en el
slice y `{modo:'corpus'}` cuando AIEP entregue el material CNA. El resto de la
máquina —matriz, medallas, motor, rutas— no cambia (ADR-003).
"""
from __future__ import annotations

from .conocimiento import DIMENSIONES
from .tipos import Concepto, Dimension

MODULOS_POR_NIVEL = {1: 2, 2: 3, 3: 4}          # S-32
XP_MODULO = {1: 60, 2: 80, 3: 100}              # S-37
XP_MEDALLA = {1: 200, 2: 300, 3: 400}           # S-37
ITEMS_POR_INTENTO = 5
LETRAS = "ABCD"


def generar(codigo_dimension: str, nivel: int, *, tema: str | None = None) -> dict:
    """Produce un bloque de contenido que cumple `schema-bloque-contenido.json`."""
    dim = DIMENSIONES[codigo_dimension]
    conceptos = dim.para_nivel(nivel)

    return {
        "version_schema": "1.0.0",
        "dimension": dim.codigo,
        "nivel_estandar": nivel,
        # Sin excepción en esta etapa: nada de esto es material oficial de acreditación.
        "es_contenido_prueba": True,
        "fuente_contenido": {"modo": "prueba", "tema": tema or dim.nombre_oficial},
        "generador_version": "1.0.0",
        "titulo": f"{dim.nombre_oficial} · Nivel {nivel}",
        "resumen": _resumen(dim, nivel, conceptos),
        "criterios": _criterios(dim, conceptos),
        "modulos": _modulos(dim, nivel, conceptos),
        "evaluacion": {
            "umbral_aprobacion": 0.8,
            "n_items_por_intento": ITEMS_POR_INTENTO,
            "max_reintentos": 3,
            "minutos_expiracion": 1440,
            "banco_items": _banco(conceptos),
        },
        "medalla": {
            "tipo": "silver",
            "nombre": f"{dim.nombre_oficial} · N{nivel}",
            "descripcion": (
                f"Acredita el recorrido de {dim.nombre_oficial} al nivel de estándar {nivel}. "
                "Se otorga solo con la evaluación del bloque aprobada."
            ),
            "xp": XP_MEDALLA[nivel],
        },
    }


def generar_todo(*, tema: str | None = None) -> list[dict]:
    """Las 15 unidades: 5 dimensiones × 3 niveles. No 30 (ADR-003)."""
    return [generar(codigo, nivel, tema=tema)
            for codigo in DIMENSIONES for nivel in (1, 2, 3)]


# ------------------------------------------------------------------ armado
def _resumen(dim: Dimension, nivel: int, conceptos: list[Concepto]) -> str:
    profundidad = {
        1: "Recorrido base: qué es, para qué sirve y cuál es tu parte",
        2: "Recorrido intermedio: cómo se evalúa y cómo se sostiene la evidencia",
        3: "Recorrido avanzado: cómo se conduce, se integra y se defiende ante pares",
    }[nivel]
    return (
        f"{profundidad}. {dim.encuadre} "
        f"Cubre {len(conceptos)} conceptos y cierra con una evaluación al 80%."
    )


def _criterios(dim: Dimension, conceptos: list[Concepto]) -> list[dict]:
    # La fuente declara 16 criterios pero no los enumera ni los reparte (S-33).
    # Estos son de prueba y quedan marcados como tales; el experto CNA de AIEP los
    # reemplaza en producción sin tocar el modelo.
    return [
        {
            "codigo": f"{dim.codigo}-{i:02d}",
            "nombre": c.nombre,
            "es_contenido_prueba": True,
        }
        for i, c in enumerate(conceptos, start=1)
    ]


def _modulos(dim: Dimension, nivel: int, conceptos: list[Concepto]) -> list[dict]:
    cantidad = MODULOS_POR_NIVEL[nivel]
    grupos = _repartir(conceptos, cantidad)
    modulos = []

    for i, grupo in enumerate(grupos, start=1):
        # min(i, nivel) garantiza que en un bloque de nivel N estén presentes todos
        # los tramos de origen de 1 a N, que es lo que exige el validador.
        origen = min(i, nivel)
        cuerpo = [
            f"## {dim.nombre_oficial} · módulo {i} de {cantidad}",
            "",
            f"> Contenido de prueba para validar la plataforma. No es material "
            f"oficial de acreditación.",
            "",
        ]
        for c in grupo:
            cuerpo += [f"### {c.nombre}", "", c.microlearning, ""]
        cuerpo += [
            "### Para llevarte",
            "",
            "· " + "\n· ".join(f"**{c.nombre}**: {c.definicion}" for c in grupo),
        ]

        modulos.append({
            "orden": i,
            "titulo": f"{dim.nombre_oficial} · {_titulo_modulo(grupo)}",
            "cuerpo": "\n".join(cuerpo),
            "duracion_min": 8 + 2 * len(grupo),
            "xp": XP_MODULO[nivel],
            "nivel_estandar_origen": origen,
            "quiz_formativo": _quiz_formativo(grupo, conceptos),
        })
    return modulos


def _titulo_modulo(grupo: list[Concepto]) -> str:
    return " y ".join(c.nombre.lower() for c in grupo[:2]) + ("…" if len(grupo) > 2 else "")


def _repartir(conceptos: list[Concepto], cantidad: int) -> list[list[Concepto]]:
    """Reparte los conceptos en `cantidad` grupos lo más parejos posible."""
    base, resto = divmod(len(conceptos), cantidad)
    grupos, i = [], 0
    for g in range(cantidad):
        n = base + (1 if g < resto else 0)
        grupos.append(conceptos[i:i + n])
        i += n
    return grupos


# ------------------------------------------------------------------- ítems
def _quiz_formativo(grupo: list[Concepto], todos: list[Concepto]) -> list[dict]:
    """Feedback inmediato dentro del módulo. No otorga completitud (S-07)."""
    items = []
    for j, c in enumerate(grupo):
        items.append(_item_definicion(c, j))
        items.append(_item_escenario(c, j + 1))
    while len(items) < 3:                      # el schema pide mínimo 3
        items.append(_item_emparejamiento(grupo[0], todos, len(items)))
    return items


def _banco(conceptos: list[Concepto]) -> list[dict]:
    """
    Tres ítems por concepto: definición, escenario aplicado y emparejamiento.

    Con 6 / 8 / 10 conceptos por nivel salen 18 / 24 / 30 ítems, holgadamente sobre
    el mínimo de 3× los ítems por intento que exige el validador (S-06).
    """
    items = []
    for i, c in enumerate(conceptos):
        items.append(_item_definicion(c, i))
        items.append(_item_escenario(c, i + 1))
        items.append(_item_emparejamiento(c, conceptos, i + 2))
    return items


def _armar(enunciado: str, correcta: str, explicacion_ok: str,
           distractores, desplazamiento: int, codigo_criterio: str, dificultad: int) -> dict:
    """
    Coloca la correcta en una posición que rota con el índice.

    Es deliberado: si la correcta cayera siempre en la misma casilla, el banco se
    aprobaría sin saber la materia y la insignia sería técnicamente válida pero
    institucionalmente falsa. El validador lo verifica (regla 16).
    """
    pos = desplazamiento % 4
    textos, explicaciones = [], []
    resto = list(distractores)
    for k in range(4):
        if k == pos:
            textos.append(correcta)
            explicaciones.append(explicacion_ok)
        else:
            d = resto.pop(0)
            textos.append(d.texto)
            explicaciones.append(d.por_que_no)
    return {
        "enunciado": enunciado,
        "alternativas": textos,
        "indice_correcta": pos,
        "explicaciones": explicaciones,
        "criterio_codigo": codigo_criterio,
        "dificultad": dificultad,
    }


def _item_definicion(c: Concepto, desplazamiento: int) -> dict:
    return _armar(
        f"En el proceso de autoevaluación, ¿qué es {c.nombre.lower()}?",
        c.definicion, c.explicacion_definicion, c.confusiones,
        desplazamiento, c.codigo, 1,
    )


def _item_escenario(c: Concepto, desplazamiento: int) -> dict:
    return _armar(
        c.escenario, c.accion_correcta, c.explicacion_escenario, c.acciones_incorrectas,
        desplazamiento, c.codigo, 3,
    )


def _item_emparejamiento(c: Concepto, todos: list[Concepto], desplazamiento: int) -> dict:
    """
    Emparejar concepto y definición.

    Se compone solo, cruzando definiciones de otros conceptos del mismo bloque:
    da variedad real sin inventar contenido, y las explicaciones salen exactas
    ("esa es la definición de X, no de Y").
    """
    otros = [o for o in todos if o.codigo != c.codigo][:3]
    while len(otros) < 3:
        otros.append(c)
    distractores = tuple(
        type(c.confusiones[0])(
            texto=o.definicion,
            por_que_no=f"Esa es la definición de {o.nombre.lower()}, no de {c.nombre.lower()}.",
        )
        for o in otros
    )
    return _armar(
        f"¿Cuál de estas afirmaciones describe correctamente {c.nombre.lower()}?",
        c.definicion,
        f"Correcto: así se entiende {c.nombre.lower()} en este proceso.",
        distractores, desplazamiento, c.codigo, 2,
    )
