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
from .contrapartes import ACCIONES, ACTORES
from .produccion import LINEAS, PRODUCCIONES

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


# D4 reparte 4 actores con contraparte —cada uno con una acción distinta— y 2 sin
# vínculo, más 2 acciones señuelo. El catálogo tiene que dar para eso con holgura,
# o el tablero se repetiría partida tras partida.
MINIMO_ACCIONES = 6
MINIMO_CONTRAPARTES = 8
MINIMO_SIN_VINCULO = 4


def validar_contrapartes() -> list[str]:
    """
    Que el catálogo dé para armar mapas distintos y que cada actor tenga postura.

    La regla que importa: **un actor sin vínculo también necesita razón**. Si el
    contenido no explica por qué un proveedor no es contraparte, el juego enseña a
    descartarlo de memoria en vez de por el criterio, que es justo lo que se busca.
    """
    errores = []
    claves = {a[0] for a in ACCIONES}

    if len(claves) != len(ACCIONES):
        errores.append("hay acciones institucionales con la clave repetida")
    if len(ACCIONES) < MINIMO_ACCIONES:
        errores.append(
            f"el catálogo tiene {len(ACCIONES)} acciones y el mapa reparte "
            f"{MINIMO_ACCIONES}"
        )

    codigos = set()
    contrapartes, sin_vinculo = 0, 0
    acciones_cubiertas = set()

    for codigo, nombre, tipo, descripcion, accion, razon in ACTORES:
        if codigo in codigos:
            errores.append(f"{codigo}: el código está repetido")
        codigos.add(codigo)

        if accion is None:
            sin_vinculo += 1
        else:
            contrapartes += 1
            acciones_cubiertas.add(accion)
            if accion not in claves:
                errores.append(f"{codigo}: cita la acción «{accion}», que no existe")

        if len((razon or "").split()) < 6:
            errores.append(
                f"{codigo}: la razón no explica por qué el vínculo se sostiene o no"
            )
        if len((descripcion or "").split()) < 5:
            errores.append(f"{codigo}: la descripción no dice qué hace el actor")

    if contrapartes < MINIMO_CONTRAPARTES:
        errores.append(
            f"solo hay {contrapartes} actores con contraparte y el mapa necesita "
            f"al menos {MINIMO_CONTRAPARTES} para variar entre partidas"
        )
    if sin_vinculo < MINIMO_SIN_VINCULO:
        errores.append(
            f"solo hay {sin_vinculo} actores sin vínculo; el descarte es la mitad "
            f"del juego y necesita al menos {MINIMO_SIN_VINCULO}"
        )
    # El mapa toma un actor por acción: sin acciones distintas suficientes no se
    # puede armar un tablero de cuatro vínculos sin ambigüedad.
    if len(acciones_cubiertas) < 4:
        errores.append(
            f"los actores con contraparte cubren solo {len(acciones_cubiertas)} "
            "acciones distintas y el mapa tiende cuatro vínculos"
        )

    return errores


# El tablero de D5 toma una pieza de cada cuadrante antes de completar al azar,
# así que cada cuadrante necesita stock propio o las partidas se repetirían.
MINIMO_POR_CUADRANTE = 3


def validar_produccion() -> list[str]:
    """
    Que los cuatro cuadrantes existan y que cada pieza justifique SUS DOS ejes.

    La regla de fondo: una razón sola no sirve. Si el contenido explica por qué
    algo es investigación pero no por qué es —o no es— de la institución, el juego
    puede premiar una respuesta correcta por un motivo equivocado.
    """
    errores = []
    claves = {l[0] for l in LINEAS}
    if len(claves) != len(LINEAS):
        errores.append("hay líneas de investigación con la clave repetida")
    if not LINEAS:
        errores.append("sin líneas declaradas el tablero pierde su referencia")

    codigos = set()
    cuadrantes = {}

    for (codigo, titulo, tipo, detalle, es_ici, es_adscrita, linea,
         razon_ici, razon_adscripcion) in PRODUCCIONES:
        if codigo in codigos:
            errores.append(f"{codigo}: el código está repetido")
        codigos.add(codigo)

        cuadrantes[(es_ici, es_adscrita)] = cuadrantes.get((es_ici, es_adscrita), 0) + 1

        # Lo que no es producción ICI no puede colgar de una línea de investigación.
        if linea is not None and not es_ici:
            errores.append(f"{codigo}: no es producción ICI y aun así declara una línea")
        if linea is not None and linea not in claves:
            errores.append(f"{codigo}: cita la línea «{linea}», que no está declarada")

        if len((detalle or "").split()) < 10:
            errores.append(
                f"{codigo}: el detalle es la única pista del tablero y no alcanza para decidir"
            )
        for campo, texto in (("razon_ici", razon_ici),
                             ("razon_adscripcion", razon_adscripcion)):
            if len((texto or "").split()) < 6:
                errores.append(f"{codigo}: «{campo}» no justifica su eje")

    for es_ici in (True, False):
        for es_adscrita in (True, False):
            cuantas = cuadrantes.get((es_ici, es_adscrita), 0)
            if cuantas < MINIMO_POR_CUADRANTE:
                errores.append(
                    f"el cuadrante (ICI={es_ici}, adscrita={es_adscrita}) tiene "
                    f"{cuantas} piezas y necesita al menos {MINIMO_POR_CUADRANTE}"
                )

    return errores


def validar_juegos() -> list[str]:
    """Todo el contenido de juegos, de una. Lo llama el seed antes de integrar."""
    errores = []
    for caso in CASOS_COHORTE:
        errores.extend(validar_caso_cohorte(caso))
    errores.extend(validar_contrapartes())
    errores.extend(validar_produccion())
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

    for clave, nombre, descripcion in ACCIONES:
        conn.execute(
            """INSERT INTO accion_institucional (clave, nombre, descripcion)
               VALUES (%s,%s,%s)
               ON CONFLICT (clave) DO UPDATE
                 SET nombre = EXCLUDED.nombre, descripcion = EXCLUDED.descripcion""",
            (clave, nombre, descripcion),
        )

    for codigo, nombre, tipo, descripcion, accion, razon in ACTORES:
        conn.execute(
            """INSERT INTO actor_externo (codigo, nombre, tipo, descripcion,
                                          accion_clave, razon)
               VALUES (%s,%s,%s,%s,%s,%s)
               ON CONFLICT (codigo) DO UPDATE
                 SET nombre = EXCLUDED.nombre, tipo = EXCLUDED.tipo,
                     descripcion = EXCLUDED.descripcion,
                     accion_clave = EXCLUDED.accion_clave, razon = EXCLUDED.razon""",
            (codigo, nombre, tipo, descripcion, accion, razon),
        )

    for clave, nombre, descripcion in LINEAS:
        conn.execute(
            """INSERT INTO linea_ici (clave, nombre, descripcion) VALUES (%s,%s,%s)
               ON CONFLICT (clave) DO UPDATE
                 SET nombre = EXCLUDED.nombre, descripcion = EXCLUDED.descripcion""",
            (clave, nombre, descripcion),
        )

    for (codigo, titulo, tipo, detalle, es_ici, es_adscrita, linea,
         razon_ici, razon_adscripcion) in PRODUCCIONES:
        conn.execute(
            """INSERT INTO produccion_ici (codigo, titulo, tipo, detalle, es_ici,
                                           es_adscrita, linea_clave, razon_ici,
                                           razon_adscripcion)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
               ON CONFLICT (codigo) DO UPDATE
                 SET titulo = EXCLUDED.titulo, tipo = EXCLUDED.tipo,
                     detalle = EXCLUDED.detalle, es_ici = EXCLUDED.es_ici,
                     es_adscrita = EXCLUDED.es_adscrita,
                     linea_clave = EXCLUDED.linea_clave,
                     razon_ici = EXCLUDED.razon_ici,
                     razon_adscripcion = EXCLUDED.razon_adscripcion""",
            (codigo, titulo, tipo, detalle, es_ici, es_adscrita, linea,
             razon_ici, razon_adscripcion),
        )

    return {
        "casos_cohorte": len(CASOS_COHORTE),
        "acciones": len(ACCIONES),
        "actores": len(ACTORES),
        "lineas": len(LINEAS),
        "producciones": len(PRODUCCIONES),
    }
