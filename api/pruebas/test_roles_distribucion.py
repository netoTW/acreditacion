"""
El modelo de AIEP: 3 roles, distribución % y estructura escalonada.

Dos capas, y las dos importan:

- **La derivación** (Python puro): que el nivel de exigencia y la criticidad salgan
  del % y no de una transcripción. Si alguien edita el Excel y actualiza solo la
  mitad de la tabla, esto lo delata.
- **Los candados** (PostgreSQL): que la gold no se pueda otorgar donde no se ganó,
  que el umbral reforzado sea real y no decorativo, y que la distribución no pueda
  quedar incoherente. Van en la base porque un invariante que solo vive en el
  servicio se pierde en el primer seed apurado (ADR-005).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import psycopg
import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from seed.datos import (  # noqa: E402
    CRITICAS_POR_ROL, DISTRIBUCION, UMBRAL_CRITICO, matriz_de, nivel_de,
)

# Las marcas 🔴 del Excel, transcritas UNA vez acá para poder contrastarlas contra
# lo que produce la derivación. Si las dos coinciden, la derivación es fiel.
CRITICAS_DEL_EXCEL = {
    "N1": {"GESTION", "CALIDAD"},
    "N2": {"DOCENCIA", "CALIDAD"},
    "N3": {"DOCENCIA", "CALIDAD"},
}


# ------------------------------------------------------- la derivación
def test_cada_rol_suma_uno():
    for rol, pesos in DISTRIBUCION.items():
        assert round(sum(pesos.values()), 3) == 1.0, rol


def test_la_criticidad_derivada_coincide_con_las_marcas_del_excel():
    """
    El hallazgo que sostiene todo el modelo: las 🔴 son las 2 dimensiones de mayor
    peso de cada rol. Si dejaran de coincidir, la derivación estaría inventando.
    """
    for rol in DISTRIBUCION:
        derivadas = {d for d, e in matriz_de(rol).items() if e["critica"]}
        assert derivadas == CRITICAS_DEL_EXCEL[rol], rol


def test_cada_rol_tiene_exactamente_dos_criticas():
    for rol in DISTRIBUCION:
        criticas = [e for e in matriz_de(rol).values() if e["critica"]]
        assert len(criticas) == CRITICAS_POR_ROL, rol


def test_toda_critica_va_al_nivel_mas_exigente_y_con_umbral_reforzado():
    for rol in DISTRIBUCION:
        for dim, e in matriz_de(rol).items():
            if e["critica"]:
                assert e["nivel"] == 3, f"{rol}/{dim}"
                assert e["umbral"] == UMBRAL_CRITICO, f"{rol}/{dim}"
            else:
                assert e["umbral"] == 0.80, f"{rol}/{dim}"


def test_ninguna_dimension_desaparece_de_ninguna_ruta():
    """«La acreditación es de todos»: la criticidad suma exigencia, no quita bloques."""
    for rol in DISTRIBUCION:
        matriz = matriz_de(rol)
        assert len(matriz) == 5, rol
        assert all(e["nivel"] >= 1 for e in matriz.values()), rol


def test_el_empate_de_pesos_se_rompe_de_forma_estable():
    """
    N1 tiene Gestión y Aseguramiento las dos en 30%. Si el desempate dependiera del
    orden de un diccionario, la ruta cambiaría de forma entre corridas.
    """
    primera = matriz_de("N1")
    for _ in range(5):
        assert matriz_de("N1") == primera


def test_el_corte_a_nivel_es_el_declarado():
    assert nivel_de(0.35) == 3 and nivel_de(0.25) == 3
    assert nivel_de(0.24) == 2 and nivel_de(0.15) == 2
    assert nivel_de(0.10) == 1 and nivel_de(0.05) == 1


# ------------------------------------------------------- los candados
@pytest.fixture
def rol(db):
    """Un rol con sus 5 dimensiones, listo para escribirle la matriz."""
    cargo_id = db.execute(
        "INSERT INTO cargo (codigo, nombre) VALUES ('N9','Rol de prueba') RETURNING id"
    ).fetchone()[0]
    dims = [
        db.execute(
            "INSERT INTO dimension (codigo, nombre_oficial, orden) VALUES (%s,%s,%s) RETURNING id",
            (c, f"Dimensión {c}", n),
        ).fetchone()[0]
        for n, c in enumerate(("GESTION", "DOCENCIA", "CALIDAD", "VCM", "ICI"), start=1)
    ]
    return cargo_id, dims


def _escribir_matriz(db, cargo_id, dims, pesos, criticas):
    plantilla, valores = [], []
    for i, (dim, pct) in enumerate(zip(dims, pesos), start=1):
        plantilla.append("(%s,%s,%s,%s,%s,%s)")
        valores += [cargo_id, dim, 3 if i in criticas else 1, i, pct, i in criticas]
    db.execute(
        """INSERT INTO exigencia_cargo_dimension
               (cargo_id, dimension_id, nivel_estandar, orden_en_ruta,
                distribucion_pct, es_critica)
           VALUES """ + ",".join(plantilla),
        valores,
    )


def test_una_distribucion_que_no_suma_uno_se_rechaza(db, rol):
    cargo_id, dims = rol
    with pytest.raises(psycopg.errors.CheckViolation, match="tiene que sumar 1"):
        _escribir_matriz(db, cargo_id, dims, [0.3, 0.2, 0.2, 0.1, 0.1], {1, 3})


def test_un_rol_con_tres_criticas_se_rechaza(db, rol):
    cargo_id, dims = rol
    with pytest.raises(psycopg.errors.CheckViolation, match="críticas"):
        _escribir_matriz(db, cargo_id, dims, [0.3, 0.2, 0.2, 0.2, 0.1], {1, 2, 3})


def test_un_rol_al_que_le_falta_una_dimension_se_rechaza(db, rol):
    """Dejar fuera una dimensión sería volverla opcional por la puerta de atrás."""
    cargo_id, dims = rol
    with pytest.raises(psycopg.errors.CheckViolation, match="dimensiones"):
        _escribir_matriz(db, cargo_id, dims[:4], [0.4, 0.2, 0.2, 0.2], {1, 2})


def test_la_matriz_valida_entra(db, rol):
    cargo_id, dims = rol
    _escribir_matriz(db, cargo_id, dims, [0.3, 0.15, 0.3, 0.15, 0.1], {1, 3})
    assert db.execute(
        "SELECT count(*) FROM exigencia_cargo_dimension WHERE cargo_id = %s", (cargo_id,)
    ).fetchone()[0] == 5


# ------------------------------------ el bloque crítico y su medalla
@pytest.fixture
def bloque(db):
    """
    Un colaborador con DOS bloques del mismo contenido-molde: uno crítico y uno no.

    Es el escenario que hace falta para probar lo que el modelo nuevo promete: que
    el rango de medalla y el umbral dependen de la RUTA, no del contenido.
    """
    cargo_id = db.execute(
        "INSERT INTO cargo (codigo, nombre) VALUES ('N9','Rol de prueba') RETURNING id"
    ).fetchone()[0]
    colaborador_id = db.execute(
        "INSERT INTO colaborador (email, nombre, cargo_id) VALUES (%s,%s,%s) RETURNING id",
        ("prueba@aiep.cl", "Persona de prueba", cargo_id),
    ).fetchone()[0]

    def contenido(codigo, orden):
        dim = db.execute(
            "INSERT INTO dimension (codigo, nombre_oficial, orden) VALUES (%s,%s,%s) RETURNING id",
            (codigo, f"Dimensión {codigo}", orden),
        ).fetchone()[0]
        bc = db.execute(
            """INSERT INTO bloque_contenido (dimension_id, nivel_estandar, titulo, estado)
               VALUES (%s,3,%s,'validado') RETURNING id""",
            (dim, f"Bloque {codigo}"),
        ).fetchone()[0]
        ev = db.execute(
            """INSERT INTO evaluacion (bloque_contenido_id, umbral_aprobacion, n_items_por_intento)
               VALUES (%s, 0.80, 5) RETURNING id""",
            (bc,),
        ).fetchone()[0]
        medallas = {
            tipo: db.execute(
                """INSERT INTO definicion_medalla (bloque_contenido_id, tipo, nombre, xp)
                   VALUES (%s,%s,%s,%s) RETURNING id""",
                (bc, tipo, f"{codigo} {tipo}", 400 if tipo == "silver" else 600),
            ).fetchone()[0]
            for tipo in ("silver", "gold")
        }
        return bc, ev, medallas

    bc_crit, ev_crit, med_crit = contenido("CALIDAD", 1)
    bc_std, ev_std, med_std = contenido("ICI", 2)

    ruta_id = db.execute(
        "INSERT INTO ruta (colaborador_id, cargo_id) VALUES (%s,%s) RETURNING id",
        (colaborador_id, cargo_id),
    ).fetchone()[0]
    br_crit = db.execute(
        """INSERT INTO bloque_ruta (ruta_id, bloque_contenido_id, orden, estado,
                                    es_critica, peso_ranking, umbral_aprobacion)
           VALUES (%s,%s,1,'disponible',true,0.35,0.85) RETURNING id""",
        (ruta_id, bc_crit),
    ).fetchone()[0]
    br_std = db.execute(
        """INSERT INTO bloque_ruta (ruta_id, bloque_contenido_id, orden, estado,
                                    es_critica, peso_ranking)
           VALUES (%s,%s,2,'bloqueado',false,0.05) RETURNING id""",
        (ruta_id, bc_std),
    ).fetchone()[0]

    return {
        "colaborador": colaborador_id,
        "critico": {"br": br_crit, "ev": ev_crit, "medallas": med_crit},
        "estandar": {"br": br_std, "ev": ev_std, "medallas": med_std},
    }


def _intento(db, b, cual, puntaje, aprobado):
    return db.execute(
        """INSERT INTO intento_evaluacion
               (colaborador_id, bloque_ruta_id, evaluacion_id, numero_intento,
                estado, expira_en, enviado_en, puntaje, aprobado)
           VALUES (%s,%s,%s,1,'enviado', now() + interval '1 day', now(), %s, %s)
           RETURNING id""",
        (b["colaborador"], b[cual]["br"], b[cual]["ev"], puntaje, aprobado),
    ).fetchone()[0]


def test_una_critica_declarada_sin_umbral_reforzado_se_rechaza(db, bloque):
    """Una crítica con umbral estándar sería una crítica de nombre."""
    with pytest.raises(psycopg.errors.CheckViolation):
        db.execute(
            """UPDATE bloque_ruta SET umbral_aprobacion = NULL WHERE id = %s""",
            (bloque["critico"]["br"],),
        )


def test_en_la_critica_el_ochenta_por_ciento_no_aprueba(db, bloque):
    """
    El refuerzo del umbral es real y lo verifica la base.

    Si el trigger siguiera leyendo el umbral del contenido, un 80% en la dimensión
    crítica pasaría como aprobado y la gold nacería sin la exigencia que la define.
    """
    with pytest.raises(psycopg.errors.CheckViolation, match="veredicto no corresponde"):
        _intento(db, bloque, "critico", 0.80, True)

    # el mismo 80% en una dimensión estándar sí aprueba
    assert _intento(db, bloque, "estandar", 0.80, True) is not None
    # y en la crítica hay que llegar al 85
    assert _intento(db, bloque, "critico", 0.90, True) is not None


def test_la_gold_no_se_otorga_en_una_dimension_que_no_es_critica(db, bloque):
    """La gold se gana; no la reparte el rol ni una llamada distraída del servicio."""
    intento = _intento(db, bloque, "estandar", 0.90, True)
    with pytest.raises(psycopg.errors.CheckViolation, match="no es crítica"):
        db.execute(
            """INSERT INTO insignia (colaborador_id, definicion_medalla_id, intento_evaluacion_id)
               VALUES (%s,%s,%s)""",
            (bloque["colaborador"], bloque["estandar"]["medallas"]["gold"], intento),
        )


def test_la_critica_no_entrega_una_medalla_de_rango_menor(db, bloque):
    intento = _intento(db, bloque, "critico", 0.90, True)
    with pytest.raises(psycopg.errors.CheckViolation, match="otorga gold"):
        db.execute(
            """INSERT INTO insignia (colaborador_id, definicion_medalla_id, intento_evaluacion_id)
               VALUES (%s,%s,%s)""",
            (bloque["colaborador"], bloque["critico"]["medallas"]["silver"], intento),
        )


def test_la_gold_legitima_si_entra(db, bloque):
    intento = _intento(db, bloque, "critico", 0.90, True)
    insignia = db.execute(
        """INSERT INTO insignia (colaborador_id, definicion_medalla_id, intento_evaluacion_id)
           VALUES (%s,%s,%s) RETURNING id""",
        (bloque["colaborador"], bloque["critico"]["medallas"]["gold"], intento),
    ).fetchone()[0]
    assert insignia is not None


def test_nadie_cobra_dos_veces_el_mismo_bloque(db, bloque):
    """
    Con dos definiciones por bloque aparece un riesgo que antes no existía: cobrar
    la silver y la gold por un mismo recorrido. Una persona, un bloque, una insignia.

    Por la silver el intento ni siquiera llega: el candado de rango la corta antes
    (lo cubre `test_la_critica_no_entrega_una_medalla_de_rango_menor`). Lo que se
    verifica acá es el otro camino, el de repetir la misma medalla.
    """
    intento = _intento(db, bloque, "critico", 0.90, True)
    db.execute(
        """INSERT INTO insignia (colaborador_id, definicion_medalla_id, intento_evaluacion_id)
           VALUES (%s,%s,%s)""",
        (bloque["colaborador"], bloque["critico"]["medallas"]["gold"], intento),
    )
    with pytest.raises(psycopg.errors.UniqueViolation):
        db.execute(
            """INSERT INTO insignia (colaborador_id, definicion_medalla_id, intento_evaluacion_id)
               VALUES (%s,%s,%s)""",
            (bloque["colaborador"], bloque["critico"]["medallas"]["gold"], intento),
        )


# ------------------------------------------------ el desafío aplicado
def _desafio(db, bloque_contenido_id):
    d = db.execute(
        """INSERT INTO desafio_aplicado (bloque_contenido_id, titulo, rol_ficticio, situacion)
           VALUES (%s,'Caso','Integras el comité','Hay que decidir') RETURNING id""",
        (bloque_contenido_id,),
    ).fetchone()[0]
    db.execute(
        """INSERT INTO decision_desafio (desafio_id, orden, tipo, enunciado, opciones,
                                         clave_correcta, explicacion)
           VALUES (%s,1,'eleccion_unica','¿Qué haces?',%s::jsonb,%s::jsonb,'porque sí, con razones')""",
        (d, json.dumps([{"clave": "a", "texto": "una"}, {"clave": "b", "texto": "otra"}]),
         json.dumps("a")),
    )
    return d


def test_el_desafio_no_se_resuelve_sobre_una_dimension_estandar(db, bloque):
    """
    El desafío es la exigencia extra de la crítica. Si se pudiera registrar en
    cualquier bloque, sería un evento de XP lúdico gratis en toda la ruta.
    """
    bc = db.execute(
        "SELECT bloque_contenido_id FROM bloque_ruta WHERE id = %s",
        (bloque["estandar"]["br"],),
    ).fetchone()[0]
    desafio_id = _desafio(db, bc)

    with pytest.raises(psycopg.errors.CheckViolation, match="bloque crítico de la ruta propia"):
        db.execute(
            """INSERT INTO resolucion_desafio (colaborador_id, bloque_ruta_id, desafio_id,
                                               respuestas, aciertos, total)
               VALUES (%s,%s,%s,'[]'::jsonb,1,1)""",
            (bloque["colaborador"], bloque["estandar"]["br"], desafio_id),
        )


def test_el_desafio_de_la_critica_si_se_registra(db, bloque):
    bc = db.execute(
        "SELECT bloque_contenido_id FROM bloque_ruta WHERE id = %s",
        (bloque["critico"]["br"],),
    ).fetchone()[0]
    desafio_id = _desafio(db, bc)
    fila = db.execute(
        """INSERT INTO resolucion_desafio (colaborador_id, bloque_ruta_id, desafio_id,
                                           respuestas, aciertos, total)
           VALUES (%s,%s,%s,'[]'::jsonb,1,1) RETURNING id""",
        (bloque["colaborador"], bloque["critico"]["br"], desafio_id),
    ).fetchone()
    assert fila is not None


def test_el_desafio_no_puede_pagar_xp_acreditable(db, bloque):
    """
    El candado de fondo: resolver el caso NO acerca a nadie a una medalla.

    Va por `origen_tipo='juego'`, que el CHECK de la migración 001 obliga a ser
    lúdico. Aunque alguien escribiera el evento a mano, la base lo rechaza.
    """
    bc = db.execute(
        "SELECT bloque_contenido_id FROM bloque_ruta WHERE id = %s",
        (bloque["critico"]["br"],),
    ).fetchone()[0]
    desafio_id = _desafio(db, bc)

    with pytest.raises(psycopg.errors.CheckViolation):
        db.execute(
            """INSERT INTO evento_gamificacion
                   (colaborador_id, tipo, origen_tipo, origen_id, xp, clase_xp,
                    clave_idempotencia)
               VALUES (%s,'desafio_aplicado_resuelto','juego',%s,300,'acreditable','x')""",
            (bloque["colaborador"], desafio_id),
        )
