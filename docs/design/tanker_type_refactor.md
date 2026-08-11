# Refactor: `tanker_type` (rígido | articulado | acoplado) y retiro de `cistern_plate`

> Estado: **propuesta re-analizada contra el código actual (2026-07-24)**
> Alcance: modelo de datos de `fleet.vehicle` en la suite `intn_fleet_cistern*` + portal (backend + OWL) + reportes.
> El branch `feature/datos-historicos` **ya está mergeado en 18.0** (PR #141); su interacción se trata en §5.8.
> Abrir branch propio para este refactor.

---

## 0. Qué cambió desde la primera redacción (léase primero)

Este documento se escribió varios commits atrás. Al re-verificarlo, **casi todas las referencias de línea siguen exactas**, pero **tres cambios estructurales del código alteran las premisas y el alcance**. No los ignores:

1. **El portal OWL fue reescrito y YA separa tractor/acoplado.** En el flujo principal de creación, el tanque de un truck **se materializa como un `fleet.vehicle` separado con `is_trailer=True`**, y la chapa del tanque se guarda en el **`license_plate` de ese trailer**, no en `cistern_plate`. Esto significa que la tesis central de este doc ("`cistern_plate` es redundante con `license_plate` del portador") **ya es la dirección real del código**. `cistern_plate` sobre el truck hoy solo sobrevive en: la columna del modelo, los `related` de verification, la **ruta HTTP legacy** `portal_create_vehicle` (`portal.py:1873`, único sitio que aún lo escribe en el truck), y demo. El refactor pasó de "introducir un modelo nuevo" a "**terminar de retirar algo que ya está medio muerto**".

2. **Ya existe un subsistema multi-trailer + compartimentos/capacidad** en `fleet_vehicle.py` (`trailer_history_ids`, `current_trailer_id/ids`, `multi_trailer_enabled`, `action_assign_trailer`, ~40 ramas `if self.is_trailer:`, y todo el bloque `compartment_count`/`capacity`/`compartment_line_ids`). Consecuencia: reemplazar `is_trailer` por `tanker_type` es **mucho más caro** de lo que estimaba §3.1 (ver Decisión 1). Y `total_capacity` (§3.3) **no existe** todavía; el total se calcula inline como `sum(...)`.

3. **`feature/datos-historicos` ya está mergeado.** Los campos `tank_*` se movieron de `service_request.py` (ya no existe) a `service_request_assigned_data_vehicle.py`, y **no son `related` vivos** sino snapshots (`store=True` + compute que copia una vez desde `trailer_id.*`). Esto convierte el remap de §5.8 en un **bugfix real**, no una simple limpieza (ver §5.8).

### Decisiones (estado)

- **Decisión 1 — `is_trailer` → RESUELTA: Opción A.** `tanker_type` pasa a ser la **fuente de verdad** (Selection, `required`, `store`, default `'rigid'`), e `is_trailer` se conserva como **campo computed `store=True`, read-only**, derivado (`is_trailer = tanker_type == 'trailer'`). No se elimina `is_trailer` (hay ~40 lecturas + subsistema multi-trailer + contrato del portal que dependen de él), pero deja de ser escribible: los ~8 sitios que hoy lo escriben migran a escribir `tanker_type`. Detalle e implementación en §3.1 y §7-Fase 1.

- **Decisión 2 — política para rígidos con `license_plate` y `cistern_plate` distintas.** Sin cambios: no adivinar; volcar a log de revisión manual (§6).

- **Decisión 3 — señal `rigid` vs `articulated` → RESUELTA: Opción (a), explícita en creación.** `tanker_type` se setea en los **puntos de entrada** de creación/asignación; `action_assign_trailer` queda **neutral** (solo enlaza, no reclasifica) para no volver articulado a un rígido cuando se le enlaza su propio tanque (`include_tank` también usa `action_assign_trailer`). Regla en §3.1bis; puntos concretos en §7-Fase 1b.

---

## 1. Objetivo

Modelar correctamente que un `fleet.vehicle` puede ser un camión **rígido**, un tractor **articulado** o un **acoplado**, y retirar la duplicación de la **matrícula de circulación** del tanque (`cistern_plate`), que repite el `license_plate` del vehículo que porta el tanque.

Se **conserva** toda la identidad real del tanque (fabricante, modelo, Nº de serie, año, capacidad, compartimentos, precintos), porque —según la normativa— es información propia del tanque, distinta del chasis.

---

## 2. Fundamento regulatorio (Paraguay: Ley 5016/2014, DINATRAN, INTN/ONM)

Cuatro elementos físicos distintos, que mapean a datos distintos:

| Elemento físico | Pertenece a | Se comparte con el chasis? |
|---|---|---|
| **Placa de fábrica del tanque** (fabricante, Nº serie único, material, presión de prueba) | Tanque | No |
| **Placa/precinto metrológico INTN** (volumen certificado) | Tanque | No |
| **Chapa de circulación / patente Mercosur** | Chasis | Sí — es la matrícula del vehículo |
| **Rotulación ONU/NFPA** (panel naranja, Nº ONU, rombo) | Carga | No (concepto aparte) |

- **Rígido:** 1 chasis + 1 chapa de circulación. El tanque va sobre ese chasis, con su placa de fábrica propia.
- **Articulado:** tractor (chasis + chapa propia) + semirremolque (chasis + chapa propia **distinta**). El tanque rueda bajo la identidad de la chapa del **acoplado**.

**Conclusión:** la matrícula pertenece al chasis (`license_plate`). `cistern_plate` (rotulada en reportes como *"Matrícula/Cisterna"* / *"Trailer plate"*) es esa misma chapa de circulación → **redundante**. Nota: el portal OWL nuevo ya aplica esta conclusión (guarda la chapa del tanque en el `license_plate` del trailer).

---

## 3. Modelo de datos objetivo

### 3.1 Discriminador

Añadir `tanker_type`:

```python
tanker_type = fields.Selection(
    [
        ("rigid", "Rígido"),
        ("articulated", "Articulado (tractor)"),
        ("trailer", "Acoplado / Semirremolque"),
    ],
    string="Tipo de unidad",
    required=True,
    tracking=True,
)
```

`is_trailer` se conserva como campo **computed `store=True`, read-only**, derivado de `tanker_type` (Opción A, Decisión 1):

```python
is_trailer = fields.Boolean(
    string="Es acoplado",
    compute="_compute_is_trailer",
    store=True,       # imprescindible: se usa en dominios de búsqueda SQL
    readonly=True,
)

@api.depends("tanker_type")
def _compute_is_trailer(self):
    for v in self:
        v.is_trailer = (v.tanker_type == "trailer")
```

> **Por qué computed y no eliminado:** ~40 lecturas (`if self.is_trailer`, dominios en XML/Python, historiales, wizard, reportes, contrato del portal OWL) siguen funcionando sin tocarse. Solo se migran los **sitios de escritura**. `store=True` es obligatorio porque `is_trailer` aparece en dominios de búsqueda (`("is_trailer","=",True)`) que se resuelven en SQL. Read-only (sin `inverse`) para evitar la doble-escritura ambigua: la única fuente es `tanker_type`.

### 3.1bis — Señal `rigid` vs `articulated` (Decisión 3, resolver en Fase 0)

`is_trailer` deriva trivialmente (`== 'trailer'`), pero **distinguir `rigid` de `articulated` no es derivable** del modelo actual: el tanque propio de un rígido y un acoplado real son ambos registros `is_trailer=True` enlazados por `action_assign_trailer`.

**RESUELTO — Opción (a): clasificación explícita en creación.** `tanker_type` se fija en el punto de entrada, no en el enlace:

| Flujo de creación / asignación | `tanker_type` del vehículo motorizado |
|---|---|
| Alta de truck con tanque propio (`include_tank=1`) | `'rigid'` (default) |
| Alta de acoplado standalone (`is_trailer=True`) | `'trailer'` (es el propio acoplado) |
| Asignar **acoplado externo** a un truck (portal.py:1307 / wizard `fleet_vehicle_assign_trailer_wizard`) | setear truck → `'articulated'` |

**Regla de oro:** `action_assign_trailer` **no** cambia `tanker_type` (queda neutral). La reclasificación a `'articulated'` la hace el *caller* solo en los puntos de asignación de acoplados externos — nunca en el enlace del tanque propio del `include_tank`.

- Migración (§6): backfill marca para revisión los `is_trailer=False` con `current_trailer_ids` no vacío (candidatos a `articulated`); el resto `'rigid'`.
- **Caso borde a vigilar:** un rígido con tanque propio que además engancha un acoplado real. En `§3.2` el tractor articulado va *sin* tanque propio, así que este caso es una excepción de negocio → dejar en log de revisión manual, no auto-clasificar. Descartadas (b) marca `is_own_tank` en trailer y (c) clasificación 100% manual por mayor costo/fragilidad.

### 3.2 Dónde vive cada dato por tipo

| Tipo | Chasis (nativo) | Tanque (mismo registro) | Matrícula | Litraje |
|---|---|---|---|---|
| `rigid` | motorizado | fabricante, modelo, serie, año, capacidad, compartimentos | `license_plate` | `capacity` propio |
| `articulated` (tractor) | motorizado, **sin tanque** | — | `license_plate` propia | `total_capacity = Σ acoplados` (**nuevo**) |
| `trailer` (acoplado) | remolque + tanque | fabricante, modelo, serie, año, capacidad, compartimentos | `license_plate` propia | `capacity` propio |

### 3.3 Litraje agregado (nuevo)

`total_capacity` **no existe** hoy (el total se calcula inline como `sum(line.capacity ...)` en `fleet_vehicle.py:599,661`). Formalizarlo como campo almacenado:

```python
total_capacity = fields.Integer(
    string="Capacidad total (litros)",
    compute="_compute_total_capacity",
    store=True,
)

@api.depends("tanker_type", "capacity", "current_trailer_ids.capacity")
def _compute_total_capacity(self):
    for v in self:
        if v.tanker_type == "articulated":
            v.total_capacity = sum(v.current_trailer_ids.mapped("capacity"))
        else:
            v.total_capacity = v.capacity
```

> Reutiliza `current_trailer_ids` (Many2many computado ya existente, `fleet_vehicle.py:69`) y el feature flag `multi_trailer_enabled` (`fleet_vehicle.py:76`). Ojo: hay un subsistema de **compartimentos** (`compartment_count` l.510, `capacity` l.514, `compartment_line_ids`, validación `_check` l.577) que ya valida `Σ compartimentos == capacity`; `total_capacity` debe convivir con eso, no duplicarlo.

---

## 4. Decisiones de campos

| Campo actual | Decisión | Motivo |
|---|---|---|
| `cistern_plate` (`fleet_vehicle.py:463`) | **ELIMINAR** | Chapa de circulación = `license_plate` del portador; el portal nuevo ya no lo usa |
| `intn_fleet_vehicle_cistern_plate_unique` (SQL, `fleet_vehicle.py:34`) | **ELIMINAR** | Su columna desaparece |
| `plate_type` opción `"cistern"` (`fleet_vehicle_plate_history.py:25`) | **ELIMINAR** (dejar solo `"license"`) | El tanque ya no tiene chapa propia |
| `cistern_vin_sn` ("Cistern Chassis (VIN)") | **RENOMBRAR** → `tank_serial_no` ("Nº de serie del tanque") | El tanque no tiene chasis; es el Nº de serie de la placa de fábrica |
| `cistern_manufacturer_id` | Conservar | Fabricante del tanque (≠ del chasis) |
| `cistern_model_id` | Conservar | Modelo del tanque |
| `manufacturing_year` | Conservar | Año de fabricación del tanque |
| `capacity`, `compartment_count`, `compartment_line_ids`, `compartment_nominal_capacity` | Conservar | Dato metrológico (INTN) — subsistema ya existente |
| Precintos (`intn_fleet_cistern_seals`) | Conservar | Ya modelado aparte |
| `is_trailer` | **CONSERVAR como derivado** de `tanker_type` | Ver Decisión 1 (§0/§3.1); NO eliminar por el subsistema multi-trailer |
| `total_capacity` | **AÑADIR** | Hoy solo existe como `sum()` inline |

---

## 5. Inventario de impacto (verificado contra el código actual)

> Las líneas marcadas ✅ se confirmaron exactas. ⚠️ = corregido respecto al doc original. 🆕 = punto de contacto que el doc original omitía.

### 5.1 Modelo base — `intn_fleet_cistern/models/fleet_vehicle.py` (1350 líneas)
- ✅ Definición `cistern_plate`: **l.463**.
- ✅ `_sql_constraints` con `intn_fleet_vehicle_cistern_plate_unique`: **l.34-37** (bloque l.22-38; conviven `vin_sn` l.24, `license_plate` l.29).
- ✅ Normalización/dedup en create: **l.802-805**. En write: **l.825-827**, **l.887**, **l.902-904**, **l.918-920**.
- ✅ Constraint Python `_check_plate_uniqueness` `@api.constrains("license_plate","cistern_plate")`: decorador **l.1068**, rama cistern **l.1090-1095**.
- ✅ Bloque historial de placas `plate_type="cistern"`: **l.902-913** (`plate_type: "cistern"` en l.909) → eliminar rama cisterna.
- ⚠️ `fleet_vehicle_plate_history.py`: opción `"cistern"` en **l.25** (el doc decía l.22; l.22 es el inicio del `Selection`).
- ✅ Migración histórica que toca la columna: `migrations/18.0.1.1.3/pre-migrate.py:13-14, 77` (referencia; no reactivar sobre columna eliminada).
- 🆕 `is_trailer` def en **l.40-45**; `current_trailer_ids` en **l.69-75** (✅). No tocar el subsistema multi-trailer salvo lo de Decisión 1.
- 🆕 Subsistema compartimentos/capacidad no mencionado antes: `compartment_count` l.510, `capacity` l.514, `compartment_nominal_capacity` l.518, `_check` l.577, helpers l.609-748. Impacta §3.3.

### 5.2 Campos `related` aguas abajo (repuntear a `license_plate` del portador)
Todos existen y **ya tienen un gemelo `*_license_plate`** en el mismo modelo → colapsables:
- ✅ `intn_fleet_cistern_verification/models/tank_inspection_certificate.py:74-75` (`vehicle_cistern_plate`; gemelo `vehicle_license_plate` l.69-70)
- ✅ `.../measurement_record.py:141-142` (`vehicle_cistern_plate`; gemelo l.116-117), `:177-178` (`trailer_cistern_plate`; gemelo `trailer_license_plate` l.162-163)
- ✅ `.../hydrostatic_test.py:198-200` (`cistern_plate`; gemelo se llama **`vehicle_plate`** l.159-161 — ⚠️ naming inconsistente)
- ✅ `.../tank_inspection.py:99-100` (`vehicle_cistern_plate`; gemelo l.94-95)
- ✅ `.../fleet_vehicle_inspection.py:177` (lista `["license_plate","vin_sn","cistern_plate","truck_code"]` pasada a `fields_get`)
- 🆕 `.../visual_verification.py:220-224` (`tank_cistern_plate` vía `service_request_id.tank_cistern_plate`; **patrón distinto** — sube por el request, no por `vehicle_id`; sin gemelo `tank_license_plate`; `string="cistern plate"` en minúsculas)

> **Criterio:** repuntear cada `*.cistern_plate` a `*.license_plate` del vehículo/acoplado, y evaluar colapsar con el gemelo ya existente. El caso `visual_verification` depende del fix del snapshot en §5.8.

### 5.3 Vistas
- ✅ `intn_fleet_cistern/views/fleet_vehicle_views.xml:85, 99, 124, 203` (`cistern_plate`) — quitar; añadir `tanker_type`, `total_capacity`; visibilidad por tipo. (`is_trailer` disperso: l.27,33,37,40,43,47,55-56,59,73,118,139,149-150,163,174-175,218,220,227.)
- ✅ `intn_fleet_cistern_verification/views/cistern_hydrostatic_test_views.xml:72` (grupo "Tank Data", `invisible="has_trailer == True"`)
- ⚠️ `.../cistern_measurement_record_views.xml:98` (`vehicle_cistern_plate`), `:107` (`trailer_cistern_plate`) — nombres de campo, no `cistern_plate` pelado
- ✅ `.../cistern_tank_inspection_views.xml:68` (`vehicle_cistern_plate`, `invisible="acoplado"`; gemelo `trailer_license_plate` l.69 con `invisible="not acoplado"`), `:172`
- 🆕 `.../cistern_visual_verification_views.xml:208` (`tank_cistern_plate`) — omitido en el doc original
- ✅ `intn_fleet_cisterns/views/fleet_vehicle_cistern_overview_views.xml:13`
- ✅ Portal OWL template: `intn_fleet_cistern/static/src/xml/portal_vehicle_app_templates.xml:194` (`state.vehicle.cistern_plate`, bajo `t-if="!state.vehicle.is_trailer"`), `:263` (`state.cistern_plate`)

### 5.4 Reportes (certificados legales — validar render)
- ✅ `intn_base/intn_inspection_certificate/reports/inspection_certificate_report.xml:184` (`vehicle_id.cistern_plate`; label "Matrícula/Cisterna" l.181)
- ✅ `intn_fleet_cistern_certificates/reports/certificate_verification_report.xml:246` (`vehicle_id.cistern_plate`; label "Trailer plate" l.243)
- ✅ `intn_fleet_cistern_verification/reports/tank_inspection_certificate_report_template.xml:166` (`vehicle_cistern_plate`; label "Matrícula/Cisterna" l.163)
- ✅ `.../tank_inspection_report_template.xml:216` (`vehicle_cistern_plate` en rama `t-else`; l.212 `t-if="s.acoplado"` → `trailer_license_plate` l.213)

### 5.5 Portal / controladores
**⚠️ Cambio arquitectónico clave:** el flujo de creación principal ya **no guarda `cistern_*` en el truck**; crea un **trailer `is_trailer=True` separado** y lo enlaza (`action_assign_trailer`). `cistern_plate` en el truck solo lo escribe la **ruta HTTP legacy**.

Backend Python (líneas ✅ exactas):
- `intn_fleet_cistern/controllers/portal.py`:
  - Snapshot OWL: `is_trailer` l.348, `cistern_plate` l.357.
  - `_portal_vehicle_form_payload` (edit): l.715, `cistern_vin_sn` l.736.
  - Normalización: l.762-765.
  - Aliases legacy `tank_*` (solo fallback, el frontend nunca los emite): l.816-817, 823, 832, 871, 879, 882.
  - **Tank → trailer separado**: `_portal_tank_trailer_vals_from_post` l.868-902 → mapea `cistern_plate → license_plate` (l.881-883) y `cistern_vin_sn → vin_sn` (l.878-880) del trailer; **no setea el `cistern_plate` del trailer**.
  - API OWL create: `is_trailer` l.1193, `check_vals["cistern_plate"]` l.1255-1256, `action_assign_trailer` l.1304-1306 (copia `capacity` al truck l.1292).
  - 🆕 **Ruta HTTP legacy** `portal_create_vehicle` l.1805: **único sitio que escribe `cistern_plate` en el truck** (l.1820, l.1872-1873). Candidata a retiro.
- `intn_portal/intn_portal_fleet_cistern/portal/_shared/controllers/cistern_service_request_mixin.py`: ✅ l.33 (mensaje constraint duplicado), ✅ l.808 (`check_vals["cistern_plate"]`); `_portal_build_and_create_truck` l.764, `_portal_build_and_create_trailer` l.847 (misma lógica tank→trailer).

🆕 Capa OWL (omitida por completo en el doc original — es la ruta de creación principal hoy):
- `static/src/js/_shared/vehicle_form_contract.js`: `TANK_FORM_FIELDS` con `cistern_vin_sn` l.31, `cistern_plate` l.33; `is_trailer` l.142; `validateTankFields` l.214-224.
- `static/src/js/portal_vehicle_app/portal_vehicle_app.js`: estado `cistern_plate` l.971-972, unique-check l.1183-1189/1264-1265, `is_trailer` l.1305, `isTrailer` l.2955.
- `static/src/js/portal_vehicle_app/portal_tank_data_panel.js`: `t-model` `cistern_vin_sn` l.72-77, `cistern_plate` l.90-95; comentario l.15 ("Tank fields map to a separate is_trailer vehicle on submit").

### 5.6 Datos demo
- ⚠️ `intn_fleet_cistern/demo/fleet_vehicle_trailer_demo.xml`: `is_trailer` l.7, 20, 56, **69** (4 registros, no 3); `cistern_plate` l.9, 22, 58.
- ⚠️ `intn_fleet_cistern/demo/fleet_portal_users_demo.xml`: `cistern_plate` en 12 registros (l.227-415 ✅) + **`is_trailer` en 20 registros más** (l.433-624) no contados antes.

### 5.7 Tests a actualizar (**38 archivos**, no ~30)
Todos existen. El doc original **subestimaba el alcance**. Lista corregida:

Listados y confirmados con uso: `intn_fleet_cistern/tests/{test_fleet_vehicle_compartments, test_fleet_vehicle_uniqueness, test_portal_vehicle_company_scope_http}.py`; `intn_fleet_cistern_verification/tests/{test_cistern_confirm_flows, test_cistern_technician_operational_acl, test_cistern_technician_vehicle_access, test_cistern_workflow_gates, test_document_review_fleet_integration, test_onm_visual, test_report_rendering, test_tank_inspection_flows, test_tank_inspection_line_sync}.py`; `intn_fleet_cistern_certificates/tests/{test_report_rendering, test_onm_measurement}.py`; `intn_fleet_cistern_constancy/tests/test_report_rendering.py`; `intn_fleet_cistern_seals/tests/{test_report_rendering, test_seal_flows, test_seal_report_wizard}.py`; `intn_fleet_cistern_fines/tests/{test_seal_return_auto_fine, test_fleet_vehicle_service_request_fine_block}.py`; `intn_base/intn_inspection_certificate/tests/test_report_rendering.py`; `intn_base/intn_service_request/tests/{test_certificate_service_request_finalize, test_service_request_finalize_guards}.py`; `intn_portal/intn_portal_fleet_requests/tests/{common, test_fleet_service_request_mixins, test_portal_fleet_vehicle_service_request, test_portal_vehicles_and_create, test_portal_service_request_pages, test_portal_fleet_cancel}.py`; `intn_portal/intn_bank_transfer_fleet_bridge/tests/test_bridge.py`.

🆕 **Omitidos en el doc original** (usan `is_trailer`): `intn_fleet_cistern_fines/tests/{test_fleet_vehicle_fine, test_report_rendering}.py`; `intn_fleet_cistern/tests/test_portal_vehicle_deactivate_http.py`; **todo `intn_fleet_seal_ranges/tests/{test_issue_gates, test_report_rendering, test_seal_homologation}.py`**; `intn_portal_fleet_requests/tests/{test_certificate_modification_autofill, test_onm_enabling_form}.py`.

⚠️ Sobre-contados por el doc (no usan los campos): `intn_fleet_cistern_verification/tests/{test_fleet_vehicle_inspection_line_traceability, test_tank_inspection_portal_certificate}.py`.

### 5.8 Interacción con `feature/datos-historicos` (ya mergeado)
Los campos `tank_*` **se movieron** a `intn_portal_fleet_requests/models/service_request_assigned_data_vehicle.py` (el `service_request.py` del doc ya no existe). **No son `related`**: son `fields.Char/Integer` con `store=True, compute="_compute_vehicle_values"` (l.91-118) que copian **una sola vez** desde `trailer_id.*` (foto histórica).

| Campo `tank_*` | def | Origen actual | Acción tras refactor |
|---|---|---|---|
| `tank_cistern_plate` | :72 | `trailer_id.cistern_plate` (:115) | ⚠️ **BUGFIX** → `trailer_id.license_plate` |
| `tank_vin_sn` | :60 | `trailer_id.cistern_vin_sn` (:113) | → `trailer_id.tank_serial_no` |
| `tank_cistern_manufacturer_id` | :48 | `trailer_id.cistern_manufacturer_id.name` (:109) | sin cambio |
| `tank_model_id` | :54 | `trailer_id.cistern_model_id.name` (:112) | sin cambio |
| `tank_manufacturing_year` | :66 | `trailer_id.manufacturing_year` (:114) | sin cambio |
| `tank_compartment_count` | :78 | `trailer_id.compartment_count` (:116) | sin cambio |
| `tank_capacity` | :84 | `trailer_id.capacity` (:117) | sin cambio |

> **Hallazgo crítico:** el portal OWL nuevo mapea la chapa del tanque al `license_plate` del trailer y **deja `trailer_id.cistern_plate` vacío**. Por lo tanto `tank_cistern_plate` (que lee `trailer_id.cistern_plate`) **ya está devolviendo vacío** para todo activo creado por el portal nuevo. El remap `→ trailer_id.license_plate` no es cosmético: **corrige un dato hoy roto**. `tank_license_plate` no existe (el doc lo listaba; el campo real es `tank_cistern_plate`).

---

## 6. Plan de migración de datos

Módulo objetivo: `intn_fleet_cistern`, nueva versión (p.ej. `18.0.1.2.0`), `migrations/<ver>/pre-migrate.py` + `post-migrate.py`.

1. **Backfill `tanker_type`** desde `is_trailer`:
   - `is_trailer = TRUE` → `'trailer'`.
   - `is_trailer = FALSE` → default `'rigid'`; marcar para revisión manual los que tengan `current_trailer_ids` (candidatos a `'articulated'`).
   - Si se adopta la opción recomendada de Decisión 1 (`tanker_type` fuente, `is_trailer` derivado `store=True`), este backfill es el que "siembra" el valor y luego `is_trailer` se recalcula.
2. **Consolidar matrícula:** registros con `cistern_plate` no nula y `license_plate` nula → copiar `cistern_plate` a `license_plate` (respetando unicidad/normalización). Ambas pobladas y **distintas** → volcar a log/tabla temporal para revisión manual (no adivinar). Nota: gran parte de los activos creados por el portal nuevo ya tienen la chapa en `license_plate` del trailer, así que este paso afecta sobre todo a datos legacy/HTTP.
3. **Renombrar columna:** `cistern_vin_sn` → `tank_serial_no` (`ALTER TABLE ... RENAME COLUMN` en pre-migrate).
4. **Historial de placas:** convertir/relabelar filas `plate_type='cistern'` a `'license'` o archivarlas según negocio.
5. **Drop** de constraint `intn_fleet_vehicle_cistern_plate_unique` y de la columna `cistern_plate` (post-migrate, tras validar consolidación). Guardar respaldo en tabla temporal antes del drop.

> Todas las transformaciones en SQL en pre/post-migrate para no depender del ORM durante el upgrade.

---

## 7. Plan de implementación por fases

**Fase 0 — Preparación / decisiones**
- ✔ **Decisión 1 resuelta: Opción A** (is_trailer computed store, read-only; ver §3.1).
- ✔ **Decisión 3 resuelta: Opción (a)** (clasificación explícita en creación; `action_assign_trailer` neutral; ver §3.1bis).
- Confirmar con negocio: (a) `cistern_vin_sn` = Nº serie del tanque ✔ (asumido); (b) política rígidos con placas distintas (Decisión 2); (c) uso real de `multi_trailer_enabled` en producción; (d) si se puede **retirar la ruta HTTP legacy** `portal_create_vehicle` (§5.5) o hay que migrarla al modelo trailer-separado.

**Fase 1 — Modelo (Opción A)**

*1a. Añadir el discriminador.*
- Añadir `tanker_type` (Selection `rigid`/`articulated`/`trailer`, `required=True`, `tracking=True`, default `'rigid'`; §3.1).
- Convertir `is_trailer` a `compute="_compute_is_trailer", store=True, readonly=True` con `@api.depends("tanker_type")` (§3.1). **No** añadir `inverse`.
- Añadir `total_capacity` (compute store; §3.3), cuidando no chocar con la validación de compartimentos existente (`_check` l.577).

*1b. Migrar los ~8 sitios de ESCRITURA de `is_trailer` a escribir `tanker_type`* (el resto de lecturas no se toca):

| Sitio | Hoy escribe | Debe escribir |
|---|---|---|
| `intn_fleet_cistern/controllers/portal.py:1217` (API create, vehículo principal) | `"is_trailer": is_trailer` | `"tanker_type": "trailer" if is_trailer else "rigid"` (Decisión 3: rigid por default; articulado se setea al asignar acoplado externo, no aquí) |
| `.../portal.py:1307+` (asignar acoplado externo a truck) y wizard `fleet_vehicle_assign_trailer_wizard` | — (solo enlaza) | setear `truck.tanker_type = "articulated"` en el *caller* (NO dentro de `action_assign_trailer`) |
| `.../portal.py:876` (`_portal_tank_trailer_vals_from_post`, tanque→trailer) | `"is_trailer": True` | `"tanker_type": "trailer"` |
| `.../portal.py:1855`, `:1928` (ruta HTTP legacy `portal_create_vehicle`) | `"is_trailer": is_trailer` | `"tanker_type": ...` (o retirar la ruta, Fase 0-d) |
| `intn_portal_fleet_cistern/.../cistern_service_request_mixin.py:797` (`_portal_build_and_create_truck`) | `"is_trailer": False` | `"tanker_type": "rigid"` (o `articulated` según Decisión 3) |
| `.../cistern_service_request_mixin.py:869` (`_portal_build_and_create_trailer`) | `"is_trailer": True` | `"tanker_type": "trailer"` |
| Form backoffice `intn_fleet_cistern/views/fleet_vehicle_views.xml` (checkbox `is_trailer`) | widget editable | reemplazar por widget `tanker_type` (el `is_trailer` queda read-only) |
| Demo `demo/fleet_vehicle_trailer_demo.xml` (l.7,20,56,69), `demo/fleet_portal_users_demo.xml` (l.433-624) | `is_trailer eval="True"` | `<field name="tanker_type">trailer</field>` |
| Tests que crean con `is_trailer=True/False` (§5.7) | `is_trailer=...` | `tanker_type=...` |

> Nota `portal.py:348` (snapshot OWL) es **lectura** (`bool(vehicle.is_trailer)`): NO se toca; sigue leyendo el computed. El payload JS `is_trailer` (contrato frontend) también puede quedarse: el backend lo traduce a `tanker_type` en el create. Alternativa más limpia (opcional): renombrar la clave del contrato a `tanker_type` en `vehicle_form_contract.js` + `portal_vehicle_app.js` + `portal_tank_data_panel.js`.

*1c. Retirar `cistern_plate`.*
- Quitar el campo (l.463), su `_sql_constraint` (l.34-37), la rama de historial `plate_type="cistern"` (l.902-913) y la normalización asociada (l.802-805, 825-827, 918-920).
- Ajustar `_check_plate_uniqueness` (l.1068) para cubrir solo `license_plate`/`vin_sn`.
- Quitar opción `"cistern"` de `fleet_vehicle_plate_history.py:25`.

**Fase 2 — Campos derivados**
- Repuntar `related` de §5.2 a `license_plate`; colapsar los `*_cistern_plate` redundantes (ojo naming `vehicle_plate` en hydrostatic).
- Arreglar `tank_cistern_plate` → `trailer_id.license_plate` (§5.8, bugfix) y `visual_verification` en consecuencia.

**Fase 3 — Vistas y portal**
- Backoffice: `tanker_type`, `total_capacity`, visibilidad por tipo.
- Portal Python: retirar/migrar ruta legacy `portal_create_vehicle`; el flujo OWL ya crea trailer separado.
- Portal OWL (§5.5): quitar `cistern_plate`/`cistern_vin_sn` de `TANK_FORM_FIELDS`, `portal_tank_data_panel.js`, `portal_vehicle_app.js`, template; el tanque ya se envía como trailer.

**Fase 4 — Reportes**
- Actualizar los 4 templates (§5.4) para imprimir `license_plate` del portador; verificar labels ("Matrícula/Cisterna", "Trailer plate").

**Fase 5 — Migración**
- Implementar pre/post-migrate (§6). Probar upgrade sobre copia de BD real.

**Fase 6 — Demo + Tests**
- Actualizar demo (§5.6) y los **38 tests** (§5.7), incluido `intn_fleet_seal_ranges/tests/`. Correr `test_report_rendering` de cada módulo.

**Fase 7 — Validación**
- Ver checklist §8.

---

## 8. Checklist de validación

- [x] Decisión 1 tomada: Opción A (is_trailer computed store, read-only, derivado de tanker_type).
- [x] Decisión 3 tomada: Opción (a) (clasificación explícita en creación; action_assign_trailer neutral).
- [ ] `action_assign_trailer` no modifica `tanker_type` (test: enlazar tanque propio de un rígido lo mantiene `rigid`).
- [ ] Asignar acoplado externo (portal + wizard) deja el truck en `articulated`.
- [ ] `is_trailer` no escribible: `grep -rn '"is_trailer":\|is_trailer\s*=\|name="is_trailer".*eval' custom_addons/` sin escrituras vivas (solo lecturas y el compute).
- [ ] `tanker_type` con default y `required` respetado; ningún registro con `tanker_type` NULL tras backfill.
- [ ] Upgrade del módulo sin errores sobre copia de BD de producción.
- [ ] Ningún registro pierde matrícula (conteo `license_plate` no nulo antes/después ≥).
- [ ] Registros con placas distintas quedaron en el log de revisión manual (ninguno silenciado).
- [ ] Los 4 reportes renderizan con la matrícula correcta (rígido y articulado).
- [ ] `total_capacity` correcto en articulado (suma de acoplados) y rígido (= capacity), sin romper la validación de compartimentos existente.
- [ ] `tank_cistern_plate` deja de venir vacío (bugfix §5.8) para activos del portal nuevo.
- [ ] Alta de vehículo desde portal (OWL) funciona para los 3 tipos; ruta legacy retirada o migrada.
- [ ] Suite de tests en verde (`intn_fleet_cistern*`, `intn_fleet_seal_ranges`, `intn_portal_fleet_*`, `intn_base/*`).
- [ ] `grep -rn "cistern_plate" custom_addons/` sin resultados vivos (solo migración/respaldo).

---

## 9. Fuera de alcance (mejoras futuras)

- **Rotulación ONU/NFPA estructurada** (Nº ONU, clase ADR, panel naranja). Hoy solo existe `product_to_transport` (texto/Many2one). Modelado aparte.
- Placa de fábrica del tanque como campos adicionales (material, presión de prueba) si se requiere trazabilidad completa de la chapa del fabricante.
- Eliminación total de `is_trailer` (si Decisión 1 opta por conservarlo derivado): reescritura del subsistema multi-trailer para pivotar sobre `tanker_type`. Cambio grande, no urgente.
