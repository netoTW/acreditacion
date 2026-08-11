import { useEffect, useState } from "react";
import {
  SesionCaida, api,
  type PiezaProduccion, type ResultadoCuadrante, type TableroProduccion, type Yo,
} from "../api";
import { Marco } from "../componentes/Marco";

/**
 * D5 Investigación — «El cuadrante de la producción».
 *
 * La mecánica que faltaba: un **juicio de dos ejes**. Las otras cuatro piden una
 * sola decisión por pieza; acá hay dos preguntas independientes que se cruzan, y
 * se pueden acertar por separado.
 *
 * Por eso el tablero es un cuadrante de verdad y no cuatro bandejas con nombre:
 * los ejes están rotulados, y al revelar se ve **cuál de los dos** fallaste. Poner
 * un artículo indexado de otra universidad en «es investigación, no es nuestra» y
 * equivocarse solo en el segundo eje no es lo mismo que no haber entendido nada.
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

type Casillero = { ici: boolean; adscrita: boolean };

const CASILLEROS: { clave: string; c: Casillero; titulo: string; sub: string }[] = [
  { clave: "si-si", c: { ici: true, adscrita: true },
    titulo: "Cuenta para el informe", sub: "es producción ICI y la institución la puede reclamar" },
  { clave: "si-no", c: { ici: true, adscrita: false },
    titulo: "Es investigación, pero no es nuestra", sub: "afiliación de otro, autor que ya no está, titularidad ajena" },
  { clave: "no-si", c: { ici: false, adscrita: true },
    titulo: "Es nuestra, pero no es investigación", sub: "material docente, gestión interna, difusión" },
  { clave: "no-no", c: { ici: false, adscrita: false },
    titulo: "Ni lo uno ni lo otro", sub: "ni produce conocimiento ni pertenece a la institución" },
];

const claveDe = (c: Casillero) => `${c.ici ? "si" : "no"}-${c.adscrita ? "si" : "no"}`;

export function Produccion(p: Props) {
  const [tablero, setTablero] = useState<TableroProduccion | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [puestas, setPuestas] = useState<Record<string, Casillero>>({});
  const [tomada, setTomada] = useState<string | null>(null);
  const [resultado, setResultado] = useState<ResultadoCuadrante | null>(null);
  const [cerrando, setCerrando] = useState(false);

  const repartir = () => {
    setResultado(null);
    setPuestas({});
    setTomada(null);
    api.produccion(p.bloqueRutaId)
      .then(setTablero)
      .catch((e) => (e instanceof SesionCaida ? p.onSalir() : setError(e.message)));
  };

  useEffect(repartir, [p.bloqueRutaId]);

  function ubicar(c: Casillero) {
    if (!tomada || resultado) return;
    setPuestas((v) => ({ ...v, [tomada]: c }));
    setTomada(null);
  }

  async function cerrar() {
    if (!tablero) return;
    setCerrando(true);
    try {
      const r = await api.cerrarProduccion(
        p.bloqueRutaId,
        tablero.piezas.map((z) => ({
          pieza_id: z.pieza_id,
          es_ici: puestas[z.pieza_id].ici,
          es_adscrita: puestas[z.pieza_id].adscrita,
        })),
      );
      setResultado(r);
      p.onXpGanado();
    } catch (e) {
      if (e instanceof SesionCaida) p.onSalir();
      else setError(e instanceof Error ? e.message : "no se pudo cerrar el tablero");
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
    if (!tablero) return <div className="cargando">abriendo el registro…</div>;

    const veredicto = Object.fromEntries(
      (resultado?.revelacion ?? []).map((r) => [r.pieza_id, r]),
    );
    const enMano = tablero.piezas.filter((z) => !puestas[z.pieza_id]);

    const ficha = (z: PiezaProduccion, dentro: boolean) => {
      const rev = veredicto[z.pieza_id];
      const fallo = rev && (!rev.acerto_ici || !rev.acerto_adscripcion);
      return (
        <button
          key={z.pieza_id}
          className={`ficha ${tomada === z.pieza_id ? "tomada" : ""} ${
            rev ? (fallo ? "mal" : "bien") : ""} ${dentro ? "dentro" : ""}`}
          disabled={!!resultado}
          aria-pressed={tomada === z.pieza_id}
          onClick={() => !resultado && setTomada(tomada === z.pieza_id ? null : z.pieza_id)}
        >
          <span className="ficha-tipo">{z.tipo}</span>
          <span className="ficha-titulo">{z.titulo}</span>
          {!dentro && <span className="ficha-detalle">{z.detalle}</span>}
          {rev && fallo && (
            <span className="ficha-verdad">
              {!rev.acerto_ici && <><b>Sobre si es ICI:</b> {rev.razon_ici} </>}
              {!rev.acerto_adscripcion && <><b>Sobre de quién es:</b> {rev.razon_adscripcion}</>}
            </span>
          )}
        </button>
      );
    };

    return (
      <div className="pantalla">
        <button className="volver" onClick={p.onVolver}>← Volver al bloque</button>

        <div className="pantalla-head">
          <div className="eyebrow">Juego de Investigación, Creación y/o Innovación</div>
          <h1>¿Qué entra al informe de investigación?</h1>
          <p>
            Cada pieza se juzga <b>dos veces</b>, y por separado: si es producción de
            investigación, creación o innovación, y si la institución puede
            reclamarla. Solo un casillero de los cuatro cuenta para el informe.
          </p>
        </div>

        <details className="lineas-declaradas">
          <summary>Líneas declaradas por la institución ({tablero.lineas.length})</summary>
          <ul>
            {tablero.lineas.map((l) => (
              <li key={l.clave}><b>{l.nombre}</b> · {l.descripcion}</li>
            ))}
          </ul>
        </details>

        {resultado && (
          <div className={`cuadrante-resultado ${resultado.cuadrante_limpio ? "limpio" : ""}`}>
            <div className="cu-marca">
              {resultado.cuadrante_limpio ? "Registro depurado" : "Tablero cerrado"}
            </div>
            <div className="cu-puntaje">
              {resultado.ejes_correctos} <span>/ {resultado.ejes_totales}</span>
            </div>
            <div className="cu-sub">
              juicios correctos · {resultado.piezas_perfectas} de {resultado.total} piezas
              en su casillero exacto
            </div>
            <div className="cu-xp">
              +{resultado.xp_otorgado} XP de juego
              {resultado.ya_jugado_hoy && <span className="cu-nota">ya jugaste hoy, esta no suma</span>}
            </div>
            <p className="cu-texto">
              Los dos ejes se cobran por separado: acertar que algo es investigación y
              equivocarse en de quién es sigue siendo medio acierto.
            </p>
            <div className="cu-acciones">
              <button className="btn btn-primary" onClick={repartir}>Otro registro</button>
              <button className="btn btn-ghost" onClick={p.onVolver}>Volver al bloque</button>
            </div>
          </div>
        )}

        {!resultado && (
          <div className={`pila ${tomada ? "con-tomada" : ""}`}>
            <div className="pila-rotulo">
              {enMano.length ? `Sin ubicar · ${enMano.length}` : "Todas ubicadas"}
            </div>
            <div className="pila-fichas">
              {enMano.map((z) => ficha(z, false))}
              {!enMano.length && <p className="pila-vacia">El registro está listo para cerrar.</p>}
            </div>
          </div>
        )}

        {/* Los ejes van rotulados: el tablero es un cuadrante, no cuatro cajones. */}
        <div className="cuadrante">
          <div className="eje-y" aria-hidden="true">¿es producción de investigación?</div>
          <div className="casillas">
            {CASILLEROS.map((k) => {
              const dentro = tablero.piezas.filter(
                (z) => puestas[z.pieza_id] && claveDe(puestas[z.pieza_id]) === k.clave,
              );
              return (
                <div
                  key={k.clave}
                  className={`casilla ${k.clave} ${tomada ? "recibiendo" : ""}`}
                  onClick={() => ubicar(k.c)}
                >
                  <div className="casilla-rotulo">
                    <b>{k.titulo}</b>
                    <span>{k.sub}</span>
                  </div>
                  <div className="casilla-fichas">{dentro.map((z) => ficha(z, true))}</div>
                </div>
              );
            })}
          </div>
          <div className="eje-x" aria-hidden="true">¿la institución puede reclamarla?</div>
        </div>

        {!resultado && (
          <div className="cuadrante-pie">
            <span className="cuadrante-pista">
              {tomada
                ? "Ahora toca el casillero donde va."
                : enMano.length
                  ? "Toca una pieza y léele el detalle: ahí está la pista."
                  : "Todas ubicadas. Cerrar corrige los dos ejes de cada una."}
            </span>
            <button className="btn btn-primary" disabled={!!enMano.length || cerrando}
                    onClick={cerrar}>
              {cerrando ? "revisando…" : "Cerrar el registro"}
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
      crumb={<><b>Vista colaborador</b> · El cuadrante de la producción</>}
      onSalir={p.onSalir}
    >
      {cuerpo()}
    </Marco>
  );
}
