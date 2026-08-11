"""
Población sintética para que el panel institucional tenga algo que mostrar.

Con los tres colaboradores del slice el panel es correcto y está vacío: **todos
los grupos quedan bajo el umbral de anonimato**, así que no se puede ver ni si
el desglose funciona ni si el candado de privacidad funciona. Esta población
existe para eso.

Dos reglas que la hacen útil en vez de decorativa:

1. **No se inventan medallas.** Cada insignia sintética nace de un
   `intento_evaluacion` aprobado de verdad, con su puntaje sobre el umbral —el
   reforzado si la dimensión es crítica—. Los triggers de ADR-005 la validan
   igual que a una persona real, así que sembrar 120 personas es también una
   prueba de carga del invariante.
2. **El reparto por unidad deja grupos chicos a propósito.** Dos unidades quedan
   con menos de 5 personas para poder ver el plegado en «reservados» y comprobar
   que el panel no las desglosa.

Es determinista: la misma semilla produce la misma población, así que el panel
se ve igual entre corridas y los números se pueden discutir.

Tamaño configurable con `POBLACION_DE_PRUEBA` (0 la desactiva). Sirve para
probar el panel a escala: con 85.000 el modelo de consulta es el mismo.
"""
from __future__ import annotations

import json
import os
import random
from datetime import datetime, timedelta, timezone

SEMILLA = 20260811
DOMINIO = "poblacion.prueba.aiep.cl"

# Cómo se reparte la gente. Las dos últimas quedan bajo el umbral a propósito.
REPARTO_UNIDAD = [
    ("Sede Providencia", 0.34),
    ("Sede La Serena", 0.28),
    ("Escuela de Administración y Negocios", 0.22),
    ("Dirección Nacional de Aseguramiento de la Calidad", 0.11),
    ("Escuela de Informática y Telecomunicaciones", 0.03),
    ("Sede Chillán", 0.02),
]

# Roles: la base de la pirámide es la más numerosa.
REPARTO_ROL = [("N3", 0.60), ("N2", 0.30), ("N1", 0.10)]

# Qué tan lejos llegó cada persona. Suma 1.
PERFILES = [
    ("sin_empezar", 0.14),   # nunca entró
    ("asomado", 0.20),       # vio algo, no cerró ningún bloque
    ("en_curso", 0.38),      # cerró 1 o 2 bloques
    ("avanzado", 0.20),      # cerró 3 o 4
    ("completo", 0.08),      # cerró los 5
]

NOMBRES = [
    "Camila", "Matías", "Valentina", "Sebastián", "Javiera", "Cristóbal", "Antonia",
    "Benjamín", "Fernanda", "Ignacio", "Catalina", "Vicente", "Josefa", "Tomás",
    "Isidora", "Agustín", "Emilia", "Martín", "Florencia", "Diego", "Constanza",
    "Joaquín", "Amanda", "Lucas", "Trinidad", "Gabriel", "Renata", "Felipe",
]
APELLIDOS = [
    "Rojas", "Muñoz", "Contreras", "Silva", "Fuentes", "Araya", "Torres", "Vergara",
    "Espinoza", "Cortés", "Bravo", "Sepúlveda", "Reyes", "Riquelme", "Gutiérrez",
    "Aravena", "Núñez", "Cárdenas", "Salazar", "Vidal", "Poblete", "Henríquez",
]


def _elegir(rng: random.Random, opciones):
    r = rng.random()
    acumulado = 0.0
    for valor, peso in opciones:
        acumulado += peso
        if r <= acumulado:
            return valor
    return opciones[-1][0]


def sembrar_poblacion(conn, *, cargo: dict, unidad: dict, generar_ruta) -> dict:
    """
    Crea la población sintética si no está. Idempotente: si ya existe, no hace nada.

    `generar_ruta` se recibe en vez de importarse para no cruzar el seed consigo
    mismo; es la misma función que arma la ruta de una persona real, así que esta
    gente recorre exactamente el mismo modelo.
    """
    cuantos = int(os.environ.get("POBLACION_DE_PRUEBA", "120"))
    if cuantos <= 0:
        return {"poblacion_de_prueba": 0, "motivo": "desactivada por POBLACION_DE_PRUEBA=0"}

    ya = conn.execute(
        "SELECT count(*) FROM colaborador WHERE es_de_prueba"
    ).fetchone()[0]
    if ya >= cuantos:
        return {"poblacion_de_prueba": ya, "motivo": "ya estaba sembrada"}

    rng = random.Random(SEMILLA)
    ahora = datetime.now(timezone.utc)
    creados = 0

    for i in range(ya, cuantos):
        nombre = f"{rng.choice(NOMBRES)} {rng.choice(APELLIDOS)}"
        email = f"p{i:05d}@{DOMINIO}"
        codigo_rol = _elegir(rng, REPARTO_ROL)
        nombre_unidad = _elegir(rng, REPARTO_UNIDAD)

        colaborador_id = conn.execute(
            """INSERT INTO colaborador (email, nombre, cargo_id, unidad_id, es_de_prueba)
               VALUES (%s,%s,%s,%s,true)
               ON CONFLICT (email) DO UPDATE SET nombre = EXCLUDED.nombre
               RETURNING id""",
            (email, nombre, cargo[codigo_rol], unidad[nombre_unidad]),
        ).fetchone()[0]

        generar_ruta(conn, colaborador_id=colaborador_id, cargo_id=cargo[codigo_rol])
        _recorrer(conn, rng, colaborador_id, _elegir(rng, PERFILES), ahora)
        creados += 1

    return {"poblacion_de_prueba": creados}


def _recorrer(conn, rng, colaborador_id, perfil: str, ahora) -> None:
    """Simula el recorrido de una persona: módulos, evaluaciones y juegos."""
    if perfil == "sin_empezar":
        return

    bloques = conn.execute(
        """SELECT br.id, br.bloque_contenido_id, br.orden, br.es_critica,
                  COALESCE(br.umbral_aprobacion, e.umbral_aprobacion), e.id
             FROM bloque_ruta br
             JOIN ruta r ON r.id = br.ruta_id
             LEFT JOIN evaluacion e ON e.bloque_contenido_id = br.bloque_contenido_id
            WHERE r.colaborador_id = %s
            ORDER BY br.orden""",
        (colaborador_id,),
    ).fetchall()

    a_completar = {"asomado": 0, "en_curso": rng.randint(1, 2),
                   "avanzado": rng.randint(3, 4), "completo": len(bloques)}[perfil]

    # La actividad se reparte hacia atrás en el tiempo: sin esto, «activos en los
    # últimos 30 días» sería el 100% y no diría nada.
    desde = ahora - timedelta(days=rng.randint(5, 150))

    for n, (br_id, bc_id, orden, es_critica, umbral, ev_id) in enumerate(bloques):
        cerrado = n < a_completar
        cuando = desde + timedelta(days=n * rng.randint(3, 12))
        if cuando > ahora:
            cuando = ahora - timedelta(hours=rng.randint(1, 72))

        modulos = conn.execute(
            "SELECT id, xp FROM modulo WHERE bloque_contenido_id = %s ORDER BY orden",
            (bc_id,),
        ).fetchall()

        # El bloque en curso puede quedar con módulos a medio ver.
        vistos = modulos if cerrado else modulos[: rng.randint(0, len(modulos))]
        for modulo_id, xp in vistos:
            _evento(conn, colaborador_id, "modulo_completado", "modulo", modulo_id,
                    xp, "acreditable", f"modulo:{colaborador_id}:{modulo_id}", cuando)

        if rng.random() < 0.55:
            _evento(conn, colaborador_id, "juego_de_prueba", "juego", br_id,
                    rng.choice([144, 200, 280, 360]), "ludico",
                    f"juego:{colaborador_id}:{br_id}", cuando)

        if not ev_id:
            continue

        if cerrado:
            # Un intento aprobado de verdad: la insignia cuelga de él y los
            # triggers lo verifican igual que a una persona real.
            puntaje = round(min(1.0, float(umbral) + rng.choice([0.0, 0.02, 0.125, 0.25])), 3)
            intento = _intento(conn, colaborador_id, br_id, ev_id, 1, puntaje, True, cuando)
            _otorgar(conn, colaborador_id, bc_id, es_critica, intento, cuando)
            conn.execute("UPDATE bloque_ruta SET estado = 'completo' WHERE id = %s", (br_id,))
        elif n == a_completar:
            # El bloque donde se quedó: disponible, o atascado si agotó intentos.
            atascado = rng.random() < 0.12
            if atascado:
                for k in range(1, 4):
                    _intento(conn, colaborador_id, br_id, ev_id, k,
                             round(float(umbral) - rng.choice([0.125, 0.25, 0.375]), 3),
                             False, cuando)
                conn.execute(
                    "UPDATE bloque_ruta SET estado = 'requiere_acompanamiento' WHERE id = %s",
                    (br_id,),
                )
            else:
                conn.execute(
                    "UPDATE bloque_ruta SET estado = 'disponible' WHERE id = %s", (br_id,)
                )
            break


def _evento(conn, colaborador_id, tipo, origen_tipo, origen_id, xp, clase, clave, cuando):
    conn.execute(
        """INSERT INTO evento_gamificacion
               (colaborador_id, tipo, origen_tipo, origen_id, xp, clase_xp,
                clave_idempotencia, ocurrido_en)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
           ON CONFLICT (clave_idempotencia) DO NOTHING""",
        (colaborador_id, tipo, origen_tipo, origen_id, xp, clase, clave, cuando),
    )


def _intento(conn, colaborador_id, br_id, ev_id, numero, puntaje, aprobado, cuando):
    return conn.execute(
        """INSERT INTO intento_evaluacion
               (colaborador_id, bloque_ruta_id, evaluacion_id, numero_intento, estado,
                items_servidos, iniciado_en, expira_en, enviado_en, puntaje, aprobado)
           VALUES (%s,%s,%s,%s,'enviado',%s::jsonb,%s,%s,%s,%s,%s)
           RETURNING id""",
        (colaborador_id, br_id, ev_id, numero, json.dumps([]), cuando,
         cuando + timedelta(days=1), cuando, puntaje, aprobado),
    ).fetchone()[0]


def _otorgar(conn, colaborador_id, bc_id, es_critica, intento_id, cuando):
    """El rango lo decide la criticidad de la ruta; la base lo vuelve a verificar."""
    medalla = conn.execute(
        "SELECT id, xp FROM definicion_medalla WHERE bloque_contenido_id = %s AND tipo = %s",
        (bc_id, "gold" if es_critica else "silver"),
    ).fetchone()
    if not medalla:
        return
    insignia = conn.execute(
        """INSERT INTO insignia (colaborador_id, definicion_medalla_id, intento_evaluacion_id,
                                 otorgada_en)
           VALUES (%s,%s,%s,%s)
           ON CONFLICT (colaborador_id, definicion_medalla_id) DO NOTHING
           RETURNING id""",
        (colaborador_id, medalla[0], intento_id, cuando),
    ).fetchone()
    if insignia:
        _evento(conn, colaborador_id, "medalla_otorgada", "medalla", insignia[0],
                medalla[1], "acreditable", f"insignia:{insignia[0]}", cuando)
