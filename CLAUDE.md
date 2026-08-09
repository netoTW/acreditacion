# CLAUDE.md — Portal de Gamificación "Somos Calidad" (AIEP)

> Constitución del proyecto. Claude Code lee este archivo automáticamente al abrir
> la carpeta. Es la autoridad sobre CÓMO se trabaja acá. El documento fuente
> (`docs-fuente/`) manda sobre cualquier resumen. Cuando algo choque, gana el
> documento fuente; si el documento no lo dice, es SUPUESTO numerado.

---

## 0. Qué es este proyecto y cuál es el objetivo real

Estamos convirtiendo un **mockup navegable** (la "cáscara" visual en
`referencia-demo/`) en un **sistema real y funcional**: el Portal de Gamificación
"Somos Calidad" para AIEP.

**El propósito institucional del producto** (esto define el invariante más
importante): la plataforma es el **respaldo con el que AIEP demuestra que sus
colaboradores cumplen con los conocimientos necesarios para la acreditación CNA**.
Cada colaborador, según su rol, recorre una ruta de niveles, aprueba evaluaciones y
gana medallas. Que la plataforma diga "Fulano completó su ruta" tiene que ser
**verdad verificable**, porque es evidencia ante un proceso de acreditación. Una
completitud falsa (una medalla o nivel otorgado sin haber aprobado de verdad) es el
**peor bug posible** del sistema.

### Objetivo de ESTA etapa: vertical slice para 3 roles

No construimos los 1.600 usuarios ni el contenido CNA real todavía. Construimos el
**sistema entero funcionando de punta a punta, para 3 usuarios reales** (el director
y sus 2 socios), cada uno en un rol distinto, usándolo como si fuera producción.

Esto es una **prueba de tesis**: si 3 personas pueden loguearse, recibir rutas
distintas por rol, completar bloques con contenido real, ganar medallas legítimas,
entrar los 3 a la misma sala 3D y verse en tiempo real, y ver su avance en el
dashboard — entonces el sistema completo funciona y solo falta ESCALARLO (más
usuarios, más contenido), no reinventarlo.

### Desacople clave: la máquina es independiente del contenido

El contenido de acreditación real (por rol) **no lo tenemos y no lo necesitamos para
probar la máquina**. Un **agente generador** toma `(rol, tema)` y produce una ruta
formativa COMPLETA de prueba —todos los niveles, módulos, banco de ítems,
evaluaciones y medallas— sobre CUALQUIER tema. Ejemplo del slice:

- Rol "Profesor" (el director) → tema **"Data Science"** → ruta completa generada.
- Rol 2 → otro tema. Rol 3 → otro tema.

En producción, el `tema` pasa a ser el contenido CNA que aporta AIEP. **La máquina de
gamificación es exactamente la misma.** Ese desacople es lo que convierte el slice en
producto vendible: probamos el motor con contenido cualquiera, y en la venta se
inyecta el contenido real.

### La cáscara de referencia

En `referencia-demo/` está el mockup (un HTML navegable con 9 pantallas: ingreso,
diagnóstico, mi ruta, bloque, evaluación, juegos, insignias, ranking, plaza virtual
3D, dashboard). **Es la referencia visual y de experiencia — el "qué se ve".** No es
código de producción; es la meta de UX. La primera tarea del arquitecto es
analizarla COMPLETA para entender la experiencia que hay que hacer real.

---

## 1. Roles del proyecto (quién hace qué)

| Rol | Quién | Hace | NO hace |
|---|---|---|---|
| **Director** | El humano (Pablo) | decide, revisa tandas, verifica EN SU MÁQUINA, responde escalamientos nivel 3 | especificar ni construir a mano |
| **Arquitecto** | agente | audita, especifica (Fase 0), propone, revisa lo construido, mantiene la doc | decidir lo estructural sin el director; escribir código de módulos |
| **Constructores** | agentes | implementan SOLO contra specs, con sus tests | tocar módulos ajenos; inventar fuera de spec |
| **Gates** | código | juzgan (tests, lint, e2e, validadores) | — un agente nunca es juez cuando existe un test |

### Los constructores especializados de ESTE proyecto

- **Arquitecto** — estructura, stack, contratos entre módulos, ADRs, Fase 0.
- **Generador de Contenido** — dado `(rol, tema)`, produce la ruta formativa completa
  como datos estructurados (niveles, módulos, piezas, banco de ítems, evaluaciones,
  definición de medallas). Ver §5.
- **Integrador de Gamificación** — toma el contenido generado y lo monta en la
  mecánica: rutas, XP, medallas, niveles, ranking, progresión. Ver §6.
- **Diseñador de Juegos/Interacción** — mecánica de quizzes, feedback, evaluaciones,
  reglas de aprobación/reintento. Ver §7.
- **Constructor Realtime** — la sala 3D multijugador. Track propio, es la pieza de
  riesgo. Ver §8.
- **Validador de Integridad** — reemplaza el "red team" del método original: verifica
  que ninguna completitud/medalla sea falsa y que el contenido generado sea coherente.
  Ver §9.

---

## 2. Protocolo de decisiones en 3 niveles (heredado, es LEY)

**Ninguna duda detiene el trabajo. Siempre hay default y se sigue.**

- **NIVEL 1 — DECIDE SOLO** (la gran mayoría): duda con default razonable y barata de
  revertir. El arquitecto decide, registra UNA LÍNEA en `DECISIONES-AUTONOMAS.md`
  {qué, default, por qué, cómo se revierte} y CONTINÚA. Valores seed, umbrales,
  nombres, formatos: siempre nivel 1.
- **NIVEL 2 — DECIDE Y AVISA**: decisiones medianas. Decide con default conservador,
  sigue, y las lista en el resumen de tanda para ratificación EN LOTE. Silencio del
  director = ratificada.
- **NIVEL 3 — ESCALA** (excepcional): SOLO si (a) es irreversible/caro de cambiar,
  (b) depende de conocer el cliente/negocio real, o (c) compromete dinero, legal o
  seguridad. Formato: pregunta en lenguaje simple SIN jerga, más la recomendación del
  arquitecto. **Máximo 3 por tanda**; el excedente baja a nivel 2.
- `DUDAS.md` es SOLO para preguntas al cliente real (levantamiento futuro), no cola de
  decisiones. Niveles 2 y 3 se presentan EN LOTE al cierre de tanda, nunca goteados.

---

## 3. DOMINIO: Actores y rutas (el cuestionario ya respondido)

### Actores
Roles institucionales de AIEP: **Profesor, Rector, Secretario Académico, Director de
Carrera, Administrativo, Servicios de Apoyo** (y más en producción). **Cada rol tiene
su PROPIA ruta**: sus niveles, sus medallas, su contenido. La progresión y las
medallas de un rol son independientes de las de otro.

**Prohibición central (invariante de acceso):** la ruta de un rol **no muestra el
contenido ni el progreso de otro rol**. Un usuario ve SU ruta y el ranking agregado,
nunca el material de una ruta que no es la suya.

**Para el slice:** 3 usuarios reales = 3 roles. Cada uno con un `tema` distinto
generado (ej: Profesor→Data Science). Deben verse claramente rutas y medallas
distintas por rol — eso prueba la personalización.

### Niveles y medallas (de la cáscara, son el default)
Escalera de nivel por XP: **Explorador → Colaborador → Facilitador → Embajador →
Líder de Calidad → Maestro de Acreditación**. Medallas por tipo: **mini** (por
módulo), **silver** (por bloque), **gold** (cada 4 bloques), **master** (graduación).
Estándar de credencial: **Open Badges** (verificable), para que la medalla sea
evidencia real y no un adorno.

---

## 4. INVARIANTE MÁXIMO: Integridad de Completitud

> Este es el corazón del sistema y reemplaza al "control de acceso a datos clínicos"
> del proyecto del que hereda el método. Acá el activo a proteger no es un dato
> sensible: es la **VERDAD de que alguien cumplió**.

Reglas invariantes (tests espejo en cada módulo que las toque):

1. **Ninguna medalla, nivel o completitud de bloque se otorga sin haber aprobado la
   evaluación correspondiente al umbral requerido (80% por defecto).** No hay ruta de
   código que produzca una medalla sin pasar por el gate de aprobación.
2. **El XP nunca es negativo y solo aumenta por eventos legítimos** (aprobar, no
   "setear"). Todo XP proviene de un `EventoGamificacion` con origen verificable.
3. **El nivel del usuario es SIEMPRE derivable de su XP acumulado** — nunca un campo
   editable a mano que pueda desincronizarse.
4. **La completitud es auditable**: para toda medalla otorgada existe el intento de
   evaluación aprobado que la respalda, con su timestamp. Si no existe el respaldo, la
   medalla es inválida por construcción.
5. **Un intento reprobado NO otorga nada** y no deja residuo que luego pueda contar
   como avance.

El **Validador de Integridad** (§9) tiene un "canario": un intento deliberadamente
reprobado que JAMÁS debe producir medalla. Si el canario produce medalla, el sistema
está roto y el build se bloquea.

---

## 5. DOMINIO: Generador de Contenido

**Entrada:** `(rol, tema, nivel_de_dificultad)`. **Salida:** datos estructurados (no
prosa suelta) que el Integrador consume directo:

- Una **ruta** con N bloques (default 8, configurable a menos para el slice).
- Cada bloque: 2 módulos + 1 evaluación final + 1 medalla definida.
- Cada módulo: pieza de microlearning (texto/guion) + quiz formativo.
- Un **banco de ítems** por evaluación (preguntas con alternativas, marca de correcta,
  y explicación por alternativa).
- Metadatos de gamificación: XP por módulo/bloque, medalla asociada.

**Reglas del generador:**
- El contenido de prueba puede ser de CUALQUIER tema (data science, cocina, historia)
  — sirve para validar la máquina. NO se presenta como contenido de acreditación
  oficial. Marca `es_contenido_prueba: true` en todo lo generado en esta etapa.
- Formato de salida FIJO (un JSON Schema definido en specs) para que el Integrador no
  dependa de improvisación. Si el generador no cumple el schema, el Validador lo
  rechaza — no se integra basura.
- En producción, el `tema` se reemplaza por el corpus CNA que aporta AIEP; el resto de
  la máquina no cambia. El generador debe estar escrito para ese swap.

---

## 6. DOMINIO: Integrador de Gamificación

Toma la salida del Generador y la monta en el motor:
- Crea la ruta del rol, sus bloques/módulos/evaluaciones en la BD.
- Cablea las reglas de XP y medallas según los metadatos.
- Conecta la progresión: completar módulo → evento → XP → recalcular nivel;
  aprobar bloque → medalla (pasando por el invariante §4).
- Alimenta el ranking y el dashboard desde los eventos.

**El estado de gamificación se deriva de EVENTOS, no se guarda "a mano".** XP, nivel,
ranking y métricas del dashboard se calculan desde la tabla `EventoGamificacion`.
(Este es el patrón analítico correcto y es terreno del director.)

---

## 7. DOMINIO: Comportamientos a especificar en Fase 0 (defaults aprobados)

El arquitecto los formaliza como specs/ADRs. Estos son los defaults que el director
ya aprobó — el arquitecto los implementa salvo que encuentre una razón para escalar:

- **Reprobar evaluación final (<80%):** NO revela las respuestas correctas; ofrece
  reintento y **le recomienda de nuevo el contenido específico del módulo** (la
  cáscara/propuesta lo indica). Evita el "memorizo la respuesta".
- **Quiz formativo (dentro del módulo):** feedback INMEDIATO — verde si acierta;
  si falla, marca en rojo la elegida y en verde la correcta + explicación. Es
  aprendizaje, se juega distinto a la evaluación.
- **Evaluación final del bloque (el gate del 80%):** resultado al FINAL, no en vivo.
  Es la nota que respalda la acreditación; no se revela pregunta a pregunta.
- **Refresh / cierre a mitad del test:** **autosave por respuesta**; al volver, retoma
  donde iba. Nunca pierde progreso. Definir expiración del intento (default: el
  intento sigue abierto 24h; nivel 1 si hay que ajustar).
- **Reintentos:** número configurable (default 3); cada reintento puede barajar
  ítems del banco para que no sea la misma prueba idéntica.

El arquitecto DEBE además descubrir y especificar los casos borde que el director no
listó (ej: ¿qué pasa si se cae la conexión al enviar la evaluación? ¿doble envío?
¿empates en el ranking?). Los resuelve por nivel 1/2 y los documenta.

---

## 8. DOMINIO: Realtime — la sala 3D (TRACK DE RIESGO, va primero como spike)

La cáscara **simula** la sala localmente (avatares con `setInterval`, sin servidor,
sin nadie conectado de verdad). Lo que falta es la **mecánica multijugador real**.

**Es la única incógnita del proyecto.** Por eso: **spike primero**. Antes de
comprometer plazos, el Constructor Realtime levanta el servidor de sincronización
mínimo y el director lo prueba con **2-3 dispositivos reales conectados** (no
localhost solo). Si eso funciona, escalar de 3 a 50 es configuración, no
reconstrucción.

- **Stack:** servidor de estado en tiempo real (Colyseus sobre Node + WebSocket es el
  default; ADR si se cambia). Cliente sobre la sala que ya existe en la cáscara.
- **Alcance del slice:** sala social con avatares + chat con globos + presencia
  (quién está) + movimiento sincronizado. **Se ELIMINA el escape room** (lógica de
  juego compleja) — se deja para fase 2. Ambición controlada.
- **Gates propios del track:** dos clientes se ven moverse; un cliente que refresca
  se reconecta sin romper la sala; el chat no se pierde; la sala aguanta N clientes
  del slice sin desincronizarse.
- **Infra:** en el slice corre LOCAL + túnel (ngrok/Cloudflare) para conectar los 3
  dispositivos. NADA de AWS/GCP en esta etapa (costo ~$0). La nube es tema de
  producción, post-firma, en cuenta del cliente.

---

## 9. DOMINIO: Validador de Integridad (reemplaza el red team)

El activo a proteger no es un dato sensible, es la **verdad de la completitud** y la
**calidad del contenido generado**. El validador:

1. **Regresión de integridad:** set congelado de casos que verifican el invariante §4
   (aprobar da medalla; reprobar no da nada; XP solo por evento; nivel derivado).
2. **Canario:** un intento reprobado que JAMÁS debe dar medalla. Si la da, build
   bloqueado.
3. **Validación de contenido generado:** todo lo que produce el Generador pasa un
   check — cumple el JSON Schema, cada pregunta tiene exactamente una correcta, las
   explicaciones existen, el banco tiene el mínimo de ítems, no hay ítems duplicados.
   Contenido que no pasa NO se integra.
4. **Tests espejo transversales:** cada módulo que toca XP/medallas/nivel verifica el
   mismo invariante desde su lado — ningún constructor lo rompe sin que otro test lo
   delate.

---

## 10. DOMINIO: Integraciones

- **Microsoft Entra ID (SSO):** los usuarios de AIEP se loguean con su cuenta
  institucional Microsoft. Se implementa como **adapter conmutable mock↔real**: el
  código de negocio nunca sabe contra cuál corre.
  - **Slice:** arranca con un login dev **"actuar como"** los 3 roles (Profesor,
    Rector, Secretario) — solo dev, excluido del build de producción.
  - Cableado a Entra real cuando los flujos internos funcionen. NO bloquear el avance
    esperando el tenant.
- Otras integraciones (correo para avisos, emisor de Open Badges) = cada una un
  adapter conmutable. Mock primero, real después.

---

## 11. Stack (ADR-001 lo fija; estos son los defaults)

- **Backend:** Python + FastAPI (o Django+DRF si el arquitecto lo justifica por el
  panel admin — ADR). PostgreSQL. Coherente con el ecosistema del director.
- **Frontend:** la cáscara está en HTML/JS; el arquitecto decide si se migra a React
  o se evoluciona. La experiencia de `referencia-demo/` es la meta de UX.
- **Realtime:** Node + Colyseus (track aparte, §8).
- **Todo corre con `docker compose up`**: healthchecks, `depends_on` condicionados,
  `.env.example` que corta con instrucción clara si falta una variable. Arranque
  autosuficiente: espera dependencias → migra → carga seed (los 3 roles con contenido
  generado) → sirve. Sin pasos manuales.
- La API interactiva (`/docs`) con seed desde el día 1 = primera interfaz de testeo
  del director.

---

## 12. Fases de trabajo (heredado)

**Día 0 — auditoría (primera tarea, NADA se construye antes):** leer COMPLETO el
mockup de `referencia-demo/` y la propuesta de `docs-fuente/`. Entregar tabla:
(a) qué tenemos en la cáscara, (b) qué falta para hacerlo real, (c) ambigüedades que
serán supuestos. El director aprueba ANTES de draftear.

**Fase 0 — especificación (NO se delega, el director revisa):** specs por tandas de
~10 agrupadas por módulo, en orden de dependencias. Todo lo inferido = SUPUESTO
numerado (S-xx) en `SUPUESTOS.md`. Toda decisión estructural = ADR en
`docs/decisiones/`. Compuerta de cierre: reporte de consistencia (numeración sin
huecos, cero links rotos, terminología idéntica, invariantes espejo completos).

**Cimientos supervisados:** scaffold, contratos, motor de gamificación, auth —
runner `--once` POR TAREA → revisión de arquitecto contra specs → **verificación del
director en su máquina** → recién la siguiente.

**Modo fábrica:** día = worktrees paralelos en módulos independientes (ej: contenido
+ gamificación mientras el realtime avanza como spike), el director integrando.
Noche = runner sobre la cola; en la mañana leer log, revisar `[x]`, atacar `[!]`.

---

## 13. Definición de "LISTO" (el quality gate del slice)

El vertical slice está TERMINADO cuando, sin que el director toque nada por detrás:

1. Los **3 roles** se loguean (login dev "actuar como") y ven **rutas distintas** con
   contenido generado por rol.
2. Cada rol **completa un bloque de punta a punta**: módulos → quiz formativo con
   feedback → evaluación final al 80% → medalla legítima → XP → sube de nivel.
3. El invariante de integridad se sostiene: **el canario reprobado no da medalla**.
4. Los **3 conectados a la vez en la sala 3D**, viéndose moverse y chateando en
   tiempo real, desde 3 dispositivos.
5. El **dashboard** muestra datos REALES de los 3 completando el curso.

Mientras estos 5 no estén verdes de punta a punta, el slice NO está listo — aunque
"se vea bien". El "se ve bien" es la cáscara; esto es el sistema.

---

## 14. Gestión operativa (heredado)

- **Runner corriendo = arquitecto en silencio** (comparten presupuesto de sesión).
  Una tarea pesada por ventana de límites, lanzada temprano.
- **Commit + push tras cada bloque aprobado.** El remoto siempre refleja lo aprobado.
- **3 fallos de gates → BLOQUEO ACTIVO:** `LIMITE-ENCONTRADO.md` + plan de destrabe en
  `BITACORA.md` (re-especificar / cambiar enfoque / escalar). Nunca es un "resultado".
- **Fallo del AGENTE ≠ fallo del módulo:** límite de plan o error de invocación →
  abortar sin quemar intentos ni marcar bloqueo.
- **BITACORA.md como control de obra:** avance vs total, bloqueos con plan, decisiones
  pendientes, horas por módulo (dato para la propuesta comercial futura).
- **UI en paralelo, nunca al final:** módulo funcional sin UI operable NO está HECHO.
  `design-system.md` antes de la primera pantalla (tokens de la cáscara ya definen la
  identidad visual: vino tinta, carmín, oro, menta; Bricolage Grotesque + Inter +
  JetBrains Mono).

---

## 15. Regla final

El documento fuente manda. El director decide lo irreversible. Los agentes construyen
contra specs y nunca son jueces cuando existe un test. Ninguna duda frena el trabajo:
default y adelante. Y el norte de todo: **que cuando el sistema diga "cumplió", sea
verdad** — porque eso es lo que AIEP le va a mostrar a la CNA.
