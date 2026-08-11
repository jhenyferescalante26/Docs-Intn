# Reporte: partición del controlador de Solicitudes de Servicio (portal)

> Estado: **análisis / propuesta** — 2026-07-27, sobre branch `18.0` (HEAD `ca46f071`)
> Alcance: capa portal de `service.request` (`/my/service_request/*`) y su reparto controller ↔ model.
> No incluye backend (vistas admin) ni el portal OWL (JS), salvo donde el contrato de payload lo obliga.

---

## 1. Resumen ejecutivo

**Respuesta corta a "¿en cuántos controladores hay que partirlo?"**

| Eje | Hoy | Propuesta |
|---|---|---|
| Rutas HTTP `/my/service_request/new` | **3 declaraciones** de la misma ruta, encadenadas por MRO | **1** |
| Ficheros de controlador para el flujo SR | 1 monolito de 1940 líneas + 3 mixins + 2 overrides | **5 controladores por responsabilidad** |
| Lógica de creación por caso de negocio | mezclada: 2 casos en controller, 4 en modelo, 1 en un tercer módulo | **6 handlers de creación**, todos en el modelo |

Es decir: **5 controladores + 6 handlers de creación (que no son controladores HTTP, son extensiones del modelo)**.

La distinción es el punto central de este documento: **no hay que crear un controlador HTTP por categoría de servicio**. Eso multiplicaría rutas, plantillas y puntos de autenticación sin reducir el acoplamiento. Lo que hay que hacer es:

1. Partir el monolito **por responsabilidad HTTP** (crear / listar / detalle / reportes / API JSON) → 5 ficheros.
2. Mover el "qué se crea" a **hooks del modelo extendidos por categoría** → 6 handlers, cada uno en el módulo que ya es dueño de esa categoría.

Lo bueno: **el patrón objetivo ya existe y funciona** en el camino de lectura (GET). `_portal_extra_create_form_initial_data` es un hook del modelo extendido por **10 módulos** distintos (OIAT, OIAT combustibles, ONI ×5, metrología, ONC, autofill). La propuesta es hacer el camino de escritura (POST) simétrico al de lectura, no inventar arquitectura nueva.

---

## 2. Diagnóstico: dónde está el volumen

### 2.1 El fichero

`custom_addons/intn_portal/intn_portal_fleet_requests/portal/_shared/controllers/service_request.py` — **1940 líneas, 45 métodos, 10 rutas HTTP**, en una sola clase `CustomerPortalFleetServiceRequest`.

Reparto real de esas 1940 líneas por tema:

| Líneas | Tema | Destino propuesto |
|---:|---|---|
| 47–85 | Prefill de sesión (set/get/clear/apply) | Controller (mixin propio) |
| 87–121 | Parseo `datetime-local` → UTC | Modelo / util |
| 123–135 | Redirect por `submission_token` | Modelo (idempotencia) |
| 137–280 | Resolución de catálogo, `service_location`, opciones | **Modelo** (`service.request.service.catalog`) |
| 282–504 | Valores del formulario de creación + estimación | **Modelo** (hooks ya existentes) |
| 506–536 | Totales del detalle | Modelo |
| **538–976** | **Metrología: parseo, validación, creación, adjuntos** | **Modelo** (módulo de metrología) |
| 978–1090 | Helpers compartidos + adjuntos OIAT | Modelo |
| 1092–1353 | Listados (`/my/service_requests`, quick_search, appointments) | Controller "list" |
| 1355–1534 | Detalle + control de acceso + bloqueo por pago | Controller "detail" |
| 1536–1682 | Reportes PDF y descarga de adjuntos | Controller "reports" |
| 1684–1811 | Endpoints JSON (`estimate_total`, `start_enabling`) | Controller "api" |
| 1813–1940 | Ruta `/new` (GET + POST) y su `if/elif` por categoría | Controller "create" |

**439 de las 1940 líneas (23 %) son metrología pura** viviendo en el controlador que se supone es genérico. Ninguna otra categoría hace eso.

### 2.2 El "método gigante" es en realidad una cadena de tres

`portal_create_service_request` está declarado **tres veces** sobre la misma URL, resuelto por orden de MRO:

```
onc_create.py:326            if category == "brand"    → _portal_create_onc_request()
  └─ super() → cistern_service_request.py:26   if category == "fleet"  → _portal_fleet_create_service_request()
       └─ super() → service_request.py:1813    if/elif metrology | oiat | oni  → ... 128 líneas
```

Problemas concretos de esta forma:

- **El orden importa y no está declarado en ningún sitio.** Depende de qué módulos estén instalados y del orden de herencia en `CustomerPortalFleetCisternServiceRequest` (`cistern_service_request.py:12-16`). Añadir una categoría nueva obliga a insertarse en la cadena.
- **La clase base conoce a sus hijos.** `service_request.py:1817` valida contra la lista literal `("fleet", "metrology", "oiat", "oni")` — `brand` no está, aunque `brand` es una categoría real (`intn_brand_service_requests/data/service_request_category_brand_data.xml:5`). Lo mismo en 354–365 y 360–365, donde se construyen diccionarios con las 4 categorías hardcodeadas **a pesar de que ya existen** `_portal_form_config_by_category()` y `_portal_catalog_options_by_category()` (`service_request_portal_payload.py:19,25`) que las recorren dinámicamente.
- **Stubs invertidos.** `_portal_fleet_trucks_domain` (1008), `_portal_fleet_trailers_domain` (1012) y `_portal_tank_inspection_certificate` (1016) devuelven `[("id","=",0)]` / recordset vacío en la base, y sólo el módulo cistern los implementa de verdad. Es la base declarando la API de un hijo.
- **`except Exception` que se traga todo.** En 1852, 1872, 1886 y en `cistern_create_handlers.py:333`, cualquier excepción (incluidos `AccessError`, `KeyError`, errores de programación) se convierte en `values["error"] = str(e)` y se re-renderiza el formulario. Un bug de código se le muestra al cliente como un mensaje de validación.

### 2.3 Asimetría entre categorías (lo más caro de mantener)

| Categoría | Dónde vive la creación | Líneas | Delegación al modelo |
|---|---|---:|---|
| `fleet` (cistern) | `cistern_create_handlers.py` (controller) + `_portal_prepare_fleet_portal_create_vals` (modelo) | 335 + 107 | **parcial** — vals en modelo, orquestación en controller |
| `metrology` (verificación) | `service_request.py:865-976` + `585-747` (controller) | ~330 | **casi nula** — sólo `_portal_prepare_metrology_header_vals` |
| `metrology` (aprobación de modelo) | `service_request.py:781-863` (controller) | 83 | parcial — `_portal_prepare_model_approval_vals` (modelo, 146 líneas) |
| `oiat` | `oiat_service_request.py:167` (**modelo**) | 267 | **total** ✅ |
| `oni` | `oni_service_request.py:293` (**modelo**) + 5 módulos que encadenan | 276 + n | **total** ✅ |
| `brand` / ONC | `onc_create.py:117` (controller de otro módulo) | 114 | parcial |

OIAT y ONI ya hacen lo correcto: el controlador llama a **una** línea

```python
request.env["service.request"].sudo()._portal_create_oiat_service_request(values, kw)
```

y toda la lógica de negocio se extiende por herencia de modelo. ONI incluso resuelve la sub-variante por catálogo con `super()` encadenado (`oni_maquila_service_request.py:251-257`), que es exactamente el mecanismo que debería usarse en todas partes.

Metrología, en cambio, tiene 330 líneas de parseo de `line_*_%s`, validación de rangos, verificación marca↔modelo y creación de `ir.attachment` **dentro del controlador**, imposible de testear sin levantar HTTP y no reutilizable desde un import masivo o un test de modelo.

---

## 3. Propuesta: los 5 controladores

Cada uno un fichero, cada uno una clase mixin, ensamblados en la clase concreta del módulo. Objetivo: **ninguno supera ~350 líneas**.

```
intn_portal_fleet_requests/portal/_shared/controllers/
├── service_request_create.py     ~180   ruta /new (GET+POST), dispatch, prefill de sesión
├── service_request_list.py       ~280   /my/service_requests, quick_search, /my/appointments
├── service_request_detail.py     ~230   /my/service_request/<id>, acceso, bloqueo por pago, pasos
├── service_request_reports.py    ~200   PDFs y descarga de adjuntos
└── service_request_api.py        ~200   endpoints JSON (estimate_total, start_enabling, lookups)
```

Más los que ya existen y quedan como están: `service_request_portal_base.py` (37), `service_request_portal_payload.py` (338), `header/controllers/header_api.py` (312).

### 3.1 `service_request_create.py` — el corazón del cambio

Una sola ruta, sin `if` por categoría:

```python
@http.route(["/my/service_request/new"], type="http", auth="user",
            website=True, methods=["GET", "POST"])
def portal_create_service_request(self, **kw):
    category = self._portal_normalize_category(kw.get("service_category"))
    values = self._portal_build_create_values(category, kw)

    if request.httprequest.method == "POST":
        redirect = self._portal_redirect_existing_submission(kw.get("submission_token"))
        if redirect:
            return redirect
        try:
            sr = request.env["service.request"].sudo()._portal_create_from_portal(
                category, values, kw, request.httprequest.files,
            )
        except (UserError, ValidationError) as err:      # ← ya no `except Exception`
            values["error"] = str(err)
        else:
            if sr:
                self._portal_sr_prefill_clear()
                return request.redirect("/my/service_request/%s" % sr.id)

    return request.render("intn_portal_fleet_requests.portal_create_service_request", values)
```

Todo lo específico de categoría desaparece del controlador. `cistern_service_request.py:19-30` y `onc_create.py:319-354` (las dos re-declaraciones de la ruta) **se eliminan**.

### 3.2 Reparto de rutas

| Fichero | Rutas |
|---|---|
| `create` | `/my/service_request/new` |
| `list` | `/my/service_requests`, `/page/<int>`, `/quick_search`, `/my/appointments` |
| `detail` | `/my/service_request/<id>` |
| `reports` | `/my/service_request/<id>/attachment/<id>`, `/metrology_technical_sheet/<line>`, y los 6 reportes hoy en `cistern_service_request_mixin.py:469-617` |
| `api` | `/my/service_request/estimate_total`, `/start_enabling` |
| (sin cambio) `header_api` | `/organizations`, `/departments`, `/categories`, `/products`, `/catalog*` |
| (sin cambio) redirects legacy | `/my/metrology_dispenser_request/new`, `/my/oiat_service_request/new` |

Las URLs no cambian — los tests E2E existentes siguen valiendo, que es la garantía de que el refactor es seguro.

---

## 4. Propuesta: los 6 handlers de creación

Un handler por caso de negocio, cada uno **en el módulo dueño de esa categoría**, todos extendiendo el mismo hook de modelo `_portal_create_from_portal`:

| # | Caso | Módulo | Hook |
|---|---|---|---|
| 1 | Fleet / cisternas | `intn_portal_fleet_cistern` | `_portal_create_fleet_service_request` |
| 2 | Metrología — verificación de surtidores | `intn_portal_metrology_dispenser_requests` | `_portal_create_metrology_service_request` |
| 3 | Metrología — aprobación de modelo | idem (sub-variante por catálogo) | `_portal_create_model_approval_service_request` |
| 4 | OIAT | `intn_portal_oiat_service_request` | `_portal_create_oiat_service_request` ✅ ya existe |
| 5 | ONI | `intn_portal_oni_seguridad_industrial` (+5 que encadenan) | `_portal_create_oni_service_request` ✅ ya existe |
| 6 | Brand / ONC | `intn_onc_certification_requests` | `_portal_create_onc_service_request` |

Despacho por registro, no por MRO de controlador. En `intn_service_request/models/service_request.py`:

```python
@api.model
def _portal_create_from_portal(self, category, values, kw, files):
    handler = getattr(self, "_portal_create_%s_service_request" % category, None)
    if not handler:
        raise UserError(_("Unsupported service category: %s") % category)
    return handler(values, kw, files)
```

Cada módulo aporta su método. Añadir la categoría N+1 es **añadir un método en un módulo nuevo**, sin tocar `intn_portal_fleet_requests`. Las sub-variantes (ONI maquila/muestreo/textil/inspección, metrología verificación/aprobación) siguen usando el `super()` encadenado con resolución por catálogo que ONI ya usa hoy (`oni_maquila_service_request.py:251`).

---

## 5. Qué va al modelo y qué se queda en el controlador

### 5.1 Regla

> El controlador toca `request`. El modelo no.

Si un método usa `request.httprequest`, `request.session`, `request.redirect`, `request.render` o `request.make_response`, es controlador. Todo lo demás — parseo del payload de negocio, validación, construcción de `vals`, `create()`, adjuntos, dominios de visibilidad, precios — es modelo.

Excepción práctica: los objetos `FileStorage` de `httprequest.files` pueden pasarse al modelo como parámetro (es lo que ya hace `_intn_portal_create_attachments_from_specs`). Lo que no debe hacer el modelo es **leerlos de `request`** por su cuenta.

### 5.2 Se queda en el controlador

| Responsabilidad | Referencia actual |
|---|---|
| Prefill en sesión (`set/get/clear/apply`) | `service_request.py:47-85` |
| Normalizar categoría del `kw` y elegir plantilla | 1816-1825 |
| Redirect / render / `make_response` JSON | 992-997, 1849, 1938 |
| Token de acceso portal y `_document_check_access` | 1471-1487 |
| Paginación (`portal_pager`), searchbars, sortby/filterby | 1113-1204 |
| Traducir excepción de negocio → `values["error"]` | 1852-1887 (acotando el `except`) |
| Servir PDF con headers | 1498-1535 |

### 5.3 Se mueve al modelo (lista accionable, con destino)

| Origen | Líneas | Destino |
|---|---:|---|
| `_portal_prepare_metrology_line_values` | 585–747 (163) | `metrology_dispenser_service_request.py` → `_portal_prepare_metrology_line_vals(kw, files)` |
| `_portal_create_metrology_request` | 865–976 (112) | idem → `_portal_create_metrology_service_request(values, kw, files)` |
| `_portal_create_model_approval_request` | 781–863 (83) | `service_request_model_approval_mixin.py` |
| `_portal_create_metrology_attachments` | 749–779 (31) | idem (usar specs declarativas existentes) |
| `_portal_metrology_parse_range`, `_portal_metrology_browse_catalog` | 556–583 (28) | idem |
| `_portal_create_oiat_certificate_attachments` + `_portal_create_oiat_protemapio_attachments` | 1050–1090 (41) | `oiat_service_request.py` (junto al `_portal_create_oiat_service_request` que ya está ahí) |
| `_portal_create_attachments` | 1020–1048 (29) | `service_request_attachment_requirement_mixin.py` |
| `_portal_derive_service_location`, `_portal_resolve_catalog_selection`, `_portal_resolve_initial_catalog_id`, `_portal_service_catalog_options` | 137–280 (144) | `service_request_service_catalog.py` — son reglas del catálogo, no de HTTP |
| `_portal_estimate_service_total_values` | 426–504 (79) | `service_request_sale_mixin.py`; el `if oiat / if oni / else` colapsa a un único camino dirigido por catálogo |
| `_portal_prepare_create_form_body_values` | 282–424 (143) | Partir: masterdata por categoría → `_portal_extra_create_form_initial_data` (**hook que ya existe**, 10 implementaciones); sólo la parte de render QWeb queda en controller |
| `_portal_intn_masterdata_domain`, `_portal_allowed_company_partner`, `_portal_fleet_*_domain` | 978–1014 (37) | Modelo — son **reglas de seguridad**; hoy sólo se aplican si pasas por el portal |
| `_portal_parse_local_datetime_to_utc` | 87–121 (35) | `service_request_scheduling_mixin.py` |
| Búsquedas por `submission_token` (×4, duplicadas) | 123-135, 792-805, 877-890, `cistern_create_handlers.py:100-114` | Un solo `_portal_find_by_submission_token(token, category=None)` |
| Creación del `helpdesk.ticket` (×3, casi idéntica) | 826-838, 916-927, `cistern_create_handlers.py:116-145` | `service_request_helpdesk_mixin.py` → `_portal_create_helpdesk_ticket(category, service_type, partner)` |
| Orquestación de creación fleet | `cistern_create_handlers.py:225-335` (111) | `service_request_fleet_portal_create.py` (el modelo ya tiene la mitad) |

Suma aproximada: **~1000 líneas migran de controller a modelo**, y de ellas ~150 desaparecen por deduplicación (ticket ×3, submission_token ×4, `_portal_json_response` ×2, dominios duplicados entre base y cistern).

### 5.4 Estado final estimado

| Capa | Hoy | Después |
|---|---:|---:|
| `service_request.py` (controller) | 1940 | **0** (se disuelve en 5 ficheros) |
| Controladores SR, mayor fichero | 1940 | ~280 |
| `cistern_create_handlers.py` | 335 | ~120 (sólo orquestación HTTP) |
| Lógica de creación testeable sin HTTP | ~55 % | **~95 %** |

---

## 6. Riesgos y orden de ejecución

Ordenado por (valor / riesgo). Cada fase es mergeable por separado y no rompe URLs.

**Fase 0 — sin riesgo, 1 día.** Partir `service_request.py` en los 5 ficheros **moviendo métodos tal cual**, sin cambiar una línea de lógica. Ensamblar por mixins en la clase concreta. Verificable con `git diff -M` (puro movimiento) y ejecutando la suite E2E existente.

**Fase 1 — riesgo bajo, alto valor.** Deduplicar: ticket de helpdesk, `submission_token`, `_portal_json_response`, dominios. Sustituir los diccionarios hardcodeados de 354–365 por `_portal_form_config_by_category()` / `_portal_catalog_options_by_category()`, que ya existen y ya son dinámicos. Efecto colateral positivo: `brand` deja de ser una categoría de segunda clase.

**Fase 2 — riesgo medio.** Acotar los `except Exception` a `(UserError, ValidationError)`. **Ojo:** hay flujos que hoy dependen de que se trague `ValueError` — `_portal_create_oni_service_request` usa `ValueError` como mecanismo de validación de usuario en al menos 11 puntos (`oni_service_request.py:322, 358, 360, 362, 364, 366, 368, 370, 372, 404, …`), y el `except Exception` de 1886 los convierte hoy en mensaje de formulario. Hay que convertir esos `ValueError` en `ValidationError` **antes** de acotar el `except`, o el usuario verá un 500 donde hoy ve "Seleccione el departamento". Es el único punto del refactor donde un descuido es visible en producción.

**Fase 3 — riesgo medio, el grueso del valor.** Mover metrología (las 439 líneas) al modelo de metrología y darle la forma de `_portal_create_oiat_service_request`. Aquí sí conviene test de modelo, aunque sea uno solo, porque el parseo de `line_*_%s` tiene 8 ramas de validación.

**Fase 4 — riesgo bajo.** Introducir `_portal_create_from_portal` con despacho por registro y eliminar las dos re-declaraciones de la ruta `/new` (`cistern_service_request.py`, `onc_create.py`).

**Fase 5 — opcional.** Mover catálogo/estimación/dominios al modelo (§5.3, filas de catálogo y seguridad). Es la parte más "arquitectónica" y la menos urgente.

### Riesgos a vigilar

- **Orden de MRO.** Al pasar de override de ruta a registro, `CustomerPortalFleetCisternServiceRequest` cambia de forma. Hay que verificar que ningún módulo dependa del orden actual de herencia.
- **Contrato del payload OWL.** `_portal_form_payload_for_catalog` (`service_request_portal_payload.py:189`) alimenta al frontend. Cualquier movimiento de `_portal_prepare_create_form_body_values` debe mantener idénticas las claves del dict — es un contrato con JS que el Python no valida.
- **`sudo()` y tracking.** Los comentarios en 854-856, 967-969 y `cistern_create_handlers.py:228-232` documentan que `category_id`/`request_type_id` son campos rastreados con comodelos admin-only: crear como usuario portal revienta con `AccessError` al leer el `display_name` para el mensaje de tracking. Al mover a modelo hay que preservar el `sudo()` en el mismo punto, no antes ni después.
- **Rutas legacy.** `/my/oiat_service_request/new` y `/my/metrology_dispenser_request/new` son alias que redirigen; conviene confirmar que no hay enlaces externos vivos antes de tocarlas (no forman parte de este refactor).

---

## 7. Conclusión

- **5 controladores**, partidos por responsabilidad HTTP, no por categoría de servicio.
- **6 handlers de creación**, uno por caso de negocio, todos en el modelo, cada uno en el módulo que ya es dueño de su categoría.
- **1 sola declaración** de la ruta `/my/service_request/new`, con despacho por registro en lugar de cadena de `super()`.
- ~1000 líneas se mueven de controller a modelo; ~150 desaparecen por deduplicación.

El argumento más fuerte a favor: **OIAT y ONI ya funcionan así**, y son las dos categorías más recientes y con más sub-variantes (ONI tiene 5 módulos encadenados sin tocar el controlador base ni una vez). El refactor no propone un diseño nuevo — propone terminar de aplicar el que el equipo ya eligió.
