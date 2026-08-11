"""
Contenido de D4 Vinculación — «El mapa de contrapartes».

Dos catálogos: **acciones institucionales** (lo que la institución hace con el
medio) y **actores externos** (con quién). El juego es tender el vínculo correcto.

La pieza que hace que esto enseñe algo y no sea un emparejamiento cualquiera:
**no todos los actores son contrapartes**. Un proveedor de insumos, una agencia
de publicidad contratada o el banco donde están las cuentas son relaciones reales
de la institución, y ninguna es vinculación con el medio — falta lo que define a
la vinculación: propósito institucional y beneficio en las dos direcciones.

Distinguir eso es exactamente lo que discute un comité cuando arma el listado de
convenios para el informe, y es donde se infla el número sin querer.

TODO es contenido de prueba: los actores son plausibles pero inventados, y
ninguno describe un convenio real de AIEP. En la fase de contenido real, AIEP
entrega sus convenios y contrapartes efectivas (ver `DUDAS.md`).
"""
from __future__ import annotations

ACCIONES = [
    ("practica", "Convenio de práctica con seguimiento de desempeño",
     "Plazas de práctica con supervisión compartida y retroalimentación al plan de estudios"),
    ("curricular", "Consulta al perfil de egreso y actualización curricular",
     "El entorno productivo revisa el perfil y sus observaciones entran al rediseño"),
    ("capacitacion", "Educación continua para el entorno",
     "Cursos y capacitación que la institución ofrece a organizaciones del territorio"),
    ("investigacion", "Proyecto de investigación aplicada con contraparte",
     "Un problema real de la contraparte se trabaja con docentes y estudiantes"),
    ("articulacion", "Articulación con enseñanza media",
     "Trabajo con establecimientos escolares para acompañar la transición a la educación superior"),
    ("servicio", "Servicio a la comunidad con aprendizaje curricularizado",
     "Estudiantes atienden una necesidad del territorio como parte de una asignatura"),
    ("empleabilidad", "Seguimiento de titulados y consulta a empleadores",
     "Se levanta cómo les va a los titulados y qué observa quien los contrata"),
    ("territorial", "Mesa de trabajo territorial",
     "Instancia permanente con la autoridad local para priorizar necesidades del sector"),
    ("certificacion", "Certificación de competencias con el gremio",
     "El gremio del sector reconoce y certifica competencias formadas en la institución"),
    ("cultural", "Extensión cultural abierta a la comunidad",
     "Actividades culturales de la institución abiertas al territorio"),
]

# (código, nombre, tipo, descripción, acción o None, razón)
#
# Los de acción None son el corazón del juego: relaciones reales que NO son
# vinculación. La razón explica qué les falta, que es siempre lo mismo — propósito
# institucional compartido y beneficio en las dos direcciones.
ACTORES = [
    ("A01", "Constructora regional del rubro obras civiles", "empresa",
     "Recibe doce estudiantes al año y su jefatura evalúa el desempeño junto al docente tutor.",
     "practica",
     "Hay trabajo conjunto y la evaluación vuelve al plan de estudios: es vinculación."),
    ("A02", "Consejo asesor empresarial del área de administración", "gremio",
     "Se reúne dos veces al año a revisar si el perfil de egreso responde a lo que el sector necesita.",
     "curricular",
     "Su observación entra al rediseño curricular; ese retorno es lo que lo hace vinculación."),
    ("A03", "Municipalidad de la comuna", "servicio_publico",
     "Convoca a las instituciones del territorio a priorizar necesidades del sector.",
     "territorial",
     "Instancia permanente con la autoridad local: es la forma típica de la mesa territorial."),
    ("A04", "Asociación de titulados de la carrera", "titulados",
     "Responde la consulta anual sobre trayectoria laboral y pertinencia de la formación.",
     "empleabilidad",
     "El seguimiento de titulados es evidencia directa de resultados del proceso formativo."),
    ("A05", "Colegio profesional de contadores de la región", "colegio_profesional",
     "Reconoce competencias formadas en la institución mediante un examen conjunto.",
     "certificacion",
     "La certificación con el gremio da validación externa a lo que la institución forma."),
    ("A06", "Liceo técnico-profesional de la comuna", "establecimiento_escolar",
     "Sus estudiantes de cuarto medio participan en talleres de la institución.",
     "articulacion",
     "Acompañar la transición a la educación superior es vinculación con propósito formativo."),
    ("A07", "Centro de salud familiar del sector", "servicio_publico",
     "Estudiantes de la carrera atienden un programa de prevención como parte de una asignatura.",
     "servicio",
     "El servicio está curricularizado: la comunidad recibe y el estudiante aprende."),
    ("A08", "Cámara de comercio local", "gremio",
     "Sus asociados toman cursos de gestión dictados por la institución.",
     "capacitacion",
     "La educación continua hacia el entorno es una vía reconocida de vinculación."),
    ("A09", "Empresa de logística del parque industrial", "empresa",
     "Trajo un problema de mermas y se trabaja con docentes y estudiantes en un proyecto.",
     "investigacion",
     "Un problema real de la contraparte trabajado con la institución: investigación aplicada."),
    ("A10", "Corporación cultural municipal", "organizacion_social",
     "Coprograma el ciclo de actividades abiertas que la institución ofrece al barrio.",
     "cultural",
     "La extensión cultural abierta al territorio es vinculación cuando hay coprogramación."),
    ("A11", "Junta de vecinos del sector norte", "organizacion_social",
     "Levantó una necesidad de alfabetización digital que estudiantes atienden en terreno.",
     "servicio",
     "La necesidad la pone la comunidad y el trabajo es parte de una asignatura."),
    ("A12", "Sindicato de trabajadores del comercio", "gremio",
     "Sus afiliados cursan un programa de nivelación de competencias.",
     "capacitacion",
     "Formación hacia una organización del territorio, con acuerdo y seguimiento."),
    ("A13", "Hospital regional", "servicio_publico",
     "Mantiene campo clínico con supervisión conjunta y evaluación del desempeño.",
     "practica",
     "El campo clínico es práctica con seguimiento: el caso clásico de vinculación."),
    ("A14", "Fundación de apoyo a la primera infancia", "organizacion_social",
     "Recibe apoyo de estudiantes en un programa de estimulación temprana.",
     "servicio",
     "Servicio a la comunidad con aprendizaje: hay beneficio en las dos direcciones."),
    ("A15", "Red de empleadores del sector gastronómico", "empresa",
     "Reporta cada semestre qué observa en los titulados que contrata.",
     "empleabilidad",
     "La consulta a empleadores cierra el ciclo entre formación y desempeño."),

    # ---- No son contrapartes. Acá está el juego. ----
    ("A16", "Proveedor de insumos de aseo del campus", "proveedor",
     "Abastece los edificios bajo contrato de suministro renovado cada año.",
     None,
     "Es una relación de abastecimiento. La institución paga y recibe un producto: "
     "no hay propósito formativo compartido ni beneficio para el proveedor más allá "
     "del contrato."),
    ("A17", "Agencia de publicidad de la campaña de admisión", "proveedor",
     "Diseña y ejecuta la campaña anual de matrícula.",
     None,
     "Es un servicio contratado. El beneficio va en una sola dirección y el propósito "
     "es comercial, no de vinculación con el medio."),
    ("A18", "Diario regional que publicó una nota sobre la institución", "medio",
     "Cubrió la ceremonia de titulación en su edición dominical.",
     None,
     "Difusión no es vinculación: no hay trabajo conjunto, ni acuerdo, ni algo que "
     "vuelva al proceso formativo. Contarlo como convenio infla el listado."),
    ("A19", "Empresa que licencia el sistema de gestión académica", "proveedor",
     "Vende y mantiene el software donde se registran las notas.",
     None,
     "Proveedor tecnológico. Que el vínculo sea estable y necesario no lo convierte "
     "en vinculación con el medio."),
    ("A20", "Banco donde la institución tiene sus cuentas", "proveedor",
     "Administra las cuentas corrientes y el pago de remuneraciones.",
     None,
     "Servicio financiero. Es una relación institucional real, y ninguna de las dos "
     "partes está persiguiendo un fin formativo compartido."),
]
