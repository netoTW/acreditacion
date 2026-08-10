"""
API de Somos Calidad.

`/docs` es la primera interfaz de prueba del director (CLAUDE.md §11): con el seed
cargado, se puede recorrer el sistema entero desde el navegador sin frontend.
"""
from __future__ import annotations

import os
from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from psycopg_pool import ConnectionPool
from pydantic import BaseModel, Field

from motor.evaluacion import (
    SinReintentos, abrir_intento, cerrar_intento, responder,
)
from motor.eventos import estado as leer_estado

DSN = os.environ["DATABASE_URL"]
pool = ConnectionPool(DSN, min_size=1, max_size=10, open=True)

app = FastAPI(
    title="Somos Calidad · API",
    version="0.3.0",
    description=(
        "Portal de gamificación de la ruta de acreditación de AIEP.\n\n"
        "El contenido de esta etapa está marcado `es_contenido_prueba` y **no es "
        "material de acreditación oficial**. La estructura —5 dimensiones, 13 hitos, "
        "gobernanza— sí sale de la ruta institucional real."
    ),
)


def filas(sql: str, args: tuple = ()) -> list[dict]:
    with pool.connection() as conn:
        cur = conn.execute(sql, args)
        cols = [c.name for c in cur.description]
        return [dict(zip(cols, f)) for f in cur.fetchall()]


@app.get("/", include_in_schema=False)
def raiz():
    return RedirectResponse("/docs")


@app.get("/salud", tags=["sistema"])
def salud():
    """¿Está viva la API y responde la base?"""
    with pool.connection() as conn:
        conn.execute("SELECT 1")
    return {"ok": True, "servicio": "api"}


# ============================================================ catálogo real
@app.get("/catalogo/dimensiones", tags=["catálogo"])
def dimensiones():
    """Las 5 dimensiones evaluativas de la CNA. Son el esqueleto del contenido."""
    return filas(
        "SELECT codigo, nombre_oficial, obligatoria, orden FROM dimension ORDER BY orden"
    )


@app.get("/catalogo/hitos", tags=["catálogo"])
def hitos():
    """Los 13 hitos de la ruta 2026–2027. H13 no tiene fecha: la fuente dice «por definir»."""
    return filas(
        """SELECT codigo, ruta, anio, periodo_texto, titulo, fecha_inicio, fecha_fin
             FROM hito ORDER BY orden"""
    )


@app.get("/catalogo/cargos", tags=["catálogo"])
def cargos():
    """Los 6 cargos del slice, con cuántas personas los ocupan."""
    return filas(
        """SELECT c.codigo, c.nombre, c.descripcion, count(col.id) AS colaboradores
             FROM cargo c LEFT JOIN colaborador col ON col.cargo_id = c.id
            GROUP BY c.id ORDER BY c.codigo"""
    )


@app.get("/catalogo/matriz", tags=["catálogo"])
def matriz():
    """
    **La matriz Cargo × Dimensión** (ADR-003) — el corazón del modelo.

    30 filas: 6 cargos × 5 dimensiones. Cada cargo toca las 5 con nivel ≥ 1 y se
    diferencia por dónde se le exige profundidad. Gracias al anidamiento de los
    estándares CNA (el nivel 3 incluye al 2 y el 2 al 1), esto se sirve con solo
    **15 unidades de contenido**, no 30.
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
def contenido():
    """Las 15 unidades de contenido (dimensión × nivel) y cuántos cargos las comparten."""
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
def comites():
    """La gobernanza de la fuente. De acá salen los permisos institucionales (S-35)."""
    return filas(
        """SELECT co.tipo, co.nombre, d.codigo AS dimension, u.nombre AS unidad,
                  (SELECT count(*) FROM membresia_comite m WHERE m.comite_id = co.id) AS integrantes
             FROM comite co
             LEFT JOIN dimension d ON d.id = co.dimension_id
             LEFT JOIN unidad u ON u.id = co.unidad_id
            ORDER BY co.tipo, co.nombre"""
    )


# ======================================================== personas y rutas
@app.get("/colaboradores", tags=["colaboradores"])
def colaboradores():
    """Los 3 del slice, con su estado derivado y si tienen permiso institucional."""
    return filas(
        """SELECT c.id, c.email, c.nombre, ca.nombre AS cargo, u.nombre AS unidad,
                  ec.xp_acreditable, ec.xp_total, ec.escalon, ec.insignias,
                  (pi.colaborador_id IS NOT NULL) AS ve_panel_institucional
             FROM colaborador c
             JOIN cargo ca ON ca.id = c.cargo_id
             LEFT JOIN unidad u ON u.id = c.unidad_id
             JOIN estado_colaborador ec ON ec.colaborador_id = c.id
             LEFT JOIN permiso_institucional pi ON pi.colaborador_id = c.id
            ORDER BY c.nombre"""
    )


@app.get("/colaboradores/{colaborador_id}/ruta", tags=["colaboradores"])
def ruta(colaborador_id: UUID):
    """
    La ruta de una persona: 5 bloques, uno por dimensión, cada uno al nivel que le
    exige su cargo y anclado a un hito real del proceso.

    Compara dos cargos distintos acá y se ve la personalización de ADR-003.
    """
    datos = filas(
        """SELECT br.id AS bloque_ruta_id, br.orden, br.estado,
                  d.codigo AS dimension, d.nombre_oficial AS dimension_nombre,
                  bc.nivel_estandar, bc.titulo, bc.es_contenido_prueba,
                  h.codigo AS hito, h.periodo_texto, h.titulo AS hito_titulo,
                  dm.nombre AS medalla, dm.xp AS medalla_xp,
                  (SELECT count(*) FROM modulo m WHERE m.bloque_contenido_id = bc.id) AS modulos
             FROM bloque_ruta br
             JOIN ruta r ON r.id = br.ruta_id
             JOIN bloque_contenido bc ON bc.id = br.bloque_contenido_id
             JOIN dimension d ON d.id = bc.dimension_id
             LEFT JOIN hito h ON h.id = br.hito_id
             LEFT JOIN definicion_medalla dm ON dm.bloque_contenido_id = bc.id
            WHERE r.colaborador_id = %s
            ORDER BY br.orden""",
        (colaborador_id,),
    )
    if not datos:
        raise HTTPException(404, "ese colaborador no tiene ruta")
    return datos


@app.get("/colaboradores/{colaborador_id}/estado", tags=["colaboradores"])
def estado(colaborador_id: UUID):
    """
    Estado DERIVADO. No hay columnas `xp` ni `nivel` que consultar: todo sale de
    los eventos (ADR-005 §3). El escalón usa solo XP acreditable; el ranking, el total.
    """
    with pool.connection() as conn:
        try:
            e = leer_estado(conn, colaborador_id)
        except LookupError:
            raise HTTPException(404, "colaborador inexistente")
    return {
        "xp_acreditable": e.xp_acreditable,
        "xp_total": e.xp_total,
        "escalon": e.escalon,
        "insignias": e.insignias,
    }


@app.get("/colaboradores/{colaborador_id}/insignias", tags=["colaboradores"])
def insignias(colaborador_id: UUID):
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
        (colaborador_id,),
    )


@app.get("/ranking", tags=["colaboradores"])
def ranking():
    """Ranking por XP total, con el desempate de S-15. El escalón usa el acreditable."""
    return filas("SELECT * FROM ranking ORDER BY posicion")


# ============================================================== evaluación
class AbrirIntento(BaseModel):
    colaborador_id: UUID
    bloque_ruta_id: UUID


class Respuesta(BaseModel):
    item_id: UUID
    indice_elegido: int = Field(ge=0, le=3)


@app.get("/bloques-ruta/{bloque_ruta_id}/evaluacion", tags=["evaluación"])
def ver_evaluacion(bloque_ruta_id: UUID):
    """Los ítems del banco. **Sin `indice_correcta`**: la respuesta no viaja al cliente."""
    return filas(
        """SELECT i.id AS item_id, i.enunciado, i.alternativas
             FROM item_evaluacion i
             JOIN evaluacion ev ON ev.id = i.evaluacion_id
             JOIN bloque_ruta br ON br.bloque_contenido_id = ev.bloque_contenido_id
            WHERE br.id = %s ORDER BY i.enunciado""",
        (bloque_ruta_id,),
    )


@app.get("/bloques-ruta/{bloque_ruta_id}/clave-de-respuestas", tags=["evaluación"])
def clave_de_respuestas(bloque_ruta_id: UUID):
    """
    **Solo para verificar el slice desde `/docs`.** Devuelve la alternativa correcta.

    Doble candado: exige `MODO_DEV=true` **y** que el bloque esté marcado
    `es_contenido_prueba`. Sobre contenido real de acreditación responde 403 aunque
    el modo dev esté encendido. Se elimina antes de producción (tarea D8).
    """
    if os.environ.get("MODO_DEV", "").lower() != "true":
        raise HTTPException(403, "solo disponible con MODO_DEV=true")

    es_prueba = filas(
        """SELECT bc.es_contenido_prueba
             FROM bloque_ruta br JOIN bloque_contenido bc ON bc.id = br.bloque_contenido_id
            WHERE br.id = %s""",
        (bloque_ruta_id,),
    )
    if not es_prueba:
        raise HTTPException(404, "bloque de ruta inexistente")
    if not es_prueba[0]["es_contenido_prueba"]:
        raise HTTPException(403, "este bloque tiene contenido real: la clave no se revela")

    return filas(
        """SELECT i.id AS item_id, i.enunciado, i.indice_correcta
             FROM item_evaluacion i
             JOIN evaluacion ev ON ev.id = i.evaluacion_id
             JOIN bloque_ruta br ON br.bloque_contenido_id = ev.bloque_contenido_id
            WHERE br.id = %s ORDER BY i.enunciado""",
        (bloque_ruta_id,),
    )


@app.post("/intentos", tags=["evaluación"])
def crear_intento(cuerpo: AbrirIntento):
    """Abre un intento y baraja los ítems. Si ya hay uno abierto y vigente, lo retoma (S-14)."""
    with pool.connection() as conn:
        try:
            intento_id = abrir_intento(
                conn, colaborador_id=cuerpo.colaborador_id, bloque_ruta_id=cuerpo.bloque_ruta_id
            )
        except SinReintentos as e:
            raise HTTPException(409, str(e))
        except LookupError as e:
            raise HTTPException(404, str(e))
        servidos = conn.execute(
            "SELECT items_servidos, expira_en, numero_intento FROM intento_evaluacion WHERE id = %s",
            (intento_id,),
        ).fetchone()
    return {
        "intento_id": intento_id,
        "numero_intento": servidos[2],
        "items_servidos": servidos[0],
        "expira_en": servidos[1],
    }


@app.post("/intentos/{intento_id}/respuestas", tags=["evaluación"])
def guardar_respuesta(intento_id: UUID, cuerpo: Respuesta):
    """Autosave por respuesta. Una caída al enviar no pierde nada (S-14)."""
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
def cerrar(intento_id: UUID):
    """
    Corrige, cierra y —solo si corresponde— otorga.

    Es la **única** ruta de código que puede producir una insignia, y aun así la
    base impone el invariante por su cuenta. Idempotente: apretar dos veces
    devuelve lo mismo y no duplica XP (S-13).
    """
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
