import { useState } from "react";
import { token } from "./api";
import { Ingreso } from "./pantallas/Ingreso";
import { MiRuta } from "./pantallas/MiRuta";

export function App() {
  const [conSesion, setConSesion] = useState(() => Boolean(token.leer()));

  if (!conSesion) return <Ingreso onEntrar={() => setConSesion(true)} />;

  return (
    <MiRuta
      onSalir={() => {
        token.borrar();
        setConSesion(false);
      }}
    />
  );
}
