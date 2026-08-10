"""
Docencia y Resultados del Proceso de Formación — base de conocimiento.

CONTENIDO DE PRUEBA. Valida la máquina, no es material oficial de acreditación.
"""
from ..tipos import Concepto, Dimension, Distractor as D

DOCENCIA = Dimension(
    codigo="DOCENCIA",
    nombre_oficial="Docencia y Resultados del Proceso de Formación",
    encuadre=(
        "Esta dimensión mira lo que le pasa al estudiante: si aprende lo que se le prometió, "
        "si avanza y si llega a titularse."
    ),
    conceptos=(
        Concepto(
            codigo="DOCENCIA-01", nombre="El perfil de egreso", nivel_minimo=1,
            microlearning=(
                "El perfil de egreso es la promesa formativa: lo que la persona titulada será "
                "capaz de hacer. Es el punto de partida de todo lo demás, porque el plan de "
                "estudios y las evaluaciones deberían poder rastrearse hasta él. Cuando un "
                "estudiante se titula sin haber sido evaluado en alguna capacidad prometida, el "
                "perfil dejó de ser una promesa y pasó a ser un texto de folleto."
            ),
            definicion=(
                "La declaración de lo que la persona titulada será capaz de hacer, que orienta "
                "el plan de estudios y sus evaluaciones"
            ),
            confusiones=(
                D("El conjunto de asignaturas que el estudiante debe aprobar para titularse",
                  "Esa es la malla; el perfil declara capacidades, no asignaturas."),
                D("El perfil laboral que demanda el sector productivo para el área de la carrera",
                  "La demanda del sector informa el perfil, pero no lo reemplaza."),
                D("Los requisitos de ingreso que definen el estudiante esperado para la carrera",
                  "Eso describe la entrada; el perfil describe la salida."),
            ),
            explicacion_definicion=(
                "El perfil declara capacidades de salida y por eso puede usarse como vara para "
                "revisar el plan y las evaluaciones."
            ),
            escenario=(
                "Al revisar la carrera se detecta que una capacidad del perfil de egreso no se "
                "evalúa en ninguna asignatura. ¿Qué corresponde?"
            ),
            accion_correcta=(
                "Levantarlo como brecha de consistencia y definir dónde y cómo se evaluará esa "
                "capacidad"
            ),
            acciones_incorrectas=(
                D("Retirar esa capacidad del perfil de egreso, ya que no se está evaluando",
                  "Ajustar la promesa a lo que se hace renuncia a formar lo que se declaró necesario."),
                D("Suponerla cubierta de manera transversal por el conjunto de las asignaturas",
                  "Lo transversal sin responsable concreto es lo que nadie termina evaluando."),
                D("Incorporarla a la evaluación final de título, sin modificar las asignaturas",
                  "Evaluar al final algo que nunca se trabajó traslada el problema al estudiante."),
            ),
            explicacion_escenario=(
                "La consistencia entre perfil, plan y evaluación es exactamente lo que se revisa: "
                "declarar la brecha es el primer paso."
            ),
        ),
        Concepto(
            codigo="DOCENCIA-02", nombre="La progresión académica", nivel_minimo=1,
            microlearning=(
                "La progresión describe cómo avanzan las cohortes: cuántos siguen, cuántos "
                "repiten, cuántos se atrasan y dónde se produce el atasco. Mirarla por cohorte y "
                "no por promedio general es lo que permite ver el problema real, porque los "
                "promedios institucionales suelen esconder asignaturas críticas donde se concentra "
                "el rezago."
            ),
            definicion=(
                "El avance de las cohortes a lo largo del plan de estudios, que permite ubicar "
                "dónde se concentran el rezago y la reprobación"
            ),
            confusiones=(
                D("El porcentaje de estudiantes que se mantiene matriculado de un año al siguiente",
                  "Eso es retención: dice si siguen, no si avanzan en el plan."),
                D("El rendimiento promedio obtenido por los estudiantes en cada asignatura",
                  "El promedio de notas no muestra el avance de la cohorte en el plan."),
                D("La proporción de estudiantes que se titula dentro del plazo formal",
                  "Esa es la titulación oportuna: es el desenlace, no la trayectoria."),
            ),
            explicacion_definicion=(
                "La progresión se lee por cohorte y a lo largo del plan; ahí aparece dónde se "
                "produce el atasco."
            ),
            escenario=(
                "Una asignatura de segundo año concentra el 40% de las reprobaciones de la "
                "carrera. ¿Cuál es el aporte más útil?"
            ),
            accion_correcta=(
                "Analizar la asignatura como nudo crítico: sus requisitos, su evaluación y el "
                "apoyo disponible, y actuar sobre eso"
            ),
            acciones_incorrectas=(
                D("Ajustar la exigencia de la asignatura hasta normalizar la tasa de reprobación",
                  "Bajar la exigencia mejora el indicador y empeora la formación prometida."),
                D("Reportar la tasa como parte de los resultados académicos del período",
                  "Reportar sin analizar deja el nudo crítico exactamente donde estaba."),
                D("Trasladar la asignatura a un semestre posterior del plan de estudios",
                  "Moverla de lugar sin entender la causa suele reproducir el problema."),
            ),
            explicacion_escenario=(
                "Un nudo crítico identificado es una oportunidad concreta de mejora; "
                "normalizarlo bajando la vara desperdicia el hallazgo."
            ),
        ),
        Concepto(
            codigo="DOCENCIA-03", nombre="La evaluación de aprendizajes", nivel_minimo=1,
            microlearning=(
                "Evaluar aprendizajes es verificar si el estudiante logró lo que la asignatura se "
                "propuso. La pregunta de calidad no es cuántas evaluaciones hay, sino si lo que "
                "se evalúa corresponde a lo que se declaró enseñar. Un instrumento que mide "
                "memoria cuando el resultado esperado era aplicación no está evaluando el "
                "aprendizaje comprometido."
            ),
            definicion=(
                "La verificación de si el estudiante logró los resultados de aprendizaje "
                "declarados, con instrumentos coherentes con ellos"
            ),
            confusiones=(
                D("El conjunto de calificaciones que el estudiante obtiene durante el semestre",
                  "Las calificaciones son el registro; la evaluación es el proceso que las produce."),
                D("La aplicación de instrumentos estandarizados al término de cada nivel formativo",
                  "Estandarizar es una opción metodológica, no la definición de evaluar."),
                D("La medición de la satisfacción del estudiante con la asignatura cursada",
                  "La satisfacción mide experiencia, no logro de aprendizaje."),
            ),
            explicacion_definicion=(
                "Lo decisivo es la coherencia entre el instrumento y el resultado de aprendizaje "
                "declarado."
            ),
            escenario=(
                "Una asignatura declara que el estudiante «aplicará» un procedimiento, pero "
                "evalúa solo con preguntas de definición. ¿Qué corresponde?"
            ),
            accion_correcta=(
                "Ajustar el instrumento para que exija aplicar el procedimiento, no solo "
                "describirlo"
            ),
            acciones_incorrectas=(
                D("Modificar el resultado de aprendizaje para que hable de conocer el procedimiento",
                  "Rebajar el resultado para calzar con el instrumento reduce la formación."),
                D("Agregar más preguntas de definición para cubrir el contenido con mayor amplitud",
                  "Más preguntas del mismo tipo no cambian el nivel cognitivo que se evalúa."),
                D("Mantener el instrumento y complementarlo con la asistencia a las prácticas",
                  "La asistencia registra presencia, no logro de aplicación."),
            ),
            explicacion_escenario=(
                "Si el resultado dice aplicar, el instrumento tiene que pedir aplicar. Esa es la "
                "consistencia que se revisa."
            ),
        ),
        Concepto(
            codigo="DOCENCIA-04", nombre="La titulación oportuna", nivel_minimo=1,
            microlearning=(
                "La titulación oportuna mide qué proporción de una cohorte se titula dentro del "
                "plazo formal de la carrera. Es un indicador exigente porque resume muchas cosas: "
                "diseño del plan, apoyo al estudiante, procesos administrativos de titulación. "
                "Cuando está bajo, conviene desagregar antes de concluir: a veces el problema no "
                "es académico sino un trámite final que se demora meses."
            ),
            definicion=(
                "La proporción de una cohorte que obtiene su título dentro del plazo formal "
                "previsto por la carrera"
            ),
            confusiones=(
                D("El número total de personas tituladas por la institución durante el año",
                  "El total absoluto no dice nada sobre oportunidad ni sobre la cohorte."),
                D("La proporción de estudiantes que aprueba la actividad final de titulación",
                  "Esa tasa mide un hito puntual, no la trayectoria completa de la cohorte."),
                D("El tiempo promedio que tardan los estudiantes en completar el plan de estudios",
                  "El promedio de duración es un indicador relacionado pero distinto."),
            ),
            explicacion_definicion=(
                "Se mide sobre la cohorte y contra el plazo formal: por eso resume el "
                "funcionamiento de toda la trayectoria."
            ),
            escenario=(
                "La titulación oportuna cayó, y al desagregar se ve que los estudiantes terminan "
                "las asignaturas a tiempo pero demoran ocho meses en el trámite final. ¿Qué haces?"
            ),
            accion_correcta=(
                "Intervenir el proceso administrativo de titulación, que es donde está la demora "
                "real"
            ),
            acciones_incorrectas=(
                D("Reforzar el acompañamiento académico durante los últimos semestres de la carrera",
                  "Reforzar lo académico no toca la causa: el atraso está después de las asignaturas."),
                D("Ampliar el plazo formal de la carrera para que el indicador refleje la realidad",
                  "Ampliar el plazo mejora el indicador sin acortar la espera del estudiante."),
                D("Excluir del cálculo a quienes tienen el trámite de titulación en curso",
                  "Excluirlos maquilla el indicador y esconde el problema que se acaba de encontrar."),
            ),
            explicacion_escenario=(
                "Desagregar sirvió justamente para eso: la causa es administrativa y ahí es donde "
                "hay que actuar."
            ),
        ),
        Concepto(
            codigo="DOCENCIA-05", nombre="La retención", nivel_minimo=1,
            microlearning=(
                "La retención mide cuántos estudiantes siguen matriculados de un período al "
                "siguiente. Es de los primeros indicadores que se mira porque la deserción "
                "temprana concentra buena parte del problema. Distinguir entre quien se va de la "
                "institución y quien cambia de carrera dentro de ella es clave: son fenómenos "
                "distintos y piden respuestas distintas."
            ),
            definicion=(
                "La proporción de estudiantes que continúa matriculada de un período académico "
                "al siguiente"
            ),
            confusiones=(
                D("La proporción de estudiantes que completa el plan de estudios de su carrera",
                  "Eso es la trayectoria completa; la retención mira período a período."),
                D("El porcentaje de vacantes que la institución logra llenar en cada admisión",
                  "Llenar vacantes es captación, no retención."),
                D("La satisfacción declarada por los estudiantes con su experiencia formativa",
                  "La satisfacción puede explicar la retención, pero no la mide."),
            ),
            explicacion_definicion=(
                "Se mide entre períodos consecutivos, y por eso detecta temprano lo que la "
                "titulación solo mostraría años después."
            ),
            escenario=(
                "La retención de primer año bajó cinco puntos. Antes de proponer medidas, ¿cuál "
                "es el paso más útil?"
            ),
            accion_correcta=(
                "Desagregar por carrera, sede y motivo de salida para saber si el fenómeno es "
                "general o está concentrado"
            ),
            acciones_incorrectas=(
                D("Implementar un programa de acompañamiento transversal para todos los ingresos",
                  "Actuar sin desagregar reparte el esfuerzo donde quizá no está el problema."),
                D("Comparar el indicador con el de instituciones similares del mismo segmento",
                  "El referente externo no dice dónde está la caída dentro de la institución."),
                D("Revisar los requisitos de admisión para mejorar el perfil de ingreso",
                  "Cambiar la admisión es una respuesta de largo plazo a un dato aún sin diagnóstico."),
            ),
            explicacion_escenario=(
                "Casi siempre la caída está concentrada en pocas carreras o sedes; sin desagregar "
                "se diseña una respuesta genérica."
            ),
        ),
        Concepto(
            codigo="DOCENCIA-06", nombre="El acompañamiento estudiantil", nivel_minimo=1,
            microlearning=(
                "El acompañamiento es el conjunto de apoyos —nivelación, tutorías, orientación— "
                "que la institución pone para que el estudiante avance. Para que cuente como "
                "mecanismo necesita criterios de activación: a quién se dirige, cómo se detecta a "
                "esa persona y qué pasa si no responde. Un apoyo que solo llega a quien lo pide "
                "no alcanza a quien más lo necesita."
            ),
            definicion=(
                "El conjunto de apoyos con criterios definidos de activación y seguimiento, "
                "orientados a que el estudiante avance en su trayectoria"
            ),
            confusiones=(
                D("Los beneficios económicos y becas que la institución otorga a sus estudiantes",
                  "El apoyo económico es otro tipo de ayuda, con lógica distinta."),
                D("La atención que cada docente brinda a sus estudiantes durante la asignatura",
                  "La atención individual es valiosa pero no constituye un mecanismo institucional."),
                D("Las actividades extracurriculares que enriquecen la experiencia estudiantil",
                  "Enriquecen la experiencia, pero no están orientadas a la trayectoria académica."),
            ),
            explicacion_definicion=(
                "Los criterios de activación y el seguimiento son lo que convierte un apoyo "
                "disponible en un mecanismo."
            ),
            escenario=(
                "El programa de tutorías existe hace tres años y solo lo usa el 4% de los "
                "estudiantes, casi todos de buen rendimiento. ¿Qué corresponde?"
            ),
            accion_correcta=(
                "Cambiar a un modelo de detección activa que convoque a quienes muestran señales "
                "de rezago"
            ),
            acciones_incorrectas=(
                D("Difundir el programa con más fuerza para aumentar la cobertura entre estudiantes",
                  "Más difusión sobre un modelo voluntario tiende a atraer al mismo perfil."),
                D("Hacer obligatoria la tutoría para todos los estudiantes de primer año",
                  "La obligatoriedad universal gasta el recurso donde no hace falta."),
                D("Evaluar el impacto del programa en quienes efectivamente participaron",
                  "Medir el impacto en un 4% autoseleccionado no dice si el programa sirve."),
            ),
            explicacion_escenario=(
                "Que lo usen los de buen rendimiento es la señal: el mecanismo no está llegando a "
                "quien debía."
            ),
        ),
        Concepto(
            codigo="DOCENCIA-07", nombre="La innovación curricular", nivel_minimo=2,
            microlearning=(
                "Innovar el currículo es modificarlo con fundamento: a partir de resultados "
                "observados, de la evolución del campo laboral o de brechas detectadas. Lo que "
                "distingue una innovación de un cambio administrativo es que se declara qué "
                "problema busca resolver y se define cómo se sabrá si funcionó. Sin eso, cada "
                "rediseño borra la evidencia del anterior."
            ),
            definicion=(
                "La modificación fundamentada del currículo, con un problema declarado y un "
                "criterio definido para evaluar su efecto"
            ),
            confusiones=(
                D("La actualización periódica de los contenidos de las asignaturas del plan",
                  "Actualizar contenidos es mantenimiento, no innovación curricular."),
                D("La incorporación de tecnología digital en las actividades de enseñanza",
                  "La tecnología puede ser un medio, pero no define la innovación."),
                D("El rediseño del plan de estudios exigido por un cambio en la normativa",
                  "Un cambio por obligación externa no necesariamente parte de un problema propio."),
            ),
            explicacion_definicion=(
                "Problema declarado y criterio de evaluación: sin ambos no se puede saber si la "
                "innovación sirvió."
            ),
            escenario=(
                "Se propone rediseñar el plan de una carrera cuyo rediseño anterior fue hace dos "
                "años y nunca se evaluó. ¿Qué planteas?"
            ),
            accion_correcta=(
                "Evaluar primero el efecto del rediseño anterior, para no perder la única "
                "evidencia disponible"
            ),
            acciones_incorrectas=(
                D("Avanzar con el nuevo rediseño e incorporar la evaluación del anterior al proceso",
                  "Evaluar mientras se cambia mezcla los efectos y no permite atribuir nada."),
                D("Rediseñar solo las asignaturas que no fueron modificadas en el proceso anterior",
                  "Acotar el alcance no resuelve que no se sepa si lo anterior funcionó."),
                D("Postergar cualquier rediseño hasta completar un ciclo formativo íntegro",
                  "Esperar un ciclo completo puede ser demasiado si hay un problema urgente."),
            ),
            explicacion_escenario=(
                "Rediseñar sobre un rediseño no evaluado borra la evidencia y deja a la carrera "
                "sin saber qué funcionó."
            ),
        ),
        Concepto(
            codigo="DOCENCIA-08", nombre="Los resultados de aprendizaje", nivel_minimo=2,
            microlearning=(
                "Un resultado de aprendizaje describe qué será capaz de hacer el estudiante al "
                "terminar una unidad o asignatura, en términos observables. La diferencia con un "
                "objetivo de enseñanza es el sujeto: el objetivo habla de lo que hará el docente, "
                "el resultado de lo que podrá hacer el estudiante. Esa distinción es la que "
                "permite después evaluarlo."
            ),
            definicion=(
                "La descripción observable de lo que el estudiante será capaz de hacer al "
                "finalizar una unidad o asignatura"
            ),
            confusiones=(
                D("Los contenidos que serán abordados durante el desarrollo de la asignatura",
                  "El contenido es lo que se trata; el resultado es lo que la persona podrá hacer."),
                D("Las actividades de enseñanza que el docente implementará en cada sesión",
                  "Eso describe el trabajo del docente, no la capacidad del estudiante."),
                D("Las calificaciones esperadas para el conjunto del curso al cierre del período",
                  "La calificación esperada es una meta de resultado, no un aprendizaje descrito."),
            ),
            explicacion_definicion=(
                "El sujeto es el estudiante y el verbo tiene que ser observable: eso es lo que "
                "lo hace evaluable."
            ),
            escenario=(
                "Un programa declara como resultado de aprendizaje «comprender la importancia de "
                "la calidad». ¿Qué observas?"
            ),
            accion_correcta=(
                "Que «comprender» no es observable y hay que redactarlo con un desempeño "
                "verificable"
            ),
            acciones_incorrectas=(
                D("Que el resultado es adecuado y basta con definir un instrumento que lo mida",
                  "No se puede construir un instrumento sólido sobre un verbo no observable."),
                D("Que falta precisar a qué ámbito de la calidad se refiere el resultado",
                  "Precisar el ámbito ayuda, pero el problema de fondo sigue siendo el verbo."),
                D("Que debe complementarse con resultados actitudinales del mismo nivel",
                  "Agregar más resultados difusos multiplica el problema en vez de resolverlo."),
            ),
            explicacion_escenario=(
                "Verbos como comprender o conocer no se pueden observar; hay que traducirlos a un "
                "desempeño concreto."
            ),
        ),
        Concepto(
            codigo="DOCENCIA-09", nombre="La empleabilidad de titulados", nivel_minimo=3,
            microlearning=(
                "La empleabilidad indaga qué pasa con las personas tituladas después: si se "
                "insertan, en qué tipo de ocupación y con qué relación con lo que estudiaron. Es "
                "un indicador delicado porque depende fuertemente del contexto económico, así que "
                "se interpreta junto con la percepción de empleadores y con la trayectoria del "
                "sector, nunca solo."
            ),
            definicion=(
                "La inserción laboral de las personas tituladas y su relación con el área de "
                "formación, leída junto al contexto del sector"
            ),
            confusiones=(
                D("La proporción de personas tituladas que se encuentra ocupada al momento de medir",
                  "La ocupación bruta ignora si el empleo se relaciona con lo estudiado."),
                D("El nivel de renta promedio alcanzado por las personas tituladas de la carrera",
                  "La renta es un dato asociado, no la definición de empleabilidad."),
                D("La demanda declarada por los empleadores del sector para el área de la carrera",
                  "Esa demanda es del mercado; la empleabilidad mide lo que ocurrió con los egresados."),
            ),
            explicacion_definicion=(
                "Interesa la inserción y su pertinencia respecto de la formación, siempre leída "
                "contra el contexto del sector."
            ),
            escenario=(
                "La empleabilidad de una carrera cayó en un año en que todo el sector se contrajo. "
                "¿Cómo se interpreta?"
            ),
            accion_correcta=(
                "Contrastando la caída con la del sector, para distinguir el efecto del contexto "
                "del desempeño propio"
            ),
            acciones_incorrectas=(
                D("Como una debilidad formativa que exige revisar el perfil de egreso de la carrera",
                  "Atribuirlo a la formación sin contrastar el contexto lleva a intervenir lo que no falla."),
                D("Como un efecto del contexto que no requiere análisis adicional de la carrera",
                  "Descartarlo sin contrastar puede esconder un problema propio bajo la crisis del sector."),
                D("Como un dato no comparable, dado que las condiciones del período fueron excepcionales",
                  "Declarar el dato incomparable renuncia a la lectura justo cuando más se necesita."),
            ),
            explicacion_escenario=(
                "El indicador solo se vuelve interpretable contra su referente sectorial; sin él "
                "se atribuye mal la causa."
            ),
        ),
        Concepto(
            codigo="DOCENCIA-10", nombre="La consistencia formativa", nivel_minimo=3,
            microlearning=(
                "Consistencia formativa es que perfil de egreso, plan de estudios, metodologías y "
                "evaluación digan lo mismo. Es la revisión más reveladora de esta dimensión "
                "porque suele mostrar desalineaciones que nadie ve desde una sola asignatura: "
                "capacidades prometidas que ninguna evaluación toca, o evaluaciones exigentes en "
                "algo que el perfil no menciona."
            ),
            definicion=(
                "La correspondencia verificable entre perfil de egreso, plan de estudios, "
                "metodologías y evaluación"
            ),
            confusiones=(
                D("La actualización simultánea de todos los programas de asignatura del plan",
                  "Actualizar todo a la vez no garantiza que digan lo mismo entre sí."),
                D("La aplicación de una metodología de enseñanza común en toda la carrera",
                  "Unificar metodología no asegura consistencia con el perfil ni con la evaluación."),
                D("El cumplimiento de la carga académica comprometida en el plan de estudios",
                  "La carga es un requisito formal, no una relación de coherencia."),
            ),
            explicacion_definicion=(
                "Es una relación entre los cuatro elementos, y se verifica rastreando cada "
                "capacidad del perfil hasta su evaluación."
            ),
            escenario=(
                "Al mapear el plan aparecen dos capacidades del perfil sin evaluación asociada y "
                "una asignatura que evalúa algo ausente del perfil. ¿Qué corresponde?"
            ),
            accion_correcta=(
                "Tratar ambos hallazgos como brechas de consistencia y resolver cada uno en el "
                "plan de mejora"
            ),
            acciones_incorrectas=(
                D("Corregir solo las capacidades sin evaluación, que son la brecha más relevante",
                  "La asignatura que evalúa fuera del perfil también indica desalineación."),
                D("Incorporar al perfil de egreso aquello que la asignatura ya está evaluando",
                  "Ampliar el perfil para calzar con lo existente invierte el orden de la revisión."),
                D("Registrar los hallazgos y abordarlos en el próximo proceso de rediseño curricular",
                  "Postergar deja titulándose a cohortes con la promesa formativa incompleta."),
            ),
            explicacion_escenario=(
                "Las dos desalineaciones son hallazgos válidos y ninguna se resuelve moviendo el "
                "perfil para que calce."
            ),
        ),
    ),
)
