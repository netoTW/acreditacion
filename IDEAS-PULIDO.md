# Ideas de pulido

> Mejoras que **no** bloquean el slice y que conviene tener anotadas para no perderlas.
> No es la cola de trabajo (esa es `tareas.md`) ni preguntas al cliente (esas van a `DUDAS.md`).

## Contenido

- **Enriquecer los bancos con más variedad temática por dimensión** para evitar ítems casi
  duplicados en producción (ej: dos preguntas del tipo «¿qué es el perfil de egreso?»).
  *Origen: revisión del director al aprobar C5.*
  Hoy cada concepto produce tres ítems con plantillas distintas —definición, escenario
  aplicado y emparejamiento—, y el validador rechaza pares con similitud sobre 0,9 medida
  en enunciado + alternativa correcta. Eso evita duplicados exactos, pero con un banco más
  grande por dimensión conviene además: más ángulos por concepto (caso límite, error
  frecuente, comparación entre conceptos), y subir el umbral de similitud a medida que el
  banco crezca.

## Quiz y evaluación

- **Los ítems del quiz formativo y los del banco de la evaluación salen de los mismos
  conceptos**, así que comparten enunciados. No compromete el invariante —la medalla sigue
  exigiendo aprobar la evaluación— pero hace que la evaluación se parezca demasiado a la
  práctica. En producción conviene que el generador produzca ángulos distintos para cada
  uno: la práctica con casos, la evaluación con aplicación.

## Realtime

- Interpolación en el cliente para suavizar el movimiento con latencia alta. El director
  reportó *lag leve* con servidor en su Mac más túnel; en producción sobre nube debería
  bajar, pero interpolar en el cliente lo disimula igual.

## Contenido de prueba

- Cuando entre el corpus real de AIEP, revisar que el aviso de `es_contenido_prueba` deje
  de mostrarse y que el validador siga exigiendo lo mismo al material oficial.

## Desafío aplicado

- **Los distractores se repiten entre decisiones.** La decisión 3 usa como opciones
  incorrectas las mismas que la decisión 1, porque ambas salen del concepto más
  exigente del bloque. Se nota al jugarlo. Arreglo: que la decisión 3 tome sus
  distractores de un concepto distinto al de la decisión 1, o del banco de acciones
  incorrectas de la dimensión completa. Verificado con el director en la Fase 1;
  no bloquea.

## Juegos por dimensión

- **La dificultad de los juegos no escala con el nivel del rol.** El microlearning y
  la evaluación sí lo hacen (quices de 3/5/7 ítems, evaluaciones de 4/6/8), pero los
  juegos reparten el mismo tablero a un nivel 1 y a un nivel 3. Falta un campo de
  dificultad en el contenido de cada juego y que `repartir` filtre por el nivel del
  bloque. Detectado por el director jugando D2; el detalle y el porqué están en
  `DUDAS.md`. No bloquea la cáscara: bloquea el contenido real.

