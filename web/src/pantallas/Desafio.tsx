import { useEffect, useState } from "react";
import {
  SesionCaida, api,
  type Decision, type DesafioAplicado, type ResultadoDesafio, type Yo,
} from "../api";
import { Marco } from "../componentes/Marco";

/**
 * Desafío aplicado — la exigencia extra de la dimensión crítica.
 *
 * No es un quiz con otro nombre: hay una silla («integras el comité»), una
 * situación con datos y decisiones que se toman mirando ese cuadro. Por eso los
 * datos van arriba, fijos, mientras se decide.
 *
 * Nada se corrige en vivo. La revelación llega toda junta al cerrar el caso,
 * porque el servidor es quien corrige y el cliente nunca recibió la clave.
 */
type Props = {
  bloqueRutaId: string;
  yo: Yo;
  totalBloques: number;
  bloquesCompletos: number;
  onVolver: () => void;
  onResuelto: () => void;
  onSalir: () => void;
};

type Respuesta = string | string[] | Record<string, string> | undefined;

export function Desafio(p: Props) {
  const [caso, setCaso] = useState<DesafioAplicado | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dadas, setDadas] = useState<Record<string, Respuesta>>({});
  const [resultado, setResultado] = useState<ResultadoDesafio | null>(null);
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    api.desafio(p.bloqueRutaId)
      .then(setCaso)
      .catch((e) => (e instanceof SesionCaida ? p.onSalir() : setError(e.message)));
  }, [p.bloqueRutaId]);

  function responder(id: string, valor: Respuesta) {
    setDadas((d) => ({ ...d, [id]: valor }));
  }

  function alternar(d: Decision, clave: string) {
    const actual = (dadas[d.decision_id] as string[] | undefined) ?? [];
    responder(
      d.decision_id,
      actual.includes(clave) ? actual.filter((c) => c !== clave) : [...actual, clave],
    );
  }

  function clasificar(d: Decision, opcion: string, grupo: string) {
    const actual = (dadas[d.decision_id] as Record<string, string> | undefined) ?? {};
    responder(d.decision_id, { ...actual, [opcion]: grupo });
  }

  /** Una decisión cuenta como tomada solo si está COMPLETA: media clasificación no decide nada. */
  function tomada(d: Decision): boolean {
    const r = dadas[d.decision_id];
    if (d.tipo === "eleccion_unica") return typeof r === "string";
    if (d.tipo === "seleccion_multiple") return Array.isArray(r) && r.length > 0;
    return !!r && Object.keys(r as object).length === d.opciones.length;
  }

  async function cerrar() {
    if (!caso) return;
    setEnviando(true);
    try {
      const r = await api.resolverDesafio(
        p.bloqueRutaId,
        caso.decisiones.map((d) => ({
          decision_id: d.decision_id,
          respuesta: dadas[d.decision_id] ?? null,
        })),
      );
      setResultado(r);
      p.onResuelto();
    } catch (e) {
      if (e instanceof SesionCaida) p.onSalir();
      else setError(e instanceof Error ? e.message : "no se pudo cerrar el caso");
    } finally {
      setEnviando(false);
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
    if (!caso) return <div className="cargando">abriendo el caso…</div>;

    const veredicto = Object.fromEntries(
      (resultado?.revelacion ?? []).map((r) => [r.decision_id, r]),
    );
    const faltan = caso.decisiones.filter((d) => !tomada(d)).length;

    return (
      <div className="pantalla">
        <button className="volver" onClick={p.onVolver}>← Volver al bloque</button>

        <div className="pantalla-head">
          <div className="eyebrow">Desafío aplicado · ruta crítica</div>
          <h1>{caso.titulo}</h1>
          <p className="silla">{caso.rol_ficticio}</p>
        </div>

        <div className="caso-situacion">
          <p>{caso.situacion}</p>
          <div className="caso-datos">
            {caso.datos.map((d) => (
              <div className="caso-dato" key={d.etiqueta}>
                <span className="cd-valor">{d.valor}</span>
                <span className="cd-etiqueta">{d.etiqueta}</span>
              </div>
            ))}
          </div>
          <p className="caso-nota">
            Datos de prueba: existen para que la decisión tenga contexto, no afirman
            nada sobre la institución.
          </p>
        </div>

        {resultado && (
          <div className={`caso-resultado ${resultado.perfecto ? "perfecto" : ""}`}>
            <div className="cr-marca">{resultado.perfecto ? "Caso resuelto sin fisuras" : "Caso cerrado"}</div>
            <div className="cr-puntaje">{resultado.aciertos} / {resultado.total}</div>
            <div className="cr-xp">
              +{resultado.xp_otorgado} XP de juego
              {resultado.ya_resuelto && <span className="cr-nota">ya lo habías resuelto</span>}
            </div>
            <p className="cr-texto">
              Este XP <b>no es acreditable</b> y no otorga medalla. Lo que hace el desafío
              es abrirte la evaluación reforzada; la medalla de oro sigue dependiendo de
              aprobarla al 85%.
            </p>
            <div className="cr-acciones">
              <button className="btn btn-primary" onClick={p.onVolver}>Ir a la evaluación</button>
            </div>
          </div>
        )}

        <div className="decisiones">
          {caso.decisiones.map((d) => {
            const rev = veredicto[d.decision_id];
            const bloqueado = !!resultado;
            const mia = dadas[d.decision_id];

            return (
              <div
                key={d.decision_id}
                className={`decision ${rev ? (rev.acerto ? "bien" : "mal") : ""}`}
              >
                <div className="dec-num">Decisión {d.orden}</div>
                <p className="dec-enunciado">{d.enunciado}</p>

                {d.tipo === "eleccion_unica" && (
                  <div className="dec-opciones">
                    {d.opciones.map((o) => (
                      <button
                        key={o.clave}
                        className={`dec-opcion ${mia === o.clave ? "elegida" : ""} ${
                          rev && (rev.clave_correcta as string) === o.clave ? "correcta" : ""
                        }`}
                        disabled={bloqueado}
                        aria-pressed={mia === o.clave}
                        onClick={() => responder(d.decision_id, o.clave)}
                      >
                        {o.texto}
                      </button>
                    ))}
                  </div>
                )}

                {d.tipo === "seleccion_multiple" && (
                  <div className="dec-opciones">
                    <div className="dec-pista">Marca todas las que correspondan.</div>
                    {d.opciones.map((o) => {
                      const marcada = ((mia as string[]) ?? []).includes(o.clave);
                      const esCorrecta = rev && (rev.clave_correcta as string[]).includes(o.clave);
                      return (
                        <button
                          key={o.clave}
                          className={`dec-opcion casilla ${marcada ? "elegida" : ""} ${
                            esCorrecta ? "correcta" : ""
                          }`}
                          disabled={bloqueado}
                          aria-pressed={marcada}
                          onClick={() => alternar(d, o.clave)}
                        >
                          <span className="marca" aria-hidden="true">{marcada ? "✓" : ""}</span>
                          {o.texto}
                        </button>
                      );
                    })}
                  </div>
                )}

                {d.tipo === "clasificacion" && (
                  <div className="dec-clasificacion">
                    {d.opciones.map((o) => {
                      const puesta = ((mia as Record<string, string>) ?? {})[o.clave];
                      const correcta = rev && (rev.clave_correcta as Record<string, string>)[o.clave];
                      return (
                        <div className="clas-fila" key={o.clave}>
                          <span className="clas-texto">{o.texto}</span>
                          <span className="clas-grupos">
                            {d.grupos.map((g) => (
                              <button
                                key={g.clave}
                                className={`clas-grupo ${puesta === g.clave ? "elegida" : ""} ${
                                  correcta === g.clave ? "correcta" : ""
                                }`}
                                disabled={bloqueado}
                                aria-pressed={puesta === g.clave}
                                onClick={() => clasificar(d, o.clave, g.clave)}
                              >
                                {g.etiqueta}
                              </button>
                            ))}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                )}

                {rev && <p className="dec-explicacion">{rev.explicacion}</p>}
              </div>
            );
          })}
        </div>

        {!resultado && (
          <div className="caso-pie">
            <span className="caso-pista">
              {faltan
                ? `Faltan ${faltan} decisiones por tomar.`
                : "Las tres están tomadas. Cerrar el caso corrige todo de una vez."}
            </span>
            <button className="btn btn-primary" disabled={!!faltan || enviando} onClick={cerrar}>
              {enviando ? "cerrando…" : "Cerrar el caso"}
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
      crumb={<><b>Vista colaborador</b> · Desafío aplicado</>}
      onSalir={p.onSalir}
    >
      {cuerpo()}
    </Marco>
  );
}
