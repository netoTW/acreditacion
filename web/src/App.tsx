import { useCallback, useEffect, useState } from "react";
import { SesionCaida, api, token, type BloqueDeRuta, type Yo } from "./api";
import { Bloque } from "./pantallas/Bloque";
import { Ingreso } from "./pantallas/Ingreso";
import { MiRuta } from "./pantallas/MiRuta";
import { Modulo } from "./pantallas/Modulo";
import { Quiz } from "./pantallas/Quiz";

/**
 * Navegación.
 *
 * Tres vistas y un estado, sin router: el slice tiene pocas pantallas y meter una
 * dependencia de enrutado ahora agrega más de lo que resuelve. Cuando entren
 * ranking, insignias y Plaza (D3–D6) se evalúa de nuevo.
 */
type Vista =
  | { t: "ruta" }
  | { t: "bloque"; bloqueRutaId: string }
  | { t: "modulo"; bloqueRutaId: string; moduloId: string }
  | { t: "quiz"; bloqueRutaId: string; moduloId: string; tituloModulo: string };

export function App() {
  const [conSesion, setConSesion] = useState(() => Boolean(token.leer()));
  const [yo, setYo] = useState<Yo | null>(null);
  const [ruta, setRuta] = useState<BloqueDeRuta[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [vista, setVista] = useState<Vista>({ t: "ruta" });

  const salir = useCallback(() => {
    token.borrar();
    setYo(null);
    setRuta(null);
    setVista({ t: "ruta" });
    setConSesion(false);
  }, []);

  /**
   * Identidad primero y datos después, en secuencia.
   *
   * En paralelo, con un token que ya no sirve, ganaba la carrera el error que
   * llegara antes: si respondía `/mi/ruta` primero, la app mostraba "todavía no
   * tienes ruta generada" en vez de detectar la sesión caída y volver al ingreso.
   */
  const cargar = useCallback(async () => {
    try {
      const y = await api.yo();
      const r = await api.miRuta();
      setYo(y);
      setRuta(r);
      setError(null);
    } catch (e) {
      if (e instanceof SesionCaida) salir();
      else setError(e instanceof Error ? e.message : "no se pudo cargar tu ruta");
    }
  }, [salir]);

  useEffect(() => {
    if (conSesion) cargar();
  }, [conSesion, cargar]);

  if (!conSesion) return <Ingreso onEntrar={() => setConSesion(true)} />;

  if (error)
    return (
      <div className="error">
        <p>{error}</p>
        <button className="btn btn-primary" style={{ marginTop: 14 }} onClick={salir}>
          Volver al ingreso
        </button>
      </div>
    );

  if (!yo || !ruta) return <div className="cargando">cargando tu ruta…</div>;

  const completos = ruta.filter((b) => b.estado === "completo").length;
  const comun = {
    yo,
    totalBloques: ruta.length,
    bloquesCompletos: completos,
    onSalir: salir,
  };

  if (vista.t === "bloque")
    return (
      <Bloque
        {...comun}
        bloqueRutaId={vista.bloqueRutaId}
        onVolver={() => { cargar(); setVista({ t: "ruta" }); }}
        onAbrirModulo={(moduloId) =>
          setVista({ t: "modulo", bloqueRutaId: vista.bloqueRutaId, moduloId })}
      />
    );

  if (vista.t === "quiz")
    return (
      <Quiz
        {...comun}
        bloqueRutaId={vista.bloqueRutaId}
        moduloId={vista.moduloId}
        tituloModulo={vista.tituloModulo}
        onVolver={() => setVista({ t: "modulo", bloqueRutaId: vista.bloqueRutaId, moduloId: vista.moduloId })}
        onXpGanado={cargar}
        onSalir={salir}
      />
    );

  if (vista.t === "modulo")
    return (
      <Modulo
        {...comun}
        bloqueRutaId={vista.bloqueRutaId}
        moduloId={vista.moduloId}
        onVolver={() => setVista({ t: "bloque", bloqueRutaId: vista.bloqueRutaId })}
        onIrAModulo={(moduloId) =>
          setVista({ t: "modulo", bloqueRutaId: vista.bloqueRutaId, moduloId })}
        onPracticar={() =>
          setVista({ t: "quiz", bloqueRutaId: vista.bloqueRutaId, moduloId: vista.moduloId,
                     tituloModulo: "Módulo" })}
        onXpGanado={cargar}
        onSalir={salir}
      />
    );

  return (
    <MiRuta
      yo={yo}
      bloques={ruta}
      onAbrirBloque={(bloqueRutaId) => setVista({ t: "bloque", bloqueRutaId })}
      onSalir={salir}
    />
  );
}
