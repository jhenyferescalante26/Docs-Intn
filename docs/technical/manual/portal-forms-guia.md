# Guía integral — nuevo formulario portal unificado (OWL)

Guía paso a paso para añadir un trámite al formulario unificado `/my/service_request/new` con cabecera Organismo / Departamento / Categoría / Producto y **cuerpo OWL declarativo**.

**Referencias de implementación:** `enabling` (fleet, vista base), `emblem_change` (fleet, herencia xpath), `periodic` (metrología), `onc_product_cert` (ONC).

Convenciones de carpetas: [Estructura](portal-forms-estructura.md).

---

## Arquitectura

```{mermaid}
sequenceDiagram
    participant Browser
    participant Header as service_request_header
    participant API as header_api / form_payload
    participant Shell as ServiceRequestFormShell
    participant Engine as PortalServiceFormView
    participant Arch as PortalFormArchNode
    participant Widgets as intn_portal_form_fields / widgets

    Browser->>Header: elegir producto
    Header->>API: GET catalog/form_payload?catalog_id=
    API-->>Header: header, form.view (arch+fields), initial_data
    Header->>Shell: event intn-portal-header-locked
    Shell->>Engine: props view + config + initialData
    Engine->>Arch: archTree + formView
    Arch->>Widgets: field / widget del ir.ui.view
    Browser->>API: POST service_type=catalog_id
```

**QWeb** solo provee el shell mínimo (form POST, CSRF, `owl-component` cabecera y shell). **El cuerpo del trámite es OWL** renderizado por `PortalServiceFormView` desde **`ir.ui.view`** enlazado en catálogo (`portal_form_view_id`).

### Objetos por capa

| Capa | Objeto | Rol |
|------|--------|-----|
| Shell | `ServiceRequestFormShell` | Tabs, estimate, slot (fleet), resuelve `PortalServiceFormView` |
| Engine | `PortalServiceFormView` (`intn_service_request`) | Parser de arch, `PortalFormRecord`, validate/prepareSubmit |
| Arch renderer | `PortalFormArchNode` | Recorre el árbol del arch; props `archNode` + `formView` |
| Vista BD | `ir.ui.view` form en catálogo | Campos `<field>` y `<widget name="portal_*"/>` |
| Fields | `intn_portal_form_fields` | Inputs Bootstrap por tipo Odoo |
| Widgets | `intn_portal_form_widgets` | Bloques de dominio (vehículo, sucursal, metrología, ONC) |
| Config | `_portal_get_form_config()` + catálogo | Flags de visibilidad en JS (no `config` en XML) |

### Trámite nuevo (patrón recomendado)

1. **Python** — `_inherit` `service.request`: `_portal_get_form_config()`, hooks `_portal_validate_portal_values` / `_portal_prepare_portal_create_vals` si aplica.
2. **`views/portal_*_form_views.xml`** — vista form base + herencias xpath para variantes.
3. **`data/service_catalog_*_portal_views.xml`** — asignar `portal_form_view_id` en catálogo (`noupdate="0"`).
4. **Widgets (solo si hace falta UI nueva)** — registrar en `static/src/portal_form_engine/*_portal_widgets.js`.

Sin `registry.js` por trámite, sin `Component` monolítico por tipo, sin `portal_owl_component` por clave.

**Legacy:** si `portal_form_view_id` está vacío, el shell intenta resolver `portal_owl_component` en `intn_portal_service_forms` (deprecado; bases antiguas migradas en `18.0.1.8.0` fleet / `18.0.1.6.0` metrología / `18.0.1.3.0` ONC).

**Submit:** fleet con tab adjuntos envía desde `PortalAttachmentsPanel`; metrología y ONC envían desde el footer del shell.

---

## Índice de fases

| Fase | Tema |
|------|------|
| 0 | Análisis previo |
| 1 | Tipo de servicio (`selection_add`) |
| 2 | Producto comercial |
| 3 | Organismo y departamento (cabecera) |
| 4 | Catálogo y `portal_form_view_id` |
| 5 | Vista portal (`ir.ui.view`) y widgets |
| 6 | Shell de página (QWeb mínimo) |
| 7 | Assets (`web.assets_frontend_lazy`) |
| 8 | Comportamiento frontend por familia |
| 9 | Controller y POST |
| 10 | Tests |
| 11 | i18n y documentación de proceso |
| 12 | Verificación manual |
| Anexo A | Metrología — pasos adicionales |
| Anexo B | ONC — pasos adicionales |
| Anexo C | Legacy (solo mantenimiento) |

---

## Sección 0 — Antes de codificar

### Checklist de análisis

| Pregunta | Ejemplo |
|----------|---------|
| ¿`service_category`? | `fleet`, `metrology`, `brand` (ONC) |
| ¿`form_key` (`service_type`)? | `emblem_change`, `periodic`, `onc_product_cert` |
| ¿Módulo dueño del trámite? | `intn_portal_fleet_requests`, `intn_portal_metrology_dispenser_requests`, `intn_onc_certification_requests` |
| ¿Campos de negocio nuevos en `service.request`? | Vehículo, líneas metrología, esquema ONC |
| ¿Adjuntos obligatorios? | Tab adjuntos fleet; adjuntos en widget ONC |
| ¿Agendamiento (slot/calendario)? | `annual_verification` sí; `emblem_change` no |
| ¿Widget nuevo o reutilizar arch existente? | Variante xpath vs. `<widget>` nuevo |
| ¿UI condicional? | Flag en `_portal_get_form_config()` |

### Árbol de decisión

```
Nuevo trámite en formulario unificado
├── service_category = fleet
│   ├── ¿Campos similares a otro trámite fleet?
│   │   ├── Sí → herencia xpath sobre portal_form_fleet_base + portal_form_view_id
│   │   └── No → ampliar vista base o añadir widget en fleet_portal_widgets.js
│   └── Create/validación en portal/_shared/controllers/service_request.py
├── service_category = metrology
│   └── portal_form_metrology_base + widget portal_metrology_form (delegado legacy)
└── service_category = brand (ONC)
    └── portal_form_onc_base + widget portal_onc_form + override POST onc_create.py
```

### Glosario obligatorio

| Término | Significado |
|---------|-------------|
| `form_key` | Clave técnica; mismo string que `service.request.service_type` |
| `catalog_id` | ID de `service.request.service.catalog`; valor POST `service_type` |
| `portal_header_ready` | Producto con `intn_organization_id` e `intn_department_id` |
| `portal_form_view_id` | Vista `ir.ui.view` form renderizada por el motor OWL |
| `portal_owl_component` | **Legacy** — clave registry cuando no hay `portal_form_view_id` |
| `portal_form_config` | JSON en catálogo; fusiona con `_portal_get_form_config()` |
| `form.view` (payload) | `{ arch, fields, view_id, model, field_names }` serializado desde la vista |
| `initial_data` | Masterdata para widgets (vehículos, estimate, header metrología, …) |

**Regla crítica:** en POST y tests, `service_type` = `str(catalog.id)`. El `form_key` viaja en `form.form_key` del payload JSON.

---

## Fase 1 — Tipo de servicio

Registrar el valor en `selection_add` del modelo de la familia (`fleet_vehicle_service_request.py`, modelos metrología u ONC).

```python
service_type = fields.Selection(
    selection_add=[("emblem_change", "Emblem Change")],
    ondelete={"emblem_change": "cascade"},
)
```

---

## Fase 2 — Producto comercial

Crear `product.template` con `intn_show_in_service_list=True` en `intn_portal_service_products/data/` (u ONC en su módulo).

---

## Fase 3 — Organismo y departamento (cabecera)

Asignar `intn_organization_id` e `intn_department_id` en el producto. Verificar `portal_header_ready=True` en catálogo. No duplicar selects de cabecera en el cuerpo.

---

## Fase 4 — Catálogo y vista portal

### Catálogo base

`data/service_catalog_*_data.xml` — fila con `service_category`, `service_type`, `main_product_id`:

```xml
<record id="service_catalog_fleet_enabling" model="service.request.service.catalog">
    <field name="name">Fleet: Enabling</field>
    <field name="service_category">fleet</field>
    <field name="service_type">enabling</field>
    <field name="main_product_id" ref="intn_portal_service_products.product_template_fleet_enabling"/>
</record>
```

### Enlace vista portal

`data/service_catalog_*_portal_views.xml` — **`noupdate="0"`** para que upgrades actualicen bases existentes:

```xml
<odoo noupdate="0">
    <record id="service_catalog_fleet_enabling" model="service.request.service.catalog">
        <field name="portal_form_view_id" ref="portal_form_fleet_base"/>
    </record>
    <record id="service_catalog_fleet_emblem_change" model="service.request.service.catalog">
        <field name="portal_form_view_id" ref="portal_form_fleet_emblem_change"/>
    </record>
</odoo>
```

### Campos relevantes del catálogo

| Campo | Uso |
|-------|-----|
| `portal_form_view_id` | **Obligatorio** — vista form del motor OWL |
| `portal_form_config` | JSON opcional; sobreescribe flags de `_portal_get_form_config()` |
| `portal_create_handler` | Método Python opcional para POST no genérico |
| `portal_owl_component` | Legacy — ignorado si hay `portal_form_view_id` |
| `portal_form_layout_id` | Deprecado |

### Config en Python (fleet)

```python
def _portal_get_form_config(self):
    config = super()._portal_get_form_config()
    if self.service_category == "fleet":
        stype = (self.service_type or "").strip()
        config.update({
            "requires_vehicle": stype in ("enabling", "annual_verification", ...),
            "allow_vehicle_creation": stype == "enabling",
            "show_enabling_attachments": stype == "enabling",
            "show_emblem_fields": stype in ("emblem_change", "company_emblem_change"),
        })
    return config
```

Los flags se aplican en `PortalFormRecord.fieldConfigVisibility()` — **no** poner `invisible="not config.requires_vehicle"` en el XML de la vista (Odoo no conoce `config` en arch backend).

### Descriptor (`catalog._portal_form_descriptor()`)

Con `portal_form_view_id`:

```python
{
    "catalog_id": 5,
    "form_key": "enabling",
    "service_category": "fleet",
    "owl_component": "portal_form",
    "config": { ... },
    "view": {
        "arch": "<form>...</form>",
        "fields": { "transport_type": { "type": "selection", ... }, ... },
        "view_id": 3275,
        "model": "service.request",
        "field_names": ["transport_type", "appointment_date", ...],
    },
}
```

### Orden en `__manifest__.py` (data)

```python
"data": [
    "data/portal_header_organization_data.xml",
    "data/service_catalog_*_data.xml",
    "views/portal_*_form_views.xml",             # ir.ui.view (antes del enlace)
    "data/service_catalog_*_portal_views.xml",   # portal_form_view_id
    "portal/_shared/views/portal_templates.xml",
],
```

### Criterio de aceptación

```
GET /my/service_request/catalog/form_payload?catalog_id=<id>
```

JSON con `ok`, `form.owl_component == "portal_form"`, `form.view.arch` no vacío, `initial_data`.

---

## Fase 5 — Vista portal y widgets

### Vista form (fleet)

`views/portal_fleet_form_views.xml`:

```xml
<record id="portal_form_fleet_base" model="ir.ui.view">
    <field name="name">service.request.portal.fleet.base</field>
    <field name="model">service.request</field>
    <field name="priority">1000</field>
    <field name="arch" type="xml">
        <form js_class="intn_portal_form">
            <group>
                <field name="transport_type"/>
                <widget name="portal_branch_partner"/>
                <widget name="portal_vehicle_selection"/>
                <field name="capacity" readonly="1"/>
                <field name="appointment_date" widget="portal_datetime_local"/>
                <field name="product_to_transport"/>
                <widget name="portal_service_location"/>
                ...
            </group>
        </form>
    </field>
</record>

<record id="portal_form_fleet_emblem_change" model="ir.ui.view">
    <field name="inherit_id" ref="portal_form_fleet_base"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='requested_emblem_id']" position="attributes">
            <attribute name="required">1</attribute>
        </xpath>
    </field>
</record>
```

### Elementos soportados en arch

| Tag | Comportamiento |
|-----|----------------|
| `<field>` | Resuelto vía `intn_portal_form_fields` (tipo Odoo o `widget="portal_*"`) |
| `<widget name="portal_*"/>` | Resuelto vía `intn_portal_form_widgets` |
| `<group>`, `<form>`, `<separator>`, `<notebook>/<page>` | Contenedores recursivos |

### Widgets fleet existentes

| Widget | Archivo |
|--------|---------|
| `portal_branch_partner` | `fleet_portal_widgets.js` |
| `portal_vehicle_selection` | `fleet_portal_widgets.js` (incluye modales camión/acoplado) |
| `portal_service_location` | `fleet_portal_widgets.js` |

Registrar widget nuevo:

```javascript
import { registry } from "@web/core/registry";
const widgetRegistry = registry.category("intn_portal_form_widgets");
widgetRegistry.add("portal_mi_widget", PortalMiWidget);
```

Props recibidas desde `PortalFormArchNode.getWidgetProps()`: `form`, `config`, `initialData`, `header`, `record`, `onFieldChange`, …

### Metrología / ONC (transición)

Usan `<widget name="portal_metrology_form"/>` u `portal_onc_form` que delegan temporalmente en `MetrologyServiceForm` / `OncCertificationForm`. El objetivo a medio plazo es migrar campos al arch nativo.

### Criterio de aceptación

Tras elegir producto, `PortalServiceFormView` renderiza campos visibles según config sin error en consola.

---

## Fase 6 — Shell de página

Template `portal_create_service_request` en `intn_portal_fleet_requests/portal/_shared/views/portal_templates.xml`:

- `owl-component` cabecera: `service_request_header`
- `owl-component` cuerpo: `service_request_form_shell`
- Form HTML `#fleet_service_request_form` (POST, CSRF)
- `#service_request_body_wrap` oculto hasta lock de cabecera

Inherits en otros módulos: solo layout (overflow, ancho). **No** añadir campos QWeb al cuerpo.

---

## Fase 7 — Assets

### Bundles

| Bundle | Contenido |
|--------|-----------|
| `intn_service_request.portal_form_engine` | Motor completo (parser, record, arch node, `PortalServiceFormView`) |
| `web.assets_frontend` | Cabecera (`service_request_header.js`) |
| `web.assets_frontend_lazy` | Include motor + widgets dominio + shell |

### Orden fleet (`intn_portal_fleet_requests`)

```python
"web.assets_frontend_lazy": [
    ("include", "intn_service_request.portal_form_engine"),
    # assets intn_fleet_cistern (modales vehículo)
    "intn_portal_fleet_requests/static/src/portal_form_engine/fleet_portal_widgets.js",
    "intn_portal_fleet_requests/static/src/portal_form_engine/fleet_portal_widgets.xml",
    "intn_portal_fleet_requests/static/src/portal/_shared/form/service_request_form_shell.js",
    "intn_portal_fleet_requests/static/src/portal/_shared/form/service_request_form_shell.xml",
],
```

### Reglas

1. Incluir `("include", "intn_service_request.portal_form_engine")` en cualquier módulo que use formularios portal.
2. Widgets de dominio **después** del include del motor, **antes** del shell.
3. El shell importa `PortalServiceFormView` directamente y registra widgets fleet por side-effect.
4. Modales camión/acoplado: montados desde `PortalVehicleSelectionWidget` (no desde el shell).
5. No usar `t-ref` en hijos OWL; usar `onFormReady` / `onFormUnready`.

---

## Fase 8 — Comportamiento frontend por familia

### Shell (`ServiceRequestFormShell`)

| Responsabilidad | Detalle |
|-----------------|---------|
| Escucha | `intn-portal-header-locked` / `intn-portal-header-unlocked` |
| Resolución form | `PortalServiceFormView` cuando `form.view` o `owl_component === "portal_form"` |
| Tabs | Datos básicos + adjuntos (fleet) |
| Estimate / slot | Debounce vía `portal_form_service.js`; lee `activeForm.record` con fallback DOM |
| Submit | `validate()` / `prepareSubmit()` del form activo; `form.requestSubmit()` |

### Fleet

| Necesidad | Dónde |
|-----------|-------|
| Campos declarativos | `portal_fleet_form_views.xml` |
| Visibilidad por trámite | `_portal_get_form_config()` |
| Vehículos / sucursal | `fleet_portal_widgets.js` |
| Adjuntos habilitación | Tab `PortalAttachmentsPanel` |

### Metrología / ONC

Widget delegado en arch + submit desde footer del shell. Validación en componente delegado hasta migración completa al arch.

---

## Fase 9 — Controller y POST

Mixins: `service_request_portal_payload.py` (`_portal_form_payload_for_catalog`), hooks en `service.request`.

Reglas POST:

1. `kw["service_type"]` = **catalog_id** (string).
2. Controller resuelve `service_type_key` desde catálogo.
3. Nombres HTML alineados con campos del arch / widgets.
4. Mixins HTTP: `request.env`, no `self.env`.

Hooks Python opcionales en catálogo/modelo:

- `_portal_validate_portal_values(values)` → mensaje de error o `""`
- `_portal_prepare_portal_create_vals(values)` → dict create

---

## Fase 10 — Tests

| Área | Tags | Qué validar |
|------|------|-------------|
| Motor descriptor | `intn_portal_form_engine` | `_portal_form_descriptor()` con `view` arch |
| Cabecera / payload | `intn_portal_header` | `form.owl_component == "portal_form"`, `form.view` presente |
| Página create | `intn_portal_pages` | 200, shell en HTML |
| POST create | `intn_portal_pages` | `service_type=str(catalog.id)`, redirect |

```python
payload = self._json(
    "/my/service_request/catalog/form_payload?catalog_id=%s" % catalog.id
)
self.assertTrue(payload.get("ok"))
self.assertEqual(payload["form"]["owl_component"], "portal_form")
self.assertTrue(payload["form"].get("view"))
self.assertIn("arch", payload["form"]["view"])
```

```bash
odx test intn_portal_form_engine intn_portal_fleet_requests
```

---

## Fase 11 — i18n

```bash
python scripts/i18n-sync.py sync -d <database> --modules <modulo>
python scripts/i18n-sync.py pending -d <database> --modules <modulo>
python scripts/i18n-sync.py apply-pending -d <database> --modules <modulo>
```

Ver `AGENTS.md` (sección *i18n*) y `docs/project/i18n/translation-es_PY.md`.

---

## Fase 12 — Verificación manual

| # | Paso | Resultado esperado |
|---|------|-------------------|
| 1 | `/my/service_request/new?service_category=fleet` | Cabecera OWL |
| 2 | Elegir organismo → departamento → producto | Formulario fleet visible (no alerta amarilla) |
| 3 | Habilitación | Camión, acoplado, fecha, botones nuevo vehículo |
| 4 | Enviar | Redirect a detalle |
| 5 | Consola | Sin OwlError en `PortalFormArchNode` / widgets |

Deep link: `/my/service_request/new?service_category=fleet&service_type=<catalog_id>`

Tras upgrade de módulos, hard refresh (Ctrl+Shift+R) para assets lazy.

---

## Anexo A — Metrología

| Paso | Detalle |
|------|---------|
| Vista | `views/portal_metrology_form_views.xml` → `portal_form_metrology_base` |
| Catálogo | `service_catalog_metrology_portal_views.xml` |
| Widget | `portal_metrology_form` en `metrology_portal_widget.js` |
| Create | `_portal_create_metrology_request` en `service_request.py` (fleet) |
| Migración BD | `migrations/18.0.1.6.0/post-migrate.py` |

---

## Anexo B — ONC

| Paso | Detalle |
|------|---------|
| Vista | `views/portal_onc_form_views.xml` → `portal_form_onc_base` |
| Catálogo | `service_catalog_onc_portal_views.xml` |
| Widget | `portal_onc_form` en `onc_portal_widget.js` |
| POST | Override en `onc_create.py` |
| Migración BD | `migrations/18.0.1.3.0/post-migrate.py` |

---

## Anexo C — Legacy (solo mantenimiento)

No usar en trámites nuevos:

- `FleetServiceForm` + `forms/registry.js` por trámite
- `portal_owl_component` como clave de registry (`enabling`, `emblem_change`, …)
- `service.request.portal.form.layout` + `portal_form_layout_id`
- `portal_service_request_bodies.xml`, `body_html` en payload
- `PortalServiceFormComponent` como base de formularios nuevos
- `invisible="not config.*"` en arch de vista portal

---

## Errores frecuentes

| Síntoma | Causa probable | Solución |
|---------|----------------|----------|
| "Formulario no disponible para este servicio" | `portal_form_view_id` vacío en BD | Upgrade módulo + migración; verificar `service_catalog_*_portal_views.xml` |
| `Cannot read properties of undefined (reading 'type')` en `PortalFormArchNode` | Props recursivas mal pasadas (`node="child"`) | Usar `t-props="{ archNode: child, formView: props.formView }"` |
| `Cannot read properties of null (reading 'values')` en widget vehículo | `formView` no propagada a nodos hijos | Pasar `formView` en todos los `PortalFormArchNode` recursivos |
| `KeyNotFoundError` en registry | Catálogo sin vista, clave legacy eliminada | Asignar `portal_form_view_id` |
| ParseError al guardar vista con `config` en invisible | Odoo valida arch contra campos del modelo | Visibilidad vía `_portal_get_form_config()` en JS |
| Formulario vacío tras upgrade | XML `noupdate="1"` no actualizó catálogo | `noupdate="0"` en portal_views + script migración |
| POST falla | `service_type` = form_key en vez de catalog_id | `str(catalog.id)` |
| Assets desactualizados | Bundle lazy cacheado | Hard refresh; `odx update-module intn_service_request,intn_portal_fleet_requests` |

---

## Checklist final pre-PR

### Backend

- [ ] `selection_add` + producto + org/dept
- [ ] `ir.ui.view` form portal + herencias xpath si aplica
- [ ] `portal_form_view_id` en `service_catalog_*_portal_views.xml` (`noupdate="0"`)
- [ ] Flags en `_portal_get_form_config()` documentados
- [ ] Migración post-migrate si el módulo ya está en producción

### Frontend

- [ ] Widgets nuevos en `intn_portal_form_widgets` (si aplica)
- [ ] `("include", "intn_service_request.portal_form_engine")` en manifest
- [ ] Sin `registry.js` por trámite
- [ ] Template OWL con `name=` alineado al POST
- [ ] `onFormReady` si el shell necesita la instancia activa

### Calidad

- [ ] Test `form_payload` con `portal_form` + `view`
- [ ] HttpCase POST exitoso
- [ ] i18n generado
- [ ] Verificación manual Fase 12

---

## Referencias rápidas

| Recurso | Ruta |
|---------|------|
| Estructura carpetas | [Estructura](portal-forms-estructura.md) |
| Motor OWL | `intn_service_request/static/src/portal_form_engine/` |
| Mixins Python | `service_request_portal_form_engine_mixin.py`, `service_request_portal_form_catalog_mixin.py` |
| Shell OWL | `intn_portal_fleet_requests/static/src/portal/_shared/form/service_request_form_shell.*` |
| Vistas fleet | `intn_portal_fleet_requests/views/portal_fleet_form_views.xml` |
| Widgets fleet | `intn_portal_fleet_requests/static/src/portal_form_engine/fleet_portal_widgets.*` |
| Tests motor | `intn_service_request/tests/test_portal_form_engine.py` |
| Tests payload | `intn_portal_fleet_requests/tests/test_portal_service_request_header.py` |
