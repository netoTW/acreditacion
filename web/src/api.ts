/**
 * Cliente de la API.
 *
 * El token de sesión vive en localStorage y viaja en la cabecera. Nunca se manda
 * un `colaborador_id`: la identidad la deriva el servidor de la sesión (I-10).
 */
const BASE = (import.meta.env.VITE_API as string | undefined) ?? "/api";
const CLAVE_TOKEN = "somoscalidad.sesion";

export const token = {
  leer: () => localStorage.getItem(CLAVE_TOKEN),
  guardar: (t: string) => localStorage.setItem(CLAVE_TOKEN, t),
  borrar: () => localStorage.removeItem(CLAVE_TOKEN),
};

export class SesionCaida extends Error {}

async function pedir<T>(ruta: string, opciones: RequestInit = {}): Promise<T> {
  const t = token.leer();
  const r = await fetch(BASE + ruta, {
    ...opciones,
    headers: {
      "Content-Type": "application/json",
      ...(t ? { Authorization: `Bearer ${t}` } : {}),
      ...(opciones.headers ?? {}),
    },
  });

  if (r.status === 401) {
    token.borrar();
    throw new SesionCaida("la sesión expiró o no es válida");
  }
  if (!r.ok) {
    const detalle = await r.json().catch(() => ({}));
    throw new Error(detalle?.detail ?? `error ${r.status} en ${ruta}`);
  }
  return r.json() as Promise<T>;
}

/* ------------------------------------------------------------------ tipos */
export type PersonaDisponible = {
  id: string;
  nombre: string;
  email: string;
  cargo: string;
  unidad: string | null;
  ve_panel_institucional: boolean;
};

export type Yo = {
  id: string;
  nombre: string;
  email: string;
  cargo: string;
  cargo_codigo: string;
  unidad: string | null;
  xp_acreditable: number;
  xp_total: number;
  escalon: string;
  insignias: number;
  ve_panel_institucional: boolean;
};

export type BloqueDeRuta = {
  bloque_ruta_id: string;
  orden: number;
  estado: "bloqueado" | "disponible" | "en_curso" | "completo" | "requiere_acompanamiento";
  dimension: string;
  dimension_nombre: string;
  nivel_estandar: number;
  titulo: string;
  es_contenido_prueba: boolean;
  /** Del modelo de impacto de AIEP: las 2 dimensiones de mayor peso del rol. */
  es_critica: boolean;
  /** El % que la dimensión pesa para este rol. Llega como string desde numeric. */
  peso_ranking: string | number;
  umbral: string | number | null;
  hito: string | null;
  periodo_texto: string | null;
  hito_titulo: string | null;
  medalla: string | null;
  medalla_tipo: "silver" | "gold" | string | null;
  medalla_xp: number | null;
  modulos: number;
  obtenida: number;
  desafio_resuelto: number;
};

export type Modulo = {
  id: string;
  orden: number;
  titulo: string;
  cuerpo: string;
  duracion_min: number;
  xp: number;
  nivel_estandar_origen: number;
  es_contenido_prueba: boolean;
  completado: boolean;
};

export type Bloque = Omit<BloqueDeRuta, "modulos"> & {
  medalla_id: string | null;
  umbral_aprobacion: string | number | null;
  n_items_por_intento: number | null;
  max_reintentos: number | null;
  intentos_usados: number;
  modulos: Modulo[];
  modulos_completos: number;
  /** En la dimensión crítica, el desafío va antes de la evaluación reforzada. */
  desafio_pendiente: boolean;
  /** El juego propio de esta dimensión. null mientras no exista (fase 2). */
  juego: { clave: string; nombre: string; descripcion: string } | null;
  evaluacion_disponible: boolean;
};

export type MapaRepartido = {
  juego: string;
  actores: { actor_id: string; codigo: string; nombre: string; tipo: string; descripcion: string }[];
  acciones: { clave: string; nombre: string; descripcion: string }[];
};

export type ResultadoMapa = {
  total: number;
  aciertos: number;
  descartes_correctos: number;
  descartes_totales: number;
  mapa_limpio: boolean;
  puntos: number;
  xp_otorgado: number;
  ya_jugado_hoy: boolean;
  revelacion: {
    actor_id: string;
    nombre: string;
    acerto: boolean;
    ato_en: string | null;
    accion_correcta: string | null;
    accion_nombre: string | null;
    es_contraparte: boolean;
    razon: string;
  }[];
};

export type CasoCohorte = {
  caso_id: string;
  codigo: string;
  titulo: string;
  contexto: string;
  etapas: { nombre: string; valor: number }[];
  /** La referencia viaja: una caída no significa nada sin ella. */
  tramos: { desde: string; hasta: string; referencia_pct: number }[];
  indicadores: { clave: string; nombre: string; valor: string }[];
};

export type PartidaCohorte = { juego: string; casos: CasoCohorte[] };

export type ResultadoCohorte = {
  total_casos: number;
  tramos_correctos: number;
  indicadores_correctos: number;
  lectura_limpia: boolean;
  puntos: number;
  xp_otorgado: number;
  ya_jugado_hoy: boolean;
  revelacion: {
    caso_id: string;
    codigo: string;
    titulo: string;
    acerto_tramo: boolean;
    acerto_indicador: boolean;
    tramo_correcto: number;
    tramo_nombre: string;
    explicacion_quiebre: string;
    indicador_correcto: string;
    indicador_nombre: string;
    explicacion_indicador: string;
  }[];
};

export type CartaHito = { hito_id: string; codigo: string; titulo: string };

export type LineaRepartida = {
  juego: string;
  dimension: string;
  cartas: CartaHito[];
};

export type ResultadoLinea = {
  total: number;
  en_su_lugar: number;
  pares_correctos: number;
  pares_totales: number;
  linea_perfecta: boolean;
  puntos: number;
  xp_otorgado: number;
  ya_jugado_hoy: boolean;
  revelacion: {
    hito_id: string;
    codigo: string;
    titulo: string;
    ruta: "autoevaluacion" | "acreditacion" | string;
    anio: number;
    periodo_texto: string;
    puesto_en: number;
    posicion_real: number;
    acerto: boolean;
  }[];
};

export type OpcionDecision = { clave: string; texto: string };
export type GrupoDecision = { clave: string; etiqueta: string };

export type Decision = {
  decision_id: string;
  orden: number;
  tipo: "eleccion_unica" | "seleccion_multiple" | "clasificacion";
  enunciado: string;
  opciones: OpcionDecision[];
  grupos: GrupoDecision[];
};

export type DesafioAplicado = {
  desafio_id: string;
  titulo: string;
  dimension: string;
  nivel_estandar: number;
  rol_ficticio: string;
  situacion: string;
  datos: { etiqueta: string; valor: string }[];
  ya_resuelto: boolean;
  aciertos_previos: number | null;
  decisiones: Decision[];
};

export type ResultadoDesafio = {
  total: number;
  aciertos: number;
  perfecto: boolean;
  xp_otorgado: number;
  ya_resuelto: boolean;
  revelacion: {
    decision_id: string;
    orden: number;
    acerto: boolean;
    respuesta_dada: unknown;
    clave_correcta: unknown;
    explicacion: string;
  }[];
};

export type ItemQuiz = {
  id: string;
  orden: number;
  enunciado: string;
  alternativas: string[];
  indice_correcta: number;
  explicaciones: string[];
};

export type ResultadoCalibre = {
  total: number;
  aciertos: number;
  seguros: number;
  seguros_acertados: number;
  puntos: number;
  bono_calibrado: boolean;
  xp_otorgado: number;
  ya_jugado_hoy: boolean;
};

export type ResultadoQuiz = {
  total: number;
  aciertos: number;
  mejor_racha: number;
  xp_otorgado: number;
  ya_jugado_hoy: boolean;
};

export type ItemEvaluacion = { item_id: string; enunciado: string; alternativas: string[] };

export type Intento = {
  id: string;
  numero_intento: number;
  estado: "abierto" | "enviado" | "expirado";
  expira_en: string;
  enviado_en: string | null;
  puntaje: number | null;
  aprobado: boolean | null;
  bloque_ruta_id: string;
  umbral_aprobacion: string | number;
  max_reintentos: number;
  dimension_nombre: string;
  nivel_estandar: number;
  items: ItemEvaluacion[];
  respuestas: Record<string, number>;
};

export type ResultadoEvaluacion = {
  aprobado: boolean;
  puntaje: number;
  insignia_id: string | null;
  xp_otorgado: number;
  reintentos_restantes: number;
};

export type MesaRepartida = {
  bandejas: { codigo: string; nombre: string }[];
  cartas: { item_id: string; texto: string }[];
};

export type ResultadoMesa = {
  total: number;
  aciertos: number;
  puntos: number;
  mesa_perfecta: boolean;
  xp_otorgado: number;
  ya_jugado_hoy: boolean;
  revelacion: {
    item_id: string; acerto: boolean; puesta_en: string;
    dimension_correcta: string; dimension_nombre: string; enunciado: string;
  }[];
};

/* --------------------------------------------------------------- llamadas */
export const api = {
  personasDisponibles: () => pedir<PersonaDisponible[]>("/auth/dev/colaboradores"),

  actuarComo: async (colaborador_id: string) => {
    const r = await pedir<{ token: string }>("/auth/dev/actuar-como", {
      method: "POST",
      body: JSON.stringify({ colaborador_id }),
    });
    token.guardar(r.token);
    return r.token;
  },

  /**
   * Un 404 acá significa que la sesión apunta a alguien que ya no existe —pasa al
   * recrear la base con `down -v`— y se trata como sesión caída, no como error de
   * pantalla. Si no, la app queda mostrando "colaborador inexistente" sin salida.
   */
  yo: async () => {
    try {
      return await pedir<Yo>("/auth/yo");
    } catch (e) {
      if (e instanceof Error && /inexistente/i.test(e.message)) {
        token.borrar();
        throw new SesionCaida("tu sesión ya no es válida");
      }
      throw e;
    }
  },

  miRuta: () => pedir<BloqueDeRuta[]>("/mi/ruta"),
  bloque: (id: string) => pedir<Bloque>(`/bloques-ruta/${id}`),

  quiz: (moduloId: string) => pedir<ItemQuiz[]>(`/modulos/${moduloId}/quiz`),

  /** Se mandan las respuestas EN ORDEN: la racha depende de él, y la calcula el servidor. */
  resultadoQuiz: (moduloId: string, respuestas: { item_id: string; indice_elegido: number }[]) =>
    pedir<ResultadoQuiz>(`/modulos/${moduloId}/quiz/resultado`, {
      method: "POST",
      body: JSON.stringify({ respuestas }),
    }),

  abrirIntento: (bloqueRutaId: string) =>
    pedir<{ intento_id: string }>(`/bloques-ruta/${bloqueRutaId}/intentos`, { method: "POST" }),

  intento: (id: string) => pedir<Intento>(`/intentos/${id}`),

  /** Autosave por respuesta: si el navegador se cierra, al volver está todo (S-14). */
  guardarRespuesta: (intentoId: string, item_id: string, indice_elegido: number) =>
    pedir<{ guardada: boolean }>(`/intentos/${intentoId}/respuestas`, {
      method: "POST",
      body: JSON.stringify({ item_id, indice_elegido }),
    }),

  cerrarIntento: (id: string) =>
    pedir<ResultadoEvaluacion>(`/intentos/${id}/cerrar`, { method: "POST" }),

  /** M1 Calibre: el servidor recalcula el puntaje, penalización incluida. */
  resultadoCalibre: (
    moduloId: string,
    respuestas: { item_id: string; indice_elegido: number; seguro: boolean }[],
  ) =>
    pedir<ResultadoCalibre>(`/modulos/${moduloId}/calibre/resultado`, {
      method: "POST",
      body: JSON.stringify({ respuestas }),
    }),

  mesa: () => pedir<MesaRepartida>("/juegos/mesa"),

  /** El cliente manda dónde puso cada carta; el puntaje lo pone el servidor. */
  cerrarMesa: (colocaciones: { item_id: string; dimension: string }[]) =>
    pedir<ResultadoMesa>("/juegos/mesa/resultado", {
      method: "POST",
      body: JSON.stringify({ colocaciones }),
    }),

  completarModulo: (id: string) =>
    pedir<{ ya_estaba: boolean; xp_otorgado: number }>(`/modulos/${id}/completar`, {
      method: "POST",
    }),

  /** D4: seis actores y seis acciones, SIN decir cuál va con cuál. */
  contrapartes: (bloqueRutaId: string) =>
    pedir<MapaRepartido>(`/bloques-ruta/${bloqueRutaId}/juego/contrapartes`),

  /** `accion_clave: null` es una respuesta: «este actor no es contraparte». */
  cerrarContrapartes: (
    bloqueRutaId: string,
    vinculos: { actor_id: string; accion_clave: string | null }[],
  ) =>
    pedir<ResultadoMapa>(`/bloques-ruta/${bloqueRutaId}/juego/contrapartes/resultado`, {
      method: "POST",
      body: JSON.stringify({ vinculos }),
    }),

  /** D2: tres cohortes con su referencia, SIN el tramo de quiebre. */
  cohorte: (bloqueRutaId: string) =>
    pedir<PartidaCohorte>(`/bloques-ruta/${bloqueRutaId}/juego/cohorte`),

  cerrarCohorte: (
    bloqueRutaId: string,
    respuestas: { caso_id: string; tramo: number | null; indicador: string | null }[],
  ) =>
    pedir<ResultadoCohorte>(`/bloques-ruta/${bloqueRutaId}/juego/cohorte/resultado`, {
      method: "POST",
      body: JSON.stringify({ respuestas }),
    }),

  /** D3: seis hitos barajados, SIN su período ni su año. */
  lineaTiempo: (bloqueRutaId: string) =>
    pedir<LineaRepartida>(`/bloques-ruta/${bloqueRutaId}/juego/linea-tiempo`),

  /** El cliente manda en qué orden los dejó; corregir es del servidor. */
  cerrarLinea: (bloqueRutaId: string, orden: string[]) =>
    pedir<ResultadoLinea>(`/bloques-ruta/${bloqueRutaId}/juego/linea-tiempo/resultado`, {
      method: "POST",
      body: JSON.stringify({ orden }),
    }),

  /** El caso aplicado de la dimensión crítica. Llega SIN las respuestas correctas. */
  desafio: (bloqueRutaId: string) =>
    pedir<DesafioAplicado>(`/bloques-ruta/${bloqueRutaId}/desafio`),

  /** El cliente manda qué decidió; corregir y puntuar es del servidor. */
  resolverDesafio: (
    bloqueRutaId: string,
    respuestas: { decision_id: string; respuesta: unknown }[],
  ) =>
    pedir<ResultadoDesafio>(`/bloques-ruta/${bloqueRutaId}/desafio/resultado`, {
      method: "POST",
      body: JSON.stringify({ respuestas }),
    }),
};
