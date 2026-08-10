
# BITÁCORA — control de obra Somos Calidad

## 2026-08-09 · Día 0 cerrado + Tanda 1 + spike arrancado

**Auditoría del Día 0** entregada y aprobada. 10 pantallas de la cáscara auditadas, 42
supuestos numerados, 3 escalamientos respondidos por el director.

**Encuadre corregido por el director:**
- No hay documento comercial que mande. El alcance técnico lo define el arquitecto.
- El sistema se arma en torno a la **ruta oficial de AIEP** (`docs-fuente/`), que pasó a ser
  la fuente de dominio: 5 dimensiones CNA, 13 hitos 2026–2027, gobernanza por comités.
- Modelo **Cargo × Dimensión**: los cargos no son las dimensiones.

**Hallazgo que definió la arquitectura.** La fuente dice que los estándares CNA están
"organizados jerárquicamente: el nivel 3 incluye al 2 y el 2 al 1". Es una escala de
profundidad anidada que ya existe en el marco real, así que se usa en vez de inventar otra:
la unidad de generación es el par **(dimensión, nivel)** → 15 unidades de contenido en vez de
30, y la ruta de cada cargo es una fila de la matriz. Ver ADR-003.

**Tanda 1 de Fase 0 — completa.** 12 documentos: dominio extraído de la fuente, 5 ADRs,
glosario, modelo de datos, sistema de diseño, JSON Schema del generador, reglas del
validador, supuestos y decisiones autónomas.

**Track A — spike de realtime levantado y probado.** Servidor Colyseus con autoridad de
posición, chat con rate limit, y reconexión de 20 s. **10 de 10 gates automatizables en
verde** (A2, A3, A5).

**Decisión que sacó E-01 del camino crítico:** el servidor sincroniza tiles del plano, no
píxeles, así que 2D y 3D consumen el mismo estado. El spike prueba el servidor; el render se
decide después del gate A4 y cuesta un módulo de cliente. Ver ADR-004.

### Incidente: A4 en rojo por el bundle del cliente — corregido

El director corrió A4 por túnel y el botón "Entrar" no hacía nada. Consola:
`Buffer is not defined` y `Colyseus.Client is not a constructor`.

**Causa raíz.** Yo servía `node_modules/colyseus.js/dist/colyseus.js`, que en la 0.15.28
es un UMD compilado contra Node (`require` de net, tls, buffer). Reventaba antes de
asignar el global, y como el fallo ocurría a nivel de módulo, los listeners nunca se
registraban: el botón moría en silencio. Error mío al elegir el archivo por su nombre en
vez de por la condición `browser` del paquete.

**Corregido.** esbuild empaqueta `lib/index.js` (condición browser) a
`cliente/vendor/colyseus.js`: 75 kb contra 378, sin Node adentro. El cliente ahora hace
autochequeo y muestra los errores en pantalla.

**Verificado** con control negativo —el verificador reproduce los dos errores exactos
contra el build viejo— y en Chrome real, incluido el camino del túnel: dos clientes en la
misma sala, uno por `ws://localhost` y otro por `wss://…ngrok-free.dev`, viéndose y
caminando, con cero errores en consola.

**Lección para el resto del proyecto:** cualquier dependencia que se sirva al navegador
pasa por un verificador que la cargue en sandbox sin globals de Node. Un bundle equivocado
no da error de compilación: da un botón muerto.

### HITO 1: multijugador realtime validado sobre internet con 3 usuarios en redes distintas

**Aprobado por el director.** Tres personas reales en ubicaciones distintas —el director,
su pareja y su tío— entraron a la Plaza por túnel, eligieron cargo, se movieron y
chatearon. Funcionó en los tres. Lag leve y usable para los remotos, esperable con el
servidor en un Mac detrás de ngrok; en producción sobre Azure debería bajar.

**Esto cierra los gates A4 y A7 de una vez** (dos dispositivos fuera de localhost, y los
tres a la vez). Es el punto 4 de la definición de LISTO de CLAUDE.md §13.

**Lo que significa para el proyecto:** la única incógnita real está despejada. Escalar de
3 a 50 es configuración, no reconstrucción. Desde acá, los plazos se pueden comprometer.

### Tanda 2 — motor de integridad: el canario está verde

Construido y corriendo contra PostgreSQL 16 real. **28 pruebas en verde, 1 declarada
pendiente** (aislamiento por cargo, que es de capa API y va en la Tanda 4).

Los invariantes viven en el esquema, no en la capa de servicio (ADR-005). La cadena que
habría que romper para falsificar una completitud es
`insignia → intento_evaluacion → bloque_ruta → bloque_contenido`, y cada eslabón tiene su
candado. Dos candados que agregué al construir y que no estaban en la spec:

- El intento que respalda la medalla tiene que ser **del mismo colaborador**. Si no,
  alguien reclama la medalla con el intento aprobado de otra persona.
- Y del **mismo bloque de contenido**. Si no, se aprueba "VcM N1", que es el bloque más
  liviano, y se reclama la medalla de "Docencia N3".

Ambos están cerrados con trigger y con su prueba.

**Banco de mutación.** Un test de integridad que pasa igual con el candado roto no prueba
nada, así que rompo cada candado a propósito y exijo que la suite se ponga roja. Los cinco
se detectan. Corre en CI como job propio.

**CI** (`.github/workflows/integridad.yml`): el canario, el canario de esquema, la
regresión, el banco de mutación y los gates de la Plaza, en cada push y cada PR.

### HITO 2: motor de integridad blindado en esquema + canario + banco de mutación verificado — falsificar una completitud es imposible por construcción

**Aprobado por el director**, verificado en su máquina: `correr-pruebas.sh` → 28 passed,
1 skipped (I-10 declarada para la Tanda 4). `prueba-mutacion.sh` → los 5 candados rotos se
detectan y la suite se pone roja donde debe. El canario está verde **antes de que exista la
primera medalla del sistema**. A6 (reconexión) también en verde.

### C1 + C2 — el sistema levanta con un comando y tiene datos de verdad

`docker compose up` y listo: espera la base, migra, siembra y sirve. Tres servicios en
**healthy**. Guía de verificación en [VERIFICAR.md](VERIFICAR.md).

Seed exacto: **5 dimensiones · 13 hitos · 6 cargos · 30 filas de matriz · 15 unidades de
contenido · 3 colaboradores**, todo derivado de la ruta oficial de AIEP.

**La tesis de ADR-003 quedó verificada con datos:** las 15 unidades de contenido sirven los
30 pares cargo×dimensión. La suma de `cargos_que_la_usan` da exactamente 30. Y las rutas se
ven distintas: el Rector no tiene ningún nivel 1; el Docente tiene un solo nivel 3.

El ciclo completo corre por la API: el canario canta dentro del sistema desplegado
(reprobar → sin medalla, sin XP, sin cambio de escalón), el camino legítimo otorga con su
respaldo auditable, y el doble envío no duplica nada.

**Dos cosas que aparecieron al levantar:**

- Los puertos 5432 y 8000 estaban tomados por `portal-inclusion`. Los defaults pasaron a
  **8010 / 5442 / 2567** para que los dos proyectos convivan sin apagar nada (S-44).
- El healthcheck del realtime daba "connection refused" con el servicio sano: en Alpine
  `localhost` resuelve primero a `::1` y el servidor escucha en IPv4. Corregido a `127.0.0.1`.

### C5 — Generador de Contenido: las rutas tienen contenido formativo real

**15 unidades generadas, 45 módulos, 360 ítems de banco.** Todo pasa el Validador antes de
entrar; si algo se rechaza, el sistema **no levanta**. Mejor no arrancar que arrancar con un
banco que se puede aprobar sin saber la materia.

El conocimiento se escribe **una vez por dimensión** —50 conceptos, 10 por dimensión, con
`nivel_minimo`— y el anidamiento de los estándares CNA produce los tres niveles. De cada
concepto salen tres ítems: definición, escenario aplicado y emparejamiento. El de
emparejamiento se compone solo cruzando definiciones del mismo bloque, así que da variedad
real sin inventar contenido.

Todo marcado `es_contenido_prueba: true`, con el aviso dentro del propio microlearning. La
estructura sale de la ruta de AIEP; el desarrollo didáctico lo reemplaza el experto CNA sin
tocar el modelo — ese es el swap de `fuente_de_contenido`.

**Dos hallazgos:**

- El detector de relleno del validador daba **falsos positivos en español**: buscaba "todo" y
  "pendiente" como subcadena y los encontraba dentro de *método* e *independiente*. Se separó
  en subcadenas inequívocas y centinelas exactos, más un mínimo de cuatro palabras por
  explicación. Quedó test de regresión.
- El Validador cargaba el schema contando niveles de directorio (`parents[3]`), lo que
  funcionaba en el repo y apuntaba a la raíz del sistema de archivos dentro del contenedor.
  Ahora lo busca hacia arriba, y el contexto de build de la API pasó a la raíz para que
  `docs/contenido/` siga siendo una sola fuente de verdad.

Verificado que la API sirve **exactamente** lo que produce el generador: mismos módulos,
mismo banco. Suite completa: **63 en verde, 1 declarada pendiente**.

### C4 — identidad, y con eso I-10 cerrado

Adapter conmutable (S-18): `ProveedorDev` para el login "actuar como" y `ProveedorEntra`
con el contrato listo, pendiente de tenant. Sesión firmada con HMAC de la biblioteca
estándar, sin dependencias nuevas y sin estado en servidor. **No hay contraseñas en
ninguna parte**, ni en dev ni en producción.

**I-10 cerrado.** Ningún endpoint recibe `colaborador_id` por parámetro: se deriva de la
sesión. Todo acceso a contenido pasa por `_bloque_propio()`. Y responde **404, no 403**:
un 403 confirmaría que el bloque existe, y eso ya filtra información del contenido de otro
cargo. Hay un test que verifica que la respuesta al bloque ajeno sea indistinguible de la
de un id inventado. 11 pruebas nuevas; la suite quedó en **74 en verde y cero pendientes**.

Un detalle de entorno: la API usaba `str | None` en una firma que FastAPI evalúa en
runtime, y la máquina del director tiene Python 3.9. Cambiado a `Optional[str]` para que
la suite se pueda correr en local, aunque el contenedor use 3.12.

### D1a — primera pantalla navegable

Vite + React + TypeScript (ADR-002), con los tokens de la cáscara literales y las fuentes
**autohospedadas** vía `@fontsource` (S-26): ya no dependen de Google Fonts.

- **Ingreso**: elección de colaborador. Sin formulario de correo y contraseña, que se
  eliminó a propósito de la cáscara.
- **Mi Ruta**: el mapa **se genera desde datos** (S-29) — serpentina calculada para N
  bloques más la graduación, con curva suave, y la línea de avance por `stroke-dasharray`.
  Cambiar el tamaño de la ruta ya no toca el dibujo.
- La marca de **contenido de prueba se ve** en la barra superior (S-27), el estado de cada
  bloque va en texto además de color, y hay foco visible en todo lo operable.
- El compose ahora levanta **cuatro servicios**: db, api, realtime y web.

**No verificado:** el layout móvil (S-28). El botón de menú y el sidebar deslizante están
implementados, pero el canal de navegador que uso mantiene el viewport en 1200 px y no
pude probarlo en angosto. Queda para el director, que ya tiene el hábito de probar en
teléfono.

### Incidente: la pantalla de Ingreso no cargaba en el contenedor — CORS

El director levantó el compose y la pantalla de Ingreso quedó vacía.

**Causa raíz, y es mía.** Al contenedorizar la web, el frontend pasó a llamar a
`http://localhost:8010` desde `http://localhost:5180`: **origen distinto**. Con el servidor
de desarrollo de Vite esto no se veía porque su proxy dejaba todo same-origin. Verifiqué el
contenedor con `curl` y revisando el bundle, pero **no lo abrí en el navegador**, que es
donde el error existe: `curl` ignora CORS.

Medido antes de tocar: el preflight `OPTIONS` daba **405** y el `GET` respondía 200 pero sin
`Access-Control-Allow-Origin`, así que el navegador descartaba la respuesta.

**Corregido** con `CORSMiddleware`: métodos GET/POST/OPTIONS, cabeceras `Authorization` y
`Content-Type`, sin credenciales —la sesión va en cabecera, no en cookie—, y preflight
cacheado 600 s. Los orígenes salen de `ORIGENES_PERMITIDOS`; si no está definida y corre en
modo dev, se acepta localhost y red privada en cualquier puerto, para poder abrir la web
**desde el teléfono**. Fuera de modo dev y sin la variable no se permite ningún origen:
mejor que falle visible a que quede abierto por omisión.

**Segundo bug, destapado por el primero.** Con la base recreada (`down -v`), el token viejo
del navegador apuntaba a un colaborador inexistente y la app quedaba en una pantalla de
error **sin salida**. Ahora una sesión que ya no identifica a nadie se trata como sesión
caída y vuelve sola al Ingreso, y toda pantalla de error tiene botón de vuelta.

**Lección, la misma que con el bundle de Colyseus:** lo que corre en el navegador se
verifica en el navegador. `curl` no hace preflight, no aplica CORS y no ejecuta el bundle.

### D1b — pantalla de bloque y visor de módulo

La pieza que la cáscara prometía y no tenía: el microlearning ahora se lee de verdad.

**Backend.** `GET /bloques-ruta/{id}` devuelve el bloque completo —módulos con su estado,
evaluación, medalla— y `POST /modulos/{id}/completar` marca el módulo como visto. Suma XP
**acreditable** (S-04: el recorrido formativo lo es), es idempotente por clave de evento, y
**no otorga insignia**: eso sigue siendo exclusivo de la evaluación aprobada.

`evaluacion_disponible` se abre cuando están vistos todos los módulos. No es un candado de
integridad —esa la impone la base— sino la secuencia formativa.

También se agregó `abrir_siguiente_bloque`: al aprobar un bloque se habilita el siguiente.
Sin eso la ruta quedaba con un solo bloque abierto para siempre y el mapa no avanzaba nunca.

**Frontend.** Se extrajo `Marco` —sidebar, barra superior y marca de contenido de prueba—
para que ninguna pantalla repita el armazón ni pueda olvidarse la marca. El microlearning se
renderiza con un componente propio: el generador produce un subconjunto acotado de Markdown,
así que se convierte a mano y **sin HTML crudo**, todo pasa por el árbol de React.

Navegación con un estado de tres vistas, sin router: con estas pantallas una dependencia de
enrutado agrega más de lo que resuelve. Se reevalúa cuando entren ranking, insignias y Plaza.

**Bug encontrado en el navegador.** `App` cargaba identidad y ruta con `Promise.all`, así que
**el error que ganaba la carrera decidía el mensaje**: con un token viejo, si `/mi/ruta`
respondía primero, la app mostraba "todavía no tienes ruta generada" en vez de detectar la
sesión caída y volver al ingreso. Ahora es secuencial: primero identidad, después datos.

Verificado en Chrome de punta a punta: ruta → bloque → módulo → completar. El XP pasó de 0 a
100, la barra del sidebar se movió y avanzó al módulo 2 de 4. Suite: **82 en verde**.

### D2a — quiz formativo: la mecánica de juego

Feedback inmediato verde y rojo con la correcta a la vista, racha, multiplicador y combo
pop. Portado de la sala de juegos de la cáscara.

**Hallazgo al empezar:** el Generador producía los ítems del quiz desde el principio, pero
**no existía dónde guardarlos** y el Integrador los descartaba en silencio. Migración 003 con
tabla propia — y propia a propósito: el quiz entrega la respuesta correcta al cliente para
dar feedback, y el banco de la evaluación no lo hace jamás. Si vivieran juntos, una consulta
distraída filtraría el banco.

**El puntaje lo calcula el servidor** desde las respuestas y su orden. El cliente solo manda
qué eligió. Si propusiera su propio XP, el tope y la racha serían decorativos.

**El XP del quiz es lúdico**, y se ve en pantalla: tras jugar, el sidebar sigue marcando
0 XP acreditable y escalón Explorador, mientras el ranking sí registra los 30 XP. Jugar no
acerca a nadie a una medalla.

**Corrección de S-05.** El tope de XP lúdico estaba implementado **global** y la spec decía
**por juego**. Global castigaba al que avanza: jugar el quiz de dos módulos el mismo día
agotaba el presupuesto y el tercero quedaba en cero sin explicación. Ahora es por `origen_id`
y el default subió de 200 a 400, porque una partida perfecta del quiz más largo vale 330.

Suite: **88 en verde**.

### D2b — evaluación final, y el canario vivido en la interfaz

Deliberadamente lo contrario al quiz: fondo claro, sin colores de acierto, sin racha, sin
corrección pregunta a pregunta. La alternativa elegida se marca en tinta, **no en verde**:
en la evaluación no hay señal de acierto hasta el final.

**Las respuestas correctas no se revelan nunca**, ni aprobando ni reprobando. La pantalla lo
explica: el reintento tiene que medir lo que sabes, no lo que recuerdas de la prueba anterior.

**Autosave verificado con recarga real:** se respondió una pregunta, se recargó el navegador
entero, y volvió con 1/5 respondida, el paso 1 marcado y el cursor en la pregunta 2 — la
primera sin responder, no la uno.

**El canario, vivido en pantalla.** Se reprobó a propósito: 0%, "Evaluación no aprobada",
sin revelar nada, 2 intentos restantes. Y detrás: **0 insignias, bloque 1 sin completar,
bloque 2 todavía cerrado**. Después se aprobó al 100%: medalla otorgada, 400 XP acreditable,
bloque 1 completo y **bloque 2 abierto solo**. El respaldo queda auditable — intento nº2,
puntaje 1.0, con su fecha.

**Endurecimiento que apareció al construir:** `abrir_intento` no exigía haber visto los
módulos. La pantalla lo escondía, pero bastaba llamar al endpoint para saltarse el bloque
entero. Ahora lo exige el servidor.

### S-28 cerrado — navegación móvil verificada

Quedaba pendiente desde D1a porque el canal de navegador mantenía el viewport en 1200 px.
Con la ventana en **900 px**: el sidebar está en `left: -280px`, el botón de menú aparece
(`display: grid`), y al pulsarlo entra a `left: 0` con su velo. Funciona.

Suite: **92 en verde**.

### D6 — arranca la capa de gamificación: prerrequisitos y M1 Calibre

**Plan de juegos aprobado** con tres ajustes del director: M2 a 2 minutos, regla del tope de
ranking ratificada, y memoria de pares descartada.

**Corrección a mi propio plan, antes de implementarlo.** Había escrito que Calibre se
alimentaría del quiz del módulo **y del banco de la evaluación**. Está mal: Calibre muestra
la respuesta correcta para dar feedback, y servir ítems del banco con su correcta habría
**filtrado la evaluación** por un endpoint nuevo. M1 usa solo ítems de quiz formativo, que
son los que ya están diseñados para revelarse.

**Migración 004 — dificultad.** Era el prerrequisito declarado. Los 360 ítems del banco
quedaron con su dificultad repartida en los tres tramos que M2 necesita.

**Migración 005 — tope de ranking.** «Jugar puede como mucho duplicar tu posición, nunca
reemplazar el recorrido»: el ranking suma XP lúdico hasta igualar el acreditable. Verificado
en el sistema corriendo — con 20 XP de juego y 0 acreditable, la posición es 0.

**M1 Calibre.** Eliges alternativa y después declaras confianza. «Seguro» acertado +60,
fallado **−40**; «Creo» +25 / 0. Bono de calibrado si todos los «Seguro» resultan correctos.
Sin reloj: la tensión sale de la apuesta.

Tres decisiones de implementación que sostienen el diseño:

- **Antes de apostar no hay verde ni rojo.** La alternativa elegida se marca en blanco. Si
  el color delatara el acierto antes de la apuesta, no habría apuesta.
- **El marcador puede quedar negativo en pantalla, el XP no.** El castigo es no ganar, no
  perder XP ya ganado.
- **El bono premia calibración, no volumen:** ir siempre a «Creo» y acertar todo no lo gana.

Suite: **100 en verde.**

### Camino B — la gamificación deja de ser cuestionarios

**Cambio de dirección del director**, y tiene razón: Calibre, Ascenso y Comité comparten el
mismo verbo —responder una pregunta con una capa de decisión encima— y por debajo se sienten
a cuestionario. El peso se mueve a mecánicas donde el contenido **se manipula**. Calibre se
queda como práctica rápida; **M2 y M3 quedan en pausa**.

**Lo primero fue mirar qué material existe de verdad**, porque eso decide qué es barato:

- **Ordenar** tiene **una sola fuente auténtica**: los 13 hitos. Todo lo demás («las fases de
  la autoevaluación», «el ciclo de mejora continua») está en prosa dentro del microlearning,
  no estructurado. Hacerlo jugable exige generarlo.
- **Clasificar por fortaleza/debilidad/oportunidad —el ejemplo del director— hoy es
  imposible**: no hay una sola afirmación etiquetada así. En cambio **clasificar por
  dimensión** sale gratis: 120 afirmaciones verdaderas ya etiquetadas.
- **Simular** no tiene absolutamente nada: ni casos encadenados, ni modelo de indicadores, ni
  consecuencias. Y su versión barata no sirve — encadenar escenarios sueltos daría
  consecuencias genéricas y se notaría.

Diseño de las cuatro en `docs/DISENO-GAMIFICACION-B.md`, con costo honesto por mecánica.

**Construida: B2 «Mesa de comité».** Cinco bandejas, seis afirmaciones, se mueven libremente
entre bandejas y solo se corrige al cerrar. Se juega comparando unas con otras. Dos formas de
mover —arrastrar y tocar-carta/tocar-bandeja— porque un juego de arrastre que solo funciona
con ratón deja fuera justo a quien lo usará en el teléfono.

El reveal es lo que la hace enseñar: la carta mal ubicada se pinta y dice **dónde iba y de qué
concepto se trataba**. Jugada real: 5 de 6, con el acompañamiento estudiantil puesto en
Aseguramiento cuando era Docencia — un error legítimo, del tipo que discute un comité.

Verificado: la Mesa no mueve XP acreditable, ni escalón, ni insignias, y respeta el tope de
ranking. Suite: **106 en verde**.

### Pendiente inmediato — son del director, no míos
- **A4** túnel + 2 dispositivos reales fuera de localhost. Hasta que pase, ningún plazo es firme.
- **A6** reconexión por refresh · **A7** los 3 dispositivos a la vez.

### Avance
- Track A: 4 de 10 · Track B: 4 de 8 · Track C: 0 de 6 · Track D: 0 de 7
- Bloqueos activos: ninguno. Fallos de gate: 0.

### Riesgo abierto
El único es A4. Si la latencia por túnel no da, el plan B es red local compartida y, si
tampoco, un servidor de estado más simple con menos frecuencia de patch. No hay plan C
porque no hace falta todavía.
