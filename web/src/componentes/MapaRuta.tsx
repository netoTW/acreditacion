import type { BloqueDeRuta } from "../api";

/**
 * El mapa de la ruta, generado DESDE DATOS (S-29).
 *
 * La cáscara traía un path SVG y unas posiciones escritas a mano para exactamente
 * ocho nodos. Acá la serpentina se calcula para N bloques más el nodo de graduación,
 * así que cambiar el tamaño de la ruta no toca el dibujo.
 */

type Props = {
  bloques: BloqueDeRuta[];
  onAbrir?: (b: BloqueDeRuta) => void;
};

type Punto = { x: number; y: number };

/** Serpentina: alterna abajo y arriba, y sube hacia la graduación. */
function posiciones(n: number): Punto[] {
  const margen = 8;
  const ancho = 100 - margen * 2;
  return Array.from({ length: n }, (_, i) => {
    const x = n === 1 ? 50 : margen + (ancho * i) / (n - 1);
    const alto = i % 2 === 0 ? 74 : 34;
    const deriva = (i / Math.max(1, n - 1)) * 12;   // la ruta asciende hacia el final
    return { x, y: alto - deriva };
  });
}

/** Curva suave que pasa por todos los puntos (Catmull-Rom convertido a Bézier). */
function trazo(ps: Punto[], w: number, h: number): string {
  if (ps.length < 2) return "";
  const p = ps.map((q) => ({ x: (q.x / 100) * w, y: (q.y / 100) * h }));
  let d = `M ${p[0].x} ${p[0].y}`;
  for (let i = 0; i < p.length - 1; i++) {
    const p0 = p[i - 1] ?? p[i];
    const p1 = p[i];
    const p2 = p[i + 1];
    const p3 = p[i + 2] ?? p2;
    const c1 = { x: p1.x + (p2.x - p0.x) / 6, y: p1.y + (p2.y - p0.y) / 6 };
    const c2 = { x: p2.x - (p3.x - p1.x) / 6, y: p2.y - (p3.y - p1.y) / 6 };
    d += ` C ${c1.x} ${c1.y}, ${c2.x} ${c2.y}, ${p2.x} ${p2.y}`;
  }
  return d;
}

const W = 1000;
const H = 430;

export function MapaRuta({ bloques, onAbrir }: Props) {
  const total = bloques.length + 1;                 // + graduación
  const puntos = posiciones(total);
  const camino = trazo(puntos, W, H);

  const completos = bloques.filter((b) => b.estado === "completo").length;
  const avance = Math.round((completos / total) * 100);

  const claseDe = (b: BloqueDeRuta) =>
    b.estado === "completo" ? "completo"
      : b.estado === "disponible" || b.estado === "en_curso" ? "ahora"
      : "cerrado";

  const graduado = completos === bloques.length;

  return (
    <div className="mapa">
      <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" aria-hidden="true">
        <defs>
          <linearGradient id="avance" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0" stopColor="#2DD4A7" />
            <stop offset="1" stopColor="#F4B740" />
          </linearGradient>
        </defs>
        <path d={camino} fill="none" stroke="rgba(255,255,255,.14)" strokeWidth={26} strokeLinecap="round" />
        {avance > 0 && (
          <path
            d={camino}
            fill="none"
            stroke="url(#avance)"
            strokeWidth={26}
            strokeLinecap="round"
            pathLength={100}
            strokeDasharray={`${avance} 100`}
          />
        )}
      </svg>

      {bloques.map((b, i) => (
        <div
          key={b.bloque_ruta_id}
          className={`nodo ${claseDe(b)}`}
          style={{ left: `${puntos[i].x}%`, top: `${puntos[i].y}%` }}
        >
          <button
            className="nodo-dot"
            onClick={() => onAbrir?.(b)}
            aria-label={`Bloque ${b.orden}: ${b.dimension_nombre}, nivel ${b.nivel_estandar}, ${b.estado}`}
          >
            {b.orden}
            <span className="nodo-nivel">N{b.nivel_estandar}</span>
            {b.obtenida > 0 && <span className="medalla-mini" aria-hidden="true">🏅</span>}
          </button>
          <div className="nodo-label">{b.dimension_nombre}</div>
          {/* El estado va en texto además de en color: no todo el mundo distingue menta de carmín. */}
          <div className="nodo-sub">
            {b.estado === "completo" ? "completo"
              : b.estado === "disponible" ? "disponible"
              : b.estado === "en_curso" ? "en curso"
              : b.estado === "requiere_acompanamiento" ? "requiere apoyo"
              : "bloqueado"}
            {b.medalla_xp ? ` · ${b.medalla_xp} XP` : ""}
          </div>
        </div>
      ))}

      <div
        className={`nodo ${graduado ? "ahora" : "cerrado"}`}
        style={{ left: `${puntos[total - 1].x}%`, top: `${puntos[total - 1].y}%` }}
      >
        <div className="nodo-dot" aria-hidden="true">🏆</div>
        <div className="nodo-label">Somos Calidad</div>
        <div className="nodo-sub">graduación</div>
      </div>
    </div>
  );
}
