# Pendientes técnicos

> Relevado el 28/07/2026 contra `d2a1c68e`. Cada ítem incluye la evidencia con
> la que se detectó, para no tener que volver a diagnosticarlo.
>
> Nada de esto bloquea el trabajo en curso: son fallos preexistentes y deuda
> que hoy no tiene tarjeta asignada.

---

## 1. Tests que fallan en `intn_portal_fleet_requests`

Confirmados sobre `intn_demo` comparando el código base contra la rama: **fallan
igual en ambos**, así que no los introdujo ningún cambio reciente.

### 1.1 `TestCertificateModificationAutofill` — 5 errores

`tests/test_certificate_modification_autofill.py`, todos al crear la solicitud
en `_create_cert_mod_request()` (línea 66):

```
odoo.exceptions.ValidationError: Este vehículo no tiene un certificado válido.
Debe completarse una Verificación Inicial antes de solicitar este tipo de servicio.
```

Lo levanta `_assert_vehicle_has_valid_certificate_for_service_type()` en
`models/fleet_vehicle_service_request.py:546`.

Tests afectados: `test_company_name_modification_autofills_old_values`,
`test_emblem_modification_autofills_old_values`,
`test_emblem_modification_uses_truck_emblem_when_trailer_has_none`,
`test_onchange_refreshes_current_values`,
`test_ruc_modification_autofills_old_values`.

**Diagnóstico probable:** el guard se agregó después que los tests, y el fixture
arma el vehículo sin un certificado válido previo. A decidir: si el fixture debe
crear la Verificación Inicial, o si el guard no corresponde para
`certificate_modification`.

### 1.2 `test_enabling_ui_specs_group_front_and_back` — ✅ resuelto (28/07/2026)

Era un bug real de `_build_fleet_portal_attachment_ui_specs()`, no un test
desactualizado: los adjuntos sueltos se volcaban antes que los agrupados, de
modo que los pares siempre quedaban al final sin respetar el `sequence`
declarado. Además, un grupo al que le faltara un lado se descartaba entero con
un `continue`, y el documento desaparecía del formulario del portal.

Corregido en una sola pasada que preserva el orden y degrada el par incompleto
a fila simple.

### 1.2 bis `test_form_payload_returns_owl_descriptor`

```
AssertionError: 'default_values' not found in {...}
```

`tests/test_portal_service_request_header.py:138`. El `initial_data` del payload
del portal ya no trae la clave `default_values` que el test espera. Confirmado
preexistente contra el código base. Falta decidir si la clave debe volver o si
el test quedó viejo.

### 1.3 `test_record_specs_follow_service_type`

```
AssertionError: 0 != 3
```

`tests/test_fleet_attachment_requirements.py:149`. Espera 3 specs para
`emblem_change`, pero ese catálogo está **inactivo en las cinco bases del
sandbox** (`service_catalog_fleet_onm_data.xml` lo declara `active=False`). El
test contradice los datos: o se reactiva el catálogo, o se ajusta la aserción.

---

## 2. Tests que fallan en `intn_brand_service_requests`

Detectados al cerrar el RF 6.2 y confirmados contra el código base con
`git stash`, o sea preexistentes:

- `test_portal_brand_pages_and_pdf_download` (unitario)
- E2E `21c-4` y `21f-4`

---

## 3. Bug de `qty_done`

Fuera del alcance del RF 6.2, que no replicó el patrón en el código nuevo:

- `models/brand_voucher.py:268`
- `models/brand_label_print_job.py:283`

---

## 4. `test_certificate_report_pdf_smoke` cuelga

En `intn_fleet_cistern_certificates`, el test dispara `wkhtmltopdf`, que se quedó
**16 minutos** en un solo render hasta que se mató el proceso. Bloquea correr la
suite completa del módulo.

La política del proyecto es verificar los reportes por **renderizado HTML**, no
generando el PDF. Este test debería alinearse con eso.

---

## 4 bis. Los tests de derivación de OT nunca se ejecutaron

`intn_mrp_workorder_forwarding/tests/` **no tiene `__init__.py`**, así que Odoo
no descubre `test_workorder_forwarding.py`. Sus 13 casos —los mismos 7
escenarios que se documentaron en la tarjeta del RF 5.20— nunca corrieron.

Al habilitarlo de prueba, **11 de 13 erroran por una sola causa compartida**:

```
File "tests/test_workorder_forwarding.py", line 44, in _get_one_ready_workorder
    workorder = mo.workorder_ids[0]
IndexError: tuple index out of range
```

`_get_one_ready_workorder()` asume que `TestMrpCommon.generate_mo()` deja
órdenes de trabajo, pero en Odoo 18 ese helper arma la LdM **sin operaciones**
(`generate_mo` no tiene parámetro de workorders y el BoM que crea no lleva
`operation_ids`), de modo que la OP nace sin ninguna OT.

Arreglarlo es reescribir el escenario del helper para que la LdM tenga
operaciones sobre `workcenter_1`. Se dejó el `__init__.py` **sin agregar** a
propósito: habilitarlo hoy pondría la suite en rojo por una condición
preexistente, en medio del trabajo de otros. Conviene hacerlo como tarea propia.

---

## 5. Modelo sin reglas de acceso

Advertencia en cada carga de módulos:

```
The models ['service.request.portal.form.layout'] have no access rules
in module intn_portal_fleet_requests
```

---

## 6. Nombres invertidos en las alturas de compartimiento

`intn_fleet_cistern_certificates/models/compartment_dimension.py`: los nombres de
campo están cruzados respecto de sus etiquetas.

| Campo | Etiqueta | Contenido real |
|---|---|---|
| `full_space_height` | "Total Space Height" | altura de espacio **total** (manual) |
| `total_space_height` | "Full Space Height" | altura de espacio **lleno** (calculada) |

**El cálculo es correcto** (`lleno = total − vacío`); sólo confunde a quien lea
el código. Los flags `compartment_show_*` arrastran la misma inversión.

Arreglarlo es un *swap* de dos columnas almacenadas: necesita columna temporal
intermedia, toca **12 archivos en 4 módulos** e incluye los reportes QWeb del
certificado de medición. Beneficio funcional: cero. Conviene hacerlo aparte, con
prueba de migración de ida y vuelta, no dentro de un lote de cambios rápidos.

---

## 7. Confirmación pendiente del ONC

La tabla **correlativo → color** de etiquetas está marcada como *inferida* en el
spec del RF 6.2. Sin los colores cargados en los seis productos no se puede
confirmar ninguna entrega en producción. Es decisión de negocio, no desarrollo.
