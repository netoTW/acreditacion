/**
 * Verifica que el bundle que se le sirve al navegador sea REALMENTE de navegador.
 *
 * Existe por un fallo real del gate A4: se estaba sirviendo
 * node_modules/colyseus.js/dist/colyseus.js, que en la version 0.15.28 es un UMD
 * compilado contra Node (require de net, tls, http, buffer). En el navegador
 * reventaba con "Buffer is not defined" ANTES de asignar el global, y por eso
 * Colyseus.Client no era constructor y el boton "Entrar" no hacia nada.
 *
 * Este test carga el bundle en un sandbox SIN Buffer, SIN require, SIN process
 * y SIN module/exports — es decir, lo mas parecido a un navegador que se puede
 * armar en Node. Si el bundle depende de algo de Node, revienta igual que
 * reventaba en Chrome.
 *
 *   node pruebas/verifica-cliente-navegador.js
 */
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const BUNDLE = path.join(__dirname, "..", "cliente", "vendor", "colyseus.js");

let fallos = 0;
function verificar(nombre, condicion, detalle = "") {
  console.log(`${condicion ? "  ok  " : " FALLA"}  ${nombre}${detalle ? "  ·  " + detalle : ""}`);
  if (!condicion) fallos++;
}

console.log("\n  Verificación del cliente de navegador\n");

// ---------- 1. El bundle existe ----------
if (!fs.existsSync(BUNDLE)) {
  console.error("  FALTA el bundle. Corre: npm run build:cliente\n");
  process.exit(1);
}
const codigo = fs.readFileSync(BUNDLE, "utf8");
verificar("el bundle existe", true, `${(codigo.length / 1024).toFixed(1)} kb`);

// ---------- 2. Estático: nada de Node adentro ----------
// Se buscan USOS del identificador Buffer (Buffer., Buffer(, new Buffer, typeof Buffer),
// no la palabra suelta: el bundle trae el string "Buffer too large" en un mensaje de
// error de msgpack, que es inofensivo. Tampoco matchea ArrayBuffer, porque \b exige
// borde de palabra y en "ArrayBuffer" no lo hay.
const usosBuffer = codigo.match(/\bBuffer\s*[.([]|new\s+Buffer\b|typeof\s+Buffer\b/g) || [];
verificar("no usa el Buffer de Node", usosBuffer.length === 0,
  usosBuffer.length ? usosBuffer.join(", ") : "ninguno");

const builtins = ["net", "tls", "zlib", "bufferutil", "utf-8-validate", "child_process"];
const requeridos = builtins.filter((m) =>
  new RegExp(`require\\(["']${m}["']\\)`).test(codigo)
);
verificar("no hace require de módulos de Node", requeridos.length === 0,
  requeridos.length ? requeridos.join(", ") : "ninguno");

verificar("no referencia process.versions.node", !/process\.versions/.test(codigo));

// ---------- 3. Dinámico: se evalúa en un sandbox tipo navegador ----------
const errores = [];
class WebSocketStub {
  constructor(url) { this.url = url; this.readyState = 0; }
  send() {} close() {} addEventListener() {}
}
WebSocketStub.OPEN = 1;

const ventana = {
  WebSocket: WebSocketStub,
  location: { protocol: "https:", host: "provoke-expedited-gusty.ngrok-free.dev", hostname: "provoke-expedited-gusty.ngrok-free.dev" },
  document: { createElement: () => ({ style: {}, setAttribute() {}, appendChild() {} }), addEventListener() {} },
  navigator: { userAgent: "verificador" },
  console: { log() {}, warn() {}, error: (...a) => errores.push(a.join(" ")) },
  setTimeout, clearTimeout, setInterval, clearInterval,
  fetch: () => Promise.reject(new Error("sin red en el verificador")),
  XMLHttpRequest: class { open() {} send() {} setRequestHeader() {} },
  localStorage: { getItem: () => null, setItem() {}, removeItem() {} },
  TextDecoder, TextEncoder, URL, Math, JSON, Date, Promise, Array, Object, Error,
};
ventana.window = ventana;
ventana.self = ventana;
ventana.globalThis = ventana;

// Explícitamente ausentes: Buffer, require, process, module, exports.
const contexto = vm.createContext(ventana);

let cargó = true;
try {
  vm.runInContext(codigo, contexto, { filename: "colyseus.js", timeout: 5000 });
} catch (e) {
  cargó = false;
  verificar("el bundle carga sin Buffer/require/process", false, e.message);
}
if (cargó) verificar("el bundle carga sin Buffer/require/process", true);

// ---------- 4. Lo que reportó el navegador ----------
const Colyseus = contexto.Colyseus;
verificar("define el global Colyseus", !!Colyseus, Colyseus ? "presente" : "undefined");
verificar("Colyseus.Client es un constructor",
  !!Colyseus && typeof Colyseus.Client === "function",
  Colyseus ? typeof Colyseus?.Client : "n/a");

if (Colyseus && typeof Colyseus.Client === "function") {
  try {
    const c = new Colyseus.Client("wss://provoke-expedited-gusty.ngrok-free.dev");
    verificar("new Colyseus.Client(wss://…) construye", !!c, c.constructor.name);
    verificar("expone joinOrCreate", typeof c.joinOrCreate === "function");
    verificar("expone joinById", typeof c.joinById === "function");
  } catch (e) {
    verificar("new Colyseus.Client(wss://…) construye", false, e.message);
  }
}

verificar("no escribió errores en consola al cargar", errores.length === 0,
  errores.slice(0, 2).join(" | ") || "ninguno");

console.log(
  fallos === 0
    ? "\n  El bundle es apto para navegador.\n"
    : `\n  ${fallos} verificación(es) en rojo.\n`
);
process.exit(fallos === 0 ? 0 : 1);
