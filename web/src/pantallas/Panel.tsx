import { useEffect, useState } from "react";
import {
  SesionCaida, api,
  type FilaDimension, type FilaPanel, type PanelResumen, type Yo,
} from "../api";
import { Marco } from "../componentes/Marco";
import type { Seccion } from "../componentes/Sidebar";

/**
 * Panel institucional — la vista de la dirección.
 *
 * Cambia de sujeto: las demás pantallas miran a una persona, esta mira a la
 * institución. Por eso **no hay un solo nombre en toda la pantalla**, ni forma de
 * llegar a uno: los endpoints sirven agregados y el umbral de anonimato lo
 * aplican las vistas de la base, no este componente.
 *
 * Cinco lecturas, en el orden en que un directivo las necesita: si la gente
 * entró, cuánto avanzó la acreditación, si están aprendiendo, dónde está el
 * riesgo, y si hay algo parecido a cultura de calidad —gente que juega sin que
 * se lo exijan—.
 */
type Props = {
  yo: Yo;
  totalBloques: number;
  bloquesCompletos: number;
  onIrA: (s: Seccion) => void;
  onSalir: () => void;
};

const porcentaje = (n: number) => `${Math.round(n * 100)}%`;
const razon = (a: number, b: number) => (b ? a / b : 0);

export function Panel(p: Props) {
  const [resumen, setResumen] = useState<PanelResumen | null>(null);
  const [unidades, setUnidades] = useState<FilaPanel[]>([]);
  const [roles, setRoles] = useState<FilaPanel[]>([]);
  const [dimensiones, setDimensiones] = useState<FilaDimension[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      api.panelResumen(), api.panelPorUnidad(), api.panelPorRol(), api.panelDimensiones(),
    ])
      .then(([r, u, ro, d]) => { setResumen(r); setUnidades(u); setRoles(ro); setDimensiones(d); })
      .catch((e) => (e instanceof SesionCaida ? p.onSalir() : setError(e.message)));
  }, []);

  const cuerpo = () => {
    if (error)
      return (
        <div className="error">
          <p>{error}</p>
          <button className="btn btn-primary" style={{ marginTop: 14 }}
                  onClick={() => p.onIrA("ruta")}>
            Volver a mi ruta
          </button>
        </div>
      );
    if (!resumen) return <div className="cargando">levantando el panel…</div>;

    const r = resumen;
    const sinActividad = r.personas - r.con_actividad;
    const puntaje = r.puntaje_promedio === null ? null : Number(r.puntaje_promedio);
    const desglosadas = unidades.reduce((s, u) => s + (u.es_reservado ? 0 : u.personas), 0);

    return (
      <div className="pantalla panel">
        <div className="pantalla-head">
          <div className="eyebrow">Vista de dirección · toda la institución</div>
          <h1>Panel de acreditación</h1>
          <p>
            {r.personas.toLocaleString("es-CL")} personas en el sistema.
            Datos agregados: <b>ningún grupo de menos de {r.umbral_anonimato} personas
            se muestra desglosado</b>, y no hay forma de llegar a un dato individual
            desde acá.
          </p>
        </div>

        {/* 1 · Participación */}
        <section className="panel-bloque">
          <h2>Participación</h2>
          <div className="kpis">
            <Kpi valor={porcentaje(razon(r.con_actividad, r.personas))} rotulo="entró al menos una vez"
                 detalle={`${r.con_actividad} de ${r.personas}`} />
            <Kpi valor={String(r.activos_30d)} rotulo="activos en 30 días"
                 detalle={`${porcentaje(razon(r.activos_30d, r.personas))} de la institución`}
                 tono={razon(r.activos_30d, r.personas) < 0.3 ? "alerta" : undefined} />
            <Kpi valor={String(sinActividad)} rotulo="nunca entraron"
                 detalle="no registran ningún evento"
                 tono={sinActividad > r.personas * 0.2 ? "alerta" : undefined} />
          </div>
        </section>

        {/* 2 · Avance de la acreditación */}
        <section className="panel-bloque">
          <h2>Avance de la acreditación</h2>
          <div className="kpis">
            <Kpi valor={porcentaje(r.avance_acreditacion)} rotulo="de los bloques completos"
                 detalle={`${r.bloques_completos} de ${r.bloques}`} destacado />
            <Kpi valor={porcentaje(r.avance_critico)} rotulo="en las dimensiones críticas"
                 detalle={`${r.criticos_completos} de ${r.bloques_criticos} · lo que más pesa por rol`} />
            <Kpi valor={String(r.rutas_completas)} rotulo="rutas terminadas"
                 detalle={`${porcentaje(razon(r.rutas_completas, r.personas))} de la institución`} />
            <Kpi valor={r.insignias.toLocaleString("es-CL")} rotulo="medallas otorgadas"
                 detalle="todas con su evaluación aprobada detrás" />
          </div>
        </section>

        {/* 3 · Aprendizaje */}
        <section className="panel-bloque">
          <h2>Aprendizaje</h2>
          <div className="kpis">
            <Kpi valor={r.tasa_aprobacion === null ? "—" : porcentaje(r.tasa_aprobacion)}
                 rotulo="de los intentos aprueba"
                 detalle={`${r.intentos_aprobados} de ${r.intentos} evaluaciones rendidas`} />
            <Kpi valor={puntaje === null ? "—" : porcentaje(puntaje)} rotulo="puntaje promedio"
                 detalle="sobre umbrales de 80% y 85%" />
          </div>

          <div className="tabla-envoltorio">
            <table className="tabla-panel">
              <caption>Dónde se atora la institución, por dimensión</caption>
              <thead>
                <tr>
                  <th>Dimensión</th><th>Avance</th><th>Rendidas</th>
                  <th>Aprueba</th><th>Puntaje</th><th>En riesgo</th>
                </tr>
              </thead>
              <tbody>
                {dimensiones.map((d) => {
                  const avance = razon(d.bloques_completos, d.bloques);
                  const aprueba = d.intentos ? razon(d.intentos_aprobados, d.intentos) : null;
                  return (
                    <tr key={d.dimension}>
                      <th scope="row">{d.nombre}</th>
                      <td>
                        <span className="mini-barra">
                          <span style={{ width: `${avance * 100}%` }} />
                        </span>
                        <b>{porcentaje(avance)}</b>
                      </td>
                      <td>{d.intentos}</td>
                      <td className={aprueba !== null && aprueba < 0.75 ? "flojo" : ""}>
                        {aprueba === null ? "—" : porcentaje(aprueba)}
                      </td>
                      <td>{d.puntaje_promedio === null ? "—" : porcentaje(Number(d.puntaje_promedio))}</td>
                      <td className={d.en_riesgo ? "flojo" : ""}>{d.en_riesgo}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>

        {/* 4 · Riesgo */}
        <section className="panel-bloque">
          <h2>Riesgo</h2>
          <div className="kpis">
            <Kpi valor={String(r.personas_en_riesgo)} rotulo="agotaron sus intentos"
                 detalle="un bloque esperando acompañamiento"
                 tono={r.personas_en_riesgo ? "alerta" : undefined} />
            <Kpi valor={String(sinActividad)} rotulo="sin ninguna actividad"
                 detalle="la acreditación es de todos y estos no partieron"
                 tono={sinActividad ? "alerta" : undefined} />
          </div>
          <p className="panel-nota">
            El riesgo se mira por unidad, nunca por persona: la tabla de abajo dice
            dónde concentrar el acompañamiento, no a quién señalar.
          </p>
        </section>

        {/* 5 · Cultura de calidad */}
        <section className="panel-bloque">
          <h2>Cultura de calidad</h2>
          <div className="kpis">
            <Kpi valor={porcentaje(razon(r.personas_que_juegan, r.personas))}
                 rotulo="juega sin que se lo exijan"
                 detalle={`${r.personas_que_juegan} personas · los juegos no dan XP acreditable`}
                 destacado />
          </div>
          <p className="panel-nota">
            Es el único indicador voluntario del panel. Jugar no acerca a nadie a una
            medalla ni mueve su escalón, así que quien juega lo hace porque quiere —y
            eso es lo más parecido a cultura de calidad que el sistema puede medir.
          </p>
        </section>

        <TablaGrupos titulo="Por sede y escuela" filas={unidades} k={r.umbral_anonimato}
                     nota={desglosadas < r.personas
                       ? `${r.personas - desglosadas} personas están en unidades bajo el umbral y no aparecen desglosadas.`
                       : undefined} />
        <TablaGrupos titulo="Por rol" filas={roles} k={r.umbral_anonimato} />

        <p className="panel-pie">
          Ley 21.719 · Los grupos con menos de {r.umbral_anonimato} personas se pliegan en
          una fila reservada para que el total siga cuadrando sin individualizar a nadie.
          El filtro vive en la base de datos, no en esta pantalla.
          {r.personas_de_prueba > 0 && (
            <> · <b>{r.personas_de_prueba} de las {r.personas} personas son población
            sintética de prueba.</b></>
          )}
        </p>
      </div>
    );
  };

  return (
    <Marco
      yo={p.yo}
      bloques={p.totalBloques}
      completos={p.bloquesCompletos}
      seccion="panel"
      onIrA={p.onIrA}
      crumb={<><b>Vista de dirección</b> · Panel institucional</>}
      onSalir={p.onSalir}
    >
      {cuerpo()}
    </Marco>
  );
}

function Kpi(
  { valor, rotulo, detalle, tono, destacado }: {
    valor: string; rotulo: string; detalle: string;
    tono?: "alerta"; destacado?: boolean;
  },
) {
  return (
    <div className={`kpi ${tono ?? ""} ${destacado ? "destacado" : ""}`}>
      <div className="kpi-valor">{valor}</div>
      <div className="kpi-rotulo">{rotulo}</div>
      <div className="kpi-detalle">{detalle}</div>
    </div>
  );
}

function TablaGrupos(
  { titulo, filas, k, nota }: { titulo: string; filas: FilaPanel[]; k: number; nota?: string },
) {
  return (
    <section className="panel-bloque">
      <h2>{titulo}</h2>
      <div className="tabla-envoltorio">
        <table className="tabla-panel">
          <thead>
            <tr>
              <th>Grupo</th><th>Personas</th><th>Avance</th>
              <th>Entraron</th><th>Terminaron</th><th>En riesgo</th><th>Juegan</th>
            </tr>
          </thead>
          <tbody>
            {filas.map((f) => {
              const avance = razon(f.bloques_completos, f.bloques);
              return (
                <tr key={f.grupo} className={f.es_reservado ? "reservada" : ""}>
                  <th scope="row">
                    {f.grupo}
                    {f.es_reservado && <span className="chip-reservado">reservado</span>}
                  </th>
                  <td>{f.personas}</td>
                  <td>
                    <span className="mini-barra"><span style={{ width: `${avance * 100}%` }} /></span>
                    <b>{porcentaje(avance)}</b>
                  </td>
                  <td>{porcentaje(razon(f.con_actividad, f.personas))}</td>
                  <td>{f.rutas_completas}</td>
                  <td className={f.en_riesgo ? "flojo" : ""}>{f.en_riesgo}</td>
                  <td>{porcentaje(razon(f.juegan, f.personas))}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {nota && <p className="panel-nota">{nota}</p>}
      {!filas.some((f) => f.es_reservado) && (
        <p className="panel-nota">
          Ningún grupo quedó bajo las {k} personas, así que no hubo nada que plegar.
        </p>
      )}
    </section>
  );
}
