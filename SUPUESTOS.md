# SUPUESTOS

> Todo lo inferido va acá, numerado. Origen: auditoría del Día 0 (S-01…S-30), Tanda 1 de
> Fase 0 (S-31…S-42) y los cimientos C1+C2 (S-43…S-44).
>
> **Estados:** `RATIFICADO` = nivel 2 aprobado en lote por el director · `VIGENTE` = nivel 1,
> decidido por el arquitecto · `SUPERADO` = reemplazado, se conserva para trazabilidad.

## Ruta, cargos y dimensiones

| # | Supuesto | Estado |
|---|---|---|
| S-01 | La ruta la determina el **cargo**. El diagnóstico solo fija dificultad y línea base; no cambia qué ruta toca. | RATIFICADO |
| S-02 | El diagnóstico se responde una vez, es obligatorio antes de abrir la ruta, y queda en solo lectura. | VIGENTE |
| S-09 | ~~La ruta del slice tiene 3 bloques genéricos.~~ | **SUPERADO por S-34** |
| S-29 | El mapa de ruta se dibuja desde datos para N nodos, no con el path SVG fijo de la cáscara. | VIGENTE |
| S-30 | Los cargos del slice usan la taxonomía estándar de IES chilena; el organigrama oficial de AIEP se cablea después. | RATIFICADO |
| S-31 | **La matriz Cargo × Dimensión** de [ADR-003](docs/decisiones/ADR-003-cargo-por-dimension.md): cada cargo toca las 5 dimensiones con nivel ≥ 1 y se diferencia por dónde se le exige profundidad. Vive en datos (30 filas de seed), no en código. | VIGENTE |
| S-34 | La ruta del slice son **5 bloques —uno por dimensión— más el nodo de graduación**. Reemplaza a S-09 y resuelve la inconsistencia de la cáscara, que dibujaba 7 nodos y decía 8 bloques. | VIGENTE |
| S-43 | **Anclaje de posiciones a hitos:** las 5 posiciones de toda ruta se anclan a H01, H04, H05, H07 y H08 — inicio, comités de sedes y escuelas, talleres con informantes, comité por dimensión y comité central. La ruta se ordena por exigencia descendente: primero la dimensión donde al cargo se le pide más. | VIGENTE |
| S-44 | Puertos por defecto **8010 / 5442 / 2567**, para convivir con `portal-inclusion` (que ocupa 8000 y 5432) y con el Postgres de pruebas (5433). | VIGENTE |
| S-38 | Cada bloque de ruta se **ancla a un hito** de la ruta oficial 2026–2027, para que el colaborador vea *por qué ahora* le toca esa dimensión y el dashboard compare avance contra calendario CNA. | VIGENTE |
| S-40 | Los 3 colaboradores del slice ocupan cargos con matrices bien distintas, para que la personalización se vea de inmediato: **Rector** (amplitud, sin ningún nivel 1), **Docente** (un solo nivel 3, el resto en 1) y **Coordinador de Calidad** (perfil de aseguramiento). | VIGENTE |

## Contenido

| # | Supuesto | Estado |
|---|---|---|
| S-06 | Sin evaluación adaptativa en el slice: banco fijo con ítems barajados por intento. La palabra sale de la UI. | VIGENTE |
| S-27 | `es_contenido_prueba: true` se muestra **visible en la UI** de todo bloque generado. | VIGENTE |
| S-32 | **Módulos por bloque según nivel:** N1 → 2, N2 → 3, N3 → 4. Conserva el default de 2 de CLAUDE.md §5 en el nivel base. Configurable en `modulos_por_nivel`. | VIGENTE |
| S-45 | **Base de conocimiento:** 10 conceptos por dimensión con `nivel_minimo`, de modo que N1 use 6, N2 use 8 y N3 los 10. De cada concepto salen 3 ítems, así los bancos quedan en 18 / 24 / 30 — por sobre el mínimo de 3× los ítems por intento. | VIGENTE |
| S-33 | La fuente declara **16 criterios** pero no los enumera ni indica su reparto entre dimensiones. `Criterio` se modela como entidad de primera clase y en el slice se genera como contenido de prueba. La lista oficial la inyecta el experto CNA de AIEP sin tocar el modelo. | VIGENTE |

## XP, niveles y medallas

| # | Supuesto | Estado |
|---|---|---|
| S-04 | **XP dual:** `acreditable` (módulos y evaluaciones aprobadas) y `ludico` (juegos). Nivel y completitud derivan solo del acreditable; el ranking usa el total. | RATIFICADO |
| S-05 | El XP lúdico tiene tope diario **por juego** (por `origen_id`), default **400 XP/día**, y se registra como evento igual que el resto. Se subió de 200 porque una partida perfecta del quiz más largo vale 330 y truncarla castiga a quien lo hace bien; el freno al farmeo no es este número sino que cada quiz paga una vez al día y que el XP lúdico nunca mueve el escalón. | VIGENTE |
| S-10 | Se conservan los umbrales de la cáscara: 0 / 1.000 / 2.500 / 4.500 / 7.000 / 10.000 XP. | VIGENTE |
| S-11 | Agotar los 3 reintentos deja el bloque en `requiere_acompanamiento`. **Nunca otorga la medalla.** | RATIFICADO |
| S-22 | Open Badges v2.0 con URL de verificación pública. En el slice, adapter local con el contrato del real. | VIGENTE |
| S-37 | **XP por nivel de estándar:** módulo 60 / 80 / 100 y medalla de bloque 200 / 300 / 400, para N1 / N2 / N3. Con esto los cargos terminan el slice en escalones distintos —un Docente alcanza *Colaborador*, un Rector alcanza *Facilitador*—, que es exactamente la diferenciación que el slice debe demostrar. | VIGENTE |
| S-39 | La medalla `master` (graduación) se otorga al **completar los 5 bloques**, no por alcanzar un umbral de XP: con el tamaño del slice, 10.000 XP es inalcanzable y la graduación quedaría muerta. | VIGENTE |

## Evaluación

| # | Supuesto | Estado |
|---|---|---|
| S-07 | La pantalla de quiz se parte en dos: **quiz formativo** (feedback inmediato, no otorga nada) y **evaluación final** (resultado al final, gate 80%). | RATIFICADO |
| S-46 | Los ítems del quiz formativo viven en **tabla propia**, no en `item_evaluacion`: el quiz entrega la respuesta correcta al cliente y el banco de la evaluación no lo hace jamás. Separarlos vuelve imposible filtrar el banco por descuido. | VIGENTE |
| S-47 | El quiz formativo **paga una vez al día por módulo** y su puntaje lo **recalcula el servidor** desde las respuestas. Si el cliente propusiera su XP, el tope y la racha serían decorativos. | VIGENTE |
| S-08 | La actividad colaborativa del bloque es **opcional**: da XP lúdico y no bloquea completitud ni medalla. | RATIFICADO |
| S-12 | El intento abierto expira a las 24 h: se cierra como no aprobado, consume reintento y no otorga nada. | VIGENTE |
| S-13 | Envío **idempotente por `intento_id`**: el segundo envío devuelve el resultado del primero y nunca crea un segundo evento de XP. | VIGENTE |
| S-14 | El autosave por respuesta deja todo en servidor; "enviar" solo cierra el intento. | VIGENTE |

## Ranking y organización

| # | Supuesto | Estado |
|---|---|---|
| S-15 | Empates: XP acreditable, luego fecha más antigua del último evento acreditable, luego alfabético. Posiciones empatadas comparten número. | VIGENTE |
| S-16 | El ranking muestra nombre, unidad, XP total y **conteo** de insignias por tipo. Nunca el nombre de insignias de otro cargo. | RATIFICADO |
| S-17 | Ranking acumulado por default, más filtro "este bloque" calculado sobre eventos. No se borra nada. | VIGENTE |
| S-20 | `Unidad` y `Comite` salen de la **gobernanza real** de la fuente (sedes, escuelas, dirección nacional, comités), no de una estructura inventada. | VIGENTE |

## Identidad, permisos y dashboard

| # | Supuesto | Estado |
|---|---|---|
| S-18 | SSO de Entra más login dev "actuar como", solo dev. **Se elimina el formulario de correo y contraseña.** | RATIFICADO |
| S-19 | El switcher Colaborador/Rectoría deja de ser un toggle de UI y pasa a ser permiso. | RATIFICADO |
| S-21 | Métricas derivables en el slice: activos, avance, aprobación, insignias, rezagados, críticos, interacciones. La "Satisfacción 4,6/5" **se oculta: no se inventa el número.** | RATIFICADO |
| S-23 | Correo y calendario van por adapters mockeados que **registran el intento**, no fallan en silencio. | VIGENTE |
| S-24 | El chat de la Plaza se persiste con autor y timestamp, con rate limit, 80 caracteres, filtro básico y reporte. Sin mensajes privados. | VIGENTE |
| S-35 | **El permiso institucional deriva de la membresía de comité**, no del cargo: lo tiene quien pertenece al Comité de Aseguramiento de la Calidad, al Comité Central o a la Dirección Nacional. Refina S-19 con la gobernanza real. | VIGENTE |
| S-36 | E-03 aplicado: ranking con nombres, **rezagados agregados por unidad**, y detalle nominal detrás de permiso con registro en `acceso_dato_personal` (Ley 21.719). | RATIFICADO |

## Plaza y frontend

| # | Supuesto | Estado |
|---|---|---|
| S-25 | Se **evoluciona** la cáscara a React + TypeScript sin reescribir la identidad visual. | RATIFICADO |
| S-26 | Tipografías y librería de gráficos se autohospedan. | VIGENTE |
| S-28 | Se agrega botón de menú móvil. Bloqueante: el gate de la Plaza se prueba con teléfonos. | VIGENTE |
| S-03 | ~~La "sala 3D" del brief es el canvas 2D isométrico de la cáscara.~~ Respondido por el director en E-01: la meta es 3D, condicionada al spike. | **SUPERADO por S-41** |
| S-41 | **El render de la Plaza se decide después del gate A4**, no antes. El servidor es agnóstico del render ([ADR-004](docs/decisiones/ADR-004-realtime-agnostico-de-render.md)): 2D y 3D consumen el mismo estado, así que E-01 sale del camino crítico. | VIGENTE |
| S-42 | La actividad social de la Plaza es una **trivia grupal contra reloj que reusa el motor de juegos de la cáscara**, no un motor nuevo. Su XP es lúdico y con tope. | RATIFICADO |
