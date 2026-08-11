# RF 6.2 — Registro de entrega de etiquetas y anillos (ONC-FOR-078)

- **Requisito**: RF 6.2 — "El sistema debe generar un registro de entregas de
  etiquetas y anillos (segun modelo en relevamiento)" (`docs/project/tasks.csv:331`,
  sprint #8).
- **Formulario oficial**: ONC-FOR-078, rev. 1 — "REGISTRO DE VENTAS DE ETIQUETAS
  Y ANILLOS - MARCA INTN - SERVICIOS".
- **Fuente**: `docs/project/relevamiento/extracted/Relevamiento-de-datos/
  ANÁLISIS-DE-ORGANISMOS/ONC/Modelo-de-registro-de-entrega-etiquetas-y-anillos.md`.
- **Módulo destino**: `custom_addons/intn_brand/intn_brand_service_requests`.
- **Rol**: Encargado de Entregas / Operador del ONC.

## 1. Contexto y antecedentes

### 1.1 Estado actual

No existe en Odoo 18 ni en la v12. Lo más cercano es
`intn.brand.voucher.management` (Gestión de Comprobantes), port 1:1 de
`gestion_comprobantes` de v12, que cubre parcialmente el caso:

| v12 | v18 | Cubre ONC-FOR-078 |
|---|---|---|
| `gestion_comprobantes.partner_id` | `partner_id` | Sí |
| `gestion_comprobantes.solicitud_id` | `print_request_id` | No (es solicitud de impresión, no expediente) |
| `gestion_comprobantes_lines.nro_inicial/nro_final` | `number_start/number_end` | Parcial: un solo rango contiguo por línea |
| — | — | Falta: serie, cantidad total por color, contador de pendientes, anillos chicos/grandes, observaciones, PDF |

No hay reporte ONC-FOR-078 en ninguna de las dos versiones (verificado sobre
`ir_act_report_xml` e `ir_ui_view` de la base `intn_v12`).

### 1.2 Evidencia de la base v12 que justifica el diseño

Sobre 545 comprobantes / 988 líneas en `intn_v12`:

- Los operadores **sí** cargaban rangos discontinuos, repitiendo líneas del mismo
  producto en un comprobante (hasta 7 líneas por producto). El caso de uso de las
  mermas por error de impresión es real y frecuente.
- **121 de 988 líneas (12 %)** tienen `qty` que no coincide con el rango
  declarado (ni `nro_final - nro_inicial`, ni `+ 1`).
- **2.177 pares de líneas** del mismo producto tienen rangos solapados: números
  de etiqueta contabilizados dos veces. Ejemplo: la línea 1505 cierra en 70768 y
  la 1502 abre en 70768.

Estos números son la justificación cuantitativa de las reglas de validación de
la sección 4: hoy nada impide que un número de etiqueta se entregue dos veces.

- Los 6 productos etiqueta de v12 (`product_template` 8168–8173) comparten el
  mismo nombre "DCPR - Etiquetas/Anillos de Seguridad" y **no tienen ningún campo
  de color**. Se distinguen solo por su correlativo propio (`sgte_numero_control`:
  48184, 148469, 464670, 941932, 50790, 1205254), que se corresponde con los
  rangos por color del formulario (Roja ~1001, Amarilla ~106873, Celeste ~10017,
  Gris ~100287, Naranja ~100157, Verde ~100091). El color es conocimiento tácito
  del operador. **1 producto = 1 color** es la regla de negocio real.

### 1.3 Decisiones tomadas

| # | Decisión | Elegido |
|---|---|---|
| D1 | Modelado del color de etiqueta | Maestro `intn.brand.label.color` + `Many2one` en `product.template`, consistente con el `intn.brand.ring.color` existente |
| D2 | Anillos chicos/grandes | Descuentan stock contra dos productos `is_ring` configurables a nivel compañía |
| D3 | Relación con Gestión de Comprobantes | Conviven sin acoplarse. El nuevo documento es manual e independiente; el flujo automático Solicitud → Impresión → Gestión de Comprobantes queda intacto |
| D4 | "Expediente" | Apunta a `service.request`. En INTN el término histórico mapeaba a `sale.order`, pero en este proyecto el expediente es la solicitud de servicio |

## 2. Alcance

### 2.1 Dentro de alcance

- Modelo de datos de tres niveles (documento / color / rango).
- Asistente de carga de rangos discontinuos con contador de pendientes en vivo.
- Reglas de validación de rangos, incluida la detección de solapes entre
  documentos confirmados.
- Registro de anillos chicos y grandes con descuento de stock.
- Congelamiento del documento al confirmar.
- Reporte PDF ONC-FOR-078 con recuadros de firma.
- Tests unitarios, tests de renderizado de reporte, suite e2e y documentación de
  backoffice.

### 2.2 Fuera de alcance

- Portal del cliente (el ONC-FOR-078 es un documento de mostrador que se firma en
  papel).
- Migración de los 545 comprobantes de v12 al modelo nuevo (decisión D3: conviven).
- Facturación. El documento registra la entrega física; el cobro sigue por
  `sale.order` como hoy.
- Lectura de códigos de barras / QR sobre las etiquetas entregadas.

## 3. Modelo de datos

### 3.1 `intn.brand.label.color` (nuevo maestro)

Análogo a `intn.brand.ring.color` (`models/brand_master_data.py:60`).

| Campo | Tipo | Notas |
|---|---|---|
| `name` | Char | Requerido. Roja, Amarilla, Celeste, Gris, Naranja, Verde |
| `code` | Char | Opcional, para el reporte y la migración |
| `sequence` | Integer | Orden en el ONC-FOR-078 |
| `active` | Boolean | Default `True` |

Data XML con los 6 colores del formulario, en `data/brand_label_color_data.xml`,
con `noupdate="1"` para que el ONC pueda renombrarlos.

### 3.2 `product.template` (extensión)

| Campo | Tipo | Notas |
|---|---|---|
| `label_color_id` | Many2one `intn.brand.label.color` | Visible solo si `is_label`. No requerido a nivel ORM (hay productos etiqueta históricos sin color), pero **requerido para confirmar** una entrega |

### 3.3 `res.company` + `res.config.settings` (extensión)

| Campo | Tipo | Notas |
|---|---|---|
| `brand_ring_small_product_id` | Many2one `product.product` | Dominio `[('is_ring','=',True)]` |
| `brand_ring_large_product_id` | Many2one `product.product` | Dominio `[('is_ring','=',True)]` |

Expuestos en Ajustes → Inventario / sección Marca, junto a la configuración de
ubicaciones de etiquetas que ya existe.

### 3.4 `intn.brand.label.delivery` (cabecera)

Hereda `mail.thread`, `mail.activity.mixin`. `_order = "id desc"`.

| Campo | Tipo | Notas |
|---|---|---|
| `name` | Char | Secuencia `EEA/000000/AÑO`, `readonly`, `copy=False` |
| `service_request_id` | Many2one `service.request` | **Requerido**. Es el Expediente (D4). `ondelete="restrict"` |
| `partner_id` | Many2one `res.partner` | Requerido. Se precarga del expediente vía onchange, editable |
| `partner_vat` | Char | `related="partner_id.vat"`, `readonly`. Es el RUC |
| `delivery_date` | Date | Default hoy. Requerido |
| `user_id` | Many2one `res.users` | Operador que entrega. Default usuario actual |
| `color_line_ids` | One2many `...delivery.color` | |
| `ring_small_qty` | Integer | Default 0 |
| `ring_large_qty` | Integer | Default 0 |
| `note` | Text | Observaciones |
| `state` | Selection | `draft` / `confirmed` / `cancel` |
| `picking_ids` | One2many `stock.picking` | Transferencias generadas |
| `picking_count` | Integer | Compute |
| `total_label_qty` | Integer | Compute `store=True`, suma de `qty_total` de las líneas |
| `total_assigned_qty` | Integer | Compute `store=True`, suma de `qty_assigned` |
| `total_pending_qty` | Integer | Compute **`store=True`**, suma de `qty_pending`. Gobierna la habilitación del botón Confirmar. Debe almacenarse: un compute sin `store` no es filtrable y el filtro "Pendientes de Asignar" de la vista de búsqueda no carga |
| `can_confirm` | Boolean | Compute. `state == 'draft' and total_pending_qty == 0 and (hay líneas o anillos)` |
| `company_id` | Many2one `res.company` | Default compañía actual |

> **Nota sobre `cancel`**: el criterio de aceptación 6 pide solo Borrador /
> Confirmado. Se agrega `cancel` porque sin él un documento confirmado por error
> queda inmutable para siempre y el criterio 6 exige congelar los rangos. Cancelar
> revierte el movimiento de stock y libera los rangos para reutilización.

### 3.5 `intn.brand.label.delivery.color` (sección por color)

| Campo | Tipo | Notas |
|---|---|---|
| `delivery_id` | Many2one | Requerido, `ondelete="cascade"` |
| `product_id` | Many2one `product.product` | Requerido. Dominio `[('product_tmpl_id.is_label','=',True)]` |
| `label_color_id` | Many2one | `related="product_id.product_tmpl_id.label_color_id"`, `store=True`, `readonly` |
| `qty_total` | Integer | **Cantidad total declarada**. Requerido, `> 0` |
| `qty_assigned` | Integer | Compute `store=True`, suma de `range_ids.qty` |
| `qty_pending` | Integer | Compute `store=True`, `qty_total - qty_assigned`. Puede ser negativo si se pasa |
| `range_ids` | One2many `...delivery.range` | |
| `state` | Selection | `related="delivery_id.state"`, para `readonly` en vistas |

### 3.6 `intn.brand.label.delivery.range` (rango numérico)

| Campo | Tipo | Notas |
|---|---|---|
| `color_line_id` | Many2one | Requerido, `ondelete="cascade"` |
| `series` | Char | Requerido. Default `"S"`. Normalizado a mayúsculas sin espacios |
| `number_from` | Integer | Requerido, `> 0` |
| `number_to` | Integer | Requerido, `>= number_from` |
| `qty` | Integer | Compute `store=True` = `number_to - number_from + 1` |
| `product_id` | Many2one | `related="color_line_id.product_id"`, `store=True`. Indexado: sostiene la búsqueda de solapes entre documentos |
| `delivery_id` | Many2one | `related="color_line_id.delivery_id"`, `store=True` |
| `state` | Selection | `related="delivery_id.state"`, `store=True`. Indexado |

**Convención de conteo**: `qty = number_to - number_from + 1`, rango cerrado en
ambos extremos. Es la convención que cumple el 88 % de los datos v12 y la que
usa el ejemplo del criterio de aceptación (1001–1049 = 49 etiquetas).

> **Diferencia deliberada con `intn.brand.label.print.job`**: el trabajo de
> impresión crea una fila por etiqueta (`_assign_control_numbers`,
> `models/brand_printing.py:253`). Aquí **no** se materializa una fila por
> unidad: una entrega de 200.000 etiquetas debe seguir siendo un puñado de
> registros. Los rangos se almacenan como intervalos.

## 4. Reglas de negocio y validaciones

### 4.1 Rango individual (`@api.constrains` sobre el rango)

| ID | Regla | Mensaje |
|---|---|---|
| R1 | `number_from > 0` | "El número inicial debe ser mayor que cero." |
| R2 | `number_to >= number_from` | "El número final no puede ser menor que el inicial (serie %s, %s / %s)." |
| R3 | `series` no vacía tras `strip()` | "La serie es obligatoria." |
| R4 | Normalización: `series = series.strip().upper()` en `create`/`write` | — |

### 4.2 Solapes

La unicidad de una etiqueta es la terna **(producto, serie, número)**. Dos series
distintas pueden repetir números legítimamente.

| ID | Regla | Alcance |
|---|---|---|
| R5 | Sin solapes entre rangos de la misma línea de color con la misma serie | `@api.constrains` sobre `range_ids` |
| R6 | Sin solapes entre líneas del mismo documento que comparten producto y serie | `@api.constrains` a nivel documento |
| R7 | Sin solapes contra rangos de **otros documentos confirmados** del mismo producto y serie | Verificado en `action_confirm()`, no como constraint |

R7 es la regla que ataca los 2.177 solapes históricos de v12. Se implementa como
búsqueda en `action_confirm()` y no como constraint SQL porque:

- La condición de solape (`a.from <= b.to AND b.from <= a.to`) no es expresable
  como índice único.
- Un borrador puede legítimamente contener rangos que después se corrigen.

El mensaje debe nombrar el documento en conflicto:
"El rango S 1001–1049 del producto Etiqueta Roja se solapa con la entrega
EEA/000012/2026 (S 1040–1060)."

### 4.3 Confirmación (`action_confirm`)

| ID | Regla | Mensaje |
|---|---|---|
| R8 | `qty_pending == 0` en **todas** las líneas de color | "No se puede confirmar: quedan N etiquetas pendientes de asignar en el color X." |
| R9 | El documento no puede estar vacío: al menos una línea de color o un anillo | "La entrega no tiene etiquetas ni anillos registrados." |
| R10 | Cada línea de color tiene al menos un rango | "El color X no tiene rangos numéricos cargados." |
| R11 | Cada producto de línea tiene `label_color_id` | "El producto X no tiene color de etiqueta configurado." |
| R12 | Un mismo producto no puede repetirse en dos líneas de color del documento | "El color X está cargado dos veces." |
| R13 | `ring_small_qty >= 0` y `ring_large_qty >= 0` | "Las cantidades de anillos no pueden ser negativas." |
| R14 | Si `ring_small_qty > 0` y no hay `brand_ring_small_product_id` configurado | "Configure el producto de anillo chico en los ajustes de la compañía." (ídem grande) |
| R15 | R7 (sin solapes contra confirmados) | Ver 4.2 |

Solo si R8–R15 pasan: `state = 'confirmed'`, se genera la transferencia de stock
y se postea el mensaje en el chatter.

### 4.4 Congelamiento (criterio de aceptación 6)

Al confirmar, los rangos quedan congelados para auditoría. No basta con
`readonly` en la vista — en `intn.brand.voucher.management` el congelamiento es
solo de vista (`views/brand_operations_views.xml:227`), lo que deja el modelo
abierto vía RPC o importación.

| ID | Regla |
|---|---|
| R16 | `write()` en documento, línea de color o rango lanza `UserError` si `state != 'draft'`, salvo los campos de la lista blanca (`note`, `message_*`, `activity_*`, `state`, `picking_ids`) |
| R17 | `unlink()` lanza `UserError` si `state != 'draft'` |
| R18 | `copy()` reinicia a `draft`, limpia `name`, `picking_ids` y `delivery_date`, y **sí** copia líneas y rangos (útil para entregas recurrentes; el operador corrige los números). Requiere `copy=True` explícito en los dos One2many: en Odoo el default de `One2many.copy` es `False`, de modo que sin él la copia sale vacía |

### 4.5 Stock

| ID | Regla |
|---|---|
| R19 | Al confirmar se crea un `stock.picking` con el tipo de operación `is_label_delivery_operation` (el mismo que ya usa `intn.brand.voucher.management.action_generate_transfers`) |
| R20 | Un `stock.move` por línea de color con `product_uom_qty = qty_total` |
| R21 | Un `stock.move` por cada anillo con cantidad > 0, contra el producto configurado en la compañía |
| R22 | Si no hay tipo de operación configurado: "Debe configurar un tipo de operación de entrega de etiquetas." (mensaje ya existente en el módulo) |
| R23 | `action_cancel()` sobre un documento confirmado cancela el picking asociado y devuelve el documento a `cancel`, liberando los rangos para R7 |
| R24 | Si algún picking asociado ya fue **validado**, `action_cancel()` falla: "La transferencia %s ya fue validada. Revierta el movimiento de stock antes de cancelar esta entrega." Sin esta guarda, cancelar liberaría los rangos de una mercadería que ya salió del inventario |

## 5. Interfaz de usuario

### 5.1 Formulario

```
┌──────────────────────────────────────────────────────────────────────┐
│ [Confirmar] [Cancelar] [Imprimir ONC-FOR-078]      draft ▸ confirmed │
├──────────────────────────────────────────────────────────────────────┤
│                                       ┌────────────────┐             │
│  EEA/000042/2026                      │ 🚚 Transferenc.│             │
│                                       └────────────────┘             │
│  Expediente      SR/000123/2026        Fecha de entrega  28/07/2026  │
│  Cliente         Industrias del Sur    Operador          M. Benítez  │
│  RUC             80012345-6                                          │
│                                                                      │
│  ⚠ Pendientes de asignar: 11        (badge rojo si > 0, verde si 0)  │
│                                                                      │
│  ┌ Etiquetas ──────────────────────────────────────────────────────┐ │
│  │ Color     Producto          Cant. total  Asignadas  Pendientes  │ │
│  │ ▾ Roja    Etiqueta Roja     110          99         11    🔴    │ │
│  │     Serie  Desde   Hasta   Cantidad                             │ │
│  │     S      1001    1049    49                                   │ │
│  │     S      1051    1100    50                                   │ │
│  │     [Agregar línea]                                             │ │
│  │ ▾ Amarilla Etiqueta Amar.   200          200        0     🟢    │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌ Anillos de seguridad ───────────────────────────────────────────┐ │
│  │ Anillos chicos   203        Anillos grandes   350               │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌ Observaciones ──────────────────────────────────────────────────┐ │
│  └─────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

Decisiones de UI:

- **Sin wizard modal.** El criterio 3 pide "tabla o asistente interactivo". Una
  `list` editable anidada dentro de la línea de color da el recálculo en vivo
  gratis vía computes, sin JS propio, y deja el documento auditable en una sola
  pantalla. Un wizard obligaría a un modelo transitorio y perdería el contexto
  del resto de colores.
- El anidamiento One2many dentro de One2many no es soportado en `list` editable
  de Odoo 18. Se resuelve con el patrón **form-in-list**: la línea de color abre
  un `form` en diálogo que contiene su propia lista de rangos editable. El
  contador de pendientes se ve tanto en el diálogo como en la lista principal.
- `qty_pending` se muestra con `decoration-danger="qty_pending > 0"` y
  `decoration-success="qty_pending == 0"`.
- El botón Confirmar usa `invisible="not can_confirm"`, de modo que "se activa
  automáticamente" cuando el contador llega a 0, como pide el criterio 3.

### 5.2 Menú

Nuevo ítem **Operaciones → Entrega de Etiquetas y Anillos** en
`views/brand_menus.xml`, después de "Gestión de Comprobantes" (secuencia 7).

### 5.3 Seguridad

Grupo nuevo `group_intn_brand_delivery` — "Brand Label Delivery", para el rol
Encargado de Entregas. `group_intn_brand_manager` lo implica.

| Modelo | manager | delivery | printer |
|---|---|---|---|
| `intn.brand.label.delivery` | RWCU | RWC | R |
| `...delivery.color` | RWCU | RWC | R |
| `...delivery.range` | RWCU | RWC | R |
| `intn.brand.label.color` | RWCU | R | R |

Sin reglas de portal: el documento no se expone al cliente (sección 2.2).

## 6. Reporte PDF ONC-FOR-078

### 6.1 Estructura

Réplica del Excel de relevamiento:

- **Cabecera**: "ORGANISMO NACIONAL DE CERTIFICACIÓN" a la izquierda; recuadro a
  la derecha con Código `ONC-FOR-078`, Revisión `1`, Vigencia y Página `1 de 1`.
- **Título**: "REGISTRO DE VENTAS DE ETIQUETAS Y ANILLOS - MARCA INTN- SERVICIOS".
- **Datos**: RUC, Empresa, Expediente, Fecha.
- **Tabla de etiquetas**: columnas `Color | Cant. | Serie | Números Etiquetas |
  Serie | Números Etiquetas`. Dos pares de columnas serie/rango por fila.
- **Anillos de seguridad entregados**: "Anillos chicos:" y "Anillos grandes:".
- **Observación**.
- **Pie**: dos recuadros con línea de firma, "Firma y Aclaración ONC" y
  "Firma y Aclaración Cliente".

### 6.2 Distribución de rangos en la grilla

El formulario original acomoda **2 rangos por fila** y reserva **2 filas por
color** (4 rangos visibles). El modelo permite N rangos.

Regla de renderizado: por cada color, agrupar sus rangos de a dos y emitir
`max(2, ceil(n_rangos / 2))` filas. La celda `Color` y `Cant.` usan `rowspan`
sobre las filas del color. Colores con más de 4 rangos generan filas adicionales
y el formulario crece hacia abajo — es preferible a truncar información oficial.

### 6.3 Implementación

- `ir.actions.report` `action_report_brand_label_delivery`, `report_type`
  `qweb-pdf`, `binding_model_id` al modelo de entrega, siguiendo el patrón de
  `reports/brand_sampling_extraction_report.xml`.
- Paperformat nuevo `paperformat_brand_label_delivery`: A4 **vertical**
  (210 × 297), márgenes 10/10/10/10, `header_line=False`. El Excel es vertical,
  a diferencia de la mayoría de los reportes de marca que son apaisados.
- Un helper `_get_report_rows()` en el modelo devuelve la matriz ya agrupada; el
  QWeb no calcula. Facilita el test unitario de la distribución sin renderizar
  PDF.
- Preferir `t-field` sobre helpers de formato, por la convención de `AGENTS.md`,
  **excepto en `number_from` / `number_to`**: `t-field` aplica el formato
  numérico del idioma y en es_PY imprime la etiqueta 1102 como "1.102". Un
  número de etiqueta no lleva separador de miles, así que esos dos campos usan
  `t-out`. Las cantidades (total por color, anillos) sí van con `t-field`.

## 7. Casos borde

Numerados para trazar contra los tests de la sección 8.

### 7.1 Rangos

| # | Caso | Comportamiento esperado |
|---|---|---|
| E1 | `number_to < number_from` | `ValidationError` (R2) |
| E2 | `number_from = 0` o negativo | `ValidationError` (R1) |
| E3 | Rango de un solo número (`1001`–`1001`) | Válido, `qty = 1` |
| E4 | Serie vacía o `"  "` | `ValidationError` (R3) |
| E5 | Serie `" s "` | Se normaliza a `"S"`; no genera falso negativo de solape contra `"S"` |
| E6 | Dos rangos con **distinta** serie y números solapados | Válido — la serie desambigua |
| E7 | Dos rangos con misma serie que se tocan en el borde (1001–1050 y 1050–1100) | `ValidationError` (R5). Es el patrón exacto del bug histórico de v12 |
| E8 | Rango contenido dentro de otro (1010–1020 dentro de 1001–1100) | `ValidationError` (R5) |
| E9 | Rango que abarca millones de números | Sin degradación: no se materializan filas por unidad |

### 7.2 Contador de pendientes

| # | Caso | Comportamiento esperado |
|---|---|---|
| E10 | Suma de rangos < `qty_total` | `qty_pending > 0`, badge rojo, Confirmar oculto |
| E11 | Suma de rangos > `qty_total` | `qty_pending` **negativo**, badge rojo, Confirmar oculto. El operador ve cuánto se pasó, en vez de un error que le borra el trabajo |
| E12 | Suma exacta | `qty_pending = 0`, Confirmar visible (criterio 3) |
| E13 | Se borra un rango de una línea ya completa | `qty_pending` vuelve a ser > 0 y Confirmar desaparece |
| E14 | Se cambia `qty_total` con rangos ya cargados | Recalcula; no borra los rangos |
| E15 | Se cambia `product_id` de la línea con rangos cargados | Los rangos se conservan pero se revalida R7 contra el producto nuevo al confirmar |

### 7.3 Confirmación

| # | Caso | Comportamiento esperado |
|---|---|---|
| E16 | Documento sin líneas ni anillos | `UserError` (R9) |
| E17 | Documento solo con anillos, sin etiquetas | Válido — entregas de solo anillos ocurren |
| E18 | Línea de color con `qty_total` cargado y cero rangos | `UserError` (R10) |
| E19 | Producto sin `label_color_id` | `UserError` (R11) con el nombre del producto |
| E20 | Mismo producto en dos líneas de color | `UserError` (R12) |
| E21 | Solape con documento **confirmado** de otro expediente | `UserError` (R7) nombrando el documento en conflicto |
| E22 | Solape con documento **en borrador** | Permitido. Solo lo confirmado es fuente de verdad |
| E23 | Solape con documento **cancelado** | Permitido (R23 libera los rangos) |
| E24 | Confirmar dos veces (doble clic) | La segunda llamada es no-op, no duplica el picking |
| E25 | Confirmación concurrente de dos documentos con rangos solapados | R7 se evalúa dentro de la transacción de `action_confirm` con `flush_model()` previo. La segunda transacción falla con el mensaje de solape |

### 7.4 Anillos y stock

| # | Caso | Comportamiento esperado |
|---|---|---|
| E26 | Cantidad de anillo negativa | `ValidationError` (R13) |
| E27 | Anillo con cantidad > 0 sin producto configurado | `UserError` (R14) indicando dónde configurarlo |
| E28 | Ambos anillos en 0 | No se generan movimientos de anillo; el documento es válido si hay etiquetas |
| E29 | Sin tipo de operación de entrega configurado | `UserError` (R22) |
| E30 | Stock insuficiente | El picking se crea en estado no disponible; no se bloquea la confirmación. La entrega física ya ocurrió — el sistema la registra, no la autoriza |

### 7.5 Congelamiento y ciclo de vida

| # | Caso | Comportamiento esperado |
|---|---|---|
| E31 | Editar un rango de un documento confirmado (UI o RPC) | `UserError` (R16) |
| E32 | Borrar una línea de color de un documento confirmado | `UserError` (R17) |
| E33 | Editar `note` en un documento confirmado | **Permitido** — lista blanca de R16. Las observaciones posteriores a la entrega son parte del proceso |
| E34 | Borrar un documento confirmado | `UserError` (R17) |
| E35 | Duplicar un documento confirmado | Copia en `draft`, sin `name` ni pickings, con líneas y rangos (R18) |
| E36 | Cancelar un confirmado y volver a confirmar otro con los mismos rangos | Permitido (E23) |

### 7.6 Datos de cabecera

| # | Caso | Comportamiento esperado |
|---|---|---|
| E37 | Expediente sin cliente asociado | `partner_id` queda vacío y es requerido: el operador lo carga a mano |
| E38 | Cliente sin RUC (`vat` vacío) | Se permite confirmar; el PDF imprime el campo vacío. Bloquear la entrega física por un dato maestro incompleto no aporta |
| E39 | Cambiar el expediente después de cargar líneas | Permitido en borrador; `partner_id` **no** se pisa si ya tiene valor |
| E40 | Fecha de entrega futura | Permitido, sin advertencia |

### 7.7 Reporte

| # | Caso | Comportamiento esperado |
|---|---|---|
| E41 | Color con 1 rango | Se emiten 2 filas (mínimo del formulario), la segunda vacía |
| E42 | Color con 5 rangos | 3 filas; el `rowspan` de Color/Cant. cubre las 3 |
| E43 | Documento en borrador | El PDF se genera igual, con marca de agua o leyenda "BORRADOR" |
| E44 | Observación larga (> 500 caracteres) | El recuadro crece; los recuadros de firma no se solapan con el texto |
| E45 | 6 colores con 4 rangos cada uno | Entra en una página; si no, el pie de firmas queda en la última página |

## 8. Estrategia de pruebas

> `AGENTS.md:39` fija una política temporal de no agregar tests nuevos. Esta
> especificación los incluye porque el usuario los pidió de forma explícita para
> este requisito.

### 8.1 Tests unitarios

Archivo nuevo `tests/test_brand_label_delivery.py`, tags
`intn`, `post_install`, `-at_install`, `intn_brand_label_delivery`.

| Test | Cubre |
|---|---|
| `test_range_qty_computation` | E3, convención `+1` |
| `test_range_invalid_bounds` | E1, E2 |
| `test_series_required_and_normalized` | E4, E5 |
| `test_overlap_same_series_rejected` | E7, E8 |
| `test_overlap_different_series_allowed` | E6 |
| `test_pending_counter_flow` | **El ejemplo textual del criterio 3**: 110 → 61 → 11 → 0 |
| `test_pending_counter_negative_when_exceeded` | E11 |
| `test_confirm_blocked_when_pending` | E10, R8 |
| `test_confirm_allowed_when_zero_pending` | E12 |
| `test_confirm_empty_document` | E16 |
| `test_confirm_rings_only` | E17 |
| `test_confirm_requires_color_on_product` | E19 |
| `test_confirm_duplicate_color_line` | E20 |
| `test_confirm_overlap_with_confirmed_document` | E21 |
| `test_confirm_overlap_with_draft_allowed` | E22 |
| `test_confirm_overlap_with_cancelled_allowed` | E23, E36 |
| `test_confirm_idempotent` | E24 |
| `test_ring_negative_qty` | E26 |
| `test_ring_without_configured_product` | E27 |
| `test_confirm_creates_picking_with_moves` | R19–R21 |
| `test_frozen_after_confirm` | E31, E32, E34 |
| `test_note_editable_after_confirm` | E33 |
| `test_copy_resets_to_draft` | E35 |
| `test_cancel_reverts_picking` | R23 |
| `test_sequence_assigned` | `name` distinto de `/` |
| `test_report_rows_grouping` | E41, E42 — sobre `_get_report_rows()`, sin renderizar |

`setUpClass` reutiliza el patrón de `tests/test_brand_workflows.py`: partner,
`product.template` con `is_label=True` + `label_color_id`, productos de anillo y
compañía configurada.

### 8.2 Tests de reporte

En `tests/test_brand_report_rendering.py`, siguiendo la convención de
`AGENTS.md:49` (HTML + PDF con `force_report_rendering=True`):

| Test | Cubre |
|---|---|
| `test_label_delivery_report_html` | Render HTML; asserts sobre `ONC-FOR-078`, `Firma y Aclaración ONC`, `Firma y Aclaración Cliente`, RUC y expediente |
| `test_label_delivery_report_pdf` | `_render_qweb_pdf` devuelve bytes que empiezan con `%PDF` |
| `test_label_delivery_report_draft` | E43 |

No hace falta test de ruta `HttpCase`: el reporte no es accesible desde el portal.

### 8.3 E2E (Playwright)

Archivo nuevo `e2e/specs/brand/21-brand-entrega-etiquetas-anillos.spec.ts`,
siguiendo el estilo de `21-brand-comprobantes-entregas.spec.ts` (contextos por
rol, `roleRpc`, `openBackendModel`).

| Caso | Descripción |
|---|---|
| `FUNC 21e-1` | El rol `onc` abre **Operaciones → Entrega de Etiquetas y Anillos** y ve la lista |
| `FUNC 21e-2` | Crear entrega: elegir expediente, verificar que el cliente y el RUC se precargan |
| `FUNC 21e-3` | **Caso del criterio 3 en UI**: cargar 110 rojas, ver "Pendientes: 110", cargar 1001–1049 → 61, 1051–1100 → 11, 1102–1112 → 0, y verificar que el botón Confirmar aparece recién al llegar a 0 |
| `FUNC 21e-4` | Intentar confirmar con pendientes ≠ 0 vía RPC → error |
| `FUNC 21e-5` | Cargar anillos chicos/grandes y confirmar; verificar el picking generado |
| `FUNC 21e-6` | Documento confirmado: campos en solo lectura; editar un rango por RPC falla |
| `FUNC 21e-7` | Descargar el PDF ONC-FOR-078 y verificar `content-type: application/pdf` |
| `FUNC 21e-8` | Solape contra documento confirmado → error nombrando el documento |
| `FUNC 21e-9` | Seguridad de menú: un rol sin `group_intn_brand_delivery` no ve el ítem |

Helper nuevo `e2e/lib/flows/brand-label-delivery.ts` con
`setupLabelDeliveryDraft()` y `addColorRange()`, reutilizable entre casos.
Requiere datos semilla en `e2e/scripts/seed_e2e_data.py`: productos etiqueta con
color asignado y productos de anillo configurados en la compañía.

### 8.4 Datos demo

En `demo/brand_traceability_scenarios_demo.xml`: una entrega en borrador con
pendientes ≠ 0 y una confirmada con rangos discontinuos que replica el ejemplo
del formulario (110 rojas en tres tramos). Sirve de escenario de UAT y alimenta
`scripts/generate-scenario-coverage-from-v12.py`.

## 9. Documentación

### 9.1 Guía de backoffice (nueva)

`docs/admin/marcas-onc/entrega-etiquetas-anillos.md`, con el frontmatter del
conjunto admin (`nn`, `dominio`, `roles`, `estado`) y la estructura que usa
`trazabilidad-etiquetas.md`:

- Para quién es esta guía — rol Encargado de Entregas / Operador ONC.
- Qué resuelve — trazabilidad oficial de insumos entregados, con mermas por error
  de impresión.
- Configuración previa — **colores de etiqueta asignados a cada producto**
  (paso obligatorio, ver 10.1), productos de anillo chico/grande en los ajustes
  de la compañía, tipo de operación de entrega, secuencia `EEA/`.
- Antes de empezar — el expediente debe existir como solicitud de servicio.
- Pasos: crear la entrega, cargar colores y cantidades, cargar rangos leyendo el
  contador de pendientes, registrar anillos, confirmar, imprimir el ONC-FOR-078
  y recolectar firmas.
- **Caso de mermas por error de impresión**, con el ejemplo 110 → 1001–1049,
  1051–1100, 1102–1112 y capturas.
- Qué revisar si algo falla — tabla de mensajes de error (R7–R22) con su causa y
  su solución.
- Capturas en `docs/admin/_images/marcas-onc/`.

### 9.2 Actualizaciones

| Archivo | Cambio |
|---|---|
| `docs/admin/marcas-onc/trazabilidad-etiquetas.md` | Agregar el menú nuevo a la lista de Operaciones y enlazar la guía nueva |
| `docs/admin/README.md` | Índice |
| `docs/project/v12-v18-gap-matrix.md` | Marcar RF 6.2 como implementado y anotar que no es migración sino funcionalidad nueva |
| `docs/project/tasks.csv` | RF 6.2 a estado implementado |
| `e2e/E2E_GAPS_CHECKLIST.md` | Reemplazar el `test.skip` "FUNC 21d-4: import XLSX registro entrega etiquetas y anillos" por la referencia a la suite nueva |

### 9.3 i18n

Todo el código y las etiquetas en inglés (convención de `AGENTS.md:115`), con
traducción `es_PY` vía `python scripts/i18n-sync.py`. Términos fijados:

| Inglés | es_PY |
|---|---|
| Label Delivery | Entrega de Etiquetas y Anillos |
| Label Color | Color de Etiqueta |
| Total Quantity | Cantidad Total |
| Assigned | Asignadas |
| Pending to Assign | Pendientes de Asignar |
| Series | Serie |
| From / To | Desde / Hasta |
| Small Rings / Large Rings | Anillos Chicos / Anillos Grandes |

## 10. Riesgos y dependencias

### 10.1 Configuración de colores en productos existentes (bloqueante operativo)

`label_color_id` es dato nuevo y **no es inferible** desde v12: los 6 productos
comparten nombre y no tienen campo de color (sección 1.2). Sin él, R11 impide
confirmar cualquier entrega.

Mitigación: el correlativo actual de cada producto identifica su color de forma
unívoca para el ONC. Se entrega una tabla de referencia en la guía de backoffice
para que el operador asigne los seis colores en una sola sesión:

| `next_control_number` v12 | Rango del ONC-FOR-078 | Color |
|---|---|---|
| 48184 | 1001 | Roja |
| 148469 | 106873 | Amarilla |
| 464670 | 10017 | Celeste |
| 941932 | 100287 | Gris |
| 50790 | 100157 | Naranja |
| 1205254 | 100091 | Verde |

> La correspondencia debe ser **confirmada por el ONC** antes de cargarla: se
> infiere del orden de magnitud de los correlativos, no de un dato explícito.

### 10.2 Otros riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| R7 sobre un histórico con solapes preexistentes | Si en el futuro se migran los 988 registros de v12, 2.177 pares fallarían | D3 evita la migración. Si se decide migrar, R7 solo aplica a documentos del modelo nuevo |
| Anidamiento One2many en One2many | Limitación de Odoo 18 | Patrón form-in-list (5.1), sin JS propio |
| Vigencia del formulario | El Excel dice rev. 1, vigencia 2022 | El código y la revisión van como texto en el QWeb, fáciles de actualizar |
| Productos de anillo no configurados | Bloquea confirmación con anillos | R14 con mensaje que indica dónde configurarlo; documentado en 9.1 |

## 11. Criterios de aceptación → trazabilidad

| CA | Descripción | Cubierto por |
|---|---|---|
| 1 | Cabecera: expediente, empresa/RUC, fecha | 3.4, E37–E39 |
| 2 | Etiqueta por color + cantidad total | 3.1–3.3, 3.5, E19 |
| 3 | Asistente de rangos, serie, cálculo por línea, contador en vivo, bloqueo de validación | 3.6, 4.3 (R8), 5.1, E10–E13, `test_pending_counter_flow`, `FUNC 21e-3` |
| 3b | Ejemplo 110 → 61 → 11 → 0 con mermas | `test_pending_counter_flow`, `FUNC 21e-3`, demo 8.4 |
| 5 | Anillos chicos y grandes | 3.3, 3.4, R13, R14, R21, E26–E28 |
| 6 | Observaciones; borrador/confirmado; congelar rangos; descontar stock | 3.4, 4.4, 4.5, E31–E35 |
| 7 | PDF ONC-FOR-078 con recuadros de firma | 6, E41–E45, 8.2 |
