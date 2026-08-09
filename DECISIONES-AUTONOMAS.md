# DECISIONES AUTÓNOMAS

> Nivel 1 del protocolo de CLAUDE.md §2: duda con default razonable y barata de revertir.
> Una línea por decisión: qué · default · por qué · cómo se revierte.
> Ninguna de estas detuvo el trabajo.

## Tanda 1 — Fase 0

- **Intérprete de Python** · dentro del contenedor, no el local · el sistema del director es 3.9 y la API pide 3.12 · se cambia la imagen base en el Dockerfile.
- **Motor de base de datos en los tests** · PostgreSQL real vía testcontainers, no SQLite · los CHECK, triggers e índices de ADR-005 no existen en SQLite y probar contra otro motor daría una garantía falsa · se cambia el fixture de pytest.
- **UUID como identificador** · en todas las tablas · evita colisiones al sembrar contenido generado en paralelo por worktrees distintos · migración de tipo de columna.
- **Marcas de tiempo** · `timestamptz` siempre en UTC · el proceso CNA cruza husos y el informe debe ser auditable · conversión en la capa de presentación.
- **Nombre del par generado** · "bloque de contenido" para el par (dimensión, nivel) y "bloque de ruta" para su instancia en la ruta de alguien · sin dos nombres, el modelo se vuelve ambiguo al hablar · renombrar en glosario y código.
- **Cantidad mínima del banco de ítems** · 3 × ítems por intento · con menos, barajar no produce pruebas distintas entre reintentos · constante en las reglas del validador.
- **Reglas anti-degeneración del banco** · similitud máxima 0,9 entre enunciados, sin sesgo de largo en la correcta, y posición de la correcta repartida · un generador de lenguaje tiende a producir bancos donde la respuesta se adivina sin saber la materia · se ajustan los umbrales en `REGLAS-VALIDADOR.md`.
- **`fecha_inicio` y `fecha_fin` del hito son nullable** · H13 (visita de pares) está "por definir" en la fuente · el sistema no inventa la fecha · se completan cuando AIEP la fije.
- **Explicación por alternativa, también en las incorrectas** · el quiz formativo las muestra al fallar · sin ellas el feedback no enseña · campo del schema.
- **Prohibida la palabra "usuario" en la UI** · se usa "colaborador", que es el término de la fuente institucional · glosario.
- **"Cargo" y no "rol"** · "rol" queda reservado para permisos técnicos · glosario y modelo.
- **La escalera de niveles no se numera en la UI** · se usa el nombre del escalón · "nivel" ya significa `nivel_estandar` en el dominio CNA y numerar ambos confunde · regla de diseño.
- **`--menta` solo para logro verificado** · nunca para "en camino" · la UI no puede sugerir una completitud que no existe · regla del sistema de diseño.
- **La API y el realtime se hablan con token firmado por la API** · la sala sabe quién entra sin duplicar la lógica de identidad · se cambia el emisor del token.
- **El seed es parte del arranque, no un script aparte** · si el seed se rompe, el sistema no levanta, y eso es lo correcto · se saca del entrypoint.
- **Punto de quiebre responsive en 1080 px** · el que ya usa la cáscara · variable CSS.
- **Se descarta portar el polyfill roto de `roundRect` y la comparación por `textContent` de la trivia** · ambos son defectos de la cáscara, no comportamiento a preservar · —.
