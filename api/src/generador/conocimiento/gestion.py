"""
Gestión Estratégica y Recursos Institucionales — base de conocimiento.

CONTENIDO DE PRUEBA. Valida la máquina, no es material oficial de acreditación.
"""
from ..tipos import Concepto, Dimension, Distractor as D

GESTION = Dimension(
    codigo="GESTION",
    nombre_oficial="Gestión Estratégica y Recursos Institucionales",
    encuadre=(
        "Esta dimensión pregunta si la institución sabe hacia dónde va, si organiza sus "
        "recursos para llegar y si puede sostenerlo en el tiempo."
    ),
    conceptos=(
        Concepto(
            codigo="GESTION-01", nombre="La misión institucional", nivel_minimo=1,
            microlearning=(
                "La misión declara a quién sirve la institución y con qué propósito. Suena "
                "abstracto hasta que se usa como vara: cada decisión relevante debería poder "
                "explicarse desde ella. Una misión que no discrimina —que serviría igual para "
                "cualquier otra institución— no orienta nada. En la evaluación, lo que se mira "
                "no es la redacción sino si las decisiones reales son coherentes con lo declarado."
            ),
            definicion=(
                "La declaración del propósito de la institución y de a quién sirve, que "
                "orienta y permite justificar sus decisiones"
            ),
            confusiones=(
                D("La proyección de dónde quiere estar la institución en el mediano plazo",
                  "Eso es la visión: mira al futuro deseado, no al propósito actual."),
                D("El conjunto de objetivos estratégicos comprometidos para el período",
                  "Los objetivos bajan la misión a metas, pero no la reemplazan."),
                D("La descripción de la oferta académica y los servicios que entrega",
                  "La oferta es lo que se hace; la misión es para qué se hace."),
            ),
            explicacion_definicion=(
                "La misión responde para qué existe la institución y para quién, y por eso sirve "
                "como criterio al decidir."
            ),
            escenario=(
                "Se evalúa abrir un programa rentable pero dirigido a un público que la misión no "
                "menciona. ¿Cuál es el aporte más consistente?"
            ),
            accion_correcta=(
                "Analizar explícitamente la coherencia con la misión y, si no la hay, resolver "
                "esa tensión antes de decidir"
            ),
            acciones_incorrectas=(
                D("Aprobar el programa por su aporte financiero y revisar la misión más adelante",
                  "Decidir primero y acomodar la misión después la vacía de función orientadora."),
                D("Rechazar el programa sin análisis, por no estar mencionado en la misión",
                  "La misión orienta el análisis; no es una lista cerrada de lo permitido."),
                D("Delegar la decisión al área comercial, que maneja el estudio de demanda",
                  "La demanda es un insumo, pero la coherencia institucional no se delega."),
            ),
            explicacion_escenario=(
                "Lo que se evalúa es si la misión se usa al decidir. Hacer explícita la tensión "
                "es exactamente ese uso."
            ),
        ),
        Concepto(
            codigo="GESTION-02", nombre="El plan de desarrollo institucional", nivel_minimo=1,
            microlearning=(
                "El plan de desarrollo traduce la misión en objetivos con metas y plazos para un "
                "período definido. Su valor no está en el documento sino en si se usa: si las "
                "decisiones presupuestarias lo citan, si alguien revisa su avance periódicamente "
                "y si se ajusta cuando el contexto cambia. Un plan que nadie consulta entre su "
                "lanzamiento y su evaluación final no está cumpliendo su función."
            ),
            definicion=(
                "El instrumento que traduce la misión en objetivos con metas y plazos para un "
                "período, y cuyo avance se revisa periódicamente"
            ),
            confusiones=(
                D("El presupuesto plurianual que asigna recursos a las unidades académicas",
                  "El presupuesto financia el plan; no define sus objetivos ni sus metas."),
                D("El informe anual de gestión que reporta los resultados alcanzados",
                  "El informe rinde cuenta de lo hecho; el plan compromete lo que se hará."),
                D("El conjunto de proyectos de mejora derivados de la última acreditación",
                  "Esos proyectos son consecuencia de un diagnóstico, no el plan institucional."),
            ),
            explicacion_definicion=(
                "Objetivos, metas, plazos y revisión periódica: sin lo último el plan se vuelve "
                "un documento de archivo."
            ),
            escenario=(
                "Tu unidad debe reportar avance del plan de desarrollo y descubre que nadie lo "
                "revisó en dieciocho meses. ¿Qué haces?"
            ),
            accion_correcta=(
                "Reportar el avance real, señalar la ausencia de revisión como brecha y proponer "
                "una instancia periódica"
            ),
            acciones_incorrectas=(
                D("Reconstruir el avance estimado para cada objetivo y reportarlo como seguimiento",
                  "Estimar hacia atrás produce un dato que no resiste una pregunta de la visita."),
                D("Reportar solo los objetivos donde hubo avance verificable durante el período",
                  "Omitir los objetivos sin avance esconde justamente lo que hay que corregir."),
                D("Solicitar una prórroga del plan antes de emitir cualquier reporte de avance",
                  "Prorrogar no responde la pregunta de qué pasó en los dieciocho meses."),
            ),
            explicacion_escenario=(
                "La ausencia de seguimiento es en sí misma un hallazgo valioso, y declararla vale "
                "más que fabricar un avance."
            ),
        ),
        Concepto(
            codigo="GESTION-03", nombre="Los recursos institucionales", nivel_minimo=1,
            microlearning=(
                "Recursos no son solo dinero: son personas, infraestructura, equipamiento y "
                "sistemas de información. La pregunta de la evaluación no es cuántos hay, sino si "
                "alcanzan para lo que la institución declara hacer y si se distribuyen con algún "
                "criterio explicable. Un recurso abundante mal asignado es tan problemático como "
                "uno escaso."
            ),
            definicion=(
                "El conjunto de personas, infraestructura, equipamiento y sistemas que sostienen "
                "lo que la institución declara hacer"
            ),
            confusiones=(
                D("Los ingresos operacionales que la institución percibe durante el período",
                  "Los ingresos son una fuente de recursos, no el conjunto de recursos."),
                D("La infraestructura física disponible en cada una de las sedes",
                  "La infraestructura es un componente; deja fuera personas y sistemas."),
                D("La dotación de académicos y su distribución por jornada y grado",
                  "La dotación es parte del recurso humano, no el conjunto completo."),
            ),
            explicacion_definicion=(
                "Personas, infraestructura, equipamiento y sistemas: el conjunto que hace posible "
                "cumplir lo declarado."
            ),
            escenario=(
                "Una carrera declara formación práctica intensiva pero comparte un solo "
                "laboratorio con otras tres carreras. ¿Qué corresponde?"
            ),
            accion_correcta=(
                "Levantar la brecha entre lo declarado y la capacidad instalada, con el dato de "
                "uso, y llevarla al plan de mejora"
            ),
            acciones_incorrectas=(
                D("Ajustar el discurso de la carrera para no comprometer formación práctica intensiva",
                  "Bajar la declaración resuelve el informe, pero no la formación de los estudiantes."),
                D("Reorganizar los horarios para que el laboratorio alcance sin inversión adicional",
                  "Puede aliviar, pero sin dimensionar la brecha no se sabe si alcanza."),
                D("Reportar la disponibilidad del laboratorio sin referirla al número de estudiantes",
                  "El dato absoluto sin relación con la demanda no dice si el recurso alcanza."),
            ),
            explicacion_escenario=(
                "Lo que se evalúa es la coherencia entre lo declarado y lo disponible; "
                "dimensionar la brecha es el primer paso para cerrarla."
            ),
        ),
        Concepto(
            codigo="GESTION-04", nombre="La estructura de gobierno", nivel_minimo=1,
            microlearning=(
                "La estructura de gobierno define quién decide qué y ante quién responde. En un "
                "proceso de autoevaluación esto se vuelve muy concreto: cada instancia tiene un "
                "producto y una atribución. Cuando las atribuciones no están claras, las "
                "decisiones se toman dos veces o ninguna, y eso aparece en el informe como "
                "descoordinación."
            ),
            definicion=(
                "El conjunto de instancias con atribuciones definidas que establece quién decide "
                "qué y ante quién responde"
            ),
            confusiones=(
                D("El organigrama que representa las dependencias jerárquicas de la institución",
                  "El organigrama muestra dependencias, pero no las atribuciones de decisión."),
                D("El reglamento interno que regula los deberes del personal institucional",
                  "El reglamento regula conductas; el gobierno distribuye atribuciones."),
                D("El equipo directivo superior que conduce la marcha cotidiana de la institución",
                  "Ese equipo es parte de la estructura, no la estructura completa."),
            ),
            explicacion_definicion=(
                "Lo definitorio son las atribuciones y la responsabilidad: quién decide y ante "
                "quién responde por esa decisión."
            ),
            escenario=(
                "Dos instancias se atribuyen la aprobación del mismo documento del proceso y "
                "ninguna avanza. ¿Qué corresponde hacer?"
            ),
            accion_correcta=(
                "Revisar las atribuciones formales de cada instancia y dejar por escrito a quién "
                "corresponde la aprobación"
            ),
            acciones_incorrectas=(
                D("Someter el documento a ambas instancias para asegurar que quede bien respaldado",
                  "La doble aprobación no resuelve la ambigüedad: la institucionaliza."),
                D("Escalar la decisión al nivel superior para destrabar el proceso rápidamente",
                  "Escalar destraba este caso puntual y deja el vacío para el siguiente."),
                D("Aprobarlo en la instancia que reúna primero el quórum necesario para sesionar",
                  "Resolver por disponibilidad convierte una atribución en un accidente."),
            ),
            explicacion_escenario=(
                "El problema no es este documento: es que la atribución no está definida. "
                "Aclararla resuelve todos los casos siguientes."
            ),
        ),
        Concepto(
            codigo="GESTION-05", nombre="Un indicador institucional", nivel_minimo=1,
            microlearning=(
                "Un indicador es una medida acordada que permite observar un fenómeno a lo largo "
                "del tiempo. Para que sirva necesita tres cosas: una fórmula estable, una fuente "
                "definida y una periodicidad. Si la fórmula cambia entre períodos, la serie deja "
                "de ser comparable y el indicador pierde su única gracia, que es mostrar "
                "trayectoria."
            ),
            definicion=(
                "Una medida con fórmula estable, fuente definida y periodicidad, que permite "
                "observar un fenómeno a lo largo del tiempo"
            ),
            confusiones=(
                D("La meta comprometida por la institución para una variable relevante",
                  "La meta es el valor esperado; el indicador es la medida que lo observa."),
                D("El dato puntual que reporta una unidad al cierre de cada período académico",
                  "Un dato aislado sin fórmula ni serie no permite observar trayectoria."),
                D("El sistema que consolida la información de gestión de la institución",
                  "El sistema almacena indicadores; no es un indicador."),
            ),
            explicacion_definicion=(
                "Fórmula estable, fuente definida y periodicidad: los tres son lo que hace "
                "comparable la serie en el tiempo."
            ),
            escenario=(
                "Para mostrar mejor resultado, alguien propone cambiar la fórmula de un indicador "
                "en el período actual. ¿Qué respondes?"
            ),
            accion_correcta=(
                "Que cambiar la fórmula rompe la comparabilidad, y si se cambia debe recalcularse "
                "toda la serie y declararlo"
            ),
            acciones_incorrectas=(
                D("Que se aplique la nueva fórmula desde este período y se explique en una nota",
                  "La nota no repara la serie: quedan dos métricas distintas presentadas como una."),
                D("Que se reporten ambas fórmulas y el lector elija cuál considera más adecuada",
                  "Trasladar la decisión al lector es evitar tomar posición sobre la propia medida."),
                D("Que se mantenga la fórmula antigua solo para los indicadores comprometidos",
                  "Convivir con dos criterios según conveniencia es lo que destruye la confianza."),
            ),
            explicacion_escenario=(
                "Un cambio metodológico es legítimo si se declara y se recalcula hacia atrás. Sin "
                "eso, es una mejora aparente."
            ),
        ),
        Concepto(
            codigo="GESTION-06", nombre="La sostenibilidad financiera", nivel_minimo=1,
            microlearning=(
                "La sostenibilidad financiera es la capacidad de sostener el proyecto educativo en "
                "el tiempo, no de tener superávit este año. Se mira la estructura: de dónde vienen "
                "los ingresos, qué tan concentrados están, y si los compromisos futuros están "
                "cubiertos. Una institución puede tener un buen año y una estructura frágil."
            ),
            definicion=(
                "La capacidad de sostener el proyecto educativo en el tiempo, considerando la "
                "estructura de ingresos y los compromisos futuros"
            ),
            confusiones=(
                D("El resultado operacional positivo obtenido al cierre del último ejercicio",
                  "Un buen año no dice nada sobre la estructura ni sobre el mediano plazo."),
                D("El nivel de endeudamiento que la institución mantiene con el sistema financiero",
                  "La deuda es un componente, no la capacidad de sostener el proyecto."),
                D("La disponibilidad de recursos para ejecutar el plan de mejora comprometido",
                  "Financiar el plan es una parte pequeña de la sostenibilidad institucional."),
            ),
            explicacion_definicion=(
                "Lo que importa es la estructura y el horizonte: sostener el proyecto, no cerrar "
                "bien un ejercicio."
            ),
            escenario=(
                "La institución tuvo tres años de superávit, pero el 80% de sus ingresos depende "
                "de dos programas. ¿Cómo se lee?"
            ),
            accion_correcta=(
                "Como una fortaleza de resultado con un riesgo de concentración que debe "
                "declararse y gestionarse"
            ),
            acciones_incorrectas=(
                D("Como una fortaleza plena, porque el resultado positivo se sostuvo tres años",
                  "Tres años de superávit no compensan una dependencia de dos programas."),
                D("Como una debilidad, porque la dependencia de dos programas es insostenible",
                  "Llamarla debilidad sin más ignora que el resultado sí es sólido."),
                D("Como un dato financiero que no corresponde analizar en la autoevaluación",
                  "La sostenibilidad es parte de esta dimensión: excluirla deja un vacío."),
            ),
            explicacion_escenario=(
                "Nombrar la fortaleza y el riesgo en la misma frase es más creíble que elegir "
                "solo uno de los dos."
            ),
        ),
        Concepto(
            codigo="GESTION-07", nombre="La alineación estratégica", nivel_minimo=2,
            microlearning=(
                "Alineación es que lo que se decide abajo tenga que ver con lo que se declaró "
                "arriba. Se comprueba de manera bastante concreta: tomando una decisión "
                "presupuestaria relevante y preguntando a qué objetivo del plan responde. Si la "
                "respuesta no existe, hay dos posibilidades: o la decisión sobra, o el plan no "
                "refleja lo que la institución realmente prioriza."
            ),
            definicion=(
                "La correspondencia verificable entre las decisiones y asignaciones concretas y "
                "los objetivos declarados en el plan"
            ),
            confusiones=(
                D("La difusión del plan de desarrollo entre todas las unidades institucionales",
                  "Difundir el plan no garantiza que las decisiones respondan a él."),
                D("La participación de las unidades en la formulación de los objetivos del plan",
                  "Participar en la formulación es previo; la alineación se ve en la ejecución."),
                D("La coherencia entre la misión declarada y la visión de mediano plazo",
                  "Esa coherencia es interna al discurso; la alineación baja a las decisiones."),
            ),
            explicacion_definicion=(
                "La prueba es de ida y vuelta: cada decisión relevante debería poder rastrearse "
                "hasta un objetivo del plan."
            ),
            escenario=(
                "El mayor gasto del año no responde a ningún objetivo del plan de desarrollo. "
                "¿Qué corresponde?"
            ),
            accion_correcta=(
                "Documentar el desalineamiento y resolver si se justifica la decisión o si el "
                "plan debe actualizarse formalmente"
            ),
            acciones_incorrectas=(
                D("Asociar el gasto al objetivo del plan que resulte más cercano temáticamente",
                  "Forzar la asociación produce una alineación aparente que no resiste revisión."),
                D("Excluir ese gasto del análisis por corresponder a una necesidad operacional",
                  "Excluir el gasto mayor del análisis deja fuera justamente lo más relevante."),
                D("Registrarlo como gasto extraordinario y mantener el plan sin modificaciones",
                  "Etiquetarlo de extraordinario no explica por qué el plan no lo previó."),
            ),
            explicacion_escenario=(
                "Una desalineación declarada y resuelta muestra un sistema que funciona; una "
                "escondida muestra un plan decorativo."
            ),
        ),
        Concepto(
            codigo="GESTION-08", nombre="La rendición de cuentas", nivel_minimo=2,
            microlearning=(
                "Rendir cuentas es informar de manera regular y comprensible qué se hizo con los "
                "recursos y qué resultados se obtuvieron, ante quienes tienen derecho a saberlo. "
                "Lo que la distingue de una campaña comunicacional es que incluye lo que no "
                "resultó. Una rendición que solo comunica logros entrena a la comunidad a "
                "desconfiar de ella."
            ),
            definicion=(
                "La entrega regular y comprensible de información sobre el uso de los recursos y "
                "los resultados, incluidos los no logrados"
            ),
            confusiones=(
                D("La publicación de los estados financieros auditados de cada ejercicio",
                  "Los estados financieros son un componente, y no cubren los resultados."),
                D("La comunicación institucional de los logros alcanzados durante el período",
                  "Comunicar solo logros es difusión, no rendición de cuentas."),
                D("La respuesta a los requerimientos de información de los organismos externos",
                  "Responder requerimientos es una obligación distinta de rendir cuentas."),
            ),
            explicacion_definicion=(
                "Incluir lo no logrado es lo que la vuelve creíble; sin eso es comunicación "
                "institucional con otro nombre."
            ),
            escenario=(
                "En la cuenta pública anual se propone omitir dos metas incumplidas para no dar "
                "una señal negativa. ¿Qué planteas?"
            ),
            accion_correcta=(
                "Incluirlas con su explicación y las medidas adoptadas, porque omitirlas debilita "
                "toda la rendición"
            ),
            acciones_incorrectas=(
                D("Omitirlas este año y reportarlas cuando muestren recuperación en el siguiente",
                  "Postergar la mala noticia hace que después se lea como un ocultamiento."),
                D("Presentarlas agregadas con otras metas para que el resultado global sea positivo",
                  "Agregar para diluir es una forma de omitir que además compromete la serie."),
                D("Mencionarlas sin cifras, señalando que están en proceso de recuperación",
                  "Sin cifra no hay rendición: queda una afirmación que nadie puede contrastar."),
            ),
            explicacion_escenario=(
                "La credibilidad de una rendición se construye justamente en cómo trata lo que "
                "salió mal."
            ),
        ),
        Concepto(
            codigo="GESTION-09", nombre="La gestión de riesgos institucionales", nivel_minimo=3,
            microlearning=(
                "Gestionar riesgos es identificar por anticipado qué podría impedir cumplir los "
                "objetivos, estimar su probabilidad e impacto, y decidir qué hacer con cada uno: "
                "mitigarlo, transferirlo, aceptarlo o evitarlo. Lo que distingue una gestión real "
                "de un registro formal es que los riesgos se revisan cuando cambia el contexto y "
                "que alguien responde por cada uno."
            ),
            definicion=(
                "La identificación anticipada de lo que puede impedir cumplir los objetivos, con "
                "su valoración y una decisión asignada a un responsable"
            ),
            confusiones=(
                D("El registro de los incidentes ocurridos y de las medidas correctivas aplicadas",
                  "Eso mira hacia atrás; la gestión de riesgos anticipa lo que aún no ocurre."),
                D("El conjunto de seguros y coberturas contratados para proteger el patrimonio",
                  "Transferir el riesgo es una decisión posible, no la gestión completa."),
                D("El análisis de amenazas del entorno realizado en la planificación estratégica",
                  "Ese análisis alimenta la gestión, pero no incluye valoración ni responsables."),
            ),
            explicacion_definicion=(
                "Anticipación, valoración y decisión con responsable: sin el responsable el "
                "registro no produce ninguna acción."
            ),
            escenario=(
                "La matriz de riesgos institucional lleva dos años sin actualizarse y en ese "
                "período cambió la normativa del sector. ¿Qué corresponde?"
            ),
            accion_correcta=(
                "Revisar la matriz a la luz del cambio normativo, revalorar los riesgos afectados "
                "y actualizar responsables"
            ),
            acciones_incorrectas=(
                D("Mantener la matriz vigente, porque los riesgos identificados siguen aplicando",
                  "Que sigan aplicando no significa que su valoración siga siendo la misma."),
                D("Elaborar una matriz nueva desde cero para incorporar el escenario actual",
                  "Partir de cero pierde la trazabilidad de cómo evolucionó cada riesgo."),
                D("Registrar el cambio normativo como un riesgo adicional en la matriz existente",
                  "Agregarlo como un ítem más ignora que altera la valoración de varios riesgos."),
            ),
            explicacion_escenario=(
                "Una matriz que no se revisa cuando cambia el contexto es un documento, no una "
                "gestión."
            ),
        ),
        Concepto(
            codigo="GESTION-10", nombre="La decisión basada en evidencia", nivel_minimo=3,
            microlearning=(
                "Decidir con evidencia es dejar rastro de qué información se tuvo a la vista, qué "
                "alternativas se compararon y por qué se eligió una. No significa que el dato "
                "decida solo: significa que la decisión pueda explicarse después. La señal más "
                "clara de madurez es cuando un acta registra que se descartó una alternativa "
                "atractiva porque los datos no la respaldaban."
            ),
            definicion=(
                "La práctica de fundar y registrar las decisiones en la información disponible, "
                "de modo que puedan explicarse y revisarse después"
            ),
            confusiones=(
                D("La disponibilidad de sistemas de información confiables para la gestión",
                  "Tener el dato disponible no implica que se use al decidir."),
                D("La aprobación de las decisiones por parte de instancias colegiadas",
                  "Que decida un colegiado no garantiza que la decisión esté fundada en datos."),
                D("La medición sistemática de los resultados de cada decisión adoptada",
                  "Medir después es evaluación; la evidencia debe estar antes de decidir."),
            ),
            explicacion_definicion=(
                "La clave es el registro: una decisión bien fundada pero sin rastro no se puede "
                "revisar ni defender."
            ),
            escenario=(
                "Se decide cerrar un programa. Al pedir el respaldo, aparece solo el acta con el "
                "acuerdo, sin los antecedentes. ¿Qué corresponde?"
            ),
            accion_correcta=(
                "Dejar registrados los antecedentes que se tuvieron a la vista y establecer que "
                "las actas los incorporen en adelante"
            ),
            acciones_incorrectas=(
                D("Considerar suficiente el acta, porque consigna formalmente el acuerdo adoptado",
                  "El acuerdo sin antecedentes no permite explicar por qué se decidió así."),
                D("Elaborar ahora un informe técnico que respalde la decisión ya tomada",
                  "Construir el respaldo después invierte el orden y se nota en las fechas."),
                D("Reabrir la decisión hasta contar con la totalidad de los antecedentes",
                  "Reabrir una decisión ejecutada por un problema de registro es desproporcionado."),
            ),
            explicacion_escenario=(
                "El problema no es la decisión sino la práctica de registro; corregirla hacia "
                "adelante es la respuesta proporcionada."
            ),
        ),
    ),
)
