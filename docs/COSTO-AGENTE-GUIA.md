# Costo de operación del agente «Guía de Calidad»

**Estado: NO CONSTRUIDO.** Este documento es una estimación previa al diseño, no
una medición. Sirve para dimensionar y para poner un tope, no para facturar.

Lo que hay acá se divide en dos: lo **medido** en la base de datos del proyecto, y
lo **supuesto**, que el director debe confirmar antes de que estos números valgan.

---

## 0. Qué existe hoy

Busqué en todo el repositorio antes de estimar:

| Dónde | Qué encontré |
|---|---|
| Código (`api/`, `web/`) | Ninguna llamada a un modelo de lenguaje. `requirements.txt` no tiene SDK de nadie |
| Endpoints | 49, ninguno de conversación |
| Esquema | 13 migraciones, ninguna tabla de mensajes ni de hilos |
| Cáscara original | Hay un `chat-card`, pero es el **chat social de la Plaza** entre avatares |
| `docs-fuente/` (PPT, brief, Excel) | Ninguna mención a un asistente |
| Specs, ADRs, SUPUESTOS, tareas | Nada |

Las coincidencias con «claude» son `CLAUDE.md`, el archivo de constitución del
proyecto, y el prompt de arranque. No hay integración de producto.

**Por lo tanto no existe consumo real que medir.** Todo consumo por consulta de
este documento es supuesto.

---

## 1. Lo medido: el corpus que el agente tendría que consultar

Medido en la base con el contenido de prueba actual, que tiene el mismo tamaño y
forma que tendría el contenido real de AIEP.

| Contenido | Filas | Caracteres |
|---|---:|---:|
| Microlearning (cuerpo de los módulos) | 30 | 67.453 |
| Desafíos aplicados y sus decisiones | 60 | 48.663 |
| Contenido de los juegos (casos, actores, producciones) | 42 | 10.265 |
| Hitos del proceso | 13 | 1.319 |
| Dimensiones | 5 | 189 |
| **Corpus consultable** | | **127.889** |

**≈ 34.500 tokens.** El corpus completo que el agente necesitaría cabe en una sola
llamada, cómodamente.

### Lo que NO puede entrar al contexto, nunca

| Contenido | Filas | Caracteres | ≈ tokens |
|---|---:|---:|---:|
| Banco de evaluación (con `indice_correcta`) | 360 | 292.073 | 78.900 |
| Ítems de quiz formativo (con su respuesta) | 150 | 115.435 | 31.200 |

Son **110.000 tokens de preguntas con su respuesta correcta marcada**. Meterlos en
el contexto convertiría al agente en la filtración más grande del sistema: un
usuario le pregunta «¿cuál es la respuesta de la pregunta sobre trazabilidad?» y
el agente se la da. Eso rompe el invariante central del proyecto —que la medalla
signifique algo— y lo rompe de la forma más difícil de detectar.

**Es la restricción de diseño número uno del agente, y además abarata el costo:**
el corpus que sí puede ver es tres veces más chico que el que no.

---

## 2. Lo supuesto: qué consume una consulta

Cada línea es un supuesto a confirmar. Los marco con su peso en el resultado.

| Componente | Tokens | Confianza |
|---|---:|---|
| Prompt de sistema (rol, tono, prohibiciones, formato) | 700 | media · se puede medir al escribirlo |
| Contexto inyectado — **corpus completo** | 34.565 | **medido** |
| Contexto inyectado — **solo el bloque pertinente** (RAG) | 1.623 | **medido** (promedio real de un bloque + estructura) |
| Historial de la conversación (≈3 turnos) | 600 | baja · depende de cuánto se conserve |
| Pregunta del usuario | 40 | media |
| Respuesta típica (salida) | 350 | baja · **es el supuesto más frágil** |

Conversión usada: **3,7 caracteres por token** en español. Es un promedio
razonable; el rango real va de 3,5 a 4,0 y mueve el resultado ±7%.

### Precios asumidos

**Confírmalos en la página de precios de Anthropic antes de usarlos en la
propuesta** — cambian, y mi información puede estar desactualizada.

| Modelo | Entrada (US$/millón) | Salida (US$/millón) | Lectura de caché |
|---|---:|---:|---:|
| Claude Sonnet | 3,00 | 15,00 | 0,30 |
| Claude Haiku | 1,00 | 5,00 | 0,10 |

---

## 3. Costo por consulta, en cuatro configuraciones

| # | Configuración | Entrada | Caché | Salida | US$/consulta |
|---|---|---:|---:|---:|---:|
| **A** | Sonnet · corpus completo · sin caché | 35.905 | — | 350 | **0,1130** |
| **B** | Sonnet · corpus completo · con caché | 1.340 | 34.565 | 350 | **0,0196** |
| **C** | Sonnet · RAG (un bloque) | 2.963 | — | 350 | **0,0141** |
| **D** | Haiku · RAG (un bloque) | 2.963 | — | 350 | **0,0047** |

**Entre A y D hay 24× de diferencia.** La configuración es la decisión de costo,
no el volumen.

> **Salvedad sobre B:** no incluye la escritura del caché, que cuesta ~1,25× la
> entrada normal y se repite cada vez que el caché expira. Con poco tráfico el
> caché se enfría entre consultas y B se acerca a A. B solo conviene con volumen
> sostenido; a volumen bajo, C es más barata y más simple.

---

## 4. Costo por escenario

Supuesto de lectura: **las consultas por usuario son del programa completo y se
reparten en los 8 meses.** Si en realidad son mensuales, multiplicar por 8.

### 1.800 usuarios (programa actual)

| Consultas c/u | Total consultas | A · US$ | B · US$ | C · US$ | **D · US$** |
|---|---:|---:|---:|---:|---:|
| 20 | 36.000 | 4.067 | 707 | 509 | **170** |
| 50 | 90.000 | 10.167 | 1.768 | 1.273 | **424** |
| 100 | 180.000 | 20.334 | 3.535 | 2.545 | **848** |

Promedio mensual (÷8): con **D**, entre **21 y 106 US$/mes**. Con **C**, entre
**64 y 318 US$/mes**.

### 80.000 usuarios (fase 2)

| Consultas c/u | Total consultas | A · US$ | B · US$ | C · US$ | **D · US$** |
|---|---:|---:|---:|---:|---:|
| 20 | 1.600.000 | 180.744 | 31.423 | 22.622 | **7.541** |
| 50 | 4.000.000 | 451.860 | 78.558 | 56.556 | **18.852** |

Promedio mensual (÷8): con **D**, entre **943 y 2.356 US$/mes**. Con **A**,
**hasta 56.483 US$/mes** — que es la cifra que justifica poner el tope antes de
encender nada.

---

## 5. Qué mueve el costo, en orden

1. **Cuánto contexto se inyecta.** De lejos el primero. Corpus completo sin caché
   contra RAG de un bloque: **8× de diferencia**. Es una decisión de arquitectura,
   se toma una vez y no se vuelve a tocar.
2. **Qué modelo.** Haiku contra Sonnet: **3× de diferencia**. Para responder dudas
   sobre un corpus propio y acotado, Haiku es probablemente suficiente — pero eso
   se verifica con preguntas reales, no se asume.
3. **Cuánto historial se conserva.** Cada turno que se arrastra se paga de nuevo en
   la consulta siguiente. Conservar 3 turnos en vez de 10 es una línea de código y
   un tercio del historial.
4. **El largo de la respuesta.** La salida cuesta 5× la entrada. Un límite de
   `max_tokens` es el freno más directo, y además mejora las respuestas: un
   asistente que contesta en 4 líneas se lee; uno que contesta en 40, no.
5. **Cuántas consultas por persona.** Es el supuesto más incierto de todos y el
   único que no controlas por diseño. Por eso el tope va por usuario.

**Nota sobre el supuesto más frágil:** «20/50/100 consultas por usuario» no está
fundado en nada observable todavía. En programas formativos internos la mediana
suele ser mucho más baja que la media —la mayoría pregunta dos o tres veces y
unos pocos preguntan cincuenta—, así que el promedio engaña. Cuando el agente
lleve un mes andando, ese número se mide y este documento se rehace con datos.

---

## 6. Cómo poner un tope para que no haya sorpresas

Tres capas. La primera sola no basta.

### 6.1 · En la consola de Anthropic

- **Límite de gasto del workspace.** Es el tope duro: al alcanzarlo las llamadas
  fallan en vez de seguir cobrando. Poner un workspace separado para este proyecto
  con su propio límite.
- **Clave de API propia del proyecto**, no compartida con nada más, para que el
  gasto sea atribuible sin ambigüedad.
- **Alertas de consumo** al 50% y al 80% del límite mensual.

### 6.2 · En el código, antes de llamar

Esto es lo que evita que el tope duro se alcance:

- **Cupo diario por persona.** El sistema ya sabe hacer esto: el tope diario de XP
  lúdico es exactamente el mismo patrón, resuelto en `motor/eventos.py`.
- **`max_tokens` de salida acotado**, con el límite explicado al usuario en vez de
  cortar la frase.
- **Historial acotado** a N turnos.
- **Registrar tokens de entrada y salida en cada llamada**, en la misma tabla de
  eventos. Sin eso no hay forma de saber si la estimación se parecía a la realidad.

### 6.3 · En el contenido

- **El banco de evaluación nunca entra al contexto.** Es privacidad del contenido,
  integridad de la medalla y ahorro, todo junto.

---

## 7. Recomendación

**Empezar con la configuración D —Haiku con RAG de un bloque— y un cupo diario por
persona.** Es la más barata por un margen amplio, y la única forma de saber si
alcanza es probarla con preguntas reales del contenido de AIEP.

Antes de comprometer una cifra en la propuesta hay que confirmar tres cosas:

1. **Los precios vigentes** de la página de Anthropic.
2. **Cuántas consultas por persona** se esperan de verdad —el rango 20→100 mueve
   el costo 5×—.
3. **Si el agente responde solo sobre el contenido del programa** o también sobre
   dudas del proceso de acreditación en general. Lo segundo es otro corpus, otro
   riesgo y otro costo.

Y una cifra para la conversación comercial: con la configuración recomendada, el
agente para los **1.800 usuarios del programa cuesta del orden de 200 a 850
dólares por los 8 meses completos**. Es una cifra chica al lado del resto del
proyecto — lo que hay que cuidar no es ese número, es no encender por descuido la
configuración A en la fase 2.
