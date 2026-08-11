import type { Yo } from "../api";

export type Seccion = "ruta" | "mesa" | "ranking" | "panel";

/** Escalera de S-10. Se nombra el escalón: "nivel" ya significa nivel_estandar (glosario). */
export const ESCALERA = [
  { nombre: "Explorador", desde: 0 },
  { nombre: "Colaborador", desde: 1000 },
  { nombre: "Facilitador", desde: 2500 },
  { nombre: "Embajador", desde: 4500 },
  { nombre: "Líder de Calidad", desde: 7000 },
  { nombre: "Maestro de Acreditación", desde: 10000 },
];

export function progresoDeEscalon(xp: number) {
  const i = Math.max(0, ESCALERA.findIndex((e) => e.desde > xp) - 1);
  const actual = ESCALERA[i === -1 ? ESCALERA.length - 1 : i];
  const siguiente = ESCALERA[i + 1];
  if (!siguiente) return { actual, siguiente: null, pct: 100, faltan: 0 };
  const pct = Math.round(((xp - actual.desde) / (siguiente.desde - actual.desde)) * 100);
  return { actual, siguiente, pct, faltan: siguiente.desde - xp };
}

const iniciales = (n: string) =>
  n.replace(/\(.*?\)/g, "").trim().split(/\s+/).map((p) => p[0]).slice(0, 2).join("").toUpperCase();

type Props = {
  yo: Yo;
  abierto: boolean;
  bloques: number;
  completos: number;
  onCerrar: () => void;
  seccion?: Seccion;
  onIrA?: (s: Seccion) => void;
  onSalir: () => void;
};

export function Sidebar({ yo, abierto, bloques, completos, seccion = "ruta", onIrA, onCerrar, onSalir }: Props) {
  const { actual, siguiente, pct } = progresoDeEscalon(yo.xp_acreditable);

  return (
    <>
      <div className={`velo ${abierto ? "visible" : ""}`} onClick={onCerrar} aria-hidden="true" />
      <aside className={`sidebar ${abierto ? "abierto" : ""}`}>
        <div className="brand">
          <svg className="brand-mark" viewBox="0 0 40 40" fill="none" aria-hidden="true">
            <path d="M20 2 L36 10 V22 C36 31 29 37 20 39 C11 37 4 31 4 22 V10 Z" fill="#E11D3C" />
            <path d="M13 20 l5 5 l10 -11" stroke="#fff" strokeWidth="3.2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
          </svg>
          <div>
            <div className="brand-name">Somos Calidad</div>
            <div className="brand-sub">Ruta AIEP</div>
          </div>
        </div>

        <nav>
          <button
            className={`nav-item ${seccion === "ruta" ? "activo" : ""}`}
            onClick={() => onIrA?.("ruta")}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 12h4l3 8 4-16 3 8h4" /></svg>
            Mi Ruta <span className="nav-badge">{completos}/{bloques}</span>
          </button>
          <button
            className={`nav-item ${seccion === "mesa" ? "activo" : ""}`}
            onClick={() => onIrA?.("mesa")}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="7" height="16" rx="1"/><rect x="14" y="4" width="7" height="9" rx="1"/></svg>
            Mesa de comité
          </button>
          <button
            className={`nav-item ${seccion === "ranking" ? "activo" : ""}`}
            onClick={() => onIrA?.("ranking")}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4 20V10M12 20V4M20 20v-6"/></svg>
            Ranking
          </button>
          {/* El panel aparece solo para quien tiene permiso institucional, que
              sale de la membresía de comité y no del rol (S-35). */}
          {yo.ve_panel_institucional && (
            <button
              className={`nav-item ${seccion === "panel" ? "activo" : ""}`}
              onClick={() => onIrA?.("panel")}
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 3v18h18M7 15l4-5 3 3 5-7"/></svg>
              Panel institucional
            </button>
          )}
          <div className="nav-proximo">Insignias y Plaza: en construcción</div>
        </nav>

        <div className="persona-card">
          <div className="persona-top">
            <div className="avatar" style={{ background: "linear-gradient(135deg,#E11D3C,#F4B740)" }}>
              {iniciales(yo.nombre)}
            </div>
            <div>
              <div className="persona-name">{yo.nombre}</div>
              <div className="persona-role">{yo.cargo}</div>
            </div>
          </div>
          <div className="xp-wrap">
            <div className="xp-meta">
              <span>{actual.nombre}</span>
              <span>
                {yo.xp_acreditable.toLocaleString("es-CL")}
                {siguiente ? ` / ${siguiente.desde.toLocaleString("es-CL")}` : ""} XP
              </span>
            </div>
            <div className="xp-track">
              <div className="xp-fill" style={{ width: `${Math.max(2, pct)}%` }} />
            </div>
          </div>
          <button className="salir" onClick={onSalir}>Cambiar de colaborador</button>
        </div>
      </aside>
    </>
  );
}
