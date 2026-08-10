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

# ---------------------------------------------------------------------- cargos
# Taxonomía estándar de IES chilena (S-30). El organigrama oficial de AIEP se
# cablea después: son filas de datos, no código.
CARGOS = [
    ("RECTOR",        "Rector",                 "Conducción institucional; visión global del proceso"),
    ("VICERRECTOR",   "Vicerrector Académico",  "Docencia y aseguramiento de la calidad"),
    ("DIR_CARRERA",   "Director de Carrera",    "Docencia y vinculación con el medio en su carrera"),
    ("DOCENTE",       "Docente",                "Aula y resultados del proceso de formación"),
    ("COORD_CALIDAD", "Coordinador de Calidad", "Aseguramiento interno y gestión"),
    ("ADMINISTRATIVO","Administrativo",         "Procesos de gestión y soporte institucional"),
]

# ----------------------------------------------------------------- LA MATRIZ
# ADR-003. Nivel de estándar CNA exigido a cada cargo por dimensión.
# Todo cargo toca las 5 con nivel >= 1: la acreditación es de todos.
MATRIZ = {
    "RECTOR":         {"GESTION": 3, "DOCENCIA": 2, "CALIDAD": 3, "VCM": 2, "ICI": 2},
    "VICERRECTOR":    {"GESTION": 2, "DOCENCIA": 3, "CALIDAD": 3, "VCM": 1, "ICI": 1},
    "DIR_CARRERA":    {"GESTION": 1, "DOCENCIA": 3, "CALIDAD": 2, "VCM": 3, "ICI": 1},
    "DOCENTE":        {"GESTION": 1, "DOCENCIA": 3, "CALIDAD": 1, "VCM": 1, "ICI": 1},
    "COORD_CALIDAD":  {"GESTION": 3, "DOCENCIA": 2, "CALIDAD": 3, "VCM": 1, "ICI": 1},
    "ADMINISTRATIVO": {"GESTION": 2, "DOCENCIA": 1, "CALIDAD": 2, "VCM": 1, "ICI": 1},
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
# Nombres de prueba: el director los renombra cuando quiera. Lo que importa es
# que los tres cargos tengan matrices bien distintas (S-40).
COLABORADORES = [
    ("pablo@aiep.cl",           "Pablo",                            "DOCENTE",
     "Sede Providencia",        ["Comité de Sede · Sede Providencia"]),
    ("rectoria.prueba@aiep.cl", "Rectoría (prueba)",                "RECTOR",
     "Dirección Nacional de Aseguramiento de la Calidad",
     ["Junta Directiva", "Comité Central de Autoevaluación"]),
    ("calidad.prueba@aiep.cl",  "Coordinación de Calidad (prueba)", "COORD_CALIDAD",
     "Dirección Nacional de Aseguramiento de la Calidad",
     ["Comité de Aseguramiento de la Calidad"]),
]

# --------------------------------------------------------- XP por nivel (S-37)
XP_MODULO  = {1: 60,  2: 80,  3: 100}
XP_MEDALLA = {1: 200, 2: 300, 3: 400}
MODULOS_POR_NIVEL = {1: 2, 2: 3, 3: 4}          # S-32
