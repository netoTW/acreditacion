
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
