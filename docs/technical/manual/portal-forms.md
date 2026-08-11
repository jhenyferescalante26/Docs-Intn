# Motor de formularios de portal

Los trámites del portal comparten un único formulario en `/my/service_request/new`: un shell QWeb mínimo (POST + CSRF + dos montajes `owl-component`) cuyo **cuerpo se renderiza por completo en OWL** desde una vista `ir.ui.view` referenciada en el catálogo (`portal_form_view_id`).

## Flujo

```{mermaid}
sequenceDiagram
    participant C as Cliente (browser)
    participant H as Header OWL
    participant S as ServiceRequestFormShell
    participant V as PortalServiceFormView
    participant B as Backend
    C->>H: elige Organismo → Departamento → Categoría → Producto
    H->>B: GET /my/service_request/catalog/form_payload?catalog_id=
    B-->>H: {header, form.view (arch+fields), initial_data}
    H->>S: evento intn-portal-header-locked
    S->>V: monta PortalServiceFormView
    V->>V: PortalFormArchNode renderiza el arch recursivamente
    S->>B: POST (service_type = str(catalog.id))
```

## Capas

| Objeto | Rol | Dónde |
|--------|-----|-------|
| `ServiceRequestFormShell` | Tabs, estimación, submit, panel de adjuntos | `intn_portal_fleet_requests/static/src/portal/_shared/form/` |
| `PortalServiceFormView` | Motor: parser de arch, `PortalFormRecord`, validate/prepareSubmit | `intn_service_request/static/src/portal_form_engine/` |
| `PortalFormArchNode` | Render recursivo de `<field>` / `<widget>` del arch | ídem |
| `ir.ui.view` (form) | Define el formulario en DB, `js_class="intn_portal_form"` | `views/portal_*_form_views.xml` de cada módulo |

Tres registries JS: `intn_portal_service_forms` (solo `portal_form`), `intn_portal_form_fields` (inputs Bootstrap por tipo Odoo) e `intn_portal_form_widgets` (bloques de dominio, ej. `portal_vehicle_selection`, `portal_branch_partner`, `portal_service_location` en `fleet_portal_widgets.js`).

La visibilidad condicional NO usa `invisible="not config.*"` en XML: viene de `_portal_get_form_config()` (Python) + `PortalFormRecord.fieldConfigVisibility()` (JS).

## Agregar un formulario nuevo (patrón recomendado)

1. `_inherit = "service.request"`: agregar el `service_type` vía `selection_add`; sobreescribir `_portal_get_form_config()` y, si aplica, `_portal_validate_portal_values` / `_portal_prepare_portal_create_vals`.
2. Crear el `product.template` comercial con organización/departamento e `intn_show_in_service_list=True`.
3. `views/portal_*_form_views.xml`: vista form base + variantes por xpath.
4. `data/service_catalog_*_portal_views.xml` (`noupdate="0"`) asignando `portal_form_view_id`.
5. Si hacen falta widgets de dominio, registrarlos en `intn_portal_form_widgets`.
6. Assets: incluir `("include", "intn_service_request.portal_form_engine")` en `web.assets_frontend_lazy`, luego los widgets de dominio, luego el shell.

Guía paso a paso completa: [Guía — nuevo formulario](portal-forms-guia.md); convenciones de carpetas y assets: [Estructura](portal-forms-estructura.md).

## Estado de migración

`intn_portal_metrology_dispenser_requests` (`portal_metrology_form`) e `intn_onc_certification_requests` (`portal_onc_form`) todavía delegan en componentes legacy (`portal_owl_component` + registry por formulario, **deprecado**) y envían desde el footer del shell; los formularios fleet envían desde la pestaña de adjuntos.
