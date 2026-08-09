# Dominio real — Ruta de autoevaluación y acreditación AIEP

> **Fuente primaria del dominio.** Extraído de `docs-fuente/2026-01 Ruta autoevaluación-acreditación [Calidad].pptx`
> (Dirección Nacional de Aseguramiento de la Calidad, enero 2026) y de
> `docs-fuente/Ruta Acreditación 2026-2027 ene2026 v3 2.jpg.jpeg`.
>
> Este documento manda sobre cualquier resumen. Todo lo que está acá **viene de esos dos
> archivos**: no hay nada inferido de internet ni contenido normativo inventado. Lo que
> el sistema genera por encima de esta estructura va marcado `es_contenido_prueba: true`.

---

## 1. Las 5 dimensiones evaluativas

Modelo de evaluación integral vigente desde **octubre de 2023**, definido por la
**Ley 20.129** (Sistema Nacional de Aseguramiento de la Calidad en Educación Superior).
Nombres oficiales tal como aparecen en la fuente:

| # | Código | Dimensión (nombre oficial) | Carácter |
|---|---|---|---|
| 1 | `GESTION` | Gestión Estratégica y Recursos Institucionales | Obligatoria |
| 2 | `DOCENCIA` | Docencia y Resultados del Proceso de Formación | Obligatoria |
| 3 | `CALIDAD` | Aseguramiento Interno de la Calidad | Obligatoria |
| 4 | `VCM` | Vinculación con el Medio | Obligatoria |
| 5 | `ICI` | Investigación, Creación y/o Innovación | Voluntaria, pero **necesaria para obtener el período máximo de vigencia** |

**Estas 5 dimensiones son el esqueleto del contenido del sistema.** El contenido se genera
una vez por dimensión (§4), no por cargo.

### Antecedente: de áreas a dimensiones

La fuente documenta la transición del modelo anterior al vigente. Se conserva porque
aparece en el material que verán los colaboradores:

| Modelo anterior — Áreas de evaluación | Modelo vigente — Dimensiones evaluativas |
|---|---|
| Gestión institucional* | Gestión Estratégica y Recursos Institucionales* |
| Docencia de pregrado* | Docencia y Resultados del Proceso de Formación* |
| Docencia de postgrado | Aseguramiento Interno de la Calidad* |
| Vinculación con el medio | Vinculación con el Medio* |
| Investigación | Investigación, Creación y/o Innovación** |

---

## 2. Dimensiones, criterios y estándares — la jerarquía que estructura todo

Definiciones textuales de la fuente:

- **Dimensiones** — áreas clave de desarrollo de las IES, alineadas con su misión y
  funciones según la **Ley 21.091**. Son **5**.
- **Criterios** — derivan de las dimensiones y representan principios generales para el
  aseguramiento de la calidad, orientados a la mejora continua y la excelencia. Son **16**
  en total.
- **Estándares** — indicadores más específicos que establecen **niveles progresivos de
  desempeño, organizados jerárquicamente: el nivel 3 incluye al 2, y el 2 al 1**,
  reflejando avances en ciclos de mejora continua.

> ### Por qué esto es la pieza arquitectónica más importante del proyecto
>
> El modelo real de la CNA **ya trae una escala de profundidad progresiva y anidada de
> tres niveles**. No necesitamos inventar cómo diferenciar la exigencia de un Rector de la
> de un Docente sobre la misma dimensión: la usamos. Un bloque de nivel 3 contiene
> literalmente el contenido del nivel 2, y ese el del nivel 1.
>
> De ahí sale el modelo Cargo × Dimensión de [ADR-003](decisiones/ADR-003-cargo-por-dimension.md).

**Hueco conocido y honesto:** la fuente declara que son **16 criterios** pero **no los
enumera ni indica cómo se reparten** entre las 5 dimensiones. El sistema modela `Criterio`
como entidad de primera clase con su código, y para el slice los criterios se generan como
contenido de prueba. La lista oficial la inyecta el experto CNA de AIEP en producción,
sin tocar el modelo.

---

## 3. Las dos rutas y sus 13 hitos

La infografía institucional (*"Nuestra ruta para avanzar · Con la fuerza de todos"*)
define **dos rutas encadenadas**. Estos hitos son la **secuencia temporal real** del
sistema: anclan cada bloque a un momento del proceso y alimentan el "¿vamos en calendario?"
del dashboard.

### Ruta de la autoevaluación · 2026

| # | Período | Hito |
|---|---|---|
| H01 | Enero | Inicio del proceso de Autoevaluación Institucional |
| H02 | Marzo | Aplicación de encuestas de opinión a **titulados, empleadores y colaboradores** |
| H03 | Abril | Aplicación de encuestas de opinión a **estudiantes y docentes** |
| H04 | Abril–Mayo | Constitución y ejecución de talleres de autoevaluación en **Comités de Sedes y Escuelas** |
| H05 | Mayo | Ejecución de talleres con **informantes clave en sedes** (estudiantes, docentes, titulados, empleadores) |
| H06 | Junio–Julio | Elaboración de **informes de análisis y síntesis** de resultados de comités de sedes y escuelas y de los talleres con informantes clave |
| H07 | Agosto–Septiembre | Constitución y ejecución de talleres de autoevaluación en **Comités por Dimensión de Evaluación** |
| H08 | Septiembre–Noviembre | Talleres de **juicios evaluativos, fortalezas y debilidades y plan de mejora** en Comité Central de Autoevaluación |
| H09 | Diciembre | Entrega de la **primera versión del Informe de Autoevaluación Institucional** |

### Ruta de la acreditación · 2027

| # | Período | Hito |
|---|---|---|
| H10 | Enero–Febrero | Ajustes, edición y diseño final del Informe de Autoevaluación Institucional |
| H11 | Marzo–Mayo | Inicio del proceso de Acreditación ante **CNA-Chile** · inicio de socialización · entrega del **Informe de Muestra Intencionada** |
| H12 | Desde Mayo | Actividades de socialización de los resultados, hasta la visita de evaluación externa |
| H13 | Por definir | **Visita de pares evaluadores** |

**Dato de contexto que fija la urgencia:** la acreditación vigente de AIEP es de
**5 años, nivel avanzado** (Gestión institucional, Docencia de pregrado y Vinculación con
el medio), **hasta octubre de 2027**. La visita de pares de H13 es la que renueva eso.

---

## 4. Gobernanza — los comités

La fuente define una cadena de instancias con responsabilidades distintas. **Esto reemplaza
la estructura organizacional que yo había inventado en la auditoría** (`Unidad`/`Sede`
genéricas): existe una jerarquía real y es la que se modela.

| Instancia | Qué hace (textual de la fuente) |
|---|---|
| **Junta Directiva** | Aprueba |
| **Comité de Aseguramiento de la Calidad** | Evalúa y valida |
| **Comité Central de Autoevaluación** | Integra la evaluación por dimensiones · elabora fortalezas, debilidades y oportunidades de mejora · propone el plan de mejora institucional |
| **Comité de Autoevaluación por Dimensiones** | Realiza la autoevaluación por dimensión · propone juicios evaluativos · elabora propuesta de fortalezas, debilidades y oportunidades |
| **Comité de Sedes** y **Comité de Escuelas** | Realizan la autoevaluación en sede y escuelas mediante análisis de indicadores institucionales, mecanismos de aseguramiento de la calidad, y fortalezas, debilidades y oportunidades de mejora |
| **Dirección Nacional de Aseguramiento de la Calidad** | Conduce el proceso |

**Consecuencias directas en el sistema:**

1. `Unidad` tiene tipo real: `sede`, `escuela`, `direccion_nacional`.
2. `Comite` es entidad propia, con tipo y —cuando corresponde— la dimensión que le toca.
3. **El permiso del dashboard sale de acá, no de un cargo:** lo ve quien pertenece al
   Comité de Aseguramiento de la Calidad, al Comité Central o a la Dirección Nacional.
   Eso resuelve S-19 con estructura real en vez de un rol inventado.
4. El ranking filtra por `Unidad`, que ahora significa algo.

---

## 5. Cómo es el proceso de autoevaluación

Textual de la fuente — es participativo, analítico y crítico. Considera:

- **Levantamiento de información:** encuestas · grupos focales y conversatorios · talleres
  en sede y escuela (análisis de MAC, indicadores, fortalezas y debilidades).
- **Elaboración de juicios evaluativos**, que fundamentan fortalezas, debilidades y
  oportunidades de mejora.
- **Productos finales:** Informe de Autoevaluación Institucional y Plan de Mejora
  Institucional.

### Etapas del proceso de acreditación institucional

1. **Autoevaluación** — examen crítico, analítico y sistemático del cumplimiento de los
   criterios y estándares por dimensión, considerando la misión y el proyecto de
   desarrollo institucional. Debe sustentarse en información **válida, confiable y
   verificable**.
2. **Evaluación externa** — evalúa, por dimensión, el grado de cumplimiento de criterios y
   estándares, y **verifica la validez del informe de autoevaluación**.
3. **Pronunciamiento de acreditación** — puede ser de **excelencia** (6 o 7 años),
   **avanzada** (4 o 5 años) o **básica** (3 años).

> "Información válida, confiable y verificable" es, textualmente, el estándar que la CNA
> le exige a la evidencia. Es la misma exigencia que el invariante de integridad de
> completitud le impone a este sistema: cuando el portal dice "cumplió", eso tiene que ser
> verificable. Ver [ADR-005](decisiones/ADR-005-integridad-de-completitud.md).

---

## 6. Qué NO está en la fuente

Registrado explícitamente para que nadie lo dé por resuelto:

- La **lista de los 16 criterios** y su reparto entre dimensiones.
- Los **estándares concretos** de cada nivel 1 / 2 / 3.
- El **organigrama oficial de AIEP** con cargos y dotación. Para el slice se usa la
  taxonomía estándar de IES chilena (S-30); el organigrama real se cablea después.
- La **composición nominal** de cada comité.
- Cualquier **contenido formativo** propiamente tal.

Todo lo anterior lo aporta AIEP en producción. El sistema deja el enchufe puesto y el
resto va como contenido de prueba.
