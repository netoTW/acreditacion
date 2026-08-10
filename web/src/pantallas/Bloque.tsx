import { useEffect, useState } from "react";
import { SesionCaida, api, type Bloque as TBloque, type Yo } from "../api";
import { Marco } from "../componentes/Marco";

type Props = {
  bloqueRutaId: string;
  yo: Yo;
  totalBloques: number;
  bloquesCompletos: number;
  onVolver: () => void;
  onAbrirModulo: (moduloId: string) => void;
  onRendir: () => void;
  onSalir: () => void;
};

const ICONO = {
  completo: <path d="M20 6 9 17l-5-5" />,
  ahora: <path d="M5 3l14 9-14 9V3z" />,
  cerrado: (
    <>
      <rect x="4" y="11" width="16" height="10" rx="2" />
      <path d="M8 11V7a4 4 0 0 1 8 0v4" />
    </>
  ),
};

export function Bloque(p: Props) {
  const [b, setB] = useState<TBloque | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.bloque(p.bloqueRutaId)
      .then(setB)
      .catch((e) => (e instanceof SesionCaida ? p.onSalir() : setError(e.message)));
  }, [p.bloqueRutaId]);

  const cuerpo = () => {
    if (error)
      return (
        <div className="error">
          <p>{error}</p>
          <button className="btn btn-primary" style={{ marginTop: 14 }} onClick={p.onVolver}>
            Volver a mi ruta
          </button>
        </div>
      );
    if (!b) return <div className="cargando">cargando el bloque…</div>;

    // El primer módulo sin ver es el que toca; los siguientes quedan por delante
    // pero no bloqueados: el orden es una sugerencia, no un candado.
    const siguiente = b.modulos.find((m) => !m.completado);

    return (
      <div className="pantalla">
        <button className="volver" onClick={p.onVolver}>← Mi Ruta</button>

        <div className="pantalla-head">
          <div className="eyebrow">
            Bloque {b.orden} · {b.hito ?? "sin hito"}
            {b.periodo_texto ? ` · ${b.periodo_texto}` : ""}
          </div>
          <h1>{b.dimension_nombre}</h1>
          <p>
            {b.hito_titulo ? `${b.hito_titulo}. ` : ""}
            Se te exige el <b>nivel de estándar {b.nivel_estandar}</b>, que incluye los
            niveles anteriores.
          </p>
        </div>

        <div className="bloque-layout">
          <div>
            <div className="section-title">Contenido del bloque</div>

            {b.modulos.map((m) => {
              const estado = m.completado ? "completo" : m === siguiente ? "ahora" : "cerrado";
              return (
                <div className="mod-row" key={m.id}>
                  <div className={`mod-ico ${estado}`}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      {ICONO[estado === "cerrado" ? "cerrado" : estado]}
                    </svg>
                  </div>
                  <div className="mod-info">
                    <div className="t">Módulo {m.orden} · {m.titulo.split(" · ").slice(1).join(" · ")}</div>
                    <div className="d">
                      Microlearning · {m.duracion_min} min · {m.xp} XP · tramo N{m.nivel_estandar_origen}
                    </div>
                  </div>
                  {m.completado ? (
                    <button className="btn btn-ghost" onClick={() => p.onAbrirModulo(m.id)}>
                      Repasar
                    </button>
                  ) : (
                    <button className="btn btn-primary" onClick={() => p.onAbrirModulo(m.id)}>
                      {m === siguiente ? "Continuar" : "Abrir"}
                    </button>
                  )}
                </div>
              );
            })}

            <div className="mod-row">
              <div className={`mod-ico ${b.evaluacion_disponible ? "ahora" : "cerrado"}`}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  {b.evaluacion_disponible ? <path d="M9 11l3 3L22 4M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" /> : ICONO.cerrado}
                </svg>
              </div>
              <div className="mod-info">
                <div className="t">Evaluación del bloque</div>
                <div className="d">
                  {b.n_items_por_intento} preguntas · aprobación{" "}
                  {Math.round(Number(b.umbral_aprobacion) * 100)}% ·{" "}
                  {(b.max_reintentos ?? 0) - b.intentos_usados} intentos disponibles
                </div>
              </div>
              {b.obtenida > 0 ? (
                <div className="mod-status" style={{ color: "var(--menta-deep)" }}>aprobada</div>
              ) : b.evaluacion_disponible ? (
                <button className="btn btn-primary" onClick={p.onRendir}>Rendir</button>
              ) : (
                <div className="mod-status">
                  faltan {b.modulos.length - b.modulos_completos} módulos
                </div>
              )}
            </div>
          </div>

          <div className="card reward-card">
            <span className="pill oro">Recompensa del bloque</span>
            <div className="big-badge" aria-hidden="true">
              <svg viewBox="0 0 100 112" fill="none">
                <path d="M50 4 92 24 V60 C92 84 73 100 50 108 C27 100 8 84 8 60 V24 Z"
                  fill={b.obtenida ? "url(#oro)" : "#e8e2e5"} stroke={b.obtenida ? "#c98e10" : "#d5cdd1"} strokeWidth="2" />
                <defs>
                  <linearGradient id="oro" x1="0" y1="0" x2="1" y2="1">
                    <stop stopColor="#F4B740" /><stop offset="1" stopColor="#d99413" />
                  </linearGradient>
                </defs>
                <circle cx="50" cy="48" r="24" fill="#fff" opacity=".9" />
                <text x="50" y="57" textAnchor="middle" fontFamily="Bricolage Grotesque Variable"
                  fontWeight="800" fontSize="22" fill={b.obtenida ? "#a9750d" : "#b3aab0"}>
                  N{b.nivel_estandar}
                </text>
              </svg>
            </div>
            <div className="reward-nombre">{b.medalla}</div>
            <p className="reward-sub">
              {b.obtenida > 0
                ? "Ya la tienes. La respalda tu intento aprobado."
                : <>Aprueba la evaluación para sumar <b className="mono">{b.medalla_xp} XP</b> y abrir el bloque siguiente.</>}
            </p>
            <div className="side-stats">
              <div className="side-stat">
                <span>Módulos vistos</span><b>{b.modulos_completos} / {b.modulos.length}</b>
              </div>
              <div className="side-stat">
                <span>XP de módulos</span><b>{b.modulos.reduce((s, m) => s + (m.completado ? m.xp : 0), 0)}</b>
              </div>
              <div className="side-stat">
                <span>Estado</span><b>{b.estado.replace("_", " ")}</b>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <Marco
      yo={p.yo}
      bloques={p.totalBloques}
      completos={p.bloquesCompletos}
      marcaPrueba={b?.es_contenido_prueba}
      crumb={<><b>Vista colaborador</b> · Mi Ruta · {b?.dimension_nombre ?? "Bloque"}</>}
      onSalir={p.onSalir}
    >
      {cuerpo()}
    </Marco>
  );
}
