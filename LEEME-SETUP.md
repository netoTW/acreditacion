# LÉEME — cómo arrancar en tu Mac (paso a paso)

Esto te deja el proyecto montado, conectado a GitHub, y Claude Code listo para
disparar la fábrica. Sigue el orden.

## 1. Ordenar la carpeta

Tu carpeta local de destino (la que tiene la demo) será el repo. Estructura final:

```
SomosCalidad/                 ← acá abres Claude Code (ES el repo)
├── referencia-demo/          ← MUEVE aquí el somos-calidad.html (la cáscara)
├── docs-fuente/              ← la propuesta AIEP + BRIEF-DOMINIO.md
├── CLAUDE.md                 ← constitución (ya incluida en este kit)
├── PROMPT-DE-ARRANQUE.txt    ← lo que pegas en Claude Code
├── scripts/                  ← runner.sh (para el modo fábrica nocturno)
```

Copia el contenido de este kit a tu carpeta SomosCalidad, y mueve tu demo a
`referencia-demo/`. Deja la propuesta comercial (docx/pdf) dentro de `docs-fuente/`.

> Importante: UN SOLO repo. No un repo de git dentro de otro. La demo va como
> subcarpeta de referencia, no como repo aparte.

## 2. Conectar a GitHub (esto era lo que no recordabas)

Abre la Terminal, parado en la carpeta:

```bash
cd ~/ruta/a/SomosCalidad          # ajusta la ruta real

# si gh no está logueado (te pasó con portal-inclusion, quizás ya está):
gh auth login                     # elige GitHub.com → HTTPS → login con navegador

git init
git add -A
git commit -m "Kickoff Somos Calidad: cascara de referencia + kit builder-agents"

# crea el repo privado en GitHub Y lo enlaza con la carpeta local, de una:
gh repo create netoTW/somos-calidad --private --source=. --remote=origin --push
```

Ese último comando es la respuesta a "no recuerdo cómo conectar la carpeta local con
GitHub": `--source=.` toma tu carpeta actual, `--remote=origin` la enlaza, y `--push`
sube el primer commit. Local ↔ GitHub quedan conectados.

Para verificar:
```bash
git remote -v      # debe mostrar origin → github.com/netoTW/somos-calidad
```

De ahí en adelante, cada avance aprobado:
```bash
git add -A && git commit -m "lo que hiciste" && git push
```

## 3. Abrir Claude Code y disparar la fábrica

```bash
cd ~/ruta/a/SomosCalidad
claude
```

Cuando abra y confíe la carpeta, **pega el contenido de PROMPT-DE-ARRANQUE.txt**.
Claude Code va a leer CLAUDE.md automáticamente y arrancar por la auditoría del Día 0.

NO lo dejes construir de una. Primero te entrega la auditoría (qué hay / qué falta /
ambigüedades). La revisas, la apruebas, y recién ahí arranca la Fase 0 de
especificación por tandas.

## 4. Orden recomendado de las primeras sesiones

1. **Auditoría Día 0** (una sesión) → la apruebas.
2. **Spike de la sala 3D** (sesión aparte, en paralelo): que levante el servidor
   Colyseus mínimo. Lo pruebas con tu notebook + tu teléfono conectados por túnel
   (ngrok). Objetivo: ver 2 avatares moverse en tiempo real fuera de localhost. Esto
   despeja la única incógnita real.
3. **Fase 0 — especificación** por tandas (varias sesiones): el arquitecto documenta
   TODO en GitHub (specs, ADRs, supuestos) antes de construir. Tú revisas cada tanda.
4. **Cimientos + modo fábrica:** scaffold, motor de gamificación, generador de
   contenido, integrador, dashboard. Runner de noche, tú integrando de día.

## 5. Dos recordatorios de disciplina (de lo que ya aprendiste)

- **Ataca la sala 3D primero.** Es lo único que no has probado. Si funciona con 2-3
  dispositivos, el resto es terreno conocido y el plazo de ~2 semanas se vuelve firme.
- **Define "listo" desde el inicio** (está en CLAUDE.md §13). Sin ese gate, el "todo
  todo funcionando al 100%" se vuelve infinito. Los 5 puntos verdes = terminado.
