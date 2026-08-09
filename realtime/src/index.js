const http = require("http");
const path = require("path");
const express = require("express");
const { Server } = require("colyseus");
const { WebSocketTransport } = require("@colyseus/ws-transport");
const { SalaPlaza } = require("./SalaPlaza");

const PUERTO = Number(process.env.PUERTO || process.env.PORT || 2567);

const app = express();
app.use(express.static(path.join(__dirname, "..", "cliente")));

// El cliente de Colyseus se sirve desde node_modules, no desde un CDN (S-26).
app.use(
  "/vendor",
  express.static(path.join(__dirname, "..", "node_modules", "colyseus.js", "dist"))
);

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
