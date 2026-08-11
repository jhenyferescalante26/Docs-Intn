# Backlog relevamiento (no cubierto o parcial en Odoo 18)

Ítems derivados de [matriz pliego](../project/relevamiento/matriz-pliego-relevamiento.md) y minutas. No sustituyen historias de usuario; priorizan trabajo futuro.

## Won't Have / fase posterior (contractual)

| Tema | Fuente | Notas |
|------|--------|-------|
| Sitio web institucional completo en Odoo | Matriz fila Generales | Fuera de alcance portal ERP |
| App Android genérica nuevos departamentos | Matriz fila Generales | App básculas otro proveedor |
| Inventario stock fase 2 ventas | Matriz fila Ventas | |
| Precintado offline VPN (app SEGEL) | Matriz / minuta 16-01 | Fuera de alcance Odoo; app de campo externa. Proceso **06** cubre remisión/devolución en línea. |

## Could Have / deseable

| Tema | Proceso doc | Estado código |
|------|-------------|---------------|
| Pasarela Aqui Pago / Ueno | 24, 14 | Parcial |
| Geolocalización contactos | 01 | No |
| Proveedores plantilla stock ONC | 21 | Parcial |
| Módulo eventos lanzamiento normas ONN | 20 | No |
| Listas de precio con fórmulas anuales | 23, 13 | Parcial |

## Must Have con brecha activa

| Tema | Proceso | Brecha |
|------|---------|--------|
| Portal ONC etiquetas sin correo manual | 21 | Portal `/my/brand_print_request/*` implementado; notificaciones mail al crear desde portal |
| Informe ONI visible solo si pagado | 17, 14 | Validar reglas en reportes portal |
| DSE inspección inicial/intermedia | 22 | Solo acceso MRP demo |
| Estructura costos Excel 2026 | 23 | Planillas fuera de Odoo |
| Facturación electrónica SIFEN en línea | 24, 14 | Integración externa |

## Decisiones de minuta (referencia)

- **2026-01-27 ONC:** portal autogestión etiquetas → [21](../processes/21-onc-trazabilidad-etiquetas.md); transición correo paralela.
- **2026-01-27 ONN:** descarga única normas, sin MRP CITN → [20](../processes/20-onn-normas-portal.md).
- **2026-01-27 Costos:** flujo presupuesto → [23](../processes/23-costos-presupuesto.md), [13](../processes/13-expedientes-ventas-convenios.md).
