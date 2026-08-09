# Track A — Spike de la Plaza Virtual

> Es el track de riesgo del proyecto: lo único que nunca se ha probado.
> **Hasta que pase el gate A4, ningún plazo del proyecto es firme.**

## Levantar

```bash
cd realtime
npm install     # ya hecho
npm start       # → http://localhost:2567
```

## Gates automatizables

```bash
npm start                 # en una terminal
node pruebas/gates.js     # en otra
```

Cubre A2, A3 y A5. Estado actual: **10 de 10 en verde.**

```
ok  A2 · dos clientes se ven
ok  A3 · el movimiento viaja · el servidor interpola, no teletransporta
ok  A3 · el servidor acota destinos fuera del mundo
ok  A5 · el chat llega · rate limit · truncado a 80 caracteres
ok  A5 · la presencia baja al salir
```

## Gate A4 — el que importa, y lo corre el director

Los gates de arriba prueban la lógica. **A4 prueba la red**, y eso no se puede automatizar
desde acá: hay que salir de localhost con dispositivos reales.

```bash
# terminal 1
cd realtime && npm start

# terminal 2
ngrok http 2567
```

Abre la URL pública de ngrok **en el notebook y en el teléfono** (datos móviles, no wifi de
la casa — la idea es probar una red de verdad). Entra con nombres distintos.

**Pasa si:** los dos avatares se ven, uno camina y el otro lo ve caminar sin saltos, y el
chat llega en ambos sentidos.

### A6 — reconexión

Con los dos conectados, refresca uno. Debe volver y la sala **no** debe romperse. El
servidor mantiene la sesión 20 segundos esperando la reconexión.

### A7 — los tres

Los tres dispositivos a la vez. Es el punto 4 de la definición de LISTO (CLAUDE.md §13).

## Qué hay acá

```
src/estado.js      esquema del mundo — tiles, no píxeles (ADR-004)
src/SalaPlaza.js   la sala: autoridad de posición, chat con rate limit, reconexión
src/index.js       servidor HTTP + WebSocket + healthcheck
cliente/           cliente de prueba con el render 2D isométrico portado de la cáscara
pruebas/gates.js   los gates automatizables
```

## La decisión de diseño que hay detrás

**El servidor no sabe nada del render** ([ADR-004](../docs/decisiones/ADR-004-realtime-agnostico-de-render.md)).
Sincroniza posiciones en **tiles del plano del salón**, no en píxeles de pantalla. Un render
isométrico 2D proyecta `(x, y)`; un render 3D mapea `(x, y)` al plano del piso. Es el mismo
estado.

Por eso este spike prueba **el servidor**, no el render — y la decisión 2D contra 3D (E-01)
se toma **después** del gate A4, con datos, y cuesta cambiar un módulo de cliente. Sale del
camino crítico.

El cliente implementa el contrato de render tal cual:

```js
montar(contenedor, opciones)
aplicarEstado(participantes)
alDestino(callback)
desmontar()
```

`RenderCanvas2D` está implementado porque el código ya existía y estaba probado en la
cáscara. `Render3D` se implementa **solo si el spike habilita la ambición**.

## Reglas que el servidor ya impone

- **El cliente pide destino, el servidor decide posición.** Sin esto la sala se desincroniza
  y las posiciones se pueden falsificar.
- Destinos fuera del mundo se acotan al salón.
- Chat: 80 caracteres máximo y 1,2 s entre mensajes por cliente (S-24).
- Al caerse un cliente, se le guardan 20 s para reconectar antes de sacarlo.

## Lo que falta y está identificado

- **Identidad**: hoy el nombre y el cargo llegan por opciones del cliente. En producción
  llegan en un token firmado por la API, para que la sala sepa quién entra sin duplicar la
  lógica de identidad (ADR-001). La costura está aislada en `onJoin`.
- **Persistencia del chat** en `mensaje_plaza` (S-24). Hoy solo va al log.
- **Actividad social** (E-02): trivia grupal contra reloj que **reusa** el motor de juegos de
  la cáscara, no un motor nuevo (S-42). Va después del gate A4.
