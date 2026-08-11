# RF 6.2 — Plan de implementación

> **Estado: implementado el 28/07/2026.** Las 8 fases están completas y
> verificadas. Resultados: 32 tests unitarios + 3 de reporte en verde
> (`odoo test intn_brand_label_delivery`), 10 casos e2e en verde
> (`21-brand-entrega-etiquetas-anillos.spec.ts`), `pre-commit` limpio.
> Al cierre quedan dos fallos **preexistentes** en el módulo, verificados
> contra el código base con `git stash`:
> `TestPortalBrandRequests.test_portal_brand_pages_and_pdf_download`
> (unitario) y los e2e `21c-4` y `21f-4`.

Deriva de [`rf-6.2-entrega-etiquetas-anillos.md`](rf-6.2-entrega-etiquetas-anillos.md).
Las referencias `Rn` / `En` apuntan a las reglas y casos borde de ese documento.

- **Módulo**: `custom_addons/intn_brand/intn_brand_service_requests`
- **Versión del manifiesto**: `18.0.3.1.0` → `18.0.4.0.0` (modelos nuevos)
- **Rama**: `18.0`
- **Commits**: `[18.0] [FEAT] ONC: registro de entrega de etiquetas y anillos (ONC-FOR-078)`
  y sucesivos por fase, según `CONTRIBUTING.md`

## Resumen de fases

| Fase | Contenido | Entregable verificable |
|---|---|---|
| 1 | Maestro de color + configuración de anillos | Módulo actualiza; los 6 colores existen; ajustes visibles |
| 2 | Modelos de entrega + computes | `qty_pending` correcto en shell |
| 3 | Validaciones y ciclo de vida | R1–R23 activas |
| 4 | Vistas, menú y seguridad | Flujo completo usable en UI |
| 5 | Reporte ONC-FOR-078 | PDF descargable |
| 6 | Tests unitarios y de reporte | `odoo test intn_brand_label_delivery` en verde |
| 7 | Datos demo y e2e | Suite Playwright en verde |
| 8 | Documentación e i18n | Guía publicada, `.po` sincronizado |

Las fases 1–5 son secuenciales. La 6 puede solaparse desde el final de la 3.

## Fase 1 — Maestro de color y configuración

**Archivos**

| Acción | Archivo |
|---|---|
| editar | `models/brand_master_data.py` — clase `BrandLabelColor` |
| editar | `models/product_template.py` — `label_color_id` |
| nuevo | `models/res_company.py` — `brand_ring_small_product_id`, `brand_ring_large_product_id` |
| nuevo | `models/res_config_settings.py` — `related` a los dos anteriores |
| nuevo | `data/brand_label_color_data.xml` — 6 colores, `noupdate="1"` |
| editar | `models/__init__.py`, `__manifest__.py` (`data`, `version`) |
| editar | `views/brand_master_data_views.xml` — list/form de color |
| editar | `views/brand_inherit_views.xml` — `label_color_id` en producto, `invisible="not is_label"` |
| nuevo | `views/res_config_settings_views.xml` — sección Marca |
| editar | `views/brand_menus.xml` — **Datos principales → Color de Etiquetas** |
| editar | `security/ir.model.access.csv` — `intn.brand.label.color` |

**Verificación**

```bash
odoo update-module intn_brand_service_requests -d intn_demo
```

Y en shell: los 6 colores existen y `product.template` acepta `label_color_id`.

## Fase 2 — Modelos de entrega

**Archivos**

| Acción | Archivo |
|---|---|
| nuevo | `models/brand_label_delivery.py` — las tres clases |
| editar | `models/__init__.py` |
| editar | `data/brand_sequences_data.xml` — secuencia `intn.brand.label.delivery`, prefijo `EEA/`, padding 6, sufijo `/%(year)s`, `use_date_range` |
| editar | `security/ir.model.access.csv` — 3 modelos × 3 grupos |
| editar | `security/security.xml` — `group_intn_brand_delivery` |

**Orden dentro del archivo de modelos**

1. `BrandLabelDelivery` — campos, `create()` con secuencia, computes
   (`total_pending_qty`, `can_confirm`, `picking_count`), onchange de expediente.
2. `BrandLabelDeliveryColor` — computes `qty_assigned` / `qty_pending` con
   `store=True` y `@api.depends("qty_total", "range_ids.qty")`.
3. `BrandLabelDeliveryRange` — compute `qty`, normalización de `series` en
   `create`/`write`.

**Puntos de atención**

- `qty_assigned` y `qty_pending` con `store=True`: los necesita el dominio del
  botón Confirmar y el reporte. Verificar que la invalidación funcione al borrar
  un rango (E13) — es el caso que suele romperse con computes almacenados.
- `product_id` y `state` del rango son `related ... store=True` **indexados**:
  sostienen la búsqueda de solapes de R7 sobre el histórico.
- Nada de generar un registro por unidad (E9).

**Verificación** — en shell sobre `intn_demo`, reproducir el ejemplo del criterio
3 y comprobar la secuencia 110 → 61 → 11 → 0.

## Fase 3 — Validaciones y ciclo de vida

Todo en `models/brand_label_delivery.py`.

| Bloque | Implementa |
|---|---|
| `@api.constrains` en rango | R1, R2, R3, R5 (E1, E2, E4, E7, E8) |
| Normalización de serie en `create`/`write` | R4 (E5) |
| `@api.constrains` en documento | R6, R13 |
| `_check_overlapping_confirmed()` | R7 (E21–E23), con `flush_model()` previo (E25) |
| `action_confirm()` | R8–R15, guard de idempotencia (E24) |
| `_create_delivery_picking()` | R19–R22 (E29, E30) |
| `action_cancel()` | R23 (E36) |
| `write()` en las tres clases | R16 con lista blanca (E31, E33) |
| `unlink()` en las tres clases | R17 (E32, E34) |
| `copy()` / `_get_copiable_values` | R18 (E35) |

**Puntos de atención**

- **R7 es el núcleo del requisito.** La consulta busca sobre
  `intn.brand.label.delivery.range` con dominio
  `[("state","=","confirmed"), ("product_id","=",p), ("series","=",s),
  ("number_from","<=",to), ("number_to",">=",from)]`, excluyendo el documento
  actual. El mensaje debe nombrar el documento en conflicto y el rango concreto.
- `write()` debe distinguir la escritura del propio `action_confirm` (que cambia
  `state`) de una edición del usuario. Usar lista blanca de campos, no un flag de
  contexto: un flag es evadible desde RPC y el congelamiento es requisito de
  auditoría.
- `_create_delivery_picking()` reutiliza `is_label_delivery_operation`, el mismo
  tipo de operación que `intn.brand.voucher.management.action_generate_transfers`
  (`models/brand_voucher.py:231`). No inventar uno nuevo.
- No usar `qty_done` en `stock.move.line`: en Odoo 18 el campo es `quantity`. El
  código existente de `brand_voucher.py` y `brand_label_print_job.py` todavía usa
  `qty_done`; **no replicar ese patrón** en el código nuevo.

**Verificación** — en shell: confirmar un documento con pendientes falla;
confirmar dos documentos con rangos solapados falla en el segundo; un documento
confirmado rechaza el `write` sobre un rango.

## Fase 4 — Vistas, menú y seguridad

| Acción | Archivo |
|---|---|
| nuevo | `views/brand_label_delivery_views.xml` — list, form del documento, form-in-list de la línea de color, search, acción |
| editar | `views/brand_menus.xml` — **Operaciones → Entrega de Etiquetas y Anillos**, secuencia 7 |
| editar | `__manifest__.py` — la vista antes de `brand_menus.xml` |

**Detalles de la vista**

- Botón Confirmar con `invisible="not can_confirm"` (criterio 3: "se activa
  automáticamente").
- `total_pending_qty` en el `sheet` como alerta:
  `<div class="alert alert-warning" invisible="total_pending_qty == 0">`.
- Lista de líneas de color: `qty_total`, `qty_assigned`, `qty_pending` con
  `decoration-danger="qty_pending != 0"` y `decoration-success="qty_pending == 0"`.
- La línea de color abre un `form` en diálogo (patrón form-in-list) con su lista
  de rangos editable `bottom` — Odoo 18 no soporta One2many anidado en `list`
  editable.
- `readonly="state != 'draft'"` en todos los campos salvo `note`, coherente con
  la lista blanca de R16.
- Search view con filtros por estado, cliente, expediente y color; agrupar por
  cliente y por mes de entrega.

**Verificación** — recorrer el flujo completo en `intn_demo` como usuario del
grupo delivery; comprobar que el ítem de menú no aparece sin el grupo.

## Fase 5 — Reporte ONC-FOR-078

| Acción | Archivo |
|---|---|
| nuevo | `reports/brand_label_delivery_report.xml` — `ir.actions.report` + template |
| editar | `reports/brand_paperformats.xml` — `paperformat_brand_label_delivery`, A4 vertical |
| editar | `models/brand_label_delivery.py` — `_get_report_rows()` |
| editar | `__manifest__.py` |

`_get_report_rows()` devuelve, por color, una lista de filas ya emparejadas
(`[(rango_izq, rango_der), ...]`) con mínimo 2 filas, más el `rowspan`. El QWeb
solo itera. Así la distribución (E41, E42) se testea sin renderizar PDF.

Réplica visual del Excel según la sección 6.1 del spec: recuadro de código /
revisión / vigencia / página arriba a la derecha, tabla de etiquetas con doble
par serie/rango, bloque de anillos, observación y los dos recuadros de firma al
pie. Preferir `t-field` sobre helpers de formato (`AGENTS.md:49`).

**Verificación** — imprimir desde la UI y comparar contra el Excel de
relevamiento; probar un color con 5 rangos y una observación larga (E44).

## Fase 6 — Tests

| Acción | Archivo |
|---|---|
| nuevo | `tests/test_brand_label_delivery.py` — 26 tests de la sección 8.1 |
| editar | `tests/test_brand_report_rendering.py` — 3 tests de la sección 8.2 |
| editar | `tests/__init__.py` |

Tags: `intn`, `post_install`, `-at_install`, `intn_brand_label_delivery`.
Los de reporte llevan además `intn_reports`.

```bash
odoo test intn_brand_label_delivery
odoo test intn_reports
```

`test_pending_counter_flow` reproduce literalmente el ejemplo del criterio de
aceptación 3 y es el test que hay que mirar primero si algo se rompe.

## Fase 7 — Demo y e2e

| Acción | Archivo |
|---|---|
| editar | `demo/brand_traceability_scenarios_demo.xml` — una entrega en borrador con pendientes y una confirmada con los tres tramos del ejemplo |
| editar | `e2e/scripts/seed_e2e_data.py` — colores en productos etiqueta, productos de anillo en la compañía |
| nuevo | `e2e/lib/flows/brand-label-delivery.ts` — `setupLabelDeliveryDraft()`, `addColorRange()` |
| nuevo | `e2e/specs/brand/21-brand-entrega-etiquetas-anillos.spec.ts` — casos `FUNC 21e-1` a `21e-9` |
| editar | `e2e/E2E_GAPS_CHECKLIST.md` |

```bash
cd e2e && npx playwright test specs/brand/21-brand-entrega-etiquetas-anillos.spec.ts
```

> Ejecutar Playwright **siempre** desde `e2e/`. Desde la raíz del repo se limpia
> `test-results/`.

Requiere Odoo corriendo sobre `e2e_intn` **sin** `--test-enable`.

## Fase 8 — Documentación e i18n

| Acción | Archivo |
|---|---|
| nuevo | `docs/admin/marcas-onc/entrega-etiquetas-anillos.md` |
| nuevo | capturas en `docs/admin/_images/marcas-onc/` |
| editar | `docs/admin/marcas-onc/trazabilidad-etiquetas.md` |
| editar | `docs/admin/README.md` |
| editar | `docs/project/v12-v18-gap-matrix.md` |
| editar | `docs/project/tasks.csv` — RF 6.2 |
| editar | `i18n/es_PY.po` |

```bash
python scripts/i18n-sync.py sync -d intn_demo --installed
python scripts/i18n-sync.py pending -d intn_demo --modules intn_brand_service_requests
msgfmt -c -v -o /dev/null custom_addons/intn_brand/intn_brand_service_requests/i18n/es_PY.po
```

Nunca sobrescribir `msgstr` existentes.

La guía sigue el conjunto admin descrito en
`.agents/skills/intn-process-documentation/SKILL.md` e incluye la tabla de
correspondencia correlativo → color de la sección 10.1 del spec, marcada como
**pendiente de confirmación por el ONC**.

## Cierre

```bash
pre-commit run --all-files
odoo test intn                     # sin regresiones en el resto del módulo
odoo update-module intn_brand_service_requests -d intn_preprod
```

## Puntos que requieren decisión o confirmación externa

| # | Punto | Quién decide | Bloquea |
|---|---|---|---|
| 1 | Correspondencia correlativo → color de los 6 productos etiqueta (spec 10.1) | ONC | Uso en producción, no el desarrollo |
| 2 | Vigencia a imprimir en el recuadro del ONC-FOR-078 (el Excel dice rev. 1, 2022) | ONC | Fase 5, valor cosmético |
| 3 | Si el rol Encargado de Entregas justifica `group_intn_brand_delivery` propio o alcanza con `group_intn_brand_manager` | Equipo | Fase 4 |

Ninguno bloquea el arranque: 1 y 2 son datos de configuración y 3 tiene un
default razonable (grupo propio, implicado por manager).
