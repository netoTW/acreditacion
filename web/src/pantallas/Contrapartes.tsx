import { useEffect, useLayoutEffect, useRef, useState } from "react";
import {
  SesionCaida, api,
  type MapaRepartido, type ResultadoMapa, type Yo,
} from "../api";
import { Marco } from "../componentes/Marco";

/**
 * D4 Vinculación — «El mapa de contrapartes».
 *
 * Se **tienden vínculos** entre dos columnas: actores externos a la izquierda,
 * acciones institucionales a la derecha, y una línea entre los que se sostienen.
 *
 * Lo que lo separa de la Mesa de comité —que también es «poner cosas en su
 * lugar»—: allá toda carta termina en una bandeja. Acá hay actores que **no van
 * a ninguna parte**, y dejarlos fuera es la respuesta correcta. Por eso la zona
 * de descarte no es un cajón de sobras: es la mitad del juego.
 *
 * Las líneas se dibujan en un SVG que se superpone al tablero, midiendo dónde
 * quedó cada tarjeta. Se recalcula al cambiar el tamaño porque en el teléfono las
 * dos columnas se apilan y las líneas tendrían que ir de arriba abajo.
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

const SIN_VINCULO = "__sin_vinculo__";
type Trazo = { x1: number; y1: number; x2: number; y2: number; estado: string };

export function Contrapartes(p: Props) {
  const [mapa, setMapa] = useState<MapaRepartido | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [vinculos, setVinculos] = useState<Record<string, string>>({});
  const [tomado, setTomado] = useState<string | null>(null);
  const [resultado, setResultado] = useState<ResultadoMapa | null>(null);
  const [cerrando, setCerrando] = useState(false);
  const [trazos, setTrazos] = useState<Trazo[]>([]);

  const tablero = useRef<HTMLDivElement>(null);
  const nodos = useRef<Record<string, HTMLElement | null>>({});

  const repartir = () => {
    setResultado(null);
    setVinculos({});
    setTomado(null);
    api.contrapartes(p.bloqueRutaId)
      .then(setMapa)
      .catch((e) => (e instanceof SesionCaida ? p.onSalir() : setError(e.message)));
  };

  useEffect(repartir, [p.bloqueRutaId]);

  /** Mide dónde quedó cada tarjeta y arma las líneas. */
  useLayoutEffect(() => {
    const medir = () => {
      const caja = tablero.current?.getBoundingClientRect();
      if (!caja || !mapa) return setTrazos([]);

      const centro = (clave: string, lado: "der" | "izq") => {
        const el = nodos.current[clave];
        if (!el) return null;
        const r = el.getBoundingClientRect();
        // En una sola columna (teléfono) la línea sale por abajo y entra por arriba.
        const apilado = caja.width < 720;
        if (apilado)
          return { x: r.left + r.width / 2 - caja.left,
                   y: (lado === "der" ? r.bottom : r.top) - caja.top };
        return { x: (lado === "der" ? r.right : r.left) - caja.left,
                 y: r.top + r.height / 2 - caja.top };
      };

      const veredicto = Object.fromEntries(
        (resultado?.revelacion ?? []).map((r) => [r.actor_id, r]),
      );

      const nuevos: Trazo[] = [];
      for (const [actorId, destino] of Object.entries(vinculos)) {
        const a = centro(`actor:${actorId}`, "der");
        const b = centro(destino === SIN_VINCULO ? "descarte" : `accion:${destino}`, "izq");
        if (!a || !b) continue;
        const rev = veredicto[actorId];
        nuevos.push({
          x1: a.x, y1: a.y, x2: b.x, y2: b.y,
          estado: rev ? (rev.acerto ? "bien" : "mal") : destino === SIN_VINCULO ? "descarte" : "",
        });
      }
      setTrazos(nuevos);
    };

    medir();
    const obs = new ResizeObserver(medir);
    if (tablero.current) obs.observe(tablero.current);
    window.addEventListener("resize", medir);
    return () => { obs.disconnect(); window.removeEventListener("resize", medir); };
  }, [mapa, vinculos, resultado]);

  function atar(destino: string) {
    if (!tomado || resultado) return;
    setVinculos((v) => ({ ...v, [tomado]: destino }));
    setTomado(null);
  }

  function soltar(actorId: string) {
    setVinculos((v) => {
      const copia = { ...v };
      delete copia[actorId];
      return copia;
    });
  }

  async function cerrar() {
    if (!mapa) return;
    setCerrando(true);
    try {
      const r = await api.cerrarContrapartes(
        p.bloqueRutaId,
        mapa.actores.map((a) => ({
          actor_id: a.actor_id,
          accion_clave: vinculos[a.actor_id] === SIN_VINCULO ? null : vinculos[a.actor_id],
        })),
      );
      setResultado(r);
      p.onXpGanado();
    } catch (e) {
      if (e instanceof SesionCaida) p.onSalir();
      else setError(e instanceof Error ? e.message : "no se pudo cerrar el mapa");
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
    if (!mapa) return <div className="cargando">levantando el catálogo…</div>;

    const veredicto = Object.fromEntries(
      (resultado?.revelacion ?? []).map((r) => [r.actor_id, r]),
    );
    const sueltos = mapa.actores.filter((a) => !vinculos[a.actor_id]).length;
    const descartados = mapa.actores.filter((a) => vinculos[a.actor_id] === SIN_VINCULO);

    return (
      <div className="pantalla">
        <button className="volver" onClick={p.onVolver}>← Volver al bloque</button>

        <div className="pantalla-head">
          <div className="eyebrow">Juego de Vinculación con el Medio</div>
          <h1>¿Qué vínculos se sostienen?</h1>
          <p>
            Toca un actor y después la acción que lo vincula con la institución.{" "}
            <b>No todos son contrapartes</b>: los que son proveedores, servicios
            contratados o simple difusión van al descarte — y dejarlos fuera es
            parte de la respuesta.
          </p>
        </div>

        {resultado && (
          <div className={`mapa-resultado ${resultado.mapa_limpio ? "limpio" : ""}`}>
            <div className="mp-marca">
              {resultado.mapa_limpio ? "Mapa limpio" : "Mapa cerrado"}
            </div>
            <div className="mp-puntaje">{resultado.aciertos} / {resultado.total}</div>
            <div className="mp-descartes">
              descartes correctos: {resultado.descartes_correctos} de{" "}
              {resultado.descartes_totales}
            </div>
            <div className="mp-xp">
              +{resultado.xp_otorgado} XP de juego
              {resultado.ya_jugado_hoy && <span className="mp-nota">ya jugaste hoy, esta no suma</span>}
            </div>
            <p className="mp-texto">
              Contar como convenio lo que es una compra es la forma más común de
              inflar el listado de vinculación sin darse cuenta.
            </p>
            <div className="mp-acciones">
              <button className="btn btn-primary" onClick={repartir}>Otro mapa</button>
              <button className="btn btn-ghost" onClick={p.onVolver}>Volver al bloque</button>
            </div>
          </div>
        )}

        <div className="mapa-tablero" ref={tablero}>
          <svg className="mapa-lineas" aria-hidden="true">
            {trazos.map((t, i) => (
              <line key={i} className={`traza ${t.estado}`}
                    x1={t.x1} y1={t.y1} x2={t.x2} y2={t.y2} />
            ))}
          </svg>

          <div className="columna actores">
            <div className="col-rotulo">Actores externos</div>
            {mapa.actores.map((a) => {
              const rev = veredicto[a.actor_id];
              const atado = vinculos[a.actor_id];
              return (
                <button
                  key={a.actor_id}
                  ref={(el) => { nodos.current[`actor:${a.actor_id}`] = el; }}
                  className={`actor ${tomado === a.actor_id ? "tomado" : ""} ${
                    atado ? "atado" : ""} ${rev ? (rev.acerto ? "bien" : "mal") : ""}`}
                  disabled={!!resultado}
                  aria-pressed={tomado === a.actor_id}
                  onClick={() => {
                    if (resultado) return;
                    if (atado) soltar(a.actor_id);
                    setTomado(tomado === a.actor_id ? null : a.actor_id);
                  }}
                >
                  <span className="actor-nombre">{a.nombre}</span>
                  <span className="actor-desc">{a.descripcion}</span>
                  {rev && (
                    <span className="actor-verdad">
                      {rev.es_contraparte
                        ? <>iba con <b>{rev.accion_nombre}</b>. {rev.razon}</>
                        : <><b>No es contraparte.</b> {rev.razon}</>}
                    </span>
                  )}
                </button>
              );
            })}
          </div>

          <div className="columna acciones">
            <div className="col-rotulo">Acciones institucionales</div>
            {mapa.acciones.map((ac) => {
              const cuantos = Object.values(vinculos).filter((v) => v === ac.clave).length;
              return (
                <button
                  key={ac.clave}
                  ref={(el) => { nodos.current[`accion:${ac.clave}`] = el; }}
                  className={`accion ${tomado ? "recibiendo" : ""} ${cuantos ? "usada" : ""}`}
                  disabled={!!resultado}
                  onClick={() => atar(ac.clave)}
                >
                  <span className="accion-nombre">{ac.nombre}</span>
                  <span className="accion-desc">{ac.descripcion}</span>
                </button>
              );
            })}

            {/* El descarte no es un cajón de sobras: es media respuesta. */}
            <button
              ref={(el) => { nodos.current["descarte"] = el; }}
              className={`accion descarte ${tomado ? "recibiendo" : ""} ${
                descartados.length ? "usada" : ""}`}
              disabled={!!resultado}
              onClick={() => atar(SIN_VINCULO)}
            >
              <span className="accion-nombre">No se sostiene como vinculación</span>
              <span className="accion-desc">
                Proveedores, servicios contratados y difusión · {descartados.length} aquí
              </span>
            </button>
          </div>
        </div>

        {!resultado && (
          <div className="mapa-pie">
            <span className="mapa-pista">
              {tomado
                ? "Ahora toca la acción que lo vincula, o el descarte."
                : sueltos === 1
                  ? "Queda un actor sin resolver."
                  : sueltos
                    ? `Quedan ${sueltos} actores sin resolver. Toca uno para empezar.`
                    : "Todos resueltos. Cerrar corrige el mapa entero."}
            </span>
            <button className="btn btn-primary" disabled={!!sueltos || cerrando} onClick={cerrar}>
              {cerrando ? "revisando…" : "Cerrar el mapa"}
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
      crumb={<><b>Vista colaborador</b> · El mapa de contrapartes</>}
      onSalir={p.onSalir}
    >
      {cuerpo()}
    </Marco>
  );
}
