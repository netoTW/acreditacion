# Plan de diseño — capa de gamificación

> **Fase 0 de los juegos.** Aprobado por el director el 2026-08-10, con estos ajustes
> ya incorporados: M2 acortado a 2 minutos, regla del tope de ranking ratificada, y
> memoria de pares descartada. **M1 Calibre está construido.**

---

## 0. El principio, en una frase

**Tres motores alimentados por las 15 unidades de contenido que ya existen.** No una
colección de juegos: tres mecánicas reutilizables que funcionan con cualquier
`(dimensión, nivel)` sin escribir contenido nuevo.

Un juego nuevo en el futuro debería ser **un motor más**, no un juego por dimensión.

---

## 1. Con qué se juega (material ya disponible)

Verificado contra la base:

| | Por unidad (N1 / N2 / N3) | Total |
|---|---|---|
| Módulos | 2 / 3 / 4 | **45** |
| Ítems de quiz formativo | 12 / 16 / 20 | **240** |
| Ítems de banco de evaluación | 18 / 24 / 30 | **360** |
| Explicaciones (una por alternativa) | — | **1.440** |

Cada ítem trae **enunciado, 4 alternativas, cuál es la correcta y por qué cada una de las
otras tres no lo es**. Ese último dato es el más valioso para diseñar: las alternativas
incorrectas están escritas para *sonar bien*. Toda la capa de juego se apoya en eso.

**Ya existe y no se toca:** el **quiz formativo** (M0) — feedback inmediato, racha y
multiplicador, uno por módulo. Es la práctica base, sin riesgo.

---

## 2. Las tres mecánicas

### Decisión de diseño previa: los juegos solitarios NO llevan reloj

El reloj es la forma más fácil de fabricar tensión y la más pobre: convierte todo en
velocidad de lectura y castiga a quien lee despacio o usa lector de pantalla.

**M1 y M2 no tienen temporizador.** La tensión viene de decisiones que el jugador toma
sabiendo lo que arriesga. Solo **M3** usa tiempo, porque ahí el reloj no es adorno: es el
mecanismo de comparación entre personas que juegan a la vez.

---

### M1 · **Calibre** — nivel módulo

> *No se juega a saber la respuesta. Se juega a saber cuánto sabes.*

**El loop.** Terminas de leer un módulo. 5 preguntas. En cada una eliges alternativa **y
declaras cuánto te la juegas**:

| | Aciertas | Fallas |
|---|---|---|
| **Seguro** | +60 | **−40** |
| **Creo que sí** | +25 | 0 |

El marcador **puede bajar**. Al final, si todos tus "Seguro" fueron correctos: **+50 de
bonificación por calibrado**.

**Qué decide el jugador:** cuánto se expone. La pregunta interesante deja de ser "¿cuál
es?" y pasa a ser "¿me la juego?".

**Por qué engancha.** Produce una emoción que un quiz normal no produce: **el
arrepentimiento**. Decir "Seguro" y fallar duele de una forma específica y memorable, y
esa es exactamente la lección. Además es la única mecánica donde el marcador retrocede a la
vista, lo que crea tensión sin necesidad de reloj.

**Por qué encaja con este contenido.** Cada distractor del banco está escrito para parecer
razonable. Calibre castiga justamente la trampa que el contenido enseña a evitar: confundir
*suena bien* con *corresponde*. Y la calibración —saber qué no sabes— es literalmente lo que
un proceso de autoevaluación le pide a una institución.

**Se alimenta de:** **solo los ítems del quiz formativo del módulo** (4–6 por módulo).

> **Corrección al plan original.** Había escrito «quiz del módulo + banco del bloque», y
> está mal: Calibre muestra la respuesta correcta para dar feedback, y servir ítems del
> banco con su correcta **filtraría la evaluación**. El banco no sale del servidor con su
> respuesta, nunca. Con 4–6 ítems por módulo alcanza para una partida de 60–90 s.

**Duración:** 60–90 s. **XP máximo:** ~250. **Contenido nuevo:** ninguno.

---

### M2 · **Ascenso** — integrador de bloque, antes del examen · **2 min**

> *Guardas lo que llevas, o subes un tramo más.*

**El loop.** Se desbloquea con todos los módulos vistos, justo antes de la evaluación.
Tres tramos por **dificultad del ítem**, que es una escalera cognitiva real:

| Tramo | Qué pide | De dónde sale |
|---|---|---|
| 1 · Reconocer | qué es cada cosa | ítems de definición |
| 2 · Distinguir | cuál corresponde y cuál no | ítems de emparejamiento |
| 3 · Aplicar | qué hacer ante un caso | ítems de escenario |

**2 vidas.** Cada error cuesta una. **Tres preguntas por tramo, nueve en total.**

> Ajuste del director: el tope es **2 minutos**. Con nueve preguntas y dos decisiones de
> guardar-o-subir la partida entra cómoda, y **no hay reloj**, así que el límite es de
> diseño y no presión sobre el jugador. Se bajó de 3 vidas a 2 justamente porque el juego
> es más corto: con nueve preguntas, tres vidas casi no se pierden y la tensión se diluye.

Al cerrar cada tramo, **la decisión**:

- **Guardar** → te llevas el pozo y termina la partida.
- **Subir** → el pozo se multiplica **×1,6** y sigues. Si te quedas sin vidas, **pierdes
  todo lo no guardado**.

Terminar el tramo 3 sin perder ninguna vida: **×2**.

**Qué decide el jugador:** cuándo parar. Y la decisión se vuelve más difícil justo cuando
el pozo ya se siente propio.

**Por qué engancha.** Es *press your luck*, y funciona por aversión a la pérdida: perder un
pozo que ya sientes tuyo pesa más que ganar uno nuevo. La tensión escala sola —en el tramo 3,
con el pozo multiplicado dos veces y una vida, cada pregunta se siente distinta— sin que
haya un reloj corriendo.

**Por qué encaja.** La escalera reconocer → distinguir → aplicar es la progresión que el
contenido ya tiene incorporada. Y funciona igual en las 15 unidades, porque **todos** los
bancos tienen ítems de los tres tipos, sea el bloque de nivel 1 o de nivel 3.

**Se alimenta de:** banco completo del bloque (18–30 ítems), agrupado por dificultad.
**Duración:** ~2 min. **XP máximo:** ~700.

---

### M3 · **Comité relámpago** — social, en la Plaza

> *Un comité que sesiona contra el reloj. Nadie queda fuera.*

**El loop.** 2 a 8 personas en la sala. Rondas simultáneas de 15 s sobre la dimensión que
elija el anfitrión. Tabla en vivo entre rondas.

Tres capas, y las tres importan:

1. **Puntos que decaen con el tiempo.** Responder rápido vale más. Es el hook de Kahoot y
   el único lugar donde el reloj se justifica.
2. **Turno de palabra.** Quien va último en la tabla recibe **×1,5** en la ronda siguiente.
   Temáticamente: en un comité, el que no ha hablado toma la palabra. Mecánicamente: es
   *rubber-banding*, y resuelve el problema número uno de los quiz multijugador — que el
   rezagado se desconecta a la tercera ronda.
3. **Consenso del comité.** Una barra compartida sube cuando el **70% o más** del grupo
   acierta la ronda. Llenarla da bonificación **a todos**. Da una razón real para querer que
   al de al lado le vaya bien.

**Qué decide el jugador:** cuánto arriesgar en velocidad, y si juega para su posición o para
el consenso. Las dos cosas compiten.

**Por qué encaja.** Reemplaza el escape room que se cortó (E-02) **reusando el motor de
preguntas de M1**, no construyendo un juego aparte (S-42). Y la metáfora del comité es la de
la fuente: el proceso avanza cuando el grupo avanza.

**Se alimenta de:** banco de la dimensión elegida. **Duración:** 5–8 min. **XP máximo:** ~400.

---

## 3. Cómo se reparten en el recorrido

| Momento | Motor | Duración | Paga XP |
|---|---|---|---|
| Después de leer un módulo | **M0 quiz** y **M1 Calibre** | 60–90 s | tope diario **compartido** por módulo |
| Con todos los módulos vistos, antes del examen | **M2 Ascenso** | ~2 min | 1 vez al día por bloque |
| En la Plaza, cuando hay gente | **M3 Comité** | 5–8 min | 1 vez al día por sala |

**La variedad se resuelve por elección, no por imposición.** En cada módulo se ofrecen los
dos formatos solitarios.

**Cómo se paga:** cada juego paga una vez al día, pero **el tope diario es del módulo**, no
del juego: jugar los dos rinde como máximo lo mismo que exprimir uno. Así probar ambos no se
castiga —queríamos variedad— y tampoco se convierte en doble cobro.

**Cuántas partidas juega una persona en todo el recorrido:**

| Cargo | Módulos | Partidas de módulo | Ascensos | Total con premio |
|---|---|---|---|---|
| Rector | 17 | 17 | 5 | **22** |
| Vicerrector · Dir. de Carrera · Coord. de Calidad | 15 | 15 | 5 | **20** |
| Docente · Administrativo | 12 | 12 | 5 | **17** |

Más la Plaza, que es libre. Práctica sin pago: ilimitada.

---

## 4. El invariante — sin excepciones

- **Todo el XP de juego es `lúdico`.** Nunca `acreditable`.
- **Ningún juego otorga medalla.** La medalla solo nace de la evaluación aprobada al 80%,
  y la base de datos lo impone: `insignia.intento_evaluacion_id` es `NOT NULL` y hay un
  trigger que exige que ese intento esté aprobado (ADR-005).
- **Ningún juego mueve el escalón.** El escalón deriva solo de XP acreditable.
- **El puntaje lo calcula el servidor**, siempre, desde las respuestas y su orden. El
  cliente manda qué eligió; nada más. Ya funciona así en el quiz.
- **Tope por juego, por día**, configurable por mecánica (S-05).

### Regla ratificada por el director

Si los tres motores pagan sin límite, el XP de juego termina **superando al acreditable** y
el ranking pasa a medir cuánto juegas, no cuánto avanzas. Propongo una regla simple:

> **Jugar puede como mucho duplicar tu posición, nunca reemplazar el recorrido.**
> El ranking suma XP lúdico **hasta un tope igual a tu XP acreditable**.

Quien no avanza en su ruta no escala jugando. Quien avanza, es premiado por jugar.

Vigente en la base desde la migración 005 y verificado en el sistema corriendo: un
colaborador con 20 XP lúdico y 0 acreditable queda con **posición de ranking 0**.

---

## 5. Reutilización — por qué son tres motores y no treinta juegos

| Motor | Qué consume | Sirve para las 15 unidades | Contenido nuevo |
|---|---|---|---|
| M0 quiz *(ya existe)* | ítems de quiz del módulo | sí | ninguno |
| M1 Calibre | cualquier ítem con 4 alternativas | sí | ninguno |
| M2 Ascenso | banco del bloque agrupado por dificultad | sí | ninguno |
| M3 Comité | banco de la dimensión | sí | ninguno |

Los tres motores nuevos comparten **un mismo servicio**: servir ítems y corregir respuestas
en el servidor. Lo que cambia entre ellos es la capa de decisión —apostar, guardar o subir,
competir— no el manejo del contenido.

Agregar una sexta dimensión, un cargo nuevo o el corpus real de AIEP **no toca ningún
juego**: los motores leen lo que haya.

---

## 6. Prerrequisitos técnicos

Dos hallazgos al revisar la base para armar este plan:

1. ~~**`dificultad` no se persiste.**~~ **Resuelto** (migración 004): la columna existe en
   `item_evaluacion` y en `item_quiz_formativo`, el integrador la guarda, y los 360 ítems del
   banco quedaron con su dificultad repartida en los tres tramos que M2 necesita.
2. **`criterio` tampoco existe como tabla**, aunque el Generador emite los códigos. **Ninguna
   de estas tres mecánicas lo necesita**, así que no se construye ahora; queda anotado por si
   más adelante se quiere agrupar por criterio.

---

## 7. Lo que NO se construye, y por qué

- **Escape room.** Cortado en E-02, sigue cortado.
- **Memoria de pares** (la de la cáscara). Recomiendo **no construirla**. Su loop real es
  recordar dónde estaba una carta, no entender el contenido: casi no hay decisión y lo que
  entrena es memoria espacial. En un sistema cuyo valor es el juicio profesional, ocupa un
  motor entero para enseñar poco. Si más adelante se quiere una mecánica de reconocimiento,
  M1 ya la cubre con mejor tensión.
- **Un juego por dimensión.** Sería contenido disfrazado de mecánica y multiplicaría por
  cinco el trabajo de mantención.

---

## 8. Riesgos y cómo se manejan

| Riesgo | Manejo |
|---|---|
| La presión de tiempo excluye a quien lee despacio | M1 y M2 **no tienen reloj**. Solo M3, que es competitivo por diseño, y ahí el modo sin reloj queda disponible con el mismo XP máximo — lo que se pierde es el bonus de velocidad |
| Repetición de ítems entre partidas | Se priorizan ítems no vistos y nunca se repite dentro de una misma partida. Con 18–30 por banco y 4–5 por partida, alcanza |
| Los ítems del quiz y del banco se parecen | Ya anotado en `IDEAS-PULIDO.md`: en producción el Generador debe darles ángulos distintos |
| El juego canibaliza el estudio | El tope de ranking de §4 y que el XP lúdico no mueva el escalón lo vuelven imposible por diseño |
| M3 depende de que haya gente conectada | Cae con gracia: con una sola persona se juega en modo solitario contra la tabla histórica de la sala |

---

## 9. Orden de construcción propuesto

1. ~~Prerrequisito: persistir `dificultad`.~~ **Hecho** (migración 004).
2. ~~**M1 Calibre.**~~ **Hecho y navegable.**
3. **M2 Ascenso** — la pieza con más tensión; cierra el recorrido del bloque. **Siguiente.**
4. **M3 Comité** — el último, porque depende del realtime y de que M1 exista.

Cada uno se muestra navegable antes de pasar al siguiente, como venimos trabajando.
