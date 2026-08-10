import { useEffect, useState } from "react";
import { api, type PersonaDisponible } from "../api";

/**
 * Ingreso — login de desarrollo "actuar como" (S-18).
 *
 * No hay formulario de correo y contraseña: se eliminó a propósito de la cáscara,
 * porque el sistema no guarda contraseñas ni acá ni en producción. Cuando exista el
 * tenant, este mismo lugar muestra el botón de Microsoft Entra y nada más cambia.
 */
export function Ingreso({ onEntrar }: { onEntrar: () => void }) {
  const [gente, setGente] = useState<PersonaDisponible[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [entrando, setEntrando] = useState<string | null>(null);

  useEffect(() => {
    api.personasDisponibles().then(setGente).catch((e) => setError(e.message));
  }, []);

  async function entrar(p: PersonaDisponible) {
    setEntrando(p.id);
    try {
      await api.actuarComo(p.id);
      onEntrar();
    } catch (e) {
      setError(e instanceof Error ? e.message : "no se pudo entrar");
      setEntrando(null);
    }
  }

  return (
    <div className="ingreso">
      <div className="ingreso-izq">
        <div>
          <span className="pill" style={{ background: "rgba(255,255,255,.12)", color: "#fff" }}>
            Ruta de autoevaluación y acreditación · 2026–2027
          </span>
          <h1 className="ingreso-title">
            La acreditación<br />es <span>de todos.</span><br />Y se recorre.
          </h1>
          <p className="ingreso-lead">
            Cada colaborador recorre las cinco dimensiones de evaluación al nivel de
            exigencia que le pide su cargo, siguiendo los hitos reales del proceso.
          </p>
        </div>
        <div className="ingreso-stats">
          <div><div className="n">5</div><div className="l">Dimensiones</div></div>
          <div><div className="n">13</div><div className="l">Hitos 2026–2027</div></div>
          <div><div className="n">6</div><div className="l">Cargos</div></div>
        </div>
      </div>

      <div className="ingreso-der">
        <div className="login-card">
          <h2>Entrar a tu ruta</h2>
          <p className="sub">Elige con qué cargo quieres recorrer el sistema.</p>

          {error && <div className="error" style={{ margin: "0 0 16px" }}>{error}</div>}
          {!gente && !error && <p className="cargando" style={{ padding: 0 }}>cargando…</p>}

          {gente?.map((p) => (
            <button
              key={p.id}
              className="persona-op"
              onClick={() => entrar(p)}
              disabled={entrando !== null}
              aria-pressed={entrando === p.id}
            >
              <div className="avatar" style={{ background: "linear-gradient(135deg,#E11D3C,#F4B740)" }}>
                {p.nombre.replace(/\(.*?\)/g, "").trim().split(/\s+/).map((x) => x[0]).slice(0, 2).join("").toUpperCase()}
              </div>
              <div className="info">
                <div className="n">{p.nombre}</div>
                <div className="c">{p.cargo}{p.unidad ? ` · ${p.unidad}` : ""}</div>
              </div>
              {p.ve_panel_institucional && <span className="marca">panel</span>}
            </button>
          ))}

          <p className="nota-dev">
            Ingreso de desarrollo. En producción esto es Microsoft Entra ID con la cuenta
            institucional; el sistema no guarda contraseñas en ningún caso.
          </p>
        </div>
      </div>
    </div>
  );
}
