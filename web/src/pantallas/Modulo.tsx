import { useEffect, useState } from "react";
import { SesionCaida, api, type Bloque, type Modulo as TModulo, type Yo } from "../api";
import { Marco } from "../componentes/Marco";
import { Microlearning } from "../componentes/Microlearning";

type Props = {
  bloqueRutaId: string;
  moduloId: string;
  yo: Yo;
  totalBloques: number;
  bloquesCompletos: number;
  onVolver: () => void;
  onIrAModulo: (moduloId: string) => void;
  onPracticar: () => void;
  onCalibrar: () => void;
  onXpGanado: () => void;
  onSalir: () => void;
};

export function Modulo(p: Props) {
  const [bloque, setBloque] = useState<Bloque | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [guardando, setGuardando] = useState(false);
  const [xpGanado, setXpGanado] = useState<number | null>(null);

  useEffect(() => {
    api.bloque(p.bloqueRutaId)
      .then(setBloque)
      .catch((e) => (e instanceof SesionCaida ? p.onSalir() : setError(e.message)));
  }, [p.bloqueRutaId]);

  // Al cambiar de módulo se vuelve arriba: si no, se entra al siguiente a media lectura.
  useEffect(() => {
    setXpGanado(null);
    window.scrollTo({ top: 0 });
  }, [p.moduloId]);

  const modulo: TModulo | undefined = bloque?.modulos.find((m) => m.id === p.moduloId);
  const siguiente = bloque && modulo
    ? bloque.modulos.find((m) => m.orden === modulo.orden + 1)
    : undefined;

  async function terminar() {
    if (!modulo) return;
    setGuardando(true);
    try {
      const r = await api.completarModulo(modulo.id);
      if (!r.ya_estaba) {
        setXpGanado(r.xp_otorgado);
        p.onXpGanado();
      }
      // Se recarga el bloque para que el estado quede al día antes de navegar.
      const fresco = await api.bloque(p.bloqueRutaId);
      setBloque(fresco);
      if (siguiente) p.onIrAModulo(siguiente.id);
      else p.onVolver();
    } catch (e) {
      if (e instanceof SesionCaida) p.onSalir();
      else setError(e instanceof Error ? e.message : "no se pudo guardar");
    } finally {
      setGuardando(false);
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
    if (!bloque) return <div className="cargando">cargando el módulo…</div>;
    if (!modulo)
      return (
        <div className="error">
          <p>Ese módulo no está en este bloque.</p>
          <button className="btn btn-primary" style={{ marginTop: 14 }} onClick={p.onVolver}>
            Volver al bloque
          </button>
        </div>
      );

    return (
      <div className="pantalla">
        <button className="volver" onClick={p.onVolver}>← {bloque.dimension_nombre}</button>

        <div className="lector">
          <div className="lector-barra">
            <span className="mono">Módulo {modulo.orden} de {bloque.modulos.length}</span>
            <div className="lector-track">
              <div className="lector-fill" style={{ width: `${(modulo.orden / bloque.modulos.length) * 100}%` }} />
            </div>
            <span className="mono">{modulo.duracion_min} min</span>
          </div>

          <div className="card lector-card">
            <div className="lector-tags">
              <span className="pill carmin">{bloque.dimension_nombre}</span>
              <span className="pill oro">Tramo N{modulo.nivel_estandar_origen}</span>
              {modulo.completado && <span className="pill menta">Ya visto</span>}
            </div>

            <h1 className="lector-titulo">{modulo.titulo.split(" · ").slice(1).join(" · ")}</h1>

            {/* El propio contenido trae el aviso de prueba; acá no se repite. */}
            <Microlearning texto={modulo.cuerpo} ocultarTitulo />

            {xpGanado !== null && (
              <div className="xp-ganado" role="status">+{xpGanado} XP · módulo completado</div>
            )}

            <div className="lector-pie">
              <button className="btn btn-ghost" onClick={p.onVolver}>Volver al bloque</button>
              <button className="btn btn-oro" onClick={p.onPracticar}>⚡ Practicar</button>
              <button className="btn btn-oro" onClick={p.onCalibrar}>🎯 Calibre</button>
              <button className="btn btn-primary" onClick={terminar} disabled={guardando}>
                {guardando
                  ? "guardando…"
                  : modulo.completado
                    ? siguiente ? "Siguiente módulo →" : "Volver al bloque"
                    : siguiente ? `Listo · siguiente módulo →` : "Listo · terminar bloque"}
              </button>
            </div>
            {!modulo.completado && (
              <p className="lector-nota">
                Al marcarlo sumas {modulo.xp} XP acreditable. La medalla del bloque llega
                solo con la evaluación aprobada.
              </p>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <Marco
      yo={p.yo}
      bloques={p.totalBloques}
      completos={p.bloquesCompletos}
      marcaPrueba={modulo?.es_contenido_prueba}
      crumb={<><b>Vista colaborador</b> · {bloque?.dimension_nombre ?? "Bloque"} · Módulo</>}
      onSalir={p.onSalir}
    >
      {cuerpo()}
    </Marco>
  );
}
