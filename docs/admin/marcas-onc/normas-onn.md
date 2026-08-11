---
nn: "20"
dominio: marcas-onc
roles: [onn, revisor, ventas]
estado: parcial
---

# Compra y reimpresión de normas ONN en backoffice

## Para quién es esta guía

- **Personal ONN/CITN** (grupo **Brand ONN Norms**, o **Brand Service Requests Manager** con acceso a todo) — da seguimiento a la solicitud en **Solicitud de Normas** y la confirma.
- **Revisor de documentos INTN** (grupo **Revisor de documentos INTN**) — aprueba, observa o rechaza la revisión documental transversal antes de que la solicitud pueda confirmarse (si el bloqueo está activo).
- **Ventas / Caja** — factura el expediente (pedido de venta) y registra el cobro; ese pago es lo que habilita la descarga del PDF en el portal.

## Qué resuelve este proceso

Da seguimiento en Odoo a la compra de una norma técnica (**ONN Norms**) o a su reimpresión (**ONN Norms Reprint**) que el cliente solicitó desde el portal ([guía de portal](../../portal/marcas-onc/normas-onn.md)), hasta que el expediente queda facturado y pagado y el cliente puede descargar su PDF una sola vez.

> **Verificado el 28/07/2026** contra el código commiteado en `a43632c8`.
>
> Este es hoy el **único** circuito de venta de normas. La tienda en línea
> (`/my/ecommerce`) tiene el tile publicado pero sin catálogo: las 887 normas de
> `intn_v12` siguen sin migrar y la tienda muestra los productos de la demo de
> Odoo. Ese circuito es RF 2.9 — ver
> [spec RF 2.9](../../project/specs/rf-2.9-ecommerce-normas.md) y el plan en
> [`venta_de_normas.md`](../../design/venta_de_normas.md).

## Configuración previa

- Usuario interno con acceso a la aplicación **Trazabilidad de Uso de Marca**.
- Para ver el menú **Operaciones → Solicitud de Normas**: pertenecer al grupo **Brand ONN Norms** o **Brand Service Requests Manager** (Ajustes → Usuarios → pestaña Derechos de acceso).
- Para aprobar/observar/rechazar documentación: grupo **Revisor de documentos INTN** (transversal a todos los trámites, ver [revisión documental](../registro-documentos/revision-documental.md)).
- En **Ajustes → Ventas**, bloque **Solicitudes de servicio**, la opción **Exigir documentación aprobada antes de confirmar** está **activada por defecto**; bloquea el botón **Confirmar** de la solicitud hasta que la revisión documental esté en **Aprobado**, aunque este trámite no le exige al cliente subir ningún archivo (ver más abajo).
- Catálogo de productos usado por este trámite: **NP 118** (producto de la compra, referencia interna `product_template_brand_onn_normas`) y **ONN Norms Reprint** (código `REPRINT01`, referencia interna `product_template_brand_reprint_onn_normas`). Ambos son productos de tipo servicio con **precio de venta 0.00 por defecto**: si el trámite debe cobrarse, Ventas debe cargar el precio (en el producto o mediante una lista de precios) antes de facturar el expediente; de lo contrario la factura queda en 0 y Odoo la marca como pagada automáticamente al validarla.
- Los productos "NP 118", "NP 322", "PNA 20 032 21", etc. que aparecen en **Datos principales → Normas** (organización ONN/CITN) son un catálogo aparte, usado por otros flujos de organización de productos; **no** son el producto que se vende en este trámite ni seleccionan una norma específica dentro de la solicitud.

## Antes de empezar

- El cliente ya envió la solicitud desde el portal (`/my/brand_request/new`), eligiendo **ONN Norms** o **ONN Norms Reprint**. Al crearla, el sistema generó automáticamente:
  - la **solicitud de servicio** (`SR…`), categoría **Brand**, en estado **Borrador**;
  - un **ticket** en el equipo **Brand Service Requests**;
  - el **pedido de venta** (expediente), con la línea del producto correspondiente al tipo de servicio.
- La solicitud no exige adjuntos del cliente (el formulario de portal para normas no pide archivos), y no usa la pestaña **Líneas** de equipos (queda vacía; esa pestaña es para trámites de flota).

## Pasos por rol

### Personal ONN/CITN

1. Abrir **Trazabilidad de Uso de Marca → Operaciones → Solicitud de Normas**, donde llegan las solicitudes que el cliente envió desde el portal. La lista muestra solo solicitudes con tipo de servicio **ONN Norms** o **ONN Norms Reprint**, con las columnas genéricas de solicitud de servicio: **Referencia**, **Categoría**, **Tipo de servicio**, **Ticket**, **Cliente**, **Manager**, **Beneficiary** y **Estado** (etiqueta amarilla para **Borrador**/**Reprogramado**, verde para **Confirmado**/**Finalizado**, roja para **Cancelado**/**Sin Asistencia**).

2. Abrir la solicitud. En la cabecera están los botones **Confirmar**, **Finalizar** y **Cancelar**, y los accesos directos **Ticket** y **Pedido de Venta** (expediente). Los datos: **Categoría**, **Tipo de servicio** (de solo lectura), **Ticket**, **Cliente**, **Manager**, **Beneficiary** y el propio **Pedido de Venta**.

3. Antes de confirmar, revisar el estado de **Document review** (campo agregado por la revisión documental transversal): si está en **Pendiente de revisión** y la opción de Ajustes sigue activa, alguien con el grupo **Revisor de documentos INTN** debe pulsar **Aprobar documentación** (ver paso siguiente), aun cuando no haya ningún archivo específico que revisar en este trámite — es el mismo candado que usan el resto de los procesos.

4. Pulsar **Confirmar**. La acción confirma también el **pedido de venta** vinculado (si estaba en borrador) y deja la solicitud en **Confirmado**. Si la revisión documental no está aprobada, aparece el mensaje "Document review must be approved before confirming (current state: Pendiente de revisión)." y la solicitud no cambia de estado.

5. Coordinar con **Ventas/Caja** la facturación y el cobro del expediente (ver [expedientes, ventas y convenios](../ventas-caja/expedientes-ventas-convenios.md) y [contabilidad, caja y pagos](../ventas-caja/contabilidad-caja-pagos.md)). El cliente solo puede descargar el PDF de la norma desde el portal cuando la factura del pedido está **Publicada** y **Pagada** (o **En proceso de pago**); mientras tanto, si intenta descargar, ve "Report not available until the related service is invoiced." o "Report not available until the related service is paid.".

6. La descarga en sí la hace el cliente desde el portal, y solo se permite **una vez**: el sistema lleva un contador interno (no editable desde ninguna vista) que bloquea intentos posteriores con "This document can only be downloaded once.". Si el cliente necesita otra copia, debe crear una **nueva solicitud ONN Norms Reprint**; no hay ninguna acción de backoffice para "reiniciar" la descarga de una solicitud ya usada.

7. Cuando el expediente esté pagado (y la revisión documental aprobada), pulsar **Finalizar** para cerrar el trámite. Si la opción **Correo cuando se finaliza el servicio** está activa (Ajustes → Ventas, por defecto activada), el cliente recibe un correo avisando que su trámite fue finalizado.

### Revisor de documentos INTN

- Sigue el circuito transversal descrito en [revisión documental](../registro-documentos/revision-documental.md): botones **Observar**, **Aprobar documentación**, **Rechazar documentación** y **Restablecer revisión** en la cabecera de la solicitud. Para este trámite en particular no hay una pestaña de adjuntos del cliente que revisar; el paso existe solo porque el bloqueo de confirmación es transversal a todas las solicitudes de servicio.

### Ventas / Caja

- Facturan y cobran el pedido de venta vinculado a la solicitud, igual que cualquier otro expediente ([expedientes, ventas y convenios](../ventas-caja/expedientes-ventas-convenios.md), [contabilidad, caja y pagos](../ventas-caja/contabilidad-caja-pagos.md)).
- Si el producto no tiene precio cargado, corresponde fijarlo antes de facturar (ver "Configuración previa"); de lo contrario la factura sale en 0 y queda pagada automáticamente sin que exista un cobro real.
- Si el cliente tiene demasiadas facturas vencidas, el portal puede bloquear la creación de **nuevas** solicitudes (parámetro **Máximo de facturas vencidas para nuevas solicitudes**, Ajustes → Ventas); esto no afecta a una solicitud ya creada.

## Estados que verá en pantalla

| Estado | Significado | Qué hacer |
|--------|-------------|-----------|
| Borrador | Solicitud creada desde el portal, con expediente ya generado | Revisar documentación (si aplica) y confirmar |
| Confirmado | Solicitud y pedido de venta confirmados | Coordinar con Ventas/Caja la facturación y el cobro |
| Finalizado | Trámite cerrado tras el pago | Nada más; si el cliente pide otra copia, es una solicitud nueva de reimpresión |
| Cancelado | Solicitud cancelada | No requiere acción |

## Casos especiales

- **Precio en 0 por defecto:** los productos **NP 118** y **ONN Norms Reprint** no traen precio cargado en los datos de fábrica; si el trámite debe cobrarse, alguien de Ventas debe fijar el precio del producto o crear una regla de lista de precios antes de facturar.
- **El PDF descargable es un documento genérico:** el reporte que el cliente descarga ("ONN Norms") solo muestra el nombre de la solicitud, la categoría, el tipo de servicio y el número de pedido de venta; no incorpora el archivo real de la norma técnica. Existe un campo **Norm Document** adjuntable en la ficha del producto (pestaña **Brand Usage**), pero el reporte actual no lo utiliza — verificar con el equipo de desarrollo si esto es intencional antes de asumir que la descarga entrega la norma en sí.
- **Sin expediente vinculado:** si la solicitud quedó sin pedido de venta (por ejemplo, se borró a mano), el cliente ve "Missing sale order for this request." al intentar descargar. Si la solicitud sigue en **Borrador**, alguien de ONN puede volver a pulsar **Confirmar** para que el sistema regenere el expediente; si ya estaba **Confirmado** o **Finalizado**, contactar a soporte técnico.
- **Reimpresión:** siempre se gestiona como una solicitud nueva de tipo **ONN Norms Reprint**, con su propio expediente y su propio ciclo de pago y descarga única.

## Si algo no funciona

| Problema | Causa habitual | Qué hacer |
|----------|----------------|-----------|
| No se puede pulsar **Confirmar** — "Document review must be approved before confirming (current state: …)." | Revisión documental no aprobada y el bloqueo está activo en Ajustes | Un **Revisor de documentos INTN** debe pulsar **Aprobar documentación** |
| Mensaje "No pricing rule matches this request. Contact support." | El catálogo de servicio para ONN Norms / Reprint quedó mal configurado o inactivo | Contactar a soporte técnico para revisar **Datos principales → Catálogo de servicio** |
| El cliente ve "Report not available until the related service is invoiced." | El pedido de venta aún no fue facturado | Facturar el expediente desde Ventas |
| El cliente ve "Report not available until the related service is paid." | La factura existe pero no está pagada | Registrar el cobro en Caja/Contabilidad |
| El cliente ve "This document can only be downloaded once." | Ya usó su única descarga | Pedirle que cree una nueva solicitud **ONN Norms Reprint** |
| El cliente ve "Missing sale order for this request." | La solicitud quedó sin expediente | Si sigue en Borrador, pulsar **Confirmar** de nuevo; si no, contactar a soporte |

## Guías relacionadas

- Trámite del cliente en portal: [../../portal/marcas-onc/normas-onn.md](../../portal/marcas-onc/normas-onn.md)
- Trazabilidad y etiquetas ONC (misma app, menú **Operaciones**): [trazabilidad-etiquetas.md](trazabilidad-etiquetas.md)
- Gestión de certificación ONC: [gestion-certificacion-onc.md](gestion-certificacion-onc.md)
- Revisión documental transversal: [../registro-documentos/revision-documental.md](../registro-documentos/revision-documental.md)
- Expedientes, ventas y convenios: [../ventas-caja/expedientes-ventas-convenios.md](../ventas-caja/expedientes-ventas-convenios.md)
- Contabilidad, caja y pagos: [../ventas-caja/contabilidad-caja-pagos.md](../ventas-caja/contabilidad-caja-pagos.md)
