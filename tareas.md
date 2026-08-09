# Cola de tareas — Somos Calidad (orden por dependencias)
# El runner procesa las líneas "- [ ]" de arriba a abajo. Las llena el arquitecto en Fase 0.
# Ejemplos de arranque (el arquitecto los reemplaza/expande tras la auditoría):

- [ ] SPIKE realtime: servidor Colyseus mínimo + sala con 2 avatares sincronizados, probable con túnel
- [ ] Scaffold: docker compose (FastAPI + Postgres + frontend), arranque autosuficiente con seed de 3 roles
- [ ] Modelo de datos: Colaborador, Ruta, Bloque, Modulo, Evaluacion, IntentoEvaluacion, EventoGamificacion, Insignia, Nivel
- [ ] Contratos/adapters: identidad (dev "actuar como" ↔ Entra), correo, Open Badges
- [ ] Generador de Contenido: (rol,tema) -> JSON Schema fijo de ruta completa
- [ ] Validador de Integridad: regresión invariante completitud + canario reprobado
- [ ] Integrador de Gamificación: contenido -> rutas/XP/medallas/nivel derivado de eventos
- [ ] Diseñador de Juegos: quiz formativo (feedback vivo), evaluacion final (80%, resultado al final), reintentos, autosave
- [ ] Dashboard: participacion/aprendizaje/riesgo/cultura desde eventos
- [ ] Sala 3D: integrar cliente a la cascara + presencia + chat con globos + reconexion
- [ ] Gate LISTO: los 5 puntos de CLAUDE.md §13 verdes end-to-end
