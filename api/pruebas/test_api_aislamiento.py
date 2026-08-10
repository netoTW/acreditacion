"""
I-10 — aislamiento por cargo, en la capa API.

CLAUDE.md §3: «la ruta de un rol no muestra el contenido ni el progreso de otro rol».
Quedó declarado pendiente desde la Tanda 2 porque no se puede verificar en la base:
es una propiedad de los endpoints. Acá se cierra.

Lo que se prueba no es que la UI oculte cosas, sino que **no exista forma de pedirlas**:
ningún endpoint acepta un `colaborador_id` por parámetro, y todo acceso a contenido pasa
por la verificación de que el bloque esté en la ruta de quien pregunta.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import psycopg
import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

DSN = os.environ.get(
    "DATABASE_URL", "postgresql://somoscalidad:somoscalidad@localhost:5433/somoscalidad_test"
)


@pytest.fixture(scope="module")
def cliente():
    os.environ["MODO_DEV"] = "true"
    os.environ.setdefault("DATABASE_URL", DSN)

    with psycopg.connect(DSN, autocommit=True) as conn:
        conn.execute("DROP SCHEMA IF EXISTS public CASCADE")
        conn.execute("CREATE SCHEMA public")
        for archivo in sorted((RAIZ / "migraciones").glob("*.sql")):
            conn.execute(archivo.read_text(encoding="utf-8"))
        from seed.sembrar import sembrar
        sembrar(conn)

    from fastapi.testclient import TestClient

    from app import app
    with TestClient(app) as c:
        yield c


def _token(cliente, cargo: str) -> str:
    gente = cliente.get("/auth/dev/colaboradores").json()
    quien = next(p for p in gente if p["cargo"] == cargo)
    r = cliente.post("/auth/dev/actuar-como", json={"colaborador_id": quien["id"]})
    assert r.status_code == 200
    return r.json()["token"]


def _cab(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def docente(cliente):
    return _token(cliente, "Docente")


@pytest.fixture(scope="module")
def rector(cliente):
    return _token(cliente, "Rector")


# ------------------------------------------------------------------ sesión
def test_sin_token_no_se_ve_nada(cliente):
    for url in ("/mi/ruta", "/mi/estado", "/ranking", "/catalogo/dimensiones"):
        assert cliente.get(url).status_code == 401, url


def test_token_manipulado_se_rechaza(cliente, docente):
    partes = docente.split(".")
    falsificado = partes[0] + "." + ("A" * len(partes[1]))
    assert cliente.get("/mi/ruta", headers=_cab(falsificado)).status_code == 401


def test_token_expirado_se_rechaza(cliente):
    from identidad.sesion import emitir
    from uuid import uuid4
    viejo = emitir(uuid4(), proveedor="dev", ahora=time.time() - 100_000)
    assert cliente.get("/mi/ruta", headers=_cab(viejo)).status_code == 401


def test_la_sesion_dice_quien_soy(cliente, docente):
    yo = cliente.get("/auth/yo", headers=_cab(docente)).json()
    assert yo["cargo"] == "Docente"
    assert yo["escalon"] == "Explorador"


# ---------------------------------------------------- I-10 · el aislamiento
def test_i10_no_se_sirve_contenido_de_otro_cargo(cliente, docente, rector):
    """
    El Rector tiene Gestión N3 en su ruta; el Docente tiene Gestión N1. Si el Docente
    pide el bloque del Rector con su id, no puede recibirlo: es contenido de otro cargo,
    a un nivel de exigencia que no le corresponde.
    """
    ruta_rector = cliente.get("/mi/ruta", headers=_cab(rector)).json()
    bloque_ajeno = ruta_rector[0]["bloque_ruta_id"]

    for url in (
        f"/bloques-ruta/{bloque_ajeno}/modulos",
        f"/bloques-ruta/{bloque_ajeno}/evaluacion",
        f"/bloques-ruta/{bloque_ajeno}/clave-de-respuestas",
    ):
        r = cliente.get(url, headers=_cab(docente))
        assert r.status_code == 404, f"{url} devolvió {r.status_code}"

    r = cliente.post(f"/bloques-ruta/{bloque_ajeno}/intentos", headers=_cab(docente))
    assert r.status_code == 404, "no se puede abrir intento sobre el bloque de otro"


def test_i10_responde_404_y_no_403(cliente, docente, rector):
    """
    Un 403 confirmaría que el bloque existe, y eso ya filtra información sobre el
    contenido de otro cargo. La respuesta es indistinguible de un id inventado.
    """
    ajeno = cliente.get("/mi/ruta", headers=_cab(rector)).json()[0]["bloque_ruta_id"]
    inventado = "00000000-0000-4000-8000-000000000000"

    r_ajeno = cliente.get(f"/bloques-ruta/{ajeno}/modulos", headers=_cab(docente))
    r_inventado = cliente.get(f"/bloques-ruta/{inventado}/modulos", headers=_cab(docente))
    assert r_ajeno.status_code == r_inventado.status_code == 404
    assert r_ajeno.json() == r_inventado.json()


def test_lo_propio_si_se_sirve(cliente, docente):
    ruta = cliente.get("/mi/ruta", headers=_cab(docente)).json()
    assert len(ruta) == 5
    assert ruta[0]["dimension"] == "DOCENCIA" and ruta[0]["nivel_estandar"] == 3

    mio = ruta[0]["bloque_ruta_id"]
    modulos = cliente.get(f"/bloques-ruta/{mio}/modulos", headers=_cab(docente))
    assert modulos.status_code == 200 and len(modulos.json()) == 4


def test_la_evaluacion_no_filtra_la_respuesta_correcta(cliente, docente):
    ruta = cliente.get("/mi/ruta", headers=_cab(docente)).json()
    items = cliente.get(
        f"/bloques-ruta/{ruta[0]['bloque_ruta_id']}/evaluacion", headers=_cab(docente)
    ).json()
    assert items
    for i in items:
        assert "indice_correcta" not in i
        assert "explicaciones" not in i


def test_no_se_puede_operar_el_intento_de_otro(cliente, docente, rector):
    ruta_rector = cliente.get("/mi/ruta", headers=_cab(rector)).json()
    intento = cliente.post(
        f"/bloques-ruta/{ruta_rector[0]['bloque_ruta_id']}/intentos", headers=_cab(rector)
    ).json()["intento_id"]

    assert cliente.post(f"/intentos/{intento}/cerrar", headers=_cab(docente)).status_code == 404
    r = cliente.post(
        f"/intentos/{intento}/respuestas",
        headers=_cab(docente),
        json={"item_id": "00000000-0000-4000-8000-000000000000", "indice_elegido": 0},
    )
    assert r.status_code == 404


# ------------------------------------------- permisos institucionales (S-35)
def test_el_panel_de_gestion_pide_permiso_institucional(cliente, docente, rector):
    """El permiso sale de la membresía de comité, no del cargo."""
    assert cliente.get("/colaboradores", headers=_cab(docente)).status_code == 403
    assert cliente.get("/catalogo/contenido", headers=_cab(docente)).status_code == 403

    assert cliente.get("/colaboradores", headers=_cab(rector)).status_code == 200
    assert cliente.get("/catalogo/contenido", headers=_cab(rector)).status_code == 200


def test_el_ranking_es_agregado_y_no_filtra_insignias_ajenas(cliente, docente):
    """S-16: nombre, unidad, XP y conteo. Nunca el nombre de insignias de otro cargo."""
    filas = cliente.get("/ranking", headers=_cab(docente)).json()
    assert len(filas) == 3
    for f in filas:
        assert isinstance(f["insignias"], int)
        assert "medalla" not in f and "insignias_detalle" not in f
