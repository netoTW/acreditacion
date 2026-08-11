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

# S-32 revisado por el modelo de AIEP: la estructura es la MISMA en las cinco
# dimensiones —2 módulos con quiz + juego + evaluación—. Lo que escala con el
# nivel de exigencia ya no es cuántas piezas hay, sino cuánto contenido llevan.
MODULOS_POR_BLOQUE = 2
ITEMS_QUIZ_POR_NIVEL = {1: 3, 2: 5, 3: 7}
ITEMS_EVAL_POR_NIVEL = {1: 4, 2: 6, 3: 8}

XP_MODULO = {1: 60, 2: 80, 3: 100}              # S-37
XP_MEDALLA = {1: 200, 2: 300, 3: 400}           # S-37
# La gold se gana con más exigencia (desafío aplicado + umbral 85%), así que rinde
# más. No la reparte el rol: la reparte haber rendido más alto.
XP_MEDALLA_GOLD = {n: int(xp * 1.5) for n, xp in XP_MEDALLA.items()}
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
        "desafio": _desafio(dim, nivel, conceptos),
        "evaluacion": {
            "umbral_aprobacion": 0.8,
            "n_items_por_intento": ITEMS_EVAL_POR_NIVEL[nivel],
            "max_reintentos": 3,
            "minutos_expiracion": 1440,
            "banco_items": _banco(conceptos),
        },
        # Dos rangos por bloque. Cuál se otorga NO lo decide el contenido: lo decide
        # si la dimensión es crítica en la ruta de esa persona, y la base lo verifica.
        "medallas": [
            {
                "tipo": "silver",
                "nombre": f"{dim.nombre_oficial} · N{nivel}",
                "descripcion": (
                    f"Acredita el recorrido de {dim.nombre_oficial} al nivel de estándar "
                    f"{nivel}. Se otorga solo con la evaluación del bloque aprobada."
                ),
                "xp": XP_MEDALLA[nivel],
            },
            {
                "tipo": "gold",
                "nombre": f"{dim.nombre_oficial} · N{nivel} · ruta crítica",
                "descripcion": (
                    f"Acredita {dim.nombre_oficial} como dimensión crítica del rol: "
                    "exige resolver el desafío aplicado y aprobar la evaluación "
                    "reforzada al 85%."
                ),
                "xp": XP_MEDALLA_GOLD[nivel],
            },
        ],
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
    cantidad = MODULOS_POR_BLOQUE
    grupos = _repartir(conceptos, cantidad)
    modulos = []

    for i, grupo in enumerate(grupos, start=1):
        # El anidamiento CNA ya no se expresa en "un módulo por tramo" —con dos
        # módulos fijos no cabría—, sino en el reparto: `para_nivel` trae los
        # conceptos de todos los tramos 1..nivel y `_repartir` los deja en orden,
        # así que el módulo 1 son los fundamentos y el 2 llega hasta el nivel del
        # rol. El bloque sigue conteniendo al nivel anterior, que es lo que exige
        # el modelo CNA; lo que cambió es dónde se ve.
        origen = 1 if i == 1 else nivel
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
            "quiz_formativo": _quiz_formativo(grupo, conceptos, ITEMS_QUIZ_POR_NIVEL[nivel]),
        })
    return modulos


# ------------------------------------------------------- desafío aplicado
# Datos de la situación. Son de PRUEBA y deliberadamente redondos: existen para
# que la decisión tenga contexto, no para afirmar nada sobre AIEP. En producción
# los reemplaza el corte real que aporte la institución.
DATOS_SITUACION = {
    "GESTION": [
        ("Unidades que entregaron su plan operativo", "7 de 12"),
        ("Presupuesto del período con ejecución registrada", "68%"),
        ("Sesiones de la instancia de conducción con acta firmada", "3 de 6"),
    ],
    "DOCENCIA": [
        ("Carreras con resultados de aprendizaje actualizados", "9 de 14"),
        ("Titulación oportuna informada", "54%, con dos fuentes que no coinciden"),
        ("Encuestas docentes con cierre de brecha documentado", "2 de 14"),
    ],
    "CALIDAD": [
        ("Dimensiones con informe de autoevaluación en borrador", "3 de 5"),
        ("Evidencias cargadas con respaldo verificable", "61%"),
        ("Planes de mejora con responsable y plazo", "4 de 11"),
    ],
    "VCM": [
        ("Convenios vigentes con actividad registrada este año", "8 de 21"),
        ("Actividades con evaluación de impacto documentada", "12%"),
        ("Contrapartes externas que respondieron la consulta", "5 de 9"),
    ],
    "ICI": [
        ("Publicaciones con afiliación institucional correcta", "18 de 26"),
        ("Proyectos con informe de avance al día", "4 de 7"),
        ("Investigadores con dedicación formalizada", "3 de 10"),
    ],
}

CLAVES = "abcdefgh"


def _opciones(textos: list[str], correcta: int) -> tuple[list[dict], str]:
    """Etiqueta las opciones y devuelve cuál es la correcta. La posición ya viene rotada."""
    return ([{"clave": CLAVES[i], "texto": t} for i, t in enumerate(textos)],
            CLAVES[correcta])


def _desafio(dim: Dimension, nivel: int, conceptos: list[Concepto]) -> dict:
    """
    Caso aplicado de la dimensión crítica.

    No pregunta qué es algo: pone a la persona en una silla, le da una situación
    con datos y le pide **decidir** entre opciones definidas. Todo lo que decide
    es corregible por el servidor — nada de texto libre— y todo sale de material
    ya etiquetado: acciones que el contenido declara correctas o incorrectas, y
    definiciones frente a sus confusiones frecuentes. No se inventa una secuencia
    canónica ni una categoría que el contenido no tenga.
    """
    c = conceptos
    principal = c[-1]                      # el concepto más exigente del bloque

    # --- decisión 1: priorizar bajo restricción ---
    textos1 = [d.texto for d in principal.acciones_incorrectas[:3]]
    pos1 = nivel % 4
    textos1.insert(pos1, principal.accion_correcta)
    opciones1, correcta1 = _opciones(textos1, pos1)

    # --- decisión 2: qué se sostiene y qué es confusión frecuente ---
    elementos, correcta2 = [], {}
    for k, concepto in enumerate(c[:2]):
        clave_ok = CLAVES[k * 2]
        clave_mal = CLAVES[k * 2 + 1]
        elementos += [
            {"clave": clave_ok,  "texto": concepto.definicion},
            {"clave": clave_mal, "texto": concepto.confusiones[0].texto},
        ]
        correcta2[clave_ok] = "sostiene"
        correcta2[clave_mal] = "no_sostiene"

    # --- decisión 3: marcar todas las que corresponden ---
    apoyo = c[2:5] if len(c) >= 5 else c[:3]
    textos3 = [x.accion_correcta for x in apoyo]
    correctas3 = [CLAVES[i] for i in range(len(textos3))]
    textos3 += [d.texto for d in principal.acciones_incorrectas[:2]]
    opciones3 = [{"clave": CLAVES[i], "texto": t} for i, t in enumerate(textos3)]

    return {
        "titulo": f"Comité de autoevaluación · {dim.nombre_oficial}",
        "rol_ficticio": (
            f"Integras el Comité de Autoevaluación de {dim.nombre_oficial}. "
            "La sesión es el jueves y hay que llegar con decisiones tomadas."
        ),
        "situacion": (
            f"{dim.encuadre} Faltan tres semanas para entregar el informe de la "
            "dimensión y el estado del material es desparejo. Esto es lo que hay "
            "sobre la mesa:"
        ),
        "datos": [
            {"etiqueta": e, "valor": v, "es_contenido_prueba": True}
            for e, v in DATOS_SITUACION[dim.codigo]
        ],
        "es_contenido_prueba": True,
        "decisiones": [
            {
                "orden": 1,
                "tipo": "eleccion_unica",
                "enunciado": (
                    f"{principal.escenario} El comité solo alcanza a resolver UNA "
                    "cosa antes de la sesión. ¿Cuál se lleva la semana?"
                ),
                "opciones": opciones1,
                "grupos": [],
                "clave_correcta": correcta1,
                "explicacion": principal.explicacion_escenario,
            },
            {
                "orden": 2,
                "tipo": "clasificacion",
                "enunciado": (
                    "Un integrante trae cuatro afirmaciones para el informe. "
                    "Separa las que se sostienen ante los pares evaluadores de las "
                    "que son confusiones frecuentes."
                ),
                "opciones": elementos,
                "grupos": [
                    {"clave": "sostiene",    "etiqueta": "Se sostiene ante los pares"},
                    {"clave": "no_sostiene", "etiqueta": "No resiste: confusión frecuente"},
                ],
                "clave_correcta": correcta2,
                "explicacion": " ".join(
                    f"{x.explicacion_definicion} {x.confusiones[0].por_que_no}" for x in c[:2]
                ),
            },
            {
                "orden": 3,
                "tipo": "seleccion_multiple",
                "enunciado": (
                    f"Para cerrar la sesión hay que comprometer acciones. Marca "
                    f"TODAS las que efectivamente sostienen {dim.nombre_oficial} "
                    "—y ninguna que no."
                ),
                "opciones": opciones3,
                "grupos": [],
                "clave_correcta": correctas3,
                "explicacion": " ".join(x.explicacion_escenario for x in apoyo),
            },
        ],
    }


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
def _quiz_formativo(grupo: list[Concepto], todos: list[Concepto], cantidad: int) -> list[dict]:
    """
    Feedback inmediato dentro del módulo. No otorga completitud (S-07).

    El largo lo fija el nivel de exigencia del bloque: es acá donde se nota que la
    dimensión pesa 35% y no 5%. La primera pasada deja **un ítem por concepto**
    alternando definición y escenario, para que ningún concepto del módulo quede
    sin tocar aunque el corte llegue antes; la segunda pasada agrega el tipo que
    faltaba, y recién ahí se corta.
    """
    primera, segunda = [], []
    for j, c in enumerate(grupo):
        if j % 2 == 0:
            primera.append(_item_definicion(c, j))
            segunda.append(_item_escenario(c, j + 1))
        else:
            primera.append(_item_escenario(c, j))
            segunda.append(_item_definicion(c, j + 1))

    items = primera + segunda
    while len(items) < 3:                      # el schema pide mínimo 3
        items.append(_item_emparejamiento(grupo[0], todos, len(items)))
    return items[:max(3, cantidad)]


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
