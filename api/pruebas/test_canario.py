"""
EL CANARIO.

    Un colaborador rinde una evaluación y la reprueba deliberadamente.
    Al terminar: CERO insignias.

Si el canario produce insignia, el sistema está roto y el build se bloquea. No es
un test más: es la condición de existencia del proyecto. Corre en CI ANTES de que
exista la primera medalla del sistema (CLAUDE.md §9.2 · ADR-005).

Por qué importa tanto: la plataforma es el respaldo con el que AIEP demuestra ante
la CNA que sus colaboradores cumplen. Una medalla sin aprobación real no es un bug
cosmético — es evidencia falsa en un proceso de acreditación.
"""
from motor.evaluacion import abrir_intento, cerrar_intento
from motor.eventos import estado

from conftest import responder_intento


def test_canario_el_intento_reprobado_jamas_produce_medalla(db, esc):
    antes = estado(db, esc.colaborador_id)
    assert antes.insignias == 0
    assert antes.xp_acreditable == 0
    assert antes.escalon == "Explorador"

    intento_id = abrir_intento(
        db, colaborador_id=esc.colaborador_id, bloque_ruta_id=esc.bloque_ruta_id
    )

    # 2 de 5 correctas = 40%. El umbral es 80%.
    responder_intento(db, intento_id, aciertos=2)
    resultado = cerrar_intento(db, intento_id=intento_id)

    assert resultado.aprobado is False
    assert resultado.puntaje == 0.4
    assert resultado.insignia_id is None, "EL CANARIO MURIÓ: un intento reprobado otorgó insignia"
    assert resultado.xp_otorgado == 0

    # Y nada quedó por detrás.
    despues = estado(db, esc.colaborador_id)
    assert despues.insignias == 0, "EL CANARIO MURIÓ: hay una insignia sin aprobación que la respalde"
    assert despues.xp_acreditable == 0, "un intento reprobado no puede dejar XP acreditable"
    assert despues.escalon == "Explorador", "el escalón no puede subir sin aprobar"

    total_insignias = db.execute("SELECT count(*) FROM insignia").fetchone()[0]
    assert total_insignias == 0, "EL CANARIO MURIÓ: hay insignias en la base"

    # §4.5: reprobar no deja residuo que después pueda contar como avance.
    eventos = db.execute(
        "SELECT count(*) FROM evento_gamificacion WHERE clase_xp = 'acreditable'"
    ).fetchone()[0]
    assert eventos == 0, "un intento reprobado no puede emitir eventos acreditables"

    estado_bloque = db.execute(
        "SELECT estado FROM bloque_ruta WHERE id = %s", (esc.bloque_ruta_id,)
    ).fetchone()[0]
    assert estado_bloque != "completo", "el bloque no puede quedar completo sin aprobar"


def test_canario_agotar_los_reintentos_tampoco_otorga(db, esc):
    """S-11: agotar los 3 intentos deja el bloque esperando acompañamiento, no lo aprueba."""
    for _ in range(3):
        intento_id = abrir_intento(
            db, colaborador_id=esc.colaborador_id, bloque_ruta_id=esc.bloque_ruta_id
        )
        responder_intento(db, intento_id, aciertos=0)
        assert cerrar_intento(db, intento_id=intento_id).aprobado is False

    assert estado(db, esc.colaborador_id).insignias == 0, (
        "EL CANARIO MURIÓ: agotar reintentos otorgó una medalla"
    )
    estado_bloque = db.execute(
        "SELECT estado FROM bloque_ruta WHERE id = %s", (esc.bloque_ruta_id,)
    ).fetchone()[0]
    assert estado_bloque == "requiere_acompanamiento"


def test_el_camino_legitimo_si_otorga(db, esc):
    """Contrapeso: si el canario nunca canta, el test no prueba nada."""
    intento_id = abrir_intento(
        db, colaborador_id=esc.colaborador_id, bloque_ruta_id=esc.bloque_ruta_id
    )
    responder_intento(db, intento_id, aciertos=5)          # 100%
    resultado = cerrar_intento(db, intento_id=intento_id)

    assert resultado.aprobado is True
    assert resultado.insignia_id is not None
    assert resultado.xp_otorgado == 400

    despues = estado(db, esc.colaborador_id)
    assert despues.insignias == 1
    assert despues.xp_acreditable == 400

    # Y la medalla es auditable: existe el intento aprobado que la respalda.
    respaldo = db.execute(
        """
        SELECT ie.aprobado, ie.puntaje, ie.enviado_en IS NOT NULL
          FROM insignia i JOIN intento_evaluacion ie ON ie.id = i.intento_evaluacion_id
         WHERE i.id = %s
        """,
        (resultado.insignia_id,),
    ).fetchone()
    assert respaldo == (True, 1.0, True)
