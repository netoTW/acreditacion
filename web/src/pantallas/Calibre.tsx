import { useEffect, useState } from "react";
import { SesionCaida, api, type ItemQuiz, type ResultadoCalibre, type Yo } from "../api";
import { Marco } from "../componentes/Marco";

/**
 * M1 «Calibre» — el juego de módulo.
 *
 * No se juega a saber la respuesta: se juega a saber **cuánto sabes**. Se elige
 * alternativa y después se declara confianza, y decir «Seguro» y fallar resta.
 *
 * Sin reloj, a propósito: la tensión sale de la apuesta, no de la prisa. Un
 * temporizador acá solo mediría velocidad de lectura.
 *
 * El puntaje que se muestra durante la partida es proyección. **El que vale lo
 * calcula el servidor** al cerrar.
 */
type Props = {
  bloqueRutaId: string;
  moduloId: string;
  yo: Yo;
  totalBloques: number;
  bloquesCompletos: number;
  onVolver: () => void;
  onXpGanado: () => void;
  onSalir: () => void;
};

type Jugada = { item_id: string; indice_elegido: number; seguro: boolean };
const LETRAS = ["A", "B", "C", "D"];
const PUNTOS = { seguroBien: 60, seguroMal: -40, creoBien: 25, creoMal: 0 };

export function Calibre(p: Props) {
  const [items, setItems] = useState<ItemQuiz[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [fase, setFase] = useState<"intro" | "jugando" | "fin">("intro");

  const [indice, setIndice] = useState(0);
  const [elegida, setElegida] = useState<number | null>(null);
  const [seguro, setSeguro] = useState<boolean | null>(null);
  const [puntos, setPuntos] = useState(0);
  const [delta, setDelta] = useState<number | null>(null);
  const [jugadas, setJugadas] = useState<Jugada[]>([]);
  const [resultado, setResultado] = useState<ResultadoCalibre | null>(null);
  const [cerrando, setCerrando] = useState(false);

  useEffect(() => {
    api.quiz(p.moduloId)
      .then(setItems)
      .catch((e) => (e instanceof SesionCaida ? p.onSalir() : setError(e.message)));
  }, [p.moduloId]);

  function empezar() {
    setIndice(0); setElegida(null); setSeguro(null);
    setPuntos(0); setDelta(null); setJugadas([]); setResultado(null);
    setFase("jugando");
  }

  function apostar(confiado: boolean) {
    if (!items || elegida === null || seguro !== null) return;
    const item = items[indice];
    const acerto = elegida === item.indice_correcta;
    const gana = confiado
      ? acerto ? PUNTOS.seguroBien : PUNTOS.seguroMal
      : acerto ? PUNTOS.creoBien : PUNTOS.creoMal;

    setSeguro(confiado);
    setPuntos((x) => x + gana);
    setDelta(gana);
    setJugadas((j) => [...j, { item_id: item.id, indice_elegido: elegida, seguro: confiado }]);
  }

  async function avanzar() {
    if (!items) return;
    setDelta(null);
    if (indice + 1 < items.length) {
      setIndice(indice + 1);
      setElegida(null);
      setSeguro(null);
      return;
    }
    setCerrando(true);
    try {
      setResultado(await api.resultadoCalibre(p.moduloId, jugadas));
      p.onXpGanado();
      setFase("fin");
    } catch (e) {
      if (e instanceof SesionCaida) p.onSalir();
      else setError(e instanceof Error ? e.message : "no se pudo cerrar la partida");
    } finally {
      setCerrando(false);
    }
  }

  const cuerpo = () => {
    if (error)
      return (
        <div className="error">
          <p>{error}</p>
          <button className="btn btn-primary" style={{ marginTop: 14 }} onClick={p.onVolver}>
            Volver al módulo
          </button>
        </div>
      );
    if (!items) return <div className="cargando">preparando Calibre…</div>;

    if (fase === "intro")
      return (
        <div className="pantalla">
          <button className="volver" onClick={p.onVolver}>← Volver al módulo</button>
          <div className="juego-stage">
            <div className="juego-intro">
              <div className="juego-emoji" aria-hidden="true">🎯</div>
              <h2>Calibre</h2>
              <p>
                {items.length} preguntas, sin reloj. En cada una eliges tu respuesta y después
                declaras cuánto te la juegas. <b>Acertar diciendo «Seguro» paga más del doble;
                fallar diciéndolo, resta.</b>
              </p>
              <table className="tabla-apuesta">
                <thead><tr><th></th><th>Aciertas</th><th>Fallas</th></tr></thead>
                <tbody>
                  <tr><td><b>Seguro</b></td><td className="sube">+60</td><td className="baja">−40</td></tr>
                  <tr><td>Creo que sí</td><td className="sube">+25</td><td>0</td></tr>
                </tbody>
              </table>
              <p className="intro-bono">
                Si todos tus «Seguro» resultan correctos: <b>+50 por calibrado</b>.
              </p>
              <button className="btn btn-oro" onClick={empezar}>Comenzar →</button>
            </div>
          </div>
        </div>
      );

    if (fase === "fin" && resultado)
      return (
        <div className="pantalla">
          <div className="juego-stage">
            <div className="juego-fin">
              <div className="juego-emoji" aria-hidden="true">{resultado.bono_calibrado ? "🎯" : "📊"}</div>
              <div className="fin-titulo">
                {resultado.bono_calibrado ? "¡Bien calibrado!" : "Partida terminada"}
              </div>
              <div className="fin-sub">
                {resultado.ya_jugado_hoy
                  ? "Ya habías jugado este módulo hoy, así que esta vez no suma XP."
                  : resultado.bono_calibrado
                    ? "Acertaste todo lo que dijiste saber"
                    : "Ganaste para tu ranking"}
              </div>
              <div className="fin-xp">+{resultado.xp_otorgado} XP</div>

              <div className="fin-stats">
                <div>
                  <div className="n" style={{ color: "var(--menta)" }}>{resultado.aciertos}/{resultado.total}</div>
                  <div className="l">Correctas</div>
                </div>
                <div>
                  <div className="n" style={{ color: "var(--oro)" }}>
                    {resultado.seguros_acertados}/{resultado.seguros}
                  </div>
                  <div className="l">«Seguro» acertados</div>
                </div>
                <div>
                  <div className="n" style={{ color: resultado.puntos < 0 ? "var(--carmin-soft)" : "#fff" }}>
                    {resultado.puntos}
                  </div>
                  <div className="l">Puntos</div>
                </div>
              </div>

              <p className="fin-nota">
                {resultado.seguros === 0
                  ? "No arriesgaste ninguna. El bono premia calibración: hay que decir «Seguro» y acertar."
                  : resultado.bono_calibrado
                    ? "Sabías lo que sabías: eso es exactamente lo que mide este juego."
                    : "Algún «Seguro» falló. Distinguir lo que suena bien de lo que corresponde es la habilidad del bloque."}
              </p>
              <p className="fin-nota">
                Es XP de juego: cuenta para el ranking, no para tu escalón ni para la medalla.
              </p>

              <div className="fin-acciones">
                <button className="btn btn-oro" onClick={empezar}>Jugar de nuevo</button>
                <button className="btn btn-oscuro" onClick={p.onVolver}>Volver al módulo</button>
              </div>
            </div>
          </div>
        </div>
      );

    const item = items[indice];
    const cerrada = seguro !== null;
    const acerto = elegida === item.indice_correcta;

    return (
      <div className="pantalla">
        <button className="volver" onClick={p.onVolver}>← Salir de Calibre</button>

        <div className="juego-stage">
          <div className="juego-hud">
            <div className={`hud-chip ${puntos < 0 ? "negativo" : "oro"}`}>
              <span className="lbl">Puntos</span> {puntos}
              {delta !== null && (
                <span className={`delta ${delta < 0 ? "baja" : "sube"}`}>
                  {delta > 0 ? `+${delta}` : delta}
                </span>
              )}
            </div>
            <div className="hud-progreso">
              <div className="hud-track">
                <div className="hud-fill" style={{ width: `${((indice + 1) / items.length) * 100}%` }} />
              </div>
            </div>
            <div className="hud-chip"><span className="lbl">Pregunta</span> {indice + 1}/{items.length}</div>
          </div>

          <div className="juego-pregunta">{item.enunciado}</div>

          <div className="juego-opciones">
            {item.alternativas.map((alt, k) => {
              // Antes de apostar no hay verde ni rojo: solo "esta elegiste".
              const clase = !cerrada
                ? elegida === k ? "marcada" : ""
                : k === item.indice_correcta ? "ok" : k === elegida ? "mal" : "";
              return (
                <button
                  key={k}
                  className={`t-opt ${clase}`}
                  onClick={() => !cerrada && setElegida(k)}
                  disabled={cerrada}
                  aria-pressed={elegida === k}
                >
                  <span className="key">{LETRAS[k]}</span>
                  <span>{alt}</span>
                </button>
              );
            })}
          </div>

          {elegida !== null && !cerrada && (
            <div className="apuesta" role="group" aria-label="¿Cuánto te la juegas?">
              <div className="apuesta-titulo">¿Cuánto te la juegas?</div>
              <div className="apuesta-botones">
                <button className="apuesta-btn seguro" onClick={() => apostar(true)}>
                  <b>Seguro</b>
                  <span>+60 si aciertas · −40 si fallas</span>
                </button>
                <button className="apuesta-btn creo" onClick={() => apostar(false)}>
                  <b>Creo que sí</b>
                  <span>+25 si aciertas · 0 si fallas</span>
                </button>
              </div>
            </div>
          )}

          {cerrada && (
            <div className={`feedback ${acerto ? "ok" : "mal"}`} role="status">
              <b>
                {acerto
                  ? seguro ? "Bien jugado. +60" : "Correcta. +25"
                  : seguro ? "Dijiste «Seguro» y no era. −40" : `No era esa. La correcta es la ${LETRAS[item.indice_correcta]}.`}
              </b>
              <p>{item.explicaciones[elegida!]}</p>
              {!acerto && (
                <p className="por-que-si">
                  <b>{LETRAS[item.indice_correcta]}:</b> {item.explicaciones[item.indice_correcta]}
                </p>
              )}
              <button className="btn btn-oro" onClick={avanzar} disabled={cerrando}>
                {cerrando ? "cerrando…" : indice + 1 < items.length ? "Siguiente →" : "Ver resultado →"}
              </button>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <Marco
      yo={p.yo}
      bloques={p.totalBloques}
      completos={p.bloquesCompletos}
      crumb={<><b>Vista colaborador</b> · Módulo · Calibre</>}
      onSalir={p.onSalir}
    >
      {cuerpo()}
    </Marco>
  );
}
