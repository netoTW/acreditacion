"""
Vinculación con el Medio — base de conocimiento.

CONTENIDO DE PRUEBA. Valida la máquina, no es material oficial de acreditación.
"""
from ..tipos import Concepto, Dimension, Distractor as D

VCM = Dimension(
    codigo="VCM",
    nombre_oficial="Vinculación con el Medio",
    encuadre=(
        "Esta dimensión pregunta qué relación real tiene la institución con su entorno y "
        "si esa relación deja algo en ambas partes."
    ),
    conceptos=(
        Concepto(
            codigo="VCM-01", nombre="La vinculación con el medio", nivel_minimo=1,
            microlearning=(
                "Vincularse con el medio es sostener una relación sistemática con el entorno que "
                "aporta valor a ambas partes y que alimenta de vuelta a la docencia. Lo que la "
                "distingue de la difusión institucional es esa vuelta: si la actividad no cambia "
                "nada adentro, fue comunicación, no vinculación."
            ),
            definicion=(
                "La relación sistemática con el entorno que aporta valor a ambas partes y "
                "retroalimenta el quehacer institucional"
            ),
            confusiones=(
                D("La difusión de la oferta académica y los logros institucionales en el entorno",
                  "Difundir es comunicar hacia afuera; no hay aporte de vuelta."),
                D("El conjunto de convenios firmados con organizaciones externas del sector",
                  "El convenio habilita la relación, pero por sí solo no es vinculación."),
                D("Las actividades de extensión cultural abiertas a la comunidad local",
                  "La extensión puede ser parte, pero no toda vinculación es extensión."),
            ),
            explicacion_definicion=(
                "Lo definitorio es la bidireccionalidad y que el resultado vuelva a la "
                "institución: sin eso es difusión."
            ),
            escenario=(
                "Una escuela realiza charlas anuales en colegios de la zona y las reporta como "
                "vinculación. ¿Qué falta para que lo sea?"
            ),
            accion_correcta=(
                "Definir qué aporta la actividad a cada parte y cómo su resultado vuelve a la "
                "docencia de la escuela"
            ),
            acciones_incorrectas=(
                D("Aumentar la cantidad de charlas y la cobertura de colegios visitados por año",
                  "Más volumen de una actividad unidireccional no la convierte en vinculación."),
                D("Registrar la asistencia a cada charla para documentar el alcance logrado",
                  "El alcance documenta cobertura, no aporte mutuo ni retroalimentación."),
                D("Formalizar un convenio con cada colegio donde se realizan las charlas",
                  "El convenio da marco, pero no responde qué recibe cada parte."),
            ),
            explicacion_escenario=(
                "La pregunta que ordena todo es qué gana cada parte y qué cambia adentro después "
                "de la actividad."
            ),
        ),
        Concepto(
            codigo="VCM-02", nombre="La bidireccionalidad", nivel_minimo=1,
            microlearning=(
                "Bidireccional significa que ambas partes aportan y ambas reciben. En la práctica "
                "se comprueba con una pregunta incómoda: ¿qué cambió en la institución a partir de "
                "esta relación? Si la respuesta es «nada, pero el socio quedó contento», la "
                "relación existe pero le falta la mitad."
            ),
            definicion=(
                "La condición de que ambas partes aporten y reciban, de modo que la relación "
                "modifique también a la institución"
            ),
            confusiones=(
                D("La participación de representantes externos en instancias consultivas internas",
                  "Participar es un medio posible; la bidireccionalidad se prueba en el efecto."),
                D("El intercambio de recursos o servicios entre la institución y sus socios",
                  "El intercambio puede ser puramente transaccional y no dejar aprendizaje."),
                D("La firma de acuerdos que establecen obligaciones para ambas partes",
                  "El acuerdo formaliza obligaciones, no garantiza aporte mutuo real."),
            ),
            explicacion_definicion=(
                "La prueba está en el efecto sobre la institución: si nada cambió adentro, la "
                "relación fue en una sola dirección."
            ),
            escenario=(
                "Un convenio de práctica lleva cuatro años funcionando. Los estudiantes se "
                "insertan bien y la empresa está conforme. ¿Qué falta revisar?"
            ),
            accion_correcta=(
                "Si lo que la empresa observa de los estudiantes ha llegado a modificar el plan "
                "de estudios o su evaluación"
            ),
            acciones_incorrectas=(
                D("Si la cantidad de cupos de práctica ofrecidos ha crecido durante el período",
                  "Más cupos es más volumen, no más retroalimentación."),
                D("Si la satisfacción de los estudiantes con la práctica se mantiene alta",
                  "La satisfacción del estudiante no informa si la institución aprendió algo."),
                D("Si el convenio se ha renovado formalmente en cada uno de los períodos",
                  "La renovación acredita continuidad, no bidireccionalidad."),
            ),
            explicacion_escenario=(
                "El socio observa a los estudiantes en terreno; si eso no vuelve al currículo, se "
                "está perdiendo la mitad del valor."
            ),
        ),
        Concepto(
            codigo="VCM-03", nombre="El medio relevante", nivel_minimo=1,
            microlearning=(
                "El medio relevante es el entorno específico con el que la institución debe "
                "vincularse según su misión y su oferta: sectores productivos, territorios, "
                "comunidades. Definirlo importa porque sin él la vinculación se dispersa y "
                "cualquier actividad parece pertinente. Una institución técnico-profesional en una "
                "región minera tiene un medio relevante bastante evidente."
            ),
            definicion=(
                "El entorno específico —sectores, territorios y actores— con el que la institución "
                "debe vincularse según su misión y su oferta"
            ),
            confusiones=(
                D("El conjunto de organizaciones con las que la institución mantiene convenios",
                  "Los convenios actuales pueden no coincidir con el medio que corresponde."),
                D("La comunidad geográfica donde se ubican las sedes de la institución",
                  "El territorio es parte, pero el medio relevante también es sectorial."),
                D("El público objetivo al que la institución dirige su oferta académica",
                  "Ese es el destinatario de la formación, no el medio con que se vincula."),
            ),
            explicacion_definicion=(
                "Se define desde la misión y la oferta, no desde los convenios que ya existen."
            ),
            escenario=(
                "Una sede reporta veinte actividades de vinculación, ninguna relacionada con los "
                "sectores de sus carreras. ¿Qué se concluye?"
            ),
            accion_correcta=(
                "Que la vinculación está dispersa respecto del medio relevante y hay que "
                "reorientarla hacia los sectores de la oferta"
            ),
            acciones_incorrectas=(
                D("Que la sede muestra un buen nivel de actividad y amplia presencia territorial",
                  "El volumen sin pertinencia no acredita vinculación con el medio relevante."),
                D("Que corresponde ampliar la definición del medio relevante de la sede",
                  "Ampliar la definición para que calce con lo hecho vacía el concepto."),
                D("Que las actividades deben reportarse como extensión y no como vinculación",
                  "Reclasificar resuelve la etiqueta y deja intacto el problema de fondo."),
            ),
            explicacion_escenario=(
                "Actividad hay; lo que falta es pertinencia respecto de lo que la institución "
                "forma."
            ),
        ),
        Concepto(
            codigo="VCM-04", nombre="El impacto de la vinculación", nivel_minimo=1,
            microlearning=(
                "Impacto es el efecto que queda después, en el entorno y en la institución. Es lo "
                "más difícil de mostrar y lo que más se confunde con cobertura. Cuántas personas "
                "asistieron es alcance; qué cambió para ellas es impacto. Declarar impacto sin "
                "medición es una de las debilidades más frecuentes en esta dimensión."
            ),
            definicion=(
                "El efecto verificable que la vinculación deja en el entorno y en la institución "
                "una vez terminada la actividad"
            ),
            confusiones=(
                D("El número de personas alcanzadas por las actividades de vinculación del período",
                  "Eso es alcance: dice a cuántos se llegó, no qué cambió."),
                D("La cantidad de actividades de vinculación ejecutadas por cada unidad académica",
                  "El volumen de actividad no informa ningún efecto."),
                D("La valoración positiva que expresan los participantes al finalizar la actividad",
                  "La satisfacción inmediata no acredita un efecto que perdure."),
            ),
            explicacion_definicion=(
                "Impacto es lo que queda después; alcance es a cuántos se llegó. Confundirlos es "
                "el error más común aquí."
            ),
            escenario=(
                "El informe declara «alto impacto» de un programa de capacitación a pymes, "
                "respaldado con la lista de asistentes. ¿Qué corresponde?"
            ),
            accion_correcta=(
                "Reemplazar la declaración por alcance, o medir qué cambió en las pymes para "
                "poder hablar de impacto"
            ),
            acciones_incorrectas=(
                D("Complementar la lista con la encuesta de satisfacción aplicada al cierre",
                  "La satisfacción sigue sin decir qué cambió en la gestión de esas pymes."),
                D("Mantener la declaración y adjuntar fotografías y registros de las sesiones",
                  "El registro documenta que ocurrió, no que haya dejado un efecto."),
                D("Precisar el número de pymes alcanzadas y su distribución por rubro",
                  "Más detalle del alcance sigue siendo alcance."),
            ),
            explicacion_escenario=(
                "O se mide el efecto, o se declara alcance. Llamar impacto a una lista de "
                "asistencia no resiste una pregunta."
            ),
        ),
        Concepto(
            codigo="VCM-05", nombre="Los empleadores como informantes clave", nivel_minimo=1,
            microlearning=(
                "Los empleadores son una de las fuentes que la institución consulta durante la "
                "autoevaluación, junto con estudiantes, docentes y titulados. Su valor es que "
                "observan a los egresados en desempeño real. Para que esa información sirva tiene "
                "que llegar a alguien que pueda modificar el currículo; si queda en un informe de "
                "encuesta, se pierde."
            ),
            definicion=(
                "La fuente externa que observa el desempeño real de las personas tituladas y cuya "
                "información debe retroalimentar la formación"
            ),
            confusiones=(
                D("Las organizaciones que ofrecen cupos de práctica a los estudiantes de la carrera",
                  "Ofrecer prácticas es una relación posible, distinta de informar el proceso."),
                D("Los socios estratégicos con los que la institución mantiene convenios vigentes",
                  "El socio estratégico puede o no ser empleador de los titulados."),
                D("Los representantes del sector que participan en los consejos asesores externos",
                  "Participar en un consejo es un mecanismo; no define quién es informante clave."),
            ),
            explicacion_definicion=(
                "Lo que los hace informantes clave es que observan el desempeño real de los "
                "egresados, y eso debe volver al currículo."
            ),
            escenario=(
                "La encuesta a empleadores señala una brecha en habilidades de comunicación "
                "escrita. El informe la reporta y ahí queda. ¿Qué falta?"
            ),
            accion_correcta=(
                "Llevar el hallazgo a la instancia curricular y decidir dónde se abordará esa "
                "brecha en el plan"
            ),
            acciones_incorrectas=(
                D("Repetir la encuesta el próximo período para confirmar si la brecha se mantiene",
                  "Confirmar dos veces la misma brecha sin actuar es postergar con método."),
                D("Incorporar el hallazgo al informe de autoevaluación como debilidad detectada",
                  "Declararla es necesario, pero sin decisión curricular el ciclo queda abierto."),
                D("Comunicar el resultado a los docentes para que lo consideren en sus asignaturas",
                  "Delegar a la buena voluntad individual no instala la respuesta en el plan."),
            ),
            explicacion_escenario=(
                "La consulta solo vale si el resultado llega a quien puede cambiar el plan de "
                "estudios."
            ),
        ),
        Concepto(
            codigo="VCM-06", nombre="Una actividad de vinculación", nivel_minimo=1,
            microlearning=(
                "Para que una actividad cuente como vinculación necesita propósito declarado, "
                "socio identificado, resultado esperado y registro. Sin esos cuatro elementos es "
                "difícil distinguirla de una actividad de difusión, y el informe termina con un "
                "listado largo que no acredita nada."
            ),
            definicion=(
                "La acción con propósito declarado, socio identificado, resultado esperado y "
                "registro, orientada al medio relevante"
            ),
            confusiones=(
                D("Cualquier acción institucional que involucre a personas externas a la institución",
                  "La sola presencia de externos no constituye vinculación."),
                D("Los eventos de difusión que la institución organiza para la comunidad",
                  "La difusión no tiene socio ni resultado esperado bidireccional."),
                D("Las actividades que se realizan fuera de las dependencias institucionales",
                  "El lugar no define la naturaleza de la actividad."),
            ),
            explicacion_definicion=(
                "Propósito, socio, resultado esperado y registro: los cuatro son lo que la hace "
                "reportable y evaluable."
            ),
            escenario=(
                "El registro de vinculación tiene 140 actividades, y al revisar una muestra la "
                "mitad no identifica socio ni resultado. ¿Qué corresponde?"
            ),
            accion_correcta=(
                "Depurar el registro según los criterios y quedarse con las actividades que sí "
                "califican"
            ),
            acciones_incorrectas=(
                D("Mantener el registro completo, porque refleja el volumen real de actividad",
                  "Un registro inflado se cae en la primera revisión de la visita externa."),
                D("Completar retroactivamente los campos faltantes con la información disponible",
                  "Completar a posteriori inventa un propósito que no existió al planificar."),
                D("Separar las actividades incompletas en un anexo del informe de autoevaluación",
                  "El anexo no resuelve que esas actividades no cumplen los criterios."),
            ),
            explicacion_escenario=(
                "Un registro depurado y creíble vale más que uno extenso que no resiste una "
                "revisión por muestreo."
            ),
        ),
        Concepto(
            codigo="VCM-07", nombre="La sistematización de la vinculación", nivel_minimo=2,
            microlearning=(
                "Sistematizar es tener una forma común de planificar, registrar y evaluar la "
                "vinculación en toda la institución. Sin eso cada unidad usa su propio criterio y "
                "los datos no se pueden sumar. La señal típica de falta de sistematización es que "
                "el total institucional no cuadra con la suma de las unidades."
            ),
            definicion=(
                "La existencia de criterios y registros comunes que permiten planificar, "
                "consolidar y evaluar la vinculación en toda la institución"
            ),
            confusiones=(
                D("La centralización de las actividades de vinculación en una unidad responsable",
                  "Centralizar la ejecución no equivale a tener criterios comunes."),
                D("La existencia de una política institucional de vinculación con el medio",
                  "La política orienta; la sistematización es el aparato que la operativiza."),
                D("El uso de una plataforma informática para registrar las actividades realizadas",
                  "La plataforma soporta el registro, pero no define los criterios."),
            ),
            explicacion_definicion=(
                "Criterios comunes y registro consolidable: sin eso los datos de las unidades no "
                "se pueden sumar."
            ),
            escenario=(
                "Cada sede reporta vinculación con su propia planilla y el consolidado "
                "institucional no cuadra. ¿Qué corresponde?"
            ),
            accion_correcta=(
                "Acordar criterios y un formato único de registro antes de volver a consolidar"
            ),
            acciones_incorrectas=(
                D("Consolidar con la mejor estimación disponible y anotar la limitación al pie",
                  "Consolidar datos incomparables produce una cifra que no significa nada."),
                D("Reportar cada sede por separado sin construir un total institucional",
                  "Renunciar al consolidado deja a la dimensión sin lectura institucional."),
                D("Solicitar a cada sede que corrija su planilla según su propio criterio",
                  "Corregir con criterios distintos reproduce exactamente el mismo problema."),
            ),
            explicacion_escenario=(
                "Mientras no haya criterio común, cualquier consolidado es una suma de cosas "
                "distintas."
            ),
        ),
        Concepto(
            codigo="VCM-08", nombre="La contribución al territorio", nivel_minimo=2,
            microlearning=(
                "La contribución al territorio es el aporte de la institución al desarrollo del "
                "lugar donde está: formación pertinente a las necesidades locales, capacidades "
                "puestas a disposición, problemas abordados con actores del territorio. Se "
                "diferencia de la presencia: tener una sede no es contribuir."
            ),
            definicion=(
                "El aporte verificable de la institución al desarrollo del territorio donde "
                "opera, más allá de su sola presencia"
            ),
            confusiones=(
                D("La cobertura territorial que alcanza la institución a través de sus sedes",
                  "La cobertura es presencia geográfica, no contribución."),
                D("El número de estudiantes de la región que la institución matricula cada año",
                  "Matricular localmente es cobertura de acceso, no aporte al desarrollo."),
                D("La generación de empleo directo asociada al funcionamiento de las sedes",
                  "El empleo propio es un efecto económico, no una contribución formativa."),
            ),
            explicacion_definicion=(
                "Lo que se evalúa es el aporte al desarrollo, y por eso tiene que ser "
                "verificable más allá de estar instalado ahí."
            ),
            escenario=(
                "Una sede argumenta su contribución territorial señalando que es la única "
                "institución de educación superior de la comuna. ¿Qué corresponde señalar?"
            ),
            accion_correcta=(
                "Que la presencia exclusiva no es contribución por sí sola y hay que mostrar qué "
                "aporta al desarrollo local"
            ),
            acciones_incorrectas=(
                D("Que la presencia exclusiva constituye por sí misma una contribución relevante",
                  "Estar es una condición, no un aporte demostrado."),
                D("Que corresponde complementar el argumento con datos de matrícula de la comuna",
                  "La matrícula local sigue describiendo acceso, no contribución."),
                D("Que el argumento es válido si se acompaña de la antigüedad de la sede",
                  "La antigüedad refuerza la presencia, no el aporte al desarrollo."),
            ),
            explicacion_escenario=(
                "Ser la única institución del lugar es una oportunidad enorme de contribuir; no "
                "es todavía la contribución."
            ),
        ),
        Concepto(
            codigo="VCM-09", nombre="La evaluación del impacto", nivel_minimo=3,
            microlearning=(
                "Evaluar impacto exige definir antes qué se espera cambiar, con qué se comparará y "
                "cuándo se medirá. Si eso no se define al diseñar la actividad, después no hay "
                "manera honesta de atribuir el cambio. Es la diferencia entre poder afirmar que la "
                "intervención sirvió y solo poder afirmar que ocurrió."
            ),
            definicion=(
                "La medición del efecto atribuible a la actividad, con línea de comparación y "
                "momento de medición definidos desde el diseño"
            ),
            confusiones=(
                D("La aplicación de instrumentos de satisfacción al término de cada actividad",
                  "La satisfacción se recoge al cierre y no permite atribuir ningún cambio."),
                D("El seguimiento del cumplimiento de las metas comprometidas en cada convenio",
                  "Cumplir metas de ejecución no dice si hubo efecto en el entorno."),
                D("La sistematización de los resultados obtenidos por cada unidad ejecutora",
                  "Sistematizar resultados es ordenar información, no evaluar impacto."),
            ),
            explicacion_definicion=(
                "Sin línea de comparación definida desde el diseño no hay atribución posible, "
                "solo coincidencia."
            ),
            escenario=(
                "Se quiere evaluar el impacto de un programa que lleva tres años sin línea base ni "
                "grupo de comparación. ¿Qué es lo honesto?"
            ),
            accion_correcta=(
                "Reconocer que no se puede atribuir impacto, documentar resultados observados y "
                "definir línea base hacia adelante"
            ),
            acciones_incorrectas=(
                D("Reconstruir una línea base con los registros disponibles del período inicial",
                  "Una línea base reconstruida a conveniencia no soporta ninguna atribución."),
                D("Comparar la situación actual con el promedio del sector como referencia externa",
                  "El promedio sectorial no controla las diferencias iniciales del grupo."),
                D("Declarar impacto positivo respaldado por los testimonios de los participantes",
                  "El testimonio ilustra, pero no permite atribuir el cambio al programa."),
            ),
            explicacion_escenario=(
                "Decir «no puedo atribuir impacto, y desde ahora sí podré» es más sólido que una "
                "atribución fabricada."
            ),
        ),
        Concepto(
            codigo="VCM-10", nombre="La integración de vinculación y docencia", nivel_minimo=3,
            microlearning=(
                "La integración ocurre cuando la vinculación deja de ser una actividad paralela y "
                "pasa a ser parte de la formación: estudiantes que trabajan sobre problemas "
                "reales dentro de asignaturas, con evaluación asociada. Es el nivel más maduro de "
                "esta dimensión, y también el que más evidencia deja, porque queda inscrito en "
                "programas y actas."
            ),
            definicion=(
                "La incorporación de la vinculación dentro de asignaturas del plan, con "
                "resultados de aprendizaje y evaluación asociados"
            ),
            confusiones=(
                D("La participación de estudiantes como voluntarios en actividades con la comunidad",
                  "El voluntariado es valioso pero queda fuera del plan y sin evaluación."),
                D("La realización de prácticas profesionales en organizaciones del medio relevante",
                  "La práctica es una modalidad establecida, distinta de integrar VcM al currículo."),
                D("La invitación de profesionales externos a exponer en asignaturas de la carrera",
                  "La charla externa enriquece la clase, pero no involucra un problema real trabajado."),
            ),
            explicacion_definicion=(
                "Lo que la define es que esté en el plan, con resultado de aprendizaje y "
                "evaluación: ahí deja de ser paralela."
            ),
            escenario=(
                "Una carrera quiere acreditar integración de vinculación y docencia mostrando su "
                "programa de voluntariado estudiantil. ¿Qué observas?"
            ),
            accion_correcta=(
                "Que el voluntariado no está en el plan ni tiene evaluación asociada, y que la "
                "integración requiere ambas cosas"
            ),
            acciones_incorrectas=(
                D("Que el programa califica si se registra la participación de cada estudiante",
                  "Registrar participación no lo incorpora al plan ni le da evaluación."),
                D("Que basta con reconocer el voluntariado con créditos electivos en la carrera",
                  "El crédito por participar no equivale a un resultado de aprendizaje evaluado."),
                D("Que corresponde reportarlo bajo vinculación y no bajo integración con docencia",
                  "Reclasificar la etiqueta no responde qué le falta para integrarse al plan."),
            ),
            explicacion_escenario=(
                "Sin estar en el plan y sin evaluación, la actividad convive con la docencia pero "
                "no se integra a ella."
            ),
        ),
    ),
)
