"""
Validador de contenido generado — implementa `docs/contenido/REGLAS-VALIDADOR.md`.

Es código, no criterio de agente: un agente nunca es juez cuando existe un test
(CLAUDE.md §1). Lo que no pasa por acá **no se integra**.

Las reglas 14 a 16 son las que más importan y las menos obvias. Un banco puede
cumplir el schema entero y aun así ser inservible: si la correcta es siempre la
más larga, o cae siempre en la misma casilla, se aprueba sin saber la materia. La
insignia quedaría técnicamente válida e institucionalmente falsa, que es
exactamente lo que este proyecto existe para impedir.
"""
from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

import jsonschema

def _ubicar_schema() -> Path:
    """
    Busca el schema hacia arriba en vez de contar niveles de directorio.

    En el repo vive en `docs/contenido/` y en la imagen en `/app/docs/contenido/`,
    a distinta profundidad. Contar `parents[n]` funcionaba en un lado y en el otro
    apuntaba a la raíz del sistema de archivos.
    """
    relativa = Path("docs") / "contenido" / "schema-bloque-contenido.json"
    for base in Path(__file__).resolve().parents:
        candidata = base / relativa
        if candidata.exists():
            return candidata
    raise FileNotFoundError(
        f"no se encontró {relativa} subiendo desde {Path(__file__).resolve()}"
    )


SCHEMA = json.loads(_ubicar_schema().read_text(encoding="utf-8"))

DIMENSIONES_VALIDAS = {"GESTION", "DOCENCIA", "CALIDAD", "VCM", "ICI"}
MODULOS_POR_NIVEL = {1: 2, 2: 3, 3: 4}
XP_MODULO = {1: 60, 2: 80, 3: 100}
XP_MEDALLA = {1: 200, 2: 300, 3: 400}

# Detectar relleno en español pide cuidado: buscar "todo" o "pendiente" como
# subcadena da falsos positivos dentro de "método" y de "independiente", que son
# palabras perfectamente normales en este dominio. Por eso van dos listas: las
# subcadenas inequívocas, y los centinelas que solo cuentan si son TODO el texto.
MARCADORES_SUBCADENA = (
    "lorem ipsum", "tbd", "xxx", "placeholder",
    "por completar", "falta redactar", "completar aqui", "completar aquí",
)
CENTINELAS_EXACTOS = {
    "todo", "n/a", "na", "...", "-", "--", "pendiente", "por definir", "sin explicacion",
}
MINIMO_PALABRAS_EXPLICACION = 4
SIMILITUD_MAXIMA = 0.90
SESGO_LARGO_MAXIMO = 1.35        # la correcta no puede ser 35% más larga en promedio
CONCENTRACION_MAXIMA = 0.50      # ninguna casilla concentra más de la mitad


@dataclass
class Resultado:
    bloque: str
    errores: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)

    @property
    def valido(self) -> bool:
        return not self.errores


def normalizar(texto: str) -> str:
    sin_tildes = "".join(
        ch for ch in unicodedata.normalize("NFD", texto.lower())
        if unicodedata.category(ch) != "Mn"
    )
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", sin_tildes)).strip()


def validar(bloque: dict) -> Resultado:
    etiqueta = f"{bloque.get('dimension', '?')} N{bloque.get('nivel_estandar', '?')}"
    r = Resultado(bloque=etiqueta)

    # 1 — schema. Si no valida, no se sigue analizando.
    try:
        jsonschema.validate(bloque, SCHEMA)
    except jsonschema.ValidationError as e:
        ruta = "/".join(str(p) for p in e.absolute_path) or "(raíz)"
        r.errores.append(f"no cumple el schema en {ruta}: {e.message}")
        return r

    nivel = bloque["nivel_estandar"]
    modulos = bloque["modulos"]
    banco = bloque["evaluacion"]["banco_items"]

    # 2 — marca de contenido de prueba
    if bloque["es_contenido_prueba"] is not True:
        r.errores.append("es_contenido_prueba debe ser true en esta etapa")

    # 3 — cantidad de módulos según nivel (S-32)
    if len(modulos) != MODULOS_POR_NIVEL[nivel]:
        r.errores.append(
            f"un bloque de nivel {nivel} lleva {MODULOS_POR_NIVEL[nivel]} módulos, "
            f"trae {len(modulos)}"
        )

    # 4 — el anidamiento de los estándares tiene que estar completo
    origenes = {m["nivel_estandar_origen"] for m in modulos}
    faltantes = set(range(1, nivel + 1)) - origenes
    if faltantes:
        r.errores.append(
            f"el anidamiento está roto: faltan módulos de origen {sorted(faltantes)} "
            f"(el nivel {nivel} debe incluir los tramos 1..{nivel})"
        )

    # 11 — dimensión del catálogo real
    if bloque["dimension"] not in DIMENSIONES_VALIDAS:
        r.errores.append(f"dimensión desconocida: {bloque['dimension']}")

    # 10 — tamaño mínimo del banco (S-06)
    minimo = 3 * bloque["evaluacion"]["n_items_por_intento"]
    if len(banco) < minimo:
        r.errores.append(
            f"el banco tiene {len(banco)} ítems y necesita al menos {minimo}: "
            "con menos, barajar no produce pruebas distintas entre reintentos"
        )

    # 13 — XP coherente con S-37
    if bloque["medalla"]["xp"] != XP_MEDALLA[nivel]:
        r.errores.append(
            f"la medalla de nivel {nivel} debe dar {XP_MEDALLA[nivel]} XP, "
            f"trae {bloque['medalla']['xp']}"
        )
    for m in modulos:
        if m["xp"] != XP_MODULO[nivel]:
            r.errores.append(
                f"el módulo {m['orden']} debe dar {XP_MODULO[nivel]} XP, trae {m['xp']}"
            )

    # 12 — los criterios referenciados existen
    codigos = {c["codigo"] for c in bloque.get("criterios", [])}
    nombres = {c["nombre"] for c in bloque.get("criterios", [])}

    # 5 a 9 — ítems, uno por uno
    todos = list(banco) + [i for m in modulos for i in m["quiz_formativo"]]
    for item in todos:
        r.errores.extend(_revisar_item(item))
        cod = item.get("criterio_codigo")
        if cod and cod not in codigos and cod not in nombres:
            r.avisos.append(f"el ítem cita el criterio '{cod}', que no está declarado")

    # 8 — sin ítems duplicados en el banco
    vistos = {}
    for item in banco:
        clave = normalizar(item["enunciado"])
        if clave in vistos:
            r.errores.append(f"ítem duplicado en el banco: «{item['enunciado'][:60]}…»")
        vistos[clave] = True

    # 14 a 16 — anti-degeneración, solo sobre el banco de la evaluación
    r.errores.extend(_revisar_banco(banco))

    return r


def _revisar_item(item: dict) -> list[str]:
    errores = []
    alts = item["alternativas"]
    exps = item["explicaciones"]
    enunciado = item["enunciado"][:50]

    # 6 — exactamente una correcta (el índice único lo garantiza; se verifica el rango)
    if not 0 <= item["indice_correcta"] < len(alts):
        errores.append(f"«{enunciado}…»: indice_correcta fuera de rango")

    # 9 — sin alternativas repetidas dentro del ítem
    normalizadas = [normalizar(a) for a in alts]
    if len(set(normalizadas)) != len(normalizadas):
        errores.append(f"«{enunciado}…»: tiene alternativas repetidas")

    # 7 — explicaciones reales, distintas y sin marcadores de relleno
    for i, e in enumerate(exps):
        bajo = (e or "").strip().lower()
        if not bajo:
            errores.append(f"«{enunciado}…»: la explicación {i} está vacía")
        elif any(m in bajo for m in MARCADORES_SUBCADENA) or bajo.rstrip(".") in CENTINELAS_EXACTOS:
            errores.append(f"«{enunciado}…»: la explicación {i} parece un marcador de relleno")
        elif len(bajo.split()) < MINIMO_PALABRAS_EXPLICACION:
            errores.append(
                f"«{enunciado}…»: la explicación {i} tiene menos de "
                f"{MINIMO_PALABRAS_EXPLICACION} palabras: no explica nada"
            )
    if len(set(normalizar(e) for e in exps)) < len(exps):
        errores.append(f"«{enunciado}…»: repite la misma explicación en varias alternativas")

    return errores


def _revisar_banco(banco: list[dict]) -> list[str]:
    errores = []

    # 14 — sin ítems casi idénticos.
    # Se compara enunciado + alternativa correcta, no el enunciado solo: dos ítems
    # que comparten plantilla pero preguntan por conceptos distintos son
    # legítimamente distintos, y castigarlos ocultaría los duplicados de verdad.
    firmas = [
        normalizar(i["enunciado"] + " " + i["alternativas"][i["indice_correcta"]])
        for i in banco
    ]
    for a in range(len(firmas)):
        for b in range(a + 1, len(firmas)):
            s = SequenceMatcher(None, firmas[a], firmas[b]).ratio()
            if s > SIMILITUD_MAXIMA:
                errores.append(
                    f"dos ítems del banco son casi idénticos ({s:.2f}): "
                    f"«{banco[a]['enunciado'][:45]}…» y «{banco[b]['enunciado'][:45]}…»"
                )

    if not banco:
        return errores

    # 15 — la correcta no puede delatarse por ser la más larga
    largos_ok, largos_mal = [], []
    for i in banco:
        for k, alt in enumerate(i["alternativas"]):
            (largos_ok if k == i["indice_correcta"] else largos_mal).append(len(alt))
    if largos_mal and largos_ok:
        razon = (sum(largos_ok) / len(largos_ok)) / (sum(largos_mal) / len(largos_mal))
        if razon > SESGO_LARGO_MAXIMO:
            errores.append(
                f"la alternativa correcta es en promedio {razon:.2f}× más larga que las "
                "incorrectas: se puede adivinar sin saber la materia"
            )

    # 16 — la correcta no puede caer siempre en la misma casilla
    conteo = [0, 0, 0, 0]
    for i in banco:
        conteo[i["indice_correcta"]] += 1
    peor = max(conteo) / len(banco)
    if peor > CONCENTRACION_MAXIMA:
        letra = "ABCD"[conteo.index(max(conteo))]
        errores.append(
            f"el {peor:.0%} de las respuestas correctas cae en la alternativa {letra}: "
            "el banco se puede aprobar marcando siempre la misma"
        )

    return errores


def validar_lote(bloques: list[dict]) -> list[Resultado]:
    return [validar(b) for b in bloques]
