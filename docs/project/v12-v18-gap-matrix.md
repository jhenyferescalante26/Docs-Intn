# Matriz de brechas v12 vs v18 — Trazabilidad de Uso de Marca

Documento de validación para stakeholders ONC. Cruza el monolito v12
(`intn_trazabilidad_uso_marca`) con la implementación Odoo 18 en
`custom_addons/intn_brand/`.

**Referencia v12:** `/home/daniel/Projects/Appex/intn_repo_viejo/extra-addons/intn_addons/intn_trazabilidad_uso_marca/`

**Procesos Odoo 18 relacionados:** 19 (certificación ONC), 20 (ONN normas), 21 (etiquetas), 15 (METCI moderno).

**Homologación v18:** ver [`v12-v18-terminology.md`](v12-v18-terminology.md).

> **Revalidado el 28/07/2026** contra el código commiteado en `a43632c8`,
> más el RF 6.2 (entrega de etiquetas y anillos, ONC-FOR-078) implementado
> sobre `intn_brand_service_requests` — ver
> [spec RF 6.2](specs/rf-6.2-entrega-etiquetas-anillos.md). El RF 6.2 **no es
> una migración**: v12 nunca tuvo este registro (sin serie, sin cantidad
> declarada por color, sin anillos chicos/grandes, sin PDF ONC-FOR-078).

## Resumen ejecutivo (actualizado)

| Pregunta | Respuesta |
|----------|-----------|
| ¿Modelos v12 portados? | Sí — equivalentes en inglés en `intn_brand_service_requests` + METCI v12 |
| ¿Forms backend? | Sí — paridad ~65–70% con tabs, chatter, readonly por estado |
| ¿Portal impresión? | Parcial — rutas `/my/brand_print_*` con cert/factura, PDF, control Excel |
| ¿Stock / Datamax? | Parcial — movimientos internos al verificar job; API Datamax poll/hecho |
| ¿Gestión comprobantes? | Parcial — expediente, transferencias, validación anillos |
| ¿Entrega ONC-FOR-078? | Sí — rangos discontinuos con serie, contador de pendientes, congelado al confirmar y PDF firmable |
| ¿Verificación pública QR? | Parcial — rutas `/brand/verify/*` |
| ¿METCI legacy? | Parcial — approve SO, intake pickup, MRP production |
| ¿Certificación ONC en portal? | Sí — `intn_onc_certification_requests` con FOR-001, FPE-001 y FSG-001 |

## Matriz por dominio

| Dominio v12 | v18 | Estado |
|-------------|-----|--------|
| Catálogos brand | `intn.brand.*` master data | Implementado |
| Licencia servicios | `certificate.management` BRAND_LICENSE | Parcial (reporte legal migrado; portal licencias pendiente) |
| Certificado lote | `intn.brand.batch.conformity.certificate` | Parcial (backend + portal + reporte legal) |
| Licencias conformidad 1/2 | `intn.brand.conformity.license` / `.type2` | Parcial (reportes legales migrados) |
| Muestreo | `intn.brand.sampling.*` | Parcial (reportes legales migrados) |
| Solicitud impresión | `intn.brand.print.request` | Parcial (assign/verify/voucher OK; portal OK) |
| Impresión etiquetas | `intn.brand.label.print.job` | Parcial (reprint auth, scrap, stock move) |
| Factura comprobante | `intn.brand.label.invoice.voucher` | Parcial |
| Gestión comprobantes | `intn.brand.voucher.management` | Parcial (expediente + picking + anillos) |
| Entrega etiquetas/anillos | `intn.brand.label.delivery` | Implementado — funcionalidad nueva (RF 6.2 / ONC-FOR-078), sin equivalente v12 |
| Control etiquetas | `intn.brand.label.control` | Parcial (upload + conteo filas Excel) |
| Portal impresión | `/my/brand_print_request/*` | Parcial |
| Datamax | `/brand/datamax/print` | Parcial |
| Verificación pública | `/brand/verify/*` | Parcial |
| ONN normas | Proceso 20 | Parcial (sin catálogo migrado; ver [spec RF 2.9](specs/rf-2.9-ecommerce-normas.md)) |
| Certificación ONC | `intn.onc.*` cert requests | Implementado (productos, personas y sistemas) |
| METCI moderno | Proceso 15 | Implementado |
| METCI v12 calibración/intake | `intn.metci.calibration.request` / `.intake` | Parcial (reportes control ingreso + etiqueta migrados) |

## Pendiente para paridad total

1. Portal licencia servicios list/detail
2. ONN e-commerce: migrar los 887 productos de norma con su PDF y despublicar la
   demo de Odoo — es la Fase N1 de [`venta_de_normas.md`](../design/venta_de_normas.md)
   y lo que bloquea RF 2.9
3. Etapas brand en expediente (`service.request.brand_stage_line_ids`)
4. Técnico metrología v12
5. Portal METCI presupuesto (alternativa: proceso 15)
6. Presupuestos brand (#13–15): layout legal específico pendiente de validación negocio

## Referencias

- Manual admin: [trazabilidad-etiquetas.md](../admin/marcas-onc/trazabilidad-etiquetas.md) ·
  [gestion-certificacion-onc.md](../admin/marcas-onc/gestion-certificacion-onc.md)
- Manual portal: [etiquetas-trazabilidad.md](../portal/marcas-onc/etiquetas-trazabilidad.md) ·
  [certificacion-onc.md](../portal/marcas-onc/certificacion-onc.md)
- Venta de normas: [venta_de_normas.md](../design/venta_de_normas.md)
- Plan implementación: `.cursor/plans/paridad_procesos_v12_v18_*.plan.md`
- Terminología: [v12-v18-terminology.md](v12-v18-terminology.md)
