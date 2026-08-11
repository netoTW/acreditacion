"""
Contenido de D5 Investigación — «El cuadrante de la producción».

Dos preguntas **independientes** sobre cada pieza de producción:

1. **¿Es investigación, creación o innovación?** Una guía docente, un informe de
   gestión o una charla de difusión son trabajo legítimo y no son ICI.
2. **¿La institución puede reclamarla?** Un artículo indexado firmado con la
   afiliación de otra universidad es ICI y no es nuestro. Una patente donde un
   docente participó a título personal, tampoco.

Las dos se cruzan y dan cuatro casilleros. Solo uno cuenta para el informe, y los
otros tres son exactamente donde se infla el listado sin querer: se suma lo que es
nuestro pero no es investigación, y lo que es investigación pero no es nuestro.

Las **líneas declaradas** existen como referencia en el tablero: una producción de
investigación que no se puede colgar de ninguna línea es una señal, no una prueba,
y por eso no forma un tercer eje.

TODO es contenido de prueba: las producciones son plausibles pero inventadas y no
describen la actividad real de AIEP. En la fase de contenido real, AIEP entrega sus
líneas declaradas y su criterio de adscripción institucional (ver `DUDAS.md`).
"""
from __future__ import annotations

LINEAS = [
    ("sostenibilidad", "Tecnologías para la sostenibilidad",
     "Eficiencia energética, gestión de residuos y adaptación en entornos urbanos"),
    ("productiva", "Innovación productiva territorial",
     "Mejora de procesos y desarrollo de producto con empresas de la región"),
    ("educacion", "Educación técnica y trayectorias formativas",
     "Progresión, empleabilidad y didáctica de la formación técnico-profesional"),
    ("creacion", "Creación y patrimonio local",
     "Producción artística y puesta en valor del patrimonio del territorio"),
    ("salud", "Salud comunitaria aplicada",
     "Intervenciones y tecnología de apoyo en atención primaria"),
]

# (código, título, tipo, detalle, es_ici, es_adscrita, línea, razón_ici, razón_adscripción)
#
# El `detalle` es la única pista: dice dónde se publicó, con qué afiliación y en
# qué condición estaba el autor. Sin leerlo, el tablero no se resuelve.
PRODUCCIONES = [
    # ---------- Es ICI y es nuestra: cuenta para el informe ----------
    ("P01", "Eficiencia energética en edificios públicos de clima templado",
     "Artículo en revista indexada",
     "Publicado en 2026 con la afiliación de la institución. La autora tiene contrato "
     "vigente y jornada asignada a investigación.",
     True, True, "sostenibilidad",
     "Es investigación original con revisión de pares.",
     "Afiliación institucional declarada y autora con contrato vigente."),
    ("P02", "Sensor de humedad de bajo costo para agricultura urbana",
     "Prototipo con registro de propiedad",
     "Desarrollado por docentes y estudiantes con una empresa de la región. El registro "
     "de propiedad industrial quedó a nombre de la institución.",
     True, True, "productiva",
     "Innovación con desarrollo de producto y resultado verificable.",
     "El registro de propiedad está a nombre de la institución."),
    ("P03", "Trayectorias de titulación en carreras técnicas vespertinas",
     "Capítulo de libro",
     "Publicado en 2025 en un volumen con comité editorial, con afiliación institucional "
     "en la portadilla del capítulo.",
     True, True, "educacion",
     "Aporta conocimiento nuevo y pasó por comité editorial.",
     "La afiliación declarada es la de la institución."),
    ("P04", "Memoria fotográfica del borde costero",
     "Obra de creación con catálogo",
     "Exposición curada por un docente del área, financiada por el fondo interno de "
     "creación, con catálogo con ISBN a nombre de la institución.",
     True, True, "creacion",
     "La creación artística con producto verificable es producción ICI.",
     "Financiamiento interno y catálogo a nombre de la institución."),

    # ---------- Es ICI pero NO es nuestra ----------
    ("P05", "Modelos predictivos de deserción en educación superior",
     "Artículo en revista indexada",
     "Firmado por un docente de la institución, pero con la afiliación de la universidad "
     "donde cursa su doctorado. Es la única afiliación que aparece.",
     True, False, "educacion",
     "Es investigación: revista indexada y revisión de pares.",
     "La afiliación declarada es de otra institución. Quien la puede reclamar es "
     "quien figura en el artículo, no quien emplea al autor."),
    ("P06", "Adaptación de invernaderos a estrés hídrico",
     "Ponencia en congreso internacional",
     "Presentada en 2026 por una investigadora que dejó la institución en 2024. El "
     "trabajo se hizo íntegramente después de su salida.",
     True, False, "sostenibilidad",
     "Es producción científica presentada ante pares.",
     "La autora ya no pertenecía a la institución cuando se produjo el trabajo."),
    ("P07", "Proyecto de trazabilidad para la pequeña agroindustria",
     "Proyecto con financiamiento público",
     "La institución aparece como entidad asociada, sin aporte comprometido ni "
     "investigadores propios en el equipo ejecutor.",
     True, False, "productiva",
     "El proyecto es investigación aplicada con financiamiento concursable.",
     "Figurar como asociada sin aporte ni investigadores propios no habilita a "
     "reclamar el resultado."),
    ("P08", "Dispositivo de asistencia para terapia respiratoria",
     "Patente inscrita",
     "Un docente participó en el desarrollo a título personal, fuera de su jornada, y "
     "la patente quedó inscrita a nombre de una empresa privada.",
     True, False, "salud",
     "Una patente es producción de innovación.",
     "El docente participó a título personal y la titularidad es de un tercero."),

    # ---------- Es nuestra pero NO es ICI ----------
    ("P09", "Guía de apoyo para la asignatura de estadística descriptiva",
     "Material docente",
     "Elaborada por el equipo académico de la carrera y usada en tres sedes.",
     False, True, None,
     "Es material de enseñanza: organiza conocimiento existente, no produce "
     "conocimiento nuevo ni pasa por revisión de pares.",
     "Es producción propia de la institución."),
    ("P10", "Caracterización de la matrícula 2022-2026",
     "Informe interno de gestión",
     "Elaborado por la dirección de análisis institucional para la planificación anual.",
     False, True, None,
     "Es análisis de gestión para uso interno, sin pregunta de investigación ni "
     "método declarado ni difusión ante pares.",
     "Es un producto propio de la institución."),
    ("P11", "Charla «Inteligencia artificial en el trabajo administrativo»",
     "Actividad de difusión",
     "Dictada por un docente en la semana de la carrera, con asistencia de estudiantes "
     "y titulados.",
     False, True, None,
     "Difundir conocimiento existente no es producirlo. Es extensión, y como tal "
     "pertenece a vinculación con el medio.",
     "La actividad es de la institución."),
    ("P12", "Manual de procedimientos del laboratorio de electricidad",
     "Documento operativo",
     "Redactado por el coordinador del laboratorio para estandarizar el uso de equipos.",
     False, True, None,
     "Es un documento operativo: no responde una pregunta ni genera resultados nuevos.",
     "Es documentación propia de la institución."),

    # ---------- Ni una cosa ni la otra ----------
    ("P13", "Entrevista sobre contingencia económica en un medio regional",
     "Nota de prensa",
     "Un académico invitado a comentar en un noticiero; la nota lo identifica por su "
     "cargo en otra consultora.",
     False, False, None,
     "Una declaración en prensa no es producción de conocimiento.",
     "Se lo identifica por su rol en otra organización, no por la institución."),
    ("P14", "Tesis de magíster en gestión pública",
     "Tesis de posgrado",
     "Cursada por un funcionario en otra universidad, financiada por él y sin relación "
     "con su función en la institución.",
     False, False, None,
     "Una tesis de posgrado propia es formación del autor, no producción de la "
     "organización donde trabaja.",
     "Fue cursada y financiada fuera de la institución."),
    ("P15", "Difusión en redes de un artículo de terceros",
     "Publicación en redes sociales",
     "La cuenta institucional compartió un estudio publicado por otro centro.",
     False, False, None,
     "Compartir un trabajo ajeno no produce conocimiento.",
     "El estudio es de otro centro; la institución solo lo difundió."),
    ("P16", "Curso en línea «Excel para la gestión»",
     "Curso comercial en plataforma externa",
     "Un docente lo produjo y lo vende por su cuenta en una plataforma comercial, sin "
     "vínculo con su jornada ni con la institución.",
     False, False, None,
     "Es formación comercial, no producción de investigación, creación o innovación.",
     "Se produjo y se comercializa fuera de la institución."),
]
