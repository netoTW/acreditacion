const http = require("http");
const path = require("path");
const express = require("express");
const { Server } = require("colyseus");
const { WebSocketTransport } = require("@colyseus/ws-transport");
const { SalaPlaza } = require("./SalaPlaza");

const PUERTO = Number(process.env.PUERTO || process.env.PORT || 2567);

const fs = require("fs");

const app = express();

// El cliente de Colyseus se autohospeda (S-26) desde cliente/vendor/, que produce
// `npm run build:cliente` con esbuild.
//
// OJO: NO servir node_modules/colyseus.js/dist/. En la version 0.15.28 ese archivo
// es un UMD compilado contra Node (require de net/tls/buffer): en el navegador
// revienta con "Buffer is not defined" antes de asignar el global, y Colyseus.Client
// queda undefined. Eso tumbó el gate A4. El build correcto sale de la condicion
// "browser" del package (lib/index.js), que es lo que empaqueta esbuild.
const BUNDLE_CLIENTE = path.join(__dirname, "..", "cliente", "vendor", "colyseus.js");
if (!fs.existsSync(BUNDLE_CLIENTE)) {
  console.error("\n  Falta cliente/vendor/colyseus.js — corre: npm run build:cliente\n");
  process.exit(1);
}

app.use(express.static(path.join(__dirname, "..", "cliente")));

// Healthcheck: lo exige CLAUDE.md §11 para el compose.
app.get("/salud", (_req, res) => res.json({ ok: true, servicio: "realtime" }));

const servidorHttp = http.createServer(app);
const gameServer = new Server({
  transport: new WebSocketTransport({ server: servidorHttp }),
});

gameServer.define("plaza", SalaPlaza);

servidorHttp.listen(PUERTO, "0.0.0.0", () => {
  console.log("");
  console.log("  Plaza Virtual — spike de realtime");
  console.log(`  local:  http://localhost:${PUERTO}`);
  console.log("");
  console.log("  Para el gate A4 hay que salir de localhost. En otra terminal:");
  console.log(`      ngrok http ${PUERTO}`);
  console.log("  y abrir la URL publica en el telefono Y en el notebook.");
  console.log("");
});
