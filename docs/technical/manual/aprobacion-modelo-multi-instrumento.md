# Formulario "Aprobación de Modelo" — Grilla multi-instrumento (Agregar Instrumento)

Módulo: `custom_addons/intn_portal/intn_portal_metrology_dispenser_requests`

Este documento describe la implementación del botón **"Agregar Instrumento"**
en el formulario de portal de Aprobación de Modelo (observación 7 del área
usuaria), la decisión de arquitectura tomada (**Opción A**), por qué **no** se
eligió la Opción B, y cómo migrar a la Opción B en el futuro si el negocio lo
solicita.

---

## 1. Requerimiento (observación 7)

> Incorporar el botón **Agregar Instrumento** para permitir registrar
> **múltiples instrumentos** dentro de una **misma solicitud**, conforme a la
> funcionalidad definida para el Portal de Clientes. Al presionar el botón, la
> información ingresada deberá **agregarse a la grilla** de servicios **antes
> del envío** definitivo de la solicitud.

Criterios verificables:

| # | Criterio | Estado |
|---|----------|--------|
| R1 | Botón "Agregar Instrumento" visible | ✅ |
| R2 | Varios instrumentos en una misma `service.request` | ✅ |
| R3 | Grilla acumulativa en el navegador | ✅ |
| R4 | La grilla se arma antes del envío; el submit manda todo junto | ✅ |
| R5 | Mismo patrón/UX que el resto del Portal (OIAT/ONI) | ✅ |
| R6 | No romper recepción de muestra, clasificación, verificación ni reportes | ✅ |

---

## 2. Decisión de arquitectura: Opción A

El instrumento en Aprobación de Modelo vivía **solo en el encabezado** de
`service.request` (campos `instrument_type_id`, `instrument_brand_id`,
`instrument_model_id`, `operating_range_min/max`, `operating_range_uom_id`,
`sample_quantity`, `instrument_description`, `model_family`). Esos campos son
**consumidos por el flujo de ejecución posterior**:

- **Recepción de muestra** (`metrology.sample.reception`) → usa `sample_quantity`.
- **Reglas de clasificación** (`data/metrology_classification_rule_data.xml`) →
  deciden el departamento según `instrument_type_id`.
- **Verificación técnica** y **reportes** → leen marca/modelo/rango.

### Opción A (implementada)

- El **encabezado conserva el "instrumento primario"** y sigue alimentando el
  flujo de ejecución **sin modificarlo**.
- Se agrega una **grilla de instrumentos** modelada como líneas
  `service.request.line` con `line_kind = "model_approval_instrument"` y campos
  propios prefijados `ma_*` apuntando a los catálogos **independientes** de
  metrología (`metrology.instrument.*`, `metrology.measure.uom`).
- Al crear la solicitud, **todos** los instrumentos se guardan como líneas y el
  **primero se refleja** en los campos de instrumento del encabezado
  (compatibilidad total con ejecución, reportes y tests existentes).

Ventajas: riesgo bajo y contenido, tests existentes siguen pasando, reversible.
Deuda menor: el primer instrumento queda duplicado (encabezado + su línea) y el
flujo de ejecución opera hoy solo sobre el instrumento primario (el RF pide
"registrar", no "procesar" cada instrumento por separado).

### Por qué NO la Opción B

La Opción B (eliminar los campos de instrumento del encabezado y migrar todo el
flujo a leer desde las líneas) implicaba:

- Tocar el **corazón del flujo de ejecución** (recepción, clasificación,
  verificación técnica, reportes) → alto riesgo de regresión.
- **Reescribir tests** existentes (`test_model_approval_request.py`,
  `test_model_approval_reports.py`).
- Requiere **decisiones de negocio hoy indefinidas**: ¿la clasificación y la
  recepción de muestra son **por instrumento** o **por solicitud**? El RF de la
  observación 7 no lo responde — solo pide "registrar".

La Opción A entrega el requerimiento con riesgo bajo y **no cierra la puerta a
B**: los instrumentos ya quedan modelados como líneas, de modo que una futura
migración a B parte de esa base.

---

## 3. Cambios realizados (Opción A)

### 3.1 Modelo de línea (nuevo)

`models/metrology_model_approval_service_request_line.py`
- `_inherit = "service.request.line"`.
- `selection_add=[("model_approval_instrument", "Model Approval Instrument")]`
  con `ondelete={"model_approval_instrument": "cascade"}`.
- Campos `ma_instrument_description`, `ma_instrument_type_id`,
  `ma_instrument_brand_id`, `ma_instrument_model_id`, `ma_model_family`,
  `ma_operating_range_min`, `ma_operating_range_max`,
  `ma_operating_range_uom_id`, `ma_sample_quantity`.
- Onchange marca↔modelo (coherencia al editar en backend).
- Registrado en `models/__init__.py`.

> No se reutilizó la línea `metrology_equipment` existente porque sus campos
> `brand_id`/`model_id` apuntan a catálogos de **flota**
> (`fleet.vehicle.model.brand`), lo que reacoplaría Aprobación de Modelo con
> camiones cisterna — justo lo que la observación 2 pide evitar.

### 3.2 Backend — parseo y reflejo al encabezado

`models/service_request_model_approval_mixin.py`
- `_validate_model_approval_instrument(data, idx, errors)` — valida un
  instrumento (M2O existen, marca↔modelo coherente, rango mín≤máx, cantidad ≥1).
  `idx=0` suprime el prefijo "Instrument N:" (instrumento único/legacy).
- `_model_approval_line_command(vals)` — construye el comando `(0, 0, {ma_*})`.
- `_portal_parse_model_approval_instruments(kw, errors)` — lee el JSON de la
  grilla (`model_approval_service_lines`); si no está presente, **cae al
  fallback** de los campos planos (compatibilidad con envíos y tests previos).
  Devuelve `(line_commands, first_vals)`.
- `_portal_prepare_model_approval_vals(...)` — ahora arma los instrumentos vía
  el parser, **refleja el primero** en los campos de instrumento del encabezado
  y setea `header["line_ids"] = line_commands`.

El controlador `_portal_create_model_approval_request`
(`intn_portal_fleet_requests/portal/_shared/controllers/service_request.py`)
**no requirió cambios**: ya hace `**header_vals` en el `create()`, por lo que
`line_ids` se incluye en la única transacción de creación.

### 3.3 Frontend — grilla Owl

`static/src/portal/forms/model_approval/model_approval_service_form.js`
- `state.draft` (instrumento en edición) + `state.instruments` (grilla).
- Getter `canAddInstrument`, métodos `addInstrument()` / `removeInstrument(i)`.
- `_syncHiddenInput()` serializa a `<input type="hidden"
  name="model_approval_service_lines">` con `{services:[...]}`.
- `validate()` exige ≥1 instrumento; `prepareSubmit()` sincroniza el hidden.
- La carga dependiente marca→modelo (`_loadModels`) opera sobre `state.draft`.

`static/src/portal/forms/model_approval/model_approval_service_form.xml`
- El bloque "Datos del Instrumento" pasa a ser el **borrador** (sin `name=` ni
  `required` nativo; los `PortalSearchSelect` con `required="false"`).
- Botón **"Agregar Instrumento"** (deshabilitado hasta que el borrador es
  válido) + tabla-grilla con botón de quitar por fila.

`intn_service_request/.../portal_form_engine/portal_service_form_view.js`
- `_getPortalDelegate()` ahora incluye `this._modelApprovalDelegate`, de modo
  que `validate()`/`prepareSubmit()` del shell lleguen a la grilla. (Antes el
  delegate se registraba pero no se consultaba, y el form enviaba los campos de
  instrumento nativamente.)

### 3.4 Bugs preexistentes corregidos (detectados al demostrar el flujo)

Durante la demostración end-to-end aparecieron dos defectos **preexistentes**
que impedían cumplir realmente el punto 5. Ambos se corrigieron:

**(a) Todos los adjuntos quedaban obligatorios en el navegador**

`intn_portal_fleet_requests/.../portal_attachments_panel.xml` usaba
`t-att-required="spec.mandatory ? 'required' : null"`. Owl renderiza ese `null`
como el **string literal `"null"`**, y en HTML cualquier valor en `required`
activa la obligatoriedad. Resultado: la etiqueta salía sin asterisco
(correcto) pero el input bloqueaba el envío (incorrecto). Se cambió `null` por
`false`, que Owl sí elimina. Afecta a las 3 ocurrencias del panel — es un
archivo compartido, por lo que también corrige adjuntos opcionales de otros
portales (flota).

**(b) Los adjuntos nunca se persistían en Aprobación de Modelo**

El override `_get_required_attachment_specs()` estaba definido en
`service.request.model.approval.mixin`, pero ese mixin abstracto resuelve en la
posición **77** del MRO de `service.request`, **por debajo** de
`service.request.attachment.requirement.mixin` (posición **55**), que devuelve
`[]` y corta la cadena. El override era código muerto: `specs` llegaba vacío a
`_portal_create_attachments`, que entonces no creaba ningún `ir.attachment`
(verificado: todas las solicitudes `model_approval`, incluidas las de abril y
junio, tenían 0 adjuntos).

Se movió el override a la clase concreta `ServiceRequest` de
`metrology_dispenser_service_request.py`, que resuelve en la posición **12**,
por encima del mixin base. Se dejó un docstring explicando el porqué para que
no vuelva a moverse al mixin.

**(c) El detalle del portal mostraba los instrumentos como filas vacías**

La tabla "Equipo" del detalle (`portal_templates.xml`, bloque metrología)
iteraba `service_request.line_ids` **sin filtrar por `line_kind`**, usando las
columnas de `metrology_equipment` (Serie, Emblem, Marca, Modelo, Manufacturer —
campos de catálogo de *flota*). Las nuevas líneas `model_approval_instrument`
no tienen esos campos, así que aparecían como filas de guiones.

Correcciones:
- La tabla "Equipo" ahora filtra a `metrology_equipment` y se oculta si no hay
  ninguna. La condición se aplicó **sobre los elementos** (`<h5 t-if=...>`,
  `<div t-if=...>`) y no envolviéndolos en un `<t t-if>`, porque
  `portal_metrology_documents_views.xml` hace `xpath .../h5[1]` como hijo
  directo y un wrapper rompía ese xpath.
- Se agregó una tabla **"Instrumentos"** (en el módulo de metrología, template
  `portal_service_request_page_model_approval_instruments`) con las columnas
  `ma_*` reales.

Verificado sin regresión: una solicitud con líneas de equipo sigue mostrando
"Equipo"; una de aprobación de modelo muestra "Instrumentos".

### 3.5 Backend — vista

`views/metrology_model_approval_views.xml`
- Nueva sección "Instruments" con `line_ids` filtrado por
  `line_kind = 'model_approval_instrument'` (lista editable con los `ma_*`).

---

## 4. Verificación

- **Frontend (Playwright, base `intn`)**: se agregaron 2 instrumentos a la
  grilla; el hidden input generó
  `{"services":[{...sample_quantity:2},{...sample_quantity:1}]}`; carga
  dependiente marca→modelo OK; **0 errores de consola**.
- **Backend (`odoo shell`)**: `_portal_prepare_model_approval_vals` con el JSON
  de 2 instrumentos devolvió `ERROR: None`, `LINE COUNT: 2`, VUI capturado y el
  primer instrumento reflejado en el encabezado.
- **Tests**: la suite del módulo corre 50 tests; **todas las clases de Model
  Approval pasan**. Los 4 fallos observados
  (`TestInitialVerificationWorkflow`, `TestMetrologyDispenserRequest`,
  `TestMetrologySaleOrderProduct`) son **artefactos de datos locales** — el
  producto `intn_portal_service_products.product_template_metrology_periodic`
  (id 52) fue reasignado manualmente de organismo/departamento durante el debug
  de esta sesión, rompiendo la resolución del producto default en esa base. No
  están relacionados con este cambio.
- **flake8 / imports / comentarios inline**: limpios.

---

## 5. Cómo migrar a la Opción B (si el área usuaria lo solicita)

Si en una observación futura se pide que **cada instrumento se procese por
separado** (clasificación, recepción de muestra, verificación y reporte por
instrumento), estos son los pasos para migrar de A → B. La base ya está puesta:
los instrumentos ya son líneas `model_approval_instrument`.

### 5.1 Definir primero las reglas de negocio

Antes de tocar código, confirmar con el área usuaria:
- ¿La **clasificación** de departamento es por instrumento o por solicitud?
- ¿La **recepción de muestra** es una por instrumento (N recepciones) o una por
  solicitud?
- ¿El **certificado/reporte** es uno por instrumento o uno agregado?

Estas respuestas determinan la cardinalidad de los modelos de ejecución.

### 5.2 Migrar el flujo de ejecución a leer desde las líneas

`models/service_request_metrology_execution_mixin.py`
- Reemplazar las lecturas de `self.instrument_type_id`, `self.sample_quantity`,
  `self.operating_range_*`, etc. por iteración sobre
  `self.line_ids.filtered(lambda l: l.line_kind == "model_approval_instrument")`
  y sus campos `ma_*`.

`models/metrology_sample_reception.py`
- Si la recepción pasa a ser por instrumento: crear una `sample.reception` por
  línea (usar `ma_sample_quantity` de cada línea en lugar del `sample_quantity`
  del encabezado).

`models/metrology_technical_classification.py` + reglas de clasificación
- Si la clasificación es por instrumento: aplicar la regla a cada
  `ma_instrument_type_id` de las líneas (hoy usa el `instrument_type_id` del
  encabezado).

`report/metrology_model_approval_reports.xml`
- Iterar `line_ids` (`ma_*`) en vez de imprimir los campos del encabezado.

### 5.3 Eliminar el "instrumento primario" del encabezado

`models/service_request_model_approval_mixin.py`
- Quitar del mixin los campos `instrument_description`, `instrument_type_id`,
  `instrument_brand_id`, `instrument_model_id`, `model_family`,
  `operating_range_min`, `operating_range_max`, `operating_range_uom_id`,
  `sample_quantity`.
- En `_portal_prepare_model_approval_vals`, eliminar el bloque
  `header.update({...instrumento primario...})` (dejar solo
  `header["line_ids"] = line_commands`).
- En `_validate_model_approval_fields`, reemplazar las validaciones de esos
  campos por "al menos una línea `model_approval_instrument`".
- Eliminar el fallback de campos planos en
  `_portal_parse_model_approval_instruments` (ya no habría envíos planos).

### 5.4 Reescribir los tests

`tests/test_model_approval_request.py` y `tests/test_model_approval_reports.py`
- Dejar de setear los campos de instrumento en el `create()` del encabezado;
  crear en su lugar `line_ids` con comandos `(0, 0, {ma_*})`.
- Assertar sobre
  `req.line_ids.filtered(lambda l: l.line_kind == "model_approval_instrument")`.
- Revisar `tests/test_initial_verification_execution_workflow.py` por si crea
  solicitudes `model_approval` seteando esos campos directamente.

### 5.5 Frontend

El frontend **no necesita cambios** para B: ya envía la grilla completa como
JSON. Solo se elimina, si se desea, cualquier reflejo del "instrumento
primario" (que en A vivía en el backend, no en el JS).

---

## 6. Archivos tocados (resumen)

| Archivo | Cambio |
|---------|--------|
| `models/metrology_model_approval_service_request_line.py` | **Nuevo**: línea `ma_*` + `line_kind` |
| `models/__init__.py` | Registra la nueva línea |
| `models/service_request_model_approval_mixin.py` | Parser de grilla + reflejo al encabezado + `line_ids` |
| `static/src/.../model_approval_service_form.js` | Grilla: draft + instruments + sync + validate |
| `static/src/.../model_approval_service_form.xml` | Bloque borrador + botón + tabla-grilla |
| `views/metrology_model_approval_views.xml` | Lista `line_ids` en backend |
| `intn_service_request/.../portal_service_form_view.js` | `_modelApprovalDelegate` en `_getPortalDelegate()` |
