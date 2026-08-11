import { useEffect, useState } from "react";
import {
  SesionCaida, api,
  type CasoCohorte, type PartidaCohorte, type ResultadoCohorte, type Yo,
} from "../api";
import { Marco } from "../componentes/Marco";

/**
 * D2 Docencia — «El caso del estudiante que se pierde».
 *
 * No se responde ni se ordena: se **lee una cohorte y se señala dónde se rompe**.
 *
 * La decisión de diseño que sostiene el juego: los tramos se muestran con su
 * **referencia** al lado. Sin ella, señalar la caída más grande sería siempre
 * correcto y el juego premiaría justo el error que existe para desarmar — perder
 * el 35% entre egreso y titulación es lo normal del sistema; perderlo entre
 * primero y segundo es una hemorragia.
 *
 * Los porcentajes se calculan acá para mostrarlos, pero **quién acertó lo decide
 * el servidor**: el tramo de quiebre no viaja hasta que la partida se cierra.
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

type Respuesta = { tramo?: number; indicador?: string };

const pct = (a: number, b: number) => Math.round((100 * b) / a);

export function Cohorte(p: Props) {
  const [partida, setPartida] = useState<PartidaCohorte | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dadas, setDadas] = useState<Record<string, Respuesta>>({});
  const [resultado, setResultado] = useState<ResultadoCohorte | null>(null);
  const [cerrando, setCerrando] = useState(false);

  const repartir = () => {
    setResultado(null);
    setDadas({});
    api.cohorte(p.bloqueRutaId)
      .then(setPartida)
      .catch((e) => (e instanceof SesionCaida ? p.onSalir() : setError(e.message)));
  };

  useEffect(repartir, [p.bloqueRutaId]);

  const marcar = (casoId: string, cambio: Respuesta) =>
    setDadas((d) => ({ ...d, [casoId]: { ...d[casoId], ...cambio } }));

  async function cerrar() {
    if (!partida) return;
    setCerrando(true);
    try {
      const r = await api.cerrarCohorte(
        p.bloqueRutaId,
        partida.casos.map((c) => ({
          caso_id: c.caso_id,
          tramo: dadas[c.caso_id]?.tramo ?? null,
          indicador: dadas[c.caso_id]?.indicador ?? null,
        })),
      );
      setResultado(r);
      p.onXpGanado();
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
            Volver al bloque
          </button>
        </div>
      );
    if (!partida) return <div className="cargando">abriendo los expedientes…</div>;

    const veredicto = Object.fromEntries(
      (resultado?.revelacion ?? []).map((r) => [r.caso_id, r]),
    );
    const completos = partida.casos.filter(
      (c) => dadas[c.caso_id]?.tramo !== undefined && dadas[c.caso_id]?.indicador,
    ).length;

    return (
      <div className="pantalla">
        <button className="volver" onClick={p.onVolver}>← Volver al bloque</button>

        <div className="pantalla-head">
          <div className="eyebrow">Juego de Docencia y Resultados del Proceso de Formación</div>
          <h1>¿Dónde se pierde la cohorte?</h1>
          <p>
            Tres carreras, tres cohortes. En cada una: señala <b>el tramo donde se
            rompe</b> —el que más cae bajo su propia referencia, no el que pierde
            más gente— y después <b>el indicador que lo explica</b>.
          </p>
        </div>

        {resultado && (
          <div className={`cohorte-resultado ${resultado.lectura_limpia ? "limpia" : ""}`}>
            <div className="cor-marca">
              {resultado.lectura_limpia ? "Lectura limpia" : "Expedientes cerrados"}
            </div>
            <div className="cor-cifras">
              <span>
                <b>{resultado.tramos_correctos}</b>/{resultado.total_casos}
                <small>tramos</small>
              </span>
              <span>
                <b>{resultado.indicadores_correctos}</b>/{resultado.total_casos}
                <small>causas</small>
              </span>
            </div>
            <div className="cor-xp">
              +{resultado.xp_otorgado} XP de juego
              {resultado.ya_jugado_hoy && <span className="cor-nota">ya jugaste hoy, esta no suma</span>}
            </div>
            <p className="cor-texto">
              Encontrar el tramo es leer datos. Explicarlo es entender el proceso —
              por eso se cobran por separado.
            </p>
            <div className="cor-acciones">
              <button className="btn btn-primary" onClick={repartir}>Otros tres casos</button>
              <button className="btn btn-ghost" onClick={p.onVolver}>Volver al bloque</button>
            </div>
          </div>
        )}

        <div className="casos">
          {partida.casos.map((c) => (
            <CasoVista
              key={c.caso_id}
              caso={c}
              dada={dadas[c.caso_id] ?? {}}
              rev={veredicto[c.caso_id]}
              onMarcar={(cambio) => marcar(c.caso_id, cambio)}
            />
          ))}
        </div>

        {!resultado && (
          <div className="cohorte-pie">
            <span className="cohorte-pista">
              {completos === partida.casos.length
                ? "Los tres están diagnosticados. Cerrar corrige todo de una vez."
                : (() => {
                    const faltan = partida.casos.length - completos;
                    return faltan === 1
                      ? "Falta un caso por diagnosticar."
                      : `Faltan ${faltan} casos por diagnosticar.`;
                  })()}
            </span>
            <button
              className="btn btn-primary"
              disabled={completos < partida.casos.length || cerrando}
              onClick={cerrar}
            >
              {cerrando ? "revisando…" : "Cerrar los expedientes"}
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
      marcaPrueba
      crumb={<><b>Vista colaborador</b> · El caso del estudiante que se pierde</>}
      onSalir={p.onSalir}
    >
      {cuerpo()}
    </Marco>
  );
}

function CasoVista(
  { caso, dada, rev, onMarcar }: {
    caso: CasoCohorte;
    dada: Respuesta;
    rev?: ResultadoCohorte["revelacion"][number];
    onMarcar: (c: Respuesta) => void;
  },
) {
  const bloqueado = !!rev;

  return (
    <div className={`caso-cohorte ${rev ? (rev.acerto_tramo && rev.acerto_indicador ? "bien" : "mal") : ""}`}>
      <div className="cc-head">
        <h2>{caso.titulo}</h2>
        <p>{caso.contexto}</p>
      </div>

      {/* La cohorte. Cada tramo se elige entero: es la unidad de la decisión. */}
      <div className="cohorte-linea">
        {caso.etapas.map((e, i) => (
          <div className="cohorte-par" key={e.nombre}>
            <div className="etapa">
              <span className="etapa-valor">{e.valor}</span>
              <span className="etapa-nombre">{e.nombre}</span>
            </div>
            {i < caso.tramos.length && (
              <button
                className={`tramo ${dada.tramo === i ? "elegido" : ""} ${
                  rev && rev.tramo_correcto === i ? "correcto" : ""
                }`}
                disabled={bloqueado}
                aria-pressed={dada.tramo === i}
                aria-label={`Tramo ${caso.tramos[i].desde} a ${caso.tramos[i].hasta}`}
                onClick={() => onMarcar({ tramo: i })}
              >
                <span className="tramo-real">
                  {pct(e.valor, caso.etapas[i + 1].valor)}%
                </span>
                <span className="tramo-ref">de {caso.tramos[i].referencia_pct}%</span>
              </button>
            )}
          </div>
        ))}
      </div>

      <div className="cc-indicadores">
        <div className="cc-rotulo">¿Cuál de estos lo explica?</div>
        {caso.indicadores.map((ind) => (
          <button
            key={ind.clave}
            className={`indicador ${dada.indicador === ind.clave ? "elegido" : ""} ${
              rev && rev.indicador_correcto === ind.clave ? "correcto" : ""
            }`}
            disabled={bloqueado}
            aria-pressed={dada.indicador === ind.clave}
            onClick={() => onMarcar({ indicador: ind.clave })}
          >
            <span className="ind-nombre">{ind.nombre}</span>
            <span className="ind-valor">{ind.valor}</span>
          </button>
        ))}
      </div>

      {rev && (
        <div className="cc-revelacion">
          <p>
            <b className={rev.acerto_tramo ? "ok" : "no"}>
              {rev.acerto_tramo ? "Tramo correcto" : "Tramo equivocado"}
            </b>{" "}
            · se rompe en <b>{rev.tramo_nombre}</b>. {rev.explicacion_quiebre}
          </p>
          <p>
            <b className={rev.acerto_indicador ? "ok" : "no"}>
              {rev.acerto_indicador ? "Causa correcta" : "Causa equivocada"}
            </b>{" "}
            · era <b>{rev.indicador_nombre}</b>. {rev.explicacion_indicador}
          </p>
        </div>
      )}
    </div>
  );
}
