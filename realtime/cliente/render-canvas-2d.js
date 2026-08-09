/**
 * RenderCanvas2D — implementacion de referencia del contrato de render (ADR-004).
 *
 *   montar(contenedor, opciones)
 *   aplicarEstado(participantes)   // en cada patch del servidor
 *   alDestino(callback)            // el usuario pidio caminar a (x, y) del PLANO
 *   desmontar()
 *
 * Portado del canvas isometrico de la cascara. La unica diferencia real es que
 * las posiciones ya no las inventa un setInterval: llegan del servidor.
 *
 * Un Render3D futuro implementa este mismo contrato y la app no cambia.
 */
export function crearRenderCanvas2D() {
  const TILE_W = 52;
  const TILE_H = 24;
  const ORIGEN_Y = 44;

  let cv, ctx, W, H, raf;
  let mundo = { ancho: 9, alto: 9 };
  let participantes = [];
  let cbDestino = null;
  let miId = null;

  const aPantalla = (x, y) => ({
    sx: W / 2 + (x - y) * TILE_W,
    sy: ORIGEN_Y + (x + y) * TILE_H,
  });

  const aPlano = (sx, sy) => {
    const dx = (sx - W / 2) / TILE_W;
    const dy = (sy - ORIGEN_Y) / TILE_H;
    return { x: (dx + dy) / 2, y: (dy - dx) / 2 };
  };

  function dibujarPiso() {
    ctx.fillStyle = "#1c0714";
    ctx.fillRect(0, 0, W, H);
    for (let r = 0; r < mundo.alto; r++) {
      for (let c = 0; c < mundo.ancho; c++) {
        const { sx, sy } = aPantalla(c, r);
        ctx.beginPath();
        ctx.moveTo(sx, sy);
        ctx.lineTo(sx + TILE_W, sy + TILE_H);
        ctx.lineTo(sx, sy + TILE_H * 2);
        ctx.lineTo(sx - TILE_W, sy + TILE_H);
        ctx.closePath();
        ctx.fillStyle = (r + c) % 2 ? "#3D1229" : "#33112a";
        ctx.fill();
        ctx.strokeStyle = "rgba(255,255,255,.04)";
        ctx.stroke();
      }
    }
    const centro = aPantalla(mundo.ancho / 2 - 0.5, mundo.alto / 2 - 0.5);
    ctx.fillStyle = "rgba(225,29,60,.14)";
    ctx.beginPath();
    ctx.ellipse(centro.sx, centro.sy + TILE_H, 170, 68, 0, 0, 7);
    ctx.fill();
    ctx.fillStyle = "rgba(244,183,64,.9)";
    ctx.font = '700 15px "Bricolage Grotesque", system-ui, sans-serif';
    ctx.textAlign = "center";
    ctx.fillText("SALÓN DE ACREDITACIÓN", centro.sx, centro.sy + TILE_H);
  }

  function dibujarAvatar(p) {
    const { sx, sy } = aPantalla(p.x, p.y);
    const soyYo = p.id === miId;

    ctx.fillStyle = "rgba(0,0,0,.3)";
    ctx.beginPath();
    ctx.ellipse(sx, sy + 2, 14, 5, 0, 0, 7);
    ctx.fill();

    ctx.fillStyle = p.color;
    roundRect(ctx, sx - 11, sy - 28, 22, 28, 8);
    ctx.fill();

    ctx.fillStyle = "#f7e2d0";
    ctx.beginPath();
    ctx.arc(sx, sy - 35, 10, 0, 7);
    ctx.fill();

    ctx.fillStyle = soyYo ? "#F4B740" : "#fff";
    ctx.font = (soyYo ? "700 " : "500 ") + '11px Inter, system-ui, sans-serif';
    ctx.textAlign = "center";
    ctx.fillText(p.nombre, sx, sy - 52);

    if (soyYo) {
      ctx.strokeStyle = "#F4B740";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(sx, sy - 14, 22, 0, 7);
      ctx.stroke();
    }
  }

  function dibujarGlobo(p) {
    if (!p.mensaje) return;
    const { sx, sy } = aPantalla(p.x, p.y);
    ctx.font = '500 12px Inter, system-ui, sans-serif';
    const pad = 10, maxW = 220, lh = 16;

    const palabras = p.mensaje.split(" ");
    const lineas = [];
    let linea = "";
    palabras.forEach((w) => {
      if (ctx.measureText(linea + " " + w).width > maxW) {
        lineas.push(linea.trim());
        linea = w;
      } else linea += " " + w;
    });
    lineas.push(linea.trim());

    const bw = Math.min(maxW, Math.max(...lineas.map((l) => ctx.measureText(l).width))) + pad * 2;
    const bh = lineas.length * lh + pad * 1.6;
    let bx = Math.max(8, Math.min(W - bw - 8, sx - bw / 2));
    const by = Math.max(8, sy - 64 - bh);

    ctx.fillStyle = "#fff";
    roundRect(ctx, bx, by, bw, bh, 11);
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(sx - 7, by + bh);
    ctx.lineTo(sx + 7, by + bh);
    ctx.lineTo(sx, by + bh + 9);
    ctx.closePath();
    ctx.fill();
    ctx.strokeStyle = p.color;
    ctx.lineWidth = 2;
    roundRect(ctx, bx, by, bw, bh, 11);
    ctx.stroke();

    ctx.fillStyle = "#2B0B1E";
    ctx.textAlign = "left";
    lineas.forEach((l, i) => ctx.fillText(l, bx + pad, by + pad + 3 + i * lh + 9));
    ctx.textAlign = "center";
  }

  function bucle() {
    dibujarPiso();
    const orden = [...participantes].sort((a, b) => a.x + a.y - (b.x + b.y));
    orden.forEach(dibujarAvatar);
    orden.forEach(dibujarGlobo);
    raf = requestAnimationFrame(bucle);
  }

  return {
    nombre: "canvas-2d",

    montar(contenedor, opciones = {}) {
      miId = opciones.miId || null;
      mundo = opciones.mundo || mundo;

      cv = document.createElement("canvas");
      cv.width = 1100;
      cv.height = 500;
      cv.style.width = "100%";
      cv.style.display = "block";
      cv.style.borderRadius = "14px";
      cv.style.cursor = "pointer";
      contenedor.appendChild(cv);

      ctx = cv.getContext("2d");
      W = cv.width;
      H = cv.height;

      cv.addEventListener("click", (e) => {
        if (!cbDestino) return;
        const r = cv.getBoundingClientRect();
        const sx = (e.clientX - r.left) * (W / r.width);
        const sy = (e.clientY - r.top) * (H / r.height);
        const destino = aPlano(sx, sy);
        // El cliente PIDE. El servidor decide (ADR-004).
        cbDestino(destino);
      });

      bucle();
    },

    aplicarEstado(lista) {
      participantes = lista;
    },

    alDestino(cb) {
      cbDestino = cb;
    },

    desmontar() {
      cancelAnimationFrame(raf);
      cv?.remove();
      cv = ctx = null;
    },
  };
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  if (ctx.roundRect) {
    ctx.roundRect(x, y, w, h, r);
    return;
  }
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}
