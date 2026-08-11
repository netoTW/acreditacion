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
  onAbrirDesafio: () => void;
  onAbrirJuego: () => void;
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

          {/* Por qué este bloque exige lo que exige. Sin esto, el 85% y el desafío
              parecen arbitrarios en vez de consecuencia del peso del rol. */}
          <div className={`banda-exigencia ${b.es_critica ? "critica" : ""}`}>
            {b.es_critica ? (
              <>
                <b>Ruta crítica de tu rol.</b> Esta dimensión pesa{" "}
                <b>{Math.round(Number(b.peso_ranking) * 100)}%</b> de tu impacto, así que
                lleva un <b>desafío aplicado</b> antes de la evaluación, se aprueba con{" "}
                <b>85%</b> y su medalla es de <b>oro</b>.
              </>
            ) : (
              <>
                <b>Dimensión estándar.</b> Pesa{" "}
                <b>{Math.round(Number(b.peso_ranking) * 100)}%</b> de tu rol: mismo
                recorrido, aprobación al <b>80%</b> y medalla de <b>plata</b>.
              </>
            )}
          </div>
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

            {/* Cada dimensión lleva su propio juego. Mientras no exista se muestra
                el hueco en vez de ocultarlo: la estructura que AIEP definió tiene
                cuatro piezas y hay que poder ver cuál falta. */}
            <div className="mod-row">
              <div className={`mod-ico ${b.juego ? "ahora" : "cerrado"}`}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="2" y="7" width="20" height="12" rx="3" />
                  <path d="M7 11v4M5 13h4M16 12h.01M18.5 15h.01" />
                </svg>
              </div>
              <div className="mod-info">
                <div className="t">{b.juego?.nombre ?? `Juego de ${b.dimension_nombre}`}</div>
                <div className="d">
                  {b.juego
                    ? `${b.juego.descripcion} · XP de juego, no acreditable`
                    : "Cada dimensión lleva el suyo · se construye en la fase 2"}
                </div>
              </div>
              {b.juego ? (
                <button className="btn btn-primary" onClick={p.onAbrirJuego}>Jugar</button>
              ) : (
                <div className="mod-status">en construcción</div>
              )}
            </div>

            {b.es_critica && (
              <div className="mod-row">
                <div className={`mod-ico ${b.desafio_pendiente ? "ahora" : "completo"}`}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    {b.desafio_pendiente ? ICONO.ahora : ICONO.completo}
                  </svg>
                </div>
                <div className="mod-info">
                  <div className="t">
                    Desafío aplicado <span className="chip-critica">ruta crítica</span>
                  </div>
                  <div className="d">
                    Un caso real con decisiones · requisito para rendir · da XP de juego,
                    no acreditable
                  </div>
                </div>
                {b.desafio_pendiente ? (
                  <button className="btn btn-primary" onClick={p.onAbrirDesafio}>
                    {b.modulos_completos === b.modulos.length ? "Entrar al caso" : "Ver el caso"}
                  </button>
                ) : (
                  <button className="btn btn-ghost" onClick={p.onAbrirDesafio}>Revisar</button>
                )}
              </div>
            )}

            <div className="mod-row">
              <div className={`mod-ico ${b.evaluacion_disponible ? "ahora" : "cerrado"}`}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  {b.evaluacion_disponible ? <path d="M9 11l3 3L22 4M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" /> : ICONO.cerrado}
                </svg>
              </div>
              <div className="mod-info">
                <div className="t">
                  Evaluación {b.es_critica ? "reforzada" : "del bloque"}
                </div>
                <div className="d">
                  {b.n_items_por_intento} preguntas · aprobación{" "}
                  <b>{Math.round(Number(b.umbral_aprobacion) * 100)}%</b> ·{" "}
                  {(b.max_reintentos ?? 0) - b.intentos_usados} intentos disponibles
                </div>
              </div>
              {b.obtenida > 0 ? (
                <div className="mod-status" style={{ color: "var(--menta-deep)" }}>aprobada</div>
              ) : b.evaluacion_disponible ? (
                <button className="btn btn-primary" onClick={p.onRendir}>Rendir</button>
              ) : (
                <div className="mod-status">
                  {b.modulos_completos < b.modulos.length
                    ? `faltan ${b.modulos.length - b.modulos_completos} módulos`
                    : "falta el desafío"}
                </div>
              )}
            </div>
          </div>

          <div className="card reward-card">
            <span className={`pill ${b.medalla_tipo === "gold" ? "oro" : "menta"}`}>
              Medalla de {b.medalla_tipo === "gold" ? "oro" : "plata"}
            </span>
            <div className="big-badge" aria-hidden="true">
              <svg viewBox="0 0 100 112" fill="none">
                <path d="M50 4 92 24 V60 C92 84 73 100 50 108 C27 100 8 84 8 60 V24 Z"
                  fill={b.obtenida ? (b.medalla_tipo === "gold" ? "url(#oro)" : "url(#plata)") : "#e8e2e5"}
                  stroke={b.obtenida ? (b.medalla_tipo === "gold" ? "#c98e10" : "#9aa4ad") : "#d5cdd1"}
                  strokeWidth="2" />
                <defs>
                  <linearGradient id="oro" x1="0" y1="0" x2="1" y2="1">
                    <stop stopColor="#F4B740" /><stop offset="1" stopColor="#d99413" />
                  </linearGradient>
                  <linearGradient id="plata" x1="0" y1="0" x2="1" y2="1">
                    <stop stopColor="#dfe6ec" /><stop offset="1" stopColor="#aab6c0" />
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
                : b.es_critica
                  ? <>La de oro se <b>gana</b>: resolver el desafío y aprobar al 85% suma{" "}
                     <b className="mono">{b.medalla_xp} XP</b>. No la reparte tu rol.</>
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
