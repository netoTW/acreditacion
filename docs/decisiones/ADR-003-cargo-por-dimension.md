# ADR-003 — Modelo Cargo × Dimensión: el contenido se genera una vez, las rutas se componen

**Estado:** aceptado · **Fecha:** 2026-08-09 · **Decide:** arquitecto, sobre encuadre del director

## Contexto

El director corrigió el encuadre del Día 0: el sistema se arma en torno a la ruta oficial
de AIEP. De ahí salen dos hechos duros ([DOMINIO-RUTA-AIEP.md](../DOMINIO-RUTA-AIEP.md)):

1. Las **5 dimensiones** son el esqueleto del contenido.
2. Los **cargos no son las dimensiones**: un cargo toca varias dimensiones y una dimensión
   la tocan varios cargos.

La restricción explícita es que el contenido se genere **una vez por dimensión**, y que
cada ruta de cargo sea una **selección y ponderación** de esas dimensiones. Un modelo
ingenuo generaría 6 cargos × 5 dimensiones = **30 contenidos distintos**, que es
precisamente lo que hay que evitar: es caro, es imposible de mantener y hace que el
experto CNA de AIEP tenga que validar treinta veces lo mismo.

Pero si el contenido de una dimensión es **idéntico** para todos los cargos, se pierde la
personalización, que es justamente lo que el slice tiene que demostrar ("deben verse
claramente rutas y medallas distintas por cargo").

## El hallazgo que resuelve la tensión

El modelo real de la CNA ya trae la respuesta. Textual de la fuente:

> **Estándares:** indicadores más específicos que establecen niveles progresivos de
> desempeño, **organizados jerárquicamente (nivel 3 incluye al 2, y el 2 al 1)**,
> reflejando avances en ciclos de mejora continua.

La CNA **ya define una escala de profundidad anidada de tres niveles**. No hay que inventar
cómo diferenciar la exigencia de un Rector de la de un Docente sobre la misma dimensión:
se usa la escala que el propio modelo de acreditación define.

## Decisión

**La unidad de generación de contenido es el par `(dimensión, nivel_estandar)`.**

- 5 dimensiones × 3 niveles = **15 unidades de contenido**, no 30.
- Como el nivel 3 contiene al 2 y el 2 al 1, la generación es **incremental**: se genera el
  núcleo de nivel 1, luego el incremento de nivel 2, luego el de nivel 3. Un bloque de
  nivel 3 se compone de los tres tramos.
- **La ruta de un cargo es una fila de la matriz Cargo × Dimensión**: cinco pares
  `(dimensión, nivel exigido)` con su orden.

### La matriz del slice

Nivel de estándar exigido a cada cargo por dimensión. Todo cargo toca **las cinco**
dimensiones con nivel ≥ 1 — la acreditación es de todos —, y se diferencia por dónde se
le exige profundidad.

| Cargo | Gestión Estratégica | Docencia | Aseg. Calidad | Vinculación | Investigación |
|---|:--:|:--:|:--:|:--:|:--:|
| **Rector** | **3** | 2 | **3** | 2 | 2 |
| **Vicerrector Académico** | 2 | **3** | **3** | 1 | 1 |
| **Director de Carrera** | 1 | **3** | 2 | **3** | 1 |
| **Docente** | 1 | **3** | 1 | 1 | 1 |
| **Coordinador de Calidad** | **3** | 2 | **3** | 1 | 1 |
| **Administrativo** | 2 | 1 | 2 | 1 | 1 |

Lecturas que confirman que el modelo es correcto:

- El **Rector** es el único con amplitud alta pareja: visión global, profundidad en
  gestión y calidad. Ningún 1.
- El **Docente** tiene un solo 3 y el resto en 1: recorrido corto y hondo en lo suyo.
- **Vicerrector** y **Coordinador de Calidad** comparten el 3 en Aseguramiento pero se
  separan en Docencia contra Gestión: rutas distintas con contenido compartido.
- Ningún par (cargo, dimensión) exige contenido que no exista en las 15 unidades.

### Consecuencias en el resto del sistema

**Medallas.** La medalla se define por `(dimensión, nivel)`, no por cargo. "Docencia · N3"
y "Docencia · N1" son insignias distintas, con distinto XP. Así, dos cargos que estudian la
misma dimensión ganan reconocimientos legítimamente diferentes, y la vitrina de insignias
se ve distinta por cargo sin duplicar nada.

**Ruta.** Son 5 bloques + graduación = 6 nodos en el mapa. Esto además resuelve la
inconsistencia de la cáscara, que dibujaba 7 nodos y decía 8 bloques.

**Módulos por bloque.** Escalan con el nivel, porque el contenido está anidado:
N1 → 2 módulos · N2 → 3 · N3 → 4. Conserva el default de 2 módulos de CLAUDE.md §5 en el
nivel base. Configurable en `modulos_por_nivel`.

**Orden de la ruta.** Los bloques se ordenan por `orden_en_ruta` de la matriz, y cada uno
se ancla a un `Hito` de la ruta oficial: el colaborador ve *por qué ahora* le toca esa
dimensión. El dashboard compara avance contra calendario CNA con eso.

**El swap a producción.** El generador recibe `fuente_de_contenido`: en el slice
`{modo:'prueba', tema:'…'}`; en producción `{modo:'corpus', corpus_id:'…'}` con el material
CNA de AIEP. **La matriz, las medallas, el motor y las rutas no cambian.** Cambia el
relleno de las 15 unidades.

## Alternativas descartadas

**Generar por cargo (30 unidades).** Descartada: contradice la instrucción del director,
multiplica el costo de validación del experto CNA por seis, y hace que corregir un error en
"Docencia" haya que corregirlo en cinco lugares.

**Contenido idéntico por dimensión, diferenciando solo el orden.** Descartada: no demuestra
personalización. Un Rector y un Docente verían exactamente el mismo material de Docencia,
lo que además es pedagógicamente falso.

**Inventar una escala de profundidad propia.** Descartada por innecesaria y por riesgosa:
la CNA ya tiene una y usar la suya mantiene el sistema alineado con el marco real.

## Cómo se revierte

La matriz vive en datos (`ExigenciaCargoDimension`, 30 filas de seed), no en código.
Cambiar la ponderación de un cargo es un `UPDATE` y regenerar su ruta. Agregar un cargo son
5 filas nuevas y **cero contenido nuevo**, siempre que reuse niveles ya generados. Ese es
el punto: cablear el organigrama real de AIEP después es trivial.
