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
  hito: string | null;
  periodo_texto: string | null;
  hito_titulo: string | null;
  medalla: string | null;
  medalla_xp: number | null;
  modulos: number;
  obtenida: number;
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

export type Bloque = BloqueDeRuta & {
  medalla_id: string | null;
  medalla_tipo: string | null;
  umbral_aprobacion: string | number | null;
  n_items_por_intento: number | null;
  max_reintentos: number | null;
  intentos_usados: number;
  modulos: Modulo[];
  modulos_completos: number;
  evaluacion_disponible: boolean;
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

  completarModulo: (id: string) =>
    pedir<{ ya_estaba: boolean; xp_otorgado: number }>(`/modulos/${id}/completar`, {
      method: "POST",
    }),
};
