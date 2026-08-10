import { useEffect, useState } from "react";
import { SesionCaida, api, type BloqueDeRuta, type Yo } from "../api";
import { MapaRuta } from "../componentes/MapaRuta";
import { ESCALERA, Sidebar, progresoDeEscalon } from "../componentes/Sidebar";

export function MiRuta({ onSalir }: { onSalir: () => void }) {
  const [yo, setYo] = useState<Yo | null>(null);
  const [bloques, setBloques] = useState<BloqueDeRuta[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [menu, setMenu] = useState(false);

  useEffect(() => {
    Promise.all([api.yo(), api.miRuta()])
      .then(([y, r]) => { setYo(y); setBloques(r); })
      .catch((e) => {
        // Si la sesión ya no sirve se vuelve al ingreso solo: quedarse en una
        // pantalla de error sin salida es peor que pedir que entre de nuevo.
        if (e instanceof SesionCaida) onSalir();
        else setError(e.message);
      });
  }, [onSalir]);

  // Y ante cualquier otro error, siempre hay puerta de salida.
  if (error)
    return (
      <div className="error">
        <p>{error}</p>
        <button className="btn btn-primary" style={{ marginTop: 14 }} onClick={onSalir}>
          Volver al ingreso
        </button>
      </div>
    );
  if (!yo || !bloques) return <div className="cargando">cargando tu ruta…</div>;

  const completos = bloques.filter((b) => b.estado === "completo").length;
  const enCurso = bloques.find((b) => b.estado === "disponible" || b.estado === "en_curso");
  const insigniasPosibles = bloques.length;
  const { actual } = progresoDeEscalon(yo.xp_acreditable);
  const hayPrueba = bloques.some((b) => b.es_contenido_prueba);

  return (
    <div className="app">
      <Sidebar
        yo={yo}
        abierto={menu}
        bloques={bloques.length}
        completos={completos}
        onCerrar={() => setMenu(false)}
        onSalir={onSalir}
      />

      <div className="main">
        <div className="topbar">
          <button className="menu-btn" onClick={() => setMenu(true)} aria-label="Abrir menú">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 6h18M3 12h18M3 18h18" />
            </svg>
          </button>
          <div className="crumb"><b>Vista colaborador</b> · Mi Ruta</div>
          {/* S-27: la marca de contenido de prueba se VE, no solo está en la base. */}
          {hayPrueba && <span className="marca-prueba">Contenido de prueba</span>}
        </div>

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

            <MapaRuta bloques={bloques} />
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
                {yo.insignias} <span style={{ fontSize: 16, color: "var(--niebla)" }}>/ {insigniasPosibles}</span>
              </div>
              <div className="d">
                {yo.xp_acreditable.toLocaleString("es-CL")} XP acreditable · escalón {actual.nombre}
              </div>
            </div>
            <div className="card">
              <span className="pill carmin">Próximo hito</span>
              <div className="n" style={{ fontSize: 20 }}>
                {enCurso?.hito ?? "—"}
              </div>
              <div className="d">
                {enCurso?.periodo_texto ? `${enCurso.periodo_texto} · ${enCurso.hito_titulo}` : "sin hito asignado"}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
