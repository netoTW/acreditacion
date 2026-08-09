/**
 * Gate A6 — reconexión.
 *
 * Un cliente que se cae (refresh, túnel que parpadea, pantalla bloqueada del
 * teléfono) tiene que volver SIN romper la sala y sin perder su identidad.
 *
 * Se simula la caída con room.leave(false): el `false` marca la salida como NO
 * consentida, que es exactamente lo que ve el servidor cuando alguien se cae de
 * verdad. Ahí entra allowReconnection.
 *
 *   node pruebas/gate-a6-reconexion.js
 */
const { Client } = require("colyseus.js");

const URL = process.env.URL_PLAZA || "ws://localhost:2567";
const esperar = (ms) => new Promise((r) => setTimeout(r, ms));

let fallos = 0;
function verificar(nombre, condicion, detalle = "") {
  console.log(`${condicion ? "  ok  " : " FALLA"}  ${nombre}${detalle ? "  ·  " + detalle : ""}`);
  if (!condicion) fallos++;
}

const listar = (sala) => {
  const l = [];
  sala.state.participantes.forEach((p) => l.push(p));
  return l;
};

async function main() {
  console.log(`\n  Gate A6 · reconexión · ${URL}\n`);

  // create() y no joinOrCreate(): la prueba corre en su PROPIA sala. Si no, hereda
  // participantes de sesiones anteriores (navegadores abiertos, otra corrida) y los
  // conteos dan cualquier cosa.
  const testigo = await new Client(URL).create("plaza", { nombre: "Testigo", cargo: "Rector" });
  await esperar(300);

  const cliente = new Client(URL);
  let sala = await cliente.joinById(testigo.id, { nombre: "Caedizo", cargo: "Docente" });
  await esperar(600);

  const sessionOriginal = sala.sessionId;
  const tokenReconexion = sala.reconnectionToken;
  verificar("hay token de reconexión", !!tokenReconexion);
  verificar("el testigo ve a los dos antes de la caída", listar(testigo).length === 2,
    `${listar(testigo).length} participantes`);

  // Se posiciona en un punto reconocible y se ESPERA A QUE LLEGUE. Si se mide a
  // media caminata, el servidor lo sigue moviendo y la comparación es contra un
  // punto que ya cambió por diseño.
  sala.send("mover", { x: 7, y: 7 });
  let posAntes = null;
  for (let i = 0; i < 30; i++) {
    await esperar(200);
    const p = listar(testigo).find((q) => q.id === sessionOriginal);
    if (p && Math.hypot(p.x - 7, p.y - 7) < 0.05) { posAntes = { x: p.x, y: p.y }; break; }
  }
  verificar("llega al destino antes de la caída", !!posAntes,
    posAntes ? `(${posAntes.x.toFixed(2)}, ${posAntes.y.toFixed(2)})` : "no llegó");
  if (!posAntes) { const p = listar(testigo).find((q) => q.id === sessionOriginal); posAntes = { x: p.x, y: p.y }; }

  // ---- la caída ----
  await sala.leave(false);
  await esperar(1200);

  verificar("tras la caída el testigo NO pierde la sala", !!testigo.state,
    `${listar(testigo).length} participantes visibles`);
  verificar("el caído sigue en la sala durante la ventana de gracia",
    listar(testigo).some((p) => p.id === sessionOriginal),
    "no se borró de inmediato");

  // ---- la vuelta ----
  let volvio = true;
  try {
    sala = await cliente.reconnect(tokenReconexion);
  } catch (e) {
    volvio = false;
    verificar("reconecta dentro de la ventana", false, e.message);
  }
  await esperar(800);

  if (volvio) {
    verificar("reconecta dentro de la ventana", true);
    verificar("conserva la misma sessionId", sala.sessionId === sessionOriginal,
      `${sessionOriginal.slice(0, 8)}…`);
    verificar("el testigo sigue viendo dos participantes", listar(testigo).length === 2,
      `${listar(testigo).length}`);

    const despues = listar(testigo).find((p) => p.id === sessionOriginal);
    const conservoPosicion =
      despues && Math.hypot(despues.x - posAntes.x, despues.y - posAntes.y) < 0.5;
    verificar("conserva su posición en el salón", conservoPosicion,
      `(${posAntes.x.toFixed(1)}, ${posAntes.y.toFixed(1)}) → (${despues.x.toFixed(1)}, ${despues.y.toFixed(1)})`);

    // La sala sigue operativa después de la reconexión.
    sala.send("decir", { texto: "volví" });
    await esperar(600);
    const trasVolver = listar(testigo).find((p) => p.id === sessionOriginal);
    verificar("puede volver a hablar tras reconectar",
      trasVolver.mensaje === "volví", `"${trasVolver.mensaje}"`);

    await sala.leave(true);
  }

  await esperar(500);
  verificar("al salir de verdad, el testigo queda solo", listar(testigo).length === 1,
    `${listar(testigo).length} participante`);

  await testigo.leave(true);
  await esperar(300);

  console.log(fallos === 0 ? "\n  Gate A6 en verde.\n" : `\n  ${fallos} en rojo.\n`);
  process.exit(fallos === 0 ? 0 : 1);
}

main().catch((e) => {
  console.error("\n  Error corriendo A6:", e.message, "\n");
  process.exit(1);
});
