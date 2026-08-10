"""
Aseguramiento Interno de la Calidad — base de conocimiento.

CONTENIDO DE PRUEBA. Sirve para validar la máquina de gamificación, no es material
oficial de acreditación. La estructura (la dimensión, su lugar en la ruta) sale de
la ruta institucional de AIEP; el desarrollo didáctico lo reemplaza el experto CNA
de AIEP en producción, sin tocar el modelo.
"""
from ..tipos import Concepto, Dimension, Distractor as D

CALIDAD = Dimension(
    codigo="CALIDAD",
    nombre_oficial="Aseguramiento Interno de la Calidad",
    encuadre=(
        "Esta dimensión mira hacia adentro: cómo la institución se observa a sí misma, "
        "detecta brechas y las cierra sin esperar a que se lo pidan."
    ),
    conceptos=(
        Concepto(
            codigo="CALIDAD-01", nombre="La autoevaluación", nivel_minimo=1,
            microlearning=(
                "Autoevaluar no es rendir una prueba: es mirarse con método y decir en voz alta "
                "qué se hace bien y qué no. Lo que la vuelve creíble es que sea sistemática "
                "—no una impresión— y que se apoye en información verificable. Un informe que "
                "solo enumera fortalezas no convence a nadie: la señal de madurez es nombrar las "
                "debilidades y mostrar qué se está haciendo con ellas."
            ),
            definicion=(
                "El examen crítico y sistemático que hace la propia institución sobre cuánto "
                "cumple los criterios, apoyado en información verificable"
            ),
            confusiones=(
                D("Una auditoría externa que revisa el cumplimiento normativo de la institución",
                  "La autoevaluación la hace la propia institución; la mirada externa viene después."),
                D("Un informe de logros que reúne los mejores resultados del período",
                  "Si solo recoge logros deja de ser crítica y pierde toda credibilidad."),
                D("Una encuesta de satisfacción aplicada a estudiantes y docentes",
                  "La encuesta es un insumo del proceso, no el proceso completo."),
            ),
            explicacion_definicion=(
                "Las tres palabras que la definen son crítica, sistemática y verificable: "
                "sin cualquiera de las tres el ejercicio no sirve como respaldo."
            ),
            escenario=(
                "Tu unidad debe entregar su parte del informe de autoevaluación. El equipo "
                "propone incluir solo los indicadores que salieron bien, para no exponer a nadie. "
                "¿Cuál es el aporte más consistente con el proceso?"
            ),
            accion_correcta=(
                "Incluir también los indicadores bajo meta, con el análisis de por qué ocurrió y "
                "qué se está haciendo"
            ),
            acciones_incorrectas=(
                D("Incluir solo los indicadores favorables y dejar el resto para el año siguiente",
                  "Un informe que oculta brechas se cae en cuanto los pares revisan los datos de origen."),
                D("Entregar todos los datos sin análisis, para que los revise el comité central",
                  "El dato sin juicio evaluativo traslada el trabajo y no aporta lectura de la unidad."),
                D("Reemplazar los indicadores bajos por testimonios positivos de estudiantes",
                  "El testimonio no sustituye al indicador: son evidencias de distinto tipo."),
            ),
            explicacion_escenario=(
                "Mostrar una brecha con su plan de acción es más fuerte que esconderla: "
                "es justo lo que distingue a una institución que se autorregula."
            ),
        ),
        Concepto(
            codigo="CALIDAD-02", nombre="La evidencia", nivel_minimo=1,
            microlearning=(
                "Una evidencia es lo que queda cuando alguien pregunta «¿y cómo sabes que eso "
                "pasó?». Tiene que poder mostrarse, tener fecha y responsable, y estar donde "
                "alguien más pueda encontrarla. La prueba de fuego es simple: si mañana llega una "
                "persona externa y pide el respaldo de lo que declaraste, ¿existe el documento y "
                "se puede ubicar sin depender de la memoria de nadie?"
            ),
            definicion=(
                "Un respaldo verificable de lo que la institución declara, con origen, fecha y "
                "responsable identificables"
            ),
            confusiones=(
                D("La opinión fundada de una autoridad sobre el funcionamiento de su área",
                  "La opinión, por informada que sea, no es verificable por un tercero."),
                D("Cualquier documento institucional que se haya publicado en el período",
                  "No basta con que exista un documento: tiene que respaldar lo que se declara."),
                D("Una meta comprometida en el plan de desarrollo para el próximo período",
                  "La meta habla del futuro; la evidencia respalda lo que ya ocurrió."),
            ),
            explicacion_definicion=(
                "Lo decisivo es que sea verificable: alguien externo debe poder llegar a la "
                "misma conclusión mirando el mismo respaldo."
            ),
            escenario=(
                "Declaras que la unidad realiza seguimiento mensual de sus indicadores, pero el "
                "seguimiento se hace conversando en reuniones que no se registran. ¿Qué haces?"
            ),
            accion_correcta=(
                "Instalar un acta breve por reunión con acuerdos y responsables, y recién "
                "entonces declarar el seguimiento"
            ),
            acciones_incorrectas=(
                D("Declarar el seguimiento igual, porque efectivamente ocurre todos los meses",
                  "Si ocurre pero no queda registro, ante la evaluación externa es como si no ocurriera."),
                D("Reconstruir las actas de los últimos doce meses desde los correos del equipo",
                  "Reconstruir a posteriori debilita la trazabilidad y se nota en las fechas."),
                D("Reemplazar la declaración por una más general que no exija respaldo",
                  "Bajar la declaración para no tener que respaldarla renuncia a una fortaleza real."),
            ),
            explicacion_escenario=(
                "La práctica ya existía; lo que faltaba era dejar rastro. Instalar el registro "
                "convierte una costumbre en evidencia."
            ),
        ),
        Concepto(
            codigo="CALIDAD-03", nombre="Un mecanismo de aseguramiento de la calidad", nivel_minimo=1,
            microlearning=(
                "Un mecanismo es un procedimiento que se repite solo, con responsable y "
                "periodicidad definidos, y que produce información para decidir. La diferencia "
                "con una buena intención es que el mecanismo funciona aunque cambien las personas. "
                "En los talleres de sede y escuela se analizan justamente estos mecanismos: no si "
                "existen en el papel, sino si operan y si alguien usa lo que producen."
            ),
            definicion=(
                "Un procedimiento formalizado, con responsable y periodicidad, que se aplica de "
                "manera regular y produce información para decidir"
            ),
            confusiones=(
                D("Una instancia de coordinación que se convoca cuando surge un problema",
                  "Si se convoca por excepción no es un mecanismo: es una reacción."),
                D("El conjunto de normativas internas que regulan el quehacer institucional",
                  "La normativa habilita el mecanismo, pero no lo reemplaza."),
                D("Un sistema informático que almacena los indicadores de la institución",
                  "El sistema es soporte; el mecanismo es el procedimiento que lo usa."),
            ),
            explicacion_definicion=(
                "Responsable, periodicidad y uso de los resultados: si falta alguno, el mecanismo "
                "existe en el papel y no en la práctica."
            ),
            escenario=(
                "La escuela evalúa la satisfacción de sus estudiantes cada semestre, pero los "
                "resultados se archivan y nadie los revisa. ¿Qué corresponde hacer?"
            ),
            accion_correcta=(
                "Definir quién analiza los resultados, en qué instancia se ven y qué decisiones "
                "deben salir de ahí"
            ),
            acciones_incorrectas=(
                D("Aumentar la frecuencia de la encuesta para tener información más actualizada",
                  "Más medición sin uso solo agranda el archivo que nadie lee."),
                D("Suspender la encuesta hasta que exista un sistema que procese los resultados",
                  "Suspender la medición elimina el insumo y agrava el problema."),
                D("Publicar los resultados en el sitio institucional para darles visibilidad",
                  "Publicar no es lo mismo que usar: sin decisión asociada el ciclo sigue abierto."),
            ),
            explicacion_escenario=(
                "El mecanismo se completa cuando la información llega a alguien que decide. "
                "Medir y archivar es medio mecanismo."
            ),
        ),
        Concepto(
            codigo="CALIDAD-04", nombre="La mejora continua", nivel_minimo=1,
            microlearning=(
                "La mejora continua es un ciclo, no un evento: se detecta una brecha, se actúa "
                "sobre ella y se deja registro del seguimiento. Lo que la CNA busca ver no es una "
                "institución sin problemas —esa no existe— sino una que detecta los suyos y los "
                "cierra. Un plan de mejora sin fechas ni responsables es una declaración de "
                "intenciones, y se lee como tal."
            ),
            definicion=(
                "El ciclo de detectar una brecha, actuar sobre ella y evidenciar el seguimiento, "
                "sostenido en el tiempo"
            ),
            confusiones=(
                D("El conjunto de proyectos de innovación que la institución impulsa cada año",
                  "La innovación puede ser parte, pero la mejora continua parte de una brecha detectada."),
                D("La corrección de los hallazgos que levanta la evaluación externa",
                  "Si solo se activa con la visita externa, no es continua ni es interna."),
                D("El aumento sostenido de los indicadores institucionales período a período",
                  "El indicador al alza es un resultado posible, no el ciclo en sí."),
            ),
            explicacion_definicion=(
                "Detectar, actuar y evidenciar: los tres pasos, y el tercero es el que suele "
                "faltar y el que hace verificable a los otros dos."
            ),
            escenario=(
                "Un indicador de tu unidad lleva dos períodos bajo la meta. ¿Cuál es la respuesta "
                "más consistente con la mejora continua?"
            ),
            accion_correcta=(
                "Documentar la brecha, comprometer una acción con responsable y plazo, y "
                "registrar su seguimiento"
            ),
            acciones_incorrectas=(
                D("Ajustar la meta del indicador a un valor alcanzable con el desempeño actual",
                  "Mover la meta hace desaparecer la brecha del informe, no de la realidad."),
                D("Esperar a que el nivel central defina un plan común para todas las unidades",
                  "Esperar instrucciones cuando la brecha es propia deja pasar el período."),
                D("Reportar el indicador solo si la comisión evaluadora lo solicita expresamente",
                  "Reportar por requerimiento es lo contrario de la autorregulación."),
            ),
            explicacion_escenario=(
                "El compromiso con responsable y plazo es lo que convierte una intención en una "
                "acción que después se puede verificar."
            ),
        ),
        Concepto(
            codigo="CALIDAD-05", nombre="Un criterio y un estándar", nivel_minimo=1,
            microlearning=(
                "El criterio dice qué se espera; el estándar, cuánto. Los criterios derivan de las "
                "dimensiones y expresan principios generales de calidad. Los estándares bajan eso "
                "a niveles de desempeño ordenados de menor a mayor, donde cada nivel incluye al "
                "anterior. Esa progresión es la que permite mostrar avance: no se trata de cumplir "
                "o no cumplir, sino de en qué punto del camino está la institución."
            ),
            definicion=(
                "El criterio expresa qué se espera de la institución; el estándar fija en qué "
                "nivel de desempeño progresivo se encuentra"
            ),
            confusiones=(
                D("El criterio lo define la institución y el estándar lo fija el organismo externo",
                  "Ambos vienen del modelo de evaluación; la institución no define sus criterios."),
                D("El criterio es cualitativo y el estándar es siempre una meta numérica",
                  "El estándar describe niveles de desarrollo, no necesariamente cifras."),
                D("El criterio se aplica a la institución y el estándar solo a las carreras",
                  "Ambos operan en el nivel institucional de este proceso."),
            ),
            explicacion_definicion=(
                "Criterio es el qué y estándar es el cuánto, y los niveles del estándar son "
                "acumulativos: el superior contiene al anterior."
            ),
            escenario=(
                "En un taller alguien afirma que la institución «cumple o no cumple» cada "
                "criterio. ¿Cómo lo corriges?"
            ),
            accion_correcta=(
                "Explicar que los estándares describen niveles progresivos y que corresponde "
                "ubicar en cuál está la institución"
            ),
            acciones_incorrectas=(
                D("Confirmar la lectura, porque simplifica el trabajo del comité de autoevaluación",
                  "Simplificar así borra la progresión, que es justamente donde se muestra el avance."),
                D("Proponer una escala propia de cumplimiento acordada entre las unidades",
                  "Inventar una escala paralela desconecta el informe del modelo de evaluación."),
                D("Dejar la definición para el cierre, cuando estén todos los datos reunidos",
                  "Sin acordar el marco al inicio, cada unidad evalúa con una vara distinta."),
            ),
            explicacion_escenario=(
                "Ubicarse en un nivel permite mostrar trayectoria; el «cumple o no cumple» deja "
                "el avance invisible."
            ),
        ),
        Concepto(
            codigo="CALIDAD-06", nombre="El plan de mejora", nivel_minimo=1,
            microlearning=(
                "El plan de mejora es la respuesta institucional a lo que la autoevaluación "
                "encontró. Toma las debilidades priorizadas y las convierte en acciones con "
                "responsable, plazo y recurso asignado. Se entrega junto al informe porque, sin "
                "él, el diagnóstico queda sin consecuencia. Un plan realista y acotado dice más "
                "de la madurez institucional que uno extenso y genérico."
            ),
            definicion=(
                "El instrumento que convierte las debilidades priorizadas en acciones con "
                "responsable, plazo y recursos asignados"
            ),
            confusiones=(
                D("El listado de proyectos estratégicos comprometidos para el próximo período",
                  "El plan de mejora nace del diagnóstico, no de la cartera de proyectos."),
                D("El informe que describe las debilidades detectadas por cada unidad",
                  "Describir la debilidad es el diagnóstico; el plan es lo que se hará con ella."),
                D("El compromiso presupuestario que respalda las acciones del período siguiente",
                  "El presupuesto habilita el plan, pero no lo constituye."),
            ),
            explicacion_definicion=(
                "Responsable, plazo y recurso: sin los tres, la acción no es exigible y el plan "
                "no se puede seguir."
            ),
            escenario=(
                "El borrador del plan de mejora de tu unidad dice «fortalecer el seguimiento "
                "académico». ¿Qué le falta?"
            ),
            accion_correcta=(
                "Precisar qué acción concreta se hará, quién responde, en qué plazo y con qué "
                "recursos"
            ),
            acciones_incorrectas=(
                D("Agregar indicadores de resultado para poder medir el fortalecimiento después",
                  "El indicador ayuda, pero sin acción, responsable y plazo no hay qué medir."),
                D("Ampliar la redacción para que cubra también otras debilidades detectadas",
                  "Ampliar el alcance de una acción difusa la vuelve todavía menos exigible."),
                D("Trasladar la acción al nivel central, que tiene más capacidad de ejecución",
                  "Trasladar sin acuerdo deja la debilidad sin responsable real."),
            ),
            explicacion_escenario=(
                "«Fortalecer» no es una acción: es una aspiración. El plan se vuelve verificable "
                "cuando dice quién hace qué y para cuándo."
            ),
        ),
        Concepto(
            codigo="CALIDAD-07", nombre="Un juicio evaluativo", nivel_minimo=2,
            microlearning=(
                "El juicio evaluativo es el paso que va del dato a la afirmación: no dice «la "
                "retención fue de 78%», dice «la retención es una fortaleza porque se sostiene "
                "sobre un mecanismo que opera y muestra tendencia al alza». Requiere tomar "
                "posición y fundamentarla. Los comités por dimensión lo elaboran, y el comité "
                "central los integra en una lectura institucional coherente."
            ),
            definicion=(
                "La afirmación fundada que interpreta la evidencia y toma posición sobre si algo "
                "es fortaleza, debilidad u oportunidad de mejora"
            ),
            confusiones=(
                D("La descripción ordenada de los indicadores relevantes de cada dimensión",
                  "Describir el dato no es juzgarlo: falta la interpretación y la posición."),
                D("La valoración que emiten los pares evaluadores durante la visita externa",
                  "Ese juicio es externo; este lo elabora la propia institución."),
                D("El acuerdo del comité sobre qué evidencias se adjuntarán al informe",
                  "Seleccionar evidencia es un paso previo al juicio, no el juicio."),
            ),
            explicacion_definicion=(
                "El juicio es donde la institución se moja: interpreta su evidencia y afirma algo "
                "que después tendrá que sostener."
            ),
            escenario=(
                "El comité de tu dimensión escribió: «La titulación oportuna alcanzó 62%». El "
                "coordinador pide convertirlo en juicio evaluativo. ¿Qué agregas?"
            ),
            accion_correcta=(
                "Una interpretación fundada de qué significa ese 62% y si constituye fortaleza o "
                "debilidad, con su respaldo"
            ),
            acciones_incorrectas=(
                D("La comparación del indicador con el de instituciones del mismo segmento",
                  "El referente externo enriquece, pero por sí solo sigue sin tomar posición."),
                D("La serie histórica del indicador durante los últimos cinco períodos",
                  "La serie es más dato: aporta contexto pero no constituye el juicio."),
                D("Las acciones que la unidad implementará para mejorar ese resultado",
                  "Las acciones van al plan de mejora, después de haber emitido el juicio."),
            ),
            explicacion_escenario=(
                "El juicio exige decir qué significa el número para esta institución y por qué, "
                "no solo mostrarlo mejor acompañado."
            ),
        ),
        Concepto(
            codigo="CALIDAD-08", nombre="La trazabilidad de la evidencia", nivel_minimo=2,
            microlearning=(
                "Trazabilidad es poder ir desde una afirmación del informe hasta el respaldo que "
                "la sostiene, sin intermediarios. Cada declaración debería tener una ruta clara: "
                "qué documento, dónde está, quién lo generó y cuándo. Cuando la visita externa "
                "pide profundizar en un punto, la trazabilidad es lo que separa una respuesta en "
                "minutos de una búsqueda de días."
            ),
            definicion=(
                "La posibilidad de recorrer, desde cada afirmación del informe, la ruta hasta el "
                "respaldo que la sostiene"
            ),
            confusiones=(
                D("El almacenamiento centralizado de todos los documentos del proceso",
                  "Centralizar ayuda, pero sin el vínculo afirmación–respaldo no hay trazabilidad."),
                D("El registro de las versiones sucesivas del informe de autoevaluación",
                  "El control de versiones es del documento, no del vínculo con la evidencia."),
                D("La autorización formal para acceder a la información institucional sensible",
                  "El permiso de acceso es otro asunto: no crea la ruta hacia el respaldo."),
            ),
            explicacion_definicion=(
                "Lo esencial es el vínculo: cada afirmación debe llevar a su respaldo sin "
                "depender de que alguien recuerde dónde quedó."
            ),
            escenario=(
                "Durante la revisión, un párrafo afirma que existe seguimiento de egresados, pero "
                "nadie identifica de dónde salió esa afirmación. ¿Qué haces?"
            ),
            accion_correcta=(
                "Ubicar el respaldo concreto y dejar registrada la referencia junto a la "
                "afirmación, o retirarla si no existe"
            ),
            acciones_incorrectas=(
                D("Mantener la afirmación y buscar el respaldo si la visita externa lo solicita",
                  "Dejarlo para la visita es exactamente cuando ya no hay tiempo de encontrarlo."),
                D("Suavizar la redacción para que la afirmación resulte menos exigente de probar",
                  "Suavizar sin verificar deja una declaración igualmente sin respaldo."),
                D("Solicitar al área de egresados que elabore un informe para respaldar el punto",
                  "Producir el respaldo después, para calzar con lo declarado, invierte el orden."),
            ),
            explicacion_escenario=(
                "O la afirmación tiene respaldo y se referencia, o no lo tiene y sale. No hay "
                "una tercera opción defendible."
            ),
        ),
        Concepto(
            codigo="CALIDAD-09", nombre="El comité de autoevaluación", nivel_minimo=3,
            microlearning=(
                "El proceso se organiza en una cadena de instancias: los comités de sede y escuela "
                "levantan la información en terreno, los comités por dimensión elaboran los juicios "
                "de su ámbito, el comité central los integra y propone el plan de mejora, y las "
                "instancias superiores validan y aprueban. Cada eslabón tiene un producto propio; "
                "cuando uno entrega algo que le tocaba a otro, la cadena se desordena."
            ),
            definicion=(
                "La instancia con composición y producto definidos que realiza una etapa del "
                "proceso y entrega su resultado a la instancia siguiente"
            ),
            confusiones=(
                D("El equipo técnico que redacta el informe final de autoevaluación institucional",
                  "La redacción es una tarea; el comité se define por su producto evaluativo."),
                D("La comisión que representa a la institución ante el organismo acreditador",
                  "La representación externa es otra función, posterior y distinta."),
                D("El grupo de directivos que aprueba las decisiones estratégicas del proceso",
                  "La aprobación corresponde a la instancia superior, no a todo comité."),
            ),
            explicacion_definicion=(
                "Lo que distingue a cada comité es su producto: quién elabora juicios, quién los "
                "integra y quién valida."
            ),
            escenario=(
                "El comité de tu sede quiere emitir directamente el juicio evaluativo institucional "
                "de la dimensión, para ahorrar tiempo. ¿Qué corresponde?"
            ),
            accion_correcta=(
                "Entregar el análisis de la sede al comité de la dimensión, que es quien elabora "
                "ese juicio"
            ),
            acciones_incorrectas=(
                D("Emitir el juicio y enviarlo al comité central para que lo ratifique después",
                  "Saltarse la instancia deja al comité de dimensión sin la base que debía integrar."),
                D("Redactar el juicio en conjunto con las otras sedes y presentarlo como acuerdo",
                  "Un acuerdo entre sedes no reemplaza la mirada institucional por dimensión."),
                D("Postergar el análisis de la sede hasta que el comité central dé lineamientos",
                  "Esperar lineamientos deja sin insumo a toda la cadena que viene después."),
            ),
            explicacion_escenario=(
                "Cada instancia aporta lo suyo. Saltarse un eslabón para ganar tiempo termina "
                "costando la coherencia del informe."
            ),
        ),
        Concepto(
            codigo="CALIDAD-10", nombre="La cultura de calidad", nivel_minimo=3,
            microlearning=(
                "La cultura de calidad es lo que queda cuando termina el proceso de acreditación. "
                "Se reconoce en señales concretas: la gente registra lo que hace sin que se lo "
                "pidan, las decisiones citan datos, y hablar de una debilidad no se vive como una "
                "acusación. Es lo más difícil de instalar y lo único que hace sostenible todo lo "
                "demás, porque un proceso que depende de un empujón cada cinco años no se sostiene."
            ),
            definicion=(
                "La práctica instalada de registrar, revisar y mejorar de forma habitual, "
                "independiente de si hay un proceso de acreditación en curso"
            ),
            confusiones=(
                D("El conjunto de valores institucionales declarados en la misión y la visión",
                  "Los valores declarados son el punto de partida, no la práctica instalada."),
                D("El nivel de participación alcanzado en las actividades de autoevaluación",
                  "La participación en un proceso puntual no acredita una práctica permanente."),
                D("La capacitación sistemática de los colaboradores en materias de calidad",
                  "La capacitación habilita la cultura, pero no equivale a que esté instalada."),
            ),
            explicacion_definicion=(
                "La prueba está en la independencia del proceso: si las prácticas solo aparecen "
                "cuando se acerca la visita, todavía no hay cultura."
            ),
            escenario=(
                "Terminada la visita externa, varios equipos dejan de registrar sus reuniones de "
                "seguimiento. ¿Qué señala esto y qué corresponde hacer?"
            ),
            accion_correcta=(
                "Que la práctica dependía del proceso y no de la cultura: hay que integrarla a la "
                "gestión habitual con soporte y sentido"
            ),
            acciones_incorrectas=(
                D("Que el proceso terminó y el nivel de registro puede volver a su estado normal",
                  "Aceptarlo como normal renuncia justamente a lo que el proceso vino a instalar."),
                D("Que hace falta una instrucción formal que obligue a mantener los registros",
                  "La obligación sin sentido compartido produce registros vacíos que nadie usa."),
                D("Que conviene esperar al siguiente ciclo para retomar la práctica con fuerza",
                  "Reactivar por ciclos es precisamente el patrón que impide instalar la cultura."),
            ),
            explicacion_escenario=(
                "Que la práctica se caiga al terminar la visita es el diagnóstico. La respuesta "
                "es darle utilidad propia, no vigilarla más."
            ),
        ),
    ),
)
