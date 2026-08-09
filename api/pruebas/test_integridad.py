"""
Regresión de integridad — el set congelado de docs/contenido/REGLAS-VALIDADOR.md.

Cubre I-1 a I-9. I-10 (aislamiento de contenido entre cargos) es de capa API y se
verifica en la Tanda 4; está declarado abajo como pendiente explícito para que no
se dé por cubierto.
"""
import psycopg
import pytest

from motor.evaluacion import abrir_intento, cerrar_intento
from motor.eventos import TOPE_DIARIO_XP_LUDICO, estado, registrar_evento

from conftest import responder_intento


# ------------------------------------------------------- I-3 · XP sin origen
def test_i3_no_hay_xp_sin_origen_verificable(db, esc):
    with pytest.raises(psycopg.errors.NotNullViolation):
        db.execute(
            """INSERT INTO evento_gamificacion
                   (colaborador_id, tipo, origen_tipo, origen_id, xp, clase_xp, clave_idempotencia)
               VALUES (%s,'regalo','modulo',NULL,100,'acreditable','sin-origen')""",
            (esc.colaborador_id,),
        )


# --------------------------------------------- I-6 · doble envío idempotente
def test_i6_el_doble_envio_no_duplica_xp_ni_insignia(db, esc):
    intento_id = abrir_intento(
        db, colaborador_id=esc.colaborador_id, bloque_ruta_id=esc.bloque_ruta_id
    )
    responder_intento(db, intento_id, aciertos=5)

    primero = cerrar_intento(db, intento_id=intento_id)
    segundo = cerrar_intento(db, intento_id=intento_id)   # el usuario apretó dos veces

    assert segundo.aprobado == primero.aprobado
    assert segundo.puntaje == primero.puntaje
    assert segundo.insignia_id == primero.insignia_id

    assert db.execute("SELECT count(*) FROM insignia").fetchone()[0] == 1
    assert db.execute(
        "SELECT count(*) FROM evento_gamificacion WHERE clase_xp='acreditable'"
    ).fetchone()[0] == 1
    assert estado(db, esc.colaborador_id).xp_acreditable == 400


def test_i6_la_clave_de_idempotencia_bloquea_el_evento_repetido(db, esc):
    args = dict(
        colaborador_id=esc.colaborador_id,
        tipo="modulo_completado",
        origen_tipo="modulo",
        origen_id=esc.bloque_contenido_id,
        xp=60,
        clase_xp="acreditable",
        clave_idempotencia="modulo:1:completado",
    )
    assert registrar_evento(db, **args) is not None
    assert registrar_evento(db, **args) is None, "el segundo evento no debe crearse"
    assert estado(db, esc.colaborador_id).xp_acreditable == 60


# ------------------------------------------------- I-8 · intento que expira
def test_i8_el_intento_expirado_no_otorga_y_consume_reintento(db, esc):
    intento_id = abrir_intento(
        db, colaborador_id=esc.colaborador_id, bloque_ruta_id=esc.bloque_ruta_id
    )
    responder_intento(db, intento_id, aciertos=5)     # iba aprobando

    db.execute(
        "UPDATE intento_evaluacion SET expira_en = now() - interval '1 minute' WHERE id = %s",
        (intento_id,),
    )

    nuevo = abrir_intento(
        db, colaborador_id=esc.colaborador_id, bloque_ruta_id=esc.bloque_ruta_id
    )
    assert nuevo != intento_id

    viejo = db.execute(
        "SELECT estado, aprobado FROM intento_evaluacion WHERE id = %s", (intento_id,)
    ).fetchone()
    assert viejo == ("expirado", False)

    assert estado(db, esc.colaborador_id).insignias == 0, (
        "un intento expirado no otorga, aunque las respuestas fueran correctas"
    )
    assert db.execute(
        "SELECT numero_intento FROM intento_evaluacion WHERE id = %s", (nuevo,)
    ).fetchone()[0] == 2, "el intento expirado consume reintento"


# ------------------------------------- I-9 · el XP lúdico no mueve el escalón
def test_i9_jugar_no_sube_de_escalon(db, esc):
    for n in range(40):                                   # intento de 20.000 XP
        registrar_evento(
            db,
            colaborador_id=esc.colaborador_id,
            tipo="trivia_jugada",
            origen_tipo="juego",
            origen_id=esc.bloque_contenido_id,
            xp=500,
            clase_xp="ludico",
            clave_idempotencia=f"trivia:{n}",
        )

    e = estado(db, esc.colaborador_id)
    assert e.xp_acreditable == 0
    assert e.escalon == "Explorador", (
        "jugar no puede llevar a Maestro de Acreditación sin aprobar nada (S-04)"
    )
    assert e.xp_total == TOPE_DIARIO_XP_LUDICO, "el tope diario de XP lúdico debe aplicarse (S-05)"


def test_i9_el_ranking_usa_el_total_y_el_escalon_el_acreditable(db, esc):
    intento_id = abrir_intento(
        db, colaborador_id=esc.colaborador_id, bloque_ruta_id=esc.bloque_ruta_id
    )
    responder_intento(db, intento_id, aciertos=5)
    cerrar_intento(db, intento_id=intento_id)

    registrar_evento(
        db,
        colaborador_id=esc.colaborador_id,
        tipo="trivia_jugada",
        origen_tipo="juego",
        origen_id=esc.bloque_contenido_id,
        xp=150,
        clase_xp="ludico",
        clave_idempotencia="trivia:rank",
    )

    e = estado(db, esc.colaborador_id)
    assert e.xp_acreditable == 400          # solo lo aprobado
    assert e.xp_total == 550                # ranking incluye lo lúdico
    assert e.escalon == "Explorador"        # 400 < 1000


# ------------------------------------------- escalón derivado, nunca guardado
@pytest.mark.parametrize(
    "xp, escalon",
    [
        (0, "Explorador"),
        (999, "Explorador"),
        (1000, "Colaborador"),
        (2500, "Facilitador"),
        (4500, "Embajador"),
        (7000, "Líder de Calidad"),
        (10000, "Maestro de Acreditación"),
    ],
)
def test_el_escalon_se_deriva_del_xp_acreditable(db, xp, escalon):
    assert db.execute("SELECT fn_escalon(%s)", (xp,)).fetchone()[0] == escalon


# ------------------------------------------------------- pendiente declarado
@pytest.mark.skip(reason="I-10 es de capa API: se implementa y verifica en la Tanda 4")
def test_i10_no_se_sirve_contenido_de_otro_cargo():
    ...
