# Plan: tours de Odoo para todos los procesos de portal

> **Objetivo:** que cada proceso de portal tenga cobertura e2e con la infraestructura
> nativa de tours de Odoo (`start_tour` + `web_tour.tours`), y retirar de Playwright
> todo lo que quede duplicado.
>
> **El objetivo original decía «retirar Playwright del repo por completo». No es
> alcanzable como estaba planteado:** 34 de los 54 specs generan las capturas de
> la documentación, un trabajo que los tours no hacen. Ver §5.
>
> Complementa a [`plan-tests-controllers-portal.md`](plan-tests-controllers-portal.md)
> (qué falta cubrir en la capa de controller) y a
> [`plan-rebalanceo-piramide-tests.md`](plan-rebalanceo-piramide-tests.md) (en qué capa
> vive cada aserción). Este documento trata **la capa de arriba**: el DOM real que ve
> el cliente.

---

## 0. Punto de partida

Hoy existe **un solo** tour en el repo:

| Archivo | Qué cubre |
|---|---|
| `intn_onc_certification_requests/static/tests/tours/onc_portal_forms_tour.js` | ONC-FOR-001, ONC-FSG-001, ONC-FPE-001 |
| `intn_onc_certification_requests/tests/test_onc_portal_tours.py` | los levanta con `start_tour` sobre `PortalFleetHttpCase` |

Nació de un bug concreto: las suites `tests/portal/` postean el payload directo al
controller, así que siguen en verde aunque el formulario renderizado **no tenga input**
para un campo que el servidor exige. FOR-001 y FSG-001 se enviaron sin ser enviables y
nada lo detectó. Ese es exactamente el hueco que un tour cierra y un HttpCase no.

Del otro lado hay **54 specs de Playwright** en `e2e/specs/` con 38 flows en
`e2e/lib/flows/`, de los cuales ~25 specs tocan portal.

### Adjuntos: un tour sí puede subir archivos

Esto era la duda que sostenía a Playwright, y está resuelta. `@web/../tests/utils`
exporta `inputFiles`, que arma un `DataTransfer`, lo asigna a `input.files` —la única
asignación que el navegador acepta en un input de archivo— y dispara `change`:

```js
import { inputFiles } from "@web/../tests/utils";

{
    trigger: 'input[type="file"][name="doc_cert_verificacion"]',
    async run() {
        const file = new File(["%PDF-1.4 x"], "cert.pdf", { type: "application/pdf" });
        await inputFiles('input[type="file"][name="doc_cert_verificacion"]', [file]);
    },
}
```

Tres cosas que hacen que esto funcione en el portal y no sólo en el backoffice:

- **El bundle llega al frontend.** `web.assets_tests` incluye
  `web/static/tests/legacy/utils.js`, y `web.frontend_layout` llama a
  `web.conditional_assets_tests` — o sea que en modo test el portal también lo carga.
  Toda referencia a QUnit dentro de ese archivo está detrás de `if (window.QUnit)`, así
  que el import no explota fuera de QUnit. Precedente en el propio Odoo:
  `mail/static/tests/tours/discuss_channel_public_tour.js` sube archivos en una ruta
  pública.
- **Nuestros formularios usan `<input type="file">` plano**, que es exactamente lo que
  `inputFiles` manipula — no un componente con API propia.
- **El `change` que dispara no burbujea.** Los formularios ONI/OIAT leen el archivo con
  `t-on-change` puesto **sobre el input mismo**, así que les llega. Si algún formulario
  futuro delega el handler a un ancestro, no se va a enterar: ahí hay que disparar el
  evento a mano con `{ bubbles: true }`.

Para los formularios que postean multipart nativo (fleet, ONC, corrección documental)
alcanza con `inputFiles` + click en submit: los bytes llegan al controller igual que
con un cliente real. **Verificado en este repo**, ver §2 bis.

### Lo que sí hay que resolver de otra forma

1. **Descargas y PDFs.** Un tour no inspecciona el archivo descargado. Los reportes se
   cubren con `HttpCase.url_open` sobre la ruta (status + `content-type`), que ya es la
   política del repo — `AGENTS.md` prohíbe generar el PDF en un test.
2. **Cruces portal↔backoffice.** Un tour es una sesión. El equivalente es un test Python
   que encadena: fixtures → `start_tour` con el usuario de portal → operaciones de
   backoffice en Python o un segundo `start_tour` con un usuario interno → aserciones.
   Es más código que un journey de Playwright, pero cubre lo mismo.
3. **Demo data.** El tour corre dentro del proceso de Odoo con `--test-enable`, contra
   la DB de test. Cada tour nuevo obliga a revisar que la demo data que necesita exista
   en el `demo/` del addon.

### El gate que había que arreglar primero (hecho)

`start_tour` **saltea** el test si no encuentra binario de Chrome, y
`HttpCase.browser_js` saltea si falta `websocket-client`. En un runner sin
ninguno de los dos, 41 tours pasan en verde sin haber ejecutado un paso — peor
que no tenerlos, porque parece cobertura.

`PortalTourMixin` convierte los dos salteos en un error de `setUpClass` cuando
`INTN_REQUIRE_TOURS=1`, que es lo que exporta el job `portal-tours` de
`.github/workflows/odoo-tests.yml`.

> Nota histórica: este documento afirmaba que CI no corría ningún test. Eso era
> cierto al 2026-07-29 y dejó de serlo al día siguiente, con `odoo-tests.yml`.
> La capa de tours es el tercer job de ese workflow, no un gate nuevo.

---

## 1. Inventario de procesos de portal

41 procesos. La columna **Cobertura hoy** es lo que existe: `PW` = spec de Playwright,
`HTTP` = suite HttpCase de controller, `TOUR` = tour.

### A. Cuenta y registro — `intn_portal_registration`, `intn_portal_hybrid_auth`

| # | Proceso | Ruta | Cobertura hoy |
|---|---|---|---|
| A1 | Signup / login híbrido (RUC o CI, toggle de password) | `/web/signup`, `/web/login` | PW, HTTP |
| A2 | Alta de empresa (OWL `company_new_form.js`, lookup de RUC, ubicación en cascada) | `/my/company/new` | PW, HTTP |
| A3 | Alta de establecimiento (OWL `establishment_new_form.js`) | `/my/establishment/new` | HTTP |
| A4 | Alta de contacto de empresa | `/my/company/<id>/contact/new` | HTTP |
| A5 | Listado y detalle de empresas | `/my/companies`, `/my/company/<id>` | PW |

### B. Flota / cisternas — `intn_portal_fleet_requests`, `intn_portal_fleet_cistern`, `intn_fleet_cistern`

| # | Proceso | Ruta | Cobertura hoy |
|---|---|---|---|
| B1 | Alta de vehículo (OWL `portal_vehicle_app`, panel de tanque y compartimientos) | `/my/vehicle/new` | PW, HTTP |
| B2 | Edición de vehículo | `/my/vehicle/<id>/edit` | PW, HTTP |
| B3 | Alta de remolque y vínculo tractor↔remolque | `/my/trailer/new`, `/assign_trailer`, `/unlink_trailer` | PW, HTTP |
| B4 | Asignación y limpieza de conductor | `/my/vehicle/<id>/assign_driver`, `/clear_driver` | HTTP |
| B5 | Baja de vehículo | `/my/vehicle/<id>/deactivate` | HTTP |
| B6 | Solicitud fleet — habilitación | `/my/service_request/fleet/new` | PW, HTTP |
| B7 | Solicitud fleet — verificación anual / eventual / posterior | idem | PW, HTTP |
| B8 | Solicitud fleet — ONM (tipos de servicio, precios) | idem | PW, HTTP |
| B9 | Calendario: días no disponibles, validación de slot, capacidad diaria | `/unavailable_days`, `/validate_slot` | PW, HTTP |
| B10 | Campos derivados de cisterna (capacidades por compartimiento) | `/vehicle_snapshot/<id>` | PW, HTTP |
| B11 | Reemplazo de precintos | `seal_replacement` | HTTP |

### C. Catálogo y cabecera compartida — `intn_portal_fleet_requests`, `intn_service_request`

| # | Proceso | Ruta | Cobertura hoy |
|---|---|---|---|
| C1 | Catálogo de servicios: búsqueda, resolve, payload del formulario | `/my/service_request/catalog` | PW, HTTP |
| C2 | Cabecera de solicitud (organización / departamento) | `/my/service_request/departments`, header API | HTTP |
| C3 | Listado de solicitudes + quick search | `/my/service_requests` | PW |
| C4 | Reprogramación | `/my/service_request/<id>/reschedule` | PW, HTTP |
| C5 | Confirmar asistencia | `/confirm_attendance` | HTTP |
| C6 | Cancelación | `/cancel` | HTTP |
| C7 | Estimación de total | `/estimate_total` | HTTP |

### D. Revisión documental — `intn_document_review`, `intn_documents`

| # | Proceso | Ruta | Cobertura hoy |
|---|---|---|---|
| D1 | Subida de documentos del expediente | `/document_upload` | PW, HTTP |
| D2 | Resubida tras rechazo | `/document_resubmit` | PW, HTTP |
| D3 | Portal DMS: listado y descarga | `/my/documents` | PW, HTTP |

### E. Metrología — `intn_portal_metrology_dispenser_requests`, `intn_portal_metci_service_request`

| # | Proceso | Ruta | Cobertura hoy |
|---|---|---|---|
| E1 | Solicitud de picos de surtidores (geolocalización, lookup de masterdata) | `/my/service_request/metrology/new` | PW, HTTP |
| E2 | Aprobación de modelo + requisitos | `/my/metrology_dispenser_request/new` | PW, HTTP |
| E3 | Verificación inicial | `initial_verification` | PW, HTTP |
| E4 | METCI — solicitud de laboratorio | `/my/service_request/metrology/new` (METCI) | PW, HTTP |
| E5 | Observación del cliente sobre la medición | `/metrology/observation` | HTTP |
| E6 | Ficha técnica por línea | `/metrology_technical_sheet/<line_id>` | HTTP |

### F. Marcas / ONC — `intn_brand_service_requests`, `intn_onc_certification_requests`

| # | Proceso | Ruta | Cobertura hoy |
|---|---|---|---|
| F1 | ONC-FOR-001 (producto) | `/my/service_request/new?...onc_product_cert` | **TOUR**, HTTP |
| F2 | ONC-FSG-001 (sistema) | `...onc_system_cert` | **TOUR**, HTTP |
| F3 | ONC-FPE-001 (personas) | `...onc_person_cert` | **TOUR**, HTTP |
| F4 | ONN — solicitud de normas | `/my/brand_request/new` (`onn_normas`) | PW, HTTP |
| F5 | ONN — reimpresión | `reprint_onn_normas` | PW |
| F6 | Solicitud de impresión de etiquetas (formulario dinámico) | `/my/brand_print_request/new`, `/dynamic_form` | PW, HTTP |
| F7 | Control de etiquetas | `/my/brand_label_control/new` | PW |
| F8 | Certificados de lote | `/my/brand_batch_certificates` | PW |

### G. ONI — 8 formularios sobre un componente base patcheado

Todos derivan de `OniSeguridadServiceForm` vía `patch`, y todos entran por
`/my/service_request/oni/new`. Un tour por tipo de servicio, helpers compartidos.

| # | Tipo de servicio | Addon | Cobertura hoy |
|---|---|---|---|
| G1 | `oni_seguridad_industrial` | `intn_portal_oni_seguridad_industrial` | HTTP |
| G2 | `oni_envases_fm` / `oni_envases_fq` / `oni_envases_migracion` | `intn_portal_oni_envases_embalajes_service_request` | PW, HTTP |
| G3 | `oni_maquila` | `intn_portal_oni_maquila_service_request` | HTTP |
| G4 | `oni_materiales_construccion` | `intn_portal_oni_materiales_construccion` | HTTP |
| G5 | `oni_metalurgia` | `intn_portal_oni_metalurgia_service_request` | — |
| G6 | `oni_muestreo` | `intn_portal_oni_muestreo_service_request` | HTTP |
| G7 | `oni_inspeccion` (programa de inspección) | `intn_portal_oni_programa_inspeccion` | HTTP |
| G8 | `oni_textil` | `intn_portal_oni_textil_service_request` | HTTP |

### H. OIAT — `intn_portal_oiat_service_request`, `..._combustibles_lubricantes_...`

| # | Proceso | Tipo de servicio | Cobertura hoy |
|---|---|---|---|
| H1 | Solicitud de muestras | `sample_request` | PW, HTTP |
| H2 | Combustibles — normal / MIC / barcazas | `combustibles_*` | HTTP |

### I. Cuenta, cobros y verificación pública

| # | Proceso | Ruta | Cobertura hoy |
|---|---|---|---|
| I1 | Facturas + comprobante de transferencia | `/my/invoices`, `/bank_transfer_receipt` | PW, HTTP |
| I2 | Pedidos y presupuestos + búsqueda | `/my/orders`, `/my/quotes` | PW |
| I3 | Certificados: listado, detalle, descarga | `/my/certificates` | PW, HTTP |
| I4 | Verificación pública de certificado / precinto (sin login) | `/verify/...` | PW, HTTP |
| I5 | Pago Pagopar | `intn_account_pagopar` | — |

---

## 2 bis. Prueba de concepto ejecutada (2026-08-07)

Para no dar por buena la teoría, se escribió y corrió un tour real que sube adjuntos:

| Archivo | Qué hace |
|---|---|
| `intn_portal_fleet_requests/static/tests/tours/portal_document_review_tour.js` | adjunta 3 PDFs a la corrección documental y envía el formulario |
| `intn_portal_fleet_requests/tests/test_portal_document_review_tour.py` | lo levanta y verifica los `ir.attachment` resultantes |

Corrido sobre `intn_cilocal` con `ODOO_BROWSER_BIN` apuntando al Chromium de Playwright:

```
[2/9] Attach a PDF to "doc_cert_verificacion"
[3/9] "doc_cert_verificacion" holds doc_cert_verificacion.pdf
...
[8/9] Submit the corrections
[9/9] The request went back to pending review
║ TOUR intn_portal_document_review_upload SUCCEEDED ║
```

**El tour funciona.** Los 9 pasos pasan, los tres archivos entran al DOM, el submit
multipart llega al controller y la solicitud vuelve a `pending`.

### Y encontró un bug de producción en la primera corrida

La aserción del servidor falló: de los tres adjuntos, **sólo se guardó uno**.

```
AssertionError: ['doc_cert_verificacion.pdf'] != ['doc_cert_verificacion.pdf',
                 'doc_green_card_back.pdf', 'doc_green_card_front.pdf']
```

Causa: `intn_documents/models/service_request.py`

- `_intn_validate_portal_attachment_specs` (línea 93) **sí** aplana las specs con
  `type == "pair"` en sus claves `front`/`back` y por eso exige los dos lados.
- `_intn_portal_create_attachments_from_specs` (línea 152) **no** lo hace: sólo lee
  `spec.get("key")`, que una spec `pair` no tiene, y hace `continue`.

Resultado: en la corrección documental, el cliente sube frente y dorso de la cédula
verde, el formulario los acepta, y **ninguno de los dos llega a INTN**.

Alcance acotado: sólo el flujo de corrección/reenvío. La ruta de alta usa
`_get_required_attachment_specs`, que devuelve las specs planas (una clave por lado) y
no pasa por la rama rota.

Por qué no lo vio nadie: `test_portal_document_review_upload.py` postea el multipart
directo y asserta `assertGreaterEqual(len(attachments), 1)` — con un solo adjunto
guardado, pasa.

**Este es el argumento del plan entero, medido:** el primer tour con adjuntos que se
escribió encontró un bug que dos capas de tests existentes no veían.

---

## 3. Plan

### Fase 0 — Infraestructura ✅ **cerrada (2026-08-07)**

Sin esto, escribir 40 tours multiplica por 40 la duplicación que ya tiene el tour ONC.

Lo entregado:

| Pieza | Dónde |
|---|---|
| Step builders compartidos (campos, secciones, `PortalSearchSelect`, `MultiSelectTags`, adjuntos) | `intn_portal_shared_widgets/static/tests/tours/portal_tour_helpers.js` |
| `PortalTourMixin` — idioma, gate de navegador, `start_portal_tour`, `start_service_form_tour` | `intn_service_request/tests/portal_tour_common.py` |
| Ganchos `intn-mst` / `intn-mst-input` / `intn-mst-item` en `MultiSelectTags` | `intn_portal_shared_widgets/.../multi_select_tags.js` |
| `web.assets_tests` en `intn_portal_shared_widgets` y `intn_portal_fleet_requests` | sus `__manifest__.py` |
| Tour ONC y tour de corrección documental refactorizados sobre los helpers | sus `static/tests/tours/` |

Verificado: `--test-tags intn_portal_tours` → 4 tours en verde; regresión de
`intn_documents,intn_portal_fleet_requests,intn_onc_certification_requests,intn_service_request`
→ 468 tests, 0 fallos. Con `INTN_REQUIRE_TOURS=1` y sin Chrome en el `PATH`, el gate
levanta `RuntimeError` en vez de saltear.

El detalle de lo que se pidió, para referencia:

1. **Helpers JS compartidos.** El tour ONC define inline `pssInput`, `pssOption`,
   `pickOption`, `expectField`, `expectHiddenField`, `expectNoField`, `expectSection`,
   `expectNoSection`. Todos son genéricos de los widgets de
   `intn_portal_shared_widgets` (`PortalSearchSelect`, `MultiSelectTags`). Extraerlos a
   `intn_portal_shared_widgets/static/tests/tours/portal_tour_helpers.js` y hacer que el
   tour ONC los importe. Agregar helpers para lo que falta: `MultiSelectTags`, el campo
   de calendario de fleet, los lookups de masterdata, y `attachPdf(key)` /
   `expectAttached(key, name)` sobre `inputFiles` (ya escritos en el tour de la §2 bis,
   hay que moverlos ahí).
2. **Caso base Python.** `PortalTourCase` en `intn_test_http_common`, que herede de
   `PortalFleetHttpCase`, fije `lang = en_US` (los tours comparan rótulos en inglés
   porque es lo que declara el JS) y exponga `run_form_tour(category, service_type,
   tour_name)` — hoy eso está copiado en el test ONC y se va a copiar 15 veces.
3. **Gate del binario de Chrome.** Agregar en `PortalTourCase.setUpClass` un chequeo que
   **falle** (no saltee) si `ODOO_BROWSER_BIN` no resuelve a un ejecutable **y** la
   variable `INTN_REQUIRE_TOURS=1` está puesta. CI la pone; en local se sigue salteando.
   Sin esto los tours son decorativos.
4. **`web.assets_tests` por addon.** Hoy sólo `intn_onc_certification_requests` lo
   declara. Cada addon que reciba tours necesita el bloque en su `__manifest__.py`.
5. **Tag y comando.** Mantener `intn_portal_tours` como tag común y documentar en
   `AGENTS.md` el comando para correr sólo la capa de tours.

**Entregable:** el tour ONC refactorizado sobre los helpers compartidos y el caso base.
Sirve de plantilla y valida la infraestructura antes de replicarla.

### Fase 1 — Formularios de solicitud (en curso)

**Cerrado (2026-08-07): fleet, metrología y los 10 tipos ONI — 24 tours en verde.**

| Familia | Tours | Archivo |
|---|---|---|
| Fleet — arch base (verificación anual, eventual, habilitación, reemplazo de precintos) + subtipos de modificación de certificado | 5 | `intn_portal_fleet_requests/static/tests/tours/portal_fleet_form_tour.js` |
| Metrología — picos (inicial, periódica, posterior, complementario) + aprobación de modelo | 5 | `intn_portal_metrology_dispenser_requests/static/tests/tours/portal_metrology_form_tour.js` |
| ONI — los 10 tipos activos, por lo que aporta el patch de cada departamento | 10 | `intn_portal_oni_seguridad_industrial/static/tests/tours/portal_oni_form_tour.js` |
| Corrección documental con adjuntos (§2 bis) | 1 | `intn_portal_fleet_requests/static/tests/tours/portal_document_review_tour.js` |
| ONC (preexistente, refactorizado sobre los helpers) | 3 | `intn_onc_certification_requests/static/tests/tours/onc_portal_forms_tour.js` |

**Herramienta que salió de esto:** `intn_portal_form_probe`, un tour de diagnóstico en
`intn_portal_shared_widgets` que vuelca el DOM real de cualquier formulario de portal
(nombres, tipo de input, cuáles son `PortalSearchSelect`, cuáles son `file`). Escribir
un tour contra el motor de formularios a ciegas es adivinar: si un campo termina siendo
un `<input>` visible, un hidden detrás de un widget, o nada, lo decide el widget y no el
arch que uno lee. El probe convierte tres corridas fallidas en una.

**Segundo bug de producción encontrado.** Los diez formularios ONI estaban **caídos en
el navegador**: `oni_envases_form_patch.xml` conservaba un
`xpath expr="//h6[contains(., 'Sample/Service Data')]"` que dejó de matchear cuando el
commit `789ad4d8` movió ese título al getter `sampleSectionTitle` del template base. La
herencia de template falla al compilar, OWL destruye el componente raíz, y se cae *todo*
ONI —no sólo envases— porque el patch se aplica al template compartido. Arreglado
siguiendo el patrón que ese mismo commit estableció: se borró el xpath muerto y el patch
de envases ahora sobreescribe `sampleSectionTitle`, igual que ya hacía el de metalurgia.

Dos hallazgos que cambiaron el diseño de los tours, ambos medidos y no supuestos:

- `oni_catalog_id` **no** es común: maquila y programa de inspección reemplazan la
  sección entera y no lo renderizan. Estaba en el bloque común y hacía fallar a esos dos.
- Los tipos de cambio sueltos de fleet (`emblem_change`, `company_name_change`,
  `company_emblem_change`) tienen el catálogo **inactivo**: los reemplazó
  `certificate_modification` con sus subtipos. No hay tour para ellos porque no hay
  formulario que recorrer.

**Cerrado también (2026-08-07, segunda tanda): OIAT y marcas — 30 tours en verde.**

| Familia | Tours | Archivo |
|---|---:|---|
| OIAT — muestras + los 3 tipos de combustibles | 4 | `intn_portal_oiat_service_request/static/tests/tours/portal_oiat_form_tour.js` |
| Marcas — solicitud ONN + impresión de etiquetas | 2 | `intn_brand_service_requests/static/tests/tours/portal_brand_form_tour.js` |

El de impresión de etiquetas es el más valioso de los dos: los certificados de lote y
los vouchers se eligen con checkboxes, y un listener de `submit` inline junta los
marcados en dos inputs ocultos justo antes de que salga el POST.
`test_portal_brand_print_request.py` postea `batch_certificate_ids="3,7"` directo al
controller —o sea, la *salida* de ese listener—, así que el mecanismo entero podía dejar
de funcionar con todos los tests en verde mientras los clientes enviaban solicitudes sin
ningún certificado adjunto. El tour marca las casillas, envía, y el test verifica los
`ir.attachment` resultantes contra los registros que creó.

### METCI: una URL dedicada que era deriva, no diseño

`intn_portal_metci_service_request` traía su propia ruta,
`/my/metrology_service_request/new`, con su propia plantilla. La cronología
explica por qué:

| Fecha | Qué pasó |
|---|---|
| 2026-01-22 | Se crea `/my/service_request/new`, la puerta única |
| 2026-06-12 | OIAT agrega `/my/oiat_service_request/new` — primera desviación |
| 2026-07-27 | METCI copia el molde de OIAT, ruta dedicada incluida |
| 2026-07-30 | `b4b2818d` fija el patrón contrario: GET compartido, POST en `/my/service_request/<categoría>/new`, un handler por categoría |

METCI se escribió **tres días antes** del refactor que fijó el patrón, copiando
una plantilla que ya estaba fuera de él. Nadie lo migró después, y
[`propuesta-dispatcher-solicitudes-portal.md`](propuesta-dispatcher-solicitudes-portal.md)
dice explícitamente que `/my/service_request/new` es la puerta única.

Que era código muerto y no una excepción deliberada lo muestran cinco cosas:
nada enlazaba a la ruta (la única referencia en el repo era el `action` de su
propio formulario); su plantilla nunca montaba el shell OWL, así que la página
servía un formulario **sin un solo campo visible**; el catálogo de METCI ya
estaba configurado para la puerta común (`portal_header_ready`,
`portal_form_view_id`); la ruta genérica ya renderizaba bien el formulario; y
los tests del módulo ya posteaban a `/my/service_request/metrology/new`.

Se borró el controller entero, su plantilla y el paquete `portal/` del módulo.
La creación no hizo falta cablearla: el controller compartido ya despacha a
`_portal_create_metci_service_request` cuando el catálogo es
`dispenser_request`. **Los cinco tests del módulo pasan sin una sola
modificación**, que era la condición.

La ruta dedicada de OIAT se borró en la misma tanda, y estaba peor: su
plantilla **no figura en el manifest**, así que la vista ni siquiera existe en
la base. Quien entrara a `/my/oiat_service_request/new` recibía un error de
render, no una página fea. OIAT ya funcionaba por la puerta común porque sí
registró su handler.

Con las dos fuera, vuelve a haber **una sola** ruta de creación de formulario en
el portal —`/my/service_request/new`— más las de POST por categoría, que es
exactamente lo que fija
[`propuesta-dispatcher-solicitudes-portal.md`](propuesta-dispatcher-solicitudes-portal.md).

Queda un hilo de código muerto que no se tocó, para no mezclar: OIAT tiene
`models/service_request_portal_form_layout.py` (un cargador de layouts) y
`portal/_shared/views/portal_service_request_bodies.xml` que tampoco están en el
manifest — la tabla de layouts de la categoría `oiat` está vacía en la base.

---

## 3. Plan

### Fase 0 — Infraestructura ✅ **cerrada (2026-08-07)**

Sin esto, escribir 40 tours multiplica por 40 la duplicación que ya tiene el tour ONC.

Lo entregado:

| Pieza | Dónde |
|---|---|
| Step builders compartidos (campos, secciones, `PortalSearchSelect`, `MultiSelectTags`, adjuntos) | `intn_portal_shared_widgets/static/tests/tours/portal_tour_helpers.js` |
| `PortalTourMixin` — idioma, gate de navegador, `start_portal_tour`, `start_service_form_tour` | `intn_service_request/tests/portal_tour_common.py` |
| Ganchos `intn-mst` / `intn-mst-input` / `intn-mst-item` en `MultiSelectTags` | `intn_portal_shared_widgets/.../multi_select_tags.js` |
| `web.assets_tests` en `intn_portal_shared_widgets` y `intn_portal_fleet_requests` | sus `__manifest__.py` |
| Tour ONC y tour de corrección documental refactorizados sobre los helpers | sus `static/tests/tours/` |

Verificado: `--test-tags intn_portal_tours` → 4 tours en verde; regresión de
`intn_documents,intn_portal_fleet_requests,intn_onc_certification_requests,intn_service_request`
→ 468 tests, 0 fallos. Con `INTN_REQUIRE_TOURS=1` y sin Chrome en el `PATH`, el gate
levanta `RuntimeError` en vez de saltear.

El detalle de lo que se pidió, para referencia:

1. **Helpers JS compartidos.** El tour ONC define inline `pssInput`, `pssOption`,
   `pickOption`, `expectField`, `expectHiddenField`, `expectNoField`, `expectSection`,
   `expectNoSection`. Todos son genéricos de los widgets de
   `intn_portal_shared_widgets` (`PortalSearchSelect`, `MultiSelectTags`). Extraerlos a
   `intn_portal_shared_widgets/static/tests/tours/portal_tour_helpers.js` y hacer que el
   tour ONC los importe. Agregar helpers para lo que falta: `MultiSelectTags`, el campo
   de calendario de fleet, los lookups de masterdata, y `attachPdf(key)` /
   `expectAttached(key, name)` sobre `inputFiles` (ya escritos en el tour de la §2 bis,
   hay que moverlos ahí).
2. **Caso base Python.** `PortalTourCase` en `intn_test_http_common`, que herede de
   `PortalFleetHttpCase`, fije `lang = en_US` (los tours comparan rótulos en inglés
   porque es lo que declara el JS) y exponga `run_form_tour(category, service_type,
   tour_name)` — hoy eso está copiado en el test ONC y se va a copiar 15 veces.
3. **Gate del binario de Chrome.** Agregar en `PortalTourCase.setUpClass` un chequeo que
   **falle** (no saltee) si `ODOO_BROWSER_BIN` no resuelve a un ejecutable **y** la
   variable `INTN_REQUIRE_TOURS=1` está puesta. CI la pone; en local se sigue salteando.
   Sin esto los tours son decorativos.
4. **`web.assets_tests` por addon.** Hoy sólo `intn_onc_certification_requests` lo
   declara. Cada addon que reciba tours necesita el bloque en su `__manifest__.py`.
5. **Tag y comando.** Mantener `intn_portal_tours` como tag común y documentar en
   `AGENTS.md` el comando para correr sólo la capa de tours.

**Entregable:** el tour ONC refactorizado sobre los helpers compartidos y el caso base.
Sirve de plantilla y valida la infraestructura antes de replicarla.

### Fase 1 — Formularios de solicitud (en curso)

**Cerrado (2026-08-07): fleet, metrología y los 10 tipos ONI — 24 tours en verde.**

| Familia | Tours | Archivo |
|---|---|---|
| Fleet — arch base (verificación anual, eventual, habilitación, reemplazo de precintos) + subtipos de modificación de certificado | 5 | `intn_portal_fleet_requests/static/tests/tours/portal_fleet_form_tour.js` |
| Metrología — picos (inicial, periódica, posterior, complementario) + aprobación de modelo | 5 | `intn_portal_metrology_dispenser_requests/static/tests/tours/portal_metrology_form_tour.js` |
| ONI — los 10 tipos activos, por lo que aporta el patch de cada departamento | 10 | `intn_portal_oni_seguridad_industrial/static/tests/tours/portal_oni_form_tour.js` |
| Corrección documental con adjuntos (§2 bis) | 1 | `intn_portal_fleet_requests/static/tests/tours/portal_document_review_tour.js` |
| ONC (preexistente, refactorizado sobre los helpers) | 3 | `intn_onc_certification_requests/static/tests/tours/onc_portal_forms_tour.js` |

**Herramienta que salió de esto:** `intn_portal_form_probe`, un tour de diagnóstico en
`intn_portal_shared_widgets` que vuelca el DOM real de cualquier formulario de portal
(nombres, tipo de input, cuáles son `PortalSearchSelect`, cuáles son `file`). Escribir
un tour contra el motor de formularios a ciegas es adivinar: si un campo termina siendo
un `<input>` visible, un hidden detrás de un widget, o nada, lo decide el widget y no el
arch que uno lee. El probe convierte tres corridas fallidas en una.

**Segundo bug de producción encontrado.** Los diez formularios ONI estaban **caídos en
el navegador**: `oni_envases_form_patch.xml` conservaba un
`xpath expr="//h6[contains(., 'Sample/Service Data')]"` que dejó de matchear cuando el
commit `789ad4d8` movió ese título al getter `sampleSectionTitle` del template base. La
herencia de template falla al compilar, OWL destruye el componente raíz, y se cae *todo*
ONI —no sólo envases— porque el patch se aplica al template compartido. Arreglado
siguiendo el patrón que ese mismo commit estableció: se borró el xpath muerto y el patch
de envases ahora sobreescribe `sampleSectionTitle`, igual que ya hacía el de metalurgia.

Dos hallazgos que cambiaron el diseño de los tours, ambos medidos y no supuestos:

- `oni_catalog_id` **no** es común: maquila y programa de inspección reemplazan la
  sección entera y no lo renderizan. Estaba en el bloque común y hacía fallar a esos dos.
- Los tipos de cambio sueltos de fleet (`emblem_change`, `company_name_change`,
  `company_emblem_change`) tienen el catálogo **inactivo**: los reemplazó
  `certificate_modification` con sus subtipos. No hay tour para ellos porque no hay
  formulario que recorrer.

**Cerrado también (2026-08-07, segunda tanda): OIAT y marcas — 30 tours en verde.**

| Familia | Tours | Archivo |
|---|---:|---|
| OIAT — muestras + los 3 tipos de combustibles | 4 | `intn_portal_oiat_service_request/static/tests/tours/portal_oiat_form_tour.js` |
| Marcas — solicitud ONN + impresión de etiquetas | 2 | `intn_brand_service_requests/static/tests/tours/portal_brand_form_tour.js` |

El de impresión de etiquetas es el más valioso de los dos: los certificados de lote y
los vouchers se eligen con checkboxes, y un listener de `submit` inline junta los
marcados en dos inputs ocultos justo antes de que salga el POST.
`test_portal_brand_print_request.py` postea `batch_certificate_ids="3,7"` directo al
controller —o sea, la *salida* de ese listener—, así que el mecanismo entero podía dejar
de funcionar con todos los tests en verde mientras los clientes enviaban solicitudes sin
ningún certificado adjunto. El tour marca las casillas, envía, y el test verifica los
`ir.attachment` resultantes contra los registros que creó.

---|---|---|
| 1 | B6, B7, B8 — fleet: habilitación, verificación, ONM | `intn_portal_fleet_requests` |
| 2 | E1, E2, E3 — metrología y aprobación de modelo | `intn_portal_metrology_dispenser_requests` |
| 3 | G1–G8 — los 8 ONI (helpers compartidos, un tour por tipo) | cada addon ONI |
| 4 | H1, H2 — OIAT muestras y combustibles | los dos addons OIAT |
| 5 | F4, F6 — ONN normas e impresión de etiquetas | `intn_brand_service_requests` |
| 6 | E4 — METCI | `intn_portal_metci_service_request` |

### Fase 2 — Alta de entidades (en curso)

**Cerrado (2026-08-07): empresa, vehículo y remolque — 3 tours.**

Lo que hizo falta primero: **el app de vehículos no tenía dónde engancharse**.
Sus inputs se dibujan con `t-model` y nada más — sin `name` y sin `id`. Por eso
el suite de Playwright tuvo que escribir
`owlFieldInput(scope, labelPattern)`: arrancar del texto de la etiqueta y saltar
al hermano siguiente por XPath, que se rompe con cualquier cambio de markup y
depende del idioma. Los 22 inputs ahora llevan un `id` que espeja su clave de
estado, igual que el motor de formularios nombra los suyos.

Sobre el alta de empresa: `test_portal_registration_owl_mount_http.py` ya
verificaba que el `<div id="intn_portal_company_new_mount">` estuviera en el
HTML. Es más débil de lo que parece — ese div se renderiza monte o no el
componente, así que un import roto deja la página estructuralmente intacta y
funcionalmente vacía. El tour asserta los ocho campos que el componente dibuja
y que todos sigan siendo obligatorios.

**Fase 2 cerrada (2026-08-07): 6 tours** — empresa, establecimiento, contacto de
empresa, camión tanque, semirremolque y edición de vehículo.

El de establecimiento necesitó un fixture con `intn_company_ids`: sin acceso a
la empresa la ruta redirige a `/my/companies`, y lo que se mide entonces no es
el formulario sino la lista de empresas.

### Cuarto bug: el alta de vehículos salía en blanco una de cada tres veces

Al correr los tours nuevos aparecieron fallos intermitentes en el paso de
montaje. Reproducían aislados, ~1 de cada 3 corridas, y con selectores
anteriores a este trabajo — así que no eran del test.

`_t()` devuelve un `LazyTranslatedString` mientras las traducciones no cargaron,
y su `valueOf()` **lanza** si se resuelve antes de que lleguen (contrato de
`web/static/src/core/l10n/translation.js`). `portal_vehicle_app.js` tiene **123
etiquetas `_t`** consumidas con `t-esc`, y montaba en `DOMContentLoaded` sin
esperar nada: era una carrera contra el fetch de traducciones, y cuando la
perdía OWL destruía el componente raíz y el cliente veía la página vacía.

El contraste que lo confirma: el alta de empresa monta exactamente igual —`mount`
crudo en `DOMContentLoaded`— y nunca falló, porque no usa `_t` en ningún lado.

Arreglado con `await translationIsReady` antes de montar, que es el mecanismo
que el propio framework exporta. Cinco corridas seguidas en verde donde antes
fallaba una de cada tres.

Es el tipo de bug que sólo aparece en un navegador y sólo si algo carga la
página muchas veces: un `HttpCase` sirve el HTML y ve el div de montaje intacto,
y una prueba manual acierta dos de cada tres veces.

#### Alcance original

Formularios OWL fuera del motor de solicitudes, con validación propia:

- A2, A3, A4 — empresa, establecimiento, contacto (lookup de RUC, cascada
  país/departamento/ciudad).
- B1, B2, B3 — vehículo, edición, remolque (panel de tanque, compartimientos, unicidad
  de chapa contra `/api/check_unique`).

### Fase 3 — Ciclo de vida de la solicitud (en curso)

**Arrancada (2026-08-07): cancelación y listado — 3 tours.**

La cancelación es el objetivo que más valía la pena. Es un `<script>` inline
(`portal_cancel_script`) con un flujo de **dos fases**: el primer confirmar
postea a `/cancel`, y cuando el servidor responde `requires_confirmation` el
modal reemplaza su cuerpo por la advertencia de multa y espera un segundo
confirmar. Un `HttpCase` postea a `/cancel` directo —la *salida* de ese script—
así que el botón podía dejar de abrir el modal, o la segunda confirmación dejar
de pedirse (y el cliente aceptar una multa sin verla), con todo en verde.

El del listado cubre además el ida y vuelta de `/my/service_requests/quick_search`:
el buscador no es un campo del formulario sino una búsqueda viva que navega al
resultado.

### Quinto bug: el mismo `LazyTranslatedString` en tres buscadores más

Al sondear el listado apareció otra vez `Error: translation error`. El arreglo
del app de vehículos había resuelto un caso de un patrón que estaba repetido:

| Archivo | `_t` | Esperaba |
|---|---:|---|
| `intn_fleet_cistern/.../vehicles_search_mount.js` | 13 | no |
| `intn_portal_fleet_requests/.../service_requests_search_mount.js` | 21 | no |
| `intn_portal_sale_orders/.../orders_search_mount.js` | 23 | no |

Los tres montaban en `DOMContentLoaded` sin esperar traducciones. Arreglados con
`await translationIsReady`. Los dos montajes del repo que **no** tienen el
problema —alta de empresa y de establecimiento— son justamente los que usan cero
`_t`, lo que confirma el mecanismo.

Regla que sale de esto: **un montaje OWL de frontend que use `_t` tiene que
esperar `translationIsReady`**. Sin eso es una carrera contra el fetch de
traducciones, y perderla deja la página en blanco.

**Cerrada (2026-08-07): 4 tours** — cancelación simple, cancelación con multa,
listado con búsqueda viva, y disponibilidad del calendario.

El de la multa cubre la rama que decide si el cliente se entera de la penalidad
*antes* de aceptarla. Posteando a `/cancel` esa advertencia es un campo del
JSON; sólo en el navegador se puede afirmar que alguien la leyó en pantalla.

El del calendario no asserta que el widget abra, sino que **convivan días
habilitados y deshabilitados**. Es la única forma de distinguir "la consulta de
disponibilidad respondió" de "no respondió": cuando `/unavailable_days` falla o
vuelve vacío, el calendario no se rompe — habilita todos los días, y el cliente
agenda para un sábado o para un día sin capacidad.

### Reprogramar y confirmar asistencia no tienen UI en el portal

`/my/service_request/<id>/reschedule` y `/confirm_attendance` existen como rutas,
pero **ningún XML ni JS del repo las enlaza**: reprogramar es un wizard de
backoffice y confirmar asistencia no tiene botón. Playwright tampoco las
ejercita — sólo menciona los nombres de estado.

No se puede escribir un tour de algo que no se puede hacer desde la pantalla.
Su cobertura queda donde ya está, en `HttpCase`, y las rutas quedan anotadas
como candidatas a la misma revisión que METCI y OIAT: o les falta la UI, o son
huérfanas.

#### Alcance original

Tours multi-paso, ya no de un formulario sino de un recorrido:

- C1 → envío → C3: catálogo, búsqueda, resolución, listado.
- C4, C5, C6: reprogramar, confirmar asistencia, cancelar.
- B9: calendario — día no disponible, slot inválido, capacidad agotada.
- D1, D2: los pasos de UI de la revisión documental **salvo la subida del archivo**, que
  queda en HttpCase.

### Fase 4 — Cuenta y cobros ✅ **cerrada (2026-08-07): 5 tours**

| Tour | Qué guarda |
|---|---|
| Listado de pedidos | Los tres widgets OWL de la página (buscador, filtro, orden), que son los que quedaban sin montar cuando `orders_search_mount.js` perdía la carrera contra las traducciones |
| Listado de certificados | Que el cliente vea los suyos |
| Verificación pública — token válido | Que un tercero sin cuenta vea el certificado |
| Verificación pública — token inválido | Que el token **gatee**: sin este caso, el camino feliz pasaría igual aunque la ruta ignorara el token |
| Comprobante de transferencia | Que el cliente pueda adjuntar y enviar su comprobante, con archivo real |

#### El comprobante bancario: lo que costó y por qué

Lo di por bloqueado en una vuelta anterior. **Fue una mala estimación por opinar
sin leer el controller.** Lo que hacía falta era chico, pero tenía tres cosas
que sólo se ven mirando:

1. El formulario no está en la página de la factura sino en
   `bank_transfer_state_header`, que hereda de `payment.state_header` y se
   muestra en `/payment/status`.
2. Esa página resuelve la transacción desde la **sesión del navegador**
   (`payment/controllers/post_processing.py:82`, clave
   `__payment_monitored_tx_id__`), no desde la URL.
3. Sembrar la clave antes del tour no alcanza: `browser_js` llama a
   `self.authenticate(...)` **siempre**, aun con `login=None`, y eso descarta la
   sesión previa (`odoo/tests/common.py:2418` y `:2292`). La clave se inyecta
   sobreescribiendo `authenticate` en la clase de test, que es el único punto
   por donde pasa la sesión que termina usando el navegador.

El tour termina en el submit a propósito: después del POST la página entra en su
ciclo de sondeo ("Please wait…") en vez de mostrar la confirmación, así que
afirmar sobre lo que se ve después sería afirmar sobre el poller. Que el archivo
haya llegado lo verifica el test en Python, contra la factura.

Valía la pena: es la única pantalla de cobro del portal donde el cliente sube un
archivo, y no la cubría nada. `test_bank_transfer.py` verifica la máquina de
estados escribiendo el campo directo, sin pasar por el formulario.

#### Alcance original

I1, I2, I3, I4. El tour cubre navegación, filtros, estados visibles y el upload del
comprobante de transferencia; sólo la descarga del PDF queda en HttpCase.

### Fase 5 — Retiro de Playwright: la premisa era falsa

> **Corrección (2026-08-07).** Este plan decía «retirar Playwright del repo por
> completo». Al ir a ejecutarlo apareció que el suite tiene **un segundo trabajo
> que los tours no reemplazan**, y que este documento no había considerado.

**34 de los 54 specs generan capturas de documentación** — 191 llamadas a
`captureDocScreenshot`, que escriben en `docs/` bajo `docs/portal/_images` y
compañía. Hoy hay 300 PNG en `docs/`. Borrar esos specs no elimina cobertura
duplicada: apaga la documentación.

Los tours no sirven de reemplazo tal como están: `ChromeBrowser.take_screenshot`
existe (`odoo/tests/common.py:1853`) pero Odoo la usa sólo ante un fallo y
escribe en `/tmp`. Portarlo es un proyecto en sí, no un paso de esta fase.

**Y la cobertura tampoco se superpone tanto como decía este plan.** Los tours
cubren el *renderizado* del formulario; los specs de portal cubren renderizado
**más** envío completo, validaciones, y verificación en backoffice. Ejemplo
concreto: `19-onc-certificacion-portal.spec.ts` tiene nueve tests, de los cuales
los tours reemplazan dos («formulario FPE visible», «formulario FSG-001
visible») — y esos dos, además, son de los que sacan capturas.

Los 54 se reparten así:

| Rol | Specs | Los tours lo reemplazan |
|---|---:|---|
| Generan capturas de documentación | 34 | No |
| Backoffice deep + journeys | 13 | No (es la Fase 6) |
| Resto | 7 | Parcialmente |

Del último grupo, el candidato más fuerte es
`03-solicitud-fleet-cistern-vehicle-form-fields.spec.ts`: de sus 12 tests, los
tours de vehículo y remolque reemplazan los 4 de visibilidad de campos, pero no
los 8 de validación (marca obligatoria, código alfanumérico, compartimientos
fuera de rango, matrículas que no pueden coincidir).

#### La decisión: las capturas se mudan al tour

Se construyó el seam que Odoo no trae. Tres piezas:

1. `docScreenshot("dominio/nombre")` en `portal_tour_helpers.js` — un paso que
   emite un marcador por consola.
2. `PortalTourScreenshotMixin` en `intn_service_request/tests/portal_tour_screenshots.py`
   — envuelve `ChromeBrowser._handle_console` para reconocer el marcador.
3. `Page.captureScreenshot` por el websocket, y la imagen se escribe con el
   nombre que pidió el tour bajo `docs/portal/_images/`.

**Es opt-in:** sin `INTN_DOC_SCREENSHOTS=1` el marcador se emite y nadie lo
escucha. Escribir en `docs/` en cada corrida de CI ensuciaría el árbol en cada
PR, y las capturas son un entregable que se regenera a propósito.

Por qué hizo falta construirlo: `ChromeBrowser.take_screenshot` existe pero sólo
se dispara ante un error de consola —y en ese camino aborta el tour— y escribe
con nombre timestampeado bajo `config['screenshots']`. Sirve para depurar un
fallo, no para producir una imagen estable que se versiona.

#### Primer par retirado, con la receta

`19-onc-certificacion-portal.spec.ts` perdió sus dos tests de "formulario
visible", y los tours de ONC ahora regeneran las mismas dos imágenes con el
mismo nombre: `19-uat-01-formulario-onc.png` y `19-uat-07-formulario-fsg.png`.
El spec pasó de 9 tests a 7.

La receta para los que faltan:

1. En el spec, ubicar el `captureDocScreenshot({processId, filename})`.
2. En el tour equivalente, agregar
   `docScreenshot("<dominio>/<filename>")` en el mismo punto del recorrido. El
   dominio es la carpeta que ya usa `docs/portal/_images/`.
3. Regenerar con `INTN_DOC_SCREENSHOTS=1` y comparar la imagen.
4. Borrar el test del spec, en el mismo commit.

#### Envío completo: el patrón, y la restricción que apareció

Los tours ya pueden enviar un formulario y verificar que el expediente se cree.
`intn_onc_fpe001_submit` lo hace de punta a punta: llena, elige en el
`PortalSearchSelect`, acepta la declaración, envía, y aterriza en el detalle.
Los helpers `fillFields` y `submitAndExpectDetail` lo dejan en pocas líneas.

Dos cosas que costó una corrida cada una y conviene no volver a descubrir:

- El paso de llegada tiene que enganchar algo que **sólo exista en el destino**.
  `.o_portal_wrap` está también en el formulario, así que se cumple antes de que
  el navegador navegue y el tour termina afirmando sobre la pantalla que acaba
  de dejar. `submitAndExpectDetail` engancha el encabezado del detalle.
- No conviene meter el click y la espera en un mismo `run()`: la navegación
  destruye el contexto del tour a mitad del paso. Click en un paso, aserción en
  el siguiente, que es como el motor de tours espera trabajar.

**La restricción: 49 de los 54 specs comparten estado entre sus tests en serie.**
Al retirar `UAT 2: cliente envia FPE-001` —cuya cobertura el tour ya reemplaza—
el spec se rompió: ese test produce `personRequestId`, que consume `UAT 6`. Se
revirtió.

O sea que el retiro **no es test por test** en esos archivos. Para cada uno hay
tres caminos: retirar el spec entero cuando todos sus tests tengan equivalente,
hacer que los tests consumidores creen su propio registro, o dejarlo hasta que
la cadena completa esté cubierta. La primera es la más limpia y la que evita
tocar código que se va a borrar.

Los dos ya retirados (`UAT 1` y `UAT 7`) se pudieron sacar justamente porque no
producían estado compartido: sólo afirmaban y capturaban.

#### Los tres envíos de ONC, cubiertos

| Tour | Qué recorre |
|---|---|
| `intn_onc_fpe001_submit` | El más chico: llena, elige en el select, acepta y envía |
| `intn_onc_for001_submit` | Elige esquema `type_1b`, llena 18 campos y adjunta **los 11 documentos** que ese esquema exige — o sea la cadena entera: catálogo → condición evaluada en el navegador → input renderizado → archivo → payload |
| `intn_onc_fsg001_submit` | El formulario tal como quedó tras la revisión de ONC contra el papel. Es la prueba de que el reordenamiento no rompió el envío |

Los tres asertan en Python los valores guardados, que es lo que en Playwright se
verificaba abriendo el backoffice (`UAT 5` y `UAT 9`). Verificar el modelo es
más directo y más robusto que leer un campo de la vista.

Un tercer detalle que costó una corrida: `run: "edit"` tipea carácter por
carácter, y en un `<input type="date">` eso no produce una fecha válida.
`fillField` asigna el valor y dispara `input` y `change`, que sirve por igual
para inputs sueltos y para los que un componente observa con `t-model`.

#### Primer spec retirado entero: `19-onc-certificacion-portal.spec.ts`

Sus 9 tests están cubiertos: 3 envíos de portal por tours, `UAT 5` y `UAT 9`
por las aserciones de modelo de esos mismos tours, `UAT 1` y `UAT 7` por los
tours de formulario, y `UAT 4` y `UAT 6` por un **tour de backoffice** nuevo.
Las cuatro capturas que producía las produce ahora `docScreenshot`.

`start_backoffice_tour(url, tour, user)` es la pieza que faltaba: recorre el
backoffice con un usuario interno y su grupo. Recibe el usuario en vez de leerlo
de la clase porque una misma suite suele recorrer el mismo flujo con roles
distintos, que es donde están los errores de permisos.

### Sexto bug: un revisor de ONC no podía abrir un expediente

Lo encontró el tour de backoffice mientras se lo escribía. Al abrir la solicitud
desde el listado, Odoo cortaba con:

> Access Error — You are not allowed to access 'Service Request Service Catalog'
> (service.request.service.catalog) records.

`service.request.service.catalog` sólo tenía lectura para `base.group_system` y
`base.group_portal`. **Ningún usuario interno común podía leerlo**, y el
formulario de ONC muestra `request_type_id`. El listado cargaba igual, así que
el problema sólo aparece al abrir un registro.

No era específico de ONC: cualquier formulario de solicitud que muestre el
catálogo le pasaba lo mismo a cualquier usuario interno que no fuera admin.
Arreglado con lectura para `base.group_user` sobre el catálogo, sus líneas y sus
specs de adjuntos.

Por qué Playwright no lo veía: su `roleContext(browser, "onc")` usa un usuario
con más grupos que el `group_intn_onc_reviewer` pelado, así que pasaba por encima
del agujero.

#### Segundo spec retirado: `16-oiat-solicitud-muestras-portal.spec.ts`

Sus 3 tests y sus 3 capturas quedan cubiertos por `intn_oiat_progressive_submit`,
que recorre la validación progresiva completa: el botón de agregar servicio
deshabilitado, los cinco campos que `canAddService` exige, el servicio agregado,
y el envío.

Esa progresión es justamente lo que un `HttpCase` no puede ver —postea el
payload final— y es donde vive la experiencia del cliente: un botón que no se
habilita sin decir por qué es una solicitud que no se envía nunca.

Dos cosas que se llevaron una corrida cada una y quedan como aprendizaje
general:

- **Enganchar por texto no sirve.** El botón decía "Agregar servicio" en el
  spec, pero los tours fijan `en_US` y el despliegue es `es_PY`. Se le puso un
  `id` estable, igual que a `MultiSelectTags` y al app de vehículos.
- **El mixin de capturas hay que mezclarlo en cada clase.** Sin
  `PortalTourScreenshotMixin` el marcador se emite y nadie lo escucha: el tour
  pasa en verde y no escribe una sola imagen. Es la misma clase de falla
  silenciosa que el gate de `INTN_REQUIRE_TOURS` existe para evitar, y conviene
  revisarla al portar cada spec.

`pickFirstOption(hiddenName)` se sumó a los helpers para los selects donde al
tour no le importa *cuál* valor se elige sino que el widget ofrezca algo: evita
clavar una etiqueta que depende del idioma y de los datos del catálogo.

#### Tercer spec retirado: `17-oni-envases-embalajes-portal.spec.ts`

Un solo test parametrizado sobre los tres trámites de envases (FQ, FM y
migración), con sus 3 capturas. Pasó a la primera corrida — el andamiaje ya
estaba hecho.

Lo que hace valiosa esta prueba no es la mitad positiva —que cada trámite tenga
sus campos— sino **la negativa**: que no tenga los de los otros dos. Los tres
entran por el mismo componente y se distinguen sólo por lo que muestran, así que
un `t-if` que se afloja no rompe nada visible: simplemente le pide al cliente de
FQ que complete el grupo de embalaje, que es de FM.

#### Metrología: la línea del instrumento sí, el envío no

`intn_metrology_instrument_line` cubre la cadena de autocompletados —emblema →
marca → modelo, donde cada uno habilita al siguiente— más la ficha técnica. Es
cobertura nueva y de la que más importa: un `HttpCase` postea los ids ya
resueltos y nunca ejerce esa dependencia.

Hizo falta `pickMasterdataOption(field, line, term)` en los helpers: metrología
no usa `PortalSearchSelect` sino su propio widget, con la caja en
`#line_<campo>_search_<n>`, el oculto en `#line_<campo>_id_<n>` y las
sugerencias como `<button>` dentro de `.intn-portal-ac-dropdown`.

Y una lección que ya había aparecido con el submit y volvió acá: **la condición
va en el trigger, no en un `run()`**. El componente re-renderiza de forma
asíncrona tras elegir, y un `run()` se ejecuta apenas el elemento existe —que es
siempre, porque el oculto está desde el principio—. Como trigger
(`:not([value=""])`), el motor reintenta hasta que el valor esté.

**El envío quedó cubierto** (2026-08-08), y el diagnóstico de la tabla de abajo
era erróneo en su premisa. Se deja porque el camino equivocado es la parte útil:

| Hipótesis | Verificado |
|---|---|
| Falta un campo requerido | **Sí, era esto** — pero no un `[required]`: dos campos que el servidor exige y el formulario no marca |
| La validación del componente rechaza | No: `validate()` devuelve `""` |
| El `action` del formulario quedó mal | No: es `/my/service_request/metrology/new`, correcto |
| Algo intercepta el `submit` | No |
| `onSubmit` corta antes de enviar | No: llega al final y el POST sale |

El POST **sí salía**. El servidor lo rechazaba y re-renderizaba el formulario
vacío, que desde afuera es indistinguible de un botón muerto: misma página, sin
alerta visible, sin navegación. Buscar "por qué no se envía" cuando en realidad
se enviaba y volvía es lo que costó las horas.

Lo que faltaba: `line_manufacturer_id_*` y `line_operating_range_uom_*`. Ambos
son obligatorios del lado del servidor y **ninguno lleva `required` en el
formulario**, así que un cliente real que los omita recibe el mismo formulario
vacío sin explicación. Eso es un defecto de UX que sigue abierto — el tour lo
esquiva llenándolos, no lo arregla.

Dos correcciones a los helpers salieron de acá:

- el submit espera `:not([disabled])`. El shell arranca deshabilitado y habilita
  al asentarse; cliquear antes es un no-op mudo. Playwright ya lo hacía
  (`toBeEnabled({timeout: 30_000})`) y ese detalle fue la primera pista.
- `selectFirstOption` apunta al `<select>`, no a la `<option>`: los tours solo
  emparejan elementos visibles y una opción no tiene caja. Es la misma trampa que
  los inputs ocultos de `PortalSearchSelect`.

**Aun así el spec no se retira.** El tour cubre el alta con un instrumento; el
spec cubre además dos instrumentos, el rechazo sin fichas, la subsanación desde
el detalle del portal y la aprobación documental con confirmación del operador
—más seis capturas de documentación—. Falta portar esos cuatro casos.

Nota de fixture: `fleet.emblem` está vacía en una base sin demo, así que el test
siembra emblema, marca y modelo con un prefijo común. Sin eso el tour falla en
la sugerencia y parece un bug del widget cuando es falta de datos.

#### Estado del retiro

| | |
|---|---:|
| Specs al empezar | 54 |
| Retirados | 3 |
| Quedan | 51 |

`10-metrologia-picos-portal.spec.ts` sigue en pie, pero ya no por el envío:
eso quedó resuelto. Lo que falta son sus cuatro UAT de backoffice y subsanación.

Los tres retirados fueron los más aislados. De los 51 que siguen, 34 generan
capturas y 49 comparten estado en serie, así que el ritmo lo va a marcar el
tamaño de cada cadena, no la infraestructura — que ya está toda construida.

### Fase 6 — Lo que no es portal, para poder borrar `e2e/` entero (~1 semana)

Quedan 3 grupos que este plan no cubre pero que hay que resolver para que el directorio
desaparezca. No requieren tours nuevos en su mayoría:

| Grupo | Specs | Destino |
|---|---|---|
| `*-backoffice-deep` (7 specs) | fleet, metrología, mrp, oiat, sales, documentos | Son aserciones de datos y de vistas, no de DOM. Van a `TransactionCase` / `HttpCase` en Python, que es más rápido y más estable que un tour de backoffice. |
| `journeys/*` (5 specs) | cisterna, cisterna-full, brand, onc-certification, onc-post-cert | Un test Python por journey que encadena `start_tour` (portal) → operaciones de backoffice en Python → `start_tour` (backend, usuario interno) → aserciones. |
| `misc/` (2 specs) | smoke-login, integraciones transversales | `smoke-login` lo cubre cualquier tour de portal (todos loguean). Integraciones transversales → Python. |

**Cierre:** borrar `e2e/`, sacar la sección "E2E (Playwright)" de `AGENTS.md`, y quitar
`node_modules`/`playwright-report`/`test-results` del `.gitignore` y del repo.
`ODOO_BROWSER_BIN` sigue apuntando al Chromium que instaló Playwright — conviene mover
esa dependencia a un `chromium` del sistema o dejar documentado que ese binario se
conserva a propósito.

---

## 4. Riesgos

| Riesgo | Mitigación |
|---|---|
| Tours en verde sin haber corrido (sin Chrome) | Fase 0.3 — gate que falla en CI |
| Que los tours se salteen en CI sin que nadie lo note | El job `portal-tours` instala chromium y `websocket-client`, exporta `INTN_REQUIRE_TOURS=1` —que convierte cualquiera de los dos salteos en error de `setUpClass`— y falla también si la corrida termina con `0 tests` |
| Demo data faltante por addon | Revisar `demo/` al abrir cada tour; varios addons ONI no tienen |
| Los tours comparan rótulos en inglés | `PortalTourCase` fija `lang = en_US`; documentarlo |
| 41 procesos es mucho alcance | Las fases son independientes y entregables; la 1 sola ya cierra el hueco que motivó el plan |
| El `change` de `inputFiles` no burbujea | Hoy todos nuestros handlers están sobre el input; si aparece uno delegado, disparar el evento a mano con `{ bubbles: true }` |
| Se borra Playwright y aparece un hueco tarde | El borrado va commit a commit contra su tour verde, nunca en bloque al final |

---

## 5. Estimación

| Fase | Tours | Esfuerzo |
|---|---:|---|
| 0 — infraestructura | 0 (refactor) | ~1 día |
| 1 — formularios de solicitud | ~18 | ~2 semanas |
| 2 — alta de entidades | ~6 | ~1 semana |
| 3 — ciclo de vida | ~8 | ~1 semana |
| 4 — cuenta y cobros | ~5 | ~3 días |
| 6 — no-portal, para borrar `e2e/` | 5 journeys + Python | ~1 semana |
| **Total** | **~42** | **~6 semanas** |
