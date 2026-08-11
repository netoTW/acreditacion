# Cambios AIEP: de 6 cargos a 3 roles con distribución de impacto

**Estado:** análisis y opciones. **No hay código escrito.** Espera decisión del director.
**Fuente de verdad:** `docs-fuente/Impacto en dimensiones por nivel (roles).xlsx`.

---

## 0. Lo que dice el archivo (verificado celda por celda)

El archivo **confirma el resumen del prompt sin una sola diferencia**. Las tres columnas
suman exactamente 1.

| Dimensión CNA | N1 Alta Dirección | N2 Liderazgo intermedio | N3 Administrativo y apoyo |
|---|---|---|---|
| D1. Gestión estratégica y recursos | **30 % 🔴** | 10 % | 15 % |
| D2. Docencia y resultados de formación | 15 % | **35 % 🔴** | **25 % 🔴** |
| D3. Aseguramiento interno de la calidad | **30 % 🔴** | **25 % 🔴** | **35 % 🔴** |
| D4. Vinculación con el medio | 15 % | 15 % | 20 % |
| D5. Investigación, creación e innovación | 10 % | 15 % | 5 % |
| | 100 % | 100 % | 100 % |

Tres lecturas del dato antes de proponer nada:

1. **D3 Aseguramiento es crítica para los tres roles** y nunca baja de 25 %. Es la única
   dimensión así. El sistema debería tratarla como columna vertebral, no como una más.
2. **D5 Investigación nunca es crítica** y en N3 vale 5 %. Es la dimensión en riesgo de
   volverse decorativa — y, casualmente, la que menos material tiene hoy.
3. **Las 🔴 son exactamente las dos dimensiones de mayor % en cada rol.** En los tres.
   Sin excepción.

El punto 3 importa mucho y lo desarrollo enseguida.

---

## 1. El hallazgo que ordena todo el resto

Las tres marcas del modelo —**el % alto**, **la 🔴**, y el **nivel de estándar CNA** que ya
usamos— caen sobre las mismas casillas. Si se deriva el nivel desde el % con un corte
simple (≥ 25 % → nivel 3; 15–24 % → nivel 2; ≤ 10 % → nivel 1), sale esta matriz:

| | Gestión | Docencia | Aseguramiento | Vinculación | Investigación |
|---|---|---|---|---|---|
| **N1 Alta Dirección** | 30 % → **N3** 🔴 | 15 % → N2 | 30 % → **N3** 🔴 | 15 % → N2 | 10 % → N1 |
| **N2 Liderazgo** | 10 % → N1 | 35 % → **N3** 🔴 | 25 % → **N3** 🔴 | 15 % → N2 | 15 % → N2 |
| **N3 Administrativo** | 15 % → N2 | 25 % → **N3** 🔴 | 35 % → **N3** 🔴 | 20 % → N2 | 5 % → N1 |

**Ruta crítica ≡ nivel de estándar 3 ≡ las dos dimensiones de mayor peso.** Las tres cosas
son la misma casilla, en los tres roles.

Dos consecuencias prácticas:

- **El modelo nuevo no reemplaza `cargo × dimensión`: lo llena mejor.** La matriz que ya
  existe en la base tiene exactamente esa granularidad —una fila por (cargo, dimensión)—
  y lo único que le falta son dos columnas. No hay que rediseñar el modelo de datos.
- **La 🔴, como *dato*, no agrega información**: es deducible del %. Por lo tanto su valor
  tiene que ser **mecánico o visual** — tiene que *hacer* algo que el % no hace. Eso es
  justamente lo que hay que decidir en la sección (b).

Y un beneficio inesperado, que reviso más abajo en (d): esa matriz derivada usa **9 de las
15 unidades de contenido ya generadas**. Con esta lectura, **no hay que regenerar nada**.

---

## (a) Qué debería controlar la «distribución %»

Antes de las opciones, una restricción que hay que decir en voz alta:

> **El cambio confirmado n.º 2 —«2 quiz + 1 juego + evaluación final» por dimensión— ya
> decidió que la estructura es idéntica en las cinco dimensiones.** Por lo tanto el % **no
> puede** controlar «cuántos módulos recibe el rol de cada dimensión»: esa cuenta ya está
> fija en 2 + 1 + 1. Si el % controlara el número de piezas, las cinco dimensiones dejarían
> de tener la misma forma y el cambio n.º 2 se cae.

Eso deja tres cosas que el % sí puede controlar sin contradecir nada.

### Opción A — El % es un **ponderador de puntaje**

La estructura y el contenido son idénticos para todos. Lo que cambia es cuánto aporta cada
dimensión a tu avance, tu XP acreditable y tu posición en el ranking. Terminar Aseguramiento
siendo N3 vale 35 % de tu ruta; terminar Investigación vale 5 %.

- **A favor:** exacto, sin redondeos. Cero contenido nuevo. Es la lectura literal de la
  palabra «impacto». Barata: es un multiplicador en una vista.
- **En contra:** **es invisible mientras juegas** — solo lo notas al final, en un número.
  Y produce una conversación incómoda: «hice el 100 % de Investigación y me sumó 5 %».
  Convierte una dimensión en trámite, que es lo contrario de lo que busca la ruta.

### Opción B — El % es **profundidad dentro de la estructura fija**

Las cinco dimensiones tienen las mismas cuatro piezas (2 quiz + 1 juego + evaluación), pero
el % define **cuán largas y exigentes** son: cuántos conceptos cubre el microlearning,
cuántos ítems trae cada quiz, cuántos ítems trae la evaluación final, y la mezcla de
dificultad.

Una curva concreta que funciona con estos números — ítems por quiz = `3 + 12 × %`, acotada
entre 3 y 7:

| % del rol | Ítems por quiz | Ítems evaluación final |
|---|---|---|
| 35 % | 7 | 8 |
| 30 % | 7 | 7 |
| 25 % | 6 | 6 |
| 20 % | 5 | 5 |
| 15 % | 5 | 5 |
| 10 % | 4 | 4 |
| 5 % | **3** (piso) | **4** (piso) |

- **A favor:** **se siente al jugarlo.** Un bloque del 35 % es visiblemente más denso que
  uno del 5 %, sin que ninguno desaparezca. El piso garantiza que Investigación al 5 %
  siga siendo un bloque real con su medalla. Y el Generador ya sabe dosificar por nivel:
  esto es cambiarle la regla de tamaño, no reescribirlo.
- **En contra:** hay que fijar la curva y el piso, y defenderlos. El redondeo obliga a
  decidir casos borde. Cambia la regla de generación (S-32) y las pruebas que la cubren.

### Opción C — El % es **orden y presupuesto de tiempo declarado**

El % ordena la ruta (primero lo que más pesa) y se muestra como presupuesto: «Aseguramiento
· 35 % de tu ruta · ≈ 45 min». Estructura y profundidad idénticas.

- **A favor:** la más barata de todas; el orden de ruta ya existe en la base. Honesta y
  visible en Mi Ruta desde el primer día.
- **En contra:** el % termina siendo casi solo narrativo. Si dos personas hacen lo mismo y
  obtienen lo mismo, el modelo de impacto no está *haciendo* nada.

### Recomendación: **B + A**, en ese orden de prioridad

**El % define la profundidad (B) y además pondera el avance y el ranking (A).** Es la
lectura honesta de «impacto»: la dimensión que más le importa a tu rol te ocupa más tiempo
**y** cuenta más. B sola es visible pero no tiene consecuencia; A sola tiene consecuencia
pero es invisible. Juntas, lo que ves es lo que pesa.

Se puede entregar por partes: **B primero** (se nota de inmediato en la pantalla) y A
después, cuando exista la pantalla de ranking, que aún no está construida.

---

## (b) Qué debería significar mecánicamente la «ruta crítica»

Recordando el hallazgo: la 🔴 **no agrega información**, así que tiene que agregar
consecuencia. Cinco candidatas, de la que descartaría a la que recomiendo.

### B-i — Obligatoria vs. opcional · **la descartaría**

Las críticas son obligatorias; las demás, opcionales o «recomendadas».

Rompe frontalmente el principio que sostiene la ruta actual y que viene de la fuente de
AIEP: **todo cargo toca las cinco dimensiones, la acreditación es de todos.** Decirle al
N3 que Investigación es opcional es exactamente el mensaje que la ruta intenta desarmar.
Además dejaría a la mayoría con 3 medallas de 5 y rompería la graduación.

### B-ii — Umbral de aprobación más alto

Las críticas exigen más que el 80 % para aprobar; las no críticas, menos.

Técnicamente el umbral **ya existe** como columna (`evaluacion.umbral_aprobacion`), pero hoy
vive pegado al **bloque de contenido**, que es compartido entre roles porque el contenido se
genera una sola vez. Para que varíe por rol habría que moverlo a la ruta de cada persona.
Es un cambio acotado y limpio, pero tiene un costo de mensaje: bajar el umbral en las no
críticas debilita el relato de la medalla, que hoy es nítido —**80 % o no hay medalla**—.
Si se usa, usarlo **solo hacia arriba** (crítica = 85–90 %, el resto se queda en 80 %).

### B-iii — Prioridad de desbloqueo y orden de la ruta

Las críticas abren primero y encabezan la ruta; las demás se abren después.

Es el sentido original de «ruta crítica» y es casi gratis: la ruta ya se ordena por exigencia
descendente, o sea que **ya se comporta así**; solo hay que nombrarlo y mostrarlo. Es
suave: no cambia lo que se te exige, solo cuándo.

### B-iv — Peso institucional, no personal

La 🔴 define qué dimensiones cuentan para la lectura de la **unidad** —el panel institucional
y la agregación de rezagados de E-03— sin gatillar nada en el recorrido individual.

Es la lectura más fiel al propósito real (dónde está el riesgo de la institución) y no
castiga a nadie. Su contra: **invisible para quien juega.**

### B-v — Jerarquía de medalla · **la recomendada, junto con B-iii**

Las dimensiones críticas otorgan una **medalla de rango superior**; las no críticas, la
medalla estándar. La tabla de medallas ya tiene los rangos (`mini / silver / gold / master`)
y hoy están sin usar: crítica → `gold`, no crítica → `silver`.

- Tiene consecuencia real y **visible desde el minuto uno**, sin quitarle a nadie su
  obligación de recorrer las cinco.
- Usa una columna que ya existe: costo de esquema **cero**.
- Le da al ranking y al perfil algo que mostrar además de un número.
- Y le dice a la persona lo que el modelo quiere decirle: *«en esta dimensión, tu rol es
  donde más se juega la acreditación»*.

**Recomendación: B-v + B-iii, y B-iv cuando exista el panel institucional.** Es decir: las
críticas **abren primero, encabezan la ruta, y su medalla es de otro rango**. Sin umbrales
distintos y sin dimensiones opcionales — esas dos tocan la integridad y el mensaje.

---

## (c) Relación con el modelo cargo × dimensión que ya existe

### Se conserva (la mayor parte)

- **El corazón de ADR-003**: el contenido se genera **una vez por (dimensión, nivel)**. Las
  15 unidades siguen siendo la unidad de generación.
- **La tabla de la matriz** `exigencia_cargo_dimension`, con grano `(cargo, dimensión)` —
  que es **exactamente** el grano del modelo nuevo.
- Todo el motor de integridad: medalla anclada al intento aprobado, evento append-only,
  XP dual acreditable/lúdico, tope de ranking, aislamiento I-10. **Nada de esto se toca.**
- Las 5 dimensiones, los 13 hitos, comités y unidades.

### Se reemplaza

- **6 cargos → 3 roles.** Son filas de datos, no código: `RECTOR`, `VICERRECTOR`,
  `DIR_CARRERA`, `DOCENTE`, `COORD_CALIDAD`, `ADMINISTRATIVO` salen; entran `N1`, `N2`, `N3`.
- **La matriz de niveles escrita a mano** deja de escribirse a mano: **se deriva del %**
  con el corte de la sección 1.
- **La regla de cantidad de módulos** (hoy: 2 módulos en nivel 1, 3 en nivel 2, 4 en nivel 3)
  → estructura fija de **2 quiz + 1 juego + evaluación final**. Esto es el cambio n.º 3.
- **La regla de orden de ruta** (hoy por exigencia descendente) → por % descendente, que da
  casi el mismo resultado.

### Se agrega

- Dos columnas en la matriz que ya existe: `distribucion_pct` y `es_ruta_critica`, más una
  verificación de que los % de cada rol **sumen 1** — al nivel de la base, como todo lo
  demás de integridad, no en el servicio.
- **El juego propio de cada dimensión** (cambio n.º 4): una pieza nueva por dimensión.
  Es, con diferencia, lo más caro de todo el paquete. Detalle en (d).

### La pregunta grande que esto abre

¿**Sobrevive `nivel_estandar`**, o el % lo reemplaza?

- **Si sobrevive** (derivado del %, como propongo): las 15 unidades ya generadas se reusan;
  la matriz nueva consume 9 de ellas y **no hay que regenerar contenido**. El argumento del
  anidamiento CNA —«el nivel 3 incluye al 2 y el 2 al 1»— se mantiene intacto.
- **Si se elimina** y hay una sola unidad por dimensión: el modelo se simplifica a 5
  unidades, pero se bota contenido ya validado y se pierde el fundamento de ADR-003.

**Recomiendo que sobreviva.** Es la diferencia entre ajustar y rehacer.

---

## (d) Impacto en lo construido y plan de ajuste

### Qué se salva intacto

El motor de integridad y su canario, el XP dual, el tope de ranking, el aislamiento por
identidad, el arranque en un comando, las 15 unidades de contenido generado y validado, y
las pantallas de Ingreso, Mi Ruta, Bloque, Módulo y Evaluación final en su estructura.
**La ruta sigue teniendo 5 bloques**, uno por dimensión: la pantalla principal no cambia de
forma.

### Qué hay que tocar, y cuánto

| Pieza | Impacto | Tamaño |
|---|---|---|
| Datos de semilla (cargos, matriz, colaboradores) | reescritura de filas | chico |
| Esquema: 2 columnas + verificación de suma | migración nueva | chico |
| Generador: estructura fija + profundidad por % | cambia la regla de tamaño | **medio** |
| Validador: reglas que cuentan módulos | ajuste de reglas | chico |
| Pantallas Mi Ruta y Bloque: mostrar % y 🔴 | añadidos visuales | chico |
| Medalla por rango (B-v) | usa columna existente | chico |
| Ponderación del ranking (opción A) | cambia la vista de estado | medio |
| **Los 5 juegos por dimensión** | diseño + contenido nuevo | **grande** |
| Pruebas que fijan la matriz y los conteos | actualización | medio |

### El problema con la Mesa de comité

**La Mesa no puede ser el juego de ninguna dimensión.** Su mecánica *es* clasificar entre
las cinco dimensiones: encerrada en una sola, se queda sin eje y deja de existir. Hay dos
salidas honestas:

1. **La Mesa sobrevive como juego de la ruta completa** —transversal, en el menú lateral,
   como está hoy— y las cinco dimensiones reciben además su juego propio. Es lo que
   recomiendo: ya funciona, ya te gustó, y no compite con nadie.
2. Se le cambia el eje de clasificación (por ejemplo, clasificar dentro de una dimensión) y
   se convierte en el juego de una sola. Cuesta contenido nuevo y pierde lo que la hace
   buena.

### Los 5 juegos: dónde estamos de verdad

De las mecánicas ya diseñadas, **solo una encaja directamente en una dimensión**:

| Dimensión | Mecánica candidata | Contenido nuevo | Costo |
|---|---|---|---|
| D3 Aseguramiento | **Línea de tiempo (B1)** — ordenar los 13 hitos del ciclo | ninguno: los 13 hitos ya están en la base con su orden | **barata** |
| D2 Docencia | secuenciar el ciclo de un resultado de aprendizaje | secuencias nuevas | media |
| D4 Vinculación | conectar actor externo ↔ acción institucional | catálogo de actores | media |
| D1 Gestión | simulación de asignación de recursos (B4 acotado) | escenarios, indicadores, consecuencias | **cara** |
| D5 Investigación | sin candidata clara | **todo** | **cara + material escaso** |

Traducido: **el cambio n.º 4 es un encargo de contenido, no de código.** Se puede empezar
por D3, que es gratis, pero D1 y D5 requieren material que hoy no existe en ninguna forma.

### Plan de ajuste, ordenado por dependencias

- **Paso 0 — tus decisiones (a), (b) y (c).** Todo lo demás cuelga de aquí. Nada avanza antes.
- **Paso 1 — migración de esquema:** roles, `distribucion_pct`, `es_ruta_critica`, suma = 1
  verificada en la base. Es la base de todo lo que sigue.
- **Paso 2 — semilla nueva:** 3 roles, matriz derivada del %, los tres colaboradores de
  prueba reasignados, rutas regeneradas. Al terminar este paso **ya se puede entrar y ver
  las tres rutas nuevas**, aunque el contenido siga con la estructura vieja.
- **Paso 3 — Generador y validador:** estructura fija 2 quiz + 1 juego + evaluación, y
  profundidad por % si eliges la opción B. Regenerar contenido y revalidar.
- **Paso 4 — pantallas:** Mi Ruta y Bloque muestran el %, la marca de ruta crítica y el rango
  de medalla. Aquí es donde **tú puedes ver y tocar el modelo nuevo completo.**
- **Paso 5 — juegos por dimensión, de a uno.** Empezando por D3 Línea de tiempo, que no
  cuesta contenido. Los demás según decidas priorizarlos.
- **Paso 6 — ponderación del ranking** (solo si eliges la opción A), junto con la pantalla
  de ranking, que todavía no existe.

Del paso 1 al 4 el sistema queda coherente y navegable. El paso 5 es largo por naturaleza y
avanza en paralelo sin bloquear nada.

---

## Tres cosas que necesito que aclares (no bloquean el análisis)

1. **¿Dónde queda el Docente?** Los tres roles se llaman Alta Dirección, Liderazgo intermedio
   y Administrativo y apoyo. Ninguno nombra a la docencia, pero Docencia es ruta crítica en
   N2 y N3. Hoy el colaborador de prueba «Pablo» es Docente. ¿El docente de aula entra en N3,
   entra en N2, o el modelo asume que se le asigna según su cargo administrativo?
2. **¿El corte % → nivel es tuyo o mío?** Propuse ≥ 25 → 3, 15–24 → 2, ≤ 10 → 1, que calza
   perfecto con las 🔴. Si AIEP tiene su propia lectura del nivel CNA por rol, mando esa y
   descarto la derivación.
3. **«1 juego» por dimensión: ¿juego distinto o mecánica distinta?** No es lo mismo cinco
   mecánicas nuevas que una mecánica reutilizada con contenido distinto por dimensión. La
   primera lectura es cinco veces más cara y es la que asumí arriba.
