# ADR-004 — El servidor de la Plaza es agnóstico del render: 2D y 3D consumen el mismo estado

**Estado:** aceptado · **Fecha:** 2026-08-09 · **Decide:** arquitecto · **Responde a:** E-01

## Contexto

El director respondió E-01: **la meta es 3D tipo Habbo**, pero **condicionado al spike**.
Si el multijugador 3D no es viable en el plazo, se cae al 2D isométrico de la cáscara sin
drama. Instrucción explícita: *no comprometer 3D antes de que el spike lo confirme; el
spike decide.*

Eso deja una pregunta de diseño que hay que responder **hoy**, porque el spike arranca hoy:
¿qué se construye mientras no sabemos si el render final es 2D o 3D?

## Decisión

**El servidor de tiempo real no sabe nada del render.** Sincroniza un mundo en un plano 2D
y nada más. El render es un detalle del cliente, intercambiable, en la hoja del árbol.

El estado autoritativo por participante es:

```
id · nombre · cargo · color · x · y · rot · mensaje · mensajeHasta · conectadoEn
```

`x` e `y` son coordenadas del **plano del salón**, no píxeles de pantalla. `rot` es la
orientación en el plano. Con eso:

- Un **render 2D isométrico** proyecta `(x, y)` con la transformación que la cáscara ya
  tiene y que ya funciona.
- Un **render 3D** mapea `(x, y)` al plano del piso y usa `rot` para orientar el avatar.

Es el mismo estado. **El spike prueba el servidor, no el render.**

### Qué significa para el plazo

El gate A4 —dos dispositivos reales fuera de localhost viéndose moverse— valida
sincronización, latencia, reconexión y túnel. Nada de eso depende de si el avatar es un
sprite o una malla. Por lo tanto:

- Si el spike pasa, **ya está probada la parte difícil**, sea cual sea el render.
- La decisión 2D/3D se toma **después** del gate, con datos, y cuesta un componente de
  cliente. No un rediseño.
- **E-01 deja de estar en el camino crítico.**

### Contrato del cliente

Un módulo de render implementa:

```
montar(contenedor, opciones)
aplicarEstado(participantes)     // llamado en cada patch del servidor
alDestino(callback)              // el usuario pidió caminar a (x, y) del plano
desmontar()
```

`RenderCanvas2D` se implementa primero, porque el código ya existe y está probado en la
cáscara. `Render3D` se implementa solo si el spike habilita la ambición. La app no cambia:
solo cambia qué módulo se monta.

## Consecuencias

- El canvas de la cáscara se conserva como **implementación de referencia**, no como deuda.
- Se prohíbe que la lógica de sala, presencia o chat toque coordenadas de pantalla.
- Se prohíbe que el cliente sea autoridad de posición: el cliente **pide** destino, el
  servidor **decide** posición. Sin esto, la sala se desincroniza y el chat se puede
  falsificar.
- La actividad social de la Plaza (E-02) también corre en el servidor y es agnóstica del
  render: es una trivia grupal contra reloj que **reusa el motor de juegos de la cáscara**,
  no un motor nuevo.

## Cómo se revierte

Es reversible por construcción: cambiar de render es cambiar un módulo. Lo que **no** se
revierte barato es la decisión contraria —acoplar el servidor a un render—, y por eso se
descarta.
