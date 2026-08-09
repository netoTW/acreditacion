# ADR-002 — Frontend: se evoluciona la cáscara a React + TypeScript, conservando su identidad

**Estado:** aceptado · **Fecha:** 2026-08-09 · **Decide:** arquitecto · **Realiza:** S-25

## Contexto

CLAUDE.md §11 deja la decisión abierta: migrar a React o evolucionar el HTML. La cáscara son
1.276 líneas con toda la identidad visual resuelta y diez pantallas navegables, pero cero
persistencia y cero estado real.

Lo que el sistema real necesita y la cáscara no tiene: sesión, ruta cargada del servidor,
intento de evaluación con autosave por respuesta, reintentos, presencia en tiempo real,
permisos, y seis pantallas nuevas. Eso es estado de verdad.

## Decisión

**React 19 + TypeScript + Vite.** Router propio de la app, TanStack Query para estado de
servidor, y **cero framework de CSS**.

**La identidad visual de la cáscara se conserva literalmente.** Los tokens del `:root` —vino
tinta, carmín, oro, menta, marfil, niebla, radios, sombras— pasan tal cual a `tokens.css`
(ver [design-system.md](../design-system.md)) y son la única fuente de color y tipografía.
No se rediseña nada: la cáscara **es** la meta de UX.

### Por qué no seguir en HTML plano

El autosave por respuesta, la reconexión de la sala y el intento de evaluación con estado
servidor son exactamente el tipo de problema donde el DOM a mano se convierte en bugs de
sincronización. Y el peor de esos bugs acá no es visual: es mostrar "completado" cuando no
lo está.

### Por qué no Tailwind

La identidad ya está diseñada y expresada en tokens CSS. Tailwind obligaría a traducir cada
decisión existente a utilidades y a mantener dos vocabularios de estilo en paralelo. Se usa
CSS con módulos por componente sobre los tokens.

### Qué se rescata tal cual de la cáscara

- El `:root` completo de tokens.
- El SVG generador de insignias por tipo, que ya funciona bien.
- El render isométrico del canvas de la Plaza, que pasa a ser `RenderCanvas2D`
  ([ADR-004](ADR-004-realtime-agnostico-de-render.md)).
- El motor de trivia y de memoria, que se extrae a un módulo reutilizable — la actividad
  social de la Plaza lo **reusa** en vez de duplicarlo (E-02).

### Qué se corrige al portar

- **Navegación móvil (S-28):** hoy bajo 1080 px el sidebar se va a `left:-280px` sin botón
  para abrirlo. Se agrega. Es bloqueante: el gate de la Plaza se prueba con teléfonos.
- **Accesibilidad:** los `div` con `onclick` pasan a `button`; foco visible, navegación por
  teclado y `aria` en quiz, evaluación y mapa de ruta.
- **Autohospedaje (S-26):** tipografías y librería de gráficos dejan de venir de CDN.
- El polyfill roto de `roundRect` y la comparación por `textContent` de la trivia no se
  portan.

## Consecuencias

- Hay un paso de build. A cambio, tipos compartidos con el contrato OpenAPI de la API, que
  es lo que impide que un constructor invente un campo.
- La UI va en paralelo desde el primer día, nunca al final (CLAUDE.md §14).
- El render de la Plaza queda en la hoja del árbol: cambiar 2D por 3D no toca la app.

## Cómo se revierte

Cara de revertir una vez escritas las pantallas, y por eso es ADR. La mitigación es que la
identidad visual vive en CSS puro sobre tokens y no en el framework: si algún día hay que
salir de React, el diseño se lleva intacto.
