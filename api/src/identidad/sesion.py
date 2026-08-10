"""
Sesión firmada.

Token propio, con HMAC de la biblioteca estándar: sin dependencias nuevas y sin
estado en servidor. Lo único que transporta es a quién representa y hasta cuándo.

Cuando entre Entra ID, esto sigue igual: el adapter de identidad valida contra el
proveedor y **emite este mismo token**. El resto del sistema nunca sabe contra
cuál se autenticó (S-18).
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from uuid import UUID

# En producción va por el gestor de secretos del cliente. El default es de
# desarrollo y el arranque avisa si no se cambió.
SECRETO = os.environ.get("SECRETO_SESION", "dev-inseguro-cambiar-en-produccion")
DURACION_SEGUNDOS = 8 * 60 * 60


class SesionInvalida(Exception):
    pass


def _b64(datos: bytes) -> str:
    return base64.urlsafe_b64encode(datos).decode().rstrip("=")


def _de_b64(texto: str) -> bytes:
    return base64.urlsafe_b64decode(texto + "=" * (-len(texto) % 4))


def _firma(carga: str) -> str:
    return _b64(hmac.new(SECRETO.encode(), carga.encode(), hashlib.sha256).digest())


def emitir(colaborador_id: UUID, *, proveedor: str, ahora: float | None = None) -> str:
    ahora = ahora if ahora is not None else time.time()
    carga = _b64(json.dumps({
        "sub": str(colaborador_id),
        "prv": proveedor,
        "exp": int(ahora + DURACION_SEGUNDOS),
    }, separators=(",", ":")).encode())
    return f"{carga}.{_firma(carga)}"


def verificar(token: str, *, ahora: float | None = None) -> dict:
    ahora = ahora if ahora is not None else time.time()
    try:
        carga, firma = token.split(".", 1)
    except ValueError:
        raise SesionInvalida("token mal formado")

    # compare_digest y no ==: comparar firmas byte a byte con salida temprana
    # filtra información sobre la firma correcta.
    if not hmac.compare_digest(firma, _firma(carga)):
        raise SesionInvalida("firma inválida")

    try:
        datos = json.loads(_de_b64(carga))
    except Exception:
        raise SesionInvalida("carga ilegible")

    if datos.get("exp", 0) < ahora:
        raise SesionInvalida("sesión expirada")

    return datos
