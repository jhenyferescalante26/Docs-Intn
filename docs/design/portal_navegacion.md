# Rediseño de la navegación del portal

> Estado: **propuesta** (2026-07-27), verificada contra `intn_demo` corriendo y el código de `custom_addons/intn_portal/*`.
> Capturas del estado actual: `docs/design/_images/rigid_vs_trailer/18-portal-inicio-actual.jpg` y siguientes.

---

## 1. Qué vende INTN, en concreto

La pregunta de partida era si el e-commerce se puede quitar. **No, y no solo
por el cobro: hay una línea de venta por catálogo real.**

### 1.1 Venta de Normas — el catálogo que falta migrar

INTN vende **Normas Paraguayas** como documentos. En la base legacy `intn_v12`:

| Dato | Valor |
|---|---|
| Productos de norma (`NP…`, `PNA-…`) | **887** |
| Publicados en la web | **846** |
| Órdenes que incluyen normas | **3.025** |
| Líneas vendidas | 7.396 |
| Facturado | **814.939.000 Gs** |

Las más vendidas: `NP 2 028 96` (371 veces), `NP-ISO 9001` (141),
`NP 24 001 80` (140), `NP-ISO/IEC 17025` (104).

El área es **ONN**, departamento **CITN** (Centro de Información Tecnológica y
de Normas Técnicas), y el relevamiento la marca explícitamente como
**ECOMMERCE** (`ANÁLISIS-DE-ORGANISMOS/ONN`).

Requisitos ya levantados para esa venta:

- «El cliente debe poder realizar **compra en línea**» y autogestionarse.
- «Realizar **pago directo desde una pasarela de Pagos**», reemplazando la
  transferencia bancaria manual de hoy (minuta 2026-01-14).
- «Incluir los **datos institucionales del INTN en el apartado de tienda** del
  portal web para consultas de los clientes» (minuta 2026-01-14).
- «Para que el cliente pueda visualizar debe estar **pagada la Norma**».
- «Marca de agua o que la descarga quede restringida», y «**restricción de
  impresión**» en el PDF entregado.
- Notificar estado del pedido: «Inicio, En proceso de entrega, Entregado».

> El gate de descarga-tras-pago ya existe en el sistema para certificados
> (`paid_invoice` → `portal_pdf_download_allowed`). La venta de normas necesita
> el mismo mecanismo, más la protección del PDF.

### 1.2 Lo que hay hoy en v18

| Dato | Valor |
|---|---|
| Productos publicados en la web | **26 — todos muebles de la demo de Odoo** |
| Productos de norma migrados | **0** |
| Productos propios de INTN | servicios de verificación + consumibles (precintos) |

O sea: **la tienda existe pero está vacía de contenido real y llena de demo.**
El problema no es que sobre la tienda: es que **falta su catálogo**.

### 1.3 La otra línea: servicios que nacen de una solicitud

Distinta de la anterior y mucho más grande. No es catálogo:

```
Solicitud de servicio (portal)
        │
        ▼
  sale.order  ──►  factura  ──►  pago
        │                          │
        │                          ▼
        └──────────────►  se habilita la descarga del certificado
```

El producto lo elige `portal_service_sale_mixin._portal_create_sale_order()`
desde el catálogo de servicios, no el cliente desde una vidriera. En v12 esta
línea suma **155.221 órdenes** contra 3.025 de normas.

**Son dos modelos de venta conviviendo en el mismo portal**, y la navegación
tiene que distinguirlos: uno se navega y se compra, el otro se solicita y se
agenda.

---

## 2. Qué se va y qué se queda

| Elemento | Decisión | Por qué |
|---|---|---|
| `website_sale`, `sale`, pagos, facturas | **Queda** | Sostiene ambas líneas de venta |
| Menú "Tienda" (`/shop`) y carrito | **Queda** ⚠️ | Es la venta de normas. El relevamiento pide datos institucionales *dentro* de la tienda |
| Los 26 muebles de demo publicados | **Se despublican** | Son ruido de la demo de Odoo, no catálogo INTN |
| Catálogo de normas | **Falta migrar** | 887 productos en v12, ninguno en v18 |
| Tiles "Mis Pedidos" / "Mis Presupuestos" | **Se separan por línea** | Hoy mezclan compras de normas con servicios solicitados |
| "Sus facturas" / "Nuestras facturas" | **Se unifica a una** | La segunda es jerga interna de Odoo |
| Menús duplicados por triplicado | **Se limpia** | 9 filas en `website_menu` para 3 entradas |

> **Corrección respecto de la versión anterior de este documento:** decía
> ocultar el menú Tienda porque "solo expone muebles de demo". Eso confundía el
> síntoma con la causa. La tienda es una línea de negocio con 814 millones de
> guaraníes facturados en el legacy y requisitos levantados; lo que hay que
> quitar son los muebles, no la tienda.

---

## 3. Arquitectura propuesta

### 3.1 Cabecera

El portal sirve **dos modelos de venta distintos** (§1), y la cabecera tiene que
mostrarlo:

```
[logo INTN]   Normas   Solicitudes   Mi flota   Certificados   Facturación   [🛒]  [usuario ▾]
              └─ comprar ─┘  └──────── solicitar y dar seguimiento ────────┘
```

- **Normas** — el catálogo (`/shop`), con los datos institucionales que pidió
  ONN. El **carrito se queda**: acá sí se compra.
- **Solicitudes / Mi flota / Certificados / Facturación** — el circuito de
  servicios: qué pedí, qué tengo, qué me emitieron, qué debo.

"Inicio" y "Contáctanos" pasan al pie.

### 3.2 Inicio: pendientes, no tiles

Reemplazar los once tiles planos por tres bloques de **estado**:

1. **Requiere tu acción** — solicitudes con documentación observada, pagos
   pendientes que bloquean la entrega de un certificado.
2. **En curso** — solicitudes con su estado y fecha de turno.
3. **Tu flota** — unidades y, cuando haya datos, próximos vencimientos.

> ⚠️ El bloque de vencimientos depende de datos que hoy recién empiezan a
> existir: `expiration_date` se computa desde los certificados desde el commit
> "el vencimiento de la verificación deshabilita el vehículo", y en `intn_demo`
> solo 3 de 45 vehículos tienen fecha. **Antes de construir el widget hay que
> ver cuántos la tienen en producción.**

### 3.3 Una sola entrada por concepto

Hoy hay tres caminos a los acoplados: `/my/trailers`, la sección dentro de
`/my/vehicles`, y el tile del inicio. Propuesta: **"Mi flota" como única
entrada**, con vehículos y acoplados como dos pestañas de la misma página.
`/my/trailers` se conserva como URL para no romper enlaces guardados.

### 3.4 Consistencia de listas

Las dos listas principales no se parecen: `/my/service_requests` usa los
widgets nuevos (`PortalSearchSelect`), `/my/vehicles` usa `<select>` planos.
Unificar sobre los widgets nuevos.

Y el mismo estado se nombra distinto según la página — "Activado" en
`/my/vehicles`, "Active" en `/my/trailers`. Un solo juego de nombres.

---

## 4. Plan por fases

### Fase A — Limpieza 🟢

- **Despublicar los 26 muebles de demo** (no tocar el menú Tienda).
- Deduplicar `website_menu`.
- Separar los tiles de venta por línea y unificar las dos entradas de facturas.
- Cerrar los encabezados de tabla que siguen en inglés (`License Plate`,
  `VIN/Chassis`, `Company`, `Status`, `Action`, `View`).

> **Resuelto (2026-07-27).** Los encabezados estaban hardcodeados dentro de
> templates `xml\`\`` inline en `portal_vehicle_app.js`, sin `_t()`. Un template
> inline no expone su texto al extractor, así que ninguna traducción los podía
> alcanzar por más que estuvieran en el `.po`. Pasan por getters con `_t()`,
> junto con el paginador y las etiquetas de filtro/orden del controlador.
>
> ⚠️ **Hallazgo colateral:** `static/src/xml/portal_vehicle_app_templates.xml`
> declara los mismos nombres de template (`PortalFleetVehiclesListPage`,
> `PortalFleetTrailerForm`, …) que las versiones inline del JS, pero **ningún
> componente lo referencia por nombre** — los componentes usan sus templates
> inline. Es código muerto que duplica el vivo, y es la trampa que explica por
> qué las cadenas parecían traducibles: alguien las tradujo mirando ese archivo.
> **No lo borré**: son 330 líneas y conviene confirmar que nadie lo tenga a
> medio refactorizar.

✅ La tienda deja de ofrecer muebles de oficina; el resto del portal deja de
mezclar jerga de e-commerce con la de servicios.

### Fase B — Cabecera y agrupación 🟡

- Cabecera de cuatro entradas (§3.1).
- "Mi flota" unifica vehículos y acoplados (§3.3).
- Un solo juego de nombres de estado.

✅ Un cliente nuevo encuentra qué hacer sin recorrer once tiles.

### Fase D — Catálogo de normas 🔴

**Alcance confirmado (2026-07-27):** el cliente compra normas y descarga el PDF,
con un límite de descargas por compra (2 por defecto, parametrizable).
Análisis completo, edge cases y fases en
[`venta_de_normas.md`](venta_de_normas.md).

Resumen:

- Migrar los 887 productos de norma desde `intn_v12` con precio y publicación.
- Datos institucionales del INTN dentro de la tienda (pedido de ONN).
- Pago por pasarela reemplazando la transferencia manual.
- Entrega del PDF con la protección pedida, reutilizando el gate
  `paid_invoice` → `portal_pdf_download_allowed` que ya existe para
  certificados.
- Notificación de estado del pedido: Inicio / En proceso de entrega / Entregado.

✅ La tienda tiene qué vender y la entrada "Normas" de la cabecera tiene sentido.

### Fase C — Inicio como panel de pendientes 🟡

- Bloques "Requiere tu acción" / "En curso" / "Tu flota" (§3.2).
- **Precondición:** medir cuántos vehículos de producción tienen
  `expiration_date` tras la migración. Si son pocos, el bloque de vencimientos
  se pospone en vez de mostrarse vacío.

✅ El inicio responde "¿qué tengo pendiente?" en vez de listar secciones.

---

## 5. A confirmar con negocio

1. **¿Cuál de los dos websites es el del portal?** Hay **dos** registros
   (`My Website`, `My Website 2`), ambos sin dominio configurado, y los menús
   están triplicados entre ellos y el menú por defecto. Ocultar "Tienda" hay
   que hacerlo en el website correcto, y sin dominios asignados no se puede
   deducir cuál sirve al portal y cuál a las landings. **Es lo primero a
   resolver: sin esto la Fase A no se puede ejecutar con seguridad.**
2. ~~**¿La migración del catálogo de normas entra en este alcance?**~~
   **RESUELTO (2026-07-27): sí.** Ver `venta_de_normas.md`, que además lista
   las cinco decisiones de negocio que faltan para arrancar.
3. **¿Quién produce el PDF protegido de la norma?** El relevamiento pide marca
   de agua y restricción de impresión. El gate de descarga-tras-pago ya existe
   para certificados; falta decidir si la protección se aplica al generar o al
   entregar.
4. **¿"Mis Pedidos" y "Mis Presupuestos" le sirven al cliente?** Son órdenes
   de venta generadas por sus propias solicitudes; puede que alcance con verlas
   dentro de la solicitud que las originó.
