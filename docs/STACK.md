# Stack técnico

Lo que hay construido y funcionando, con versiones exactas, y lo que falta con lo
que haría falta para hacerlo. Las versiones salen de los archivos del repo, no de
memoria: `api/requirements.txt`, `web/package.json`, `realtime/package.json`, los
`Dockerfile` y `.github/workflows/integridad.yml`.

Última revisión: agosto de 2026.

---

## 1. Lo construido

### Backend — API y motor

| Pieza | Versión | Para qué |
|---|---|---|
| Python | 3.12 (en el contenedor) | El intérprete va dentro de la imagen: la máquina del director tiene 3.9 |
| FastAPI | 0.115.6 | API HTTP y `/docs` interactivo, que fue la primera interfaz de prueba |
| Uvicorn | 0.34.0 (`[standard]`) | Servidor ASGI |
| psycopg | 3.2.13 (`[binary]`) | Driver de PostgreSQL |
| psycopg_pool | 3.2.4 | Pool de conexiones |
| Pydantic | vía FastAPI (v2) | Validación de los cuerpos que entran |
| jsonschema | 4.23.0 | Valida el contrato del Generador (`schema-bloque-contenido.json`) |

### Base de datos

| Pieza | Versión | Para qué |
|---|---|---|
| PostgreSQL | 16 | **Es donde viven los invariantes**, no solo donde se guardan los datos |
| Migraciones | SQL plano + corredor propio (`src/migrar.py`, ~40 líneas) | 13 migraciones numeradas, aplicadas en orden y registradas |

El esquema hace trabajo real, no es un depósito: triggers que impiden que exista
una medalla sin su intento aprobado, CHECKs que prohíben XP acreditable desde un
juego, un constraint diferido que exige que la distribución de un rol sume 1, y
vistas que aplican el umbral de anonimato de la Ley 21.719 **antes** de que
cualquier consulta pueda pedir un desglose demasiado fino.

### Identidad

| Pieza | Para qué |
|---|---|
| `hmac` + `hashlib` + `base64` de la stdlib | Sesión firmada con HMAC-SHA256. Sin librería de JWT |
| Adapter conmutable | `ProveedorDev` (login "actuar como") ↔ `ProveedorEntra` (contrato listo, sin cablear) |

**No hay contraseñas en ninguna parte del sistema**, ni en desarrollo ni en el
diseño de producción.

### Frontend

| Pieza | Versión | Para qué |
|---|---|---|
| React | 19 | Interfaz |
| TypeScript | 5.7 | Tipos |
| Vite | 6 | Build |
| @vitejs/plugin-react | 4.3 | — |
| @fontsource | 5.3 | Bricolage Grotesque, Inter y JetBrains Mono **autohospedadas** (S-26) |
| nginx | alpine | Sirve el build y hace de proxy de `/api` hacia la API |

Construido con `node:22-alpine`, servido con `nginx:alpine`.

### Tiempo real (la Plaza — spike, no integrado)

| Pieza | Versión | Para qué |
|---|---|---|
| Node | 22 | Runtime |
| Colyseus | 0.15 | Servidor de estado sincronizado (ADR-004) |
| @colyseus/ws-transport | 0.15 | WebSocket |
| @colyseus/schema | 2.0 | Serialización del estado de la sala |
| Express | 4.19 | Sirve el cliente de prueba y `/salud` |
| esbuild | 0.28 | Empaqueta el cliente **para navegador** |

El bundle del cliente se construye con esbuild a propósito: servir
`node_modules/colyseus.js/dist` reventaba en el navegador con `Buffer is not
defined`, porque está compilado contra Node.

### Pruebas y CI

| Pieza | Versión | Para qué |
|---|---|---|
| pytest | 8.4.2 | 200 pruebas |
| httpx | 0.28.1 | `TestClient` de FastAPI |
| PostgreSQL real | 16 | **Nunca SQLite**: los CHECK y triggers no existen ahí y darían una garantía falsa |
| Banco de mutación | Bash | Rompe cada candado a propósito y exige que la suite se ponga roja |
| GitHub Actions | `ubuntu-latest`, `setup-python@v5` (3.12), `setup-node@v4` (22), servicio `postgres:16` | 3 jobs |

### Infraestructura

| Pieza | Para qué |
|---|---|
| Docker Compose | 4 servicios con healthchecks y `depends_on` condicionados: un `docker compose up` y listo |
| ngrok | 3.39 | Túnel para demos externas |
| `caffeinate` | Mantiene el Mac despierto mientras el túnel está publicado |

**Costo de infraestructura hoy: cero.** Todo corre local. La nube es tema de
producción, post-firma y en la cuenta del cliente.

---

## 2. Lo que deliberadamente NO se usó

Vale la pena para la propuesta: cada omisión fue una decisión, no un olvido.

| Lo habitual | Qué se usó en cambio | Por qué |
|---|---|---|
| ORM (SQLAlchemy) | SQL escrito a mano | Los invariantes viven en el esquema y hay que poder leerlos tal cual. Un ORM los esconde |
| Alembic | Migraciones SQL + corredor propio | Mismo motivo. Alembic entra cuando haya que migrar en caliente |
| Librería de JWT | HMAC-SHA256 de la stdlib | Una dependencia menos en la superficie de autenticación |
| Framework CSS (Tailwind, Bootstrap) | CSS propio con tokens de diseño | La identidad visual estaba definida; un framework la habría diluido |
| Librería de gráficos | SVG y CSS a mano | Los gráficos del panel son barras y líneas; una librería pesa más de lo que resuelve |
| Router (React Router) | ~200 líneas de estado | Pocas pantallas. Se reevalúa cuando entren las que faltan |
| Gestor de estado (Redux, Zustand) | `useState` y props | El estado que importa vive en el servidor |
| Redis / colas | Nada | No hay trabajo asíncrono que justificarlas todavía |
| Servicio de autenticación externo | Adapter propio conmutable | El código de negocio no sabe contra cuál corre |

---

## 3. Lo que falta

### 3.1 · Decidido, falta cablear

**Microsoft Entra ID (SSO real).** El adapter está escrito y `ProveedorEntra`
levanta `NotImplementedError` con el motivo: falta el tenant de AIEP. Hace falta:

- Registro de aplicación en el tenant de AIEP (client ID, secret o certificado,
  redirect URI).
- Librería: **MSAL for Python** (`msal`) o un cliente OIDC genérico
  (`authlib`). MSAL es lo natural siendo Microsoft.
- Mapeo de grupos de Entra → roles N1/N2/N3 y unidad. **Esto es una definición de
  AIEP, no técnica**: hay que saber qué grupos existen.

Nada del resto del sistema cambia: el código de negocio nunca recibe más que un
`colaborador_id` de una sesión firmada.

**Open Badges (medalla verificable).** Está en la constitución del proyecto
(CLAUDE.md §3) y es lo que convierte la medalla en evidencia y no en adorno. La
tabla `insignia` ya tiene la columna `open_badge_assertion_id` esperando. Dos
caminos, sin decidir:

- **Emitir nosotros:** Open Badges 3.0 son Verifiable Credentials del W3C —
  JSON-LD firmado con Ed25519. Librerías: `pyld` + `cryptography`. Más control,
  más trabajo, y hay que custodiar una llave.
- **Usar un emisor:** Badgr / Canvas Credentials, u otro. Menos trabajo, una
  dependencia externa y un costo por credencial.

Es una decisión de nivel 3 (cuesta plata y es difícil de revertir): la dejo para
el director.

**La Plaza.** El servidor existe y se probó con tres personas en redes distintas.
Falta el cliente y el enganche. El servidor sincroniza **casillas de un plano**,
no píxeles (ADR-004), justamente para que esta decisión no lo obligue a
reescribirse:

- **2D:** Canvas, cero dependencias nuevas. Es lo que ya tiene el cliente de prueba.
- **3D:** `three.js`, o `@react-three/fiber` para que conviva con React. Más peso
  y más riesgo en equipos modestos.

Recomiendo empezar por 2D, medir con gente real y subir a 3D si el gate lo
aguanta.

### 3.2 · Pendiente sin decisión previa

| Qué | Con qué |
|---|---|
| **Correo** (avisos, recordatorios) | Adapter conmutable como el de identidad. SMTP del tenant de AIEP, o un proveedor (SES, SendGrid) |
| **Pantalla de insignias** (D3) | Nada nuevo: React sobre lo que ya hay |
| **Accesibilidad completa** (D7b) | `axe-core` en CI para que no sea una revisión manual |
| **Endurecer para producción** (D8) | Quitar `MODO_DEV` y `/clave-de-respuestas`, rotar `SECRETO_SESION` |
| **Migraciones en caliente** | Alembic, adoptando el esquema actual como revisión inicial |
| **Panel a 85.000 personas** | Vistas materializadas refrescadas por hora. Medido: 6.000 personas responden en 23–72 ms; a 85.000 se estima 0,3–1 s, que puede molestar |

### 3.3 · Producción: recomendación, no decisión

Hoy no hay nada en la nube y el costo es cero. Cuando haya que desplegar, y
**siendo AIEP una casa Microsoft**, lo natural es su propio tenant de Azure:

| Pieza | Recomendación | Nota |
|---|---|---|
| API y web | **Azure Container Apps** | Las imágenes ya existen y son las mismas |
| Base de datos | **Azure Database for PostgreSQL Flexible Server** | Backups y punto de recuperación gestionados |
| Realtime | Container App con WebSocket, o **Azure Web PubSub** | Colyseus necesita conexiones persistentes |
| Secretos | **Azure Key Vault** | `SECRETO_SESION`, credenciales de Entra |
| Identidad | **Entra ID** | Ya es el destino del adapter |

Esto es una recomendación coherente con el resto, no una decisión tomada: el
sistema corre en cualquier sitio que sepa levantar contenedores y un PostgreSQL,
y esa portabilidad fue deliberada.

---

## 4. Resumen en una línea

**Python 3.12 + FastAPI + PostgreSQL 16 en el servidor, React 19 + TypeScript +
Vite en el navegador, Node 22 + Colyseus para el tiempo real, todo en Docker
Compose con un solo comando y sin una línea de nube.**
