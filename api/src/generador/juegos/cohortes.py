"""
Contenido de D2 Docencia — «El caso del estudiante que se pierde».

Casos de cohorte: cuántos estudiantes quedan en cada etapa, con la **referencia**
de cuánto se esperaría conservar en cada tramo. El juego es señalar dónde se
rompe y por qué.

Por qué la referencia se muestra: una caída no significa nada sin ella. Perder el
40% entre egreso y titulación oportuna es lo normal del sistema; perder el 35%
entre primero y segundo año es una hemorragia. Sin referencia, el juego premiaría
señalar el número más grande, que es justo el error que este juego existe para
desarmar.

Los indicadores están diseñados para que el paso 2 NO se resuelva con aritmética:
los cuatro muestran alguna desviación, y lo que distingue al correcto es que
**pertenece a la etapa donde se rompió**. Encontrar el quiebre es leer datos;
explicarlo es entender el proceso formativo. Son dos habilidades distintas y el
juego las cobra por separado.

TODO es contenido de prueba. Las cifras son sintéticas y no describen a ninguna
carrera de AIEP; en producción las reemplaza el corte real de la institución.
"""
from __future__ import annotations

ETAPAS = ["Ingreso", "1º año", "2º año", "3º año", "Egreso", "Titulación oportuna"]

# Cuánto se conserva normalmente en cada tramo. El último es bajo a propósito: la
# titulación oportuna es la brecha conocida del sistema, no una anomalía.
REFERENCIAS = [85, 88, 92, 90, 65]


def _caso(codigo, titulo, contexto, valores, quiebre, explicacion, indicadores, correcto,
          explicacion_indicador):
    return {
        "codigo": codigo,
        "titulo": titulo,
        "contexto": contexto,
        "etapas": [{"nombre": n, "valor": v} for n, v in zip(ETAPAS, valores)],
        "tramos": [
            {"desde": ETAPAS[i], "hasta": ETAPAS[i + 1], "referencia_pct": REFERENCIAS[i]}
            for i in range(len(REFERENCIAS))
        ],
        "tramo_quiebre": quiebre,
        "explicacion_quiebre": explicacion,
        "indicadores": [
            {"clave": c, "nombre": n, "valor": v} for c, n, v in indicadores
        ],
        "indicador_correcto": correcto,
        "explicacion_indicador": explicacion_indicador,
        "es_contenido_prueba": True,
    }


CASOS = [
    _caso(
        "D2-01",
        "La cohorte que no llega a segundo",
        "Cohorte 2022 de una carrera técnica de la Escuela de Administración. "
        "La dirección de carrera dice que el problema es la selección de entrada.",
        [240, 204, 128, 120, 108, 70],
        1,
        "Entre primero y segundo año se conserva el 63% donde se esperaría un 88%: "
        "veinticinco puntos bajo la referencia. La caída de egreso a titulación "
        "oportuna es mayor en número, pero está dentro de lo esperado — por eso la "
        "referencia importa más que el tamaño de la caída.",
        [
            ("asistencia", "Asistencia promedio en primer año", "78% (referencia 75%)"),
            ("alineacion", "Asignaturas de segundo año con evaluación alineada al perfil de egreso",
             "41% (referencia 85%)"),
            ("titulacion", "Actividades de titulación con plazo definido", "72% (referencia 80%)"),
            ("convenios", "Convenios de práctica vigentes", "63% (referencia 70%)"),
        ],
        "alineacion",
        "Los cuatro indicadores están bajo su referencia, pero solo uno ocurre en la "
        "etapa donde se pierde la cohorte. Si en segundo año se evalúa algo distinto "
        "de lo que el perfil promete, el estudiante reprueba sin saber qué le faltó.",
    ),
    _caso(
        "D2-02",
        "Los que se van antes de empezar",
        "Cohorte 2023 de una carrera del área de salud. La deserción se atribuye a "
        "razones económicas, pero nadie revisó el primer semestre.",
        [320, 214, 188, 173, 156, 100],
        0,
        "Del ingreso a primer año se conserva el 67% contra una referencia de 85%. "
        "Los demás tramos están en su rango: la cohorte no se desgrana, se derrumba "
        "de entrada.",
        [
            ("nivelacion", "Estudiantes de primer año con diagnóstico de entrada aplicado",
             "34% (referencia 90%)"),
            ("perfil", "Perfil de egreso publicado y vigente", "88% (referencia 95%)"),
            ("practica", "Plazas de práctica por estudiante de tercer año", "0,8 (referencia 1,0)"),
            ("empleadores", "Empleadores consultados en el último ciclo", "61% (referencia 70%)"),
        ],
        "nivelacion",
        "Sin diagnóstico de entrada no hay forma de activar el acompañamiento a "
        "tiempo: el sistema se entera de que el estudiante estaba en riesgo cuando "
        "ya se fue. Los otros tres indicadores son reales, pero ocurren después.",
    ),
    _caso(
        "D2-03",
        "Egresan y no se titulan",
        "Cohorte 2021 de una carrera profesional. La tasa de titulación aparece baja "
        "en el informe y la escuela sostiene que la formación es sólida.",
        [180, 153, 135, 124, 112, 47],
        4,
        "El 42% de titulación oportuna contra una referencia de 65% son veintitrés "
        "puntos de brecha. Y es el único tramo fuera de rango: la escuela tiene "
        "razón en que la formación se sostiene — el problema está en el cierre.",
        [
            ("aprendizaje", "Resultados de aprendizaje evaluados en segundo año",
             "82% (referencia 85%)"),
            ("retencion", "Retención de primer año", "84% (referencia 85%)"),
            ("titulacion", "Estudiantes egresados con actividad de titulación iniciada dentro del año",
             "38% (referencia 85%)"),
            ("vinculacion", "Actividades con el medio evaluadas", "24% (referencia 60%)"),
        ],
        "titulacion",
        "El egresado que no inicia su actividad de titulación dentro del año queda "
        "fuera del cálculo de titulación oportuna aunque haya aprobado todo. Es el "
        "único indicador que ocurre en el tramo donde se pierde la cohorte.",
    ),
    _caso(
        "D2-04",
        "El cuello de botella de la práctica",
        "Cohorte 2022 de una carrera con práctica obligatoria en tercer año.",
        [260, 221, 194, 142, 128, 84],
        2,
        "De segundo a tercer año se conserva el 73% donde se esperaría un 92%: "
        "diecinueve puntos. Es el tramo donde entra la práctica obligatoria.",
        [
            ("plazas", "Plazas de práctica disponibles por estudiante de tercer año",
             "0,6 (referencia 1,0)"),
            ("perfil", "Asignaturas de primer año alineadas al perfil", "79% (referencia 85%)"),
            ("titulacion", "Titulación oportuna del ciclo anterior", "61% (referencia 65%)"),
            ("docentes", "Docentes con evaluación de desempeño al día", "88% (referencia 90%)"),
        ],
        "plazas",
        "Con seis plazas cada diez estudiantes, cuatro no pueden avanzar aunque "
        "aprueben. Es una restricción de gestión que se manifiesta como problema "
        "académico, y por eso se busca en la etapa equivocada.",
    ),
    _caso(
        "D2-05",
        "Los que quedan a un paso del egreso",
        "Cohorte 2021 de una carrera de la Escuela de Informática.",
        [200, 170, 150, 138, 96, 63],
        3,
        "De tercer año a egreso se conserva el 70% contra una referencia de 90%. "
        "Los tramos anteriores están sanos: la cohorte llega bien y se pierde al "
        "final del recorrido formativo, no en el trámite de titulación.",
        [
            ("integradora", "Asignaturas integradoras de último año con criterios de evaluación publicados",
             "29% (referencia 80%)"),
            ("nivelacion", "Cobertura del diagnóstico de entrada", "91% (referencia 90%)"),
            ("empleadores", "Empleadores que respondieron la consulta", "58% (referencia 70%)"),
            ("titulacion", "Actividad de titulación iniciada dentro del año", "79% (referencia 85%)"),
        ],
        "integradora",
        "La asignatura integradora es donde el perfil de egreso se verifica entero. "
        "Sin criterios publicados, el estudiante llega a ella sin saber contra qué "
        "se lo evalúa, y es justo el punto donde la cohorte se detiene.",
    ),
    _caso(
        "D2-06",
        "Dos años que no se parecen",
        "Cohorte 2023 de una carrera vespertina. El informe anterior decía que el "
        "problema era la asistencia.",
        [150, 128, 84, 78, 70, 46],
        1,
        "El 66% de primero a segundo contra un 88% de referencia. La asistencia "
        "está sobre su referencia: el problema no es que no vengan.",
        [
            ("asistencia", "Asistencia promedio en primer año", "81% (referencia 75%)"),
            ("progresion", "Estudiantes de segundo año con seguimiento de progresión registrado",
             "22% (referencia 80%)"),
            ("vcm", "Actividades de vinculación con evaluación de impacto", "18% (referencia 50%)"),
            ("titulacion", "Titulación oportuna", "63% (referencia 65%)"),
        ],
        "progresion",
        "Si nadie registra cómo avanza la cohorte en segundo año, el rezago se "
        "detecta cuando ya es abandono. La asistencia está bien y aun así se pierden: "
        "venir no es lo mismo que avanzar.",
    ),
]
