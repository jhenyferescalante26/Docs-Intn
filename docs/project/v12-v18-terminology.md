# Homologación de términos v12 → v18 — Trazabilidad de Uso de Marca

Documento maestro de homologación para migración Odoo 12 → Odoo 18.

**Regla:** identificadores técnicos en inglés; textos de usuario en español vía `_()` / `es_PY.po`.

## Convención

| Capa | v12 | v18 |
|------|-----|-----|
| `_name` | español | `intn.brand.*` / `intn.metci.*` |
| Campos Python | español | inglés snake_case |
| `string=` UI | español | español traducible |
| Rutas portal | `/my/solicitud-impresion` | `/my/brand_print_requests` |

## Modelos — Datos principales

| Menú (UI es) | v12 `_name` | v18 `_name` |
|--------------|-------------|-------------|
| Marcas | `marca.producto` | `intn.brand.product.brand` |
| Fabricantes | `fabricante.producto` | `intn.brand.product.manufacturer` |
| Normas | `normas.licencia` | `intn.brand.license.norm` |
| Reglamentos | `reglamentos.licencia` | `intn.brand.license.regulation` |
| Determinaciones | `determinacion.ensayos` | `intn.brand.test.determination` |
| Color de Anillos | `intn_trazabilidad_uso_marca.color_anillos` | `intn.brand.ring.color` |
| Impresoras | `impresora.etiquetas` | `intn.brand.label.printer` |
| Imprentas | `imprenta` | `intn.brand.print.shop` |
| Métodos de pago | `metodos_pago` | `intn.brand.payment.method` |
| Etapas | `uso_marca_nombre_etapas` | `intn.brand.stage` |
| Sub etapas | `uso_marca_sub_etapas` | `intn.brand.substage` |

## Modelos — Licencias e impresión

| Menú (UI es) | v12 `_name` | v18 `_name` |
|--------------|-------------|-------------|
| Licencia INTN-Servicios | `licencia.servicios` | `certificate.management` (`BRAND_LICENSE_SERVICES`) |
| Certificado lote | `certificado.conformidad` | `intn.brand.batch.conformity.certificate` |
| Licencia conformidad | `licencia.conformidad` | `intn.brand.conformity.license` |
| Licencia conformidad tipo 2 | `licencia.conformidad.dos` | `intn.brand.conformity.license.type2` |
| Solicitudes de Impresión | `solicitud.impresiones` | `intn.brand.print.request` |
| Impresión de Etiquetas | `impresion.etiquetas` | `intn.brand.label.print.job` |
| Control de Etiquetas | `control.etiquetas` | `intn.brand.label.control` |
| Facturas/Comprobantes | `factura_comprobante` | `intn.brand.label.invoice.voucher` |
| Gestión de Comprobantes | `gestion.comprobantes` | `intn.brand.voucher.management` |

## Modelos — Muestreo

| Menú (UI es) | v12 `_name` | v18 `_name` |
|--------------|-------------|-------------|
| Acta de extracción | `acta.extraccion` | `intn.brand.sampling.extraction.minutes` |
| Informe de Muestreo | `informe.muestreo` | `intn.brand.sampling.report` |
| Solicitud de Ensayos | `solicitud.ensayos` | `intn.brand.sampling.test.request` |
| Nota de Rechazo | `intn_trazabilidad_uso_marca.nota_rechazo` | `intn.brand.rejection.note` |

## Modelos — METCI

| Menú (UI es) | v12 `_name` | v18 `_name` |
|--------------|-------------|-------------|
| Solicitud de Calibración | `calibration.request` | `intn.metci.calibration.request` |
| Control de Ingresos | `control.ingreso.instrumentos` | `intn.metci.instrument.intake` |
| Instrumentos | `instrument.inventory.metci` | `intn.metci.instrument` |
| Marcas instrumento | `instrument.brand` | `intn.metci.instrument.brand` |
| Modelos instrumento | `instrument.model` | `intn.metci.instrument.model` |

## Campos clave

| v12 | v18 | Modelo |
|-----|-----|--------|
| `es_etiqueta` | `is_label` | `product.template` |
| `es_anillo` | `is_ring` | `product.template` |
| `kg_polvo` | `powder_kg_per_unit` | `product.template` |
| `sgte_numero_control` | `next_control_number` | `product.template` |
| `state_uso_marca` | `brand_usage_state` | `res.partner` |
| `nombre_impresion` | `label_print_name` | `res.partner` |
| `cod_uso_marca` | `brand_usage_code` | `res.partner` |
| `nro_control` | `control_number` | print job line |
| `fecha_solicitud` | `request_datetime` | `intn.brand.print.request` |
| `primera_etiqueta` | `first_label_printed` | `intn.brand.label.print.job` |
| `reimpresion` | `reprint_status` | `intn.brand.label.print.job` |
| `des_servicio_1` | `service_description_html_1` | `certificate.management` |
| `agentes_1` | `agent_product_ids_1` | `certificate.management` |
| `reglamento_general_id` | `general_regulation_id` | `certificate.management` |
| `fabricante_id` (partner) | `manufacturer_partner_id` | `intn.brand.conformity.license` |
| `fecha_vencimiento` | `expiry_date` | `intn.brand.conformity.license` |
| `licencia_servicios_ids` | `brand_license_certificate_ids` | `res.partner` |
| `observaciones_certificado` | `certificate_notes` (Html) | `product.template` |
| `additional_cost` (bool) | `applies_additional_cost` | `product.template` |
| `rango` | `range_capacity` | `intn.metci.instrument` |
| `division` | `resolution` | `intn.metci.instrument` |
| `firma_recibi` | `signature_received` | `intn.metci.instrument.intake` |
| `cantidad_salida` | `quantity_delivered` | `intn.metci.instrument.intake.line` |

## Rutas portal

| v12 | v18 |
|-----|-----|
| `/my/solicitud-impresion` | `/my/brand_print_requests` |
| `/new/solicitud-impresion` | `/my/brand_print_request/new` |
| `/my/control-etiquetas` | `/my/brand_label_controls` |
| `/my/certificado-conformidad` | `/my/brand_batch_certificates` |
| `/usomarca/datamax/print` | `/brand/datamax/print` |

## Wizards

| v12 | v18 |
|-----|-----|
| `impresion.etiquetas.imprimir.wizard` | `intn.brand.label.print.wizard` |
| `verificar_impresion_wizard` | `intn.brand.label.print.verify.wizard` |
| `reimprimir.wizard` | `intn.brand.label.reprint.wizard` |
| `solicitud.impresiones.report.wizard` | `intn.brand.print.request.report.wizard` |
| `update.delivered.quantities` | `intn.brand.delivered.qty.update.wizard` |
| `rejection.reason.wizard` | `intn.brand.invoice.rejection.wizard` |

## Secuencias (`ir.sequence`)

Regla: catálogos y facturas manuales **no** usan secuencia. Número de control de etiqueta usa `product.template.next_control_number` (contador, no `ir.sequence`).

| v12 modelo | v12 `code` | v12 formato | Momento | v18 modelo | v18 `code` | v18 formato |
|------------|------------|-------------|---------|------------|------------|-------------|
| `solicitud.impresiones` | `seq_solicitud_impresiones` | `SI/` + `/año` | `create()` | `intn.brand.print.request` | `intn.brand.print.request` | `SI/` + `/año` |
| `impresion.etiquetas` | `seq_impresion_etiquetas` | `I/` + `/año` | `create()` | `intn.brand.label.print.job` | `intn.brand.label.print.job` | `I/` + `/año` |
| `control.etiquetas` | `seq_control_etiquetas` | `CE/` | `create()` | `intn.brand.label.control` | `intn.brand.label.control` | `CE/` |
| `gestion.comprobantes` | `seq_gestion_comprobantes` | `GC/` | `create()` | `intn.brand.voucher.management` | `intn.brand.voucher.management` | `GC/` |
| `certificado.conformidad` | `seq_certificado_conformidad` | `/año` suffix | confirm | `intn.brand.batch.conformity.certificate` | `intn.brand.batch.conformity.certificate` | `/año` suffix |
| `licencia.conformidad` | `seq_licencia_conformidad` | `/año` suffix | confirm | `intn.brand.conformity.license` | `intn.brand.conformity.license` | `/año` suffix |
| `licencia.conformidad.dos` | `seq_licencia_conformidad_dos` | `/año` suffix | confirm | `intn.brand.conformity.license.type2` | `intn.brand.conformity.license.type2` | `/año` suffix |
| `acta.extraccion` | `seq_acta_extraccion` | `/año` suffix | confirm | `intn.brand.sampling.extraction.minutes` | `intn.brand.sampling.extraction.minutes` | `/año` suffix |
| `informe.muestreo` | `seq_informe_muestreo` | `/año` suffix | confirm | `intn.brand.sampling.report` | `intn.brand.sampling.report` | `/año` suffix |
| `solicitud.ensayos` | `seq_solicitud_ensayos` | `/año` suffix | confirm | `intn.brand.sampling.test.request` | `intn.brand.sampling.test.request` | `/año` suffix |
| `nota.rechazo` | `seq_nota_rechazo` | `ONC N°` + `/año` | confirm | `intn.brand.rejection.note` | `intn.brand.rejection.note` | `ONC N°` + `/año` |
| `licencia.servicios` | `seq_licencia_servicios` | (no usada) | confirm | `certificate.management` | — | `400S - {brand_usage_code}` |
| `factura_comprobante` | — | manual 15 chars | — | `intn.brand.label.invoice.voucher` | — | manual |
| `calibration.request` | `calibration.request` | `CAL-` | `create()` | `intn.metci.calibration.request` | `intn.metci.calibration.request` | `CAL-` |
| `control.ingreso.instrumentos` | `control.ingreso.instrumentos` | `CI/` | `create()` | `intn.metci.instrument.intake` | `intn.metci.instrument.intake` | `CI/` |
| `instrument.inventory.metci` | `instrument.inventory` | `INST-` | `create()` | `intn.metci.instrument` | `intn.metci.instrument` | `INST-` |

Archivos v18: [`ir_sequence_data.xml`](../custom_addons/intn_brand/intn_brand_service_requests/data/ir_sequence_data.xml), [`brand_sequences_data.xml`](../custom_addons/intn_brand/intn_brand_service_requests/data/brand_sequences_data.xml), [`metci_v12_sequence_data.xml`](../custom_addons/intn_mrp/intn_mrp_metci/data/metci_v12_sequence_data.xml).
