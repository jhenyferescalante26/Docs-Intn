# v12 reference subset for demo data (curated)

Source database: `intn_v12` on `localhost:5557`. Records below are **reference IDs** from production v12; demo XML uses anonymized values inspired by this structure.

## Organization (master data)

| v12 `intn_organismos.id` | Name | v18 XML ID |
|--------------------------|------|------------|
| 30 | DSE | `intn_organization.intn_org_dse` |
| 31 | OIAT | `intn_organization.intn_org_oiat` |
| 32 | ONC | `intn_organization.intn_org_onc` |
| 33 | ONI | `intn_organization.intn_org_oni` |
| 34 | ONM | `intn_organization.intn_org_onm` |
| 35 | ONN | `intn_organization.intn_org_onn` |
| 36 | ATC | `intn_organization.intn_org_atc` |
| 37 | DAF | `intn_organization.intn_org_daf` |
| 38 | DG | `intn_organization.intn_org_dg` |

Key ONC departments (v12 id → v18): DCPE (86), DCPR (87), DCSI (88).

## UAT scenarios

### Brand (process 21)

| Scenario | v12 source | v18 models |
|----------|------------|------------|
| A. Enabled brand partner | `marca_producto` id 19 EXTINFUEGOS + partner `state_uso_marca=habilitado` | `intn.brand.product.brand`, `res.partner` |
| B. Batch certificate | `certificado_conformidad` id 485 | `intn.brand.batch.conformity.certificate` |
| C. Print request + job | `solicitud_impresiones` state `asignado` | `intn.brand.print.request`, `intn.brand.label.print.job` |
| D. Label control | derived from print job | `intn.brand.label.control` |
| E. Voucher management | `gestion_comprobantes` | `intn.brand.voucher.management` |
| F. Master catalogs | `normas_licencia`, `fabricante_producto`, ring colors | `intn.brand.*` master data |

### E2E seed (`e2e_intn`)

| Scenario | v18 seed key / helper | Spec |
|----------|----------------------|------|
| Metrology draft without sheets | `metrology_service_request_id` | `10-metrologia-picos-portal` UAT 4 |
| Unpaid portal certificate | `documents_e2e.unpaid_certificate_id` | `11-documentos-portal-dms` UAT 4 |
| Brand print portal | `brand_batch_certificate_e2e` + `brand_print_balance` | `21-onc-trazabilidad-etiquetas` UAT 5-6 |
| Brand SR link | `brand_service_request_e2e.id` | `21-onc-trazabilidad-etiquetas` UAT 8 |
| DSE MO | `dse_e2e.production_id` | `22-dse-inspecciones` |

## Fleet (process 08-10)

| Scenario | v12 `tipo_solicitud` | v18 `service.request` catalog |
|----------|----------------------|-------------------------------|
| Annual verification | `verificacion_anual` | `service_catalog_fleet_annual_verification` |
| Enabling | `habilitacion` | `service_catalog_fleet_enabling` |
| Emblem change | `cambio_emblema` | `service_catalog_fleet_emblem_change` |
| Seal replacement | `reposicion_precintos` | `service_catalog_fleet_seal_replacement` |
| Company change | `cambio_cliente` | `service_catalog_fleet_company_name_change` |
| Company + emblem | `cambio_cliente_emblema` | `service_catalog_fleet_company_emblem_change` |

Reference cistern (habilitado): v12 id 10656 — matricula `BFE426`, cisterna `AAEI335`, 7 compartments, 39000 L, emblem SHELL.

Reference emblems: SHELL, PARTICULAR, ECOP (v12 `emblemas`).

### Organization coordination and laboratories (TYPE A)

v12 CSV `intn_coordinaciones` / `intn_laboratorios` (74 / 117 prod). v18 subset in `intn_organization/data/organization_coordination_data.xml` and `organization_laboratory_data.xml` (ONC DCPE/DCPR/DCSI, OIAT DEIN/ENIN/Micro, ONI muestreo).

### Portal products (`aparece_solicitudes_servicio`)

31 products in v12; subset exported to `intn_product_organization` master data (ONN NP norms, ONC DCPE certifications, ONM metrology).

### Brand sampling and expediente (process 20-21)

| Scenario | v18 models / XML |
|----------|------------------|
| Sampling chain | `intn.brand.sampling.extraction.minutes`, `intn.brand.sampling.report`, `intn.brand.sampling.test.request` (`brand_sampling_demo.xml`) |
| Extended brand flow | Licencias conformidad, voucher, print job line, SR ONN (`brand_extended_demo.xml`) |
| Draft expediente | `sale.order` + line (`intn_sale_agreement.demo_expediente_sale_order`) |

### MRP laboratory flows (process 15-18)

| Organism | v18 demo module | Key models |
|----------|-----------------|------------|
| METCI | `intn_mrp_metci` | `intn.metci.service.request`, instrument intake, calibration request |
| OIAT | `intn_mrp_oiat`, `intn_mrp_oiat_fuel` | `intn.mrp.oiat.report`, certificate, fuel report |
| ONI | `intn_mrp_oni` | `intn.mrp.oni.inspection_report`, inspection certificate, assay report |
| All | `intn_mrp_organism_access` | `mrp.workorder` on demo MOs, `intn.mrp.workorder.lab_registry` |
| Forwarding | `intn_mrp_workorder_forwarding` | `intn.mrp.workorder.internal_request` |

### ONC certification (process 19)

| Type | v12 product example | v18 |
|------|---------------------|-----|
| Person | DCPE electricista B1 | `intn.onc.person.cert.request` |
| Product | DCPR product cert | `intn.onc.product.cert.request` |
| System | DCSI system cert | `intn.onc.system.cert.request` |

## Anonymization rules (demo XML)

| Field | Rule |
|-------|------|
| RUC | `80099xxx-x` |
| Email | `*@intn-demo.local` |
| Phone | `+595 21 500 XXXX` |
| Partner name | `Demo {type} S.A.` |
| Vehicle plates | `DEMO-xxx` |

## Excluded from demo

- `auditlog_*`, `account_move`, `mail_message`
- Materialized views `x_bi_sql_view_*`
- Full partner/product catalogs (1M+ / 6k+ records)
