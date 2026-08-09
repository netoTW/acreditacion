"""
CANARIO DE ESQUEMA.

El canario de arriba prueba que la ruta de código no otorga de más. Este prueba
algo más fuerte: que **aunque alguien escriba directo en la base**, la medalla
falsa es imposible.

Existe porque validar en la capa de servicio no alcanza. No protege contra un
seed, una migración, una corrección manual, ni contra un constructor futuro que
agregue una segunda ruta de código. Si alguno de estos tests empieza a pasar
—es decir, si la base deja de rechazar—, alguien aflojó el esquema en una
migración y hay que detenerse (ADR-005).
"""
import psycopg
import pytest

from motor.evaluacion import abrir_intento, cerrar_intento

from conftest import responder_intento


def _intento_cerrado(db, esc, *, aciertos, bloque_ruta_id=None, colaborador_id=None):
    intento_id = abrir_intento(
        db,
        colaborador_id=colaborador_id or esc.colaborador_id,
        bloque_ruta_id=bloque_ruta_id or esc.bloque_ruta_id,
    )
    responder_intento(db, intento_id, aciertos=aciertos)
    cerrar_intento(db, intento_id=intento_id)
    return intento_id


# --------------------------------------------------------------- la insignia
def test_insignia_sin_intento_es_imposible(db, esc):
    """
    El invariante máximo, con dos candados encima.

    En PostgreSQL los triggers BEFORE corren ANTES de evaluar el NOT NULL, así que
    quien ataja el intento es fn_insignia_respaldada(). El NOT NULL sigue siendo la
    garantía declarativa de fondo, y se verifica aparte contra el catálogo: si
    alguien quitara el trigger en una migración, la columna igual rechaza el nulo.
    """
    with pytest.raises(psycopg.errors.DatabaseError) as exc:
        db.execute(
            """INSERT INTO insignia (colaborador_id, definicion_medalla_id, intento_evaluacion_id)
               VALUES (%s, %s, NULL)""",
            (esc.colaborador_id, esc.medalla_id),
        )
    assert "INTEGRIDAD" in str(exc.value)
    assert db.execute("SELECT count(*) FROM insignia").fetchone()[0] == 0

    es_nullable = db.execute(
        """SELECT is_nullable FROM information_schema.columns
            WHERE table_name = 'insignia' AND column_name = 'intento_evaluacion_id'"""
    ).fetchone()[0]
    assert es_nullable == "NO", "insignia.intento_evaluacion_id dejó de ser NOT NULL"


def test_insignia_sobre_intento_reprobado_es_imposible(db, esc):
    intento_id = _intento_cerrado(db, esc, aciertos=0)

    with pytest.raises(psycopg.errors.CheckViolation, match="no aprobado"):
        db.execute(
            """INSERT INTO insignia (colaborador_id, definicion_medalla_id, intento_evaluacion_id)
               VALUES (%s, %s, %s)""",
            (esc.colaborador_id, esc.medalla_id, intento_id),
        )


def test_insignia_con_el_intento_aprobado_de_otra_persona_es_imposible(db, esc):
    """Robarse el respaldo ajeno tiene que ser imposible, no improbable."""
    otra_ruta = db.execute(
        "INSERT INTO ruta (colaborador_id, cargo_id) SELECT %s, cargo_id FROM colaborador WHERE id = %s RETURNING id",
        (esc.otro_colaborador_id, esc.otro_colaborador_id),
    ).fetchone()[0]
    br_otro = db.execute(
        """INSERT INTO bloque_ruta (ruta_id, bloque_contenido_id, orden, estado)
           VALUES (%s,%s,1,'disponible') RETURNING id""",
        (otra_ruta, esc.bloque_contenido_id),
    ).fetchone()[0]

    intento_ajeno = _intento_cerrado(
        db, esc, aciertos=5, bloque_ruta_id=br_otro, colaborador_id=esc.otro_colaborador_id
    )

    with pytest.raises(psycopg.errors.CheckViolation, match="otro colaborador"):
        db.execute(
            """INSERT INTO insignia (colaborador_id, definicion_medalla_id, intento_evaluacion_id)
               VALUES (%s, %s, %s)""",
            (esc.colaborador_id, esc.medalla_id, intento_ajeno),
        )


def test_insignia_respaldada_por_el_bloque_equivocado_es_imposible(db, esc):
    """
    Aprobar "VcM N1" no puede desbloquear la medalla de "Docencia N3".
    Sin este candado, alguien aprueba el bloque más fácil y reclama el más exigente.
    """
    intento_vcm = _intento_cerrado(db, esc, aciertos=5, bloque_ruta_id=esc.otro_bloque_ruta_id)

    with pytest.raises(psycopg.errors.CheckViolation, match="otro bloque de contenido"):
        db.execute(
            """INSERT INTO insignia (colaborador_id, definicion_medalla_id, intento_evaluacion_id)
               VALUES (%s, %s, %s)""",
            (esc.colaborador_id, esc.medalla_id, intento_vcm),
        )


def test_insignia_sobre_intento_abierto_es_imposible(db, esc):
    intento_id = abrir_intento(
        db, colaborador_id=esc.colaborador_id, bloque_ruta_id=esc.bloque_ruta_id
    )
    with pytest.raises(psycopg.errors.CheckViolation):
        db.execute(
            """INSERT INTO insignia (colaborador_id, definicion_medalla_id, intento_evaluacion_id)
               VALUES (%s, %s, %s)""",
            (esc.colaborador_id, esc.medalla_id, intento_id),
        )


def test_la_misma_medalla_no_se_otorga_dos_veces(db, esc):
    intento_id = _intento_cerrado(db, esc, aciertos=5)
    with pytest.raises(psycopg.errors.UniqueViolation):
        db.execute(
            """INSERT INTO insignia (colaborador_id, definicion_medalla_id, intento_evaluacion_id)
               VALUES (%s, %s, %s)""",
            (esc.colaborador_id, esc.medalla_id, intento_id),
        )


def test_la_insignia_no_se_borra(db, esc):
    """Es evidencia ante la CNA: no se reescribe la historia."""
    _intento_cerrado(db, esc, aciertos=5)
    with pytest.raises(psycopg.errors.InsufficientPrivilege, match="append-only"):
        db.execute("DELETE FROM insignia")


# ----------------------------------------------------------------- el intento
def test_marcar_aprobado_con_puntaje_bajo_es_imposible(db, esc):
    """
    Si esto se pudiera, falsificar la medalla sería trivial: basta con mentir en
    el intento y después el trigger de la insignia lo daría por bueno.
    """
    intento_id = abrir_intento(
        db, colaborador_id=esc.colaborador_id, bloque_ruta_id=esc.bloque_ruta_id
    )
    with pytest.raises(psycopg.errors.CheckViolation, match="no corresponde al puntaje"):
        db.execute(
            """UPDATE intento_evaluacion
                  SET estado='enviado', enviado_en=now(), puntaje=0.200, aprobado=true
                WHERE id = %s""",
            (intento_id,),
        )


# ------------------------------------------------------------------- eventos
def test_xp_negativo_es_imposible(db, esc):
    with pytest.raises(psycopg.errors.CheckViolation):
        db.execute(
            """INSERT INTO evento_gamificacion
                   (colaborador_id, tipo, origen_tipo, origen_id, xp, clase_xp, clave_idempotencia)
               VALUES (%s,'castigo','modulo',gen_random_uuid(),-50,'acreditable','x')""",
            (esc.colaborador_id,),
        )


def test_un_juego_no_puede_emitir_xp_acreditable(db, esc):
    """S-04 en el esquema: sin esto se llega a Maestro jugando trivia."""
    with pytest.raises(psycopg.errors.CheckViolation):
        db.execute(
            """INSERT INTO evento_gamificacion
                   (colaborador_id, tipo, origen_tipo, origen_id, xp, clase_xp, clave_idempotencia)
               VALUES (%s,'trivia','juego',gen_random_uuid(),500,'acreditable','y')""",
            (esc.colaborador_id,),
        )


def test_los_eventos_no_se_editan_ni_se_borran(db, esc):
    db.execute(
        """INSERT INTO evento_gamificacion
               (colaborador_id, tipo, origen_tipo, origen_id, xp, clase_xp, clave_idempotencia)
           VALUES (%s,'modulo_completado','modulo',gen_random_uuid(),60,'acreditable','z')""",
        (esc.colaborador_id,),
    )
    with pytest.raises(psycopg.errors.InsufficientPrivilege, match="append-only"):
        db.execute("UPDATE evento_gamificacion SET xp = 99999")
    with pytest.raises(psycopg.errors.InsufficientPrivilege, match="append-only"):
        db.execute("DELETE FROM evento_gamificacion")


def test_no_existe_columna_de_nivel_ni_de_xp(db):
    """§4.3: el escalón es derivable siempre porque no hay dónde desincronizarlo."""
    columnas = [
        c[0]
        for c in db.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'colaborador'"
        ).fetchall()
    ]
    assert "nivel" not in columnas
    assert "xp" not in columnas
    assert "escalon" not in columnas
