# DUDAS — preguntas para AIEP

No es una cola de decisiones: nada de acá detiene el trabajo (CLAUDE.md §2). Son
las preguntas que solo puede responder el cliente real, y que se levantan cuando
haya interlocución con AIEP. Todo lo que está en duda tiene un default funcionando.

---

## Modelo de roles

| # | Pregunta | Default en funcionamiento |
|---|---|---|
| S-48 | ¿Tiene AIEP su propia tabla de nivel de exigencia CNA por rol y dimensión? El Excel entrega el % y la marca de ruta crítica, pero no el nivel. | Derivación del arquitecto: ≥25% → 3, 15–24% → 2, ≤10% → 1. Está parametrizada en `CORTES_NIVEL`; cambiarla no toca nada más. |
| S-49 | ¿En qué rol caen los **docentes de aula**? Ninguno de los tres los nombra, pero Docencia es crítica en N2 y N3. | Provisional en N2, donde Docencia pesa 35%. El colaborador de prueba lo dice en su propio nombre. |

---

## Contenido real de los juegos por dimensión

Toda la fase 2 es **cáscara funcional**: el contenido es de prueba, plausible y
marcado `es_contenido_prueba`, y existe para que la mecánica se pueda probar. En
la fase de contenido real, AIEP reemplaza el relleno sin que cambie el motor.

Dos dimensiones necesitan **más material propio de la institución** que las otras,
porque su juego no se puede construir sobre conceptos genéricos:

| Dimensión | Qué aporta hoy la cáscara | Qué tendría que entregar AIEP |
|---|---|---|
| **D4 Vinculación con el Medio** | Un catálogo de actores externos inventado (empresas, municipios, colegios profesionales, egresados) con la acción institucional que les corresponde. | **Los convenios y contrapartes reales**: con quién tiene relación la institución, de qué tipo, y qué actividad se registra con cada uno. Sin esto el juego funciona pero enseña vínculos que no existen. |
| **D5 Investigación, Creación e Innovación** | Líneas de investigación e innovación de ejemplo, y criterios de qué cuenta como producción institucional. | **Las líneas declaradas de AIEP** y su criterio de adscripción institucional: cómo se reconoce que una publicación, proyecto o innovación es de la institución. Es la dimensión con menos material derivable de otras fuentes. |

Las otras tres se sostienen mejor con contenido de prueba: D1 y D2 se apoyan en
cifras sintéticas que no afirman nada sobre AIEP, y D3 usa los 13 hitos reales,
que ya están en la fuente.
