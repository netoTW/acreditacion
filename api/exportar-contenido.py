#!/usr/bin/env python3
"""
Exporta el contenido generado a JSON, para revisarlo a ojo.

    python3 api/exportar-contenido.py
    python3 api/exportar-contenido.py DOCENCIA:3 GESTION:1 VCM:2 CALIDAD:3
    python3 api/exportar-contenido.py --todo            # las 15 unidades
    python3 api/exportar-contenido.py --salida /tmp/x.json

Sin argumentos exporta DOCENCIA:3, GESTION:1 y VCM:2 a `contenido-muestra.json`
en la raíz del repo.

No necesita la base ni el stack levantado: el Generador es determinista y produce
exactamente lo que la API sirve. Para comprobarlo con el stack arriba:

    curl -s localhost:8010/bloques-ruta/<id>/modulos | python3 -m json.tool

El formato de salida NO es el del schema: las alternativas vienen emparejadas con
su explicación y con la marca de cuál es la correcta, que es como se revisa. El
formato canónico, el que valida contra `docs/contenido/schema-bloque-contenido.json`,
es el que produce `generador.generar()`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "src"))

from generador import generar, validar                    # noqa: E402
from generador.conocimiento import DIMENSIONES            # noqa: E402

POR_DEFECTO = [("DOCENCIA", 3), ("GESTION", 1), ("VCM", 2)]
LETRAS = "ABCD"


def item_legible(item: dict) -> dict:
    correcta = item["indice_correcta"]
    return {
        "enunciado": item["enunciado"],
        "respuesta_correcta": LETRAS[correcta],
        "alternativas": [
            {
                "letra": LETRAS[k],
                "texto": texto,
                "correcta": k == correcta,
                "explicacion": item["explicaciones"][k],
            }
            for k, texto in enumerate(item["alternativas"])
        ],
        "dificultad": item.get("dificultad"),
        "criterio": item.get("criterio_codigo"),
    }


def unidad_legible(codigo: str, nivel: int) -> dict:
    bloque = generar(codigo, nivel)
    resultado = validar(bloque)
    ev = bloque["evaluacion"]

    return {
        "dimension": bloque["dimension"],
        "dimension_nombre": DIMENSIONES[codigo].nombre_oficial,
        "nivel_estandar": nivel,
        "titulo": bloque["titulo"],
        "resumen": bloque["resumen"],
        "es_contenido_prueba": bloque["es_contenido_prueba"],
        "aviso": (
            "Contenido de prueba para validar la plataforma. NO es material oficial "
            "de acreditación. La estructura sale de la ruta institucional de AIEP; el "
            "desarrollo didáctico lo reemplaza el experto CNA en producción."
        ),
        "validacion": {
            "valido": resultado.valido,
            "errores": resultado.errores,
            "avisos": resultado.avisos,
        },
        "medalla": bloque["medalla"],
        "criterios": bloque["criterios"],
        "modulos": [
            {
                "orden": m["orden"],
                "titulo": m["titulo"],
                "nivel_estandar_origen": m["nivel_estandar_origen"],
                "duracion_min": m["duracion_min"],
                "xp": m["xp"],
                "microlearning": m["cuerpo"],
                "quiz_formativo": [item_legible(i) for i in m["quiz_formativo"]],
            }
            for m in bloque["modulos"]
        ],
        "evaluacion_final": {
            "umbral_aprobacion": ev["umbral_aprobacion"],
            "n_items_por_intento": ev["n_items_por_intento"],
            "max_reintentos": ev["max_reintentos"],
            "banco_items": [item_legible(i) for i in ev["banco_items"]],
        },
    }


def main(argv: list[str]) -> int:
    salida = RAIZ.parent / "contenido-muestra.json"
    pares = []

    args = list(argv)
    if "--salida" in args:
        i = args.index("--salida")
        salida = Path(args[i + 1]).expanduser().resolve()
        del args[i:i + 2]

    if "--todo" in args:
        pares = [(c, n) for c in DIMENSIONES for n in (1, 2, 3)]
        args.remove("--todo")
    else:
        for a in args:
            if ":" not in a:
                print(f"  argumento no reconocido: {a}\n  formato: DIMENSION:NIVEL", file=sys.stderr)
                return 2
            codigo, nivel = a.split(":", 1)
            codigo = codigo.upper()
            if codigo not in DIMENSIONES:
                print(f"  dimensión desconocida: {codigo}\n"
                      f"  válidas: {', '.join(DIMENSIONES)}", file=sys.stderr)
                return 2
            if nivel not in ("1", "2", "3"):
                print(f"  nivel inválido: {nivel} (debe ser 1, 2 o 3)", file=sys.stderr)
                return 2
            pares.append((codigo, int(nivel)))

    if not pares:
        pares = POR_DEFECTO

    unidades = [unidad_legible(c, n) for c, n in pares]
    invalidas = [u for u in unidades if not u["validacion"]["valido"]]

    documento = {
        "_lee_esto": (
            "Contenido de prueba. NO es material oficial de acreditación. Cada ítem trae "
            "sus alternativas con la marca de cuál es correcta y la explicación de cada una."
        ),
        "generado_por": "Generador de Contenido v1.0.0 · Somos Calidad",
        "unidades_exportadas": len(unidades),
        "unidades": unidades,
    }

    salida.write_text(
        json.dumps(documento, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"\n  escrito: {salida}")
    print(f"  {len(unidades)} unidad(es) · {salida.stat().st_size // 1024} kb\n")
    for u in unidades:
        n_items = len(u["evaluacion_final"]["banco_items"])
        n_quiz = sum(len(m["quiz_formativo"]) for m in u["modulos"])
        marca = "ok" if u["validacion"]["valido"] else "INVÁLIDA"
        print(f"    {marca:8} {u['dimension']:9} N{u['nivel_estandar']}  "
              f"{len(u['modulos'])} módulos · {n_items} ítems de banco · {n_quiz} de quiz")
    print()

    return 1 if invalidas else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
