import { useEffect, useState } from "react";
import { SesionCaida, api, type MesaRepartida, type ResultadoMesa, type Yo } from "../api";
import { Marco } from "../componentes/Marco";

/**
 * B2 «Mesa de comité» — clasificar afirmaciones por dimensión.
 *
 * No se responde una pregunta: se **acomoda un tablero**. Las seis afirmaciones
 * están a la vista a la vez, se mueven entre bandejas cuantas veces se quiera, y
 * la decisión real es cuándo cerrar.
 *
 * Dos formas de mover, a propósito: arrastrar (ratón) y tocar-carta / tocar-bandeja
 * (táctil y teclado). Un juego de arrastrar que solo funciona con ratón deja fuera
 * justamente al que lo va a usar en el teléfono.
 */
type Props = {
  yo: Yo;
  totalBloques: number;
  bloquesCompletos: number;
  onVolver: () => void;
  onXpGanado: () => void;
  onSalir: () => void;
};

/** Las bandejas necesitan un rótulo corto; el nombre oficial no cabe en una columna. */
const CORTO: Record<string, string> = {
  GESTION: "Gestión Estratégica",
  DOCENCIA: "Docencia",
  CALIDAD: "Aseguramiento de la Calidad",
  VCM: "Vinculación con el Medio",
  ICI: "Investigación",
};

export function Mesa(p: Props) {
  const [mesa, setMesa] = useState<MesaRepartida | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [donde, setDonde] = useState<Record<string, string | null>>({});
  const [tomada, setTomada] = useState<string | null>(null);
  const [sobre, setSobre] = useState<string | null>(null);
  const [resultado, setResultado] = useState<ResultadoMesa | null>(null);
  const [cerrando, setCerrando] = useState(false);

  const repartir = () => {
    setResultado(null); setTomada(null); setSobre(null);
    api.mesa()
      .then((m) => {
        setMesa(m);
        setDonde(Object.fromEntries(m.cartas.map((c) => [c.item_id, null])));
      })
      .catch((e) => (e instanceof SesionCaida ? p.onSalir() : setError(e.message)));
  };

  useEffect(repartir, []);

  function colocar(item_id: string, dimension: string | null) {
    setDonde((d) => ({ ...d, [item_id]: dimension }));
    setTomada(null);
    setSobre(null);
  }

  function tocarBandeja(dimension: string | null) {
    if (tomada) colocar(tomada, dimension);
  }

  async function cerrar() {
    if (!mesa) return;
    setCerrando(true);
    try {
      const r = await api.cerrarMesa(
        mesa.cartas.map((c) => ({ item_id: c.item_id, dimension: donde[c.item_id]! })),
      );
      setResultado(r);
      p.onXpGanado();
    } catch (e) {
      if (e instanceof SesionCaida) p.onSalir();
      else setError(e instanceof Error ? e.message : "no se pudo cerrar la mesa");
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
            Volver a mi ruta
          </button>
        </div>
      );
    if (!mesa) return <div className="cargando">armando la mesa…</div>;

    const enMano = mesa.cartas.filter((c) => !donde[c.item_id]);
    const completa = enMano.length === 0;
    const verdad = Object.fromEntries((resultado?.revelacion ?? []).map((r) => [r.item_id, r]));

    const carta = (c: { item_id: string; texto: string }) => {
      const rev = verdad[c.item_id];
      const clase = rev ? (rev.acerto ? "bien" : "mal") : tomada === c.item_id ? "tomada" : "";
      return (
        <button
          key={c.item_id}
          className={`carta ${clase}`}
          draggable={!resultado}
          onDragStart={() => setTomada(c.item_id)}
          onDragEnd={() => setSobre(null)}
          onClick={() => !resultado && setTomada(tomada === c.item_id ? null : c.item_id)}
          disabled={!!resultado}
          aria-pressed={tomada === c.item_id}
        >
          <span className="carta-texto">{c.texto}</span>
          {rev && !rev.acerto && (
            <span className="carta-verdad">
              iba en <b>{CORTO[rev.dimension_correcta] ?? rev.dimension_correcta}</b> ·{" "}
              {rev.enunciado.replace(/^En el proceso de autoevaluación, /, "")}
            </span>
          )}
        </button>
      );
    };

    return (
      <div className="pantalla">
        <button className="volver" onClick={p.onVolver}>← Mi Ruta</button>

        <div className="pantalla-head">
          <div className="eyebrow">Juego · Mesa de comité</div>
          <h1>¿A qué dimensión pertenece cada una?</h1>
          <p>
            Seis afirmaciones sobre la mesa. Arrástralas —o tócalas y luego toca una
            bandeja— hasta que te convenza cómo quedó. <b>Puedes moverlas todas las veces
            que quieras</b>; solo se corrige cuando cierras la mesa.
          </p>
        </div>

        {resultado && (
          <div className={`mesa-resultado ${resultado.mesa_perfecta ? "perfecta" : ""}`}>
            <div className="mr-marca">
              {resultado.mesa_perfecta ? "Mesa perfecta" : "Mesa cerrada"}
            </div>
            <div className="mr-puntaje">{resultado.aciertos} / {resultado.total}</div>
            <div className="mr-xp">
              +{resultado.xp_otorgado} XP
              {resultado.mesa_perfecta && <span className="mr-bono">incluye +80 de bono</span>}
            </div>
            <p className="mr-nota">
              {resultado.ya_jugado_hoy
                ? "Ya cerraste una mesa hoy, así que esta no suma XP."
                : resultado.mesa_perfecta
                  ? "Ubicaste las seis. Distinguir a qué dimensión pertenece cada cosa es lo que discute un comité de verdad."
                  : "Las que quedaron mal muestran dónde iban. Varias son discutibles entre dos dimensiones — esa discusión es el punto."}
            </p>
            <div className="mr-acciones">
              <button className="btn btn-primary" onClick={repartir}>Otra mesa</button>
              <button className="btn btn-ghost" onClick={p.onVolver}>Volver a mi ruta</button>
            </div>
          </div>
        )}

        {!resultado && (
          <div
            className={`mano ${sobre === "__mano" ? "encima" : ""}`}
            onDragOver={(e) => { e.preventDefault(); setSobre("__mano"); }}
            onDragLeave={() => setSobre(null)}
            onDrop={(e) => { e.preventDefault(); if (tomada) colocar(tomada, null); }}
            onClick={() => tomada && colocar(tomada, null)}
          >
            <div className="mano-rotulo">
              {enMano.length ? `Sin ubicar · ${enMano.length}` : "Todas ubicadas"}
            </div>
            <div className="mano-cartas">
              {enMano.map(carta)}
              {!enMano.length && <p className="mano-vacia">La mesa está lista para cerrar.</p>}
            </div>
          </div>
        )}

        <div className="bandejas">
          {mesa.bandejas.map((b) => {
            const dentro = mesa.cartas.filter((c) => donde[c.item_id] === b.codigo);
            return (
              <div
                key={b.codigo}
                className={`bandeja ${sobre === b.codigo ? "encima" : ""} ${tomada ? "recibiendo" : ""}`}
                onDragOver={(e) => { e.preventDefault(); setSobre(b.codigo); }}
                onDragLeave={() => setSobre(null)}
                onDrop={(e) => { e.preventDefault(); tocarBandeja(b.codigo); }}
                onClick={() => tocarBandeja(b.codigo)}
              >
                <div className="bandeja-rotulo">
                  <b>{CORTO[b.codigo] ?? b.codigo}</b>
                  <span>{dentro.length}</span>
                </div>
                <div className="bandeja-cartas">{dentro.map(carta)}</div>
              </div>
            );
          })}
        </div>

        {!resultado && (
          <div className="mesa-pie">
            <span className="mesa-pista">
              {tomada
                ? "Toca la bandeja donde va."
                : completa
                  ? "Revisa cómo quedó. Cerrar corrige las seis de una vez."
                  : `Faltan ${enMano.length} por ubicar.`}
            </span>
            <button className="btn btn-primary" disabled={!completa || cerrando} onClick={cerrar}>
              {cerrando ? "corrigiendo…" : "Cerrar la mesa"}
            </button>
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
      seccion="mesa"
      crumb={<><b>Vista colaborador</b> · Mesa de comité</>}
      onSalir={p.onSalir}
    >
      {cuerpo()}
    </Marco>
  );
}
