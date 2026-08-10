"""
Investigación, Creación y/o Innovación — base de conocimiento.

CONTENIDO DE PRUEBA. Valida la máquina, no es material oficial de acreditación.

Nota de dominio: es la única de las cinco dimensiones de carácter voluntario, pero
necesaria para obtener el período máximo de vigencia de la acreditación.
"""
from ..tipos import Concepto, Dimension, Distractor as D

ICI = Dimension(
    codigo="ICI",
    nombre_oficial="Investigación, Creación y/o Innovación",
    encuadre=(
        "Esta dimensión es voluntaria pero necesaria para el período máximo de vigencia, y "
        "pregunta si la institución genera conocimiento propio y qué hace con él."
    ),
    conceptos=(
        Concepto(
            codigo="ICI-01", nombre="La investigación aplicada", nivel_minimo=1,
            microlearning=(
                "La investigación aplicada busca resolver un problema concreto de un sector o "
                "territorio, con método y resultados verificables. En instituciones "
                "técnico-profesionales suele ser la forma más natural de esta dimensión, porque "
                "conecta con el mundo productivo que ya es su medio relevante."
            ),
            definicion=(
                "La indagación sistemática orientada a resolver un problema concreto de un "
                "sector o territorio, con método y resultados verificables"
            ),
            confusiones=(
                D("El estudio de mercado que la institución realiza antes de abrir una carrera",
                  "El estudio de mercado apoya una decisión de gestión, no genera conocimiento nuevo."),
                D("La recopilación de buenas prácticas del sector para actualizar los programas",
                  "Recopilar prácticas existentes es actualización curricular, no indagación."),
                D("El diagnóstico institucional que se elabora durante la autoevaluación",
                  "El diagnóstico mira hacia adentro y responde a otro proceso."),
            ),
            explicacion_definicion=(
                "Problema concreto, método y resultado verificable: eso la distingue de un "
                "estudio de gestión."
            ),
            escenario=(
                "Un equipo docente quiere presentar como investigación aplicada un levantamiento "
                "de necesidades de capacitación de empresas de la zona. ¿Qué corresponde?"
            ),
            accion_correcta=(
                "Precisar la pregunta, el método y el resultado esperado, o reportarlo como "
                "vinculación si no los tiene"
            ),
            acciones_incorrectas=(
                D("Presentarlo como investigación aplicada, dado que aborda un problema real del sector",
                  "Abordar un problema real no basta: sin método y resultado verificable no califica."),
                D("Ampliar la muestra de empresas para darle mayor solidez al levantamiento",
                  "Más muestra sin pregunta ni método sigue siendo un levantamiento descriptivo."),
                D("Publicar los resultados en un medio institucional para darle carácter académico",
                  "Publicar no le agrega método a un trabajo que no lo tuvo."),
            ),
            explicacion_escenario=(
                "Un levantamiento puede ser un excelente insumo de vinculación; llamarlo "
                "investigación sin método debilita toda la dimensión."
            ),
        ),
        Concepto(
            codigo="ICI-02", nombre="La innovación", nivel_minimo=1,
            microlearning=(
                "Innovar es introducir algo nuevo que efectivamente se implementa y produce un "
                "cambio observable. La palabra clave es implementación: una idea nueva que no se "
                "puso en marcha es una propuesta. Y lo nuevo se juzga en el contexto donde se "
                "aplica, no en términos absolutos."
            ),
            definicion=(
                "La introducción de una solución nueva en su contexto que se implementa "
                "efectivamente y produce un cambio observable"
            ),
            confusiones=(
                D("La generación de ideas y propuestas de mejora por parte de los equipos",
                  "La idea es el punto de partida; sin implementación no hay innovación."),
                D("La incorporación de tecnología de última generación en los procesos",
                  "Adoptar tecnología puede ser innovación o solo actualización de equipamiento."),
                D("La obtención de un resultado superior al de períodos anteriores",
                  "Mejorar un resultado no implica que se haya introducido algo nuevo."),
            ),
            explicacion_definicion=(
                "Novedad en su contexto, implementación efectiva y cambio observable: los tres."
            ),
            escenario=(
                "Se reporta como innovación un nuevo sistema de gestión académica que fue "
                "adquirido pero aún no se pone en operación. ¿Qué corresponde?"
            ),
            accion_correcta=(
                "No reportarlo todavía como innovación: sin implementación no hay cambio "
                "observable que mostrar"
            ),
            acciones_incorrectas=(
                D("Reportarlo, señalando que la implementación está programada para el próximo período",
                  "Reportar lo que aún no ocurre compromete la credibilidad del resto del informe."),
                D("Reportarlo como innovación en curso y actualizar el estado más adelante",
                  "La categoría en curso invita a reportar intenciones como resultados."),
                D("Reportar la inversión realizada como evidencia del compromiso institucional",
                  "La inversión evidencia decisión, no innovación."),
            ),
            explicacion_escenario=(
                "Un sistema comprado y sin operar es una compra. Se vuelve innovación cuando "
                "cambia algo en la práctica."
            ),
        ),
        Concepto(
            codigo="ICI-03", nombre="La creación", nivel_minimo=1,
            microlearning=(
                "La creación es la producción de obra original en ámbitos artísticos, de diseño o "
                "proyectuales, con reconocimiento de pares o del campo. Está en la misma dimensión "
                "que investigación e innovación porque también genera conocimiento nuevo, aunque "
                "su forma de validación sea distinta: exposición, publicación, premiación, "
                "circulación en el campo."
            ),
            definicion=(
                "La producción de obra original en ámbitos artísticos o proyectuales, validada "
                "por el reconocimiento de pares o del campo"
            ),
            confusiones=(
                D("El trabajo final que los estudiantes desarrollan para obtener su título",
                  "El trabajo de titulación es una actividad formativa, no producción validada."),
                D("La producción de material didáctico y recursos para las asignaturas",
                  "El material docente apoya la enseñanza; no se valida como obra original."),
                D("La organización de exposiciones y muestras abiertas a la comunidad",
                  "Difundir obra es extensión; crear obra es otra cosa."),
            ),
            explicacion_definicion=(
                "Originalidad y validación por el campo: sin la segunda, la obra existe pero no "
                "acredita esta dimensión."
            ),
            escenario=(
                "La escuela de diseño quiere reportar como creación los proyectos de titulación de "
                "sus estudiantes. ¿Qué corresponde?"
            ),
            accion_correcta=(
                "Reportar solo aquellos que hayan tenido validación externa del campo, y el resto "
                "como actividad formativa"
            ),
            acciones_incorrectas=(
                D("Reportarlos todos, ya que constituyen producción original de la escuela",
                  "Sin validación externa no se distingue producción académica de obra reconocida."),
                D("Reportar una selección de los mejores proyectos evaluados por la escuela",
                  "La evaluación interna no equivale al reconocimiento del campo."),
                D("Reportarlos como creación estudiantil en una categoría separada del informe",
                  "Crear una categoría propia no resuelve la falta de validación externa."),
            ),
            explicacion_escenario=(
                "El proyecto que se expuso o fue premiado tiene validación; el resto es formación, "
                "y también vale, en otra dimensión."
            ),
        ),
        Concepto(
            codigo="ICI-04", nombre="La productividad académica", nivel_minimo=1,
            microlearning=(
                "La productividad académica es el conjunto de resultados formalizados que produce "
                "la institución: publicaciones, ponencias, patentes, obra reconocida. Lo relevante "
                "no es solo el número sino su relación con la misión: en una institución "
                "técnico-profesional, una patente o una transferencia puede valer más que un "
                "artículo en una revista alejada de su campo."
            ),
            definicion=(
                "El conjunto de resultados formalizados y verificables que produce la institución, "
                "leído en relación con su misión"
            ),
            confusiones=(
                D("El número de académicos con grado de doctor que integran la planta institucional",
                  "La planta es una capacidad instalada, no un resultado producido."),
                D("Las horas destinadas a actividades de investigación en la carga académica",
                  "Las horas son insumo; la productividad son los resultados."),
                D("Los proyectos de investigación que se encuentran en ejecución en el período",
                  "El proyecto en curso todavía no produjo resultados formalizados."),
            ),
            explicacion_definicion=(
                "Resultados formalizados y verificables, y siempre leídos contra la misión de la "
                "institución."
            ),
            escenario=(
                "Una institución técnico-profesional compara su productividad con la de "
                "universidades complejas y concluye que es baja. ¿Qué observas?"
            ),
            accion_correcta=(
                "Que la comparación debe hacerse contra su propia misión y su segmento, no contra "
                "un modelo institucional distinto"
            ),
            acciones_incorrectas=(
                D("Que la conclusión es correcta y debe declararse como debilidad institucional",
                  "Declarar debilidad contra un referente que no corresponde distorsiona el diagnóstico."),
                D("Que conviene aumentar la producción de artículos para acortar la brecha",
                  "Perseguir un referente ajeno desvía recursos de lo que sí corresponde a la misión."),
                D("Que la comparación no es pertinente y el análisis debe omitirse del informe",
                  "Omitir el análisis deja la dimensión sin lectura; lo que cambia es el referente."),
            ),
            explicacion_escenario=(
                "El referente importa tanto como el dato: comparar contra otro tipo de institución "
                "produce un diagnóstico falso."
            ),
        ),
        Concepto(
            codigo="ICI-05", nombre="La transferencia", nivel_minimo=1,
            microlearning=(
                "Transferir es que el conocimiento generado llegue a alguien que lo usa fuera de "
                "la institución. Puede ser una empresa que adopta un procedimiento, un servicio "
                "público que aplica un modelo, una comunidad que incorpora una práctica. Sin "
                "receptor identificado y sin uso, hay difusión pero no transferencia."
            ),
            definicion=(
                "El proceso por el cual el conocimiento generado llega a un receptor externo "
                "identificado que efectivamente lo utiliza"
            ),
            confusiones=(
                D("La publicación de los resultados de investigación en medios especializados",
                  "Publicar pone el conocimiento disponible; no acredita que alguien lo use."),
                D("La presentación de hallazgos en congresos y seminarios del área disciplinar",
                  "La presentación es difusión entre pares, no transferencia a un usuario."),
                D("La capacitación de los equipos internos en los resultados obtenidos",
                  "Capacitar hacia adentro no involucra a un receptor externo."),
            ),
            explicacion_definicion=(
                "Receptor externo identificado y uso efectivo: sin esos dos, es difusión."
            ),
            escenario=(
                "Un proyecto desarrolló un protocolo y lo publicó en el repositorio institucional. "
                "Se reporta como transferencia. ¿Qué corresponde?"
            ),
            accion_correcta=(
                "Reportarlo como difusión, salvo que se identifique una organización que haya "
                "adoptado el protocolo"
            ),
            acciones_incorrectas=(
                D("Mantenerlo como transferencia, ya que el protocolo quedó disponible para el sector",
                  "Disponible no es adoptado: falta el receptor que lo usa."),
                D("Complementar con las estadísticas de descarga del repositorio institucional",
                  "Las descargas miden interés, no uso ni adopción."),
                D("Enviar el protocolo a las empresas del sector para formalizar la transferencia",
                  "Enviar es difundir; la transferencia se acredita cuando alguien lo incorpora."),
            ),
            explicacion_escenario=(
                "La pregunta que decide es simple: ¿quién lo está usando? Si no hay nombre, no "
                "hubo transferencia."
            ),
        ),
        Concepto(
            codigo="ICI-06", nombre="La política de investigación", nivel_minimo=1,
            microlearning=(
                "La política define qué tipo de investigación, creación o innovación va a "
                "priorizar la institución según su misión, y con qué recursos y reglas. Su "
                "función principal es acotar: una institución que declara priorizarlo todo no "
                "priorizó nada, y sus resultados terminan dispersos y difíciles de sostener."
            ),
            definicion=(
                "El marco que define qué se prioriza en investigación, creación e innovación "
                "según la misión, con sus recursos y reglas"
            ),
            confusiones=(
                D("El reglamento que regula la asignación de fondos concursables internos",
                  "El reglamento operativiza la política; no define las prioridades."),
                D("El plan de trabajo anual de la unidad responsable de investigación",
                  "El plan ejecuta; la política orienta y acota el ámbito."),
                D("El conjunto de líneas de investigación declaradas por las escuelas",
                  "Las líneas son resultado de la política, no la política misma."),
            ),
            explicacion_definicion=(
                "Su valor está en priorizar: define qué sí y, por lo tanto, qué no."
            ),
            escenario=(
                "La política institucional declara doce líneas prioritarias y la institución tiene "
                "capacidad para sostener tres. ¿Qué corresponde?"
            ),
            accion_correcta=(
                "Reducir las líneas a las que la capacidad instalada permite sostener con "
                "resultados verificables"
            ),
            acciones_incorrectas=(
                D("Mantener las doce líneas para no cerrar oportunidades de desarrollo futuro",
                  "Mantener doce sin capacidad produce doce líneas sin resultados."),
                D("Priorizar tres líneas en la práctica y conservar las doce en el documento",
                  "La distancia entre el documento y la práctica es justamente lo que se detecta."),
                D("Buscar financiamiento externo que permita activar las líneas restantes",
                  "Condicionar la política a un financiamiento incierto la deja sin vigencia real."),
            ),
            explicacion_escenario=(
                "Una política que no acota no orienta, y una lista de doce prioridades es una "
                "lista sin prioridades."
            ),
        ),
        Concepto(
            codigo="ICI-07", nombre="Las capacidades instaladas", nivel_minimo=2,
            microlearning=(
                "Las capacidades instaladas son las condiciones que hacen posible investigar: "
                "personas con dedicación real, infraestructura, financiamiento y reglas. La "
                "palabra que más pesa es dedicación: horas comprometidas en el contrato y "
                "protegidas en la práctica. Sin eso, la investigación depende del entusiasmo "
                "personal y no sobrevive a un cambio de equipo."
            ),
            definicion=(
                "Las condiciones estables —dedicación protegida, infraestructura, financiamiento "
                "y reglas— que hacen posible la actividad de investigación"
            ),
            confusiones=(
                D("La cantidad de proyectos que la institución logra adjudicar en cada período",
                  "Los proyectos adjudicados son resultado de la capacidad, no la capacidad."),
                D("El nivel de formación de posgrado alcanzado por el cuerpo académico",
                  "La formación es un componente, pero sin dedicación protegida no se traduce en actividad."),
                D("La disponibilidad de laboratorios y equipamiento científico en las sedes",
                  "La infraestructura es una parte; falta dedicación, financiamiento y reglas."),
            ),
            explicacion_definicion=(
                "Dedicación protegida es la condición que más suele faltar y sin la cual el resto "
                "no opera."
            ),
            escenario=(
                "La institución reporta veinte académicos investigadores, pero ninguno tiene horas "
                "de investigación en su contrato. ¿Qué corresponde?"
            ),
            accion_correcta=(
                "Declarar la brecha de dedicación como debilidad y comprometer horas protegidas "
                "para un núcleo acotado"
            ),
            acciones_incorrectas=(
                D("Reportar los veinte académicos como capacidad instalada de investigación",
                  "Sin horas protegidas esos veinte no constituyen capacidad instalada."),
                D("Registrar las horas efectivamente dedicadas fuera de la jornada comprometida",
                  "Formalizar el trabajo fuera de jornada institucionaliza una práctica insostenible."),
                D("Priorizar la contratación de nuevos investigadores con dedicación exclusiva",
                  "Contratar sin resolver las reglas de dedicación repite el problema con más gente."),
            ),
            explicacion_escenario=(
                "Veinte personas sin horas no son capacidad; tres con horas protegidas sí lo son."
            ),
        ),
        Concepto(
            codigo="ICI-08", nombre="La vinculación entre investigación y docencia", nivel_minimo=2,
            microlearning=(
                "Esta relación se comprueba cuando lo que se investiga entra al aula: casos "
                "actualizados, estudiantes participando en proyectos, contenidos que cambian a "
                "partir de resultados propios. Es especialmente relevante en instituciones "
                "técnico-profesionales, donde la investigación aplicada puede alimentar "
                "directamente lo que se enseña."
            ),
            definicion=(
                "La incorporación verificable de resultados de investigación en el currículo y "
                "en la experiencia formativa de los estudiantes"
            ),
            confusiones=(
                D("La participación de los docentes de la carrera en proyectos de investigación",
                  "Que el docente investigue no garantiza que eso llegue a sus asignaturas."),
                D("La existencia de asignaturas de metodología de investigación en el plan",
                  "Enseñar metodología no es incorporar resultados propios al currículo."),
                D("La realización de seminarios donde se presentan los avances de los proyectos",
                  "El seminario difunde; no modifica el currículo ni la experiencia formativa."),
            ),
            explicacion_definicion=(
                "Lo verificable es el cambio en el currículo o en la experiencia del estudiante, "
                "no la actividad del docente."
            ),
            escenario=(
                "Un proyecto de investigación aplicada terminó hace un año con resultados útiles "
                "y ninguna asignatura los incorporó. ¿Qué corresponde?"
            ),
            accion_correcta=(
                "Llevar los resultados a la instancia curricular y definir en qué asignaturas se "
                "incorporarán"
            ),
            acciones_incorrectas=(
                D("Difundir el informe final entre los docentes del área para que lo consideren",
                  "Difundir deja la incorporación librada a la iniciativa individual."),
                D("Incorporar los resultados como lectura complementaria en las asignaturas afines",
                  "La lectura complementaria es lo primero que se cae cuando aprieta el programa."),
                D("Programar un seminario donde el equipo presente los resultados a estudiantes",
                  "Un seminario puntual no modifica el currículo."),
            ),
            explicacion_escenario=(
                "Sin decisión curricular, el resultado se queda en el informe final y la relación "
                "no se produce."
            ),
        ),
        Concepto(
            codigo="ICI-09", nombre="El impacto de la investigación", nivel_minimo=3,
            microlearning=(
                "El impacto de la investigación es el efecto que sus resultados producen fuera de "
                "la institución: en un sector, en una política, en una práctica profesional. Se "
                "confunde con productividad porque ambos se reportan juntos, pero publicar mucho y "
                "no cambiar nada es perfectamente posible. La atribución acá es exigente y conviene "
                "ser prudente al declararla."
            ),
            definicion=(
                "El efecto verificable que los resultados de investigación producen fuera de la "
                "institución, en prácticas, políticas o sectores"
            ),
            confusiones=(
                D("El número de citaciones que reciben las publicaciones de la institución",
                  "La citación mide circulación académica, no efecto en la práctica."),
                D("El volumen de financiamiento externo captado por los proyectos institucionales",
                  "El financiamiento es insumo, no efecto producido."),
                D("El reconocimiento obtenido por los investigadores en instancias del área",
                  "El reconocimiento es a las personas; el impacto es sobre el entorno."),
            ),
            explicacion_definicion=(
                "Es un efecto fuera de la institución, y por eso exige mostrar qué cambió y en "
                "quién."
            ),
            escenario=(
                "Se quiere declarar impacto porque una publicación institucional fue citada en un "
                "documento de política pública. ¿Qué corresponde?"
            ),
            accion_correcta=(
                "Verificar si la cita influyó en una decisión concreta antes de declarar impacto; "
                "si no, reportarla como circulación"
            ),
            acciones_incorrectas=(
                D("Declarar impacto en política pública, respaldado por la cita en el documento",
                  "Ser citado no acredita haber influido en la decisión."),
                D("Declarar impacto potencial, señalando que la política aún está en tramitación",
                  "El impacto potencial no es impacto; declararlo así relaja el estándar."),
                D("Complementar la cita con el número de descargas de la publicación",
                  "Las descargas refuerzan circulación, no influencia."),
            ),
            explicacion_escenario=(
                "Ser citado es circulación. El impacto aparece cuando se puede mostrar qué "
                "decisión cambió."
            ),
        ),
        Concepto(
            codigo="ICI-10", nombre="La ética de la investigación", nivel_minimo=3,
            microlearning=(
                "La ética de la investigación es el conjunto de resguardos que protegen a las "
                "personas involucradas y la integridad del proceso: consentimiento informado, "
                "manejo de datos personales, declaración de conflictos de interés, revisión previa "
                "por una instancia independiente. Su ausencia no se compensa con la calidad del "
                "resultado."
            ),
            definicion=(
                "El conjunto de resguardos que protege a las personas participantes y la "
                "integridad del proceso, con revisión previa e independiente"
            ),
            confusiones=(
                D("El cumplimiento de las normas de citación y atribución de autoría",
                  "La integridad académica es parte, pero no cubre la protección de participantes."),
                D("La protección de la propiedad intelectual de los resultados obtenidos",
                  "La propiedad intelectual regula derechos sobre el resultado, no resguardos éticos."),
                D("La aprobación del proyecto por la unidad que administra los fondos internos",
                  "La aprobación administrativa no equivale a revisión ética independiente."),
            ),
            explicacion_definicion=(
                "Resguardo de las personas más revisión previa e independiente: lo segundo es lo "
                "que suele faltar."
            ),
            escenario=(
                "Un proyecto que recogerá datos de salud de estudiantes ya comenzó el trabajo de "
                "campo sin revisión ética previa. ¿Qué corresponde?"
            ),
            accion_correcta=(
                "Suspender el trabajo de campo hasta obtener la revisión ética, y evaluar qué "
                "hacer con lo ya recogido"
            ),
            acciones_incorrectas=(
                D("Continuar el trabajo de campo y presentar el proyecto a revisión en paralelo",
                  "Seguir recogiendo datos sensibles sin resguardo aprobado expone a los participantes."),
                D("Solicitar consentimiento informado a los participantes y continuar el estudio",
                  "El consentimiento es necesario pero no reemplaza la revisión independiente."),
                D("Regularizar la situación al momento de publicar los resultados del proyecto",
                  "La revisión es previa por definición: regularizar al final no protege a nadie."),
            ),
            explicacion_escenario=(
                "Con datos de salud el resguardo es previo y no negociable; lo ya recogido debe "
                "evaluarse aparte."
            ),
        ),
    ),
)
