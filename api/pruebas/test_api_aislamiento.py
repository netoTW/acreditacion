"""
I-10 — aislamiento por rol, en la capa API.

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
def apoyo(cliente):
    return _token(cliente, "Nivel 3 · Administrativo y apoyo")


@pytest.fixture(scope="module")
def direccion(cliente):
    return _token(cliente, "Nivel 1 · Alta Dirección")


# ------------------------------------------------------------------ sesión
def test_sin_token_no_se_ve_nada(cliente):
    for url in ("/mi/ruta", "/mi/estado", "/ranking", "/catalogo/dimensiones"):
        assert cliente.get(url).status_code == 401, url


def test_token_manipulado_se_rechaza(cliente, apoyo):
    partes = apoyo.split(".")
    falsificado = partes[0] + "." + ("A" * len(partes[1]))
    assert cliente.get("/mi/ruta", headers=_cab(falsificado)).status_code == 401


def test_token_expirado_se_rechaza(cliente):
    from identidad.sesion import emitir
    from uuid import uuid4
    viejo = emitir(uuid4(), proveedor="dev", ahora=time.time() - 100_000)
    assert cliente.get("/mi/ruta", headers=_cab(viejo)).status_code == 401


def test_la_sesion_dice_quien_soy(cliente, apoyo):
    yo = cliente.get("/auth/yo", headers=_cab(apoyo)).json()
    assert yo["cargo"] == "Nivel 3 · Administrativo y apoyo"
    assert yo["escalon"] == "Explorador"


# ---------------------------------------------------- I-10 · el aislamiento
def test_i10_no_se_sirve_contenido_de_otro_cargo(cliente, apoyo, direccion):
    """
    Alta Dirección tiene Gestión al nivel 3; Administrativo y apoyo la tiene al 2. Si el segundo
    pide el bloque del primero con su id, no puede recibirlo: es contenido de otro rol,
    a un nivel de exigencia que no le corresponde.
    """
    ruta_direccion = cliente.get("/mi/ruta", headers=_cab(direccion)).json()
    bloque_ajeno = ruta_direccion[0]["bloque_ruta_id"]

    for url in (
        f"/bloques-ruta/{bloque_ajeno}/modulos",
        f"/bloques-ruta/{bloque_ajeno}/evaluacion",
        f"/bloques-ruta/{bloque_ajeno}/clave-de-respuestas",
    ):
        r = cliente.get(url, headers=_cab(apoyo))
        assert r.status_code == 404, f"{url} devolvió {r.status_code}"

    r = cliente.post(f"/bloques-ruta/{bloque_ajeno}/intentos", headers=_cab(apoyo))
    assert r.status_code == 404, "no se puede abrir intento sobre el bloque de otro"


def test_i10_responde_404_y_no_403(cliente, apoyo, direccion):
    """
    Un 403 confirmaría que el bloque existe, y eso ya filtra información sobre el
    contenido de otro rol. La respuesta es indistinguible de un id inventado.
    """
    ajeno = cliente.get("/mi/ruta", headers=_cab(direccion)).json()[0]["bloque_ruta_id"]
    inventado = "00000000-0000-4000-8000-000000000000"

    r_ajeno = cliente.get(f"/bloques-ruta/{ajeno}/modulos", headers=_cab(apoyo))
    r_inventado = cliente.get(f"/bloques-ruta/{inventado}/modulos", headers=_cab(apoyo))
    assert r_ajeno.status_code == r_inventado.status_code == 404
    assert r_ajeno.json() == r_inventado.json()


def test_lo_propio_si_se_sirve(cliente, apoyo):
    """La ruta abre por donde el rol más impacta: Aseguramiento, 35% y crítica."""
    ruta = cliente.get("/mi/ruta", headers=_cab(apoyo)).json()
    assert len(ruta) == 5
    assert ruta[0]["dimension"] == "CALIDAD" and ruta[0]["nivel_estandar"] == 3
    assert ruta[0]["es_critica"] is True
    assert float(ruta[0]["peso_ranking"]) == 0.35

    mio = ruta[0]["bloque_ruta_id"]
    modulos = cliente.get(f"/bloques-ruta/{mio}/modulos", headers=_cab(apoyo))
    # La estructura es la misma en las cinco dimensiones: 2 módulos, siempre.
    assert modulos.status_code == 200 and len(modulos.json()) == 2


def test_la_evaluacion_no_filtra_la_respuesta_correcta(cliente, apoyo):
    ruta = cliente.get("/mi/ruta", headers=_cab(apoyo)).json()
    items = cliente.get(
        f"/bloques-ruta/{ruta[0]['bloque_ruta_id']}/evaluacion", headers=_cab(apoyo)
    ).json()
    assert items
    for i in items:
        assert "indice_correcta" not in i
        assert "explicaciones" not in i


def _ver_modulos(cliente, token, bloque_ruta_id):
    """
    Deja el bloque listo para rendir: el servidor exige recorrerlo antes.

    En una dimensión crítica no basta con los módulos —hay que resolver además el
    desafío aplicado—, así que este ayudante lo resuelve. Da igual si se acierta:
    el requisito es haberlo enfrentado, y la medalla sigue dependiendo del 85%.
    """
    for m in cliente.get(f"/bloques-ruta/{bloque_ruta_id}/modulos", headers=_cab(token)).json():
        cliente.post(f"/modulos/{m['id']}/completar", headers=_cab(token))

    caso = cliente.get(f"/bloques-ruta/{bloque_ruta_id}/desafio", headers=_cab(token))
    if caso.status_code == 200:
        cliente.post(
            f"/bloques-ruta/{bloque_ruta_id}/desafio/resultado", headers=_cab(token),
            json={"respuestas": [
                {"decision_id": d["decision_id"], "respuesta": d["opciones"][0]["clave"]}
                for d in caso.json()["decisiones"]
            ]},
        )


def test_no_se_puede_operar_el_intento_de_otro(cliente, apoyo, direccion):
    ruta_direccion = cliente.get("/mi/ruta", headers=_cab(direccion)).json()
    _ver_modulos(cliente, direccion, ruta_direccion[0]["bloque_ruta_id"])
    intento = cliente.post(
        f"/bloques-ruta/{ruta_direccion[0]['bloque_ruta_id']}/intentos", headers=_cab(direccion)
    ).json()["intento_id"]

    assert cliente.post(f"/intentos/{intento}/cerrar", headers=_cab(apoyo)).status_code == 404
    r = cliente.post(
        f"/intentos/{intento}/respuestas",
        headers=_cab(apoyo),
        json={"item_id": "00000000-0000-4000-8000-000000000000", "indice_elegido": 0},
    )
    assert r.status_code == 404


# ------------------------------------------- permisos institucionales (S-35)
def test_el_panel_de_gestion_pide_permiso_institucional(cliente, apoyo, direccion):
    """El permiso sale de la membresía de comité, no del rol."""
    assert cliente.get("/colaboradores", headers=_cab(apoyo)).status_code == 403
    assert cliente.get("/catalogo/contenido", headers=_cab(apoyo)).status_code == 403

    assert cliente.get("/colaboradores", headers=_cab(direccion)).status_code == 200
    assert cliente.get("/catalogo/contenido", headers=_cab(direccion)).status_code == 200


def test_el_ranking_es_agregado_y_no_filtra_insignias_ajenas(cliente, apoyo):
    """S-16: nombre, unidad, XP y conteo. Nunca el nombre de insignias de otro cargo."""
    filas = cliente.get("/ranking", headers=_cab(apoyo)).json()
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
def test_el_bloque_trae_modulos_evaluacion_y_medalla(cliente, apoyo):
    ruta = cliente.get("/mi/ruta", headers=_cab(apoyo)).json()
    b = cliente.get(f"/bloques-ruta/{ruta[0]['bloque_ruta_id']}", headers=_cab(apoyo)).json()

    # Aseguramiento es la dimensión crítica de este rol: 35%, nivel 3, gold y 85%.
    assert b["dimension"] == "CALIDAD" and b["nivel_estandar"] == 3
    assert b["es_critica"] is True
    assert len(b["modulos"]) == 2, "la estructura es la misma en las cinco dimensiones"
    assert [m["nivel_estandar_origen"] for m in b["modulos"]] == [1, 3]
    assert b["medalla_tipo"] == "gold" and b["medalla_xp"] == 600
    assert float(b["umbral_aprobacion"]) == 0.85, "la crítica exige más que el 80%"
    assert b["modulos_completos"] == 0
    assert b["desafio_pendiente"] is True
    assert b["evaluacion_disponible"] is False, "la evaluación no se abre sin ver los módulos"


def test_una_dimension_estandar_lleva_silver_al_80_y_sin_desafio(cliente, apoyo):
    """El contraste: mismo esqueleto, menos exigencia. Investigación pesa 5% en N3."""
    ruta = cliente.get("/mi/ruta", headers=_cab(apoyo)).json()
    estandar = next(x for x in ruta if x["dimension"] == "ICI")
    b = cliente.get(f"/bloques-ruta/{estandar['bloque_ruta_id']}", headers=_cab(apoyo)).json()

    assert b["es_critica"] is False
    assert len(b["modulos"]) == 2, "la estructura NO cambia: cambia la profundidad"
    assert b["medalla_tipo"] == "silver" and float(b["umbral_aprobacion"]) == 0.8
    assert b["desafio_pendiente"] is False
    # Y el desafío ni siquiera existe acá: no es que falte, es que no lleva.
    assert cliente.get(
        f"/bloques-ruta/{estandar['bloque_ruta_id']}/desafio", headers=_cab(apoyo)
    ).status_code == 409


def test_completar_modulos_abre_la_evaluacion_y_suma_xp_una_vez(cliente, apoyo):
    ruta = cliente.get("/mi/ruta", headers=_cab(apoyo)).json()
    bid = ruta[0]["bloque_ruta_id"]
    b = cliente.get(f"/bloques-ruta/{bid}", headers=_cab(apoyo)).json()

    antes = cliente.get("/mi/estado", headers=_cab(apoyo)).json()["xp_acreditable"]
    for m in b["modulos"]:
        r = cliente.post(f"/modulos/{m['id']}/completar", headers=_cab(apoyo)).json()
        assert r["ya_estaba"] is False and r["xp_otorgado"] == 100

    # marcar de nuevo no vuelve a pagar
    repetido = cliente.post(f"/modulos/{b['modulos'][0]['id']}/completar", headers=_cab(apoyo)).json()
    assert repetido["ya_estaba"] is True and repetido["xp_otorgado"] == 0

    despues = cliente.get("/mi/estado", headers=_cab(apoyo)).json()
    assert despues["xp_acreditable"] == antes + 200
    assert despues["insignias"] == 0, "ver módulos no otorga insignia"

    # Bloque crítico: con los módulos vistos la evaluación TODAVÍA no se abre.
    b2 = cliente.get(f"/bloques-ruta/{bid}", headers=_cab(apoyo)).json()
    assert b2["modulos_completos"] == 2
    assert b2["evaluacion_disponible"] is False, "falta el desafío aplicado"

    caso = cliente.get(f"/bloques-ruta/{bid}/desafio", headers=_cab(apoyo)).json()
    cliente.post(
        f"/bloques-ruta/{bid}/desafio/resultado", headers=_cab(apoyo),
        json={"respuestas": [
            {"decision_id": d["decision_id"], "respuesta": d["opciones"][0]["clave"]}
            for d in caso["decisiones"]
        ]},
    )
    b3 = cliente.get(f"/bloques-ruta/{bid}", headers=_cab(apoyo)).json()
    assert b3["evaluacion_disponible"] is True


def test_no_se_puede_completar_un_modulo_de_otro_cargo(cliente, apoyo, direccion):
    ruta_direccion = cliente.get("/mi/ruta", headers=_cab(direccion)).json()
    ajeno = cliente.get(
        f"/bloques-ruta/{ruta_direccion[0]['bloque_ruta_id']}/modulos", headers=_cab(direccion)
    ).json()[0]
    r = cliente.post(f"/modulos/{ajeno['id']}/completar", headers=_cab(apoyo))
    assert r.status_code == 404


def test_aprobar_un_bloque_abre_el_siguiente(cliente, direccion):
    """Sin esto la ruta queda con un solo bloque abierto para siempre."""
    ruta = cliente.get("/mi/ruta", headers=_cab(direccion)).json()
    primero, segundo = ruta[0], ruta[1]
    assert segundo["estado"] == "bloqueado"
    _ver_modulos(cliente, direccion, primero["bloque_ruta_id"])

    clave = {c["item_id"]: c["indice_correcta"] for c in cliente.get(
        f"/bloques-ruta/{primero['bloque_ruta_id']}/clave-de-respuestas", headers=_cab(direccion)
    ).json()}
    intento = cliente.post(
        f"/bloques-ruta/{primero['bloque_ruta_id']}/intentos", headers=_cab(direccion)
    ).json()
    for item in intento["items_servidos"]:
        cliente.post(f"/intentos/{intento['intento_id']}/respuestas", headers=_cab(direccion),
                     json={"item_id": item, "indice_elegido": clave[item]})
    assert cliente.post(f"/intentos/{intento['intento_id']}/cerrar",
                        headers=_cab(direccion)).json()["aprobado"] is True

    ruta2 = cliente.get("/mi/ruta", headers=_cab(direccion)).json()
    assert ruta2[0]["estado"] == "completo"
    assert ruta2[1]["estado"] == "disponible", "el bloque siguiente debe abrirse"


# ------------------------------------------------ D2 · quiz formativo
def test_el_quiz_entrega_la_respuesta_para_dar_feedback(cliente, apoyo):
    """A diferencia del banco de la evaluación, acá la correcta SÍ viaja: es formativo."""
    ruta = cliente.get("/mi/ruta", headers=_cab(apoyo)).json()
    mod = cliente.get(
        f"/bloques-ruta/{ruta[0]['bloque_ruta_id']}/modulos", headers=_cab(apoyo)
    ).json()[0]

    items = cliente.get(f"/modulos/{mod['id']}/quiz", headers=_cab(apoyo)).json()
    assert len(items) >= 3
    for i in items:
        assert 0 <= i["indice_correcta"] <= 3
        assert len(i["alternativas"]) == 4 and len(i["explicaciones"]) == 4


def test_el_quiz_de_otro_cargo_no_se_sirve(cliente, apoyo, direccion):
    ruta_direccion = cliente.get("/mi/ruta", headers=_cab(direccion)).json()
    ajeno = cliente.get(
        f"/bloques-ruta/{ruta_direccion[0]['bloque_ruta_id']}/modulos", headers=_cab(direccion)
    ).json()[0]
    assert cliente.get(f"/modulos/{ajeno['id']}/quiz", headers=_cab(apoyo)).status_code == 404


def test_el_servidor_recalcula_racha_y_xp(cliente, apoyo):
    """El cliente manda qué eligió; los aciertos, la racha y el XP los pone el servidor."""
    ruta = cliente.get("/mi/ruta", headers=_cab(apoyo)).json()
    mod = cliente.get(
        f"/bloques-ruta/{ruta[0]['bloque_ruta_id']}/modulos", headers=_cab(apoyo)
    ).json()[0]
    items = cliente.get(f"/modulos/{mod['id']}/quiz", headers=_cab(apoyo)).json()

    # Todo correcto: la racha crece y el XP es 30 + 40 + 50 + …
    respuestas = [{"item_id": i["id"], "indice_elegido": i["indice_correcta"]} for i in items]
    r = cliente.post(f"/modulos/{mod['id']}/quiz/resultado", headers=_cab(apoyo),
                     json={"respuestas": respuestas}).json()

    esperado = sum(20 + (n + 1) * 10 for n in range(len(items)))
    assert r["aciertos"] == len(items)
    assert r["mejor_racha"] == len(items)
    assert r["xp_otorgado"] == esperado


def test_el_xp_del_quiz_es_ludico_y_no_mueve_el_escalon(cliente, apoyo):
    """Jugar no puede acercar a nadie a una medalla ni subirlo de escalón (S-04)."""
    antes = cliente.get("/mi/estado", headers=_cab(apoyo)).json()
    mod, items = _items_quiz(cliente, apoyo, 1)

    cliente.post(f"/modulos/{mod['id']}/quiz/resultado", headers=_cab(apoyo),
                 json={"respuestas": [{"item_id": i["id"], "indice_elegido": i["indice_correcta"]}
                                      for i in items]})

    despues = cliente.get("/mi/estado", headers=_cab(apoyo)).json()
    assert despues["xp_acreditable"] == antes["xp_acreditable"], "el quiz no da XP acreditable"
    assert despues["xp_total"] > antes["xp_total"], "sí suma al total, que es lo que ve el ranking"
    assert despues["insignias"] == antes["insignias"]


def test_repetir_el_quiz_el_mismo_dia_no_vuelve_a_pagar(cliente, apoyo):
    mod, items = _items_quiz(cliente, apoyo, 2)
    cuerpo = {"respuestas": [{"item_id": i["id"], "indice_elegido": i["indice_correcta"]}
                            for i in items]}

    primero = cliente.post(f"/modulos/{mod['id']}/quiz/resultado", headers=_cab(apoyo),
                           json=cuerpo).json()
    segundo = cliente.post(f"/modulos/{mod['id']}/quiz/resultado", headers=_cab(apoyo),
                           json=cuerpo).json()

    assert primero["xp_otorgado"] > 0
    assert segundo["xp_otorgado"] == 0 and segundo["ya_jugado_hoy"] is True
    assert segundo["aciertos"] == primero["aciertos"], "el resultado igual se informa"


def test_una_racha_rota_reduce_el_xp(cliente, apoyo):
    """Fallar en medio corta el multiplicador: es la mecánica de la cáscara."""
    mod, items = _items_quiz(cliente, apoyo, 3)

    respuestas = []
    for n, i in enumerate(items):
        elegido = i["indice_correcta"] if n != 1 else (i["indice_correcta"] + 1) % 4
        respuestas.append({"item_id": i["id"], "indice_elegido": elegido})

    r = cliente.post(f"/modulos/{mod['id']}/quiz/resultado", headers=_cab(apoyo),
                     json={"respuestas": respuestas}).json()
    assert r["aciertos"] == len(items) - 1
    assert r["mejor_racha"] < len(items), "la racha se cortó en el fallo"


# --------------------------------------------- D2b · evaluación final
def test_la_evaluacion_exige_haber_visto_los_modulos(cliente, direccion):
    """No basta con que la pantalla lo esconda: el servidor lo rechaza."""
    ruta = cliente.get("/mi/ruta", headers=_cab(direccion)).json()
    pendiente = next(b for b in ruta if b["estado"] != "completo")
    r = cliente.post(f"/bloques-ruta/{pendiente['bloque_ruta_id']}/intentos", headers=_cab(direccion))
    assert r.status_code == 409
    assert "módulos" in r.json()["detail"]


def test_el_intento_se_retoma_con_lo_ya_respondido(cliente, apoyo):
    """S-14: si el navegador se cierra a mitad de la prueba, al volver está todo."""
    ruta = cliente.get("/mi/ruta", headers=_cab(apoyo)).json()
    bid = ruta[0]["bloque_ruta_id"]
    _ver_modulos(cliente, apoyo, bid)

    intento = cliente.post(f"/bloques-ruta/{bid}/intentos", headers=_cab(apoyo)).json()
    detalle = cliente.get(f"/intentos/{intento['intento_id']}", headers=_cab(apoyo)).json()
    # 8 ítems: la profundidad la fija el nivel de exigencia del bloque (N3).
    assert len(detalle["items"]) == 8
    assert detalle["respuestas"] == {}
    for i in detalle["items"]:
        assert "indice_correcta" not in i, "la respuesta no viaja jamás en la evaluación"

    primero = detalle["items"][0]["item_id"]
    cliente.post(f"/intentos/{intento['intento_id']}/respuestas", headers=_cab(apoyo),
                 json={"item_id": primero, "indice_elegido": 2})

    # "recargar": se vuelve a abrir y debe devolver EL MISMO intento, con la respuesta
    otra_vez = cliente.post(f"/bloques-ruta/{bid}/intentos", headers=_cab(apoyo)).json()
    assert otra_vez["intento_id"] == intento["intento_id"]
    retomado = cliente.get(f"/intentos/{intento['intento_id']}", headers=_cab(apoyo)).json()
    assert retomado["respuestas"][primero] == 2
    assert [i["item_id"] for i in retomado["items"]] == [i["item_id"] for i in detalle["items"]]


def test_el_canario_en_la_api_reprobar_no_deja_nada(cliente, apoyo):
    ruta = cliente.get("/mi/ruta", headers=_cab(apoyo)).json()
    bid = ruta[0]["bloque_ruta_id"]
    _ver_modulos(cliente, apoyo, bid)
    antes = cliente.get("/mi/estado", headers=_cab(apoyo)).json()

    intento = cliente.post(f"/bloques-ruta/{bid}/intentos", headers=_cab(apoyo)).json()
    clave = {c["item_id"]: c["indice_correcta"] for c in cliente.get(
        f"/bloques-ruta/{bid}/clave-de-respuestas", headers=_cab(apoyo)).json()}
    for n, item in enumerate(intento["items_servidos"]):
        # solo una correcta de cinco → 20%
        elegido = clave[item] if n == 0 else (clave[item] + 1) % 4
        cliente.post(f"/intentos/{intento['intento_id']}/respuestas", headers=_cab(apoyo),
                     json={"item_id": item, "indice_elegido": elegido})

    r = cliente.post(f"/intentos/{intento['intento_id']}/cerrar", headers=_cab(apoyo)).json()
    assert r["aprobado"] is False and r["insignia_id"] is None and r["xp_otorgado"] == 0

    despues = cliente.get("/mi/estado", headers=_cab(apoyo)).json()
    assert despues["insignias"] == antes["insignias"], "reprobar no otorga insignia"
    assert despues["xp_acreditable"] == antes["xp_acreditable"], "ni XP acreditable"

    bloque = cliente.get(f"/bloques-ruta/{bid}", headers=_cab(apoyo)).json()
    assert bloque["estado"] != "completo" and bloque["obtenida"] == 0


def test_aprobar_al_umbral_si_otorga_y_deja_respaldo(cliente, apoyo):
    ruta = cliente.get("/mi/ruta", headers=_cab(apoyo)).json()
    bid = ruta[0]["bloque_ruta_id"]
    clave = {c["item_id"]: c["indice_correcta"] for c in cliente.get(
        f"/bloques-ruta/{bid}/clave-de-respuestas", headers=_cab(apoyo)).json()}

    intento = cliente.post(f"/bloques-ruta/{bid}/intentos", headers=_cab(apoyo)).json()
    for item in intento["items_servidos"]:
        cliente.post(f"/intentos/{intento['intento_id']}/respuestas", headers=_cab(apoyo),
                     json={"item_id": item, "indice_elegido": clave[item]})

    r = cliente.post(f"/intentos/{intento['intento_id']}/cerrar", headers=_cab(apoyo)).json()
    # Dimensión crítica: la medalla que nace es la GOLD, y rinde más que la silver.
    assert r["aprobado"] is True and r["insignia_id"] is not None and r["xp_otorgado"] == 600

    insignias = cliente.get("/mi/insignias", headers=_cab(apoyo)).json()
    assert len(insignias) == 1
    assert insignias[0]["tipo"] == "gold"
    assert insignias[0]["puntaje_del_respaldo"] == 1.0
    assert insignias[0]["numero_intento"] == 2, "la respalda el intento aprobado, el segundo"


# ------------------------------------------------------- M1 · Calibre
def _items_quiz(cliente, token, n_modulo=0):
    """
    Un módulo de la ruta y su quiz.

    Con 2 módulos por bloque, los índices altos salen del bloque siguiente. Lo que
    importa acá es que cada prueba tome un módulo DISTINTO: el tope diario de XP
    lúdico es por juego, y repetir módulo haría que la segunda no pagara.
    """
    ruta = cliente.get("/mi/ruta", headers=_cab(token)).json()
    modulos = []
    for b in ruta:
        modulos += cliente.get(
            f"/bloques-ruta/{b['bloque_ruta_id']}/modulos", headers=_cab(token)
        ).json()
    mod = modulos[n_modulo]
    return mod, cliente.get(f"/modulos/{mod['id']}/quiz", headers=_cab(token)).json()


def test_calibre_premia_arriesgar_y_castiga_equivocarse_arriesgando(cliente, apoyo):
    mod, items = _items_quiz(cliente, apoyo, 4)
    # Todo correcto y todo "Seguro": 60 por ítem + bono de calibrado
    r = cliente.post(f"/modulos/{mod['id']}/calibre/resultado", headers=_cab(apoyo),
                     json={"respuestas": [{"item_id": i["id"], "indice_elegido": i["indice_correcta"],
                                           "seguro": True} for i in items]}).json()
    assert r["puntos"] == len(items) * 60 + 50
    assert r["bono_calibrado"] is True
    assert r["xp_otorgado"] == r["puntos"]


def test_calibre_el_marcador_puede_quedar_negativo_pero_el_xp_no(cliente, apoyo):
    """El castigo es no ganar, no perder XP ya ganado."""
    mod, items = _items_quiz(cliente, apoyo, 5)
    r = cliente.post(f"/modulos/{mod['id']}/calibre/resultado", headers=_cab(apoyo),
                     json={"respuestas": [{"item_id": i["id"],
                                           "indice_elegido": (i["indice_correcta"] + 1) % 4,
                                           "seguro": True} for i in items]}).json()
    assert r["puntos"] == -40 * len(items), "en pantalla el marcador baja"
    assert r["xp_otorgado"] == 0, "pero nunca se resta XP"
    assert r["bono_calibrado"] is False


def test_calibre_ir_siempre_a_lo_seguro_no_gana_el_bono(cliente, apoyo):
    """El bono premia calibración, no volumen: hay que declarar seguro y acertar."""
    mod, items = _items_quiz(cliente, apoyo, 6)
    r = cliente.post(f"/modulos/{mod['id']}/calibre/resultado", headers=_cab(apoyo),
                     json={"respuestas": [{"item_id": i["id"], "indice_elegido": i["indice_correcta"],
                                           "seguro": False} for i in items]}).json()
    assert r["puntos"] == len(items) * 25
    assert r["bono_calibrado"] is False, "sin ningún 'Seguro' no hay calibrado que premiar"


def test_calibre_un_solo_seguro_fallado_rompe_el_bono(cliente, apoyo):
    mod, items = _items_quiz(cliente, apoyo, 7)
    respuestas = []
    for n, i in enumerate(items):
        malo = n == 0
        respuestas.append({"item_id": i["id"],
                           "indice_elegido": (i["indice_correcta"] + 1) % 4 if malo else i["indice_correcta"],
                           "seguro": True})
    r = cliente.post(f"/modulos/{mod['id']}/calibre/resultado", headers=_cab(apoyo),
                     json={"respuestas": respuestas}).json()
    assert r["seguros"] == len(items) and r["seguros_acertados"] == len(items) - 1
    assert r["bono_calibrado"] is False


def test_calibre_es_ludico_y_no_toca_el_acreditable(cliente, apoyo):
    antes = cliente.get("/mi/estado", headers=_cab(apoyo)).json()
    mod, items = _items_quiz(cliente, apoyo, 8)
    cliente.post(f"/modulos/{mod['id']}/calibre/resultado", headers=_cab(apoyo),
                 json={"respuestas": [{"item_id": i["id"], "indice_elegido": i["indice_correcta"],
                                       "seguro": True} for i in items]})
    despues = cliente.get("/mi/estado", headers=_cab(apoyo)).json()
    assert despues["xp_acreditable"] == antes["xp_acreditable"]
    assert despues["escalon"] == antes["escalon"]
    assert despues["insignias"] == antes["insignias"]


def test_calibre_no_se_juega_el_modulo_de_otro_cargo(cliente, apoyo, direccion):
    ruta_direccion = cliente.get("/mi/ruta", headers=_cab(direccion)).json()
    ajeno = cliente.get(
        f"/bloques-ruta/{ruta_direccion[0]['bloque_ruta_id']}/modulos", headers=_cab(direccion)
    ).json()[0]
    r = cliente.post(f"/modulos/{ajeno['id']}/calibre/resultado", headers=_cab(apoyo),
                     json={"respuestas": []})
    assert r.status_code == 404


# ------------------------------------------- tope de ranking (ratificado)
def test_el_ranking_suma_ludico_solo_hasta_el_acreditable(cliente, apoyo):
    """«Jugar puede duplicar tu posición, nunca reemplazar el recorrido.»"""
    e = cliente.get("/mi/estado", headers=_cab(apoyo)).json()
    assert e["xp_ranking"] == e["xp_acreditable"] + min(e["xp_ludico"], e["xp_acreditable"])
    assert e["xp_ranking"] <= 2 * e["xp_acreditable"]


def test_quien_no_avanza_no_escala_jugando(cliente, direccion):
    """Con XP acreditable en cero, todo el XP lúdico aporta cero al ranking."""
    fila = [f for f in cliente.get("/ranking", headers=_cab(direccion)).json()
            if f["xp_acreditable"] == 0]
    for f in fila:
        assert f["xp_ranking"] == 0, "sin recorrido, jugar no da posición"


# ------------------------------------------- B2 · Mesa de comité (Camino B)
def test_la_mesa_reparte_cartas_sin_revelar_la_bandeja(cliente, apoyo):
    m = cliente.get("/juegos/mesa", headers=_cab(apoyo)).json()
    assert len(m["bandejas"]) == 5
    assert len(m["cartas"]) == 6
    for c in m["cartas"]:
        assert set(c) == {"item_id", "texto"}, "la carta no puede traer su dimensión"
        assert len(c["texto"]) > 20, "la afirmación tiene que entenderse sola"


def test_la_mesa_busca_variedad_de_dimensiones(cliente, apoyo):
    """Una mesa casi monodimensional se resuelve por descarte y deja de ser interesante."""
    m = cliente.get("/juegos/mesa", headers=_cab(apoyo)).json()
    r = cliente.post("/juegos/mesa/resultado", headers=_cab(apoyo),
                     json={"colocaciones": [{"item_id": c["item_id"], "dimension": "GESTION"}
                                            for c in m["cartas"]]}).json()
    dims = {x["dimension_correcta"] for x in r["revelacion"]}
    assert len(dims) >= 4, f"solo {len(dims)} dimensiones en la mesa"


def test_cerrar_la_mesa_perfecta_da_el_bono(cliente, apoyo):
    m = cliente.get("/juegos/mesa", headers=_cab(apoyo)).json()
    # Se cierra mal a propósito para conocer la verdad, y se vuelve a armar bien.
    espia = cliente.post("/juegos/mesa/resultado", headers=_cab(apoyo),
                         json={"colocaciones": [{"item_id": c["item_id"], "dimension": "ICI"}
                                                for c in m["cartas"]]}).json()
    correcto = {x["item_id"]: x["dimension_correcta"] for x in espia["revelacion"]}

    r = cliente.post("/juegos/mesa/resultado", headers=_cab(apoyo),
                     json={"colocaciones": [{"item_id": k, "dimension": v}
                                            for k, v in correcto.items()]}).json()
    assert r["aciertos"] == r["total"]
    assert r["mesa_perfecta"] is True
    assert r["puntos"] == r["total"] * 40 + 80


def test_la_revelacion_dice_donde_iba_cada_carta(cliente, apoyo):
    m = cliente.get("/juegos/mesa", headers=_cab(apoyo)).json()
    r = cliente.post("/juegos/mesa/resultado", headers=_cab(apoyo),
                     json={"colocaciones": [{"item_id": c["item_id"], "dimension": "VCM"}
                                            for c in m["cartas"]]}).json()
    for x in r["revelacion"]:
        assert x["puesta_en"] == "VCM"
        assert x["dimension_correcta"] and x["dimension_nombre"]
        assert x["enunciado"], "el reveal muestra de qué concepto se trataba"
        assert x["acerto"] == (x["dimension_correcta"] == "VCM")


def test_la_mesa_solo_usa_contenido_de_la_propia_ruta(cliente, apoyo, direccion):
    """I-10 también rige para los juegos."""
    mia = cliente.get("/juegos/mesa", headers=_cab(apoyo)).json()
    ajena = cliente.get("/juegos/mesa", headers=_cab(direccion)).json()
    r = cliente.post("/juegos/mesa/resultado", headers=_cab(apoyo),
                     json={"colocaciones": [{"item_id": c["item_id"], "dimension": "GESTION"}
                                            for c in ajena["cartas"]]}).json()
    # Ninguna carta del Rector es válida en la mesa del Docente salvo que compartan bloque.
    assert r["total"] <= len(ajena["cartas"])
    assert {c["item_id"] for c in mia["cartas"]} != {c["item_id"] for c in ajena["cartas"]}


def test_la_mesa_es_ludica_y_no_toca_el_acreditable(cliente, apoyo):
    antes = cliente.get("/mi/estado", headers=_cab(apoyo)).json()
    m = cliente.get("/juegos/mesa", headers=_cab(apoyo)).json()
    cliente.post("/juegos/mesa/resultado", headers=_cab(apoyo),
                 json={"colocaciones": [{"item_id": c["item_id"], "dimension": "CALIDAD"}
                                        for c in m["cartas"]]})
    despues = cliente.get("/mi/estado", headers=_cab(apoyo)).json()
    assert despues["xp_acreditable"] == antes["xp_acreditable"]
    assert despues["escalon"] == antes["escalon"]
    assert despues["insignias"] == antes["insignias"]


# ----------------------------------------- desafío aplicado (dimensión crítica)
def test_el_desafio_no_entrega_la_clave_antes_de_decidir(cliente, direccion):
    """Igual que el banco de la evaluación: lo que corrige no viaja al cliente."""
    ruta = cliente.get("/mi/ruta", headers=_cab(direccion)).json()
    critico = next(b for b in ruta if b["es_critica"])
    caso = cliente.get(
        f"/bloques-ruta/{critico['bloque_ruta_id']}/desafio", headers=_cab(direccion)
    ).json()

    assert caso["rol_ficticio"] and caso["situacion"] and caso["datos"]
    assert len(caso["decisiones"]) >= 2
    for d in caso["decisiones"]:
        assert "clave_correcta" not in d, "la respuesta no puede viajar antes de decidir"
        assert d["opciones"], "decidir necesita opciones definidas"


def test_el_desafio_es_requisito_de_la_evaluacion_reforzada(cliente, direccion):
    """La secuencia se impone en el servidor, no solo en la pantalla."""
    ruta = cliente.get("/mi/ruta", headers=_cab(direccion)).json()
    critico = next(b for b in ruta if b["es_critica"] and b["estado"] != "completo")
    bid = critico["bloque_ruta_id"]

    for m in cliente.get(f"/bloques-ruta/{bid}/modulos", headers=_cab(direccion)).json():
        cliente.post(f"/modulos/{m['id']}/completar", headers=_cab(direccion))

    r = cliente.post(f"/bloques-ruta/{bid}/intentos", headers=_cab(direccion))
    assert r.status_code == 409 and "desafío" in r.json()["detail"]


def test_el_desafio_da_xp_ludico_y_nunca_medalla(cliente, direccion):
    """Resolverlo perfecto no acerca a nadie a una medalla ni mueve el escalón (S-04)."""
    ruta = cliente.get("/mi/ruta", headers=_cab(direccion)).json()
    critico = next(b for b in ruta if b["es_critica"] and b["estado"] != "completo")
    bid = critico["bloque_ruta_id"]

    antes = cliente.get("/mi/estado", headers=_cab(direccion)).json()
    caso = cliente.get(f"/bloques-ruta/{bid}/desafio", headers=_cab(direccion)).json()
    r = cliente.post(
        f"/bloques-ruta/{bid}/desafio/resultado", headers=_cab(direccion),
        json={"respuestas": [{"decision_id": d["decision_id"],
                              "respuesta": d["opciones"][0]["clave"]}
                             for d in caso["decisiones"]]},
    ).json()

    assert r["total"] == len(caso["decisiones"])
    assert all("clave_correcta" in x for x in r["revelacion"]), "al cerrar sí se revela"

    despues = cliente.get("/mi/estado", headers=_cab(direccion)).json()
    assert despues["xp_acreditable"] == antes["xp_acreditable"], "ni un punto acreditable"
    assert despues["insignias"] == antes["insignias"], "ni una insignia"
    assert despues["escalon"] == antes["escalon"], "ni un escalón"


def test_reenviar_el_desafio_no_vuelve_a_pagar(cliente, direccion):
    ruta = cliente.get("/mi/ruta", headers=_cab(direccion)).json()
    critico = next(b for b in ruta if b["es_critica"] and b["estado"] != "completo")
    bid = critico["bloque_ruta_id"]
    caso = cliente.get(f"/bloques-ruta/{bid}/desafio", headers=_cab(direccion)).json()
    cuerpo = {"respuestas": [{"decision_id": d["decision_id"],
                              "respuesta": d["opciones"][0]["clave"]}
                             for d in caso["decisiones"]]}

    cliente.post(f"/bloques-ruta/{bid}/desafio/resultado", headers=_cab(direccion), json=cuerpo)
    otra = cliente.post(
        f"/bloques-ruta/{bid}/desafio/resultado", headers=_cab(direccion), json=cuerpo
    ).json()
    assert otra["ya_resuelto"] is True and otra["xp_otorgado"] == 0


def test_el_desafio_de_otro_rol_no_se_abre(cliente, apoyo, direccion):
    ruta_ajena = cliente.get("/mi/ruta", headers=_cab(direccion)).json()
    critico = next(b for b in ruta_ajena if b["es_critica"])
    r = cliente.get(
        f"/bloques-ruta/{critico['bloque_ruta_id']}/desafio", headers=_cab(apoyo)
    )
    assert r.status_code == 404


# ------------------------------------ D3 · Línea de tiempo (juego de la dimensión)
def _bloque_calidad(cliente, token):
    ruta = cliente.get("/mi/ruta", headers=_cab(token)).json()
    return next(b for b in ruta if b["dimension"] == "CALIDAD")["bloque_ruta_id"]


def test_el_bloque_dice_que_juego_le_toca(cliente, apoyo):
    """
    Cada dimensión lleva el suyo. Las que no lo tienen aún devuelven null, y la
    pantalla muestra el hueco: esconderlo daría a entender que el bloque está completo.
    """
    ruta = cliente.get("/mi/ruta", headers=_cab(apoyo)).json()
    juegos = {}
    for b in ruta:
        detalle = cliente.get(f"/bloques-ruta/{b['bloque_ruta_id']}", headers=_cab(apoyo)).json()
        juegos[b["dimension"]] = detalle["juego"]

    # Se listan a mano y no desde el registro a propósito: si se leyera el mismo
    # mapa que sirve la API, la prueba pasaría con el registro vacío.
    assert juegos["CALIDAD"]["clave"] == "linea_tiempo"
    assert juegos["DOCENCIA"]["clave"] == "cohorte"
    assert juegos["VCM"]["clave"] == "contrapartes"
    assert all(juegos[d] is None for d in ("GESTION", "ICI")), "faltan de la fase 2"


def test_la_linea_no_entrega_las_fechas_antes_de_ordenar(cliente, apoyo):
    """Si el período viajara con la carta, ordenar sería leer fechas."""
    linea = cliente.get(
        f"/bloques-ruta/{_bloque_calidad(cliente, apoyo)}/juego/linea-tiempo",
        headers=_cab(apoyo),
    ).json()

    assert len(linea["cartas"]) == 6
    for c in linea["cartas"]:
        assert set(c) == {"hito_id", "codigo", "titulo"}


def test_la_linea_solo_se_juega_en_su_dimension(cliente, apoyo):
    """El juego de una dimensión no se juega desde otra."""
    ruta = cliente.get("/mi/ruta", headers=_cab(apoyo)).json()
    ajena = next(b for b in ruta if b["dimension"] != "CALIDAD")["bloque_ruta_id"]
    r = cliente.get(f"/bloques-ruta/{ajena}/juego/linea-tiempo", headers=_cab(apoyo))
    assert r.status_code == 409


def test_la_linea_de_otro_rol_no_se_abre(cliente, apoyo, direccion):
    ajeno = _bloque_calidad(cliente, direccion)
    r = cliente.get(f"/bloques-ruta/{ajeno}/juego/linea-tiempo", headers=_cab(apoyo))
    assert r.status_code == 404


def test_el_orden_correcto_da_linea_perfecta(cliente, apoyo):
    """El servidor conoce la secuencia real; el cliente solo manda en qué orden la dejó."""
    bid = _bloque_calidad(cliente, apoyo)
    linea = cliente.get(f"/bloques-ruta/{bid}/juego/linea-tiempo", headers=_cab(apoyo)).json()
    # Los códigos H01..H13 llevan el orden real: sirven de clave para la prueba.
    correcto = [c["hito_id"] for c in sorted(linea["cartas"], key=lambda c: c["codigo"])]

    r = cliente.post(f"/bloques-ruta/{bid}/juego/linea-tiempo/resultado",
                     headers=_cab(apoyo), json={"orden": correcto}).json()

    assert r["linea_perfecta"] is True
    assert r["pares_correctos"] == r["pares_totales"] == 15
    assert r["en_su_lugar"] == 6
    assert r["puntos"] == 15 * 18 + 90


def test_la_linea_invertida_no_acierta_ni_un_par(cliente, apoyo):
    """El puntaje por pares tiene que distinguir «casi» de «al revés»."""
    bid = _bloque_calidad(cliente, apoyo)
    linea = cliente.get(f"/bloques-ruta/{bid}/juego/linea-tiempo", headers=_cab(apoyo)).json()
    invertido = [c["hito_id"] for c in sorted(linea["cartas"], key=lambda c: c["codigo"],
                                              reverse=True)]

    r = cliente.post(f"/bloques-ruta/{bid}/juego/linea-tiempo/resultado",
                     headers=_cab(apoyo), json={"orden": invertido}).json()

    assert r["pares_correctos"] == 0 and r["puntos"] == 0
    assert r["linea_perfecta"] is False
    # La revelación llega ordenada por la secuencia real, con el período que faltaba.
    assert [h["posicion_real"] for h in r["revelacion"]] == [1, 2, 3, 4, 5, 6]
    assert all(h["periodo_texto"] for h in r["revelacion"])


def test_un_solo_hito_corrido_conserva_casi_todo_el_puntaje(cliente, apoyo):
    """
    Lo que justifica puntuar por pares: con puntaje por casilla, mover uno de lugar
    puede desplazar a todos los demás y perderlo todo aunque la secuencia se entienda.
    """
    bid = _bloque_calidad(cliente, apoyo)
    linea = cliente.get(f"/bloques-ruta/{bid}/juego/linea-tiempo", headers=_cab(apoyo)).json()
    orden = [c["hito_id"] for c in sorted(linea["cartas"], key=lambda c: c["codigo"])]
    orden.insert(0, orden.pop())            # el último se va al principio

    r = cliente.post(f"/bloques-ruta/{bid}/juego/linea-tiempo/resultado",
                     headers=_cab(apoyo), json={"orden": orden}).json()

    assert r["en_su_lugar"] == 0, "ni una casilla exacta"
    assert r["pares_correctos"] == 10, "pero 10 de 15 pares siguen bien ordenados"
    assert r["puntos"] > 0


def test_la_linea_es_ludica_y_no_toca_lo_acreditable(cliente, apoyo):
    bid = _bloque_calidad(cliente, apoyo)
    antes = cliente.get("/mi/estado", headers=_cab(apoyo)).json()
    linea = cliente.get(f"/bloques-ruta/{bid}/juego/linea-tiempo", headers=_cab(apoyo)).json()
    cliente.post(f"/bloques-ruta/{bid}/juego/linea-tiempo/resultado", headers=_cab(apoyo),
                 json={"orden": [c["hito_id"] for c in linea["cartas"]]})

    despues = cliente.get("/mi/estado", headers=_cab(apoyo)).json()
    assert despues["xp_acreditable"] == antes["xp_acreditable"]
    assert despues["insignias"] == antes["insignias"]
    assert despues["escalon"] == antes["escalon"]


def test_repetir_la_linea_el_mismo_dia_no_vuelve_a_pagar(cliente, apoyo):
    bid = _bloque_calidad(cliente, apoyo)
    linea = cliente.get(f"/bloques-ruta/{bid}/juego/linea-tiempo", headers=_cab(apoyo)).json()
    cuerpo = {"orden": [c["hito_id"] for c in linea["cartas"]]}
    cliente.post(f"/bloques-ruta/{bid}/juego/linea-tiempo/resultado", headers=_cab(apoyo),
                 json=cuerpo)
    otra = cliente.post(f"/bloques-ruta/{bid}/juego/linea-tiempo/resultado",
                        headers=_cab(apoyo), json=cuerpo).json()
    assert otra["ya_jugado_hoy"] is True and otra["xp_otorgado"] == 0


def test_una_linea_con_hitos_repetidos_se_rechaza(cliente, apoyo):
    bid = _bloque_calidad(cliente, apoyo)
    linea = cliente.get(f"/bloques-ruta/{bid}/juego/linea-tiempo", headers=_cab(apoyo)).json()
    uno = linea["cartas"][0]["hito_id"]
    r = cliente.post(f"/bloques-ruta/{bid}/juego/linea-tiempo/resultado",
                     headers=_cab(apoyo), json={"orden": [uno, uno]})
    assert r.status_code == 422


# ------------------------------- D2 · El caso del estudiante que se pierde
def _bloque_docencia(cliente, token):
    ruta = cliente.get("/mi/ruta", headers=_cab(token)).json()
    return next(b for b in ruta if b["dimension"] == "DOCENCIA")["bloque_ruta_id"]


def test_la_cohorte_no_entrega_el_quiebre_antes_de_diagnosticar(cliente, apoyo):
    """Como el banco de la evaluación: lo que corrige no viaja."""
    partida = cliente.get(
        f"/bloques-ruta/{_bloque_docencia(cliente, apoyo)}/juego/cohorte", headers=_cab(apoyo)
    ).json()

    assert len(partida["casos"]) == 3
    for c in partida["casos"]:
        assert "tramo_quiebre" not in c and "indicador_correcto" not in c
        # La referencia SÍ viaja: sin ella el juego premiaría la caída más grande.
        assert all("referencia_pct" in t for t in c["tramos"])
        assert len(c["etapas"]) == len(c["tramos"]) + 1
        assert len(c["indicadores"]) == 4


def test_el_juego_de_docencia_no_se_juega_en_otra_dimension(cliente, apoyo):
    bid = _bloque_calidad(cliente, apoyo)      # ahí vive la Línea de tiempo
    assert cliente.get(f"/bloques-ruta/{bid}/juego/cohorte",
                       headers=_cab(apoyo)).status_code == 409


def test_la_cohorte_de_otro_rol_no_se_abre(cliente, apoyo, direccion):
    ajeno = _bloque_docencia(cliente, direccion)
    assert cliente.get(f"/bloques-ruta/{ajeno}/juego/cohorte",
                       headers=_cab(apoyo)).status_code == 404


def _clave_de_casos(conexion, codigos):
    filas = conexion.execute(
        """SELECT codigo, tramo_quiebre, indicador_correcto
             FROM caso_cohorte WHERE codigo = ANY(%s)""",
        (codigos,),
    ).fetchall()
    return {f[0]: (f[1], f[2]) for f in filas}


def test_diagnosticar_los_tres_casos_da_lectura_limpia(cliente, apoyo):
    """El servidor corrige contra el contenido; el cliente solo dice qué señaló."""
    import psycopg
    bid = _bloque_docencia(cliente, apoyo)
    partida = cliente.get(f"/bloques-ruta/{bid}/juego/cohorte", headers=_cab(apoyo)).json()

    with psycopg.connect(DSN, autocommit=True) as conn:
        clave = _clave_de_casos(conn, [c["codigo"] for c in partida["casos"]])

    r = cliente.post(
        f"/bloques-ruta/{bid}/juego/cohorte/resultado", headers=_cab(apoyo),
        json={"respuestas": [
            {"caso_id": c["caso_id"], "tramo": clave[c["codigo"]][0],
             "indicador": clave[c["codigo"]][1]}
            for c in partida["casos"]
        ]},
    ).json()

    assert r["tramos_correctos"] == 3 and r["indicadores_correctos"] == 3
    assert r["lectura_limpia"] is True
    assert r["puntos"] == 3 * 45 + 3 * 45 + 90
    assert all(x["explicacion_quiebre"] and x["explicacion_indicador"] for x in r["revelacion"])


def test_el_tramo_y_la_causa_se_cobran_por_separado(cliente, apoyo):
    """
    Encontrar el quiebre es leer datos; explicarlo es entender el proceso. Acertar
    uno y fallar el otro tiene que notarse en el puntaje.
    """
    import psycopg
    bid = _bloque_docencia(cliente, apoyo)
    partida = cliente.get(f"/bloques-ruta/{bid}/juego/cohorte", headers=_cab(apoyo)).json()

    with psycopg.connect(DSN, autocommit=True) as conn:
        clave = _clave_de_casos(conn, [c["codigo"] for c in partida["casos"]])

    r = cliente.post(
        f"/bloques-ruta/{bid}/juego/cohorte/resultado", headers=_cab(apoyo),
        json={"respuestas": [
            # tramos correctos, causas todas equivocadas
            {"caso_id": c["caso_id"], "tramo": clave[c["codigo"]][0], "indicador": "no-existe"}
            for c in partida["casos"]
        ]},
    ).json()

    assert r["tramos_correctos"] == 3 and r["indicadores_correctos"] == 0
    assert r["lectura_limpia"] is False
    assert r["puntos"] == 3 * 45, "sin bono y sin los puntos de la causa"


def test_la_cohorte_es_ludica_y_no_toca_lo_acreditable(cliente, apoyo):
    bid = _bloque_docencia(cliente, apoyo)
    antes = cliente.get("/mi/estado", headers=_cab(apoyo)).json()
    partida = cliente.get(f"/bloques-ruta/{bid}/juego/cohorte", headers=_cab(apoyo)).json()
    cliente.post(f"/bloques-ruta/{bid}/juego/cohorte/resultado", headers=_cab(apoyo),
                 json={"respuestas": [{"caso_id": c["caso_id"], "tramo": 0, "indicador": "x"}
                                      for c in partida["casos"]]})
    despues = cliente.get("/mi/estado", headers=_cab(apoyo)).json()
    assert despues["xp_acreditable"] == antes["xp_acreditable"]
    assert despues["insignias"] == antes["insignias"]
    assert despues["escalon"] == antes["escalon"]


# ------------------------------------------- D4 · El mapa de contrapartes
def _bloque_vcm(cliente, token):
    ruta = cliente.get("/mi/ruta", headers=_cab(token)).json()
    return next(b for b in ruta if b["dimension"] == "VCM")["bloque_ruta_id"]


def test_el_mapa_no_dice_cual_va_con_cual(cliente, apoyo):
    mapa = cliente.get(
        f"/bloques-ruta/{_bloque_vcm(cliente, apoyo)}/juego/contrapartes", headers=_cab(apoyo)
    ).json()

    assert len(mapa["actores"]) == 6 and len(mapa["acciones"]) == 6
    for a in mapa["actores"]:
        assert "accion_clave" not in a and "razon" not in a


def test_el_mapa_reparte_mas_acciones_de_las_que_usa(cliente, apoyo):
    """
    Sin señuelos, el tablero se termina por descarte: tendidos los primeros
    vínculos, los que quedan calzan solos.
    """
    import psycopg
    mapa = cliente.get(
        f"/bloques-ruta/{_bloque_vcm(cliente, apoyo)}/juego/contrapartes", headers=_cab(apoyo)
    ).json()
    with psycopg.connect(DSN, autocommit=True) as conn:
        usadas = {
            f[0] for f in conn.execute(
                """SELECT accion_clave FROM actor_externo
                    WHERE id = ANY(%s::uuid[]) AND accion_clave IS NOT NULL""",
                ([a["actor_id"] for a in mapa["actores"]],),
            ).fetchall()
        }
    repartidas = {a["clave"] for a in mapa["acciones"]}
    assert usadas < repartidas, "no hay acciones señuelo"
    assert len(usadas) == 4, "cuatro vínculos con acciones distintas entre sí"


def test_el_mapa_trae_actores_que_no_son_contraparte(cliente, apoyo):
    """El descarte es la mitad del juego: sin actores que sobren, no hay qué decidir."""
    import psycopg
    mapa = cliente.get(
        f"/bloques-ruta/{_bloque_vcm(cliente, apoyo)}/juego/contrapartes", headers=_cab(apoyo)
    ).json()
    with psycopg.connect(DSN, autocommit=True) as conn:
        sin_vinculo = conn.execute(
            """SELECT count(*) FROM actor_externo
                WHERE id = ANY(%s::uuid[]) AND accion_clave IS NULL""",
            ([a["actor_id"] for a in mapa["actores"]],),
        ).fetchone()[0]
    assert sin_vinculo == 2


def _clave_del_mapa(mapa):
    import psycopg
    with psycopg.connect(DSN, autocommit=True) as conn:
        filas = conn.execute(
            "SELECT id, accion_clave FROM actor_externo WHERE id = ANY(%s::uuid[])",
            ([a["actor_id"] for a in mapa["actores"]],),
        ).fetchall()
    return {str(f[0]): f[1] for f in filas}


def test_el_mapa_completo_da_mapa_limpio(cliente, apoyo):
    bid = _bloque_vcm(cliente, apoyo)
    mapa = cliente.get(f"/bloques-ruta/{bid}/juego/contrapartes", headers=_cab(apoyo)).json()
    clave = _clave_del_mapa(mapa)

    r = cliente.post(
        f"/bloques-ruta/{bid}/juego/contrapartes/resultado", headers=_cab(apoyo),
        json={"vinculos": [{"actor_id": a["actor_id"], "accion_clave": clave[a["actor_id"]]}
                           for a in mapa["actores"]]},
    ).json()

    assert r["aciertos"] == 6 and r["mapa_limpio"] is True
    assert r["descartes_correctos"] == r["descartes_totales"] == 2
    assert r["puntos"] == 6 * 50 + 60
    assert all(x["razon"] for x in r["revelacion"])


def test_atar_un_proveedor_a_una_accion_lo_cuenta_como_error(cliente, apoyo):
    """
    El error que el juego existe para desarmar: contar como convenio lo que es
    una compra. Tiene que costar puntos, no pasar desapercibido.
    """
    bid = _bloque_vcm(cliente, apoyo)
    mapa = cliente.get(f"/bloques-ruta/{bid}/juego/contrapartes", headers=_cab(apoyo)).json()
    clave = _clave_del_mapa(mapa)
    una_accion = mapa["acciones"][0]["clave"]

    r = cliente.post(
        f"/bloques-ruta/{bid}/juego/contrapartes/resultado", headers=_cab(apoyo),
        json={"vinculos": [
            # a los que no son contraparte se les ata una acción cualquiera
            {"actor_id": a["actor_id"],
             "accion_clave": clave[a["actor_id"]] or una_accion}
            for a in mapa["actores"]
        ]},
    ).json()

    assert r["descartes_correctos"] == 0 and r["descartes_totales"] == 2
    assert r["mapa_limpio"] is False
    assert r["aciertos"] == 4, "los cuatro vínculos reales siguen valiendo"


def test_el_mapa_de_otra_dimension_y_de_otro_rol_no_se_abre(cliente, apoyo, direccion):
    propio_pero_ajeno = _bloque_calidad(cliente, apoyo)     # ahí vive la Línea de tiempo
    assert cliente.get(f"/bloques-ruta/{propio_pero_ajeno}/juego/contrapartes",
                       headers=_cab(apoyo)).status_code == 409
    de_otro = _bloque_vcm(cliente, direccion)
    assert cliente.get(f"/bloques-ruta/{de_otro}/juego/contrapartes",
                       headers=_cab(apoyo)).status_code == 404


def test_el_mapa_es_ludico_y_no_toca_lo_acreditable(cliente, apoyo):
    bid = _bloque_vcm(cliente, apoyo)
    antes = cliente.get("/mi/estado", headers=_cab(apoyo)).json()
    mapa = cliente.get(f"/bloques-ruta/{bid}/juego/contrapartes", headers=_cab(apoyo)).json()
    cliente.post(f"/bloques-ruta/{bid}/juego/contrapartes/resultado", headers=_cab(apoyo),
                 json={"vinculos": [{"actor_id": a["actor_id"], "accion_clave": None}
                                    for a in mapa["actores"]]})
    despues = cliente.get("/mi/estado", headers=_cab(apoyo)).json()
    assert despues["xp_acreditable"] == antes["xp_acreditable"]
    assert despues["insignias"] == antes["insignias"]
    assert despues["escalon"] == antes["escalon"]


def test_abrir_mi_ruta_no_otorga_nada(cliente, direccion):
    """
    El atajo de desarrollo levanta el candado de secuencia y NADA más: si además
    marcara progreso, sería una ruta de código que produce completitud sin haber
    aprobado, que es exactamente lo que el sistema existe para impedir.
    """
    antes = cliente.get("/mi/estado", headers=_cab(direccion)).json()
    r = cliente.post("/auth/dev/abrir-mi-ruta", headers=_cab(direccion))
    assert r.status_code == 200

    ruta = cliente.get("/mi/ruta", headers=_cab(direccion)).json()
    assert all(b["estado"] != "bloqueado" for b in ruta)

    despues = cliente.get("/mi/estado", headers=_cab(direccion)).json()
    assert despues == antes, "abrir la ruta no puede mover XP, insignias ni escalón"

    # Y el bloque recién abierto sigue exigiendo su recorrido.
    ultimo = ruta[-1]["bloque_ruta_id"]
    assert cliente.post(f"/bloques-ruta/{ultimo}/intentos",
                        headers=_cab(direccion)).status_code == 409
