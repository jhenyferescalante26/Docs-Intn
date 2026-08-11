# Traducción español Paraguay (es_PY)

Este documento fija el alcance y la prioridad para completar `i18n/es_PY.po` en el proyecto INTN. El flujo técnico sigue [AGENTS.md](../AGENTS.md) (sección *i18n*) y `scripts/i18n-sync.py`.

## Alcance

| Fase | Ámbito | Cuándo |
|------|--------|--------|
| 1 | `custom_addons/` solo | Prioridad: código y negocio INTN; control de revisión. |
| 2 | `external_addons/` (OCA) | Opcional; conviene submódulos actualizados o traducir solo módulos instalados o pantallas usadas. |

No mezclar en un mismo PR fase 1 y 2 si el volumen dificulta la revisión.

## Orden sugerido de módulos (custom_addons)

Prioridad por impacto de usuario y volumen de cadenas pendientes:

1. Portal y registro: `intn_portal_registration`, `intn_portal_fleet_requests`, `intn_portal_helpdesk`, `intn_portal_metrology_dispenser_requests`, `intn_portal_service_products`, demás `intn_portal_*` con pendientes.
2. Flota / cisternas: `intn_fleet_cistern`, `intn_fleet_cistern_verification`, `intn_fleet_cistern_seals`, `intn_fleet_cistern_fines`, `intn_fleet_cistern_extensions`, `intn_fleet_cistern_certificates`, `intn_fleet_cisterns`, `intn_fleet_cistern_constancy`, `intn_fleet_cistern_scheduling`.
3. Base y certificados: `intn_service_request`, `intn_organization`, `intn_product_organization`, `intn_certificate_management`, `intn_delivery_certificate`, `intn_inspection_certificate`, `intn_product_remission`, `intn_partner_credit_limit`.
4. Integración y contabilidad local: `intn_api_invoices`, `l10n_py`, `l10n_py_edi_segel`.
5. Extensiones base: `partner_map_picker`, `l10n_py_ruc`, `partner_vat_unique`, `base_res_config_website_sale_stock`, `base_website_password`, `rf_customer_registration`, `web_many2many_kanban_cards`.
6. Otros: módulos `custom_addons/` con pendientes no listados arriba.

## Criterios de idioma (es_PY)

- Mantener coherencia en términos fiscales locales (RUC, factura electrónica, timbrado según contexto del módulo).
- UI Odoo: traducir cadenas visibles al usuario; no inventar variantes en cada pantalla para el mismo concepto.
- Revisar entradas `#, fuzzy` tras el merge desde `.pot` (pueden quedar desactualizadas).
- Acordar en el equipo formalidad (ustedes/tú) y registrar la decisión aquí si se fija un estilo único.

## Comandos

Exportar términos desde la BD y fusionar en `es_PY.po` sin sobrescribir
`msgstr` existentes (requiere BD con módulos actualizados):

```bash
python scripts/i18n-sync.py sync -d <base_de_datos> --installed
python scripts/i18n-sync.py sync -d <base_de_datos> --modules modulo1,modulo2
```

Generar borradores con entradas pendientes y aplicar traducciones revisadas:

```bash
python scripts/i18n-sync.py pending -d <base_de_datos> --installed
python scripts/i18n-sync.py apply-pending -d <base_de_datos> --installed
python scripts/i18n-sync.py stats --installed
```

Validar sintaxis de un `.po`:

```bash
msgfmt -c -v -o /dev/null <modulo>/i18n/es_PY.po
```

Validar todos los `es_PY.po` en `custom_addons`:

```bash
find custom_addons -path '*/i18n/es_PY.po' -print0 \
  | xargs -0 -I{} msgfmt -c -v -o /dev/null {}
```

## Prueba manual en Odoo

Cargar idioma **Spanish (PY) / es_PY** en la base, asignarlo al usuario y comprobar menús y formularios de los módulos tocados (portal, flota, etc.).
