import { useEffect, useRef, useState } from "react";
import { SesionCaida, api, type ItemQuiz, type ResultadoQuiz, type Yo } from "../api";
import { Marco } from "../componentes/Marco";

/**
 * Quiz formativo — la mecánica de juego dentro del módulo.
 *
 * Se juega distinto a la evaluación final a propósito (S-07): feedback inmediato
 * en verde y rojo, la correcta a la vista con su explicación, racha y multiplicador.
 * Tiene que sentirse jugar, no rendir.
 *
 * El XP que se ve durante la partida es proyección para el feedback. **El número
 * que vale lo calcula el servidor** al cerrar: si el cliente propusiera su propio
 * XP, el tope y la racha serían decorativos.
 */
type Props = {
  bloqueRutaId: string;
  moduloId: string;
  tituloModulo: string;
  yo: Yo;
  totalBloques: number;
  bloquesCompletos: number;
  onVolver: () => void;
  onXpGanado: () => void;
  onSalir: () => void;
};

type Elegida = { item_id: string; indice_elegido: number };
type Pop = { id: number; texto: string; x: number; y: number };

const XP_BASE = 20;
const XP_POR_RACHA = 10;
const LETRAS = ["A", "B", "C", "D"];

export function Quiz(p: Props) {
  const [items, setItems] = useState<ItemQuiz[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [fase, setFase] = useState<"intro" | "jugando" | "fin">("intro");

  const [indice, setIndice] = useState(0);
  const [elegido, setElegido] = useState<number | null>(null);
  const [racha, setRacha] = useState(0);
  const [xpProyectado, setXpProyectado] = useState(0);
  const [respuestas, setRespuestas] = useState<Elegida[]>([]);
  const [pops, setPops] = useState<Pop[]>([]);
  const [resultado, setResultado] = useState<ResultadoQuiz | null>(null);
  const [cerrando, setCerrando] = useState(false);
  const contadorPop = useRef(0);

  useEffect(() => {
    api.quiz(p.moduloId)
      .then(setItems)
      .catch((e) => (e instanceof SesionCaida ? p.onSalir() : setError(e.message)));
  }, [p.moduloId]);

  function empezar() {
    setIndice(0);
    setElegido(null);
    setRacha(0);
    setXpProyectado(0);
    setRespuestas([]);
    setResultado(null);
    setFase("jugando");
  }

  function responder(k: number, evento: React.MouseEvent<HTMLButtonElement>) {
    if (elegido !== null || !items) return;
    const item = items[indice];
    const acerto = k === item.indice_correcta;

    setElegido(k);
    setRespuestas((r) => [...r, { item_id: item.id, indice_elegido: k }]);

    if (acerto) {
      const nueva = racha + 1;
      const ganado = XP_BASE + nueva * XP_POR_RACHA;
      setRacha(nueva);
      setXpProyectado((x) => x + ganado);

      const caja = evento.currentTarget.getBoundingClientRect();
      const id = ++contadorPop.current;
      setPops((ps) => [
        ...ps,
        { id, texto: `+${ganado}${nueva >= 3 ? " 🔥" : ""}`, x: caja.left + caja.width / 2, y: caja.top },
      ]);
      setTimeout(() => setPops((ps) => ps.filter((x) => x.id !== id)), 1000);
    } else {
      setRacha(0);
    }
  }

  async function avanzar() {
    if (!items) return;
    if (indice + 1 < items.length) {
      setIndice(indice + 1);
      setElegido(null);
      return;
    }
    // Última: el servidor recalcula todo y su número es el que vale.
    setCerrando(true);
    try {
      setResultado(await api.resultadoQuiz(p.moduloId, respuestas));
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
    if (!items) return <div className="cargando">preparando la práctica…</div>;

    if (fase === "intro")
      return (
        <div className="pantalla">
          <button className="volver" onClick={p.onVolver}>← Volver al módulo</button>
          <div className="juego-stage">
            <div className="juego-intro">
              <div className="juego-emoji" aria-hidden="true">⚡</div>
              <h2>Practica lo que acabas de leer</h2>
              <p>
                {items.length} preguntas del módulo. Cada acierto seguido sube tu racha y
                multiplica el XP; un error la vuelve a cero. Es para aprender: el XP es de
                juego y no cuenta para tu acreditación.
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
              <div className="juego-emoji" aria-hidden="true">🏅</div>
              <div className="fin-titulo">¡Práctica terminada!</div>
              <div className="fin-sub">
                {resultado.ya_jugado_hoy
                  ? "Ya habías practicado este módulo hoy, así que esta vez no suma XP."
                  : "Ganaste para tu ranking"}
              </div>
              <div className="fin-xp">+{resultado.xp_otorgado} XP</div>
              <div className="fin-stats">
                <div>
                  <div className="n" style={{ color: "var(--menta)" }}>
                    {resultado.aciertos}/{resultado.total}
                  </div>
                  <div className="l">Correctas</div>
                </div>
                <div>
                  <div className="n" style={{ color: "var(--oro)" }}>×{resultado.mejor_racha}</div>
                  <div className="l">Mejor racha</div>
                </div>
              </div>
              <p className="fin-nota">
                El XP de práctica cuenta para el ranking, no para tu escalón ni para la
                medalla: esa llega solo con la evaluación del bloque aprobada.
              </p>
              <div className="fin-acciones">
                <button className="btn btn-oro" onClick={empezar}>Practicar de nuevo</button>
                <button className="btn btn-oscuro" onClick={p.onVolver}>Volver al módulo</button>
              </div>
            </div>
          </div>
        </div>
      );

    const item = items[indice];
    const respondida = elegido !== null;

    return (
      <div className="pantalla">
        <button className="volver" onClick={p.onVolver}>← Salir de la práctica</button>

        <div className="juego-stage">
          <div className="juego-hud">
            <div className="hud-chip oro"><span className="lbl">XP</span> {xpProyectado}</div>
            <div className="hud-chip racha"><span className="lbl">Racha</span> ×{racha}</div>
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
              const esCorrecta = k === item.indice_correcta;
              const clase = !respondida
                ? ""
                : esCorrecta
                  ? "ok"
                  : k === elegido
                    ? "mal"
                    : "";
              return (
                <button
                  key={k}
                  className={`t-opt ${clase}`}
                  onClick={(e) => responder(k, e)}
                  disabled={respondida}
                  aria-label={`Alternativa ${LETRAS[k]}: ${alt}`}
                >
                  <span className="key">{LETRAS[k]}</span>
                  <span>{alt}</span>
                </button>
              );
            })}
          </div>

          {respondida && (
            <div className={`feedback ${elegido === item.indice_correcta ? "ok" : "mal"}`} role="status">
              <b>
                {elegido === item.indice_correcta
                  ? `¡Correcto! +${XP_BASE + racha * XP_POR_RACHA} XP`
                  : `No era esa. La correcta es la ${LETRAS[item.indice_correcta]}.`}
              </b>
              <p>{item.explicaciones[elegido!]}</p>
              {elegido !== item.indice_correcta && (
                <p className="por-que-si">
                  <b>{LETRAS[item.indice_correcta]}:</b> {item.explicaciones[item.indice_correcta]}
                </p>
              )}
              <button className="btn btn-oro" onClick={avanzar} disabled={cerrando}>
                {cerrando
                  ? "cerrando…"
                  : indice + 1 < items.length ? "Siguiente →" : "Ver resultado →"}
              </button>
            </div>
          )}
        </div>

        {pops.map((pop) => (
          <div key={pop.id} className="combo-pop" style={{ left: pop.x, top: pop.y }}>
            {pop.texto}
          </div>
        ))}
      </div>
    );
  };

  return (
    <Marco
      yo={p.yo}
      bloques={p.totalBloques}
      completos={p.bloquesCompletos}
      crumb={<><b>Vista colaborador</b> · {p.tituloModulo} · Práctica</>}
      onSalir={p.onSalir}
    >
      {cuerpo()}
    </Marco>
  );
}
