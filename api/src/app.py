"""
API de Somos Calidad.

`/docs` es la primera interfaz de prueba del director (CLAUDE.md §11).

**Aislamiento por cargo (I-10 · CLAUDE.md §3).** Ningún endpoint recibe un
`colaborador_id` por parámetro: se deriva de la sesión. Y todo acceso a contenido
pasa por `_bloque_propio()`, que verifica que el bloque esté en la ruta de quien
pregunta. No existe forma de pedir un bloque por id y recibirlo si no es tuyo.
"""
from __future__ import annotations

import os
from typing import Optional
from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from psycopg_pool import ConnectionPool
from pydantic import BaseModel, Field

from identidad import SesionInvalida, proveedor_activo, verificar
from motor.desafio import NoCritica, resolver_desafio, ver_desafio
from motor.juegos import JuegoNoCorresponde, juego_de
from motor.linea_tiempo import cerrar_linea, repartir as repartir_linea
from motor.evaluacion import (
    DesafioPendiente, ModulosPendientes, SinReintentos, abrir_intento,
    cerrar_intento, responder,
)
from motor.eventos import estado as leer_estado
from motor.progreso import completar_modulo
from motor.calibre import puntuar_calibre
from motor.mesa import cerrar_mesa, repartir
from motor.quiz import puntuar_quiz

DSN = os.environ["DATABASE_URL"]
pool = ConnectionPool(DSN, min_size=1, max_size=10, open=True)
identidad = proveedor_activo()

app = FastAPI(
    title="Somos Calidad · API",
    version="0.4.0",
    description=(
        "Portal de gamificación de la ruta de acreditación de AIEP.\n\n"
        "El contenido de esta etapa está marcado `es_contenido_prueba` y **no es "
        "material de acreditación oficial**. La estructura —5 dimensiones, 13 hitos, "
        "gobernanza— sí sale de la ruta institucional real.\n\n"
        "**Para probar:** `POST /auth/dev/actuar-como` con el id de un colaborador, "
        "copia el token y pégalo en *Authorize* como `Bearer <token>`."
    ),
)


# ------------------------------------------------------------------- CORS
#
# El frontend se sirve en su propio puerto (5180) y la API en el suyo (8010), así
# que toda llamada del navegador es cross-origin y necesita preflight. Con el
# servidor de desarrollo de Vite esto no se notaba, porque su proxy dejaba todo
# same-origin; al contenedorizar la web apareció.
#
# `ORIGENES_PERMITIDOS` (separados por coma) manda siempre. Si no está definida y
# corre en modo dev, se acepta cualquier localhost o IP de red privada en
# cualquier puerto, para poder abrir la web desde el teléfono. Fuera de modo dev y
# sin la variable no se permite ningún origen: es preferible que falle visible a
# que quede abierto por omisión.
_origenes = [o.strip() for o in os.environ.get("ORIGENES_PERMITIDOS", "").split(",") if o.strip()]
_es_dev = os.environ.get("MODO_DEV", "").lower() == "true"
_regex_dev = r"^http://(localhost|127\.0\.0\.1|(10|192\.168)\.[0-9.]+|172\.(1[6-9]|2[0-9]|3[01])\.[0-9.]+)(:\d+)?$"

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origenes,
    allow_origin_regex=None if _origenes else (_regex_dev if _es_dev else None),
    # No se usan cookies: la sesión viaja en la cabecera Authorization. Dejarlo en
    # False evita el modo con credenciales, que es más estricto y no hace falta.
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600,
)


def filas(sql: str, args: tuple = ()) -> list[dict]:
    with pool.connection() as conn:
        cur = conn.execute(sql, args)
        cols = [c.name for c in cur.description]
        return [dict(zip(cols, f)) for f in cur.fetchall()]


# ============================================================== identidad
def colaborador_actual(authorization: Optional[str] = Header(default=None)) -> UUID:
    """
    Quién eres. Sale de la sesión firmada, nunca de un parámetro.

    `Optional[str]` y no `str | None`: FastAPI evalúa esta anotación en tiempo de
    ejecución y la máquina del director corre Python 3.9. El contenedor usa 3.12,
    pero la suite tiene que poder correrse en local.
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "falta la cabecera Authorization: Bearer <token>")
    try:
        datos = verificar(authorization.split(" ", 1)[1].strip())
    except SesionInvalida as e:
        raise HTTPException(401, str(e))
    return UUID(datos["sub"])


def con_permiso_institucional(yo: UUID = Depends(colaborador_actual)) -> UUID:
    """
    El permiso sale de la membresía de comité, no del cargo (S-35): lo tiene quien
    está en Aseguramiento de la Calidad, en el Comité Central o en la Junta.
    """
    tiene = filas("SELECT 1 FROM permiso_institucional WHERE colaborador_id = %s", (yo,))
    if not tiene:
        raise HTTPException(403, "requiere permiso institucional")
    return yo


def _bloque_propio(bloque_ruta_id: UUID, yo: UUID) -> dict:
    """
    El candado de I-10.

    Devuelve el bloque solo si está en la ruta de quien pregunta. Responde 404 y no
    403 a propósito: un 403 confirmaría que el bloque existe, y eso ya filtra
    información sobre el contenido de otro cargo.
    """
    encontrado = filas(
        """SELECT br.id, br.bloque_contenido_id, bc.es_contenido_prueba
             FROM bloque_ruta br
             JOIN ruta r ON r.id = br.ruta_id
             JOIN bloque_contenido bc ON bc.id = br.bloque_contenido_id
            WHERE br.id = %s AND r.colaborador_id = %s""",
        (bloque_ruta_id, yo),
    )
    if not encontrado:
        raise HTTPException(404, "ese bloque no está en tu ruta")
    return encontrado[0]


@app.get("/", include_in_schema=False)
def raiz():
    return RedirectResponse("/docs")


@app.get("/salud", tags=["sistema"])
def salud():
    """¿Está viva la API y responde la base?"""
    with pool.connection() as conn:
        conn.execute("SELECT 1")
    return {"ok": True, "servicio": "api", "proveedor_identidad": identidad.nombre}


class ActuarComo(BaseModel):
    colaborador_id: UUID


@app.get("/auth/dev/colaboradores", tags=["identidad"])
def colaboradores_para_actuar():
    """
    A quién se puede representar en desarrollo. Con Entra devuelve vacío: ahí uno se
    autentica de verdad. **No hay contraseñas en el sistema** (S-18).
    """
    with pool.connection() as conn:
        return identidad.colaboradores_disponibles(conn)


@app.post("/auth/dev/actuar-como", tags=["identidad"])
def actuar_como(cuerpo: ActuarComo):
    """Emite la sesión. Pega el token en *Authorize* como `Bearer <token>`."""
    with pool.connection() as conn:
        try:
            token = identidad.autenticar(conn, colaborador_id=cuerpo.colaborador_id)
        except LookupError as e:
            raise HTTPException(404, str(e))
        except NotImplementedError as e:
            raise HTTPException(501, str(e))
    return {"token": token, "tipo": "Bearer"}


@app.get("/auth/yo", tags=["identidad"])
def quien_soy(yo: UUID = Depends(colaborador_actual)):
    """La identidad de la sesión actual, con su estado derivado."""
    datos = filas(
        """SELECT c.id, c.nombre, c.email, ca.nombre AS cargo, ca.codigo AS cargo_codigo,
                  u.nombre AS unidad, ec.xp_acreditable, ec.xp_total, ec.escalon, ec.insignias,
                  (pi.colaborador_id IS NOT NULL) AS ve_panel_institucional
             FROM colaborador c
             JOIN cargo ca ON ca.id = c.cargo_id
             LEFT JOIN unidad u ON u.id = c.unidad_id
             JOIN estado_colaborador ec ON ec.colaborador_id = c.id
             LEFT JOIN permiso_institucional pi ON pi.colaborador_id = c.id
            WHERE c.id = %s""",
        (yo,),
    )
    if not datos:
        raise HTTPException(404, "colaborador inexistente")
    return datos[0]


# ============================================================ catálogo real
@app.get("/catalogo/dimensiones", tags=["catálogo"])
def dimensiones(yo: UUID = Depends(colaborador_actual)):
    """Las 5 dimensiones evaluativas de la CNA. Son el esqueleto del contenido."""
    return filas(
        "SELECT codigo, nombre_oficial, obligatoria, orden FROM dimension ORDER BY orden"
    )


@app.get("/catalogo/hitos", tags=["catálogo"])
def hitos(yo: UUID = Depends(colaborador_actual)):
    """Los 13 hitos de la ruta 2026–2027. H13 no tiene fecha: la fuente dice «por definir»."""
    return filas(
        """SELECT codigo, ruta, anio, periodo_texto, titulo, fecha_inicio, fecha_fin
             FROM hito ORDER BY orden"""
    )


@app.get("/catalogo/cargos", tags=["catálogo"])
def cargos(yo: UUID = Depends(colaborador_actual)):
    """Los 6 cargos del slice, con cuántas personas los ocupan."""
    return filas(
        """SELECT c.codigo, c.nombre, c.descripcion, count(col.id) AS colaboradores
             FROM cargo c LEFT JOIN colaborador col ON col.cargo_id = c.id
            GROUP BY c.id ORDER BY c.codigo"""
    )


@app.get("/catalogo/matriz", tags=["catálogo"])
def matriz(yo: UUID = Depends(colaborador_actual)):
    """
    **La matriz Cargo × Dimensión** (ADR-003) — el corazón del modelo.

    30 filas: 6 cargos × 5 dimensiones. Gracias al anidamiento de los estándares CNA
    esto se sirve con solo **15 unidades de contenido**, no 30.

    Es catálogo, no contenido: dice qué nivel se le exige a cada cargo, nunca el
    material de esos bloques. El aislamiento de I-10 opera sobre el contenido.
    """
    return filas(
        """SELECT ca.codigo AS cargo, ca.nombre AS cargo_nombre,
                  d.codigo  AS dimension, d.nombre_oficial AS dimension_nombre,
                  e.nivel_estandar, e.orden_en_ruta, h.codigo AS hito
             FROM exigencia_cargo_dimension e
             JOIN cargo ca ON ca.id = e.cargo_id
             JOIN dimension d ON d.id = e.dimension_id
             LEFT JOIN hito h ON h.id = e.hito_id
            ORDER BY ca.codigo, e.orden_en_ruta"""
    )


@app.get("/catalogo/contenido", tags=["catálogo"])
def contenido(yo: UUID = Depends(con_permiso_institucional)):
    """Inventario de las 15 unidades. Requiere permiso institucional: es vista de gestión."""
    return filas(
        """SELECT d.codigo AS dimension, bc.nivel_estandar, bc.titulo,
                  bc.es_contenido_prueba, bc.estado,
                  (SELECT count(*) FROM modulo m WHERE m.bloque_contenido_id = bc.id) AS modulos,
                  (SELECT count(*) FROM item_evaluacion i
                     JOIN evaluacion ev ON ev.id = i.evaluacion_id
                    WHERE ev.bloque_contenido_id = bc.id) AS items_del_banco,
                  (SELECT count(*) FROM exigencia_cargo_dimension e
                    WHERE e.dimension_id = bc.dimension_id
                      AND e.nivel_estandar = bc.nivel_estandar) AS cargos_que_la_usan
             FROM bloque_contenido bc JOIN dimension d ON d.id = bc.dimension_id
            ORDER BY d.orden, bc.nivel_estandar"""
    )


@app.get("/catalogo/comites", tags=["catálogo"])
def comites(yo: UUID = Depends(colaborador_actual)):
    """La gobernanza de la fuente. De acá salen los permisos institucionales (S-35)."""
    return filas(
        """SELECT co.tipo, co.nombre, d.codigo AS dimension, u.nombre AS unidad,
                  (SELECT count(*) FROM membresia_comite m WHERE m.comite_id = co.id) AS integrantes
             FROM comite co
             LEFT JOIN dimension d ON d.id = co.dimension_id
             LEFT JOIN unidad u ON u.id = co.unidad_id
            ORDER BY co.tipo, co.nombre"""
    )


# ============================================================= lo mío
@app.get("/mi/ruta", tags=["mi ruta"])
def mi_ruta(yo: UUID = Depends(colaborador_actual)):
    """
    Mis 5 bloques, uno por dimensión, cada uno al nivel que me exige mi rol y
    anclado a un hito real del proceso.

    Desde el modelo de AIEP cada bloque viaja además con su **peso** en el rol, si
    es **ruta crítica**, el umbral que le corresponde y el **rango de medalla** que
    está en juego. La medalla se elige por criticidad: un bloque define silver y
    gold, y acá se muestra la que efectivamente se puede ganar en esta ruta.
    """
    datos = filas(
        """SELECT br.id AS bloque_ruta_id, br.orden, br.estado,
                  d.codigo AS dimension, d.nombre_oficial AS dimension_nombre,
                  bc.nivel_estandar, bc.titulo, bc.es_contenido_prueba,
                  br.es_critica, br.peso_ranking,
                  COALESCE(br.umbral_aprobacion, e.umbral_aprobacion) AS umbral,
                  h.codigo AS hito, h.periodo_texto, h.titulo AS hito_titulo,
                  dm.nombre AS medalla, dm.tipo AS medalla_tipo, dm.xp AS medalla_xp,
                  (SELECT count(*) FROM modulo m WHERE m.bloque_contenido_id = bc.id) AS modulos,
                  (SELECT count(*) FROM insignia i
                     WHERE i.colaborador_id = %s AND i.definicion_medalla_id = dm.id) AS obtenida,
                  (SELECT count(*) FROM resolucion_desafio rd
                     WHERE rd.colaborador_id = %s AND rd.bloque_ruta_id = br.id) AS desafio_resuelto
             FROM bloque_ruta br
             JOIN ruta r ON r.id = br.ruta_id
             JOIN bloque_contenido bc ON bc.id = br.bloque_contenido_id
             JOIN dimension d ON d.id = bc.dimension_id
             LEFT JOIN evaluacion e ON e.bloque_contenido_id = bc.id
             LEFT JOIN hito h ON h.id = br.hito_id
             LEFT JOIN definicion_medalla dm
                    ON dm.bloque_contenido_id = bc.id
                   AND dm.tipo = CASE WHEN br.es_critica THEN 'gold' ELSE 'silver' END
            WHERE r.colaborador_id = %s
            ORDER BY br.orden""",
        (yo, yo, yo),
    )
    if not datos:
        raise HTTPException(404, "todavía no tienes ruta generada")
    return datos


@app.get("/mi/estado", tags=["mi ruta"])
def mi_estado(yo: UUID = Depends(colaborador_actual)):
    """
    Estado DERIVADO. No hay columnas `xp` ni `nivel` que consultar: todo sale de los
    eventos (ADR-005 §3). El escalón usa solo XP acreditable; el ranking, el total.
    """
    with pool.connection() as conn:
        try:
            e = leer_estado(conn, yo)
        except LookupError:
            raise HTTPException(404, "colaborador inexistente")
    return {
        "xp_acreditable": e.xp_acreditable,
        "xp_ludico": e.xp_ludico,
        "xp_total": e.xp_total,
        "xp_ranking": e.xp_ranking,
        "escalon": e.escalon,
        "insignias": e.insignias,
    }


@app.get("/mi/insignias", tags=["mi ruta"])
def mis_insignias(yo: UUID = Depends(colaborador_actual)):
    """Cada insignia con el intento aprobado que la respalda. Auditable por diseño."""
    return filas(
        """SELECT dm.nombre AS medalla, dm.tipo, dm.xp, i.otorgada_en,
                  ie.puntaje AS puntaje_del_respaldo, ie.enviado_en AS rendida_en,
                  ie.numero_intento
             FROM insignia i
             JOIN definicion_medalla dm ON dm.id = i.definicion_medalla_id
             JOIN intento_evaluacion ie ON ie.id = i.intento_evaluacion_id
            WHERE i.colaborador_id = %s
            ORDER BY i.otorgada_en""",
        (yo,),
    )


@app.get("/ranking", tags=["mi ruta"])
def ranking(yo: UUID = Depends(colaborador_actual)):
    """
    Ranking por XP total, con el desempate de S-15.

    Es agregado: nombre, unidad, XP y **conteo** de insignias. Nunca el nombre de las
    insignias de otro cargo, que filtraría su contenido (S-16).
    """
    return filas("SELECT * FROM ranking ORDER BY posicion")


@app.get("/colaboradores", tags=["gestión"])
def colaboradores(yo: UUID = Depends(con_permiso_institucional)):
    """Nómina con avance. Requiere permiso institucional (E-03)."""
    return filas(
        """SELECT c.id, c.email, c.nombre, ca.nombre AS cargo, u.nombre AS unidad,
                  ec.xp_acreditable, ec.xp_total, ec.escalon, ec.insignias
             FROM colaborador c
             JOIN cargo ca ON ca.id = c.cargo_id
             LEFT JOIN unidad u ON u.id = c.unidad_id
             JOIN estado_colaborador ec ON ec.colaborador_id = c.id
            ORDER BY c.nombre"""
    )


# =============================================================== contenido
@app.get("/bloques-ruta/{bloque_ruta_id}", tags=["contenido"])
def bloque(bloque_ruta_id: UUID, yo: UUID = Depends(colaborador_actual)):
    """
    El bloque completo: cabecera, módulos con su estado, la evaluación y la medalla.

    `evaluacion_disponible` es lo que ordena el recorrido: la evaluación se abre
    cuando están vistos todos los módulos —y, en la dimensión crítica, también
    cuando está resuelto el desafío aplicado. No es un candado de integridad —esa
    la impone la base—, es la secuencia formativa.
    """
    _bloque_propio(bloque_ruta_id, yo)

    cabecera = filas(
        """SELECT br.id AS bloque_ruta_id, br.orden, br.estado,
                  d.codigo AS dimension, d.nombre_oficial AS dimension_nombre,
                  bc.nivel_estandar, bc.titulo, bc.es_contenido_prueba,
                  br.es_critica, br.peso_ranking,
                  h.codigo AS hito, h.periodo_texto, h.titulo AS hito_titulo,
                  dm.id AS medalla_id, dm.nombre AS medalla, dm.tipo AS medalla_tipo,
                  dm.xp AS medalla_xp,
                  COALESCE(br.umbral_aprobacion, ev.umbral_aprobacion) AS umbral_aprobacion,
                  ev.n_items_por_intento, ev.max_reintentos,
                  (SELECT count(*) FROM insignia i
                    WHERE i.colaborador_id = %s AND i.definicion_medalla_id = dm.id) AS obtenida,
                  (SELECT count(*) FROM intento_evaluacion ie
                    WHERE ie.bloque_ruta_id = br.id) AS intentos_usados,
                  (SELECT count(*) FROM resolucion_desafio rd
                    WHERE rd.colaborador_id = %s AND rd.bloque_ruta_id = br.id) AS desafio_resuelto
             FROM bloque_ruta br
             JOIN bloque_contenido bc ON bc.id = br.bloque_contenido_id
             JOIN dimension d ON d.id = bc.dimension_id
             LEFT JOIN hito h ON h.id = br.hito_id
             LEFT JOIN definicion_medalla dm
                    ON dm.bloque_contenido_id = bc.id
                   AND dm.tipo = CASE WHEN br.es_critica THEN 'gold' ELSE 'silver' END
             LEFT JOIN evaluacion ev ON ev.bloque_contenido_id = bc.id
            WHERE br.id = %s""",
        (yo, yo, bloque_ruta_id),
    )[0]

    modulos = _modulos_del_bloque(bloque_ruta_id, yo)
    completos = sum(1 for m in modulos if m["completado"])
    falta_desafio = bool(cabecera["es_critica"]) and not cabecera["desafio_resuelto"]
    juego = juego_de(cabecera["dimension"])

    return {
        **cabecera,
        # Cada dimensión lleva su propio juego. Mientras no exista, la pantalla
        # muestra el hueco en vez de esconderlo (fase 2).
        "juego": juego,
        "modulos": modulos,
        "modulos_completos": completos,
        "desafio_pendiente": falta_desafio,
        "evaluacion_disponible": (
            completos == len(modulos) and len(modulos) > 0 and not falta_desafio
        ),
    }


def _modulos_del_bloque(bloque_ruta_id: UUID, yo: UUID) -> list[dict]:
    return filas(
        """SELECT m.id, m.orden, m.titulo, m.cuerpo, m.duracion_min, m.xp,
                  m.nivel_estandar_origen, bc.es_contenido_prueba,
                  (e.id IS NOT NULL) AS completado
             FROM modulo m
             JOIN bloque_contenido bc ON bc.id = m.bloque_contenido_id
             JOIN bloque_ruta br ON br.bloque_contenido_id = bc.id
             LEFT JOIN evento_gamificacion e
                    ON e.origen_id = m.id AND e.origen_tipo = 'modulo' AND e.colaborador_id = %s
            WHERE br.id = %s ORDER BY m.orden""",
        (yo, bloque_ruta_id),
    )


@app.get("/bloques-ruta/{bloque_ruta_id}/modulos", tags=["contenido"])
def modulos(bloque_ruta_id: UUID, yo: UUID = Depends(colaborador_actual)):
    """
    El microlearning del bloque.

    `nivel_estandar_origen` muestra el anidamiento: en un bloque de nivel 3 conviven
    módulos de origen 1, 2 y 3, porque el estándar superior incluye a los anteriores.
    """
    _bloque_propio(bloque_ruta_id, yo)
    return _modulos_del_bloque(bloque_ruta_id, yo)


def _modulo_propio(modulo_id: UUID, yo: UUID) -> None:
    mio = filas(
        """SELECT 1 FROM modulo m
             JOIN bloque_ruta br ON br.bloque_contenido_id = m.bloque_contenido_id
             JOIN ruta r ON r.id = br.ruta_id
            WHERE m.id = %s AND r.colaborador_id = %s""",
        (modulo_id, yo),
    )
    if not mio:
        raise HTTPException(404, "ese módulo no está en tu ruta")


@app.get("/modulos/{modulo_id}/quiz", tags=["quiz formativo"])
def quiz(modulo_id: UUID, yo: UUID = Depends(colaborador_actual)):
    """
    Los ítems del quiz formativo, **con la respuesta correcta y las explicaciones**.

    Acá sí viajan al cliente, y es deliberado: el quiz da feedback inmediato y no
    otorga completitud (S-07). El banco de la evaluación final es otra tabla y no
    entrega la respuesta jamás.
    """
    _modulo_propio(modulo_id, yo)
    return filas(
        """SELECT id, orden, enunciado, alternativas, indice_correcta, explicaciones
             FROM item_quiz_formativo WHERE modulo_id = %s ORDER BY orden""",
        (modulo_id,),
    )


class RespuestaQuiz(BaseModel):
    item_id: UUID
    indice_elegido: int = Field(ge=0, le=3)


class ResultadoQuizEnviado(BaseModel):
    respuestas: list[RespuestaQuiz]


@app.post("/modulos/{modulo_id}/quiz/resultado", tags=["quiz formativo"])
def cerrar_quiz(modulo_id: UUID, cuerpo: ResultadoQuizEnviado,
                yo: UUID = Depends(colaborador_actual)):
    """
    Puntúa la partida. **El servidor recalcula todo**: aciertos, racha y XP.

    El cliente manda solo qué eligió y en qué orden. Si propusiera su propio XP,
    el tope diario y la racha serían decorativos. El XP es lúdico: no mueve el
    escalón ni acerca a una medalla (S-04).
    """
    _modulo_propio(modulo_id, yo)
    with pool.connection() as conn:
        try:
            r = puntuar_quiz(
                conn, colaborador_id=yo, modulo_id=modulo_id,
                respuestas=[{"item_id": x.item_id, "indice_elegido": x.indice_elegido}
                            for x in cuerpo.respuestas],
            )
        except LookupError as e:
            raise HTTPException(404, str(e))
    return {
        "total": r.total,
        "aciertos": r.aciertos,
        "mejor_racha": r.mejor_racha,
        "xp_otorgado": r.xp_otorgado,
        "ya_jugado_hoy": r.ya_jugado_hoy,
    }


class RespuestaCalibre(BaseModel):
    item_id: UUID
    indice_elegido: int = Field(ge=0, le=3)
    seguro: bool


class PartidaCalibre(BaseModel):
    respuestas: list[RespuestaCalibre]


@app.post("/modulos/{modulo_id}/calibre/resultado", tags=["quiz formativo"])
def cerrar_calibre(modulo_id: UUID, cuerpo: PartidaCalibre,
                   yo: UUID = Depends(colaborador_actual)):
    """
    Puntúa una partida de **Calibre** (M1).

    Los ítems son los mismos que sirve `GET /modulos/{id}/quiz`: solo quiz
    formativo, nunca el banco de la evaluación. Lo que cambia es la apuesta.

    El servidor recalcula todo, **penalización incluida**: decir «Seguro» y fallar
    resta. Si el puntaje lo propusiera el cliente, la apuesta sería decorativa.
    El XP es lúdico y no mueve el escalón (S-04).
    """
    _modulo_propio(modulo_id, yo)
    with pool.connection() as conn:
        try:
            r = puntuar_calibre(
                conn, colaborador_id=yo, modulo_id=modulo_id,
                respuestas=[{"item_id": x.item_id, "indice_elegido": x.indice_elegido,
                             "seguro": x.seguro} for x in cuerpo.respuestas],
            )
        except LookupError as e:
            raise HTTPException(404, str(e))
    return {
        "total": r.total, "aciertos": r.aciertos,
        "seguros": r.seguros, "seguros_acertados": r.seguros_acertados,
        "puntos": r.puntos, "bono_calibrado": r.bono_calibrado,
        "xp_otorgado": r.xp_otorgado, "ya_jugado_hoy": r.ya_jugado_hoy,
    }


# ======================================================= B2 · Mesa de comité
class Colocacion(BaseModel):
    item_id: UUID
    dimension: str


class MesaCerrada(BaseModel):
    colocaciones: list[Colocacion]


@app.get("/juegos/mesa", tags=["juegos"])
def mesa(yo: UUID = Depends(colaborador_actual)):
    """
    Reparte una **Mesa de comité**: cinco bandejas y seis afirmaciones sueltas.

    Las cartas vienen **sin decir a qué bandeja van** — eso lo sabe solo el servidor
    hasta que se cierra la mesa. Salen de los bloques de tu propia ruta (I-10) y solo
    del quiz formativo, nunca del banco de la evaluación.
    """
    with pool.connection() as conn:
        try:
            return repartir(conn, colaborador_id=yo)
        except LookupError as e:
            raise HTTPException(404, str(e))


@app.post("/juegos/mesa/resultado", tags=["juegos"])
def resultado_mesa(cuerpo: MesaCerrada, yo: UUID = Depends(colaborador_actual)):
    """
    Cierra la mesa y la corrige.

    El cliente manda **dónde puso cada carta**; los aciertos, los puntos y el bono de
    mesa perfecta los calcula el servidor. XP lúdico: no mueve el escalón ni acerca a
    una medalla.
    """
    with pool.connection() as conn:
        try:
            r = cerrar_mesa(
                conn, colaborador_id=yo,
                colocaciones=[{"item_id": c.item_id, "dimension": c.dimension}
                              for c in cuerpo.colocaciones],
            )
        except LookupError as e:
            raise HTTPException(404, str(e))
    return {
        "total": r.total, "aciertos": r.aciertos, "puntos": r.puntos,
        "mesa_perfecta": r.mesa_perfecta, "xp_otorgado": r.xp_otorgado,
        "ya_jugado_hoy": r.ya_jugado_hoy, "revelacion": r.revelacion,
    }


@app.post("/modulos/{modulo_id}/completar", tags=["contenido"])
def completar(modulo_id: UUID, yo: UUID = Depends(colaborador_actual)):
    """
    Marca el módulo como visto y suma su XP acreditable.

    Idempotente: marcarlo dos veces no suma XP dos veces. **No otorga insignia** —
    eso sigue siendo exclusivo de la evaluación aprobada, y lo impone la base.
    """
    with pool.connection() as conn:
        try:
            return completar_modulo(conn, colaborador_id=yo, modulo_id=modulo_id)
        except LookupError as e:
            raise HTTPException(404, str(e))


# ============================================================== evaluación
class Respuesta(BaseModel):
    item_id: UUID
    indice_elegido: int = Field(ge=0, le=3)


@app.get("/bloques-ruta/{bloque_ruta_id}/evaluacion", tags=["evaluación"])
def ver_evaluacion(bloque_ruta_id: UUID, yo: UUID = Depends(colaborador_actual)):
    """Los ítems del banco. **Sin `indice_correcta`**: la respuesta no viaja al cliente."""
    _bloque_propio(bloque_ruta_id, yo)
    return filas(
        """SELECT i.id AS item_id, i.enunciado, i.alternativas
             FROM item_evaluacion i
             JOIN evaluacion ev ON ev.id = i.evaluacion_id
             JOIN bloque_ruta br ON br.bloque_contenido_id = ev.bloque_contenido_id
            WHERE br.id = %s ORDER BY i.enunciado""",
        (bloque_ruta_id,),
    )


@app.get("/bloques-ruta/{bloque_ruta_id}/clave-de-respuestas", tags=["evaluación"])
def clave_de_respuestas(bloque_ruta_id: UUID, yo: UUID = Depends(colaborador_actual)):
    """
    **Solo para verificar el slice desde `/docs`.** Devuelve la alternativa correcta.

    Triple candado: el bloque tiene que estar en tu ruta, `MODO_DEV=true`, y el bloque
    marcado `es_contenido_prueba`. Sobre contenido real responde 403 aunque el modo dev
    esté encendido. Se elimina antes de producción (tarea D8).
    """
    bloque = _bloque_propio(bloque_ruta_id, yo)

    if os.environ.get("MODO_DEV", "").lower() != "true":
        raise HTTPException(403, "solo disponible con MODO_DEV=true")
    if not bloque["es_contenido_prueba"]:
        raise HTTPException(403, "este bloque tiene contenido real: la clave no se revela")

    return filas(
        """SELECT i.id AS item_id, i.enunciado, i.indice_correcta
             FROM item_evaluacion i
             JOIN evaluacion ev ON ev.id = i.evaluacion_id
             JOIN bloque_ruta br ON br.bloque_contenido_id = ev.bloque_contenido_id
            WHERE br.id = %s ORDER BY i.enunciado""",
        (bloque_ruta_id,),
    )


# ============================================ juego de la dimensión (fase 2)
class LineaCerrada(BaseModel):
    """El orden en que quedaron las cartas. Cuál era el real lo pone el servidor."""
    orden: list[UUID] = Field(min_length=2, max_length=6)


@app.get("/bloques-ruta/{bloque_ruta_id}/juego/linea-tiempo", tags=["juegos"])
def linea_tiempo(bloque_ruta_id: UUID, yo: UUID = Depends(colaborador_actual)):
    """
    Seis hitos del proceso real, barajados y **sin su período ni su año**.

    Si viajaran las fechas, ordenar sería leerlas. Llegan en la revelación.
    """
    _bloque_propio(bloque_ruta_id, yo)
    with pool.connection() as conn:
        try:
            return repartir_linea(conn, colaborador_id=yo, bloque_ruta_id=bloque_ruta_id)
        except JuegoNoCorresponde as e:
            raise HTTPException(409, str(e))
        except LookupError as e:
            raise HTTPException(404, str(e))


@app.post("/bloques-ruta/{bloque_ruta_id}/juego/linea-tiempo/resultado", tags=["juegos"])
def resultado_linea_tiempo(bloque_ruta_id: UUID, cuerpo: LineaCerrada,
                           yo: UUID = Depends(colaborador_actual)):
    """Corrige la secuencia en el servidor. XP lúdico, con su cupo diario por bloque."""
    _bloque_propio(bloque_ruta_id, yo)
    with pool.connection() as conn:
        try:
            r = cerrar_linea(conn, colaborador_id=yo, bloque_ruta_id=bloque_ruta_id,
                             orden_propuesto=[str(h) for h in cuerpo.orden])
        except JuegoNoCorresponde as e:
            raise HTTPException(409, str(e))
        except ValueError as e:
            raise HTTPException(422, str(e))
        except LookupError as e:
            raise HTTPException(404, str(e))
    return {
        "total": r.total,
        "en_su_lugar": r.en_su_lugar,
        "pares_correctos": r.pares_correctos,
        "pares_totales": r.pares_totales,
        "linea_perfecta": r.linea_perfecta,
        "puntos": r.puntos,
        "xp_otorgado": r.xp_otorgado,
        "ya_jugado_hoy": r.ya_jugado_hoy,
        "revelacion": r.revelacion,
    }


# ======================================================== desafío aplicado
class RespuestaDecision(BaseModel):
    decision_id: UUID
    # La forma depende del tipo: "b" | ["a","c"] | {"a":"sostiene"}.
    respuesta: object


class DesafioResuelto(BaseModel):
    respuestas: list[RespuestaDecision] = Field(min_length=1)


@app.get("/bloques-ruta/{bloque_ruta_id}/desafio", tags=["desafío aplicado"])
def desafio(bloque_ruta_id: UUID, yo: UUID = Depends(colaborador_actual)):
    """
    El caso aplicado de una dimensión crítica, **sin las respuestas correctas**.

    Solo existe donde el rol tiene ruta crítica. En una dimensión estándar
    responde 409: no es que falte contenido, es que ese bloque no lleva desafío.
    """
    _bloque_propio(bloque_ruta_id, yo)
    with pool.connection() as conn:
        try:
            return ver_desafio(conn, colaborador_id=yo, bloque_ruta_id=bloque_ruta_id)
        except NoCritica as e:
            raise HTTPException(409, str(e))
        except LookupError as e:
            raise HTTPException(404, str(e))


@app.post("/bloques-ruta/{bloque_ruta_id}/desafio/resultado", tags=["desafío aplicado"])
def resultado_desafio(bloque_ruta_id: UUID, cuerpo: DesafioResuelto,
                      yo: UUID = Depends(colaborador_actual)):
    """
    Corrige el desafío **en el servidor** y abre la evaluación reforzada.

    Da XP lúdico y nada más: ni medalla ni XP acreditable, ni siquiera con las
    tres decisiones correctas. La medalla gold sigue naciendo únicamente del
    intento de evaluación aprobado al 85%.
    """
    _bloque_propio(bloque_ruta_id, yo)
    with pool.connection() as conn:
        try:
            r = resolver_desafio(
                conn, colaborador_id=yo, bloque_ruta_id=bloque_ruta_id,
                respuestas=[x.model_dump() for x in cuerpo.respuestas],
            )
        except NoCritica as e:
            raise HTTPException(409, str(e))
        except LookupError as e:
            raise HTTPException(404, str(e))
    return {
        "total": r.total,
        "aciertos": r.aciertos,
        "perfecto": r.perfecto,
        "xp_otorgado": r.xp_otorgado,
        "ya_resuelto": r.ya_resuelto,
        "revelacion": r.revelacion,
    }


@app.post("/bloques-ruta/{bloque_ruta_id}/intentos", tags=["evaluación"])
def crear_intento(bloque_ruta_id: UUID, yo: UUID = Depends(colaborador_actual)):
    """Abre un intento y baraja los ítems. Si ya hay uno abierto y vigente, lo retoma (S-14)."""
    _bloque_propio(bloque_ruta_id, yo)
    with pool.connection() as conn:
        try:
            intento_id = abrir_intento(conn, colaborador_id=yo, bloque_ruta_id=bloque_ruta_id)
        except SinReintentos as e:
            raise HTTPException(409, str(e))
        except ModulosPendientes as e:
            raise HTTPException(409, str(e))
        except DesafioPendiente as e:
            raise HTTPException(409, str(e))
        except LookupError as e:
            raise HTTPException(404, str(e))
        datos = conn.execute(
            "SELECT items_servidos, expira_en, numero_intento FROM intento_evaluacion WHERE id = %s",
            (intento_id,),
        ).fetchone()
    return {
        "intento_id": intento_id,
        "numero_intento": datos[2],
        "items_servidos": datos[0],
        "expira_en": datos[1],
    }


def _intento_propio(intento_id: UUID, yo: UUID) -> None:
    mio = filas(
        "SELECT 1 FROM intento_evaluacion WHERE id = %s AND colaborador_id = %s",
        (intento_id, yo),
    )
    if not mio:
        raise HTTPException(404, "ese intento no es tuyo")


@app.get("/intentos/{intento_id}", tags=["evaluación"])
def ver_intento(intento_id: UUID, yo: UUID = Depends(colaborador_actual)):
    """
    El intento completo: sus ítems **en el orden en que se sirvieron** y las
    respuestas ya guardadas.

    Con esto se retoma donde iba (S-14): si el navegador se cierra a mitad de la
    prueba, al volver está todo. Nunca incluye `indice_correcta`: es la nota que
    respalda la acreditación y la respuesta no viaja jamás.
    """
    _intento_propio(intento_id, yo)

    cab = filas(
        """SELECT ie.id, ie.numero_intento, ie.estado, ie.expira_en, ie.enviado_en,
                  ie.puntaje, ie.aprobado, ie.items_servidos, ie.bloque_ruta_id,
                  ev.umbral_aprobacion, ev.max_reintentos,
                  d.nombre_oficial AS dimension_nombre, bc.nivel_estandar
             FROM intento_evaluacion ie
             JOIN evaluacion ev ON ev.id = ie.evaluacion_id
             JOIN bloque_ruta br ON br.id = ie.bloque_ruta_id
             JOIN bloque_contenido bc ON bc.id = br.bloque_contenido_id
             JOIN dimension d ON d.id = bc.dimension_id
            WHERE ie.id = %s""",
        (intento_id,),
    )[0]

    servidos = [str(x) for x in cab.pop("items_servidos")]
    textos = {
        str(f["item_id"]): f
        for f in filas(
            """SELECT id AS item_id, enunciado, alternativas
                 FROM item_evaluacion WHERE id = ANY(%s::uuid[])""",
            (servidos,),
        )
    }
    guardadas = {
        str(f["item_id"]): f["indice_elegido"]
        for f in filas(
            "SELECT item_id, indice_elegido FROM respuesta_intento WHERE intento_id = %s",
            (intento_id,),
        )
    }

    return {
        **cab,
        # El orden importa: es el barajado de ESTE intento (S-06).
        "items": [textos[i] for i in servidos if i in textos],
        "respuestas": guardadas,
    }


@app.post("/intentos/{intento_id}/respuestas", tags=["evaluación"])
def guardar_respuesta(intento_id: UUID, cuerpo: Respuesta,
                      yo: UUID = Depends(colaborador_actual)):
    """Autosave por respuesta. Una caída al enviar no pierde nada (S-14)."""
    _intento_propio(intento_id, yo)
    with pool.connection() as conn:
        try:
            responder(conn, intento_id=intento_id, item_id=cuerpo.item_id,
                      indice_elegido=cuerpo.indice_elegido)
        except LookupError as e:
            raise HTTPException(404, str(e))
        except Exception as e:
            raise HTTPException(409, str(e))
    return {"guardada": True}


@app.post("/intentos/{intento_id}/cerrar", tags=["evaluación"])
def cerrar(intento_id: UUID, yo: UUID = Depends(colaborador_actual)):
    """
    Corrige, cierra y —solo si corresponde— otorga.

    Es la **única** ruta de código que puede producir una insignia, y aun así la base
    impone el invariante por su cuenta. Idempotente: apretar dos veces devuelve lo
    mismo y no duplica XP (S-13).
    """
    _intento_propio(intento_id, yo)
    with pool.connection() as conn:
        try:
            r = cerrar_intento(conn, intento_id=intento_id)
        except LookupError as e:
            raise HTTPException(404, str(e))
    return {
        "aprobado": r.aprobado,
        "puntaje": r.puntaje,
        "insignia_id": r.insignia_id,
        "xp_otorgado": r.xp_otorgado,
        "reintentos_restantes": r.reintentos_restantes,
    }
