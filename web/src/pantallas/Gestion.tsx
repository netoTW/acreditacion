import { useEffect, useMemo, useState } from "react";
import {
  SesionCaida, api,
  type EscenarioGestion, type ResultadoGestion, type Yo,
} from "../api";
import { Marco } from "../componentes/Marco";

/**
 * D1 Gestión — «El presupuesto de la acreditación».
 *
 * La única mecánica con estado que evoluciona. Tres semestres de decisión, un
 * presupuesto que no alcanza, y lo sembrado aterriza dos semestres después.
 *
 * Decisión de diseño que sostiene todo: **la proyección muestra solo lo que ya
 * está comprometido**, nunca lo que estás pensando invertir. Ves con claridad
 * hacia dónde va cada frente con las decisiones ya tomadas —eso es leer un
 * tablero de gestión, no adivinar— pero el efecto de lo que decides ahora
 * aparece recién cuando aterriza. Ese desfase es el juego.
 *
 * La simulación se repite acá para poder mostrarla; **el puntaje lo recalcula el
 * servidor** desde las asignaciones, así que esta copia no puede inflar nada.
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

type Reparto = Record<string, number>;

/** El mismo modelo del servidor. Se usa solo para dibujar. */
function simular(e: EscenarioGestion, asignaciones: Reparto[]) {
  const frentes = Object.fromEntries(e.frentes.map((f) => [f.clave, f]));
  const valor: Record<string, number> = {};
  for (const f of e.frentes) valor[f.clave] = f.inicial;

  const historia = [];
  for (let turno = 1; turno <= e.turnos; turno++) {
    for (const f of e.frentes) valor[f.clave] -= f.desgaste;

    const origen = turno - e.retardo;
    const llegadas = origen >= 1 && origen <= asignaciones.length ? asignaciones[origen - 1] : {};
    for (const [clave, u] of Object.entries(llegadas ?? {})) {
      if (frentes[clave]) valor[clave] += u * frentes[clave].efecto;
    }
    for (const k of Object.keys(valor)) valor[k] = Math.max(0, Math.min(100, valor[k]));

    const techo = e.regla.base + e.regla.factor * valor[e.regla.habilitador];
    valor[e.regla.frente] = Math.min(valor[e.regla.frente], techo);

    historia.push({ turno, valores: { ...valor }, techo, llegadas: llegadas ?? {} });
  }
  return historia;
}

export function Gestion(p: Props) {
  const [e, setE] = useState<EscenarioGestion | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [decisiones, setDecisiones] = useState<Reparto[]>([]);
  const [enCurso, setEnCurso] = useState<Reparto>({});
  const [resultado, setResultado] = useState<ResultadoGestion | null>(null);
  const [cerrando, setCerrando] = useState(false);

  const repartir = () => {
    setResultado(null);
    setDecisiones([]);
    setEnCurso({});
    api.gestion(p.bloqueRutaId)
      .then(setE)
      .catch((x) => (x instanceof SesionCaida ? p.onSalir() : setError(x.message)));
  };

  useEffect(repartir, [p.bloqueRutaId]);

  const semestre = decisiones.length + 1;
  const gastado = Object.values(enCurso).reduce((a, b) => a + b, 0);
  const quedan = e ? e.presupuesto - gastado : 0;

  /**
   * El estado visible: solo lo ya comprometido. Mientras decides el semestre N,
   * la proyección corre con las decisiones 1..N-1 y no con la que estás armando.
   */
  const historia = useMemo(
    () => (e ? simular(e, decisiones) : []),
    [e, decisiones],
  );
  const hasta = Math.min(decisiones.length, historia.length);
  const actual = hasta > 0 ? historia[hasta - 1].valores : null;

  function mover(clave: string, delta: number) {
    if (!e || resultado) return;
    setEnCurso((r) => {
      const ahora = r[clave] ?? 0;
      const nuevo = Math.max(0, ahora + delta);
      const total = Object.values({ ...r, [clave]: nuevo }).reduce((a, b) => a + b, 0);
      if (total > e.presupuesto) return r;
      return { ...r, [clave]: nuevo };
    });
  }

  function cerrarSemestre() {
    setDecisiones((d) => [...d, enCurso]);
    setEnCurso({});
  }

  async function cerrarPeriodo() {
    if (!e) return;
    setCerrando(true);
    try {
      const r = await api.cerrarGestion(p.bloqueRutaId, e.escenario_id, decisiones);
      setResultado(r);
      p.onXpGanado();
    } catch (x) {
      if (x instanceof SesionCaida) p.onSalir();
      else setError(x instanceof Error ? x.message : "no se pudo cerrar el período");
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
    if (!e) return <div className="cargando">abriendo el período…</div>;

    const decidiendo = !resultado && semestre <= e.turnos_de_decision;
    const finales = resultado
      ? resultado.historia[resultado.historia.length - 1].valores
      : null;
    const veredicto = Object.fromEntries(
      (resultado?.cierre.frentes ?? []).map((f) => [f.clave, f]),
    );

    return (
      <div className="pantalla">
        <button className="volver" onClick={p.onVolver}>← Volver al bloque</button>

        <div className="pantalla-head">
          <div className="eyebrow">Juego de Gestión Estratégica y Recursos Institucionales</div>
          <h1>{e.titulo}</h1>
          <p>{e.contexto}</p>
        </div>

        <div className="reglas-juego">
          <div className="rg-item">
            <b>{e.presupuesto} cupos</b> por semestre, durante {e.turnos_de_decision}.
            No alcanza para todo.
          </div>
          <div className="rg-item">
            Lo que inviertes <b>aterriza {e.retardo} semestres después</b>. Lo del
            último semestre se ve recién en el cierre.
          </div>
          <div className="rg-item">
            Todo <b>se desgasta solo</b> cada semestre. No atender un frente también
            es decidir.
          </div>
          <div className="rg-item rg-regla">{e.regla.texto}</div>
        </div>

        {resultado && (
          <div className={`gestion-resultado ${resultado.periodo_limpio ? "limpio" : ""}`}>
            <div className="ge-marca">
              {resultado.periodo_limpio
                ? "La institución llegó en pie"
                : "El período cerró"}
            </div>
            <div className="ge-puntaje">
              {resultado.frentes_en_pie} <span>/ {resultado.frentes_totales}</span>
            </div>
            <div className="ge-sub">
              frentes sobre su umbral · usaste {resultado.cupos_usados} de{" "}
              {resultado.cupos_disponibles} cupos
            </div>
            <div className="ge-xp">
              +{resultado.xp_otorgado} XP de juego
              {resultado.ya_jugado_hoy && <span className="ge-nota">ya jugaste hoy, esta no suma</span>}
            </div>
            <p className="ge-texto">{resultado.cierre.texto}</p>
            <div className="ge-acciones">
              <button className="btn btn-primary" onClick={repartir}>Otro período</button>
              <button className="btn btn-ghost" onClick={p.onVolver}>Volver al bloque</button>
            </div>
          </div>
        )}

        <div className="semestres">
          {Array.from({ length: e.turnos }, (_, i) => i + 1).map((t) => (
            <span
              key={t}
              className={`sem ${t < semestre || resultado ? "pasado" : ""} ${
                t === semestre && decidiendo ? "ahora" : ""} ${
                t > e.turnos_de_decision ? "solo-resuelve" : ""}`}
            >
              {t <= e.turnos_de_decision ? `Semestre ${t}` : `Cierre ${t}`}
            </span>
          ))}
        </div>

        <div className="frentes">
          {e.frentes.map((f) => {
            const valor = finales ? finales[f.clave] : actual ? actual[f.clave] : f.inicial;
            const rev = veredicto[f.clave];
            const enCamino = decisiones
              .map((d, i) => ({ turno: i + 1 + e.retardo, u: d[f.clave] ?? 0 }))
              .filter((x) => x.u > 0 && x.turno > decisiones.length);
            return (
              <div key={f.clave} className={`frente ${rev ? (rev.en_pie ? "bien" : "mal") : ""}`}>
                <div className="fr-cabecera">
                  <div>
                    <div className="fr-nombre">{f.nombre}</div>
                    <div className="fr-desc">{f.descripcion}</div>
                  </div>
                  <div className="fr-valor">
                    {valor.toFixed(0)}
                    <span>umbral {f.umbral}</span>
                  </div>
                </div>

                <div className="fr-barra">
                  <span className="fr-relleno" style={{ width: `${valor}%` }} />
                  <span className="fr-umbral" style={{ left: `${f.umbral}%` }} />
                </div>

                <div className="fr-pie">
                  <span className="fr-nota">
                    −{f.desgaste} por semestre · +{f.efecto} por cupo
                    {enCamino.length > 0 && (
                      <b className="fr-camino">
                        {" · "}
                        {enCamino.map((x) => `${x.u} cupo${x.u > 1 ? "s" : ""} llega el ${x.turno}º`)
                          .join(", ")}
                      </b>
                    )}
                  </span>

                  {decidiendo && (
                    <span className="fr-cupos">
                      <button className="cupo-btn" disabled={!(enCurso[f.clave] ?? 0)}
                              aria-label={`Quitar cupo de ${f.nombre}`}
                              onClick={() => mover(f.clave, -1)}>−</button>
                      <b>{enCurso[f.clave] ?? 0}</b>
                      <button className="cupo-btn" disabled={quedan <= 0}
                              aria-label={`Poner cupo en ${f.nombre}`}
                              onClick={() => mover(f.clave, +1)}>+</button>
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {decidiendo && (
          <div className="gestion-pie">
            <span className="gestion-pista">
              Semestre {semestre} de {e.turnos_de_decision} · te quedan{" "}
              <b>{quedan}</b> de {e.presupuesto} cupos.
              {quedan > 0 && " Los que no repartas se pierden."}
            </span>
            <button className="btn btn-primary" onClick={cerrarSemestre}>
              Cerrar el semestre {semestre}
            </button>
          </div>
        )}

        {!resultado && !decidiendo && (
          <div className="gestion-pie">
            <span className="gestion-pista">
              Los tres semestres están decididos. Faltan los cierres, donde aterriza
              lo último que sembraste.
            </span>
            <button className="btn btn-primary" disabled={cerrando} onClick={cerrarPeriodo}>
              {cerrando ? "cerrando…" : "Ver el cierre del período"}
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
      crumb={<><b>Vista colaborador</b> · El presupuesto de la acreditación</>}
      onSalir={p.onSalir}
    >
      {cuerpo()}
    </Marco>
  );
}
