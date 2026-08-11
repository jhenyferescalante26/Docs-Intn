# Widgets OWL reutilizables (`base_widgets`)

Cuatro field widgets de backend registrados en `registry.category("fields")` y cargados en `web.assets_backend`. Cada módulo tiene su propio README con el detalle de props.

## `catalog_product_picker` — Catálogo de productos

Selector de `product.template` que muestra reglas de variantes y contenido de combos al elegir un producto de catálogo. Incluye un segundo widget `pricing_rules_one2many` para listas de reglas de precio.

- JS: `web_catalog_product_picker/static/src/js/catalog_product_picker_field.js`
- Uso: `intn_base/intn_service_request/views/service_request_service_catalog_views.xml`

## `intn_seal_capture` — Captura de precintos

Widget one2many orientado a lector de código de barras: captura precintos por número de serie (tipeo, escaneo o rango) hacia compartimentos de cisterna o checklist de homologación.

- JS: `web_intn_seal_capture/static/src/js/seal_capture_field.js`
- Uso: `intn_fleet_cistern_seals/views/product_remission_views.xml`, `intn_fleet_seal_ranges/views/seal_homologation_views.xml`
- Capturas de referencia en `_static/widget-seal-capture/`

```{image} ../_static/widget-seal-capture/03-remision-captura-chips.png
:alt: Captura de precintos por chips en remisión
:width: 90%
```

## `partner_kanban_cards` — Tarjetas many2many

Muestra relaciones many2many como tarjetas estilo kanban.

- JS: `web_many2many_kanban_cards/static/src/js/partner_kanban_cards_field.js`
- Uso: `intn_portal_registration/views/res_partner_views.xml`

## `mutual_boolean_pair` — Cumple / No cumple

Par de checkboxes mutuamente excluyentes (Cumple / No cumple) para checklists de inspección.

- JS: `web_mutual_boolean_pair/static/src/js/mutual_boolean_pair_field.js`
- Uso: `intn_fleet_cistern_verification/views/cistern_tank_inspection_views.xml`

## Convención

Los widgets de `base_widgets` son **backend puro** y no dependen de módulos INTN. Los widgets de portal (frontend OWL) viven en `intn_portal_shared_widgets` y en el motor de formularios — ver [Formularios de portal](portal-forms.md).
