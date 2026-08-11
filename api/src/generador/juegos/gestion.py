"""
Contenido de D1 Gestión — «El presupuesto de la acreditación».

Tres semestres de decisión, un presupuesto que no alcanza, y consecuencias que
llegan **dos semestres después**. Es la única mecánica del sistema con estado que
evoluciona: lo que se decide en el primer semestre se ve recién en el tercero.

Cada escenario tiene una **regla encadenada**: un frente está limitado por otro.
Es lo que convierte el reparto en una decisión y no en una suma — el indicador
que la acreditación mira de frente está tapado por uno que nadie mira, y volcar
todo en el visible lo deja en su techo mientras el resto se desmorona.

Tres supuestos que hacen que decidir duela, y que van a la vista del jugador:

- **Todo se desgasta.** No atender un frente es una decisión, no una pausa.
- **Lo que excede el techo se pierde.** No queda esperando a que el habilitador
  suba: se evapora en ese turno.
- **El presupuesto total alcanza para unos 13 o 14 de los 18 cupos necesarios si
  se ordena bien, y para nada si se reparte parejo.**

`solucion_ejemplo` NO viaja al cliente: existe para que el validador compruebe
que el escenario se puede ganar de verdad, simulándolo.

TODO es contenido de prueba. Las cifras son sintéticas y no describen la gestión
de ninguna institución.
"""
from __future__ import annotations

ESCENARIOS = [
    {
        "codigo": "G1",
        "titulo": "El informe que nadie puede documentar",
        "contexto": "Quedan tres semestres para entregar el informe de autoevaluación. "
                    "El comité insiste en reforzar la evidencia y la dirección quiere ver "
                    "movimiento en ese indicador cuanto antes.",
        "turnos": 5,
        "turnos_de_decision": 3,
        "presupuesto": 5,
        "retardo": 2,
        "frentes": [
            {"clave": "evidencia", "nombre": "Evidencia documentada",
             "descripcion": "Respaldos verificables de lo que la institución declara",
             "inicial": 45, "desgaste": 6, "efecto": 9, "umbral": 58},
            {"clave": "dotacion", "nombre": "Dotación y carga docente",
             "descripcion": "Horas asignadas y equipos completos en las unidades",
             "inicial": 55, "desgaste": 4, "efecto": 7, "umbral": 60},
            {"clave": "infraestructura", "nombre": "Infraestructura y equipamiento",
             "descripcion": "Salas, laboratorios y equipos en condiciones de uso",
             "inicial": 60, "desgaste": 3, "efecto": 6, "umbral": 48},
            {"clave": "sistemas", "nombre": "Sistemas de información",
             "descripcion": "Lo que la institución es capaz de registrar y recuperar",
             "inicial": 35, "desgaste": 2, "efecto": 8, "umbral": 45},
        ],
        "regla": {
            "frente": "evidencia", "habilitador": "sistemas", "base": 30, "factor": 0.7,
            "texto": "No se puede documentar lo que el sistema no registra: la evidencia "
                     "no supera 30 + 0,7 × sistemas de información, y lo que exceda ese "
                     "techo se pierde.",
        },
        # sistemas primero (llega al 3º), dotación al medio, evidencia al final.
        "solucion_ejemplo": [
            {"sistemas": 3, "infraestructura": 1},
            {"dotacion": 4},
            {"evidencia": 5},
        ],
        "cierre": "La evidencia es lo que se mira, pero está tapada por lo que nadie "
                  "mira. Invertir en sistemas al final no alcanza: llega cuando el "
                  "período ya cerró.",
    },
    {
        "codigo": "G2",
        "titulo": "El plan de mejora que nadie ejecuta",
        "contexto": "El plan de mejora está escrito y aprobado. Lleva dos años sin "
                    "avanzar y cada informe repite los mismos compromisos.",
        "turnos": 5,
        "turnos_de_decision": 3,
        "presupuesto": 5,
        "retardo": 2,
        "frentes": [
            {"clave": "plan", "nombre": "Avance del plan de mejora",
             "descripcion": "Compromisos con responsable, plazo y avance verificable",
             "inicial": 40, "desgaste": 6, "efecto": 10, "umbral": 58},
            {"clave": "personas", "nombre": "Dotación y competencias",
             "descripcion": "Gente con el tiempo y la formación para ejecutar",
             "inicial": 50, "desgaste": 4, "efecto": 7, "umbral": 58},
            {"clave": "presupuesto", "nombre": "Ejecución presupuestaria",
             "descripcion": "Recursos comprometidos que efectivamente se gastan",
             "inicial": 62, "desgaste": 3, "efecto": 6, "umbral": 50},
            {"clave": "gobernanza", "nombre": "Instancias de decisión",
             "descripcion": "Comités que sesionan, revisan y corrigen el rumbo",
             "inicial": 38, "desgaste": 2, "efecto": 8, "umbral": 48},
        ],
        "regla": {
            "frente": "plan", "habilitador": "gobernanza", "base": 25, "factor": 0.8,
            "texto": "Un plan sin instancia que lo revise no avanza: el plan no supera "
                     "25 + 0,8 × instancias de decisión, y el exceso se pierde.",
        },
        "solucion_ejemplo": [
            {"gobernanza": 3, "presupuesto": 1},
            {"personas": 4},
            {"plan": 5},
        ],
        "cierre": "Un plan de mejora no se acelera escribiéndolo mejor. Sin una "
                  "instancia que lo revise y corrija, el avance tiene techo.",
    },
    {
        "codigo": "G3",
        "titulo": "La sede nueva que no alcanza a consolidarse",
        "contexto": "Una sede abrió hace dos años con edificio nuevo y equipamiento "
                    "recién comprado. El aseguramiento de la calidad quedó para después.",
        "turnos": 5,
        "turnos_de_decision": 3,
        "presupuesto": 5,
        "retardo": 2,
        "frentes": [
            {"clave": "aseguramiento", "nombre": "Aseguramiento interno instalado",
             "descripcion": "Procesos de calidad funcionando en la sede, no en el papel",
             "inicial": 42, "desgaste": 6, "efecto": 10, "umbral": 58},
            {"clave": "equipamiento", "nombre": "Equipamiento operativo",
             "descripcion": "Equipos con mantención y reposición al día",
             "inicial": 58, "desgaste": 4, "efecto": 7, "umbral": 60},
            {"clave": "infraestructura", "nombre": "Infraestructura",
             "descripcion": "Recintos suficientes para la matrícula proyectada",
             "inicial": 65, "desgaste": 3, "efecto": 6, "umbral": 49},
            {"clave": "dotacion", "nombre": "Dotación de la sede",
             "descripcion": "Cargos provistos y con permanencia",
             "inicial": 40, "desgaste": 2, "efecto": 8, "umbral": 48},
        ],
        "regla": {
            "frente": "aseguramiento", "habilitador": "dotacion", "base": 28,
            "factor": 0.7,
            "texto": "Sin gente que lo sostenga no hay sistema de calidad: el "
                     "aseguramiento no supera 28 + 0,7 × dotación de la sede, y el "
                     "exceso se pierde.",
        },
        "solucion_ejemplo": [
            {"dotacion": 3},
            {"equipamiento": 4},
            {"aseguramiento": 5},
        ],
        "cierre": "Un edificio nuevo no instala calidad. El aseguramiento se sostiene "
                  "con gente, y la gente demora dos semestres en estar en régimen.",
    },
]
