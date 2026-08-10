import type { ReactNode } from "react";

/**
 * Render del microlearning.
 *
 * El Generador produce un subconjunto acotado y conocido de Markdown —`##`, `###`,
 * citas y viñetas con `·`— así que se convierte a mano en vez de traer una
 * librería completa. Nada de HTML crudo: todo pasa por el árbol de React, así que
 * no hay forma de inyectar marcado desde el contenido.
 */
export function Microlearning({ texto, ocultarTitulo }: { texto: string; ocultarTitulo?: boolean }) {
  const bloques: ReactNode[] = [];
  let lista: ReactNode[] = [];

  const cerrarLista = (clave: string) => {
    if (lista.length) {
      bloques.push(<ul key={clave}>{lista}</ul>);
      lista = [];
    }
  };

  texto.split("\n").forEach((cruda, i) => {
    const linea = cruda.trim();
    if (!linea) return cerrarLista(`u${i}`);

    if (linea.startsWith("## ")) {
      cerrarLista(`u${i}`);
      if (!ocultarTitulo) bloques.push(<h2 key={i}>{linea.slice(3)}</h2>);
    } else if (linea.startsWith("### ")) {
      cerrarLista(`u${i}`);
      bloques.push(<h3 key={i}>{linea.slice(4)}</h3>);
    } else if (linea.startsWith("> ")) {
      cerrarLista(`u${i}`);
      bloques.push(<blockquote key={i}>{linea.slice(2)}</blockquote>);
    } else if (linea.startsWith("· ")) {
      lista.push(<li key={i}>{negritas(linea.slice(2))}</li>);
    } else {
      cerrarLista(`u${i}`);
      bloques.push(<p key={i}>{linea}</p>);
    }
  });
  cerrarLista("final");

  return <div className="microlearning">{bloques}</div>;
}

/** Solo `**negrita**`, que es lo único que el generador usa dentro de una línea. */
function negritas(texto: string): ReactNode[] {
  return texto.split("**").map((parte, i) =>
    i % 2 === 1 ? <strong key={i}>{parte}</strong> : <span key={i}>{parte}</span>
  );
}
