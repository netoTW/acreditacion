#!/usr/bin/env bash
# runner.sh — modo fábrica nocturno para Somos Calidad
# Procesa la cola de tareas de tareas.md con Claude Code, una por una, con guardas.
# Uso:  ./scripts/runner.sh            (corre la cola completa)
#       ./scripts/runner.sh --once     (una sola tarea y para — para cimientos)
#       ./scripts/runner.sh --no-install (no reinstala deps entre tareas)
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COLA="$ROOT/tareas.md"
LOG="$ROOT/BITACORA.md"
ONCE=false
NO_INSTALL=false
for arg in "$@"; do
  case "$arg" in
    --once) ONCE=true ;;
    --no-install) NO_INSTALL=true ;;
  esac
done

# --- guardas de existencia ---
[[ -f "$COLA" ]] || { echo "ABORT: no existe tareas.md — nada que correr."; exit 1; }
command -v claude >/dev/null 2>&1 || { echo "ABORT: 'claude' (Claude Code) no está en PATH."; exit 1; }

stamp() { date "+%Y-%m-%d %H:%M"; }
log() { echo "- [$(stamp)] $*" >> "$LOG"; }

echo "== runner Somos Calidad — $(stamp) ==" | tee -a "$LOG"

# Toma tareas pendientes: líneas que empiezan con "- [ ]"
mapfile -t PENDIENTES < <(grep -n '^- \[ \]' "$COLA" || true)
[[ ${#PENDIENTES[@]} -eq 0 ]] && { echo "No hay tareas pendientes. Fin."; exit 0; }

for entry in "${PENDIENTES[@]}"; do
  LINE_NO="${entry%%:*}"
  TASK="${entry#*- \[ \] }"
  echo ">> Tarea (línea $LINE_NO): $TASK"
  log "INICIO tarea: $TASK"

  # Invoca Claude Code en modo no interactivo contra la tarea, guiado por CLAUDE.md
  PROMPT="Lee CLAUDE.md. Ejecuta SOLO esta tarea contra las specs existentes, con sus tests/gates: \"$TASK\". Respeta el protocolo de 3 niveles: default y adelante en dudas menores; escala solo lo irreversible. Al terminar, corre los gates. Si un gate cuyo objetivo existe falla, NO lo deshabilites: reporta."
  set +e
  claude -p "$PROMPT" 2>>"$LOG"
  RC=$?
  set -e 2>/dev/null || true

  # Fallo del AGENTE (límite de plan / invocación) ≠ fallo del módulo: aborta sin quemar la tarea
  if [[ $RC -ne 0 ]]; then
    echo "!! Claude Code devolvió código $RC — posible límite de plan o error de invocación."
    echo "   NO se marca la tarea como fallida (no es fallo del módulo). Se aborta el runner."
    log "ABORT por RC=$RC en tarea: $TASK (no cuenta como bloqueo del módulo)"
    exit $RC
  fi

  # Marca la tarea como hecha en la cola (dentro del commit, no antes)
  sed -i.bak "${LINE_NO}s/^- \[ \]/- [x]/" "$COLA" && rm -f "$COLA.bak"
  log "FIN tarea (marcada [x]): $TASK"

  # Commit del avance aprobado por gates
  if command -v git >/dev/null 2>&1; then
    git -C "$ROOT" add -A
    git -C "$ROOT" commit -m "runner: $TASK" >/dev/null 2>&1 && log "commit hecho: $TASK"
  fi

  $ONCE && { echo "Modo --once: una tarea hecha, saliendo."; break; }
done

echo "== runner terminado — $(stamp) =="
echo "Revisa BITACORA.md: los [x] por encima, ataca los [!] con plan de destrabe."
