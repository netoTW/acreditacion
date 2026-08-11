"""
Catálogo institucional — datos reales de la ruta de AIEP.

Todo lo de este archivo sale de `docs-fuente/` vía `docs/DOMINIO-RUTA-AIEP.md`.
Lo que NO está en la fuente va marcado como dato de prueba y se señala acá mismo,
para que nadie lo confunda con información oficial.
"""

# ----------------------------------------------------------------- dimensiones
# Modelo de evaluación integral vigente desde octubre de 2023 (Ley 20.129).
# Nombres oficiales, textuales de la fuente.
DIMENSIONES = [
    ("GESTION",  "Gestión Estratégica y Recursos Institucionales", True,  1),
    ("DOCENCIA", "Docencia y Resultados del Proceso de Formación",  True,  2),
    ("CALIDAD",  "Aseguramiento Interno de la Calidad",             True,  3),
    ("VCM",      "Vinculación con el Medio",                        True,  4),
    # Voluntaria, pero necesaria para el período máximo de vigencia.
    ("ICI",      "Investigación, Creación y/o Innovación",          False, 5),
]

# ----------------------------------------------------------------------- hitos
# Los 13 de la infografía "Nuestra ruta para avanzar".
# (codigo, ruta, anio, periodo, titulo, fecha_inicio, fecha_fin, orden)
HITOS = [
    ("H01", "autoevaluacion", 2026, "Enero",
     "Inicio del proceso de Autoevaluación Institucional", "2026-01-01", "2026-01-31", 1),
    ("H02", "autoevaluacion", 2026, "Marzo",
     "Aplicación de encuestas de opinión a titulados, empleadores y colaboradores",
     "2026-03-01", "2026-03-31", 2),
    ("H03", "autoevaluacion", 2026, "Abril",
     "Aplicación de encuestas de opinión a estudiantes y docentes",
     "2026-04-01", "2026-04-30", 3),
    ("H04", "autoevaluacion", 2026, "Abril–Mayo",
     "Constitución y ejecución de talleres de autoevaluación en Comités de Sedes y Escuelas",
     "2026-04-01", "2026-05-31", 4),
    ("H05", "autoevaluacion", 2026, "Mayo",
     "Ejecución de talleres con informantes clave en sedes "
     "(estudiantes, docentes, titulados y empleadores)", "2026-05-01", "2026-05-31", 5),
    ("H06", "autoevaluacion", 2026, "Junio–Julio",
     "Elaboración de informes de análisis y síntesis de resultados de comités de "
     "autoevaluación de sedes y escuelas y de los talleres con informantes clave",
     "2026-06-01", "2026-07-31", 6),
    ("H07", "autoevaluacion", 2026, "Agosto–Septiembre",
     "Constitución y ejecución de talleres de autoevaluación en Comités de "
     "Autoevaluación por Dimensión de Evaluación", "2026-08-01", "2026-09-30", 7),
    ("H08", "autoevaluacion", 2026, "Septiembre–Noviembre",
     "Constitución y ejecución de talleres de juicios evaluativos, fortalezas y "
     "debilidades y plan de mejora en Comité Central de Autoevaluación",
     "2026-09-01", "2026-11-30", 8),
    ("H09", "autoevaluacion", 2026, "Diciembre",
     "Entrega de la primera versión del Informe de Autoevaluación Institucional",
     "2026-12-01", "2026-12-31", 9),
    ("H10", "acreditacion", 2027, "Enero–Febrero",
     "Ajustes, edición y diseño final del Informe de Autoevaluación Institucional",
     "2027-01-01", "2027-02-28", 10),
    ("H11", "acreditacion", 2027, "Marzo–Mayo",
     "Inicio del proceso de Acreditación Institucional ante CNA-Chile · inicio de "
     "socialización · entrega del Informe de Muestra Intencionada",
     "2027-03-01", "2027-05-31", 11),
    ("H12", "acreditacion", 2027, "Desde Mayo",
     "Actividades de socialización de los resultados de la autoevaluación hasta la "
     "visita de evaluación externa (CNA)", "2027-05-01", None, 12),
    # La fuente dice "Por definir". No se inventa la fecha.
    ("H13", "acreditacion", 2027, "Por definir", "Visita de pares evaluadores", None, None, 13),
]

# ----------------------------------------------------------------------- roles
# Los 3 roles que AIEP definió en `docs-fuente/Impacto en dimensiones por nivel
# (roles).xlsx`. Reemplazan la taxonomía de 6 cargos que servía de marcador de
# posición (S-30). La tabla sigue llamándose `cargo`: cambian las filas, no el
# modelo — el grano (rol, dimensión) es el mismo de siempre (ADR-003).
CARGOS = [
    ("N1", "Nivel 1 · Alta Dirección",
     "Conducción institucional: gestión estratégica y aseguramiento de la calidad"),
    ("N2", "Nivel 2 · Liderazgo intermedio",
     "Conducción académica de la docencia y del aseguramiento en su unidad"),
    ("N3", "Nivel 3 · Administrativo y apoyo",
     "Procesos y soporte que sostienen la docencia y el aseguramiento"),
]

# --------------------------------------------- DISTRIBUCIÓN DE IMPACTO (AIEP)
# Fuente: el Excel, verificado celda por celda. Cada rol suma 1.
# Es el ÚNICO dato que se escribe a mano: el nivel de exigencia y la criticidad
# se derivan de acá abajo, no se transcriben.
DISTRIBUCION = {
    "N1": {"GESTION": 0.30, "DOCENCIA": 0.15, "CALIDAD": 0.30, "VCM": 0.15, "ICI": 0.10},
    "N2": {"GESTION": 0.10, "DOCENCIA": 0.35, "CALIDAD": 0.25, "VCM": 0.15, "ICI": 0.15},
    "N3": {"GESTION": 0.15, "DOCENCIA": 0.25, "CALIDAD": 0.35, "VCM": 0.20, "ICI": 0.05},
}

# ------------------------------------------------- derivación %→nivel CNA
# TODO CONFIRMAR CON AIEP (S-48): este corte es una derivación del arquitecto, no
# un dato de la fuente. El Excel entrega el % y la marca de ruta crítica, pero no
# dice qué nivel de estándar CNA le corresponde a cada rol en cada dimensión.
# Con estos cortes, las 2 críticas de cada rol caen siempre en nivel 3, que es
# coherente con el modelo; si AIEP tiene su propia tabla, se reemplaza ACÁ y nada
# más del sistema cambia.
CORTES_NIVEL = ((0.25, 3), (0.15, 2), (0.00, 1))   # (piso de %, nivel)

# Cuántas dimensiones son críticas por rol. Del Excel: 2 marcadas por rol.
CRITICAS_POR_ROL = 2

# El umbral se refuerza en las dimensiones críticas: la medalla gold se gana
# rindiendo más alto, no por pertenecer a un rol.
UMBRAL_ESTANDAR = 0.80
UMBRAL_CRITICO  = 0.85


def nivel_de(pct: float) -> int:
    """Nivel de exigencia CNA que corresponde a un peso. Parametrizado en CORTES_NIVEL."""
    for piso, nivel in CORTES_NIVEL:
        if pct >= piso:
            return nivel
    return 1


def matriz_de(codigo_rol: str) -> dict[str, dict]:
    """
    La matriz del rol, derivada de su distribución.

    Devuelve, por dimensión: el %, el nivel de exigencia, si es crítica y el
    umbral que le corresponde. La criticidad son las `CRITICAS_POR_ROL` de mayor
    peso; los empates se rompen por el orden oficial de las dimensiones, para que
    la derivación sea determinista y no dependa del orden del diccionario.
    """
    pesos = DISTRIBUCION[codigo_rol]
    orden_oficial = [d[0] for d in DIMENSIONES]
    ranking = sorted(pesos, key=lambda d: (-pesos[d], orden_oficial.index(d)))
    criticas = set(ranking[:CRITICAS_POR_ROL])

    return {
        dim: {
            "pct": pesos[dim],
            "nivel": nivel_de(pesos[dim]),
            "critica": dim in criticas,
            "umbral": UMBRAL_CRITICO if dim in criticas else UMBRAL_ESTANDAR,
        }
        for dim in orden_oficial
    }

# Anclaje de cada posición de la ruta a un hito real (S-43). La ruta se ordena
# por exigencia descendente: primero la dimensión donde al cargo se le pide más.
HITOS_POR_POSICION = ["H01", "H04", "H05", "H07", "H08"]

# ------------------------------------------------------------------- unidades
# Estructura de la gobernanza de la fuente. Los nombres de sedes y escuelas son
# marcadores de posición hasta que AIEP entregue el organigrama (S-30).
UNIDADES = [
    ("direccion_nacional", "Dirección Nacional de Aseguramiento de la Calidad"),
    ("sede",               "Sede Providencia"),
    ("sede",               "Sede La Serena"),
    ("escuela",            "Escuela de Administración y Negocios"),
    ("escuela",            "Escuela de Informática y Telecomunicaciones"),
    # Sede chica a propósito: con la población de prueba queda bajo el umbral
    # de anonimato y sirve para ver el plegado del panel (Ley 21.719).
    ("sede",               "Sede Chillán"),
]

# -------------------------------------------------------------------- comités
# Cadena de instancias de la fuente: aprueba → evalúa y valida → integra →
# autoevalúa por dimensión → autoevalúa en sede y escuela.
COMITES_FIJOS = [
    ("junta_directiva",        "Junta Directiva"),
    ("aseguramiento_calidad",  "Comité de Aseguramiento de la Calidad"),
    ("central_autoevaluacion", "Comité Central de Autoevaluación"),
]

# ------------------------------------------------------- los 3 del slice
# Uno por rol, para que las tres rutas se puedan comparar lado a lado.
#
# TODO CONFIRMAR CON AIEP (S-49): dónde caen los DOCENTES. Los tres roles se
# llaman Alta Dirección, Liderazgo intermedio y Administrativo y apoyo, y ninguno
# nombra la docencia de aula, pero Docencia es crítica en N2 y N3. Provisional:
# el docente va en N2, donde Docencia pesa 35% y es crítica. Pablo queda ahí.
COLABORADORES = [
    ("pablo@aiep.cl",           "Pablo (docente · provisional N2)", "N2",
     "Sede Providencia",        ["Comité de Sede · Sede Providencia"]),
    ("rectoria.prueba@aiep.cl", "Rectoría (prueba)",                "N1",
     "Dirección Nacional de Aseguramiento de la Calidad",
     ["Junta Directiva", "Comité Central de Autoevaluación"]),
    ("registro.prueba@aiep.cl", "Registro Curricular (prueba)",     "N3",
     "Sede La Serena",          ["Comité de Sede · Sede La Serena"]),
]

# --------------------------------------------------------- XP por nivel (S-37)
XP_MODULO  = {1: 60,  2: 80,  3: 100}
XP_MEDALLA = {1: 200, 2: 300, 3: 400}
# La gold cuesta más y rinde más: mismo bloque, mayor exigencia (desafío + 85%).
XP_MEDALLA_GOLD = {n: int(xp * 1.5) for n, xp in XP_MEDALLA.items()}
# S-32 revisado: la estructura es la MISMA en las 5 dimensiones —2 módulos con
# quiz + juego + evaluación—. La profundidad ya no se expresa en cuántos módulos
# hay, sino en cuánto contenido lleva cada uno.
MODULOS_POR_BLOQUE = 2
