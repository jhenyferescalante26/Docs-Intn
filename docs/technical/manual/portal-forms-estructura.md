# Estructura de carpetas — formularios portal unificados (OWL)

Cada módulo Odoo mantiene su `__manifest__.py`, modelos backend y data XML fuera de `portal/`. El código website se organiza bajo `portal/` (QWeb shell, controllers) y `static/src/` (OWL).

## Árbol de carpetas

```
intn_service_request/                          # Motor compartido
├── models/
│   ├── service_request_portal_form_engine_mixin.py
│   └── service_request_portal_form_catalog_mixin.py
├── views/
│   └── service_request_service_catalog_views.xml   # portal_form_view_id en catálogo
└── static/src/portal_form_engine/
    ├── portal_service_form_view.js               # Componente único portal_form
    ├── portal_form_arch_node.js                  # Render recursivo del arch
    ├── portal_form_record.js
    ├── portal_form_arch_parser.js
    ├── portal_form_field_registry.js
    ├── fields/portal_base_fields.js              # intn_portal_form_fields
    └── portal_form_engine_templates.xml

intn_portal_fleet_requests/
├── __manifest__.py
├── data/
│   ├── portal_header_organization_data.xml
│   ├── service_catalog_fleet_data.xml
│   └── service_catalog_fleet_portal_views.xml    # portal_form_view_id por trámite
├── views/
│   └── portal_fleet_form_views.xml               # ir.ui.view form + herencias xpath
├── models/
│   └── fleet_vehicle_service_request.py          # _portal_get_form_config()
├── portal/
│   ├── _shared/
│   │   ├── header/controllers/header_api.py
│   │   ├── controllers/service_request*.py
│   │   └── views/portal_templates.xml
│   └── forms/                                    # QWeb organización, tests
├── static/src/
│   ├── portal/_shared/
│   │   ├── header/js/service_request_header.js   # web.assets_frontend
│   │   └── form/
│   │       ├── service_request_form_shell.js     # web.assets_frontend_lazy
│   │       ├── portal_form_service.js
│   │       └── portal_attachments_panel.*
│   └── portal_form_engine/
│       ├── fleet_portal_widgets.js               # intn_portal_form_widgets (fleet)
│       └── fleet_portal_widgets.xml
├── migrations/
│   └── 18.0.1.8.0/post-migrate.py                # portal_form_view_id en bases existentes
└── tests/

intn_portal_metrology_dispenser_requests/
├── views/portal_metrology_form_views.xml
├── data/service_catalog_metrology_portal_views.xml
└── static/src/portal_form_engine/
    └── metrology_portal_widget.js                # widget portal_metrology_form

intn_onc_certification_requests/
├── views/portal_onc_form_views.xml
├── data/service_catalog_onc_portal_views.xml
└── static/src/portal_form_engine/
    └── onc_portal_widget.js                      # widget portal_onc_form
```

**Importante:** no crear `static/src/portal/forms/registry.js` ni un `Component` monolítico por trámite. El registry `intn_portal_service_forms` solo expone `portal_form` (`PortalServiceFormView`).

## Dependencias entre módulos

```{mermaid}
flowchart TB
    intn_service_request["intn_service_request\nmotor OWL + portal_form_view_id"]
    intn_product_org["intn_product_organization\nportal_header_ready"]
    intn_fleet["intn_portal_fleet_requests\nheader + shell + widgets fleet"]
    intn_metrology["intn_portal_metrology_dispenser_requests\nwidget metrología"]
    intn_onc["intn_onc_certification_requests\nwidget ONC"]
    intn_service_request --> intn_fleet
    intn_product_org --> intn_fleet
    intn_fleet --> intn_metrology
    intn_fleet --> intn_onc
```

| Módulo | `service_category` | Rol |
|--------|-------------------|-----|
| `intn_service_request` | — | Motor `PortalServiceFormView`, mixins Python, bundle `portal_form_engine` |
| `intn_portal_fleet_requests` | `fleet` | Shell, cabecera, vistas form fleet, widgets dominio, controller hub |
| `intn_portal_metrology_dispenser_requests` | `metrology` | Vista form + widget delegado; create en fleet |
| `intn_onc_certification_requests` | `brand` | Vista form + widget delegado; override POST |

## Registries JS

| Registry | Contenido | Dónde registrar |
|----------|-----------|-----------------|
| `intn_portal_service_forms` | `portal_form` → `PortalServiceFormView` | `intn_service_request/.../portal_form_registry.js` |
| `intn_portal_form_fields` | Tipos Odoo → inputs Bootstrap (`char`, `selection`, `many2one`, …) | `portal_base_fields.js` o módulo dominio |
| `intn_portal_form_widgets` | `<widget name="portal_*"/>` del arch | `fleet_portal_widgets.js`, `metrology_portal_widget.js`, … |

## Nomenclatura

| Concepto | Patrón | Ejemplo |
|----------|--------|---------|
| `form_key` / `service_type` | `snake_case` | `emblem_change` |
| Catálogo XML id | `service_catalog_{familia}_{form_key}` | `service_catalog_fleet_emblem_change` |
| Vista form XML id | `portal_form_{familia}_{variante}` | `portal_form_fleet_base`, `portal_form_fleet_emblem_change` |
| Widget arch | `portal_{dominio}_{nombre}` | `portal_vehicle_selection` |
| Shell OWL público | `intn_portal_fleet_requests.service_request_form_shell` | — |
| Cabecera OWL pública | `intn_portal_fleet_requests.service_request_header` | — |

## Reglas

- No renombrar xml ids al mover archivos; actualizar rutas en `__manifest__.py`.
- La cabecera vive en `intn_portal_fleet_requests/portal/_shared/header/`; el cuerpo **no** repite selects de organismo/categoría.
- En POST, `service_type` = **catalog_id** (`str(catalog.id)`). El `form_key` va en `data-service-type` y en `form.form_key` del payload.
- Orden data: org/dept en productos → catálogo base → **vistas portal** → **`service_catalog_*_portal_views.xml`** (`portal_form_view_id`) → shell QWeb.
- Orden assets lazy: `("include", "intn_service_request.portal_form_engine")` → widgets dominio → `service_request_form_shell`.
- **`portal_form_view_id` obligatorio** en trámites nuevos; `portal_owl_component` por trámite es legacy.
- Visibilidad condicional: flags en `_portal_get_form_config()` + `PortalFormRecord.fieldConfigVisibility()` — **no** usar `invisible="not config.*"` en XML (Odoo backend rechaza `config` como campo).
- Variantes de trámite: herencia `ir.ui.view` con xpath sobre vista base; asignar la vista concreta en catálogo.
- Nodos recursivos del arch: prop `archNode` + `formView` explícita en `PortalFormArchNode` (no depender solo del parent OWL).
- No usar `t-ref` en componentes OWL hijos; usar `onFormReady` / `onFormUnready`.
- Controladores portal: `request.env`, no `self.env`.
- **Submit unificado:** `PortalServiceFormView` implementa `validate()` y `prepareSubmit()`. Fleet envía desde tab adjuntos; metrología/ONC desde footer del shell.

## Rutas HTTP unificadas

| Ruta | Uso |
|------|-----|
| `GET /my/service_request/new` | Formulario de creación |
| `GET /my/service_request/catalog/form_payload?catalog_id=` | Descriptor OWL + `view` arch + `initial_data` |
| `GET /my/service_request/organizations` | JSON cabecera |
| `GET /my/service_request/products` | JSON productos |
| `POST /my/service_request/new` | Crear solicitud (`service_type` = catalog id) |
| `POST /my/service_request/estimate_total` | Estimate JSON (fleet / metrología) |

Metrología: redirects legacy en `portal/_shared/controllers/redirects.py`.
