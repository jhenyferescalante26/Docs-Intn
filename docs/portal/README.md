# Manual de usuario — Portal de clientes INTN

Manual funcional para clientes/empresas que usan el portal web de INTN (fuera del escritorio de Odoo). Describe qué hace cada trámite paso a paso, con capturas de pantalla, sin lenguaje técnico ni referencias a código.

Las capturas se generan **exclusivamente con Playwright** (ver `e2e/specs/`): cada guía se considera terminada cuando el test correspondiente corre de punta a punta navegando por el portal y deja sus capturas en `_images/<dominio>/`.

## Cómo está organizado

Una carpeta por **área de trámites**; dentro, una página por trámite. Cada página indica qué necesita el cliente antes de empezar, los pasos con capturas, qué esperar después de enviar, y qué hacer si algo no sale como se espera. El número `NN` del relevamiento histórico se conserva como campo `nn:` en el front-matter, solo para trazabilidad.

## Índice

### Mi cuenta (`cuenta/`)

| Página | Trámite |
|--------|---------|
| [Registro y aprobación](cuenta/registro-y-aprobacion.md) | Crear la cuenta, esperar habilitación, primer acceso |

### Cisternas (`cisternas/`)

| Página | Trámite |
|--------|---------|
| [Solicitud de verificación ONM](cisternas/solicitud-verificacion-onm.md) | Inicial, periódica, eventual, complementaria; citas y vehículos |
| [Certificados](cisternas/certificados.md) | Descarga de certificados emitidos |
| [Multas y bloqueos](cisternas/multas-y-bloqueos.md) | Qué hacer si el sistema bloquea una nueva solicitud |

### Metrología (`metrologia/`)

| Página | Trámite |
|--------|---------|
| [Solicitud de picos/surtidores](metrologia/solicitud-picos-surtidores.md) | Verificación de surtidores con fichas por instrumento |
| [Aprobación de modelo de picos](metrologia/aprobacion-modelo-picos.md) | Envío, correcciones y descarga de habilitación |

### Laboratorios (`laboratorios/`)

| Página | Trámite |
|--------|---------|
| [Solicitud de muestra de alimentos (OIAT)](laboratorios/solicitud-muestra-alimentos.md) | Análisis de muestras de alimentos en el laboratorio OIAT |
| [Combustibles y Lubricantes (OIAT)](laboratorios/solicitud-combustibles-lubricantes.md) | Servicio Normal, MIC y Barcazas |
| [Seguridad Industrial, Textil y Muestreo (ONI)](laboratorios/solicitud-oni-seguridad-textil-muestreo.md) | Los tres servicios comparten el mismo formulario base |
| [Inspección de Garrafas (ONI)](laboratorios/solicitud-oni-inspeccion-garrafas.md) | Programa de Inspección de garrafas de gas |
| [Maquila y Manufactura (ONI)](laboratorios/solicitud-oni-maquila.md) | Servicio de maquila y manufactura |

### Marcas / ONC (`marcas-onc/`)

| Página | Trámite |
|--------|---------|
| [Certificación ONC](marcas-onc/certificacion-onc.md) | FOR-001 (productos), FPE-001 (personas), FSG-001 (sistemas) |
| [Normas ONN](marcas-onc/normas-onn.md) | Compra y descarga de normas |
| [Etiquetas y trazabilidad](marcas-onc/etiquetas-trazabilidad.md) | Solicitud de impresión y saldo de etiquetas |

### Documentos y pagos (`documentos-pagos/`)

| Página | Trámite |
|--------|---------|
| [Mis documentos](documentos-pagos/mis-documentos.md) | Consultar y descargar certificados y adjuntos |
| [Corrección de documentos](documentos-pagos/correccion-documentos.md) | Resubir archivos observados o rechazados |
| [Facturas y pagos](documentos-pagos/facturas-y-pagos.md) | Consultar pedidos, pagar con PagoPar o transferencia |

## Plantilla

Nuevas páginas: copiar `docs/portal/_templates/TRAMITE-PORTAL.md`.

```{toctree}
:hidden:
:glob:

cuenta/*
cisternas/*
metrologia/*
laboratorios/*
marcas-onc/*
documentos-pagos/*
```
