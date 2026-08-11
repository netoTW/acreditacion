-- =============================================================================
-- 010 — D1 Gestión · «El presupuesto de la acreditación»
-- =============================================================================
--
-- La única mecánica del sistema con estado que evoluciona. El escenario guarda
-- el modelo completo —frentes, desgaste, efecto, umbral, retardo y la regla
-- encadenada— como datos, para que ajustar la dificultad sea editar filas y no
-- tocar el motor.
--
-- `solucion_ejemplo` NO sale nunca al cliente: existe para que el validador
-- compruebe, simulando, que el escenario se puede ganar de verdad. Un escenario
-- imposible no se detecta leyéndolo.

CREATE TABLE escenario_gestion (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  codigo               text NOT NULL UNIQUE,
  titulo               text NOT NULL,
  contexto             text NOT NULL,
  turnos               smallint NOT NULL CHECK (turnos > 0),
  turnos_de_decision   smallint NOT NULL CHECK (turnos_de_decision > 0),
  presupuesto          smallint NOT NULL CHECK (presupuesto > 0),
  retardo              smallint NOT NULL CHECK (retardo >= 0),
  -- [{clave, nombre, descripcion, inicial, desgaste, efecto, umbral}]
  frentes              jsonb NOT NULL,
  -- {frente, habilitador, base, factor, texto} — el techo que hace que decidir duela.
  regla                jsonb NOT NULL,
  solucion_ejemplo     jsonb NOT NULL,
  cierre               text NOT NULL,
  es_contenido_prueba  boolean NOT NULL DEFAULT true,
  -- Lo que se siembra en el último turno de decisión tiene que alcanzar a
  -- aterrizar, o habría decisiones que el período nunca resuelve.
  CONSTRAINT ck_el_periodo_alcanza_a_resolver
    CHECK (turnos >= turnos_de_decision + retardo)
);

COMMENT ON TABLE escenario_gestion IS
  'Contenido de prueba de D1. Cifras sintéticas: no describen la gestión de '
  'ninguna institución.';
