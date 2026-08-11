# RF 2.7 — Presupuesto asociado a la solicitud

> Estado: **retornado en ClickUp** ([86e0yxqna](https://app.clickup.com/t/86e0yxqna), sprint #2).
> Análisis al commit `a43632c8` (28/07/2026). No considera trabajo sin commitear.
>
> **Enunciado:** *«El sistema debe permitir al cliente visualizar el presupuesto
> asociado a una solicitud.»*

---

## 1. Por qué está retornado

La tarjeta pasó a *Retornado*, no a *Pendiente*: se implementó, se probó y QA la
devolvió con **dos observaciones**. Ambas están registradas como comentarios en
ClickUp y son la razón por la que no se puede cerrar sin más.

| # | Observación | Autor | Fecha |
|---|---|---|---|
| O1 | «Dependiendo de la capacidad y compartimiento del vehículo debe mostrar el precio en el portal, hoy en día ya se tiene un precio fijo para cada uno (es un servicio que ya existe)» | Isaura Flores | 05/04/2026 |
| O2 | «En vez de COTIZACIONES debe decir PRESUPUESTOS» | — | 15/03/2026 |

El punto de O1 es que el portal mostraba **un precio único** para la
verificación de cisternas, cuando el negocio ya cobraba por tramo de capacidad
× cantidad de compartimientos. Es decir: el presupuesto que veía el cliente
estaba mal, no ausente.

---

## 2. Estado real de cada observación

### O1 — Precio por capacidad y compartimiento ✅ resuelto

Resuelto por el commit `53a1a0a4` (23/07/2026),
*"feat(fleet): capacity-bracket pricing for cistern verification catalogs"*,
posterior a la devolución.

**Dónde:**

| Archivo | Rol |
|---|---|
| `intn_portal_fleet_requests/models/service_request_fleet_asset_mixin.py` | Campos `capacity`, `compartment_count` y el calculado `verification_price_bracket` |
| `intn_portal_fleet_requests/hooks.py` | Crea el producto con una variante por tramo y fija `price_extra` por variante |
| `intn_portal_fleet_requests/migrations/18.0.2.1.15/post-migrate.py` | Reapunta los catálogos existentes al producto por tramos |

**Tabla de tramos** (`_compute_verification_price_bracket`):

| Tramo | Capacidad | Compartimientos | Precio (Gs) |
|---|---|---|---|
| 1 | ≤ 20.000 L | ≤ 2 | 1.375.000 |
| 2 | ≤ 20.000 L | > 2 | 1.485.000 |
| 3 | ≤ 40.000 L | ≤ 2 | 1.650.000 |
| 4 | ≤ 40.000 L | ≤ 4 | 1.870.000 |
| 5 | ≤ 40.000 L | > 4 | 2.310.000 |
| 6 | > 40.000 L | — | 2.750.000 |

`compartment_count` suma tanque + acoplado, y `_onchange_vehicle_id()` lo
precarga desde el vehículo (en altas de vehículo nuevo queda manual, porque el
activo todavía no existe en base).

Catálogos alcanzados: `service_catalog_fleet_annual_verification_line_main` y
`service_catalog_fleet_enabling_line_main`.

> ⚠️ **Riesgo abierto.** Los tramos y los importes fueron **reconstruidos del
> texto libre** de las líneas de venta de `intn_v12` (v12 nunca los guardó como
> dato estructurado), contrastados contra la venta más reciente de cada tramo a
> enero/2026. El propio código lo deja anotado: *«Pending official sign-off from
> ONM commercial»*. **Sin esa validación de ONM, el cliente puede estar viendo
> un precio incorrecto** — que es exactamente lo que O1 vino a corregir.

### O2 — Terminología «Presupuesto» 🟡 casi resuelto

`intn_portal_sale_orders/i18n/es_PY.po` ya traduce los términos visibles:

| msgid | msgstr |
|---|---|
| `Back to Quotations` | Volver a Presupuestos |
| `My Quotations` | Mis Presupuestos |
| `Quotation (Draft)` | Presupuesto (Borrador) |
| `Quotation Sent` | Presupuesto Enviado |

**Queda un remanente:**

- `intn_portal_fleet_requests/i18n/es_PY.po:149` →
  `msgstr "<strong>Cotización / Pedido de Venta:</strong>"`

Es la etiqueta que se ve dentro del detalle de la solicitud de flota, es decir
**justo en la pantalla que el RF describe**. Hay que cambiarla a
`<strong>Presupuesto / Pedido de Venta:</strong>`.

Aparte: `intn_portal_sale_orders/i18n/es_PY.po` tiene 41 `msgstr ""` sin
traducir. No bloquean el RF, pero conviene pasarles
`scripts/i18n-sync.py apply-pending` antes de la demo.

---

## 3. Qué falta para cerrar

| # | Acción | Tipo | Bloqueante |
|---|---|---|---|
| A1 | Validar los 6 tramos y sus importes con el área comercial de ONM | Negocio | **Sí** |
| A2 | Corregir «Cotización» → «Presupuesto» en `intn_portal_fleet_requests/i18n/es_PY.po:149` | Código | Sí |
| A3 | Correr `apply-pending` sobre `intn_portal_sale_orders` | Código | No |
| A4 | Re-test del flujo: alta de solicitud → el portal muestra el presupuesto con el precio del tramo correcto | QA | Sí |

A1 es el único que no depende del equipo de desarrollo. Conviene pedirlo ya,
porque sin firma de ONM el re-test no prueba nada: se validaría contra una
tabla que nadie confirmó.

---

## 4. Criterios de aceptación

1. El cliente ve, dentro de su solicitud de servicio, el presupuesto asociado
   con importe, moneda y estado.
2. Para verificación de cisternas, el importe corresponde al tramo que resulta
   de capacidad × compartimientos, según tabla firmada por ONM.
3. Al cambiar el vehículo o el acoplado, el importe se recalcula.
4. La interfaz dice «Presupuesto» en todas las pantallas del portal; no aparece
   «Cotización» en ningún punto del circuito.
5. El presupuesto es visible sólo para el gestor y el beneficiario de la
   solicitud.

---

## 5. Referencias

- Tarea: [86e0yxqna](https://app.clickup.com/t/86e0yxqna)
- Commit del tramo de precios: `53a1a0a4`
- `docs/project/user-stories/SPRINT_1_5_COMPLIANCE_CHECKLIST.csv` → US-S2-03
- Escenarios de prueba de la migración: `ESCENARIOS_DE_PRUEBA.md` (workspace de migración)
