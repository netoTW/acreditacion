# Sistema de diseño

> Extraído literalmente de la cáscara (`referencia-demo/somos-calidad.html`). **La identidad
> ya está decidida y no se rediseña**: esto la congela como contrato para que ningún
> constructor invente un color. CLAUDE.md §14 exige que esto exista antes de la primera
> pantalla.

## Tokens

```css
:root{
  /* Color */
  --tinta:#2B0B1E;        /* base vino profundo */
  --tinta-2:#3D1229;      /* superficies oscuras */
  --tinta-3:#511a37;      /* hover oscuro */
  --carmin:#E11D3C;       /* rojo AIEP / acción */
  --carmin-soft:#ff6b82;
  --oro:#F4B740;          /* XP / insignias */
  --menta:#2DD4A7;        /* progreso / logro */
  --menta-deep:#0f9e7d;
  --marfil:#FBF7F5;       /* fondo claro */
  --blanco:#ffffff;
  --niebla:#8A7A83;       /* texto muted */
  --linea:#ECE2E6;        /* bordes claros */
  --linea-osc:rgba(255,255,255,.10);

  /* Elevación */
  --sombra:0 1px 2px rgba(43,11,30,.06), 0 8px 28px rgba(43,11,30,.08);
  --sombra-alta:0 20px 60px rgba(43,11,30,.22);

  /* Radio */
  --r:16px; --r-sm:10px; --r-lg:24px;

  /* Tipografía */
  --disp:"Bricolage Grotesque", system-ui, sans-serif;
  --body:"Inter", system-ui, sans-serif;
  --mono:"JetBrains Mono", ui-monospace, monospace;
}
```

## Significado de cada color

Se usa por significado, no por gusto. Un constructor que necesite un color busca acá el rol.

| Token | Rol | Dónde |
|---|---|---|
| `--tinta` | superficie institucional, texto principal | sidebar, mapa de ruta, escenarios |
| `--carmin` | acción y estado actual | botón primario, bloque en curso, alertas |
| `--oro` | XP e insignias | barra de XP, medallas, recompensas |
| `--menta` | progreso y logro consumado | bloques completos, aprobado, tendencia buena |
| `--niebla` | texto secundario | descripciones, metadatos |
| `--marfil` | fondo de aplicación | body |

> **Regla:** `--menta` significa *ya está logrado y verificado*. No se usa para "en camino".
> El estado de un bloque no aprobado nunca se pinta de menta — la UI no puede sugerir una
> completitud que no existe.

## Tipografía

| Familia | Uso | Detalle |
|---|---|---|
| Bricolage Grotesque | títulos, cifras grandes, nombres de insignia | 700–800, `letter-spacing:-.02em`, `line-height:1.08` |
| Inter | cuerpo, formularios, navegación | 400–700, `line-height:1.5` |
| JetBrains Mono | XP, posiciones, códigos, contadores | 500–700, siempre con `tabular-nums` |

Las tres se **autohospedan** (S-26): hoy vienen de Google Fonts por CDN y un portal
institucional interno no debe depender de eso.

## Componentes que se portan tal cual

Ya resueltos en la cáscara y que se conservan al migrar a React ([ADR-002](decisiones/ADR-002-frontend.md)):

- `.card` · `.pill` (variantes oro, menta, carmín, tinta) · `.btn` (primary, dark, ghost)
- `.nav-item` con badge · `.persona-card` con barra de XP
- Nodo del mapa de ruta con sus estados `done` / `now` / `lock`
- Generador SVG de insignia por tipo (`mini`, `silver`, `gold`, `master`)
- Escalera de niveles · fila de ranking · tarjeta KPI del dashboard

## Reglas de accesibilidad

Corrigen lo que la cáscara no tiene. Son obligatorias en toda pantalla nueva:

- Todo lo clicable es `button` o `a`. **Ningún `div` con `onclick`.**
- Foco visible siempre; nunca `outline:none` sin reemplazo.
- Alternativas de quiz y evaluación operables por teclado, con `aria-checked` y las teclas
  A–D que la cáscara ya insinúa.
- El mapa de ruta expone estado por texto además de por color: alguien que no distingue
  menta de carmín tiene que poder leer "completo" y "en curso".
- Contraste mínimo 4.5:1 en texto. `--niebla` sobre `--marfil` cumple; sobre `--tinta` no,
  ahí va `rgba(255,255,255,.72)`.
- `prefers-reduced-motion` respetado — la cáscara ya lo hace, se conserva.

## Responsive

Punto de quiebre en **1080 px**, el de la cáscara.

> **Corrección obligatoria (S-28):** hoy bajo 1080 px el sidebar se va a `left:-280px` **sin
> botón que lo abra** y la aplicación queda sin navegación en teléfono. Se agrega el botón
> de menú. Es bloqueante: el gate de la Plaza se prueba con teléfonos.

## Marca de contenido de prueba

Todo bloque generado en esta etapa lleva `es_contenido_prueba: true` y **se ve** (S-27): un
distintivo permanente en la cabecera del bloque y del módulo. Nadie puede confundir el
slice con acreditación oficial.

## Nota sobre la marca real de AIEP

La infografía oficial usa rojo AIEP y azul marino, con el lema *"Con la fuerza de todos"*.
La identidad de la cáscara —vino tinta, carmín, oro, menta— **es la aprobada para este
producto** y es la que manda acá. Queda registrado por si en producción AIEP pide alinear
con su manual de marca: sería un cambio de tokens, no de componentes.
