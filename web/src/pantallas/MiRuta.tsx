import type { BloqueDeRuta, Yo } from "../api";
import { MapaRuta, pct } from "../componentes/MapaRuta";
import { Marco } from "../componentes/Marco";
import { ESCALERA, progresoDeEscalon, type Seccion } from "../componentes/Sidebar";

type Props = {
  yo: Yo;
  bloques: BloqueDeRuta[];
  onAbrirBloque: (bloqueRutaId: string) => void;
  onIrA: (s: Seccion) => void;
  onSalir: () => void;
};

export function MiRuta({ yo, bloques, onAbrirBloque, onIrA, onSalir }: Props) {
  const completos = bloques.filter((b) => b.estado === "completo").length;
  const enCurso = bloques.find((b) => b.estado === "disponible" || b.estado === "en_curso");
  const { actual } = progresoDeEscalon(yo.xp_acreditable);
  const hayPrueba = bloques.some((b) => b.es_contenido_prueba);
  const criticas = bloques.filter((b) => b.es_critica).length;

  return (
    <Marco
      yo={yo}
      bloques={bloques.length}
      completos={completos}
      marcaPrueba={hayPrueba}
      seccion="ruta"
      onIrA={onIrA}
      crumb={<><b>Vista colaborador</b> · Mi Ruta</>}
      onSalir={onSalir}
    >
      <div className="pantalla">
        <div className="pantalla-head">
          <div className="eyebrow">Tu recorrido · {bloques.length} dimensiones de evaluación</div>
          <h1>Mi Ruta de Acreditación</h1>
          <p>
            Recorres las cinco dimensiones —la acreditación es de todos—, pero no todas
            pesan igual en tu rol. Las dos de mayor impacto son tu <b>ruta crítica</b>:
            exigen más y su medalla es de otro rango.
          </p>
        </div>

        {/* La distribución del rol, que es el dato nuevo de AIEP. Va arriba y completa:
            es lo que explica por qué dos personas ven rutas distintas. */}
        <div className="distribucion">
          <div className="dist-head">
            <span className="eyebrow">Impacto de tu rol por dimensión</span>
            <span className="dist-total">suma 100%</span>
          </div>
          <div className="dist-barras">
            {[...bloques]
              .sort((a, b) => Number(b.peso_ranking) - Number(a.peso_ranking))
              .map((b) => (
                <div key={b.bloque_ruta_id} className={`dist-fila ${b.es_critica ? "critica" : ""}`}>
                  <span className="dist-nombre">
                    {b.dimension_nombre}
                    {b.es_critica && <span className="marca-critica">ruta crítica</span>}
                  </span>
                  <span className="dist-barra">
                    <span style={{ width: `${Number(b.peso_ranking) * 100 * 2.4}%` }} />
                  </span>
                  <span className="dist-pct">{pct(b)}</span>
                  <span className="dist-nivel">
                    nivel {b.nivel_estandar} · {b.es_critica ? "85%" : "80%"} ·{" "}
                    {b.medalla_tipo === "gold" ? "oro" : "plata"}
                  </span>
                </div>
              ))}
          </div>
        </div>

        <div className="ruta-shell">
          <div className="ruta-head">
            <div>
              <h2>{yo.cargo} · {yo.nombre.replace(/\s*\(.*?\)/, "")}</h2>
              <p>
                {enCurso
                  ? `Vas en el bloque ${enCurso.orden}: ${enCurso.dimension_nombre}. Te faltan ${bloques.length - completos} para la graduación.`
                  : completos === bloques.length
                    ? "Completaste los cinco bloques. Falta la graduación."
                    : "Tu ruta está lista para empezar."}
              </p>
            </div>
            <div className="escalera">
              {ESCALERA.map((e) => (
                <span key={e.nombre} className={`lvl ${e.desde <= yo.xp_acreditable ? "on" : ""}`}>
                  {e.nombre === "Maestro de Acreditación" ? "Maestro" : e.nombre}
                </span>
              ))}
            </div>
          </div>

          <MapaRuta
            bloques={bloques}
            onAbrir={(b) => {
              // Un bloque bloqueado no se abre: se llega a él completando el anterior.
              if (b.estado !== "bloqueado") onAbrirBloque(b.bloque_ruta_id);
            }}
          />
        </div>

        <div className="resumen">
          <div className="card">
            <span className="pill menta">Progreso general</span>
            <div className="n">{Math.round((completos / bloques.length) * 100)}%</div>
            <div className="d">{completos} de {bloques.length} bloques completos</div>
          </div>
          <div className="card">
            <span className="pill oro">Insignias</span>
            <div className="n">
              {yo.insignias} <span style={{ fontSize: 16, color: "var(--niebla)" }}>/ {bloques.length}</span>
            </div>
            <div className="d">
              {criticas} de oro en juego · {yo.xp_acreditable.toLocaleString("es-CL")} XP · {actual.nombre}
            </div>
          </div>
          <div className="card">
            <span className="pill carmin">Próximo hito</span>
            <div className="n" style={{ fontSize: 20 }}>{enCurso?.hito ?? "—"}</div>
            <div className="d">
              {enCurso?.periodo_texto ? `${enCurso.periodo_texto} · ${enCurso.hito_titulo}` : "sin hito asignado"}
            </div>
          </div>
        </div>
      </div>
    </Marco>
  );
}
