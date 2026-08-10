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

  yo: () => pedir<Yo>("/auth/yo"),
  miRuta: () => pedir<BloqueDeRuta[]>("/mi/ruta"),
};
