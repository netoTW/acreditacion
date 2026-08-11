import { useEffect, useState } from "react";
import {
  SesionCaida, api,
  type RankingInstitucional, type RankingUnidad, type FilaUnidad, type Yo,
} from "../api";
import { Marco } from "../componentes/Marco";
import type { Seccion } from "../componentes/Sidebar";

/**
 * Ranking.
 *
 * Tres tablas y una omisión deliberada: **no existe la escalera completa**. Ver
 * el puesto 47.000 de 85.000 no le sirve a nadie y desmotiva a casi todos, así
 * que se muestra la cabeza —que es aspiracional— y tu propia posición, que es la
 * única que puedes mover.
 *
 * Tampoco hay una lista de los últimos. Los rezagados se miran agregados por
 * unidad, en el panel, y sirven para decidir dónde acompañar; una tabla de peores
 * solo sirve para señalar.
 *
 * El dato que hace útil esta pantalla no es la posición: es cuánto XP de juego
 * tienes sin contar por no haber avanzado la ruta. El tope no es un castigo, es
 * lo que se desbloquea avanzando.
 */
type Props = {
  yo: Yo;
  totalBloques: number;
  bloquesCompletos: number;
  onIrA: (s: Seccion) => void;
  onSalir: () => void;
};

const xp = (n: number | string) => Number(n).toLocaleString("es-CL");

export function Ranking(p: Props) {
  const [institucional, setInstitucional] = useState<RankingInstitucional | null>(null);
  const [miUnidad, setMiUnidad] = useState<RankingUnidad | null>(null);
  const [unidades, setUnidades] = useState<FilaUnidad[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.ranking(), api.rankingMiUnidad(), api.rankingUnidades()])
      .then(([i, u, us]) => { setInstitucional(i); setMiUnidad(u); setUnidades(us); })
      .catch((e) => (e instanceof SesionCaida ? p.onSalir() : setError(e.message)));
  }, []);

  const cuerpo = () => {
    if (error)
      return (
        <div className="error">
          <p>{error}</p>
          <button className="btn btn-primary" style={{ marginTop: 14 }}
                  onClick={() => p.onIrA("ruta")}>Volver a mi ruta</button>
        </div>
      );
    if (!institucional || !miUnidad) return <div className="cargando">contando puntos…</div>;

    const yo = institucional.yo;
    const sinContar = institucional.xp_de_juego_sin_contar;

    return (
      <div className="pantalla ranking">
        <div className="pantalla-head">
          <div className="eyebrow">Ranking · {institucional.personas.toLocaleString("es-CL")} personas</div>
          <h1>Dónde vas</h1>
          <p>
            El puntaje es tu <b>XP acreditable</b> más el <b>XP de juego, contado solo
            hasta donde llega tu recorrido</b>. Jugar mucho sin avanzar no escala;
            avanzar y además jugar, sí.
          </p>
        </div>

        {yo && (
          <div className="mi-posicion">
            <div className="mp-bloque">
              <div className="mp-rotulo">Tu posición en la institución</div>
              <div className="mp-valor">
                {yo.posicion}
                <span>de {institucional.personas.toLocaleString("es-CL")}</span>
              </div>
            </div>
            <div className="mp-bloque">
              <div className="mp-rotulo">Tu puntaje</div>
              <div className="mp-valor mono">{xp(yo.xp_ranking)}</div>
              <div className="mp-detalle">
                {xp(yo.xp_acreditable)} acreditable + {xp(Number(yo.xp_ranking) - Number(yo.xp_acreditable))} de juego
              </div>
            </div>
            {institucional.xp_para_subir !== null && (
              <div className="mp-bloque">
                <div className="mp-rotulo">Para subir un puesto</div>
                <div className="mp-valor mono">+{xp(institucional.xp_para_subir)}</div>
              </div>
            )}
          </div>
        )}

        {/* El tope, dicho como lo que es: algo que se desbloquea, no que se pierde. */}
        {sinContar > 0 && (
          <div className="aviso-tope">
            Tienes <b className="mono">{xp(sinContar)} XP de juego sin contar</b> porque el
            juego suma hasta donde llega tu recorrido. Cada bloque que apruebes
            desbloquea esa misma cantidad de puntos que ya ganaste jugando.
          </div>
        )}

        <section className="rk-bloque">
          <h2>En mi unidad</h2>
          {miUnidad.disponible ? (
            <>
              <p className="rk-sub">
                {miUnidad.unidad} · {miUnidad.personas} personas
              </p>
              <Tabla filas={miUnidad.cabeza} yo={miUnidad.yo} conUnidad={false} />
            </>
          ) : (
            <p className="rk-reservado">
              Tu unidad tiene menos de {miUnidad.umbral_anonimato} personas, así que
              acá no hay ranking nominal: en un grupo tan chico, una posición con
              nombre identifica a una persona. Tu avance lo ves en tu ruta, y la
              comparación entre unidades está más abajo.
            </p>
          )}
        </section>

        <section className="rk-bloque">
          <h2>Cabeza de la institución</h2>
          <p className="rk-sub">
            Los {institucional.cabeza.length} primeros. No hay tabla completa ni lista
            de los últimos: el rezago se acompaña, no se publica.
          </p>
          <Tabla filas={institucional.cabeza} yo={yo} conUnidad />
        </section>

        <section className="rk-bloque">
          <h2>Entre sedes y escuelas</h2>
          <p className="rk-sub">
            Compara <b>promedios</b>, no totales: una sede grande no gana por ser grande.
          </p>
          <div className="tabla-envoltorio">
            <table className="tabla-panel">
              <thead>
                <tr><th>Unidad</th><th>Personas</th><th>XP promedio</th>
                  <th>Avance</th><th>Con avance</th><th>Medallas</th></tr>
              </thead>
              <tbody>
                {unidades.map((u) => (
                  <tr key={u.unidad} className={u.es_reservado ? "reservada" : ""}>
                    <th scope="row">
                      {!u.es_reservado && <b className="rk-pos">{u.posicion}</b>}
                      {u.unidad}
                      {u.es_reservado && <span className="chip-reservado">reservado</span>}
                    </th>
                    <td>{u.personas}</td>
                    <td className="mono">{xp(u.xp_promedio)}</td>
                    <td>
                      <span className="mini-barra">
                        <span style={{ width: `${Number(u.avance) * 100}%` }} />
                      </span>
                      <b>{Math.round(Number(u.avance) * 100)}%</b>
                    </td>
                    <td>{Math.round(Number(u.con_avance) * 100)}%</td>
                    <td>{u.insignias}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <p className="panel-pie">
          Ley 21.719 · Las unidades con menos de {miUnidad.umbral_anonimato} personas no
          producen ranking nominal ni aparecen con su nombre en la comparación entre
          sedes. El filtro vive en las vistas de la base, no en esta pantalla, y ningún
          endpoint del ranking devuelve identificadores de personas.
        </p>
      </div>
    );
  };

  return (
    <Marco
      yo={p.yo}
      bloques={p.totalBloques}
      completos={p.bloquesCompletos}
      seccion="ranking"
      onIrA={p.onIrA}
      crumb={<><b>Vista colaborador</b> · Ranking</>}
      onSalir={p.onSalir}
    >
      {cuerpo()}
    </Marco>
  );
}

function Tabla(
  { filas, yo, conUnidad }: {
    filas: { posicion: number; nombre: string; unidad?: string | null; xp_ranking: number | string;
             insignias: number; escalon: string; soy_yo: boolean }[];
    yo: { posicion: number } | null;
    conUnidad: boolean;
  },
) {
  const estoyEnLaCabeza = filas.some((f) => f.soy_yo);
  return (
    <>
      <div className="tabla-envoltorio">
        <table className="tabla-panel">
          <thead>
            <tr>
              <th>#</th><th>Persona</th>{conUnidad && <th>Unidad</th>}
              <th>Escalón</th><th>Medallas</th><th>Puntaje</th>
            </tr>
          </thead>
          <tbody>
            {filas.map((f) => (
              <tr key={`${f.posicion}-${f.nombre}`} className={f.soy_yo ? "soy-yo" : ""}>
                <td className="rk-celda-pos">{f.posicion}</td>
                <th scope="row">
                  {f.nombre}
                  {f.soy_yo && <span className="chip-yo">tú</span>}
                </th>
                {conUnidad && (
                  <td className="rk-unidad">
                    {/* Sin nombre de unidad = grupo bajo el umbral. La persona sigue
                        en la tabla; lo que se reserva es la etiqueta que la vuelve
                        ubicable dentro de un grupo diminuto. */}
                    {f.unidad ?? <span className="rk-reserva">unidad reservada</span>}
                  </td>
                )}
                <td className="rk-unidad">{f.escalon}</td>
                <td>{f.insignias}</td>
                <td className="mono">{xp(f.xp_ranking)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {!estoyEnLaCabeza && yo && (
        <p className="rk-sub">Tú vas en el puesto {yo.posicion}.</p>
      )}
    </>
  );
}
