# Auditoría del Día 0 — Somos Calidad (AIEP)

> Entregable del arquitecto según CLAUDE.md §12. **Pendiente de aprobación del director.**
> Nada se construye ni se especifica hasta que esta auditoría esté aprobada.
>
> Fuentes leídas: `somos-calidad_1 (1).html` (1.276 líneas, completo) · `docs-fuente/BRIEF-DOMINIO.md` (completo) · `CLAUDE.md` · `tareas.md` · `LEEME-SETUP.md`

---

## 0. Hallazgos de partida (antes de la tabla)

Cuatro cosas del estado del repo que afectan la auditoría misma:

1. **La propuesta comercial de AIEP no está.** `docs-fuente/` contiene solo `BRIEF-DOMINIO.md` y un `.Rhistory` vacío. CLAUDE.md §0 dice "el documento fuente manda sobre cualquier resumen" — y ese documento no está en el repo. Audité contra el brief + la cáscara. Los tres escalamientos del final existen precisamente porque no puedo verificar qué se le prometió al cliente.
2. **El mockup no está en `referencia-demo/`** (esa carpeta está vacía). Está en la raíz como `somos-calidad_1 (1).html`. Propongo moverlo y renombrarlo a `referencia-demo/somos-calidad.html` al aprobar.
3. **Todavía no es un repo git.** El paso 2 del `LEEME-SETUP.md` está pendiente. Sin repo no hay "commit tras cada bloque aprobado" (§14).
4. **La cáscara tiene 10 pantallas, no 9.** CLAUDE.md §0 dice 9 pero enumera 10: `ingreso, diagnostico, ruta, bloque, quiz, juegos, insignias, ranking, plaza, dashboard`. Corrijo el conteo en la doc.

---

## 1. La tabla — qué tenemos / qué falta / qué queda ambiguo

Leyenda de la tercera columna: cada ambigüedad se convierte en un **supuesto numerado S-xx** (§2 de este documento) o en un **escalamiento E-xx** (§5).

### Área 1 · Ingreso e identidad

| (a) Qué tenemos en la cáscara | (b) Qué falta construir de verdad | (c) Ambigüedad |
|---|---|---|
| Pantalla de login completa: hero institucional partido (1.600 colaboradores / 8 bloques / 5 rutas), tarjeta con botón "Continuar con Microsoft 365", campos de correo y contraseña prellenados, estados de foco. Es la promesa visual del SSO. | Todo lo que va detrás. Adapter de identidad conmutable (login dev "actuar como" ↔ Entra ID por OIDC), sesión, expiración, logout, mapeo del claim de Entra al rol institucional, y perfil persistido. Hoy el botón ejecuta `go('diagnostico')`: no autentica absolutamente nada. | ¿De dónde sale el **rol** de cada persona — de un claim de Entra, de un CSV que aporta AIEP, o se asigna a mano? El brief no lo dice y determina todo el arranque. → **S-18, S-30**. Además el hero dice "5 rutas por rol" y el brief define 6 roles. |

### Área 2 · Diagnóstico

| (a) Qué tenemos | (b) Qué falta | (c) Ambigüedad |
|---|---|---|
| Tres preguntas de selección única con barra de progreso de 3 pasos, y una pantalla de "perfil generado" con 4 atributos (nivel institucional, rol, conocimiento inicial, impacto CNA) y dos rutas sugeridas. | El banco real de preguntas, la persistencia de las respuestas, y la lógica que convierte respuestas → perfil. Hoy `showPerfil()` solo esconde un `div` y muestra otro; el perfil está escrito a mano en el HTML. El botón "Atrás" no hace nada. | **Contradicción de fondo:** la cáscara sugiere que el diagnóstico **asigna** la ruta ("Ruta sugerida: Académica + Liderazgo"), pero CLAUDE.md §3 dice que la ruta la determina el **rol**. ¿Y se puede repetir? ¿es obligatorio para entrar? → **S-01, S-02**. |

### Área 3 · Mi Ruta (la pantalla firma)

| (a) Qué tenemos | (b) Qué falta | (c) Ambigüedad |
|---|---|---|
| El mapa serpenteante con 8 nodos, estados `done`/`now`/`lock`, línea de progreso en degradado menta→oro, escalera de 6 niveles, y tres tarjetas de resumen. Es la mejor pieza del mockup. | Generar el mapa **desde datos**: hoy el path SVG y cada posición (`left:8%;top:81%`) están escritos a mano para exactamente 8 nodos. Falta la regla de desbloqueo (qué abre el bloque N+1), el % de avance calculado, el estado "en curso · 60%" derivado, y que la ruta sea distinta por rol. | Las cifras no cuadran entre sí: el mapa dibuja 7 bloques + graduación pero el texto dice 8; "44% · 3,5 de 8 bloques" contra un bloque 4 al 60% (=3,6/8=45%); "7/20 insignias" con un catálogo de 12. ¿Los 8 bloques / 8 meses son compromiso contractual o configuración? → **S-09, S-29**. |

### Área 4 · Bloque

| (a) Qué tenemos | (b) Qué falta | (c) Ambigüedad |
|---|---|---|
| La estructura del bloque: 2 módulos + evaluación final + actividad colaborativa, con iconos de estado, y la tarjeta de recompensa (medalla silver, XP del bloque, progreso, ranking en la unidad). Coincide con §5 del brief. | **El contenido de los módulos: no existe ninguna pantalla de módulo ni de lección.** La cáscara promete "Microlearning · 12 min · quiz interactivo" y no hay dónde verlo. Es el hueco más grande del mockup. Falta el visor de la pieza, la marca de "visto", el quiz formativo dentro del módulo, y el desbloqueo secuencial real. | ¿La "Actividad colaborativa" es requisito para cerrar el bloque? Si lo es y se corta el escape room (CLAUDE.md §8), el bloque queda incompletable. → **S-08, E-02**. Y "190/380 XP" (50%) contra "progreso del bloque 60%": ¿el progreso se mide por XP o por ítems completados? |

### Área 5 · Quiz y evaluación

| (a) Qué tenemos | (b) Qué falta | (c) Ambigüedad |
|---|---|---|
| Una pantalla de pregunta con 4 alternativas, teclas A–D, barra "3/5", feedback en verde con explicación y XP, y el texto del umbral 80%. | **Son dos mecánicas distintas metidas en una sola pantalla** y hay que partirlas: quiz formativo (feedback inmediato, no otorga nada) vs evaluación final (resultado solo al final, gate 80%, es la nota que respalda la acreditación). Y falta el motor entero: intento, autosave por respuesta, envío idempotente, corrección, reintentos con barajado, y las dos pantallas de resultado (aprobado → medalla / reprobado → sin respuestas + recomendación del módulo). Hoy "Siguiente pregunta →" te manda a Mi Ruta. | La cáscara promete evaluación "Adaptativa" en dos lugares y eso no está definido en ninguna parte. → **S-06**. Y los casos borde que el brief pide descubrir: caída al enviar, doble envío, intento expirado, agotar los 3 reintentos. → **S-11 a S-14**. |

### Área 6 · Juegos

| (a) Qué tenemos | (b) Qué falta | (c) Ambigüedad |
|---|---|---|
| Dos juegos completos y funcionando en cliente: Trivia contrarreloj (45 s, racha, multiplicador, pop de combo, pantalla de resultado) y Memoria de pares (6 pares, intentos, XP decreciente). Es la parte más terminada del mockup. | Que las preguntas salgan del banco del bloque del usuario — hoy son 8 preguntas de CNA escritas a mano, idénticas para todos — y que el XP ganado se registre como evento en el servidor. | **Riesgo de integridad, y es serio.** La trivia entrega `20 + racha×10` XP por acierto y tiene "Jugar de nuevo" sin límite. Como el nivel se deriva del XP (§4.3), alguien puede llegar a **Maestro de Acreditación jugando trivia sin aprobar una sola evaluación**. Es exactamente la completitud falsa que el proyecto existe para impedir. → **S-04, S-05**. |

### Área 7 · Insignias, niveles y XP

| (a) Qué tenemos | (b) Qué falta | (c) Ambigüedad |
|---|---|---|
| Escalera de 6 niveles con umbrales, catálogo de 12 insignias con SVG generado por tipo (Mini/Silver/Gold/Master) y estado ganado/bloqueado, y la barra de XP del sidebar. | El motor completo: `EventoGamificacion`, XP derivado de eventos, nivel derivado del XP, otorgamiento de medalla **solo** tras intento aprobado, y la trazabilidad medalla→intento que exige §4.4. Falta Open Badges (hoy la medalla es un SVG decorativo, no una credencial verificable) y la pantalla de "ganaste una medalla". | Los números de la cáscara se contradicen solos: el sidebar dice "Nivel 4 · Facilitador · 2.840/3.500 XP", pero Facilitador es el nivel **3** de 6 y su banda va de 2.500 a 4.500 — el 3.500 no existe en la escalera. Sirve de prueba de por qué esto debe derivarse y no escribirse. → **S-04, S-10, S-22**. |

### Área 8 · Ranking

| (a) Qué tenemos | (b) Qué falta | (c) Ambigüedad |
|---|---|---|
| Tabla con posición, avatar de iniciales, unidad, insignias, XP, fila propia destacada, corte "· · ·" para saltar a tu posición, y 4 filtros. | El cálculo desde eventos, la paginación alrededor de tu posición, y que los filtros hagan algo (hoy son chips estáticos). Falta la entidad **`Unidad`/`Sede`**, que no existe en el modelo de dominio y sin la cual "mi unidad" no significa nada. | El encabezado dice "se reinicia cada bloque" pero la tabla muestra XP acumulado: se contradicen. ¿Cómo se rompen los empates? ¿Mostrar los nombres de insignias de otros roles viola el invariante de acceso de §3? → **S-15, S-16, S-17, S-20**. |

### Área 9 · Plaza Virtual — track de riesgo

| (a) Qué tenemos | (b) Qué falta | (c) Ambigüedad |
|---|---|---|
| Un salón isométrico en canvas que funciona bien: piso en damero, click-para-caminar con interpolación, avatares con sombra y ordenados por profundidad, globos de habla con wrap y colita, NPCs que caminan y conversan solos, e input de chat. | **Todo lo multijugador, que es literalmente todo lo que importa.** No hay servidor, ni protocolo, ni identidad, ni sincronización, ni reconexión. Los "otros" son `setInterval` con `Math.random()`, y las "42 personas conectadas" es texto fijo. Falta: servidor de estado (Colyseus), esquema de sala, autoridad del servidor sobre las posiciones, presencia real, persistencia y moderación del chat, rate limit, y el túnel para probar fuera de localhost. | **La cáscara es 2D y el brief dice 3D** — la propia pantalla dice "un espacio 2D con avatares". No es un matiz: son semanas de diferencia. → **E-01**. El Escape Room aparece vendido en tres lugares del mockup y CLAUDE.md §8 lo corta → **E-02**. ¿El chat institucional se guarda? ¿quién modera? → **S-24**. |

### Área 10 · Dashboard de Rectoría

| (a) Qué tenemos | (b) Qué falta | (c) Ambigüedad |
|---|---|---|
| Panel completo: 4 KPIs, 2 gráficos Chart.js (participación semanal vs meta, aprobación por segmento), unidades rezagadas con barras, colaboradores críticos, y 4 indicadores de cultura. | Que cada número salga de `EventoGamificacion` en vez de arrays literales. De las 12 métricas, 7 son derivables en el slice; "Satisfacción 4,6/5" exige una encuesta que no existe en ninguna parte del sistema, e "Interacciones en Plaza" exige telemetría del servidor realtime. Los botones "Enviar recordatorio a rezagados" y "Agendar seguimiento 1:1" necesitan adapters de correo y calendario. | El switcher Colaborador/Rectoría es un toggle de UI **sin ninguna autorización**: hoy cualquiera "es" Rectoría con un click. En el sistema real es un permiso. Y el panel expone nombre + cargo + sede + % de avance de personas identificadas → **E-03**. → **S-19, S-21, S-23**. |

### Área 11 · Transversal

| (a) Qué tenemos | (b) Qué falta | (c) Ambigüedad |
|---|---|---|
| Identidad visual completa y coherente (tokens de color, tres tipografías, sombras, radios), 10 pantallas navegables, animación de entrada, y `prefers-reduced-motion` respetado. | **Persistencia cero**: un refresh borra todo, no hay ni `localStorage`. Falta el backend completo, migraciones, seed de los 3 roles, `docker compose` autosuficiente y `/docs` viva. En UI faltan **6 pantallas** que el sistema real necesita y la cáscara no tiene: visor de módulo, resultado de evaluación (aprobado/reprobado), medalla obtenida, perfil y configuración, verificación pública de la insignia, y administración de contenido. | Accesibilidad ausente (`div` con `onclick`, sin navegación por teclado, sin `aria`). Y el menú móvil **no existe**: bajo 1080 px el sidebar se va a `left:-280px` sin botón que lo abra — la app queda sin navegación en teléfono, justo el dispositivo con el que hay que probar la Plaza. → **S-25, S-26, S-28**. |

### Detalles menores detectados (nivel 1, se corrigen al reconstruir)

- El polyfill de `roundRect` se asigna a `HTMLCanvasElement.prototype` en vez de `CanvasRenderingContext2D.prototype`, y además es una función vacía: no parcha nada y en un navegador antiguo los globos y avatares no se dibujan en silencio.
- `tvAnswer()` identifica la alternativa correcta comparando `textContent`, lo que se rompe con textos parecidos.
- El "Próximo evento · Escape Room · vie 19:00" está escrito a mano y no viene de ningún calendario.
- Fuentes de Google Fonts y Chart.js vienen de CDN externo — un portal institucional interno no debería depender de eso (**S-26**).

---

## 2. Supuestos numerados (van a `SUPUESTOS.md` en Fase 0)

**Ruta y diagnóstico**
- **S-01** La ruta la determina el **rol** (CLAUDE.md §3 manda sobre la cáscara). El diagnóstico solo fija `nivel_de_dificultad` y queda como línea base medible; no cambia qué ruta te toca.
- **S-02** El diagnóstico se responde una vez, es obligatorio antes de abrir la ruta, y después queda consultable en solo lectura. Repetirlo no reasigna ruta.
- **S-09** La ruta del slice tiene **3 bloques** por rol, no 8. El mapa se genera desde datos para N nodos. Los 8 bloques quedan como configuración de producción.
- **S-29** El mapa de ruta se dibuja calculado desde los datos, no con el path SVG fijo de 8 nodos.
- **S-30** Los 6 roles del brief son el catálogo; el slice instancia 3 (Profesor, Rector, Secretario Académico). Se corrige el "5 rutas por rol" del hero.

**XP, niveles y medallas**
- **S-04** El XP se parte en dos tipos: **acreditable** (módulos y evaluaciones aprobadas) y **lúdico** (juegos). El **nivel y la completitud derivan solo del acreditable**; el ranking usa el total. Sin esto, jugar trivia en bucle lleva a "Maestro de Acreditación" sin aprobar nada.
- **S-05** El XP lúdico tiene tope diario por juego (default 200 XP/día) y se registra como evento igual que todo lo demás.
- **S-10** Umbrales de nivel = los de la cáscara (0 / 1.000 / 2.500 / 4.500 / 7.000 / 10.000 XP), reescalados al tamaño del slice para que 3 bloques alcancen a subir de nivel al menos una vez — si no, el punto 2 del gate de LISTO no se puede demostrar.
- **S-22** Open Badges v2.0: cada medalla emite una assertion con URL de verificación pública. En el slice el emisor es un adapter local con el mismo contrato que el real.
- **S-27** `es_contenido_prueba: true` se muestra como marca **visible en la UI** de toda ruta generada, para que nadie confunda el slice con acreditación oficial.

**Evaluación**
- **S-06** La "evaluación adaptativa" que anuncia la cáscara no se implementa en el slice: banco fijo por evaluación con ítems barajados por intento. La palabra "Adaptativa" sale de la UI.
- **S-07** La pantalla `#quiz` se parte en dos: **quiz formativo** (feedback inmediato, no gatea nada) y **evaluación final** (resultado al final, gate 80%). Comparten el layout, no la mecánica.
- **S-08** La actividad colaborativa del bloque es **opcional** en el slice: da XP lúdico y no bloquea la completitud ni la medalla.
- **S-11** Reintentos: 3 por evaluación. Al agotarlos el bloque queda "requiere acompañamiento" y solo un rol con permiso institucional puede reabrirlo. **Agotar reintentos nunca otorga la medalla.**
- **S-12** Un intento abierto expira a las 24 h; al expirar se cierra como no aprobado, consume reintento y no otorga nada.
- **S-13** El envío de evaluación es **idempotente por `intento_id`**: un segundo envío devuelve el resultado del primero y nunca crea un segundo evento de XP.
- **S-14** Ante caída al enviar, el autosave por respuesta ya dejó todo en el servidor; "enviar" solo cierra el intento, y al volver se puede cerrar de nuevo sin duplicar (ver S-13).

**Ranking y organización**
- **S-15** Los empates se rompen por: (1) XP acreditable, (2) fecha más antigua del último evento acreditable (premia constancia), (3) alfabético. Las posiciones empatadas muestran el mismo número.
- **S-16** El ranking muestra nombre, unidad, XP total y **conteo** de insignias por tipo — nunca el nombre de insignias de otro rol, porque eso filtraría contenido ajeno (§3).
- **S-17** El "se reinicia cada bloque" se reinterpreta: hay ranking acumulado (default) más un filtro "este bloque" calculado sobre los eventos de ese bloque. No se borra nada.
- **S-20** Se agrega `Unidad` (y `Sede`) al modelo, porque el ranking y el dashboard filtran por ella y hoy no existe.

**Identidad, permisos y dashboard**
- **S-18** Login: SSO de Entra + login dev "actuar como" (solo dev, excluido del build de producción). **Se elimina el formulario de correo y contraseña** de la cáscara: no guardamos contraseñas.
- **S-19** El switcher Colaborador/Rectoría deja de ser un toggle de UI y pasa a ser un permiso; el dashboard solo lo ve quien lo tiene. En dev lo simula el "actuar como".
- **S-21** Métricas derivables en el slice: activos, avance promedio, % de aprobación, insignias otorgadas, rezagados por unidad, colaboradores críticos e interacciones en Plaza. "Satisfacción 4,6/5" requiere una encuesta inexistente → **la tarjeta se oculta, no se inventa el número**.
- **S-23** "Enviar recordatorio a rezagados" y "Agendar seguimiento 1:1" pasan por adapters de correo y calendario; en el slice quedan mockeados y **registran el intento**, no fallan en silencio.
- **S-24** El chat de la Plaza se persiste con autor y timestamp (es un espacio institucional), con rate limit y máximo de 80 caracteres como la cáscara, filtro básico de contenido y capacidad de reporte. No hay mensajes privados.

**Frontend**
- **S-25** Se **evoluciona** la cáscara a componentes con build, sin reescribir la identidad visual. ADR-002 lo fija.
- **S-26** Tipografías y Chart.js se auto-hospedan.
- **S-28** Se agrega botón de menú móvil: hoy el sidebar desaparece bajo 1080 px sin forma de abrirlo.

---

## 3. Orden de trabajo propuesto

**Track A y Track B arrancan el mismo día, en paralelo.** A es el riesgo, B es el papel.

### Track A · Realtime — el que define el plazo

| # | Paso | Gate |
|---|---|---|
| A1 | Fijar 2D vs 3D (ver **E-01**; se arranca con el 2D isométrico de la cáscara mientras se responde) | — |
| A2 | Servidor Colyseus mínimo: sala, esquema de estado (posición, nombre, color), join/leave | dos clientes en localhost se ven |
| A3 | Cliente: reemplazar los `setInterval` por el estado del servidor sobre el canvas que ya existe | el movimiento propio viaja al otro cliente |
| A4 | **Túnel + 2 dispositivos reales fuera de localhost** | ⛔ **hasta que esto pase, ningún plazo es firme** |
| A5 | Chat sincronizado + presencia real (reemplaza el "42" fijo) | el chat no se pierde |
| A6 | Reconexión: un cliente refresca y vuelve sin romper la sala | la sala sobrevive |
| A7 | Los 3 dispositivos a la vez | punto 4 del gate de LISTO |

### Track B · Fase 0 — especificación por tandas (el director revisa cada tanda)

1. **Tanda 1 · Fundaciones** — ADR-001 stack, ADR-002 frontend, glosario, `design-system.md` extraído de los tokens de la cáscara, modelo de datos, JSON Schema del contenido, `SUPUESTOS.md` con los S-01…S-30 de esta auditoría.
2. **Tanda 2 · Motor de integridad** — `EventoGamificacion`, XP acreditable vs lúdico, nivel derivado, otorgamiento de medalla, los 5 invariantes de §4 con sus tests espejo, y el canario. *Todo lo demás depende de esto.*
3. **Tanda 3 · Contenido y evaluación** — contrato del Generador, validador de contenido, quiz formativo vs evaluación final, autosave, reintentos y los casos borde (S-11…S-14).
4. **Tanda 4 · Superficie** — adapters (identidad, correo, Open Badges), permisos, especificación de las 10 pantallas + las 6 que faltan, dashboard desde eventos.

Compuerta de cierre de Fase 0: reporte de consistencia (numeración sin huecos, cero enlaces rotos, terminología idéntica, invariantes espejo completos).

### Track C · Cimientos supervisados — secuencial, el director verifica en su máquina entre cada uno

`C1` scaffold `docker compose up` autosuficiente con `/docs` viva → `C2` modelo + migraciones + seed → `C3` **motor de gamificación + Validador de Integridad + canario en CI** → `C4` adapter de identidad + login "actuar como" → `C5` generador de contenido (3 roles × 3 temas) → `C6` integrador: contenido → rutas en BD.

> C3 antes que cualquier pantalla que otorgue algo: el canario tiene que estar verde **antes de que exista la primera medalla del sistema**.

### Track D · Modo fábrica — worktrees en paralelo, ya con cimientos verdes

UI de ruta/bloque/**módulo** (la pieza que no existe) · quiz formativo + evaluación final · insignias y Open Badges · ranking · dashboard · juegos recableados al banco real y al tope de XP lúdico.

**Cierre:** los 5 puntos de CLAUDE.md §13, verdes de punta a punta.

### Por qué este orden

1. El realtime es lo único no probado: se prueba con dispositivos reales **antes** de comprometer plazos.
2. El motor de integridad va antes que cualquier pantalla que otorgue algo, porque una medalla emitida sin gate es el peor bug del sistema y hay que hacerla **imposible por construcción**, no arreglarla después.
3. El generador va después del motor: produce datos para un motor que ya tiene que existir.
4. La UI va en paralelo desde el principio (§14: módulo sin UI operable no está HECHO), nunca al final.

---

## 4. Decisiones que tomé y no te consulto

**Nivel 1 (decididas y registradas):** S-05, S-06, S-10, S-12, S-13, S-14, S-15, S-17, S-20, S-22, S-24, S-25, S-26, S-27, S-28, S-29, S-30 y los detalles menores.

**Nivel 2 (decididas con default conservador — ratificación en lote, tu silencio las ratifica):**

| # | Decisión | Default tomado |
|---|---|---|
| S-04 | XP de juegos vs integridad | XP dual: nivel y completitud solo del acreditable |
| S-01 | Rol vs diagnóstico como asignador de ruta | manda el rol; el diagnóstico fija dificultad |
| S-07 | La pantalla de quiz | se parte en dos mecánicas |
| S-09 | Tamaño de la ruta del slice | 3 bloques, no 8 |
| S-11 | Agotar los 3 reintentos | no cierra el bloque ni otorga medalla |
| S-16 | Insignias ajenas en el ranking | solo conteos, no nombres |
| S-18 | Login con contraseña de la cáscara | se elimina |
| S-19 | Switcher Rectoría | pasa a ser permiso |
| S-21 | "Satisfacción 4,6/5" | se oculta la tarjeta, no se inventa el dato |

---

## 5. Escalamientos — las 3 que sí necesito de ti

### E-01 · ¿La Plaza es 2D o 3D?

El brief y CLAUDE.md dicen "sala 3D". La cáscara entrega un salón **2D isométrico** tipo Habbo, y el texto de la propia pantalla dice "un espacio 2D con avatares". No es un detalle de vocabulario: 3D real (motor, modelos, animaciones, cámara) son varias semanas más y cambia el perfil de riesgo del proyecto entero.

**Mi recomendación:** construir el 2D isométrico que ya está en el mockup. Es lo que la demo le mostró al cliente y prueba exactamente la misma tesis — verse, moverse y hablar en tiempo real desde tres dispositivos.

**Lo que necesito saber:** ¿qué vio AIEP en la propuesta: este salón, o algo tridimensional? *(Para verificarlo yo mismo necesito la propuesta comercial, que no está en el repo.)*

### E-02 · El Escape Room está vendido en la cáscara

CLAUDE.md §8 lo corta para fase 2, pero el mockup lo muestra en **tres lugares**: "Próximo evento · Escape Room" en Mi Ruta, el banner de la Plaza con "+250 XP en juego", y la actividad colaborativa bloqueada dentro del Bloque 4. Si AIEP lo vio en la demo, cortarlo es una decisión comercial, no técnica, y prefiero que la tomes tú.

**Mi recomendación:** cortarlo del slice como manda CLAUDE.md, y reemplazar esos tres puntos de la UI por "Encuentro en la Plaza" — mismo espacio social, sin lógica de juego.

**Lo que necesito saber:** ¿AIEP tiene el escape room como expectativa firme para esta etapa?

### E-03 · Exponer el avance individual con nombre y apellido

El dashboard lista "Colaboradores críticos" con nombre, cargo, sede y su porcentaje de avance (0 %, 12 %…), y el ranking publica nombres con XP. Es dato personal en contexto laboral, con la ley 21.719 ya vigente en Chile.

**Mi recomendación (conservadora):** el ranking mantiene los nombres — es gamificación aceptada y ya está en la demo —, pero el panel de rezagados se muestra **agregado por unidad**, y el detalle nominal queda detrás de un permiso explícito y con registro de quién lo consultó.

**Lo que necesito saber:** ¿AIEP o su área de personas ya autorizó que las jefaturas vean el avance individual nominado de cada colaborador?

---

## 6. Qué necesito para cerrar el Día 0

1. **La propuesta comercial de AIEP** en `docs-fuente/` — es el documento que manda y es el que responde E-01 y E-02.
2. Tu respuesta a los tres escalamientos (o "usa tu recomendación" en los que te dé lo mismo).
3. Permiso para mover el mockup a `referencia-demo/somos-calidad.html` y hacer `git init` + primer commit.

Con eso arranco **Track A (spike realtime)** y **Tanda 1 de Fase 0** el mismo día.
