"""
Adapter de identidad conmutable (S-18 · CLAUDE.md §10).

El código de negocio **nunca sabe** contra cuál proveedor se autenticó alguien:
solo recibe un `colaborador_id` de una sesión firmada. Cambiar de dev a Entra es
cambiar qué proveedor se monta, no tocar endpoints.

- `ProveedorDev` — login "actuar como" los colaboradores del slice. **Solo dev**;
  se excluye del build de producción con `MODO_DEV`.
- `ProveedorEntra` — OIDC contra Microsoft Entra ID. El contrato está; el cableado
  llega cuando exista el tenant, y no bloquea el avance (§10).
"""
from __future__ import annotations

import os
from typing import Protocol
from uuid import UUID

from .sesion import emitir


class Identidad(Protocol):
    nombre: str

    def colaboradores_disponibles(self, conn) -> list[dict]:
        """A quién se puede representar. En Entra: nadie, se autentica de verdad."""
        ...

    def autenticar(self, conn, **datos) -> str:
        """Devuelve un token de sesión firmado."""
        ...


class ProveedorDev:
    """
    Login de desarrollo: se elige a quién representar, sin contraseña.

    No hay contraseñas en ninguna parte del sistema, ni acá ni en producción: el
    formulario de correo y clave de la cáscara se eliminó a propósito (S-18).
    """

    nombre = "dev"

    def colaboradores_disponibles(self, conn) -> list[dict]:
        filas = conn.execute(
            """SELECT c.id, c.nombre, c.email, ca.nombre AS cargo, u.nombre AS unidad,
                      (pi.colaborador_id IS NOT NULL) AS ve_panel_institucional
                 FROM colaborador c
                 JOIN cargo ca ON ca.id = c.cargo_id
                 LEFT JOIN unidad u ON u.id = c.unidad_id
                 LEFT JOIN permiso_institucional pi ON pi.colaborador_id = c.id
                ORDER BY c.nombre"""
        ).fetchall()
        return [
            {"id": f[0], "nombre": f[1], "email": f[2], "cargo": f[3],
             "unidad": f[4], "ve_panel_institucional": f[5]}
            for f in filas
        ]

    def autenticar(self, conn, *, colaborador_id: UUID, **_) -> str:
        existe = conn.execute(
            "SELECT 1 FROM colaborador WHERE id = %s", (colaborador_id,)
        ).fetchone()
        if not existe:
            raise LookupError("ese colaborador no existe")
        return emitir(colaborador_id, proveedor=self.nombre)


class ProveedorEntra:
    """
    Microsoft Entra ID por OIDC.

    Pendiente de tenant. Cuando llegue: validar el id_token, mapear el claim a
    `colaborador.subject_id` y emitir el mismo token de sesión. Nada más cambia.
    """

    nombre = "entra"

    def colaboradores_disponibles(self, conn) -> list[dict]:
        return []          # con Entra no se elige a quién representar

    def autenticar(self, conn, **datos) -> str:
        raise NotImplementedError(
            "el proveedor Entra todavía no está cableado: falta el tenant de AIEP. "
            "Mientras tanto corre con MODO_DEV=true y el login 'actuar como'."
        )


def proveedor_activo() -> Identidad:
    if os.environ.get("MODO_DEV", "").lower() == "true":
        return ProveedorDev()
    return ProveedorEntra()
