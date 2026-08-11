# Arquitectura de módulos

Los 71 módulos custom viven en `custom_addons/` agrupados en 11 dominios. El apilado general es:

```{mermaid}
flowchart TB
    subgraph framework [Capa framework]
        BE[base_extensions]
        BW[base_widgets]
    end
    subgraph core [Núcleo de dominio]
        IB[intn_base]
    end
    subgraph verticals [Verticales de negocio]
        FL[intn_fleet]
        MR[intn_mrp]
        BR[intn_brand]
        SA[intn_sales]
        AC[intn_accounting]
    end
    subgraph facing [Capa expuesta]
        PO[intn_portal]
        IN[intn_integration]
        HR[intn_hr]
    end
    framework --> core --> verticals --> facing
```

## Capas

**Framework (`base_extensions`, `base_widgets`)** — extensiones genéricas sin dependencia INTN: localización paraguaya (`l10n_py_ruc`, `partner_vat_unique`), registro de clientes con aprobación ATC (`rf_customer_registration`), selector de mapa (`partner_map_picker`) y los cuatro widgets OWL reutilizables (ver [Widgets](widgets.md)).

**Núcleo (`intn_base`)** — los módulos de los que depende casi todo:

| Módulo | Rol |
|--------|-----|
| `intn_organization` | Jerarquía interna de 5 niveles: organización → unidad → departamento → coordinación → laboratorio |
| `intn_service_request` | Modelo unificado `service.request`, columna vertebral de todos los formularios de portal y solicitudes de dominio; incluye el motor de formularios OWL (ver [Formularios de portal](portal-forms.md)) |
| `intn_certificate_management` | Creación, numeración y vencimiento genérico de certificados |
| `intn_documents` | Trazabilidad documental: persistencia de PDF emitidos, auditoría de impresión, acceso unificado en portal |
| `intn_product_organization` | Vincula productos a la jerarquía organizacional; flag `portal_header_ready` que habilita productos en el portal |

**Verticales** — cada dominio de negocio implementa sus flujos sobre el núcleo:

- `intn_fleet` — verificación de camiones cisterna: solicitudes, verificación técnica, certificados (VCC/DINS/LIE), precintos y rangos, multas, agendamiento.
- `intn_mrp` — laboratorios y organismos sobre órdenes de producción; `intn_mrp_organism_access` segmenta por organismo con reglas de registro estrictas; un módulo instalable por organismo (`intn_mrp_oiat`, `intn_mrp_oni`, `intn_mrp_metci`, …).
- `intn_brand` — uso de marca (ONN) y certificación ONC sobre `service.request`.
- `intn_sales` — convenios de precios (`intn_sale_agreement`), costos adicionales, estado de pago de pedidos.
- `intn_accounting` — contabilidad paraguaya (`l10n_py`), facturación electrónica SET (`l10n_py_edi_segel`), caja (`intn_account_cashier`), grupos de pago y transferencias.

**Capa expuesta** — `intn_portal` (formularios de trámites del portal, registro, autenticación híbrida MITIC), `intn_integration/intn_api_invoices` (API REST de facturas) e `intn_hr_organization_bridge` (puente opcional RRHH ↔ organismos).

## Dónde mirar primero

- Un trámite de portal nuevo → [Formularios de portal](portal-forms.md) y `intn_portal_fleet_requests` (hub del motor).
- Permisos y visibilidad → [Modelo de seguridad](security-model.md).
- Detalle de cualquier módulo (modelos, campos, vistas, ACL, rutas) → páginas generadas en [Módulos](../generated/index.md).
