# Manual de administración — Backoffice INTN

Manual funcional para el personal de INTN que usa Odoo desde el escritorio (no el portal de clientes). Describe qué hace cada proceso paso a paso, con capturas de pantalla, sin lenguaje técnico ni referencias a código.

Las capturas se generan **exclusivamente con Playwright** (ver `e2e/specs/`): cada guía se considera terminada cuando el test correspondiente corre de punta a punta navegando por menú y deja sus capturas en `_images/<dominio>/`.

## Cómo está organizado

Una carpeta por **dominio de negocio**; dentro, una página por proceso. Cada página indica para qué rol es, qué configuración previa requiere, los pasos por rol con capturas, y qué hacer ante casos especiales. El número `NN` del relevamiento histórico se conserva como campo `nn:` en el front-matter de cada página, solo para trazabilidad.

## Índice

### Cisternas (`cisternas/`)

| Página | Proceso |
|--------|---------|
| [Gestión de solicitudes ONM](cisternas/gestion-solicitudes-onm.md) | Revisión documental, confirmación y seguimiento de solicitudes de verificación |
| [Verificación técnica](cisternas/verificacion-tecnica.md) | Cadena visual → inspección tanque → hidrostática → medición |
| [Certificados de cisterna](cisternas/certificados-cisterna.md) | VCC / DINS / LIE: emisión, aprobación e impresión |
| [Carga de precintos en inventario](cisternas/carga-precintos-inventario.md) | Alta de series/códigos de precintos y carga de stock |
| [Precintos: remisión y devolución](cisternas/precintos-remision-devolucion.md) | Entrega y devolución de precintos |
| [Homologación y rangos de precintos](cisternas/homologacion-rangos-precintos.md) | Checklist por lote, rangos, emisiones y precintado |
| [Constancia de entrega](cisternas/constancia-entrega.md) | Constancia remisión + certificado |
| [Multas y bloqueos](cisternas/multas-bloqueos.md) | Multas, inasistencias y desbloqueo de vehículos |

### Metrología (`metrologia/`)

| Página | Proceso |
|--------|---------|
| [Gestión de solicitudes de picos](metrologia/gestion-solicitudes-picos.md) | Revisión y confirmación de solicitudes de surtidores |
| [Aprobación de modelo de picos](metrologia/aprobacion-modelo-picos.md) | Recepción, clasificación, verificación y devolución |
| [METCI — solicitud a laboratorio](metrologia/metci-solicitud-laboratorio.md) | Solicitudes internas de calibración |

### Marcas / ONC (`marcas-onc/`)

| Página | Proceso |
|--------|---------|
| [Gestión de certificación ONC](marcas-onc/gestion-certificacion-onc.md) | Revisión de FOR-001 / FPE-001 / FSG-001 |
| [Compra y reimpresión de normas ONN](marcas-onc/normas-onn.md) | Confirmación, facturación/cobro y descarga única del PDF |
| [Trazabilidad y etiquetas](marcas-onc/trazabilidad-etiquetas.md) | Licencias, saldos, impresión, muestreo y comprobantes |
| [Entrega de etiquetas y anillos](marcas-onc/entrega-etiquetas-anillos.md) | Registro ONC-FOR-078: rangos discontinuos, anillos y PDF firmable |

### Ventas y caja (`ventas-caja/`)

| Página | Proceso |
|--------|---------|
| [Expedientes, ventas y convenios](ventas-caja/expedientes-ventas-convenios.md) | Pedido de venta, convenios y crédito |
| [Contabilidad, caja y pagos](ventas-caja/contabilidad-caja-pagos.md) | SIFEN/SEGEL, sesiones de caja, recibos, transferencias |
| [Costos y presupuesto](ventas-caja/costos-presupuesto.md) | Convenios y costos adicionales |

### OIAT / ONI / MRP (`oiat-oni-mrp/`)

| Página | Proceso |
|--------|---------|
| [OIAT — informes y certificados](oiat-oni-mrp/oiat-informes-certificados.md) | Elaboración y aprobación escalonada |
| [ONI — informes](oiat-oni-mrp/oni-informes.md) | Informes, certificados y bitácora |
| [Acceso por organismos](oiat-oni-mrp/acceso-organismos.md) | Aislamiento por organismo y derivaciones |
| [DSE — inspecciones](oiat-oni-mrp/dse-inspecciones.md) | Equipos a presión (parcial) |
| [Integraciones transversales](oiat-oni-mrp/integraciones-transversales.md) | SIFEN, API facturas, PagoPar (guía TI) |

### Registro y documentos (`registro-documentos/`)

| Página | Proceso |
|--------|---------|
| [Aprobación de cuentas (ATC)](registro-documentos/aprobacion-cuentas-atc.md) | Habilitación de clientes registrados |
| [Solicitud de servicio unificada](registro-documentos/solicitud-servicio-unificada.md) | Ciclo backoffice de `service.request` |
| [Revisión documental](registro-documentos/revision-documental.md) | Aprobar / observar / rechazar (transversal) |
| [Documentos y DMS](registro-documentos/documentos-dms.md) | DMS interno, políticas de descarga, auditoría |

## Plantilla

Nuevas páginas: copiar `docs/admin/_templates/PROCESO-ADMIN.md`.

```{toctree}
:hidden:
:glob:

cisternas/*
metrologia/*
marcas-onc/*
ventas-caja/*
oiat-oni-mrp/*
registro-documentos/*
```
