# Glosario

> Terminología única del proyecto. La compuerta de cierre de Fase 0 verifica que specs,
> código, UI y base de datos usen **estas mismas palabras**. Si un término no está acá,
> no se usa en el código.
>
> Origen: `docs-fuente/` (marcado **[fuente]**) o decisión del proyecto (marcado **[proy]**).

## Dominio CNA

| Término | Significado | Identificador en código |
|---|---|---|
| **Acreditación institucional** [fuente] | Proceso que provee garantía pública de calidad institucional. Su pronunciamiento puede ser de excelencia (6–7 años), avanzada (4–5) o básica (3). | — |
| **Autoevaluación** [fuente] | Examen crítico, analítico y sistemático del cumplimiento de criterios y estándares por dimensión, sustentado en información válida, confiable y verificable. | — |
| **Evaluación externa** [fuente] | Proceso que evalúa el grado de cumplimiento por dimensión y verifica la validez del informe de autoevaluación. | — |
| **Dimensión** [fuente] | Área clave de desarrollo de la institución. Son 5. Es el esqueleto del contenido. | `Dimension` |
| **Criterio** [fuente] | Principio general derivado de una dimensión. Son 16 en total; el reparto oficial no está en la fuente. | `Criterio` |
| **Estándar** [fuente] | Indicador de desempeño en niveles progresivos y anidados: el 3 incluye al 2 y el 2 al 1. | `nivel_estandar` (1–3) |
| **Hito** [fuente] | Cada uno de los 13 momentos de la ruta 2026–2027. | `Hito` |
| **MAC** [fuente] | Mecanismos de Aseguramiento de la Calidad. Objeto de análisis en los talleres de sede y escuela. | — |
| **Juicio evaluativo** [fuente] | Valoración fundada que elaboran los comités y que sustenta fortalezas, debilidades y oportunidades. | — |
| **Muestra Intencionada** [fuente] | Informe que se entrega a la CNA en H11. | — |
| **Pares evaluadores** [fuente] | Quienes realizan la visita de evaluación externa (H13). | — |
| **Plan de Mejora Institucional** [fuente] | Producto del Comité Central junto al informe de autoevaluación. | — |

## Estructura institucional

| Término | Significado | Identificador |
|---|---|---|
| **Colaborador** [fuente] | Persona de AIEP que recorre una ruta. Es el usuario del sistema. **Nunca "usuario" en la UI.** | `Colaborador` |
| **Cargo** [proy] | Puesto institucional del colaborador. Determina su ruta. Son 6 en el slice. **Nunca "rol"** — "rol" queda reservado para permisos técnicos. | `Cargo` |
| **Unidad** [fuente] | Sede, escuela o dirección nacional. | `Unidad` |
| **Comité** [fuente] | Instancia de gobernanza del proceso. Determina permisos institucionales. | `Comite` |

## Máquina de gamificación

| Término | Significado | Identificador |
|---|---|---|
| **Ruta** [proy] | Recorrido completo de un colaborador: sus 5 bloques, uno por dimensión, cada uno al nivel de estándar que le exige su cargo. | `Ruta` |
| **Bloque** [proy] | Una dimensión a un nivel de estándar, dentro de la ruta de alguien. Contiene módulos, una evaluación y una medalla. | `BloqueRuta` |
| **Bloque de contenido** [proy] | El contenido generado una vez para un par (dimensión, nivel). Lo comparten todos los cargos que exigen ese par. | `BloqueContenido` |
| **Módulo** [proy] | Pieza de microlearning con su quiz formativo. | `Modulo` |
| **Quiz formativo** [proy] | Ejercicio dentro del módulo. Feedback inmediato. **No otorga nada.** | `QuizFormativo` |
| **Evaluación** [proy] | Prueba final del bloque. Resultado al final, umbral 80%. Es la que respalda la completitud. | `Evaluacion` |
| **Intento** [proy] | Una ejecución de una evaluación por un colaborador. Es el respaldo auditable de toda medalla. | `IntentoEvaluacion` |
| **Ítem** [proy] | Pregunta del banco, con alternativas, correcta y explicación por alternativa. | `ItemEvaluacion` |
| **Evento de gamificación** [proy] | Registro append-only del que se deriva todo el estado. Nada de XP, nivel o ranking se guarda a mano. | `EventoGamificacion` |
| **XP acreditable** [proy] | XP proveniente de módulos y evaluaciones aprobadas. **Solo este determina nivel y completitud.** | `clase_xp='acreditable'` |
| **XP lúdico** [proy] | XP proveniente de juegos. Cuenta para el ranking, nunca para el nivel ni la completitud. | `clase_xp='ludico'` |
| **Nivel** [proy] | Escalón del colaborador. **Siempre derivado** del XP acreditable, jamás un campo editable. | derivado |
| **Insignia** [proy] | Medalla otorgada. Solo existe si existe su intento aprobado. | `Insignia` |
| **Canario** [proy] | Caso de prueba congelado: un intento deliberadamente reprobado que jamás debe producir insignia. Si la produce, el build se bloquea. | — |

## Escalera de niveles

Se conserva la de la cáscara (S-10). **Nunca se numeran "Nivel 1..6" en la UI** — se usa el
nombre, porque "nivel" ya significa `nivel_estandar` en el dominio CNA.

`Explorador` → `Colaborador` → `Facilitador` → `Embajador` → `Líder de Calidad` → `Maestro de Acreditación`

## Tipos de insignia

`mini` (por módulo) · `silver` (por bloque) · `gold` (hito de ruta) · `master` (graduación)

## Palabras prohibidas

| No usar | Usar | Por qué |
|---|---|---|
| "usuario" en UI | colaborador | Es el término institucional de la fuente |
| "rol" para el puesto | cargo | "rol" se reserva para permisos |
| "curso", "lección" | bloque, módulo | Coherencia con el modelo |
| "adaptativa" | — | No se implementa (S-06) |
| "escape room" | actividad de la Plaza | Fuera de alcance (E-02) |
| "nivel 1/2/3" para la escalera | nombre del escalón | Colisiona con `nivel_estandar` |
