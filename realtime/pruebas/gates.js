/**
 * Gates automatizables del Track A.
 *
 * Cubre lo que se puede verificar sin dispositivos: A2 (dos clientes se ven),
 * A3 (el movimiento viaja y lo decide el servidor), A5 (chat y presencia).
 *
 * A4 (dos dispositivos reales fuera de localhost), A6 (reconexion real por
 * refresh) y A7 (tres dispositivos) los verifica el director a mano: son
 * gates de red y de dispositivo, no de logica.
 *
 *   node pruebas/gates.js
 */
const { Client } = require("colyseus.js");

const URL = process.env.URL_PLAZA || "ws://localhost:2567";
const esperar = (ms) => new Promise((r) => setTimeout(r, ms));

let fallos = 0;
function verificar(nombre, condicion, detalle = "") {
  const marca = condicion ? "  ok  " : " FALLA";
  console.log(`${marca}  ${nombre}${detalle ? "  ·  " + detalle : ""}`);
  if (!condicion) fallos++;
}

function participantesDe(sala) {
  const lista = [];
  sala.state.participantes.forEach((p) => lista.push(p));
  return lista;
}

async function main() {
  console.log(`\n  Gates del Track A · ${URL}\n`);

  const clienteA = new Client(URL);
  const clienteB = new Client(URL);

  // ---- A2: dos clientes en la misma sala se ven ----
  // create() y no joinOrCreate(): la prueba corre en su PROPIA sala, para no heredar
  // participantes de navegadores abiertos o de otra corrida.
  const salaA = await clienteA.create("plaza", { nombre: "Ana", cargo: "Rector" });
  await esperar(300);
  const salaB = await clienteB.joinById(salaA.id, { nombre: "Beto", cargo: "Docente" });
  await esperar(600);

  verificar("A2 · A ve a los dos participantes", participantesDe(salaA).length === 2,
    `${participantesDe(salaA).length} participantes`);
  verificar("A2 · B ve a los dos participantes", participantesDe(salaB).length === 2,
    `${participantesDe(salaB).length} participantes`);
  verificar("A2 · A ve el nombre de B",
    participantesDe(salaA).some((p) => p.nombre === "Beto"));

  // ---- A3: el movimiento viaja y la posicion la decide el servidor ----
  const yoEnB = participantesDe(salaB).find((p) => p.id === salaB.sessionId);
  const origen = { x: yoEnB.x, y: yoEnB.y };

  // Se apunta a la esquina MÁS LEJANA desde donde apareció B, no a una fija: el
  // punto de aparición es aleatorio y con un destino cercano el avatar alcanzaba
  // a llegar dentro de la espera, haciendo fallar la prueba por azar.
  const destino = { x: origen.x < 4.5 ? 9 : 0, y: origen.y < 4.5 ? 9 : 0 };
  salaB.send("mover", { x: destino.x, y: destino.y });

  // Se mira A MEDIA CAMINATA: a 2,4 tiles/s son ~0,5 tiles en 200 ms, y la esquina
  // opuesta está siempre a más de 4. Tiene que haberse movido y NO haber llegado.
  await esperar(220);
  const enCamino = participantesDe(salaA).find((p) => p.id === salaB.sessionId);
  const avance = Math.hypot(enCamino.x - origen.x, enCamino.y - origen.y);
  const restante = Math.hypot(destino.x - enCamino.x, destino.y - enCamino.y);

  verificar("A3 · A ve moverse a B", avance > 0.1,
    `avanzó ${avance.toFixed(2)} tiles`);
  verificar("A3 · el servidor interpola, el cliente no teletransporta", restante > 0.5,
    `le faltan ${restante.toFixed(2)} tiles`);

  await esperar(700);

  // El servidor es la autoridad: un destino fuera del mundo se acota.
  salaB.send("mover", { x: 999, y: -50 });
  await esperar(1800);
  const bAcotado = participantesDe(salaA).find((p) => p.id === salaB.sessionId);
  verificar("A3 · el servidor acota destinos fuera del mundo",
    bAcotado.x <= 9.01 && bAcotado.y >= -0.01,
    `(${bAcotado.x.toFixed(1)}, ${bAcotado.y.toFixed(1)})`);

  // ---- A5: chat y presencia ----
  salaA.send("decir", { texto: "Hola, ¿vamos con la dimensión de Docencia?" });
  await esperar(500);
  const aVistoPorB = participantesDe(salaB).find((p) => p.id === salaA.sessionId);
  verificar("A5 · el mensaje de A llega a B", aVistoPorB.mensaje.includes("Docencia"),
    `"${aVistoPorB.mensaje}"`);

  // rate limit: el segundo mensaje inmediato se descarta
  salaA.send("decir", { texto: "PRIMERO" });
  salaA.send("decir", { texto: "SEGUNDO-INMEDIATO" });
  await esperar(500);
  const trasFlood = participantesDe(salaB).find((p) => p.id === salaA.sessionId);
  verificar("A5 · el rate limit descarta el mensaje seguido",
    !trasFlood.mensaje.includes("SEGUNDO-INMEDIATO"), `"${trasFlood.mensaje}"`);

  // truncado a 80 caracteres (S-24)
  await esperar(1300);
  salaA.send("decir", { texto: "x".repeat(200) });
  await esperar(500);
  const trasLargo = participantesDe(salaB).find((p) => p.id === salaA.sessionId);
  verificar("A5 · el mensaje se trunca a 80 caracteres",
    trasLargo.mensaje.length === 80, `${trasLargo.mensaje.length} caracteres`);

  // presencia: al salir, desaparece
  await salaB.leave(true);
  await esperar(700);
  verificar("A5 · al salir B, A queda con un solo participante",
    participantesDe(salaA).length === 1, `${participantesDe(salaA).length} participantes`);

  await salaA.leave(true);
  await esperar(300);

  console.log(
    fallos === 0
      ? "\n  Todos los gates automatizables pasan. Falta A4/A6/A7 con dispositivos reales.\n"
      : `\n  ${fallos} gate(s) en rojo.\n`
  );
  process.exit(fallos === 0 ? 0 : 1);
}

main().catch((e) => {
  console.error("\n  Error corriendo los gates:", e.message, "\n");
  process.exit(1);
});
