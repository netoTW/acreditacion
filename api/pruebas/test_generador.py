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

MODULOS_ESPERADOS = {1: 2, 2: 3, 3: 4}
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


def test_los_modulos_escalan_con_el_nivel(bloques):
    for b in bloques:
        assert len(b["modulos"]) == MODULOS_ESPERADOS[b["nivel_estandar"]]


def test_el_anidamiento_de_estandares_esta_completo(bloques):
    """El nivel 3 incluye al 2 y el 2 al 1: los tramos de origen deben estar todos."""
    for b in bloques:
        nivel = b["nivel_estandar"]
        origenes = {m["nivel_estandar_origen"] for m in b["modulos"]}
        assert set(range(1, nivel + 1)) <= origenes, f"{b['dimension']} N{nivel}: {origenes}"


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
    b["medalla"]["xp"] = 999
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
