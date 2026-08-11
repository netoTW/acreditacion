"""
Generador y Validador.

Dos cosas que probar, y la segunda importa tanto como la primera:
  1. que lo generado pase el validador;
  2. que el validador **rechace** contenido saboteado. Un validador que aprueba
     todo da una garantía imaginaria, igual que un test sin dientes.
"""
import copy

import pytest

from generador import generar, generar_todo, validar
from generador.conocimiento import DIMENSIONES

MODULOS_POR_BLOQUE = 2                      # igual en las 5 dimensiones y los 3 niveles
ITEMS_QUIZ_ESPERADOS = {1: 3, 2: 5, 3: 7}   # la profundidad la fija el nivel
BANCO_ESPERADO = {1: 18, 2: 24, 3: 30}      # 6 / 8 / 10 conceptos × 3 ítems


@pytest.fixture(scope="module")
def bloques():
    return generar_todo()


# ------------------------------------------------------------ lo generado
def test_se_generan_quince_unidades_no_treinta(bloques):
    """El ahorro de ADR-003: 5 dimensiones × 3 niveles sirven los 30 pares cargo×dimensión."""
    assert len(bloques) == 15
    assert len({(b["dimension"], b["nivel_estandar"]) for b in bloques}) == 15


@pytest.mark.parametrize("codigo", list(DIMENSIONES))
@pytest.mark.parametrize("nivel", [1, 2, 3])
def test_cada_bloque_pasa_el_validador(codigo, nivel):
    r = validar(generar(codigo, nivel))
    assert r.valido, f"{codigo} N{nivel} no valida: {r.errores}"


def test_todo_va_marcado_como_contenido_de_prueba(bloques):
    """Nada de esto puede presentarse como material oficial de acreditación."""
    for b in bloques:
        assert b["es_contenido_prueba"] is True
        assert b["fuente_contenido"]["modo"] == "prueba"
        for c in b["criterios"]:
            assert c["es_contenido_prueba"] is True


def test_la_estructura_es_la_misma_en_todas_las_dimensiones(bloques):
    """
    El modelo de AIEP fija una sola forma: 2 quiz + 1 juego + evaluación.

    Antes la cantidad de módulos crecía con el nivel (2/3/4). Ya no: lo que sube
    con el nivel es cuánto trae cada módulo, no cuántos hay.
    """
    for b in bloques:
        assert len(b["modulos"]) == MODULOS_POR_BLOQUE, b["dimension"]


def test_la_profundidad_escala_con_el_nivel(bloques):
    """Donde el rol impacta más, el bloque pesa más: es lo que hace real la distribución."""
    for b in bloques:
        esperado = ITEMS_QUIZ_ESPERADOS[b["nivel_estandar"]]
        for m in b["modulos"]:
            assert len(m["quiz_formativo"]) == esperado, f"{b['dimension']} N{b['nivel_estandar']}"


def test_el_anidamiento_de_estandares_sigue_expresado(bloques):
    """
    El nivel 3 sigue incluyendo al 2 y al 1: con 2 módulos, el anidamiento se ve en
    que el primero cubre los fundamentos y el último llega al nivel del rol.
    """
    for b in bloques:
        origenes = [m["nivel_estandar_origen"] for m in sorted(b["modulos"], key=lambda m: m["orden"])]
        assert origenes[0] == 1, f"{b['dimension']}: el primer módulo no parte en fundamentos"
        assert origenes[-1] == b["nivel_estandar"], f"{b['dimension']}: no llega al nivel del bloque"


def test_el_banco_crece_con_el_nivel(bloques):
    for b in bloques:
        assert len(b["evaluacion"]["banco_items"]) == BANCO_ESPERADO[b["nivel_estandar"]]
        # y siempre por sobre el triple de los ítems por intento (S-06)
        assert len(b["evaluacion"]["banco_items"]) >= 3 * b["evaluacion"]["n_items_por_intento"]


def test_la_correcta_no_se_concentra_en_una_alternativa(bloques):
    for b in bloques:
        banco = b["evaluacion"]["banco_items"]
        conteo = [0, 0, 0, 0]
        for i in banco:
            conteo[i["indice_correcta"]] += 1
        assert max(conteo) / len(banco) <= 0.5, f"{b['dimension']}: {conteo}"


def test_cada_alternativa_tiene_su_propia_explicacion(bloques):
    for b in bloques:
        for i in b["evaluacion"]["banco_items"]:
            assert len(i["explicaciones"]) == 4
            assert len(set(i["explicaciones"])) == 4, "explicación repetida entre alternativas"


def test_el_generador_es_determinista():
    """Misma entrada, misma salida: el contenido tiene que ser revisable y diffeable."""
    assert generar("CALIDAD", 3) == generar("CALIDAD", 3)


def test_el_microlearning_tiene_sustancia(bloques):
    for b in bloques:
        for m in b["modulos"]:
            assert len(m["cuerpo"]) >= 400
            assert "lorem" not in m["cuerpo"].lower()


# ------------------------------------------- el validador tiene que morder
def _bloque_base():
    return copy.deepcopy(generar("CALIDAD", 3))


def test_rechaza_si_falta_un_tramo_del_anidamiento():
    b = _bloque_base()
    for m in b["modulos"]:
        m["nivel_estandar_origen"] = 1          # se pierden los tramos 2 y 3
    r = validar(b)
    assert not r.valido and any("anidamiento" in e for e in r.errores)


def test_rechaza_un_banco_demasiado_chico():
    b = _bloque_base()
    b["evaluacion"]["banco_items"] = b["evaluacion"]["banco_items"][:10]
    r = validar(b)
    assert not r.valido and any("banco" in e for e in r.errores)


def test_rechaza_items_duplicados():
    b = _bloque_base()
    b["evaluacion"]["banco_items"][1] = copy.deepcopy(b["evaluacion"]["banco_items"][0])
    r = validar(b)
    assert not r.valido and any("duplicado" in e or "idénticos" in e for e in r.errores)


def test_rechaza_explicaciones_de_relleno():
    """El sabotaje respeta el schema (largo mínimo): lo que debe atajarlo es la regla 7."""
    b = _bloque_base()
    b["evaluacion"]["banco_items"][0]["explicaciones"] = [
        "lorem ipsum dolor sit amet",
        "TBD, queda por escribir",
        "placeholder de la explicación",
        "falta redactar esta parte",
    ]
    r = validar(b)
    assert not r.valido and any("relleno" in e for e in r.errores)


def test_no_confunde_palabras_normales_con_relleno():
    """
    Regresión: buscar «todo» o «pendiente» como subcadena marcaba como relleno
    explicaciones legítimas por decir «método» o «independiente».
    """
    b = _bloque_base()
    b["evaluacion"]["banco_items"][0]["explicaciones"] = [
        "El método exige revisión independiente antes de recoger datos.",
        "Todo el proceso queda pendiente de la validación del comité.",
        "La metodología descrita no corresponde a este tipo de estudio.",
        "Su independencia respecto del equipo evaluador es la clave.",
    ]
    assert validar(b).valido


def test_rechaza_si_la_correcta_siempre_cae_en_la_misma_casilla():
    """Un banco así se aprueba marcando siempre A, sin saber nada de la materia."""
    b = _bloque_base()
    for i in b["evaluacion"]["banco_items"]:
        correcta = i["alternativas"][i["indice_correcta"]]
        explicacion = i["explicaciones"][i["indice_correcta"]]
        resto = [a for k, a in enumerate(i["alternativas"]) if k != i["indice_correcta"]]
        exps = [e for k, e in enumerate(i["explicaciones"]) if k != i["indice_correcta"]]
        i["alternativas"] = [correcta] + resto
        i["explicaciones"] = [explicacion] + exps
        i["indice_correcta"] = 0
    r = validar(b)
    assert not r.valido and any("cae en la alternativa" in e for e in r.errores)


def test_rechaza_si_la_correcta_se_delata_por_ser_mas_larga():
    """Se acortan las incorrectas —dentro del schema— para producir el sesgo de largo."""
    b = _bloque_base()
    for i in b["evaluacion"]["banco_items"]:
        for k in range(4):
            if k != i["indice_correcta"]:
                i["alternativas"][k] = f"No corresponde ({k})"
    r = validar(b)
    assert not r.valido and any("más larga" in e for e in r.errores)


def test_rechaza_alternativas_repetidas_dentro_de_un_item():
    b = _bloque_base()
    i = b["evaluacion"]["banco_items"][0]
    i["alternativas"][1] = i["alternativas"][0]
    r = validar(b)
    assert not r.valido and any("repetidas" in e for e in r.errores)


def test_rechaza_xp_que_no_corresponde_al_nivel():
    b = _bloque_base()
    b["medallas"][0]["xp"] = 999
    r = validar(b)
    assert not r.valido and any("XP" in e for e in r.errores)


def test_rechaza_contenido_no_marcado_como_prueba():
    b = _bloque_base()
    b["es_contenido_prueba"] = False
    r = validar(b)
    assert not r.valido


def test_rechaza_una_dimension_inventada():
    b = _bloque_base()
    b["dimension"] = "MARKETING"
    r = validar(b)
    assert not r.valido


# ----------------------------------------- contenido de los juegos por dimensión
def test_los_casos_de_cohorte_tienen_una_sola_respuesta_defendible():
    """
    La regla de fondo de D2: el tramo declarado es el que más cae bajo SU
    referencia, y por un margen claro. Un caso donde dos tramos están igual de mal
    castiga a quien entendió.
    """
    from generador.juegos import validar_juegos
    assert validar_juegos() == []


def test_un_caso_con_el_quiebre_mal_declarado_se_rechaza():
    from copy import deepcopy
    from generador.juegos import validar_caso_cohorte
    from generador.juegos.cohortes import CASOS

    malo = deepcopy(CASOS[0])
    malo["tramo_quiebre"] = (malo["tramo_quiebre"] + 1) % len(malo["tramos"])
    errores = validar_caso_cohorte(malo)
    assert any("el que más cae bajo su referencia" in e for e in errores)


def test_un_caso_con_dos_tramos_igual_de_malos_se_rechaza():
    """Si la respuesta es discutible, el juego no se integra."""
    from copy import deepcopy
    from generador.juegos import validar_caso_cohorte
    from generador.juegos.cohortes import CASOS

    malo = deepcopy(CASOS[0])
    # Se hunde otro tramo hasta empatar con el declarado.
    malo["etapas"][4]["valor"] = 40
    malo["etapas"][5]["valor"] = 26
    errores = validar_caso_cohorte(malo)
    assert any("discutible" in e or "el que más cae" in e for e in errores)


def test_una_cohorte_que_crece_se_rechaza():
    from copy import deepcopy
    from generador.juegos import validar_caso_cohorte
    from generador.juegos.cohortes import CASOS

    malo = deepcopy(CASOS[0])
    malo["etapas"][3]["valor"] = malo["etapas"][2]["valor"] + 10
    assert any("crece" in e for e in validar_caso_cohorte(malo))


def test_el_catalogo_de_contrapartes_da_para_armar_mapas():
    from generador.juegos import validar_contrapartes
    assert validar_contrapartes() == []


def test_un_actor_sin_vinculo_sin_razon_se_rechaza():
    """
    Descartar sin explicación enseña a descartar de memoria. La razón es lo que
    convierte «este no va» en un criterio.
    """
    import generador.juegos as juegos
    original = juegos.ACTORES
    juegos.ACTORES = [
        (c, n, t, d, a, "" if a is None else r) for c, n, t, d, a, r in original
    ]
    try:
        errores = juegos.validar_contrapartes()
    finally:
        juegos.ACTORES = original
    assert any("razón no explica" in e for e in errores)


def test_el_catalogo_de_produccion_cubre_los_cuatro_cuadrantes():
    from generador.juegos import validar_produccion
    assert validar_produccion() == []


def test_una_produccion_que_no_es_ici_no_puede_declarar_linea():
    """Colgar material docente de una línea de investigación es el error que se busca."""
    import generador.juegos as juegos
    original = juegos.PRODUCCIONES
    juegos.PRODUCCIONES = [
        (c, t, tp, d, ici, ads, ("educacion" if not ici else ln), ri, ra)
        for c, t, tp, d, ici, ads, ln, ri, ra in original
    ]
    try:
        errores = juegos.validar_produccion()
    finally:
        juegos.PRODUCCIONES = original
    assert any("no es producción ICI y aun así declara una línea" in e for e in errores)


def test_un_cuadrante_vacio_se_rechaza():
    import generador.juegos as juegos
    original = juegos.PRODUCCIONES
    # Se dejan fuera todas las que son ICI y no adscritas.
    juegos.PRODUCCIONES = [p for p in original if not (p[4] and not p[5])]
    try:
        errores = juegos.validar_produccion()
    finally:
        juegos.PRODUCCIONES = original
    assert any("cuadrante (ICI=True, adscrita=False)" in e for e in errores)


def test_los_escenarios_de_gestion_son_ganables_y_no_triviales():
    from generador.juegos import validar_gestion
    assert validar_gestion() == []


def test_un_escenario_que_no_se_puede_ganar_se_rechaza():
    """Un escenario imposible se ve idéntico a uno difícil: hay que simularlo."""
    from copy import deepcopy
    from generador.juegos import validar_escenario_gestion
    from generador.juegos.gestion import ESCENARIOS

    malo = deepcopy(ESCENARIOS[0])
    for f in malo["frentes"]:
        f["umbral"] = 95
    assert any("no gana el escenario" in e for e in validar_escenario_gestion(malo))


def test_un_escenario_que_se_gana_repartiendo_parejo_se_rechaza():
    """Si el reparto uniforme alcanza, no hubo decisión que tomar."""
    from copy import deepcopy
    from generador.juegos import validar_escenario_gestion
    from generador.juegos.gestion import ESCENARIOS

    malo = deepcopy(ESCENARIOS[0])
    malo["presupuesto"] = 20          # sobra para todo
    malo["solucion_ejemplo"] = [{f["clave"]: 5 for f in malo["frentes"]}] * 3
    assert any("parejo gana el escenario" in e for e in validar_escenario_gestion(malo))


def test_un_frente_no_puede_ser_su_propio_habilitador():
    from copy import deepcopy
    from generador.juegos import validar_escenario_gestion
    from generador.juegos.gestion import ESCENARIOS

    malo = deepcopy(ESCENARIOS[0])
    malo["regla"]["habilitador"] = malo["regla"]["frente"]
    assert any("su propio habilitador" in e for e in validar_escenario_gestion(malo))
