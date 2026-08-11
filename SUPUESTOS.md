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
| S-32 | ~~**Módulos por bloque según nivel:** N1 → 2, N2 → 3, N3 → 4.~~ AIEP fijó una estructura idéntica en las cinco dimensiones: **2 módulos + 1 juego + evaluación**. La profundidad dejó de expresarse en cuántos módulos hay y pasó a cuánto trae cada uno (S-50). | **SUPERADO por S-50** |
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
| S-48 | **Corte %→nivel de exigencia CNA:** ≥25% → 3, 15–24% → 2, ≤10% → 1. Es una **derivación del arquitecto**, no un dato del Excel: la fuente entrega el % y la marca de ruta crítica, pero no el nivel. Con estos cortes las 2 críticas de cada rol caen siempre en nivel 3. Parametrizado en `CORTES_NIVEL`; cambiarlo no toca nada más del sistema. | **A CONFIRMAR CON AIEP** |
| S-49 | **Los docentes de aula van en N2 Liderazgo intermedio.** Ninguno de los tres roles nombra la docencia, pero Docencia es crítica en N2 y N3. Provisional hasta que AIEP lo diga; Pablo, el colaborador de prueba, queda ahí. | **A CONFIRMAR CON AIEP** |
| S-50 | **Estructura escalonada:** todas las dimensiones llevan 2 módulos con quiz + 1 juego + evaluación. La **crítica suma** un desafío aplicado, sube el umbral a 85% y otorga medalla gold. La profundidad escala con el nivel: quices de 3/5/7 ítems y evaluaciones de 4/6/8. | VIGENTE |
| S-51 | **La criticidad no se transcribe, se deriva:** son las 2 dimensiones de mayor % de cada rol. Coinciden exactamente con las 🔴 del Excel en los tres roles, y hay un test que lo contrasta. | VIGENTE |
| S-52 | **El desafío aplicado es requisito, no gate.** Hay que resolverlo para abrir la evaluación reforzada, pero equivocarse no bloquea: paga menos XP lúdico y nada más. Un requisito que se puede reprobar sin consecuencia sería teatro; uno que bloquea sería un segundo umbral escondido. | VIGENTE |
| S-53 | **XP de la medalla gold = 1,5× la silver** (300/450/600 por nivel). Exige más —desafío + 85%—, así que rinde más. | VIGENTE |
| S-54 | **El umbral de anonimato del panel es 5 y vive en la base**, no en la pantalla: las vistas `panel_por_*` pliegan los grupos menores en una fila «reservada». Ponerlo en el frontend dejaría la puerta abierta a que una consulta nueva lo olvide. Se cambia en `fn_umbral_anonimato()`. | VIGENTE |
| S-55 | **Los grupos pequeños se pliegan, no se borran.** El total institucional sigue cuadrando. Si ni plegados llegan al umbral, la fila desaparece y el panel declara la diferencia — sacar gente del denominador es la otra forma de mentir con privacidad. | VIGENTE |
| S-56 | **Población sintética de prueba** (`POBLACION_DE_PRUEBA`, default 120) para que el panel tenga volumen. Sus medallas nacen de intentos aprobados reales, así que sembrarla también prueba el invariante a escala. No aparece en el login «actuar como». | VIGENTE |
| S-57 | **El ranking se sirve acotado** a la cabeza de la tabla (`CABEZA_DEL_RANKING`, default 50). Con 85.000 personas devolverlas todas no es una respuesta usable. | VIGENTE |
| S-58 | **No existe ranking global individual completo ni lista de los últimos.** Se sirve la cabeza y tu propia posición. Ver el puesto 47.000 de 85.000 no es información accionable, y publicar la cola solo sirve para señalar; el rezago se acompaña agregado por unidad (E-03). | VIGENTE |
| S-59 | **No hay ranking competitivo entre roles.** N1, N2 y N3 recorren rutas con distinta exigencia y distinto peso por dimensión: rankearlos compara lo que se les pide, no lo que hacen. La comparación por rol existe en el panel como diagnóstico, no como tabla de posiciones. | VIGENTE |
| S-60 | **El ranking nominal dentro de la unidad solo existe si la unidad pasa el umbral**, y aun así va acotado a los 10 primeros: en un grupo chico, servir la tabla entera equivale a publicar quiénes van últimos entre sus pares. | VIGENTE |
| S-61 | **El ranking institucional no nombra la unidad de un grupo bajo el umbral.** La persona sigue en la tabla; lo que se reserva es la etiqueta que la vuelve ubicable dentro de un grupo diminuto. | VIGENTE |
