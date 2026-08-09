# Brief de dominio — Portal de Gamificación "Somos Calidad" (AIEP)

> Este brief acompaña a la propuesta comercial y al mockup. El arquitecto lo lee en la
> auditoría del Día 0. Si algo acá choca con la propuesta oficial de AIEP, gana la
> propuesta; este brief ordena lo que el director tiene en la cabeza para el slice.

## Qué estamos construyendo
Un portal gamificado donde cada colaborador de AIEP, según su rol, recorre una ruta de
niveles, aprueba evaluaciones y gana medallas. Es el **respaldo de que la institución
cumple con los conocimientos de acreditación CNA**. La verdad de la completitud es
sagrada: una medalla sin aprobación real es el peor bug.

## Objetivo de esta etapa: vertical slice para 3 roles
El sistema entero funcionando para 3 usuarios reales (director + 2 socios), cada uno en
un rol distinto. Es una prueba de tesis, no el despliegue a 1.600.

## Roles (actores)
Profesor, Rector, Secretario Académico, Director de Carrera, Administrativo, Servicios
de Apoyo. Cada rol = su propia ruta, niveles y medallas. La ruta de un rol no muestra
contenido de otro. Para el slice: 3 usuarios = 3 roles.

## Contenido de prueba (desacople clave)
No tenemos el contenido de acreditación real por rol, y NO lo necesitamos para probar la
máquina. Un agente generador toma (rol, tema) y crea una ruta completa de prueba sobre
cualquier tema. Ejemplo: rol Profesor (el director) → tema "Data Science" → ruta
completa con todos los niveles y medallas. En producción, el tema = contenido CNA que
aporta AIEP; la máquina no cambia. Todo lo generado ahora se marca como
`es_contenido_prueba: true` y no se presenta como acreditación oficial.

## Comportamientos a definir (defaults aprobados por el director)
- Reprobar evaluación final (<80%): no revela respuestas; reintento; recomienda de
  nuevo el contenido del módulo.
- Quiz formativo dentro del módulo: feedback inmediato, verde/rojo, muestra la correcta
  y explica.
- Evaluación final del bloque: resultado al final, no en vivo (es la nota que respalda).
- Refresh a mitad del test: autosave por respuesta, retoma donde iba.
- Reintentos: default 3, barajando ítems.
El arquitecto debe además descubrir los casos borde no listados (caída al enviar, doble
envío, empates de ranking, expiración de intento) y especificarlos.

## Invariante máximo
Ninguna medalla/nivel/completitud sin aprobar al umbral (80%). XP solo por evento
legítimo, nunca negativo, nivel derivado del XP. Toda medalla tiene su intento aprobado
que la respalda. Canario: un intento reprobado jamás da medalla.

## Sala 3D (realtime) — pieza de riesgo, va primero como spike
La cáscara la simula localmente. Falta la mecánica multijugador real (servidor de
sincronización). Se ataca primero: levantar el servidor mínimo y probar con 2-3
dispositivos reales antes de comprometer plazos. Alcance del slice: sala social con
avatares + chat con globos + presencia + movimiento sincronizado. Se elimina el escape
room (fase 2). En el slice corre local + túnel; nada de nube.

## Integraciones
Microsoft Entra ID (SSO) como adapter conmutable. Slice arranca con login dev "actuar
como" los 3 roles; Entra real se cablea después. Correo y Open Badges: mock primero.

## Definición de LISTO (quality gate del slice)
1. Los 3 roles se loguean y ven rutas distintas con contenido generado.
2. Cada uno completa un bloque de punta a punta (módulo → quiz → evaluación 80% →
   medalla → XP → nivel).
3. El canario reprobado no da medalla.
4. Los 3 conectados a la vez en la sala 3D, viéndose y chateando en tiempo real.
5. El dashboard muestra datos reales de los 3.

## Referencia visual
En `referencia-demo/` está el mockup navegable (la "cáscara"). Es la meta de UX: darle
vida. Identidad visual ya definida: vino tinta, carmín, oro, menta; tipografías
Bricolage Grotesque + Inter + JetBrains Mono.
