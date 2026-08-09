#!/usr/bin/env bash
# ¿Tienen dientes los tests de integridad?
#
# Rompe un candado a la vez y exige que la suite SE PONGA ROJA. Si con el candado
# saboteado los tests siguen pasando, el candado no estaba siendo verificado y la
# garantía es imaginaria.
set -uo pipefail
cd "$(dirname "$0")"

MUTACIONES=(
  "DROP TRIGGER tg_insignia_respaldada ON insignia|el trigger que exige intento aprobado"
  "ALTER TABLE insignia ALTER COLUMN intento_evaluacion_id DROP NOT NULL|el NOT NULL del respaldo"
  "DROP TRIGGER tg_intento_coherente ON intento_evaluacion|el trigger de coherencia puntaje/veredicto"
  "DROP TRIGGER tg_evento_append_only ON evento_gamificacion|el append-only de los eventos"
  "ALTER TABLE evento_gamificacion DROP CONSTRAINT evento_gamificacion_check|la prohibición de XP acreditable desde juegos"
)

echo ""
echo "  Banco de mutación — cada candado roto DEBE poner la suite en rojo"
echo ""

sobrevivientes=0
for entrada in "${MUTACIONES[@]}"; do
  sql="${entrada%%|*}"
  desc="${entrada##*|}"
  salida=$(MUTACION="$sql" ./correr-pruebas.sh -q 2>&1 | tail -1)
  if echo "$salida" | grep -q "failed"; then
    fallos=$(echo "$salida" | grep -oE '[0-9]+ failed' | head -1)
    printf "  ok    se rompe %-52s → %s\n" "$desc" "$fallos"
  else
    printf " SOBREVIVE  %-52s → nadie lo notó\n" "$desc"
    sobrevivientes=$((sobrevivientes + 1))
  fi
done

echo ""
if [ "$sobrevivientes" -eq 0 ]; then
  echo "  Todos los candados están verificados: romper cualquiera pone la suite en rojo."
  exit 0
fi
echo "  $sobrevivientes candado(s) sin verificar. La garantía de esos es imaginaria."
exit 1
