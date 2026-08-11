import { useState, type ReactNode } from "react";
import type { Yo } from "../api";
import { Sidebar, type Seccion } from "./Sidebar";

/**
 * Shell de la aplicación: sidebar, barra superior y el hueco de la pantalla.
 *
 * Existe para que Mi Ruta, Bloque y el visor de módulo no repitan el mismo
 * armazón. La marca de contenido de prueba vive acá, así que ninguna pantalla
 * puede olvidarse de mostrarla (S-27).
 */
type Props = {
  yo: Yo;
  crumb: ReactNode;
  bloques: number;
  completos: number;
  marcaPrueba?: boolean;
  seccion?: Seccion;
  onIrA?: (s: Seccion) => void;
  onSalir: () => void;
  children: ReactNode;
};

export function Marco({ yo, crumb, bloques, completos, marcaPrueba, seccion = "ruta", onIrA, onSalir, children }: Props) {
  const [menu, setMenu] = useState(false);

  return (
    <div className="app">
      <Sidebar
        yo={yo}
        abierto={menu}
        bloques={bloques}
        completos={completos}
        onCerrar={() => setMenu(false)}
        seccion={seccion}
        onIrA={onIrA}
        onSalir={onSalir}
      />
      <div className="main">
        <div className="topbar">
          <button className="menu-btn" onClick={() => setMenu(true)} aria-label="Abrir menú">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 6h18M3 12h18M3 18h18" />
            </svg>
          </button>
          <div className="crumb">{crumb}</div>
          {marcaPrueba && <span className="marca-prueba">Contenido de prueba</span>}
        </div>
        {children}
      </div>
    </div>
  );
}
