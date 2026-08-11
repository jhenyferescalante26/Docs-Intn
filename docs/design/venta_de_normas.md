# Venta de Normas — análisis y plan

> Estado: **propuesta** (2026-07-27). Basado en el relevamiento de ONN
> (flujo conformado el 27/01/2026, acta del 04/02/2026), las minutas del
> 13 y 14/01, y la base legacy `intn_v12`.
> Complementa a [`portal_navegacion.md`](portal_navegacion.md) §1 y su Fase D.

---

## 1. Qué hay hoy

### 1.1 En la base legacy

| Dato | Valor |
|---|---|
| Productos de norma (`NP…`, `PNA-…`) | 887 |
| Publicados en la web | 846 |
| **Con el PDF cargado** (`product_template.norma_document`, `bytea`) | **857** |
| Órdenes que incluyen normas | 3.025 |
| Facturado | 814.939.000 Gs |

**El PDF ya vive en el producto**, en una columna binaria propia. No hay
tabla de descargas, ni contador, ni límite: **el control de descargas no
existe en v12** — es funcionalidad nueva.

### 1.2 En v18

Cero normas migradas. La tienda existe pero muestra los 26 muebles de la demo
de Odoo. Ya hay, eso sí, un tile "Ecommerce" (`/my/ecommerce`) en el inicio del
portal, agregado por `intn_portal_registration` — una entrada preparada y sin
contenido.

---

## 2. El circuito, según el flujo conformado

El flujograma de ONN separa dos caminos con una línea punteada:

**Presencial (CITN)** — se mantiene:
```
Depto crea contacto → carga expediente (producto "Venta de Norma")
  → facturación → notifica → entrega en físico
```

**Virtual (ONN)** — el que toca construir:
```
0. Registro en el portal
1. Compra en línea
2. El cliente adjunta comprobante de pago
3. Se genera el expediente
4. ONN revisa y concilia el pago por transferencia
5. Se envía el PDF automáticamente          ← "PDF «Pagado»"
```

Con dos notas escritas en el mismo flujo: *«se sugiere avisar a los usuarios el
envío de la norma»* y, como evolución, *«ya no sea x transferencia sino x QR —
AquiPago / PagoPar»*.

### Requisitos textuales del relevamiento

| Requisito | Fuente |
|---|---|
| «El cliente debe poder realizar **compra en línea**» y autogestionarse | ANÁLISIS ONN |
| «**Pago directo desde una pasarela**», hoy es transferencia manual | minuta 14/01 |
| «Incluir los **datos institucionales del INTN en el apartado de tienda**» | minuta 14/01 |
| «Para que el cliente pueda visualizar debe estar **pagada la Norma**» | ANÁLISIS ONN |
| «**Marca de agua** o que la descarga quede restringida y deba volver a solicitarse autorización» | ANÁLISIS ONN |
| «El PDF cuente con **restricción de impresión**» | minuta 14/01 |
| Notificar estado: **Inicio / En proceso de entrega / Entregado** | ANÁLISIS ONN |

### Decisión de negocio agregada (2026-07-27)

**Límite de descargas por compra: 2**, parametrizable en
`res.config.settings`. No figura en el relevamiento; es una definición nueva
que concreta el «que la descarga quede restringida» de arriba.

---

## 3. Modelo de datos propuesto

Reutiliza lo que ya existe en vez de inventar: el gate de descarga-tras-pago ya
está resuelto para certificados (`paid_invoice` → `portal_pdf_download_allowed`).

```
product.template
  └── intn_norma_document      (Binary)   el PDF, migrado de v12
  └── intn_is_norma            (Boolean)  discrimina norma de servicio

res.config.settings
  └── intn_norma_download_limit (Integer, default 2)

intn.norma.download            (nuevo — la bitácora)
  ├── order_line_id   → sale.order.line   qué compra habilita la descarga
  ├── partner_id      → res.partner       quién descargó
  ├── user_id         → res.users
  ├── download_date
  └── ip / user_agent (auditoría)
```

El contador **no se guarda como campo**: se cuenta sobre la bitácora. Un
contador escrito se desincroniza; una bitácora además responde *quién* y
*cuándo*, que es lo que se necesita si el cliente reclama.

---

## 4. Edge cases

Esta es la parte que hay que definir antes de escribir código. Cada fila es una
decisión de negocio, no una de implementación.

### 4.1 Sobre el límite de descargas

| # | Caso | Por qué importa | Propuesta |
|---|---|---|---|
| E1 | Se agotan las 2 descargas | El relevamiento dice «deba volver a solicitarse autorización» | Botón "Solicitar nueva descarga" que abre un ticket a ONN; ONN autoriza y suma cupo |
| E2 | La descarga se corta a mitad | ¿Consume cupo una descarga fallida? | Registrar al **completar** la respuesta, no al iniciarla. Si no se puede, no descontar y auditar |
| E3 | ¿El límite es por orden, por empresa o por usuario? | Una empresa con 5 usuarios de portal compró una vez | **Por línea de orden**: la compra habilita 2 descargas, las use quien las use dentro de la empresa |
| E4 | El cliente compra **dos veces** la misma norma | ¿Se suman los cupos? | Sí: cada línea de orden aporta su propio cupo |
| E5 | Compra presencial (CITN) del mismo cliente | Pagó en ventanilla, ¿puede bajarla del portal? | Si el expediente carga el producto, aplica igual. Confirmar con ONN |

### 4.2 Sobre el ciclo de vida de la norma

| # | Caso | Por qué importa | Propuesta |
|---|---|---|---|
| E6 | La norma se **revisa** tras la compra (`NP-ISO 9001:2015` reemplaza `:2008`) | ¿El cliente baja la que compró o la vigente? | **La que compró.** Guardar el PDF en la línea de orden, no resolverlo contra el producto en cada descarga |
| E7 | La norma se **deroga/anula** | ¿Se puede seguir bajando? | Sí, con leyenda de estado. Un cliente puede necesitar la derogada para un litigio |
| E8 | El producto no tiene PDF cargado | 30 de los 887 en v12 | Bloquear la venta: si no hay documento, no se publica |
| E9 | Cambio de precio entre compra y descarga | — | Irrelevante: la orden congela el precio |

### 4.3 Sobre el pago

| # | Caso | Por qué importa | Propuesta |
|---|---|---|---|
| E10 | Pago **parcial** | ¿Habilita? | No. El gate ya existente exige factura pagada |
| E11 | Transferencia **rechazada** tras haber entregado | Hoy la conciliación es manual y posterior | Revocar el cupo restante y notificar. Lo ya descargado no se puede deshacer — es el argumento fuerte para pasar a pasarela |
| E12 | Nota de crédito / devolución | ¿Se revoca? | Sí, revocar cupo restante |
| E13 | Carrito con **normas + servicios** mezclados | Los servicios nacen de una solicitud, no del carrito | Decidir si se permite. Recomiendo **no**: son circuitos distintos |

### 4.4 Sobre el PDF entregado

| # | Caso | Por qué importa | Propuesta |
|---|---|---|---|
| E14 | Marca de agua | El relevamiento la pide | Con datos del comprador (RUC/razón social) y fecha. Desalienta la redistribución |
| E15 | Restricción de impresión | Pedido en minuta 14/01 | Requiere cifrar el PDF con permisos. **Ojo: es disuasorio, no infalible** — hay que decirlo a ONN para no prometer de más |
| E16 | ¿Se regenera en cada descarga o se guarda? | Regenerar permite marca de agua con fecha real de descarga | Regenerar al vuelo desde el original |
| E17 | Norma en varios idiomas | Algunas NP-ISO tienen versión ES/EN | Confirmar si existe el caso; hoy es un único binario |

### 4.5 Sobre la migración

| # | Caso | Por qué importa | Propuesta |
|---|---|---|---|
| E18 | 857 PDFs en `bytea` | Pesan; van a `ir.attachment` | Migrar como adjuntos, no como columna binaria |
| E19 | 887 productos vs 846 publicados | 41 no publicados | Migrar todos, publicar solo los que lo estaban |
| E20 | Compras históricas de v12 | ¿El cliente puede bajar lo que compró antes? | **Decisión de negocio.** Si sí, hay que sembrar cupos a partir de las 3.025 órdenes |

---

## 5. Plan por fases

### Fase N1 — Catálogo 🟡
Migrar los 887 productos con precio, publicación y PDF (a `ir.attachment`).
Despublicar los muebles de demo. Datos institucionales del INTN en la tienda.

✅ La tienda muestra normas reales.

### Fase N2 — Compra y entrega 🔴
Gate de descarga sobre factura pagada, reutilizando
`portal_pdf_download_allowed`. Bitácora `intn.norma.download`, límite
parametrizable en `res.config.settings`. Notificaciones de estado.

✅ El cliente compra, paga y baja su norma, con cupo controlado.

### Fase N3 — Protección del PDF 🟡
Marca de agua con datos del comprador y restricción de impresión.

✅ El documento entregado es trazable.

### Fase N4 — Autorización adicional 🟢
Flujo de "solicitar nueva descarga" al agotarse el cupo (E1).

---

## 6. A confirmar antes de empezar

1. **E3** — ¿el cupo es por orden, por empresa o por usuario?
2. **E6** — ¿el cliente baja la versión que compró o la vigente?
3. **E13** — ¿se permite carrito mixto de normas y servicios?
4. **E20** — ¿las compras históricas de v12 dan derecho a descarga?
5. **E15** — confirmar con ONN que la restricción de impresión es disuasoria,
   no una garantía técnica.
