
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
