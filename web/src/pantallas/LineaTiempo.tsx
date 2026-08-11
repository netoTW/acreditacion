import { useEffect, useState } from "react";
import { SesionCaida, api, type CartaHito, type LineaRepartida, type ResultadoLinea, type Yo } from "../api";
import { Marco } from "../componentes/Marco";

/**
 * D3 Aseguramiento — «Línea de tiempo del proceso».
 *
 * No se responde: se **acomoda una secuencia**. Seis hitos reales del proceso de
 * AIEP, desordenados, y hay que dejarlos en el orden en que ocurren.
 *
 * Dos formas de mover, igual que en la Mesa: arrastrar con el ratón, y subir/bajar
 * con botones —que además funcionan con teclado—. Un juego de arrastrar que solo
 * anda con ratón deja fuera justo a quien lo va a usar en el teléfono.
 */
type Props = {
  bloqueRutaId: string;
  yo: Yo;
  totalBloques: number;
  bloquesCompletos: number;
  onVolver: () => void;
  onXpGanado: () => void;
  onSalir: () => void;
};

const FASE: Record<string, string> = {
  autoevaluacion: "Autoevaluación · 2026",
  acreditacion: "Acreditación · 2027",
};

export function LineaTiempo(p: Props) {
  const [linea, setLinea] = useState<LineaRepartida | null>(null);
  const [orden, setOrden] = useState<CartaHito[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [tomada, setTomada] = useState<string | null>(null);
  const [resultado, setResultado] = useState<ResultadoLinea | null>(null);
  const [cerrando, setCerrando] = useState(false);

  const repartir = () => {
    setResultado(null);
    setTomada(null);
    api.lineaTiempo(p.bloqueRutaId)
      .then((l) => { setLinea(l); setOrden(l.cartas); })
      .catch((e) => (e instanceof SesionCaida ? p.onSalir() : setError(e.message)));
  };

  useEffect(repartir, [p.bloqueRutaId]);

  function mover(desde: number, hasta: number) {
    if (hasta < 0 || hasta >= orden.length) return;
    const copia = [...orden];
    const [carta] = copia.splice(desde, 1);
    copia.splice(hasta, 0, carta);
    setOrden(copia);
  }

  function soltarSobre(indice: number) {
    if (!tomada) return;
    const desde = orden.findIndex((c) => c.hito_id === tomada);
    if (desde >= 0) mover(desde, indice);
    setTomada(null);
  }

  async function cerrar() {
    setCerrando(true);
    try {
      const r = await api.cerrarLinea(p.bloqueRutaId, orden.map((c) => c.hito_id));
      setResultado(r);
      p.onXpGanado();
    } catch (e) {
      if (e instanceof SesionCaida) p.onSalir();
      else setError(e instanceof Error ? e.message : "no se pudo cerrar la línea");
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
            Volver al bloque
          </button>
        </div>
      );
    if (!linea) return <div className="cargando">barajando los hitos…</div>;

    return (
      <div className="pantalla">
        <button className="volver" onClick={p.onVolver}>← Volver al bloque</button>

        <div className="pantalla-head">
          <div className="eyebrow">Juego de Aseguramiento Interno de la Calidad</div>
          <h1>¿En qué orden ocurre el proceso?</h1>
          <p>
            Seis hitos reales de la ruta de AIEP, barajados. Déjalos de{" "}
            <b>lo que pasa primero</b> a <b>lo que pasa último</b>. Puedes moverlos
            cuantas veces quieras; se corrige al cerrar la línea.
          </p>
        </div>

        {resultado ? (
          <ResultadoLineaVista r={resultado} onOtra={repartir} onVolver={p.onVolver} />
        ) : (
          <>
            <ol className="linea">
              {orden.map((c, i) => (
                <li
                  key={c.hito_id}
                  className={`hito-fila ${tomada === c.hito_id ? "tomada" : ""}`}
                  draggable
                  onDragStart={() => setTomada(c.hito_id)}
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={(e) => { e.preventDefault(); soltarSobre(i); }}
                  onDragEnd={() => setTomada(null)}
                >
                  <span className="hito-pos">{i + 1}</span>
                  <span className="hito-titulo">{c.titulo}</span>
                  <span className="hito-mover">
                    <button
                      className="mover-btn"
                      disabled={i === 0}
                      aria-label={`Subir: ${c.titulo}`}
                      onClick={() => mover(i, i - 1)}
                    >
                      ▲
                    </button>
                    <button
                      className="mover-btn"
                      disabled={i === orden.length - 1}
                      aria-label={`Bajar: ${c.titulo}`}
                      onClick={() => mover(i, i + 1)}
                    >
                      ▼
                    </button>
                  </span>
                </li>
              ))}
            </ol>

            <div className="linea-pie">
              <span className="linea-pista">
                Cada par que quede en el orden correcto suma, aunque la línea no
                quede perfecta.
              </span>
              <button className="btn btn-primary" disabled={cerrando} onClick={cerrar}>
                {cerrando ? "corrigiendo…" : "Cerrar la línea"}
              </button>
            </div>
          </>
        )}
      </div>
    );
  };

  return (
    <Marco
      yo={p.yo}
      bloques={p.totalBloques}
      completos={p.bloquesCompletos}
      crumb={<><b>Vista colaborador</b> · Línea de tiempo</>}
      onSalir={p.onSalir}
    >
      {cuerpo()}
    </Marco>
  );
}

/** La revelación: la secuencia real, con el período que durante el juego no se veía. */
function ResultadoLineaVista(
  { r, onOtra, onVolver }: { r: ResultadoLinea; onOtra: () => void; onVolver: () => void },
) {
  return (
    <>
      <div className={`linea-resultado ${r.linea_perfecta ? "perfecta" : ""}`}>
        <div className="lr-marca">{r.linea_perfecta ? "Línea perfecta" : "Línea cerrada"}</div>
        <div className="lr-puntaje">
          {r.pares_correctos} <span>/ {r.pares_totales}</span>
        </div>
        <div className="lr-sub">pares en el orden correcto</div>
        <div className="lr-xp">
          +{r.xp_otorgado} XP de juego
          {r.ya_jugado_hoy && <span className="lr-nota">ya jugaste hoy, esta no suma</span>}
        </div>
        <p className="lr-texto">
          {r.linea_perfecta
            ? "Los seis en su lugar. Saber en qué orden ocurre el proceso es lo que permite anticiparlo en vez de reaccionar."
            : `Dejaste ${r.en_su_lugar} de ${r.total} en su casilla exacta. Abajo va la secuencia real con su período.`}
        </p>
        <div className="lr-acciones">
          <button className="btn btn-primary" onClick={onOtra}>Otros seis hitos</button>
          <button className="btn btn-ghost" onClick={onVolver}>Volver al bloque</button>
        </div>
      </div>

      <ol className="linea revelada">
        {r.revelacion.map((h) => (
          <li key={h.hito_id} className={`hito-fila ${h.acerto ? "bien" : "mal"}`}>
            <span className="hito-pos">{h.posicion_real}</span>
            <span className="hito-titulo">
              {h.titulo}
              <span className="hito-cuando">
                {FASE[h.ruta] ?? h.ruta} · {h.periodo_texto}
              </span>
            </span>
            {!h.acerto && (
              <span className="hito-donde">lo pusiste {h.puesto_en}º</span>
            )}
          </li>
        ))}
      </ol>
    </>
  );
}
