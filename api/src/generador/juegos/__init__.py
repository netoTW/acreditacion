"""
Contenido de los juegos por dimensión: validación e integración.

Mismo principio que el resto del Generador (CLAUDE.md §9.3): **lo que no pasa el
validador no entra**. Un juego con contenido mal armado es peor que no tenerlo,
porque enseña algo falso con la autoridad de una pantalla.

La regla que más importa acá no es de formato, es de **resolubilidad**: que el
caso tenga una respuesta defendible y una sola. Un tablero donde dos respuestas
son igual de razonables castiga al que entendió.
"""
from __future__ import annotations

from .cohortes import CASOS as CASOS_COHORTE

# Margen mínimo entre la brecha del tramo que se rompe y la del segundo peor.
# Sin esto se puede colar un caso donde dos tramos están igual de mal y el juego
# exige adivinar cuál eligió quien lo escribió.
MARGEN_MINIMO_PUNTOS = 8.0

INDICADORES_POR_CASO = 4


def _brechas(caso: dict) -> list[float]:
    """Cuántos puntos porcentuales por debajo de su referencia queda cada tramo."""
    valores = [e["valor"] for e in caso["etapas"]]
    brechas = []
    for i, tramo in enumerate(caso["tramos"]):
        conservado = 100.0 * valores[i + 1] / valores[i]
        brechas.append(max(0.0, tramo["referencia_pct"] - conservado))
    return brechas


def validar_caso_cohorte(caso: dict) -> list[str]:
    errores = []
    etiqueta = caso.get("codigo", "?")
    etapas = caso.get("etapas", [])
    tramos = caso.get("tramos", [])

    if len(etapas) < 3:
        errores.append(f"{etiqueta}: un caso necesita al menos 3 etapas")
        return errores
    if len(tramos) != len(etapas) - 1:
        errores.append(f"{etiqueta}: hay {len(tramos)} tramos para {len(etapas)} etapas")
        return errores

    if not caso.get("es_contenido_prueba"):
        errores.append(f"{etiqueta}: todo el contenido de esta etapa va marcado como prueba")

    # Una cohorte no crece: si un tramo sube, el caso está mal construido y el
    # jugador leería un dato imposible.
    valores = [e["valor"] for e in etapas]
    for i in range(len(valores) - 1):
        if valores[i + 1] > valores[i]:
            errores.append(
                f"{etiqueta}: la cohorte crece entre «{etapas[i]['nombre']}» y "
                f"«{etapas[i + 1]['nombre']}», y eso no puede pasar"
            )
    if any(v <= 0 for v in valores):
        errores.append(f"{etiqueta}: hay etapas con cero o menos estudiantes")
        return errores

    # La regla de fondo: el tramo declarado es el peor, y por un margen claro.
    brechas = _brechas(caso)
    quiebre = caso["tramo_quiebre"]
    if not 0 <= quiebre < len(tramos):
        errores.append(f"{etiqueta}: el tramo de quiebre está fuera de rango")
        return errores

    peor = max(range(len(brechas)), key=lambda i: brechas[i])
    if peor != quiebre:
        errores.append(
            f"{etiqueta}: se declara el quiebre en el tramo {quiebre} pero el que más "
            f"cae bajo su referencia es el {peor} "
            f"({brechas[peor]:.1f} contra {brechas[quiebre]:.1f} puntos)"
        )
    else:
        segunda = sorted(brechas, reverse=True)[1] if len(brechas) > 1 else 0.0
        if brechas[quiebre] - segunda < MARGEN_MINIMO_PUNTOS:
            errores.append(
                f"{etiqueta}: el quiebre solo aventaja al segundo tramo por "
                f"{brechas[quiebre] - segunda:.1f} puntos; con menos de "
                f"{MARGEN_MINIMO_PUNTOS} la respuesta es discutible"
            )

    # Los indicadores: cuatro, con claves únicas, y el correcto entre ellos.
    indicadores = caso.get("indicadores", [])
    claves = {i["clave"] for i in indicadores}
    if len(indicadores) != INDICADORES_POR_CASO:
        errores.append(
            f"{etiqueta}: lleva {len(indicadores)} indicadores y el juego reparte "
            f"{INDICADORES_POR_CASO}"
        )
    if len(claves) != len(indicadores):
        errores.append(f"{etiqueta}: hay indicadores con la clave repetida")
    if caso.get("indicador_correcto") not in claves:
        errores.append(f"{etiqueta}: el indicador correcto no está entre los repartidos")

    for campo in ("explicacion_quiebre", "explicacion_indicador", "contexto", "titulo"):
        if len((caso.get(campo) or "").split()) < 4:
            errores.append(f"{etiqueta}: «{campo}» no dice nada")

    return errores


def validar_juegos() -> list[str]:
    """Todo el contenido de juegos, de una. Lo llama el seed antes de integrar."""
    errores = []
    for caso in CASOS_COHORTE:
        errores.extend(validar_caso_cohorte(caso))
    return errores


def integrar_juegos(conn) -> dict:
    """Integra el contenido de los juegos. Idempotente por código."""
    errores = validar_juegos()
    if errores:
        raise RuntimeError(
            "contenido de juegos rechazado por el validador → " + "; ".join(errores)
        )

    import json

    for caso in CASOS_COHORTE:
        conn.execute(
            """INSERT INTO caso_cohorte (codigo, titulo, contexto, etapas, tramos,
                                         tramo_quiebre, explicacion_quiebre, indicadores,
                                         indicador_correcto, explicacion_indicador,
                                         es_contenido_prueba)
               VALUES (%s,%s,%s,%s::jsonb,%s::jsonb,%s,%s,%s::jsonb,%s,%s,%s)
               ON CONFLICT (codigo) DO UPDATE
                 SET titulo = EXCLUDED.titulo, contexto = EXCLUDED.contexto,
                     etapas = EXCLUDED.etapas, tramos = EXCLUDED.tramos,
                     tramo_quiebre = EXCLUDED.tramo_quiebre,
                     explicacion_quiebre = EXCLUDED.explicacion_quiebre,
                     indicadores = EXCLUDED.indicadores,
                     indicador_correcto = EXCLUDED.indicador_correcto,
                     explicacion_indicador = EXCLUDED.explicacion_indicador""",
            (caso["codigo"], caso["titulo"], caso["contexto"],
             json.dumps(caso["etapas"], ensure_ascii=False),
             json.dumps(caso["tramos"], ensure_ascii=False),
             caso["tramo_quiebre"], caso["explicacion_quiebre"],
             json.dumps(caso["indicadores"], ensure_ascii=False),
             caso["indicador_correcto"], caso["explicacion_indicador"],
             caso["es_contenido_prueba"]),
        )

    return {"casos_cohorte": len(CASOS_COHORTE)}
