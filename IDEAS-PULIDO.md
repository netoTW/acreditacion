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

## Realtime

- Interpolación en el cliente para suavizar el movimiento con latencia alta. El director
  reportó *lag leve* con servidor en su Mac más túnel; en producción sobre nube debería
  bajar, pero interpolar en el cliente lo disimula igual.

## Contenido de prueba

- Cuando entre el corpus real de AIEP, revisar que el aviso de `es_contenido_prueba` deje
  de mostrarse y que el validador siga exigiendo lo mismo al material oficial.
