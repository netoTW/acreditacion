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


def _ver_modulos(cliente, token, bloque_ruta_id):
    """La evaluación se rinde después de recorrer el bloque: el servidor lo exige."""
    for m in cliente.get(f"/bloques-ruta/{bloque_ruta_id}/modulos", headers=_cab(token)).json():
        cliente.post(f"/modulos/{m['id']}/completar", headers=_cab(token))


def test_no_se_puede_operar_el_intento_de_otro(cliente, docente, rector):
    ruta_rector = cliente.get("/mi/ruta", headers=_cab(rector)).json()
    _ver_modulos(cliente, rector, ruta_rector[0]["bloque_ruta_id"])
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


# ------------------------------------------------------------------- CORS
# El frontend vive en otro puerto que la API, así que toda llamada del navegador
# es cross-origin. Con el proxy del servidor de desarrollo esto quedaba oculto;
# al contenedorizar la web, la pantalla de Ingreso dejó de cargar.
def test_el_preflight_options_se_responde(cliente):
    r = cliente.options(
        "/auth/dev/colaboradores",
        headers={
            "Origin": "http://localhost:5180",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    assert r.status_code == 200, "el preflight daba 405 sin el middleware de CORS"
    assert r.headers["access-control-allow-origin"] == "http://localhost:5180"
    permitidos = r.headers["access-control-allow-methods"]
    assert "GET" in permitidos and "POST" in permitidos
    cabeceras = r.headers["access-control-allow-headers"].lower()
    assert "authorization" in cabeceras and "content-type" in cabeceras


def test_la_respuesta_trae_la_cabecera_de_origen(cliente):
    r = cliente.get("/auth/dev/colaboradores", headers={"Origin": "http://localhost:5180"})
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == "http://localhost:5180"
    assert len(r.json()) == 3


def test_se_acepta_la_red_local_para_probar_desde_el_telefono(cliente):
    r = cliente.get("/auth/dev/colaboradores", headers={"Origin": "http://192.168.0.27:5180"})
    assert r.headers.get("access-control-allow-origin") == "http://192.168.0.27:5180"


def test_un_origen_externo_no_recibe_la_cabecera(cliente):
    r = cliente.get("/auth/dev/colaboradores", headers={"Origin": "https://sitio-ajeno.cl"})
    assert "access-control-allow-origin" not in r.headers


# ------------------------------------------------- D1b · bloque y módulos
def test_el_bloque_trae_modulos_evaluacion_y_medalla(cliente, docente):
    ruta = cliente.get("/mi/ruta", headers=_cab(docente)).json()
    b = cliente.get(f"/bloques-ruta/{ruta[0]['bloque_ruta_id']}", headers=_cab(docente)).json()

    assert b["dimension"] == "DOCENCIA" and b["nivel_estandar"] == 3
    assert len(b["modulos"]) == 4
    assert {m["nivel_estandar_origen"] for m in b["modulos"]} == {1, 2, 3}
    assert b["medalla_xp"] == 400 and float(b["umbral_aprobacion"]) == 0.8
    assert b["modulos_completos"] == 0
    assert b["evaluacion_disponible"] is False, "la evaluación no se abre sin ver los módulos"


def test_completar_modulos_abre_la_evaluacion_y_suma_xp_una_vez(cliente, docente):
    ruta = cliente.get("/mi/ruta", headers=_cab(docente)).json()
    bid = ruta[0]["bloque_ruta_id"]
    b = cliente.get(f"/bloques-ruta/{bid}", headers=_cab(docente)).json()

    antes = cliente.get("/mi/estado", headers=_cab(docente)).json()["xp_acreditable"]
    for m in b["modulos"]:
        r = cliente.post(f"/modulos/{m['id']}/completar", headers=_cab(docente)).json()
        assert r["ya_estaba"] is False and r["xp_otorgado"] == 100

    # marcar de nuevo no vuelve a pagar
    repetido = cliente.post(f"/modulos/{b['modulos'][0]['id']}/completar", headers=_cab(docente)).json()
    assert repetido["ya_estaba"] is True and repetido["xp_otorgado"] == 0

    despues = cliente.get("/mi/estado", headers=_cab(docente)).json()
    assert despues["xp_acreditable"] == antes + 400
    assert despues["insignias"] == 0, "ver módulos no otorga insignia"

    b2 = cliente.get(f"/bloques-ruta/{bid}", headers=_cab(docente)).json()
    assert b2["modulos_completos"] == 4 and b2["evaluacion_disponible"] is True


def test_no_se_puede_completar_un_modulo_de_otro_cargo(cliente, docente, rector):
    ruta_rector = cliente.get("/mi/ruta", headers=_cab(rector)).json()
    ajeno = cliente.get(
        f"/bloques-ruta/{ruta_rector[0]['bloque_ruta_id']}/modulos", headers=_cab(rector)
    ).json()[0]
    r = cliente.post(f"/modulos/{ajeno['id']}/completar", headers=_cab(docente))
    assert r.status_code == 404


def test_aprobar_un_bloque_abre_el_siguiente(cliente, rector):
    """Sin esto la ruta queda con un solo bloque abierto para siempre."""
    ruta = cliente.get("/mi/ruta", headers=_cab(rector)).json()
    primero, segundo = ruta[0], ruta[1]
    assert segundo["estado"] == "bloqueado"
    _ver_modulos(cliente, rector, primero["bloque_ruta_id"])

    clave = {c["item_id"]: c["indice_correcta"] for c in cliente.get(
        f"/bloques-ruta/{primero['bloque_ruta_id']}/clave-de-respuestas", headers=_cab(rector)
    ).json()}
    intento = cliente.post(
        f"/bloques-ruta/{primero['bloque_ruta_id']}/intentos", headers=_cab(rector)
    ).json()
    for item in intento["items_servidos"]:
        cliente.post(f"/intentos/{intento['intento_id']}/respuestas", headers=_cab(rector),
                     json={"item_id": item, "indice_elegido": clave[item]})
    assert cliente.post(f"/intentos/{intento['intento_id']}/cerrar",
                        headers=_cab(rector)).json()["aprobado"] is True

    ruta2 = cliente.get("/mi/ruta", headers=_cab(rector)).json()
    assert ruta2[0]["estado"] == "completo"
    assert ruta2[1]["estado"] == "disponible", "el bloque siguiente debe abrirse"


# ------------------------------------------------ D2 · quiz formativo
def test_el_quiz_entrega_la_respuesta_para_dar_feedback(cliente, docente):
    """A diferencia del banco de la evaluación, acá la correcta SÍ viaja: es formativo."""
    ruta = cliente.get("/mi/ruta", headers=_cab(docente)).json()
    mod = cliente.get(
        f"/bloques-ruta/{ruta[0]['bloque_ruta_id']}/modulos", headers=_cab(docente)
    ).json()[0]

    items = cliente.get(f"/modulos/{mod['id']}/quiz", headers=_cab(docente)).json()
    assert len(items) >= 3
    for i in items:
        assert 0 <= i["indice_correcta"] <= 3
        assert len(i["alternativas"]) == 4 and len(i["explicaciones"]) == 4


def test_el_quiz_de_otro_cargo_no_se_sirve(cliente, docente, rector):
    ruta_rector = cliente.get("/mi/ruta", headers=_cab(rector)).json()
    ajeno = cliente.get(
        f"/bloques-ruta/{ruta_rector[0]['bloque_ruta_id']}/modulos", headers=_cab(rector)
    ).json()[0]
    assert cliente.get(f"/modulos/{ajeno['id']}/quiz", headers=_cab(docente)).status_code == 404


def test_el_servidor_recalcula_racha_y_xp(cliente, docente):
    """El cliente manda qué eligió; los aciertos, la racha y el XP los pone el servidor."""
    ruta = cliente.get("/mi/ruta", headers=_cab(docente)).json()
    mod = cliente.get(
        f"/bloques-ruta/{ruta[0]['bloque_ruta_id']}/modulos", headers=_cab(docente)
    ).json()[0]
    items = cliente.get(f"/modulos/{mod['id']}/quiz", headers=_cab(docente)).json()

    # Todo correcto: la racha crece y el XP es 30 + 40 + 50 + …
    respuestas = [{"item_id": i["id"], "indice_elegido": i["indice_correcta"]} for i in items]
    r = cliente.post(f"/modulos/{mod['id']}/quiz/resultado", headers=_cab(docente),
                     json={"respuestas": respuestas}).json()

    esperado = sum(20 + (n + 1) * 10 for n in range(len(items)))
    assert r["aciertos"] == len(items)
    assert r["mejor_racha"] == len(items)
    assert r["xp_otorgado"] == esperado


def test_el_xp_del_quiz_es_ludico_y_no_mueve_el_escalon(cliente, docente):
    """Jugar no puede acercar a nadie a una medalla ni subirlo de escalón (S-04)."""
    antes = cliente.get("/mi/estado", headers=_cab(docente)).json()
    ruta = cliente.get("/mi/ruta", headers=_cab(docente)).json()
    mod = cliente.get(
        f"/bloques-ruta/{ruta[0]['bloque_ruta_id']}/modulos", headers=_cab(docente)
    ).json()[1]
    items = cliente.get(f"/modulos/{mod['id']}/quiz", headers=_cab(docente)).json()

    cliente.post(f"/modulos/{mod['id']}/quiz/resultado", headers=_cab(docente),
                 json={"respuestas": [{"item_id": i["id"], "indice_elegido": i["indice_correcta"]}
                                      for i in items]})

    despues = cliente.get("/mi/estado", headers=_cab(docente)).json()
    assert despues["xp_acreditable"] == antes["xp_acreditable"], "el quiz no da XP acreditable"
    assert despues["xp_total"] > antes["xp_total"], "sí suma al total, que es lo que ve el ranking"
    assert despues["insignias"] == antes["insignias"]


def test_repetir_el_quiz_el_mismo_dia_no_vuelve_a_pagar(cliente, docente):
    ruta = cliente.get("/mi/ruta", headers=_cab(docente)).json()
    mod = cliente.get(
        f"/bloques-ruta/{ruta[0]['bloque_ruta_id']}/modulos", headers=_cab(docente)
    ).json()[2]
    items = cliente.get(f"/modulos/{mod['id']}/quiz", headers=_cab(docente)).json()
    cuerpo = {"respuestas": [{"item_id": i["id"], "indice_elegido": i["indice_correcta"]}
                            for i in items]}

    primero = cliente.post(f"/modulos/{mod['id']}/quiz/resultado", headers=_cab(docente),
                           json=cuerpo).json()
    segundo = cliente.post(f"/modulos/{mod['id']}/quiz/resultado", headers=_cab(docente),
                           json=cuerpo).json()

    assert primero["xp_otorgado"] > 0
    assert segundo["xp_otorgado"] == 0 and segundo["ya_jugado_hoy"] is True
    assert segundo["aciertos"] == primero["aciertos"], "el resultado igual se informa"


def test_una_racha_rota_reduce_el_xp(cliente, docente):
    """Fallar en medio corta el multiplicador: es la mecánica de la cáscara."""
    ruta = cliente.get("/mi/ruta", headers=_cab(docente)).json()
    mod = cliente.get(
        f"/bloques-ruta/{ruta[0]['bloque_ruta_id']}/modulos", headers=_cab(docente)
    ).json()[3]
    items = cliente.get(f"/modulos/{mod['id']}/quiz", headers=_cab(docente)).json()

    respuestas = []
    for n, i in enumerate(items):
        elegido = i["indice_correcta"] if n != 1 else (i["indice_correcta"] + 1) % 4
        respuestas.append({"item_id": i["id"], "indice_elegido": elegido})

    r = cliente.post(f"/modulos/{mod['id']}/quiz/resultado", headers=_cab(docente),
                     json={"respuestas": respuestas}).json()
    assert r["aciertos"] == len(items) - 1
    assert r["mejor_racha"] < len(items), "la racha se cortó en el fallo"


# --------------------------------------------- D2b · evaluación final
def test_la_evaluacion_exige_haber_visto_los_modulos(cliente, rector):
    """No basta con que la pantalla lo esconda: el servidor lo rechaza."""
    ruta = cliente.get("/mi/ruta", headers=_cab(rector)).json()
    pendiente = next(b for b in ruta if b["estado"] != "completo")
    r = cliente.post(f"/bloques-ruta/{pendiente['bloque_ruta_id']}/intentos", headers=_cab(rector))
    assert r.status_code == 409
    assert "módulos" in r.json()["detail"]


def test_el_intento_se_retoma_con_lo_ya_respondido(cliente, docente):
    """S-14: si el navegador se cierra a mitad de la prueba, al volver está todo."""
    ruta = cliente.get("/mi/ruta", headers=_cab(docente)).json()
    bid = ruta[0]["bloque_ruta_id"]
    _ver_modulos(cliente, docente, bid)

    intento = cliente.post(f"/bloques-ruta/{bid}/intentos", headers=_cab(docente)).json()
    detalle = cliente.get(f"/intentos/{intento['intento_id']}", headers=_cab(docente)).json()
    assert len(detalle["items"]) == 5
    assert detalle["respuestas"] == {}
    for i in detalle["items"]:
        assert "indice_correcta" not in i, "la respuesta no viaja jamás en la evaluación"

    primero = detalle["items"][0]["item_id"]
    cliente.post(f"/intentos/{intento['intento_id']}/respuestas", headers=_cab(docente),
                 json={"item_id": primero, "indice_elegido": 2})

    # "recargar": se vuelve a abrir y debe devolver EL MISMO intento, con la respuesta
    otra_vez = cliente.post(f"/bloques-ruta/{bid}/intentos", headers=_cab(docente)).json()
    assert otra_vez["intento_id"] == intento["intento_id"]
    retomado = cliente.get(f"/intentos/{intento['intento_id']}", headers=_cab(docente)).json()
    assert retomado["respuestas"][primero] == 2
    assert [i["item_id"] for i in retomado["items"]] == [i["item_id"] for i in detalle["items"]]


def test_el_canario_en_la_api_reprobar_no_deja_nada(cliente, docente):
    ruta = cliente.get("/mi/ruta", headers=_cab(docente)).json()
    bid = ruta[0]["bloque_ruta_id"]
    _ver_modulos(cliente, docente, bid)
    antes = cliente.get("/mi/estado", headers=_cab(docente)).json()

    intento = cliente.post(f"/bloques-ruta/{bid}/intentos", headers=_cab(docente)).json()
    clave = {c["item_id"]: c["indice_correcta"] for c in cliente.get(
        f"/bloques-ruta/{bid}/clave-de-respuestas", headers=_cab(docente)).json()}
    for n, item in enumerate(intento["items_servidos"]):
        # solo una correcta de cinco → 20%
        elegido = clave[item] if n == 0 else (clave[item] + 1) % 4
        cliente.post(f"/intentos/{intento['intento_id']}/respuestas", headers=_cab(docente),
                     json={"item_id": item, "indice_elegido": elegido})

    r = cliente.post(f"/intentos/{intento['intento_id']}/cerrar", headers=_cab(docente)).json()
    assert r["aprobado"] is False and r["insignia_id"] is None and r["xp_otorgado"] == 0

    despues = cliente.get("/mi/estado", headers=_cab(docente)).json()
    assert despues["insignias"] == antes["insignias"], "reprobar no otorga insignia"
    assert despues["xp_acreditable"] == antes["xp_acreditable"], "ni XP acreditable"

    bloque = cliente.get(f"/bloques-ruta/{bid}", headers=_cab(docente)).json()
    assert bloque["estado"] != "completo" and bloque["obtenida"] == 0


def test_aprobar_al_umbral_si_otorga_y_deja_respaldo(cliente, docente):
    ruta = cliente.get("/mi/ruta", headers=_cab(docente)).json()
    bid = ruta[0]["bloque_ruta_id"]
    clave = {c["item_id"]: c["indice_correcta"] for c in cliente.get(
        f"/bloques-ruta/{bid}/clave-de-respuestas", headers=_cab(docente)).json()}

    intento = cliente.post(f"/bloques-ruta/{bid}/intentos", headers=_cab(docente)).json()
    for item in intento["items_servidos"]:
        cliente.post(f"/intentos/{intento['intento_id']}/respuestas", headers=_cab(docente),
                     json={"item_id": item, "indice_elegido": clave[item]})

    r = cliente.post(f"/intentos/{intento['intento_id']}/cerrar", headers=_cab(docente)).json()
    assert r["aprobado"] is True and r["insignia_id"] is not None and r["xp_otorgado"] == 400

    insignias = cliente.get("/mi/insignias", headers=_cab(docente)).json()
    assert len(insignias) == 1
    assert insignias[0]["puntaje_del_respaldo"] == 1.0
    assert insignias[0]["numero_intento"] == 2, "la respalda el intento aprobado, el segundo"
