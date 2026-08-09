#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
watch.py — Panel de observación en vivo para el proyecto (estilo "flota de agentes").

Qué muestra, auto-refrescándose solo, en el navegador:
  - TAREAS: avance de la cola (tareas.md): hechas / pendientes / bloqueadas.
  - TIMELINE: los últimos commits (lo que la "flota" fue produciendo).
  - DECISIONES: cuántas decisiones autónomas tomaron los agentes (nivel 1).
  - BITÁCORA: las últimas líneas del control de obra.
  - TOKENS Y COSTO: tirados de ccusage (si está instalado); si no, muestra cómo instalarlo.

Uso (parado en la carpeta del repo):
    python3 watch.py
Luego abre solo el navegador en http://localhost:8787

No requiere pip install: usa solo la librería estándar de Python.
Para tokens/costo necesita ccusage (opcional):  npx ccusage  ó  npm i -g ccusage
"""

import http.server, socketserver, json, subprocess, os, re, webbrowser, threading, time
from datetime import datetime

PORT = 8787
ROOT = os.getcwd()

# ---------------------------------------------------------------- lectores de estado

def read_file(name, limit_lines=None):
    path = os.path.join(ROOT, name)
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
        if limit_lines:
            lines = lines[-limit_lines:]
        return lines
    except Exception:
        return None

def parse_tareas():
    lines = read_file("tareas.md") or []
    done, pend, block, items = 0, 0, 0, []
    for ln in lines:
        s = ln.strip()
        if s.startswith("- [x]") or s.startswith("- [X]"):
            done += 1; items.append({"e": "done", "t": s[5:].strip()})
        elif s.startswith("- [!]"):
            block += 1; items.append({"e": "block", "t": s[5:].strip()})
        elif s.startswith("- [ ]"):
            pend += 1; items.append({"e": "pend", "t": s[5:].strip()})
    total = done + pend + block
    return {"done": done, "pend": pend, "block": block, "total": total, "items": items}

def git(args):
    try:
        out = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                             text=True, timeout=6)
        return out.stdout.strip()
    except Exception:
        return ""

def parse_git():
    branch = git(["rev-parse", "--abbrev-ref", "HEAD"]) or "—"
    raw = git(["log", "-15", "--pretty=format:%h\x1f%s\x1f%cr\x1f%an"])
    commits = []
    if raw:
        for line in raw.splitlines():
            parts = line.split("\x1f")
            if len(parts) == 4:
                commits.append({"hash": parts[0], "msg": parts[1],
                                "when": parts[2], "who": parts[3]})
    # ¿actividad reciente? (último commit hace < 10 min)
    last_epoch = git(["log", "-1", "--pretty=format:%ct"])
    active = False
    if last_epoch.isdigit():
        active = (time.time() - int(last_epoch)) < 600
    return {"branch": branch, "commits": commits, "active": active}

def parse_decisiones():
    lines = read_file("DECISIONES-AUTONOMAS.md") or []
    decs = [l.strip("-* ").strip() for l in lines
            if l.strip().startswith(("-", "*")) and len(l.strip()) > 3]
    return {"count": len(decs), "last": decs[-5:]}

def parse_bitacora():
    lines = read_file("BITACORA.md", limit_lines=12) or []
    return [l for l in lines if l.strip()]

# ---------------------------------------------------------------- ccusage (tokens/costo)

def try_ccusage():
    """Intenta obtener tokens y costo desde ccusage en JSON. Defensivo ante cambios de schema."""
    candidates = [
        ["ccusage", "daily", "--json"],
        ["npx", "-y", "ccusage@latest", "daily", "--json"],
        ["bunx", "ccusage", "daily", "--json"],
    ]
    for cmd in candidates:
        try:
            out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=40)
            if out.returncode != 0 or not out.stdout.strip():
                continue
            data = json.loads(out.stdout)
            return summarize_ccusage(data, source=cmd[0])
        except FileNotFoundError:
            continue
        except Exception:
            continue
    return {"ok": False}

def _find_num(d, needles):
    """Busca recursivamente la primera clave que contenga alguno de los 'needles' y sea numérica."""
    found = 0
    if isinstance(d, dict):
        for k, v in d.items():
            kl = str(k).lower()
            if any(n in kl for n in needles) and isinstance(v, (int, float)):
                found += v
            elif isinstance(v, (dict, list)):
                found += _find_num(v, needles)
    elif isinstance(d, list):
        for it in d:
            found += _find_num(it, needles)
    return found

def summarize_ccusage(data, source=""):
    # totales de tokens y costo, robusto a variantes de schema
    total_cost = _find_num(data, ["totalcost", "cost"])
    total_tok = _find_num(data, ["totaltokens"])
    if total_tok == 0:
        total_tok = _find_num(data, ["inputtokens"]) + _find_num(data, ["outputtokens"])
    # intenta sacar el día de hoy si viene una lista "daily"
    today_cost, today_tok = None, None
    arr = data.get("daily") if isinstance(data, dict) else None
    if isinstance(arr, list) and arr:
        last = arr[-1]
        today_cost = _find_num(last, ["cost"])
        today_tok = _find_num(last, ["totaltokens"]) or (
            _find_num(last, ["inputtokens"]) + _find_num(last, ["outputtokens"]))
    return {"ok": True, "source": source,
            "total_cost": round(total_cost, 2),
            "total_tokens": int(total_tok),
            "today_cost": round(today_cost, 2) if today_cost is not None else None,
            "today_tokens": int(today_tok) if today_tok is not None else None}

# ---------------------------------------------------------------- snapshot

_CACHE = {"data": {"ok": False, "loading": True}}

def _cc_poller():
    """Hilo de fondo: refresca tokens/costo cada 30s SIN bloquear nunca el panel."""
    if os.environ.get("CCUSAGE_OFF"):
        _CACHE["data"] = {"ok": False}
        return
    while True:
        try:
            _CACHE["data"] = try_ccusage()
        except Exception:
            _CACHE["data"] = {"ok": False}
        time.sleep(30)

def snapshot():
    cc = _CACHE["data"]   # lectura instantánea, jamás bloquea
    return {
        "project": os.path.basename(ROOT),
        "now": datetime.now().strftime("%H:%M:%S"),
        "tareas": parse_tareas(),
        "git": parse_git(),
        "decisiones": parse_decisiones(),
        "bitacora": parse_bitacora(),
        "cc": cc,
    }

# ---------------------------------------------------------------- HTML

HTML = r"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<title>Flota · panel</title>
<style>
:root{--bg:#0a0a0c;--panel:#121216;--line:#26262e;--txt:#e7e7ea;--dim:#7a7a86;
--violet:#a78bfa;--green:#34d399;--amber:#fbbf24;--red:#fb7185;--cyan:#38bdf8;}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--txt);font-family:"JetBrains Mono",ui-monospace,
SFMono-Regular,Menlo,monospace;padding:22px;font-size:13px;line-height:1.5}
.head{display:flex;align-items:center;gap:14px;margin-bottom:20px;flex-wrap:wrap}
.dot{width:9px;height:9px;border-radius:50%;background:var(--green);
box-shadow:0 0 0 4px rgba(52,211,153,.18);animation:p 1.8s infinite}
.dot.idle{background:var(--dim);box-shadow:none;animation:none}
@keyframes p{50%{box-shadow:0 0 0 9px rgba(52,211,153,0)}}
.title{font-weight:700;font-size:18px;letter-spacing:-.02em}
.title b{color:var(--violet)}
.muted{color:var(--dim);font-size:11px}
.eyebrow{color:var(--dim);font-size:10px;letter-spacing:.16em;text-transform:uppercase;margin-bottom:9px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:14px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:15px;border-left:3px solid var(--violet)}
.kpi.g{border-left-color:var(--green)}.kpi.a{border-left-color:var(--amber)}
.kpi.c{border-left-color:var(--cyan)}.kpi.r{border-left-color:var(--red)}
.kpi .l{color:var(--dim);font-size:10px;text-transform:uppercase;letter-spacing:.1em}
.kpi .v{font-size:26px;font-weight:700;margin-top:6px;letter-spacing:-.02em}
.kpi .s{color:var(--dim);font-size:11px;margin-top:2px}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px;margin-bottom:12px}
.bar{height:8px;background:#1e1e24;border-radius:20px;overflow:hidden;margin:10px 0;display:flex}
.bar>i{height:100%}
.seg-done{background:var(--green)}.seg-block{background:var(--red)}.seg-pend{background:#2f2f38}
.row{display:flex;gap:9px;align-items:flex-start;padding:6px 0;border-bottom:1px solid #1b1b21}
.row:last-child{border:none}
.tag{font-size:9px;padding:2px 7px;border-radius:20px;flex:none;margin-top:2px;font-weight:700}
.tag.done{background:rgba(52,211,153,.15);color:var(--green)}
.tag.pend{background:rgba(122,122,134,.15);color:var(--dim)}
.tag.block{background:rgba(251,113,133,.15);color:var(--red)}
.row .t{font-size:12px;color:#cfcfd6}
.commit{display:flex;gap:10px;padding:7px 0;border-bottom:1px solid #1b1b21}
.commit:last-child{border:none}
.commit .h{color:var(--amber);font-size:11px}
.commit .m{flex:1;font-size:12px;color:#cfcfd6;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.commit .w{color:var(--dim);font-size:10px;flex:none}
pre.bit{white-space:pre-wrap;color:#b9b9c2;font-size:11px;line-height:1.7}
.note{background:rgba(251,191,36,.08);border:1px solid rgba(251,191,36,.3);border-radius:10px;padding:12px;color:#e8d9a8;font-size:11.5px;line-height:1.7}
.note code{background:#000;padding:2px 6px;border-radius:5px;color:var(--amber)}
a{color:var(--cyan)}
@media(max-width:820px){.grid{grid-template-columns:1fr 1fr}.cols{grid-template-columns:1fr}}
</style></head><body>
<div class="head">
  <span class="dot" id="dot"></span>
  <span class="title">Flota · <b id="proj">…</b></span>
  <span class="muted" id="branch"></span>
  <span class="muted" style="margin-left:auto" id="clock"></span>
</div>

<div class="grid" id="kpis"></div>

<div class="cols">
  <div>
    <div class="panel">
      <div class="eyebrow">Cola de tareas</div>
      <div class="bar" id="taskbar"></div>
      <div id="tasklist"></div>
    </div>
    <div class="panel">
      <div class="eyebrow">Decisiones autónomas de los agentes</div>
      <div id="decs"></div>
    </div>
  </div>
  <div>
    <div class="panel">
      <div class="eyebrow">Timeline — lo que la flota fue produciendo</div>
      <div id="commits"></div>
    </div>
    <div class="panel">
      <div class="eyebrow">Bitácora (control de obra)</div>
      <pre class="bit" id="bit"></pre>
    </div>
  </div>
</div>

<script>
const fmt = n => n>=1000 ? (n/1000).toFixed(n>=100000?0:1)+'k' : String(n);
async function tick(){
  let d; try{ d = await (await fetch('/data')).json(); }catch(e){ return; }
  document.getElementById('proj').textContent = d.project;
  document.getElementById('branch').textContent = 'git:'+d.git.branch;
  document.getElementById('clock').textContent = 'act. '+d.now;
  document.getElementById('dot').className = 'dot'+(d.git.active?'':' idle');

  // KPIs
  const t = d.tareas, cc = d.cc || {};
  const loading = cc.loading;
  const costV = cc.ok ? ('$'+(cc.today_cost!=null?cc.today_cost:cc.total_cost)) : (loading?'…':'—');
  const tokV  = cc.ok ? fmt(cc.today_tokens!=null?cc.today_tokens:cc.total_tokens) : (loading?'…':'—');
  document.getElementById('kpis').innerHTML = `
    <div class="kpi g"><div class="l">Tareas hechas</div><div class="v">${t.done}<span style="font-size:14px;color:var(--dim)"> / ${t.total}</span></div><div class="s">${t.pend} pendientes</div></div>
    <div class="kpi ${t.block?'r':''}"><div class="l">Bloqueadas</div><div class="v">${t.block}</div><div class="s">${t.block?'requieren destrabe':'sin bloqueos'}</div></div>
    <div class="kpi c"><div class="l">Costo API ${cc.today_cost!=null?'(hoy)':'(total)'}</div><div class="v">${costV}</div><div class="s">${cc.ok?('estimado · '+cc.source):'ccusage no detectado'}</div></div>
    <div class="kpi a"><div class="l">Tokens ${cc.today_tokens!=null?'(hoy)':'(total)'}</div><div class="v">${tokV}</div><div class="s">${cc.ok?'in+out':'—'}</div></div>`;

  // barra de tareas
  const pct = x => t.total? (x/t.total*100):0;
  document.getElementById('taskbar').innerHTML =
    `<i class="seg-done" style="width:${pct(t.done)}%"></i><i class="seg-block" style="width:${pct(t.block)}%"></i><i class="seg-pend" style="width:${pct(t.pend)}%"></i>`;
  document.getElementById('tasklist').innerHTML = t.items.slice(0,10).map(i=>
    `<div class="row"><span class="tag ${i.e}">${i.e==='done'?'✓':i.e==='block'?'!':'·'}</span><span class="t">${esc(i.t)}</span></div>`).join('') || '<span class="muted">tareas.md vacío o aún sin cola</span>';

  // commits
  document.getElementById('commits').innerHTML = d.git.commits.length ? d.git.commits.map(c=>
    `<div class="commit"><span class="h">${c.hash}</span><span class="m">${esc(c.msg)}</span><span class="w">${esc(c.when)}</span></div>`).join('') : '<span class="muted">sin commits todavía</span>';

  // decisiones
  const de = d.decisiones;
  document.getElementById('decs').innerHTML =
    `<div style="font-size:22px;font-weight:700">${de.count}<span style="font-size:12px;color:var(--dim)"> decisiones nivel 1</span></div>` +
    de.last.map(x=>`<div class="row"><span class="tag pend">·</span><span class="t">${esc(x)}</span></div>`).join('');

  // bitácora / nota ccusage
  let bit = d.bitacora.join('\n') || '(sin entradas)';
  if(!cc.ok){
    bit += '\n\n';
    document.getElementById('bit').innerHTML =
      esc(d.bitacora.join('\n')||'(sin entradas)') +
      '<div class="note" style="margin-top:10px">Para ver <b>tokens y costo</b> instala ccusage (lee los logs locales de Claude Code, no envía nada):<br><code>npx ccusage@latest</code> &nbsp;o&nbsp; <code>npm i -g ccusage</code><br>Luego este panel los toma solo.</div>';
  } else {
    document.getElementById('bit').textContent = bit;
  }
}
function esc(s){return String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
tick(); setInterval(tick, 3500);
</script>
</body></html>"""

# ---------------------------------------------------------------- servidor

class Server(socketserver.TCPServer):
    allow_reuse_address = True   # evita "address already in use" al reiniciar

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        if self.path.startswith("/data"):
            body = json.dumps(snapshot()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers(); self.wfile.write(body)
        else:
            body = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers(); self.wfile.write(body)

def main():
    os.chdir(ROOT)
    url = f"http://localhost:{PORT}"
    print(f"\n  Panel de la flota corriendo → {url}")
    print(f"  Leyendo el proyecto en: {ROOT}")
    print("  (déjalo corriendo y solo mira el navegador · Ctrl+C para salir)\n")
    threading.Thread(target=_cc_poller, daemon=True).start()
    if not os.environ.get("NO_BROWSER"):
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    with Server(("", PORT), Handler) as httpd:
        try: httpd.serve_forever()
        except KeyboardInterrupt: print("\n  panel detenido.\n")

if __name__ == "__main__":
    main()
