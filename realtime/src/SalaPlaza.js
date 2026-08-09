const { Room } = require("colyseus");
const { Participante, EstadoPlaza, MUNDO, VELOCIDAD } = require("./estado");

/** Paleta de la cascara (design-system.md). */
const COLORES = ["#2DD4A7", "#E11D3C", "#7a5cff", "#F4B740", "#22a7f0", "#ff7ac2"];

const MAX_CHARS_MENSAJE = 80;       // S-24, igual que la cascara
const MS_ENTRE_MENSAJES = 1200;     // rate limit por cliente
const MS_VIDA_GLOBO = 5200;
const TICK_MS = 50;                 // 20 Hz

class SalaPlaza extends Room {
  onCreate(opciones) {
    this.maxClients = 60;
    this.setState(new EstadoPlaza());
    this.ultimoMensaje = new Map();

    // El cliente PIDE destino. El servidor decide si es valido y a que velocidad
    // se llega. Sin esto la sala se desincroniza y las posiciones se pueden falsificar.
    this.onMessage("mover", (client, datos) => {
      const p = this.state.participantes.get(client.sessionId);
      if (!p || !datos) return;
      const x = Number(datos.x);
      const y = Number(datos.y);
      if (!Number.isFinite(x) || !Number.isFinite(y)) return;
      p.destinoX = clamp(x, 0, MUNDO.ancho);
      p.destinoY = clamp(y, 0, MUNDO.alto);
    });

    this.onMessage("decir", (client, datos) => {
      const p = this.state.participantes.get(client.sessionId);
      if (!p || !datos) return;

      const ahora = Date.now();
      const previo = this.ultimoMensaje.get(client.sessionId) || 0;
      if (ahora - previo < MS_ENTRE_MENSAJES) return;   // rate limit
      this.ultimoMensaje.set(client.sessionId, ahora);

      const texto = String(datos.texto || "").trim().slice(0, MAX_CHARS_MENSAJE);
      if (!texto) return;

      p.mensaje = texto;
      p.mensajeHasta = ahora + MS_VIDA_GLOBO;

      // En produccion esto ademas se persiste en mensaje_plaza (S-24).
      console.log(`[plaza] ${p.nombre}: ${texto}`);
    });

    this.setSimulationInterval((delta) => this.avanzar(delta), TICK_MS);
    console.log(`[plaza] sala creada · mundo ${MUNDO.ancho}x${MUNDO.alto} tiles`);
  }

  /** El servidor mueve a cada participante hacia su destino. Es la autoridad. */
  avanzar(deltaMs) {
    const paso = VELOCIDAD * (deltaMs / 1000);
    const ahora = Date.now();

    this.state.participantes.forEach((p) => {
      if (p.mensaje && ahora > p.mensajeHasta) p.mensaje = "";

      const dx = p.destinoX - p.x;
      const dy = p.destinoY - p.y;
      const dist = Math.hypot(dx, dy);
      if (dist < 0.02) return;

      p.rot = Math.atan2(dy, dx);
      if (dist <= paso) {
        p.x = p.destinoX;
        p.y = p.destinoY;
      } else {
        p.x += (dx / dist) * paso;
        p.y += (dy / dist) * paso;
      }
    });
  }

  onJoin(client, opciones = {}) {
    const p = new Participante();
    p.id = client.sessionId;
    // SPIKE: la identidad llega por opciones. En produccion llega en un token
    // firmado por la API, para que la sala sepa quien entra sin duplicar la
    // logica de identidad (ADR-001). Esa es la costura y esta aislada aqui.
    p.nombre = String(opciones.nombre || "Invitado").slice(0, 24);
    p.cargo = String(opciones.cargo || "").slice(0, 40);
    p.color = COLORES[this.state.participantes.size % COLORES.length];
    p.x = 2 + Math.random() * (MUNDO.ancho - 4);
    p.y = 2 + Math.random() * (MUNDO.alto - 4);
    p.destinoX = p.x;
    p.destinoY = p.y;
    p.rot = 0;
    p.mensaje = "";
    p.mensajeHasta = 0;
    p.conectadoEn = Date.now();

    this.state.participantes.set(client.sessionId, p);
    console.log(`[plaza] entra ${p.nombre} · conectados: ${this.state.participantes.size}`);
  }

  async onLeave(client, intencional) {
    const p = this.state.participantes.get(client.sessionId);
    const nombre = p ? p.nombre : client.sessionId;

    if (!intencional) {
      // Gate A6: un cliente que refresca debe volver sin romper la sala.
      try {
        console.log(`[plaza] ${nombre} se cayo · esperando reconexion 20s`);
        await this.allowReconnection(client, 20);
        console.log(`[plaza] ${nombre} reconecto`);
        return;
      } catch (e) {
        // no volvio dentro de la ventana
      }
    }

    this.state.participantes.delete(client.sessionId);
    this.ultimoMensaje.delete(client.sessionId);
    console.log(`[plaza] sale ${nombre} · conectados: ${this.state.participantes.size}`);
  }
}

function clamp(v, min, max) {
  return Math.max(min, Math.min(max, v));
}

module.exports = { SalaPlaza };
