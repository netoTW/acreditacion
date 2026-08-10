import { useEffect, useState } from "react";
import {
  SesionCaida, api,
  type Intento, type ResultadoEvaluacion, type Yo,
} from "../api";
import { Marco } from "../componentes/Marco";

/**
 * Evaluación final — deliberadamente lo contrario al quiz formativo.
 *
 * Sobria, sin colores de acierto, sin racha y sin corrección pregunta a pregunta.
 * El resultado llega al final y las respuestas correctas **no se revelan nunca**,
 * ni aprobando ni reprobando (§7): es la nota que respalda la acreditación, y
 * revelarlas convertiría el reintento en un ejercicio de memoria.
 *
 * Cada respuesta se guarda al elegirla (S-14): cerrar el navegador no pierde nada.
 */
type Props = {
  bloqueRutaId: string;
  yo: Yo;
  totalBloques: number;
  bloquesCompletos: number;
  onVolver: () => void;
  onCambio: () => void;
  onSalir: () => void;
};

const LETRAS = ["A", "B", "C", "D"];

export function Evaluacion(p: Props) {
  const [intento, setIntento] = useState<Intento | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [indice, setIndice] = useState(0);
  const [guardando, setGuardando] = useState(false);
  const [confirmando, setConfirmando] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [resultado, setResultado] = useState<ResultadoEvaluacion | null>(null);

  useEffect(() => {
    api.abrirIntento(p.bloqueRutaId)
      .then((r) => api.intento(r.intento_id))
      .then((i) => {
        setIntento(i);
        // Se retoma en la primera sin responder, no siempre en la uno.
        const pendiente = i.items.findIndex((x) => !(x.item_id in i.respuestas));
        setIndice(pendiente === -1 ? 0 : pendiente);
      })
      .catch((e) => (e instanceof SesionCaida ? p.onSalir() : setError(e.message)));
  }, [p.bloqueRutaId]);

  async function elegir(item_id: string, k: number) {
    if (!intento) return;
    setIntento({ ...intento, respuestas: { ...intento.respuestas, [item_id]: k } });
    setGuardando(true);
    try {
      await api.guardarRespuesta(intento.id, item_id, k);
    } catch (e) {
      if (e instanceof SesionCaida) p.onSalir();
      else setError(e instanceof Error ? e.message : "no se pudo guardar la respuesta");
    } finally {
      setGuardando(false);
    }
  }

  async function enviar() {
    if (!intento) return;
    setEnviando(true);
    try {
      setResultado(await api.cerrarIntento(intento.id));
      p.onCambio();
    } catch (e) {
      if (e instanceof SesionCaida) p.onSalir();
      else setError(e instanceof Error ? e.message : "no se pudo enviar");
    } finally {
      setEnviando(false);
      setConfirmando(false);
    }
  }

  const cuerpo = () => {
    if (error)
      return (
        <div className="error">
          <p>{error}</p>
          <button className="btn btn-primary" style={{ marginTop: 14 }} onClick={p.onVolver}>
            Volver al bloque
          </button>
        </div>
      );
    if (!intento) return <div className="cargando">preparando la evaluación…</div>;

    const umbral = Math.round(Number(intento.umbral_aprobacion) * 100);

    // ---------------------------------------------------------- resultado
    if (resultado) {
      const pct = Math.round(resultado.puntaje * 100);
      return (
        <div className="pantalla">
          <div className={`resultado ${resultado.aprobado ? "aprobado" : "reprobado"}`}>
            <div className="res-marca">
              {resultado.aprobado ? "Evaluación aprobada" : "Evaluación no aprobada"}
            </div>
            <div className="res-puntaje">{pct}%</div>
            <div className="res-umbral">se requiere {umbral}% · intento {intento.numero_intento}</div>

            {resultado.aprobado ? (
              <>
                <div className="res-medalla">
                  <svg viewBox="0 0 100 112" aria-hidden="true">
                    <path d="M50 4 92 24 V60 C92 84 73 100 50 108 C27 100 8 84 8 60 V24 Z"
                      fill="url(#oroRes)" stroke="#c98e10" strokeWidth="2" />
                    <defs>
                      <linearGradient id="oroRes" x1="0" y1="0" x2="1" y2="1">
                        <stop stopColor="#F4B740" /><stop offset="1" stopColor="#d99413" />
                      </linearGradient>
                    </defs>
                    <circle cx="50" cy="48" r="24" fill="#fff" opacity=".9" />
                    <text x="50" y="57" textAnchor="middle" fontFamily="Bricolage Grotesque Variable"
                      fontWeight="800" fontSize="22" fill="#a9750d">N{intento.nivel_estandar}</text>
                  </svg>
                </div>
                <p className="res-texto">
                  Ganaste la medalla de <b>{intento.dimension_nombre} · N{intento.nivel_estandar}</b> y{" "}
                  <b className="mono">{resultado.xp_otorgado} XP acreditable</b>. Queda respaldada por
                  este intento: si alguien pregunta con qué evidencia se otorgó, la respuesta es esta
                  prueba, con su puntaje y su fecha.
                </p>
              </>
            ) : (
              <p className="res-texto">
                No se revelan las respuestas correctas, a propósito: el reintento tiene que
                medir lo que sabes, no lo que recuerdas de la prueba anterior. Vuelve a los
                módulos del bloque y rinde de nuevo.
                {resultado.reintentos_restantes > 0
                  ? ` Te quedan ${resultado.reintentos_restantes} intentos.`
                  : " Se te acabaron los intentos: el bloque queda esperando acompañamiento y no se otorga la medalla."}
              </p>
            )}

            <div className="res-acciones">
              <button className="btn btn-primary" onClick={p.onVolver}>Volver al bloque</button>
            </div>
          </div>
        </div>
      );
    }

    // ------------------------------------------------------------ rindiendo
    const item = intento.items[indice];
    const elegida = intento.respuestas[item.item_id];
    const respondidas = intento.items.filter((x) => x.item_id in intento.respuestas).length;
    const completa = respondidas === intento.items.length;

    return (
      <div className="pantalla">
        <div className="eval">
          <div className="eval-cabecera">
            <div>
              <div className="eyebrow">Evaluación del bloque · intento {intento.numero_intento} de {intento.max_reintentos}</div>
              <h1>{intento.dimension_nombre}</h1>
            </div>
            <div className="eval-meta">
              <div><b>{umbral}%</b><span>para aprobar</span></div>
              <div><b>{respondidas}/{intento.items.length}</b><span>respondidas</span></div>
            </div>
          </div>

          <div className="eval-aviso">
            El resultado se entrega al final. No hay corrección pregunta a pregunta y las
            respuestas correctas no se muestran. <b>Tus respuestas se guardan solas</b>: si
            cierras esto, al volver retomas donde ibas.
          </div>

          <div className="eval-pasos">
            {intento.items.map((x, n) => (
              <button
                key={x.item_id}
                className={`paso ${n === indice ? "actual" : ""} ${x.item_id in intento.respuestas ? "hecha" : ""}`}
                onClick={() => setIndice(n)}
                aria-label={`Ir a la pregunta ${n + 1}${x.item_id in intento.respuestas ? ", respondida" : ""}`}
              >
                {n + 1}
              </button>
            ))}
          </div>

          <div className="card eval-card">
            <div className="eval-num">Pregunta {indice + 1} de {intento.items.length}</div>
            <div className="eval-pregunta">{item.enunciado}</div>

            <div className="eval-opciones" role="radiogroup" aria-label="Alternativas">
              {item.alternativas.map((alt, k) => (
                <button
                  key={k}
                  role="radio"
                  aria-checked={elegida === k}
                  className={`eval-opt ${elegida === k ? "elegida" : ""}`}
                  onClick={() => elegir(item.item_id, k)}
                >
                  <span className="key">{LETRAS[k]}</span>
                  <span>{alt}</span>
                </button>
              ))}
            </div>

            <div className="eval-pie">
              <span className="eval-guardado">{guardando ? "guardando…" : elegida !== undefined ? "respuesta guardada" : ""}</span>
              <div className="eval-nav">
                <button className="btn btn-ghost" disabled={indice === 0} onClick={() => setIndice(indice - 1)}>
                  ← Anterior
                </button>
                {indice + 1 < intento.items.length ? (
                  <button className="btn btn-primary" onClick={() => setIndice(indice + 1)}>Siguiente →</button>
                ) : (
                  <button className="btn btn-primary" disabled={!completa} onClick={() => setConfirmando(true)}>
                    {completa ? "Enviar evaluación" : `Faltan ${intento.items.length - respondidas}`}
                  </button>
                )}
              </div>
            </div>
          </div>

          <button className="volver" onClick={p.onVolver}>Salir y seguir después</button>
        </div>

        {confirmando && (
          <div className="modal-velo" onClick={() => setConfirmando(false)}>
            <div className="modal" onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
              <h2>¿Enviar la evaluación?</h2>
              <p>
                Se corrige y se cierra este intento. No podrás cambiar respuestas.
                Si apruebas con {umbral}% o más, se otorga la medalla del bloque.
              </p>
              <div className="modal-acciones">
                <button className="btn btn-ghost" onClick={() => setConfirmando(false)}>Revisar antes</button>
                <button className="btn btn-primary" onClick={enviar} disabled={enviando}>
                  {enviando ? "corrigiendo…" : "Enviar"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <Marco
      yo={p.yo}
      bloques={p.totalBloques}
      completos={p.bloquesCompletos}
      crumb={<><b>Vista colaborador</b> · {intento?.dimension_nombre ?? "Bloque"} · Evaluación</>}
      onSalir={p.onSalir}
    >
      {cuerpo()}
    </Marco>
  );
}
