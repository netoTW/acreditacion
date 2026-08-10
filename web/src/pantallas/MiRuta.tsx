import type { BloqueDeRuta, Yo } from "../api";
import { MapaRuta } from "../componentes/MapaRuta";
import { Marco } from "../componentes/Marco";
import { ESCALERA, progresoDeEscalon } from "../componentes/Sidebar";

type Props = {
  yo: Yo;
  bloques: BloqueDeRuta[];
  onAbrirBloque: (bloqueRutaId: string) => void;
  onSalir: () => void;
};

export function MiRuta({ yo, bloques, onAbrirBloque, onSalir }: Props) {
  const completos = bloques.filter((b) => b.estado === "completo").length;
  const enCurso = bloques.find((b) => b.estado === "disponible" || b.estado === "en_curso");
  const { actual } = progresoDeEscalon(yo.xp_acreditable);
  const hayPrueba = bloques.some((b) => b.es_contenido_prueba);

  return (
    <Marco
      yo={yo}
      bloques={bloques.length}
      completos={completos}
      marcaPrueba={hayPrueba}
      crumb={<><b>Vista colaborador</b> · Mi Ruta</>}
      onSalir={onSalir}
    >
      <div className="pantalla">
        <div className="pantalla-head">
          <div className="eyebrow">Tu recorrido · {bloques.length} dimensiones de evaluación</div>
          <h1>Mi Ruta de Acreditación</h1>
          <p>
            Cada bloque es una dimensión del modelo de evaluación, al nivel de estándar que
            le corresponde a tu cargo, y está anclado a un hito real del proceso.
          </p>
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
              {yo.xp_acreditable.toLocaleString("es-CL")} XP acreditable · escalón {actual.nombre}
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
