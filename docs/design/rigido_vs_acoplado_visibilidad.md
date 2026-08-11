# Rígido vs. acoplado: visibilidad en registro de vehículo y en solicitud de servicio

> Estado: **análisis** (2026-07-27), verificado contra la rama `18.0` y contra el portal corriendo en `intn_demo`.
> **Revisión 2026-07-27 (misma fecha):** confirmado con negocio que **un rígido puede enganchar un acoplado si lo necesita**, y que el alta debe resolverse con un toggle explícito rígido / no-rígido. Los puntos afectados están marcados «Revisado 2026-07-27»; el resumen del delta está en §8.
> Capturas del estado actual: `docs/design/_images/rigid_vs_trailer/`.
> Complementa —no reemplaza— a [`tanker_type_refactor.md`](tanker_type_refactor.md): aquel define el modelo de datos (`tanker_type`), éste define **qué se muestra y qué se exige** en las dos pantallas del portal.

---

## 1. El problema, en una frase

El sistema modela **"camión con tanque"** creando *siempre* un segundo `fleet.vehicle` con `is_trailer=True`. Es decir: **el tanque propio de un rígido se guarda como si fuera un acoplado**. De ahí nacen los tres síntomas que se observan en producción.

| Concepto real | Cómo lo guarda hoy el sistema |
|---|---|
| Acoplado (vehículo **no motorizado**, chasis + tanque, chapa propia) | `fleet.vehicle` con `is_trailer=True` |
| Camión **rígido** (motorizado, tanque **incorporado**) | `fleet.vehicle` motorizado **+ un `is_trailer=True` fantasma** con los datos del tanque |
| Tractor / cabezal (motorizado, **sin** tanque, arrastra acoplado) | `fleet.vehicle` motorizado + acoplado real — indistinguible del caso anterior |

No existe ningún campo que distinga rígido de tractor. `is_trailer` sólo responde "¿es acoplado?", nunca "¿el motorizado lleva tanque propio?".

---

## 2. Síntomas verificados en el portal

### 2.1 El alta de vehículo obliga a cargar tanque, siempre

`/my/vehicle/new` muestra "Tractor Truck Data" y a continuación **"Tank Data *"** ya expandido y obligatorio, sin preguntar nada.

📷 `01-registro-vehiculo-actual-tank-obligatorio.jpg`, `02-registro-vehiculo-tank-data-obligatorio.jpg`

Causa: `portal_vehicle_app.js:966`

```js
// New vehicles must always register tank data alongside the
// truck; the panel is only collapsible when editing an
// existing (readonly) record.
include_tank: !this.props.recordId,
```

El botón colapsable "Add tank information" de `portal_tank_data_panel.js:20-29` es por lo tanto **código muerto en el alta**: sólo aparece al editar. Consecuencia: **es imposible registrar un tractor/cabezal sin tanque desde el portal**, y todo camión dado de alta genera un acoplado fantasma.

### 2.2 La solicitud de servicio exige acoplado, siempre

Tanto en "Flota: Verificación Anual" como en "Flota: Habilitación", el campo **Tráiler** aparece con asterisco de obligatorio.

📷 `03-sr-verificacion-anual-trailer-obligatorio.jpg`, `04-sr-habilitacion-trailer-obligatorio.jpg`

Al elegir un camión rígido real de la demo (`TN-001`, 15 000 L en su propio registro, sin acoplado), el formulario lo **bloquea**:

> «Debe registrar al menos un acoplado para este camion antes de continuar. Use el boton "Nuevo acoplado" si todavia no tiene uno cargado.»

📷 `05-sr-rigido-bloqueado-exige-acoplado.jpg`

En `intn_demo` esto afecta a **12 de 16 vehículos motorizados**: tienen litraje propio y ningún acoplado, y por lo tanto **ninguno puede pedir un servicio** sin inventarse un acoplado.

Causas:
- Servidor: `service_request_fleet_portal_create.py:57-58` → `if not trailer_id: return _("You must select a trailer.")`
- Cliente: `fleet_portal_widgets.xml:46` (`<span class="text-danger">*</span>`), `:53` (`required="true"`), y el aviso de `fleet_portal_widgets.js:463-465` / `:525-531`.

Nótese que el campo del modelo **ya es opcional**: `service_request_fleet_asset_mixin.py:47-53` define `trailer_id` sin `required`, y el create de `service_request_fleet_portal_create.py:132` ya acepta `False`. La obligatoriedad es **sólo** la validación del portal.

### 2.3 La capacidad se duplica

Al elegir `EURI3299` (tractor + acoplado `TR-TN-004` de 60 000 L), el formulario declara **120 000 L**.

📷 `06-sr-capacidad-duplicada-120000.jpg`

Cadena del error:

1. `service_request_portal_payload.py:48-54` — si el camión tiene acoplado, la `capacity` **del camión** en el payload se **sobrescribe** con la del acoplado.
2. `fleet_portal_widgets.js:612-632` (`_syncTotalCapacity`) — suma `capacidad del camión + capacidad del acoplado` → 60 000 + 60 000.

El mismo patrón existe del lado servidor: `service_request_fleet_asset_mixin.py:137-144` suma `vehicle_id.capacity + trailer_id.capacity`, y para compensar el alta escribe la capacidad del tanque **también** en el camión (`portal.py:1282-1292` y `cistern_service_request_mixin.py:835-839`, ambos con comentario explícito). Con el modelo actual (tanque = acoplado fantasma) esa compensación **garantiza** el doble conteo en cuanto el motorizado tenga cualquier acoplado.

Impacto de negocio: `capacity` alimenta `verification_price_bracket` (`service_request_fleet_asset_mixin.py:99-122`) y el control de litraje diario. Un litraje inflado **cambia el precio del servicio**.

### 2.4 El modal "Nuevo Camión Tanque" repite el problema

📷 `07-modal-nuevo-camion-tanque-sr.jpg` — mismo formulario, "Tank Data *" obligatorio, sin pregunta de rigidez.

### 2.5 Hoy un rígido con acoplado es imposible

`_intn_max_trailers_per_truck()` (`fleet_vehicle.py:313-316`) devuelve **1** salvo que se active `intn_fleet_cistern.multi_trailer_enabled`, que viene apagado. Como el tanque propio del rígido se materializa como acoplado fantasma, **ocupa esa única plaza**: engancharle un acoplado real revienta con «This truck already has the maximum of 1 active trailer assignment(s)» (`fleet_vehicle.py:239-245`, y el mismo control en `fleet_vehicle_trailer.py:_check_overlapping_assignments`).

Al dejar de crear el fantasma (B10), la plaza queda libre y **rígido + acoplado funciona con la configuración por defecto**, sin tocar el ajuste multi-trailer. Éste sigue gobernando sólo el caso de *más de un* acoplado simultáneo.

### 2.6 El backoffice tampoco lo muestra

`views/fleet_vehicle_views.xml`:
- `:55` — `<field name="is_trailer" invisible="1"/>`: el discriminador **ni siquiera es visible ni editable** desde el formulario.
- `:59` — el grupo del motorizado se rotula **"Tractor Truck Data"** aunque sea un rígido.
- `:118` — `<group string="Tank Data" invisible="not is_trailer">`: los campos de tanque (`cistern_*`, `compartment_count`, `capacity`, `compartment_line_ids`) **existen en el motorizado pero están ocultos**. Un rígido no puede mostrar su propio tanque.

---

## 3. Modelo objetivo

Se adopta el discriminador ya decidido en `tanker_type_refactor.md` §3.1:

```python
tanker_type = fields.Selection(
    [
        ("rigid", "Rígido"),
        ("articulated", "Articulado (tractor)"),
        ("trailer", "Acoplado / Semirremolque"),
    ],
    string="Tipo de unidad",
    required=True,
    default="rigid",
    tracking=True,
)
```

con `is_trailer` degradado a `compute="_compute_is_trailer", store=True, readonly=True`.

**Regla de visibilidad que resuelve este caso** (revisada 2026-07-27: un rígido **puede** enganchar acoplado):

| `tanker_type` | Motorizado | Datos de tanque en el propio registro | Acoplado |
|---|---|---|---|
| `rigid` | sí | **sí, obligatorios** (fabricante, modelo, serie, año, compartimentos, litraje) | **opcional** |
| `articulated` | sí | **no** (ocultos) | **obligatorio** (≥1) |
| `trailer` | no | sí, obligatorios | no aplica |

Para el rígido, el tanque pasa a vivir **en el propio registro del camión** — *"si es rígido sabemos que va a tener un tanque incorporado con un litraje y la data"*. Se deja de crear el acoplado fantasma.

> **`tanker_type` responde una sola pregunta: ¿el motorizado lleva tanque propio?** No dice nada sobre acoplados. Enganchar o desenganchar un acoplado **nunca** reclasifica el vehículo. Esto reemplaza la "regla de oro" de `tanker_type_refactor.md` §3.1bis, que hacía que asignar un acoplado externo marcara el camión como `articulated`: con rígidos que arrastran acoplado, esa regla daría falsos positivos.

Campo derivado que simplifica todo lo demás:

```python
has_own_tank = fields.Boolean(
    compute="_compute_has_own_tank", store=True,
)

@api.depends("tanker_type")
def _compute_has_own_tank(self):
    for v in self:
        v.has_own_tank = v.tanker_type in ("rigid", "trailer")
```

Y el litraje total, hoy inexistente (`tanker_type_refactor.md` §3.3):

```python
total_capacity = fields.Integer(compute="_compute_total_capacity", store=True)
# rigid       -> capacity propio + sum(current_trailer_ids.capacity)
# articulated ->                   sum(current_trailer_ids.capacity)
# trailer     -> capacity propio
```

La clave anti-doble-conteo no es "no sumar", sino que **`capacity` propio y acoplados son ahora conjuntos disjuntos**: un `articulated` nunca tiene `capacity` propio (constraint B5) y un `rigid` nunca tiene un fantasma que replique el suyo. La suma pasa a ser siempre correcta, incluso en el caso rígido + acoplado.

> **`total_capacity` (del vehículo) ≠ `capacity` (de la solicitud).** El primero agrega *todos* los acoplados vinculados y sirve al backoffice (F22). El segundo describe **la unidad que se presenta a verificar**: el tanque propio más el acoplado elegido en esa solicitud. Con multi-acoplado apagado coinciden; con multi-acoplado encendido no, y manda el de la solicitud (ver §7.1-3).

### 3.4 Litraje de la solicitud (confirmado 2026-07-27)

Un rígido de 15 000 L que engancha un acoplado de 30 000 L es **una sola solicitud de 45 000 L**, no dos servicios.

Esto es exactamente lo que ya calcula el código existente:

```python
# service_request_fleet_asset_mixin.py:137-144  -- SIN CAMBIOS
record.capacity = (record.vehicle_id.capacity or 0) + (record.trailer_id.capacity or 0)
record.compartment_count = (
    (record.vehicle_id.compartment_count or 0)
    + (record.trailer_id.compartment_count or 0)
)
```

| Caso | vehicle.capacity | trailer.capacity | Resultado |
|---|---|---|---|
| Rígido solo | 15 000 | 0 | 15 000 ✓ |
| Rígido + acoplado | 15 000 | 30 000 | **45 000** ✓ |
| Tractor + acoplado | 0 (constraint B5) | 30 000 | 30 000 ✓ |

> **La fórmula nunca estuvo mal — los datos sí.** El doble conteo de §2.3 no lo produce esta suma, sino (a) el fantasma que replica el litraje del rígido en dos registros y (b) `_portal_serialize_vehicle_option` sobrescribiendo la `capacity` del camión con la del acoplado. Arreglado B10 y B19, esta suma queda correcta sola. Lo mismo aplica a `compartment_count`, que junto con `capacity` alimenta `verification_price_bracket`.

---

### 3.5 🆕 Evidencia: el modelo v12 ya era el modelo objetivo (2026-07-27)

La BD legacy `intn_v12` conserva las tablas propias del subsistema de cisternas — `camiones_cisterna`, `acoplados`, `dimensiones_tanque` — que **no** existen en el `fleet_vehicle` estándar (el `fleet_vehicle` de v12 es Odoo de fábrica, sin una sola columna custom).

`camiones_cisterna` (el **motorizado**):

| Columna v12 | Equivalente v18 | Qué prueba |
|---|---|---|
| `chasis` | `vin_sn` | chasis **del camión** |
| `matricula_camion` | `license_plate` | chapa del camión |
| `fabricante_cisterna` | `cistern_manufacturer_id` | **el tanque vive en el registro del camión** |
| `matricula_cisterna` | `cistern_plate` | idem |
| `year_fabricacion` | `manufacturing_year` | idem |
| `cantidad_compartimientos` / `capacidad` | `compartment_count` / `capacity` | idem |
| `acoplado_id` (Many2one, **nullable**) | `current_trailer_id` | el acoplado era **opcional**, no obligatorio |

`acoplados` tenía su propia identidad completa y separada: `chasis_acoplado`, `matricula_acoplado`, `fabricante_acoplado`, `marca_acoplado_id`, `cantidad_compartimientos`, `capacidad`.

> **v12 modelaba exactamente lo que se está pidiendo ahora**: tanque propio en el camión, acoplado como enlace opcional con identidad propia. El acoplado fantasma es una invención de la reescritura v18, no una herencia.

#### Distribución real de la flota (3 165 camiones en `intn_v12`)

| | con tanque propio | sin tanque propio |
|---|---|---|
| **sin acoplado** | **3 090** (97,6 %) → rígido puro | 3 (0,1 %) |
| **con acoplado** | **71** (2,2 %) → **rígido + acoplado** | **1** (0,03 %) → tractor puro |

Tres lecturas que ordenan todo el diseño:

1. **`rigid` es el caso normal, no un caso más.** El default del toggle (§5.1) y del campo debe ser `rigid`, y el ramal "no es rígido" es la excepción rara.
2. **"Rígido + acoplado" es real y frecuente en términos absolutos** (71 unidades), no una excepción de negocio — confirma la decisión de 2026-07-27 y refuerza §2.5: hoy esas 71 unidades **no se pueden registrar** en v18.
3. **`articulated` puro es prácticamente inexistente**: 1 registro en 3 165. Vale la pena preguntarse si es un dato incompleto más que un tractor real.

> El portal v18 hoy fuerza al **100 %** de los camiones a la forma "camión + acoplado fantasma", que describe correctamente a **1 de 3 165** vehículos de la flota real.

---

## 4. Cambios de backend

### 4.1 Modelo — `intn_fleet_cistern/models/fleet_vehicle.py`

| # | Cambio | Referencia |
|---|---|---|
| B1 | Añadir `tanker_type` (Selection, required, default `rigid`, tracking) | tras `:40` |
| B2 | `is_trailer` → computed store readonly derivado de `tanker_type` | `:40-45` |
| B3 | Añadir `has_own_tank` (computed store) | nuevo |
| B4 | Añadir `total_capacity` (computed store) según tabla §3 | nuevo |
| B5 | Constraint: `articulated` no puede tener `capacity`/`compartment_count` propios | nuevo |
| B6 | Constraint: `rigid` requiere datos de tanque completos | nuevo |
| B7 | `action_assign_trailer` queda **neutral** (no reclasifica) | `:153-230` |
| B8 | ~~El *caller* que asigna un acoplado externo marca el camión como `articulated`~~ **ELIMINADO** (2026-07-27): un rígido puede engancharse un acoplado, así que la asignación no es señal de tipo. `tanker_type` se fija **sólo** en el alta, desde la respuesta del usuario. Ningún *caller* lo toca. | — |

### 4.2 Alta desde el portal — `intn_fleet_cistern/controllers/portal.py`

| # | Cambio | Línea |
|---|---|---|
| B9 | `portal_vehicle_api_create`: leer `tanker_type` del POST en vez de derivar `include_tank`; validar contra los 3 valores | `:1191-1199` |
| B10 | **`rigid`: escribir los `cistern_*` / `compartment_*` / `capacity` en el propio camión** y *no* crear trailer | `:1282-1306` |
| B11 | `articulated`: no exigir ni aceptar datos de tanque | `:1251-1264` |
| B12 | Eliminar `vals["capacity"] = tank_vals.get("capacity")` — el parche que causa el doble conteo | `:1292` |
| B13 | `_portal_vehicle_api_validate_required(..., include_tank=)` → parametrizar por `tanker_type` | `:768-811` |
| B14 | `_portal_tank_trailer_vals_from_post` queda **sólo** para el alta de acoplado real | `:868-902` |
| B15 | Snapshot `_portal_vehicle_payload`: exponer `tanker_type`, `has_own_tank`, `total_capacity` | `:344-360` |

Mismo tratamiento en el gemelo del flujo de solicitud: `intn_portal_fleet_cistern/portal/_shared/controllers/cistern_service_request_mixin.py:764-845` (`_portal_build_and_create_truck`), incluido el borrado del parche de `:835-839`.

### 4.3 Acoplado opcional en la solicitud

| # | Cambio | Ubicación |
|---|---|---|
| B16 | Quitar `if not trailer_id: return _("You must select a trailer.")` | `service_request_fleet_portal_create.py:57-58` |
| B17 | Sustituir por validación condicional: exigir acoplado **sólo si** `vehicle.tanker_type == 'articulated'` | mismo archivo |
| B18 | **Revisado 2026-07-27: sin cambios.** La suma `vehicle.capacity + trailer.capacity` es correcta una vez limpios los datos (§3.4). Sólo agregar test de regresión para los tres casos de la tabla. | `service_request_fleet_asset_mixin.py:124-144` |
| B19 | `_portal_serialize_vehicle_option`: dejar de sobrescribir `capacity` con la del acoplado; enviar `total_capacity` + `tanker_type` | `service_request_portal_payload.py:48-54, 66-78` |
| B20 | `_portal_fleet_trucks_domain`: la vigencia del certificado de un rígido debe mirarse **en el propio camión**, no vía `current_trailer_id` | `cistern_service_request_mixin.py:52-58` |

### 4.3bis 🆕 El acoplado creado desde el modal no se vincula al camión

Hallazgo al validar la regla "registrado **o vinculado**" (2026-07-27).

En el flujo del modal la creación es **diferida**: `_portal_resolve_pending_fleet_vehicles` (`cistern_create_handlers.py:170-223`) crea camión y acoplado dentro de la misma transacción que la solicitud. Pero mirando `:209-220`:

```python
if new_truck_fields:
    vehicle, trailer = self._portal_build_and_create_truck(new_truck_fields, cp)
    kw["vehicle_id"] = str(vehicle.id)
    if trailer:                          # <- sólo el tanque fantasma queda vinculado
        kw["trailer_id"] = str(trailer.id)
if new_trailer_fields:
    trailer = self._portal_build_and_create_trailer(new_trailer_fields, cp)
    kw["trailer_id"] = str(trailer.id)   # <- se asigna a la SR, pero NO se vincula al camión
```

`_portal_build_and_create_trailer` (`cistern_service_request_mixin.py:847-888`) termina en un `Fleet.create(vals)` seco: **nunca llama a `action_assign_trailer`**. Sólo el tanque fantasma quedaba vinculado, y sólo porque `_portal_build_and_create_truck:844` sí lo hace.

Hoy el síntoma queda enmascarado porque todo camión nace con fantasma. Con la regla nueva se vuelve visible: un tractor creado con acoplado desde el modal quedaría con `current_trailer_id` vacío, y por lo tanto (a) `needsTrailerSelection` volvería a dispararse en la siguiente solicitud, y (b) `total_capacity` del articulado daría **0**.

Compárese con la ruta suelta `/my/vehicle/api/create`, que **sí** vincula (`portal.py:1307-1322`), porque su formulario de acoplado tiene campo `truck_id` (`vehicle_form_contract.js:39-50`).

| # | Cambio | Ubicación |
|---|---|---|
| B24 | Vincular el acoplado recién creado al camión de la solicitud (`action_assign_trailer`) | `cistern_create_handlers.py:216-220` |
| B25 | Vincular también el acoplado **existente** elegido en el selector, si no está vinculado a ningún camión | mismo |
| B26 | Validar en el submit: si `vehicle.tanker_type == 'articulated'`, exigir acoplado vinculado. Es la contraparte servidor de F10 | `service_request_fleet_portal_create.py:57-58` (reemplaza B16/B17) |

Reglas para B25, para no pisar administración de flota:

| Estado del acoplado elegido | Acción |
|---|---|
| Ya vinculado al camión seleccionado | nada |
| Sin vincular a ningún camión | vincular al camión seleccionado |
| Vinculado a **otro** camión | rechazar — ya lo impide `filteredTrailers` (`fleet_portal_widgets.js:686-697`) y la reasignación es tarea de flota, no del portal |

> ⚠️ **B20 no es cosmético.** Hoy `_portal_fleet_trucks_domain` acepta un camión si el certificado está en su acoplado. Un rígido sin acoplado fantasma quedaría fuera del combo y el cliente vería «Ninguno de los camiones de su empresa cuenta con una Verificación Inicial vigente». Debe migrarse junto con B10.

### 4.3ter 🆕 Identidad del tanque: qué certifica un rígido (2026-07-27)

**Pregunta:** para un rígido, ¿la verificación certifica el chasis o el tanque?
**Respuesta de negocio:** el **chasis es del acoplado**. El tanque de un rígido no tiene chasis: tiene **código de tanque** (placa de fábrica del fabricante, con Nº de serie propio) — coherente con §2 de `tanker_type_refactor.md`, donde la placa de fábrica del tanque y la chapa de circulación son dos elementos físicos distintos.

#### El certificado ya cuelga del chasis, pero imprime el tanque en blanco

`certificate.management.vehicle_id` apunta al **vehículo motorizado**, no al acoplado — verificado en `intn_demo`: los 3 certificados existentes apuntan a registros `is_trailer=false`. Se crea así en `fleet_vehicle_inspection.py:249` y `fleet_vehicle_log_services.py:160`.

Pero el certificado de verificación imprime la identidad del tanque leyendo del **mismo registro**:

```xml
<!-- certificate_verification_report.xml -->
:240  <span t-field="s.vehicle_id.cistern_manufacturer_id"/>
:246  <span t-field="s.vehicle_id.cistern_plate"/>   <!-- label: "Trailer plate" -->
```

Para una unidad articulada esos campos están **vacíos en el camión** (el tanque vive en el acoplado). Comprobado en `intn_demo`: `DEMO-BFE426` y `DEMO-CEG127` tienen certificado, `capacity = 0`, `cistern_manufacturer_id` NULL y `cistern_plate` vacío — **el certificado legal sale con el fabricante y la matrícula del tanque en blanco**.

> Es el mismo patrón ya detectado en `tanker_type_refactor.md` §5.8 para `tank_cistern_plate`: el dato existe, pero se lee del registro equivocado.

#### Estado real de los campos de identidad del tanque

Conteo sobre los 45 `fleet.vehicle` de `intn_demo`:

| Dato regulatorio (§2 doc previo) | Campo existente | ¿Existe? | Poblado |
|---|---|---|---|
| Fabricante del tanque | `cistern_manufacturer_id` | ✅ | 15/45 |
| Modelo del tanque | `cistern_model_id` | ✅ | **0/45** |
| **Código / Nº de serie del tanque** | `cistern_vin_sn` | ✅ (mal nombrado) | **0/45** |
| Año de fabricación del tanque | `manufacturing_year` | ✅ | parcial |
| Capacidad nominal | `capacity` | ✅ | sí |
| Compartimentos y su litraje | `compartment_count`, `compartment_line_ids` | ✅ | sí |
| Chapa de circulación del portador | `license_plate` | ✅ | sí |
| Matrícula de cisterna (legacy) | `cistern_plate` | ✅ | parcial — el doc previo propone **retirarlo** |
| Dimensiones del tanque | `tank.dimension` (por certificado) | ✅ | según certificado |
| Presión de prueba | `fleet.vehicle.log.services.test_pressure` | ✅ pero en el **ensayo**, no en el maestro | según ensayo |
| Material del tanque | — | ❌ **no existe** | — |

**Conclusión: no hacen falta campos nuevos para la identidad del tanque.** Todo está modelado. Lo que falta es (a) que se pueble y (b) que se lea del registro correcto. Las dos excepciones son *material del tanque* y *presión de prueba* (existe, pero como dato del ensayo hidrostático, no del maestro) — ambas son decisión de negocio, no bloqueo.

#### Material del tanque: no existe en ningún lado (verificado 2026-07-27)

Rastreado en las tres fuentes posibles, sin resultado:

| Fuente | Resultado |
|---|---|
| **Relevamiento** (`docs/project/relevamiento/`, incl. `ONM/UMLE/Cisternas/Form-01..06` y `Puntos-Faltantes-en-General`) | **0 menciones** de material de tanque. Todos los aciertos de "material" son ajenos: compras, inspección eléctrica DSE, dpto. de Materiales de Construcción de ONI, norma de extintores de ONC. |
| **BD legacy `intn_v12`** | Ni `camiones_cisterna`, ni `acoplados`, ni `dimensiones_tanque` (`id, medicion_id, name, milimetros`) tienen columna de material. **Nunca se registró.** |
| **Código v18** | Sin campo. |

**¿Lo registra ATC?** No, y el relevamiento no lo sugiere. **ATC = Atención al Cliente** (`minutas/2026-01-12.md:123`), y su alcance documentado es crear expedientes y contactos; sus pedidos son cantidad de muestras, datos de contacto y estado de pago (`minutas/2026-01-21.md:137`, `ONI/ANALISIS-DE-ORGANISMOS---ONI.md`) — **nada técnico del vehículo ni del tanque**. Los datos del tanque entran por dos vías, ninguna de ellas ATC:

1. **El cliente**, desde el portal. `Form-01 - Habilitación Camión Cisterna` es explícito: *"Solamente en este formulario se habilitan los botones de NUEVO CAMIÓN y NUEVO ACOPLADO"*.
2. **El técnico de ONM/UMLE**, durante la verificación (dimensiones, presión de prueba, mediciones).

> **Conclusión:** el material del tanque sería un campo **genuinamente nuevo**, sin dato histórico que migrar y sin dueño definido. Si se decide incorporarlo, la pregunta previa no es dónde guardarlo (iría junto a `cistern_manufacturer_id`) sino **quién lo carga**: si es dato declarado por el cliente va al formulario del portal; si es dato constatado, va al registro de verificación. **Recomendación: dejarlo fuera de este refactor** — no bloquea nada y hoy nadie lo pide.



#### `cistern_vin_sn` es el "código de tanque", pero está mal nombrado y mal ruteado

- **Mal nombrado:** su label es `"Cistern Chassis (VIN)"` (`fleet_vehicle.py:485-489`). Para un rígido eso es incorrecto: el tanque no tiene VIN. Esto **refuerza** el rename ya propuesto en `tanker_type_refactor.md` §6-paso 3 (`cistern_vin_sn` → `tank_serial_no`); con la definición de negocio de hoy, el nombre correcto es *código / Nº de serie de tanque*.
- **Mal ruteado:** el portal OWL lo captura (`portal_tank_data_panel.js:70-78`) pero lo escribe en el **`vin_sn` del acoplado fantasma** (`portal.py:878-880`), dejando `cistern_vin_sn` vacío — de ahí el 0/45. Y `service_request_assigned_data_vehicle.py:113` lee justamente `trailer_id.cistern_vin_sn`, o sea **siempre vacío**. Mismo bug que `tank_cistern_plate`.
- **Nunca se imprime:** ningún reporte lo usa. Se captura, se valida por unicidad y se muestra en el backoffice, pero no llega a ningún certificado.

| # | Cambio | Ubicación |
|---|---|---|
| B27 | Renombrar `cistern_vin_sn` → `tank_serial_no`, label "Código de tanque (Nº de serie)" | `fleet_vehicle.py:485`, + migración `tanker_type_refactor.md` §6-3 |
| B28 | En `rigid`, escribir el código de tanque en el **propio camión** (parte de B10); en `trailer`, en el propio acoplado | `portal.py:1282-1306` |
| B29 | Reportes: leer la identidad del tanque del **portador**, no de `vehicle_id` a secas. Ya existe el patrón `trailer_id or vehicle_id` en `fleet_vehicle_service_request.py:87` | `certificate_verification_report.xml:240,246` + los otros 3 de `tanker_type_refactor.md` §5.4 |
| B30 | `tank_vin_sn` histórico: leer del portador en vez de `trailer_id.cistern_vin_sn` | `service_request_assigned_data_vehicle.py:113` |

> **B29 es independiente de todo este refactor y arregla un certificado legal que hoy sale incompleto.** Puede adelantarse.

---

### 4.4 Datos históricos (bugfix arrastrado)

`service_request_assigned_data_vehicle.py:103-117` copia los `tank_*` desde `trailer_id.*`. Para un rígido sin acoplado quedarían todos vacíos. Debe leer del **portador del tanque**:

```python
tank_holder = record.trailer_id or record.vehicle_id   # ya existe este patrón en
                                                       # fleet_vehicle_service_request.py:87
```

### 4.5 Migración

Sobre lo ya previsto en `tanker_type_refactor.md` §6, se suma un paso propio de este caso:

**Colapsar los acoplados fantasma.** Para cada motorizado con un `is_trailer=True` enlazado que sea un fantasma creado por `include_tank`:
1. copiar `cistern_*` / `compartment_*` / `capacity` del fantasma al motorizado;
2. marcar el motorizado como `rigid`;
3. re-apuntar `service.request.trailer_id`, certificados, precintos e inspecciones que referencien al fantasma;
4. archivar el fantasma (no borrar — hay historial legal enganchado).

Heurística para detectar el fantasma vs. un acoplado real: fue creado en la misma transacción que el camión y su `truck_code` coincide. **Todo lo dudoso va a log de revisión manual**, nunca se adivina (Decisión 2 del doc previo).

**Backfill de `tanker_type`** (revisado 2026-07-27). La señal ya no puede ser "¿tiene acoplado?", porque un rígido puede tenerlo:

| Situación del motorizado | `tanker_type` |
|---|---|
| Tiene fantasma (mismo `truck_code`, misma transacción) | `rigid` + colapsar (pasos 1-4) |
| Sin fantasma, pero con `capacity`/`compartment_count` propios | `rigid` (los 12 casos de `intn_demo` caen acá) |
| Sin tanque propio y con ≥1 acoplado real | `articulated` |
| Sin tanque propio y sin acoplado | log de revisión manual |

Contrastado contra la flota real de `intn_v12` (§3.5), el reparto esperado es **~97,6 % `rigid` puro, ~2,2 % `rigid` + acoplado, ~0,03 % `articulated`**, y sólo **4 registros de 3 165** caerían en revisión manual. Si el backfill produce una proporción muy distinta a ésa, la heurística está mal y hay que frenar antes de seguir.

> **Esta revisión simplifica la migración.** `tanker_type_refactor.md` §3.1bis marcaba "un rígido con tanque propio que además engancha un acoplado real" como **excepción de negocio a revisión manual**. Ahora es un estado legal y frecuente: **esa cola de revisión desaparece**. A cambio, "sin tanque propio y sin acoplado" pasa a ser el único caso ambiguo, y es raro.

---

## 5. Cambios de frontend

### 5.1 Selector de tipo en el alta de vehículo

Nuevo control al tope de `FleetVehicleForm` (`portal_vehicle_app.js:623+`), antes de los datos del vehículo. **Toggle de dos botones con icono**, no un `<select>`: es una decisión binaria que reconfigura el resto del formulario, y conviene que se vea como tal.

```
¿El vehículo es rígido? *
┌─────────────────────────────┐  ┌─────────────────────────────┐
│  [🚛]  Sí, es rígido        │  │  [🚚]  No, es tractor       │
│  Tanque montado sobre el    │  │  Sin tanque propio;         │
│  propio chasis              │  │  arrastra acoplado(s)       │
└─────────────────────────────┘  └─────────────────────────────┘
```

- **Sí** → se despliega el panel "Datos del tanque" con todos sus campos **obligatorios** (es el comportamiento actual, pero ahora explicado por una elección del usuario).
- **No** → el panel de tanque **se oculta por completo** y aparece un aviso:

  > ⚠️ Este vehículo no tiene tanque propio. Para poder solicitar servicios deberás registrar al menos un acoplado y vincularlo a este camión.
  > \[ Registrar acoplado ahora \]

- Sin elegir → ambos paneles ocultos y el botón Guardar deshabilitado. Nada de default silencioso: hoy el default implícito (`include_tank: true`) es justamente lo que produce los fantasmas.

Iconografía: reusar `IntnIcon` (ya importado en `portal_tank_data_panel.js:5`), con los nombres `truck` / `car-front` que ya se usan en `portal_vehicle_app.js:1631` para distinguir acoplado de camión.

> El alta de **acoplado** tiene su propio formulario (`FleetTrailerForm`), así que este toggle sólo ofrece las dos variantes de motorizado. `tanker_type='trailer'` nunca sale de aquí.

**Sobre el aviso y el botón "Registrar acoplado ahora":** el comportamiento difiere según dónde esté montado el formulario, y esto conviene decidirlo antes de implementar (ver §7.1):

**RESUELTO 2026-07-27:**

| Contexto | Comportamiento |
|---|---|
| `/my/vehicle/new` (alta suelta) | Aviso **informativo**; el guardado procede. El camión queda creado sin acoplado y el botón redirige al alta de acoplado con el camión preseleccionado. Permite cargar la flota en dos pasos. |
| Modal "Nuevo Camión Tanque" dentro de la solicitud | Si es `articulated`, la solicitud **no avanza** hasta que el vehículo tenga al menos un acoplado **registrado o vinculado**. El bloqueo vive en el selector de tráiler de la solicitud (`needsTrailerSelection`, F10), no en el guardado del camión. |

> Nótese la asimetría deliberada: el **alta** de un tractor sin acoplado es un estado válido y persistente del maestro de flota; lo que no es válido es **solicitar un servicio** para un tractor que no tiene nada que verificar.

| # | Cambio | Archivo |
|---|---|---|
| F1 | Añadir `tanker_type` al `useState` **sin default** (`""`); **eliminar** `include_tank: !this.props.recordId` | `portal_vehicle_app.js:946-978` |
| F2 | Renderizar el toggle de dos botones con icono | `portal_vehicle_app.js:623-747` y `:770-915` (las dos variantes de template) |
| F2b | 🆕 Aviso condicional "necesitás registrar un acoplado" cuando `tanker_type === 'articulated'`, con botón de acción según contexto | mismo |
| F2c | 🆕 Deshabilitar Guardar mientras `tanker_type` esté vacío | `onSubmit`, `:1228+` |
| F3 | `canEditTank` → `state.tanker_type === 'rigid'` | `portal_vehicle_app.js:1228-1236` |
| F4 | Rotular el grupo según tipo: "Datos del camión rígido" / "Datos del tractor" en vez de "Tractor Truck Data" fijo | `lblTractorTruckData`, `:929` |
| F5 | `PortalTankDataPanel`: quitar el botón colapsable «Add tank information» (código muerto); el panel se muestra u oculta por tipo | `portal_tank_data_panel.js:20-29, 191-193` |
| F6 | `vehicleFormPayload`: emitir `tanker_type`; enviar `TANK_FORM_FIELDS` sólo si `rigid` | `vehicle_form_contract.js:134-176` |
| F7 | `validateVehicleForm`: exigir tanque sólo en `rigid`; en `articulated` prohibirlo | `vehicle_form_contract.js:233-266` |

### 5.2 Acoplado opcional en la solicitud

| # | Cambio | Archivo |
|---|---|---|
| F8 | Quitar el `*` del label y `required="true"` del selector de tráiler; marcarlo `*` **dinámicamente** sólo si el camión elegido es `articulated` | `fleet_portal_widgets.xml:46, 53` |
| F9 | **Revisado 2026-07-27:** el bloque de acoplado queda **siempre visible** (un rígido puede engancharlo). Sólo cambia si es obligatorio u opcional. Más simple que la ocultación condicional que planteaba la versión anterior. | `fleet_portal_widgets.xml:44-62` |
| F10 | `needsTrailerSelection` → sólo `true` si `articulated` y sin acoplado | `fleet_portal_widgets.js:463-465` |
| F11 | Reescribir `needsTrailerMessage` para que hable de tractores, no de "camiones" en general | `fleet_portal_widgets.js:525-531` |
| F12 | **Revisado 2026-07-27:** "Nuevo acoplado" queda **siempre visible** (misma razón que F9). Sin cambio respecto del código actual. | `fleet_portal_widgets.xml:70-75` |
| F13 | **Revisado 2026-07-27: sin cambios.** `vehicleCapacity + trailerCapacity` queda correcto en cuanto B19 deje de sobrescribir la `capacity` del camión con la del acoplado. | `fleet_portal_widgets.js:612-632` |
| F14 | Idem F13: sin cambios en la fórmula; verificar que el snapshot no reintroduzca la capacidad del acoplado en el campo del camión | `fleet_portal_widgets.js:104, 158` |
| F15 | Modal "Nuevo Camión Tanque": hereda F1-F7 (reusa `FleetVehicleForm` en modo `service_request_enabling`) | automático |
| F16 | Mostrar el tipo junto al nombre en el combo de camión (p. ej. `Ford/Focus/TN-001 · Rígido`) | `fleet_portal_widgets.js:718-727` |

### 5.3 Backoffice — `views/fleet_vehicle_views.xml`

| # | Cambio | Línea |
|---|---|---|
| F17 | Reemplazar `<field name="is_trailer" invisible="1"/>` por `tanker_type` visible y editable (widget `radio`) | `:55` |
| F18 | Rótulo del grupo del motorizado dependiente del tipo | `:59` |
| F19 | `<group string="Tank Data" invisible="not is_trailer">` → `invisible="not has_own_tank"` — **el cambio que hace visible el tanque del rígido** | `:118` |
| F20 | Grupo "Tanques Actuales" → `invisible="tanker_type != 'articulated'"` | `:73` |
| F21 | Página "Trailer History" → sólo para `articulated` | `:149` |
| F22 | Mostrar `total_capacity` (readonly) junto a `capacity` | `:128` |
| F23 | Añadir `tanker_type` a filtros/agrupaciones de la vista lista y search | mismo archivo |

---

## 6. Plan de implementación

Seis fases, cada una **entregable por separado** (rama + PR propio). El criterio de corte es que ninguna deje el sistema en un estado peor que el actual si se detiene ahí.

Notación: 🔴 alto riesgo (toca datos o comportamiento de cliente) · 🟡 medio · 🟢 bajo.

---

### Fase 0 — Arreglos independientes 🟢

**No dependen del refactor. Se pueden mergear ya.**

| Ítem | Qué |
|---|---|
| B29 | Centralizar la resolución del portador del tanque en un helper `_intn_tank_holder()` y usarlo en los 4 reportes (`tanker_type_refactor.md` §5.4). Regla pre-refactor: `trailer_id or vehicle_id`. |
| B30, §4.4 | `tank_*` históricos (`service_request_assigned_data_vehicle.py:103-117`) leen del portador vía el mismo helper. |
| B24 | Vincular con `action_assign_trailer` el acoplado creado desde el modal (`cistern_create_handlers.py:216-220`). |

**Por qué primero:** B29 arregla un **certificado legal que hoy sale con fabricante y matrícula del tanque en blanco** (§4.3ter, verificado en `intn_demo`). No hay razón para que eso espere al refactor.

**El helper es la pieza clave del plan.** Se introduce acá con la regla simple y se refina una sola línea en la Fase 4. Sin él, la corrección queda esparcida en 4 reportes + 7 campos históricos y hay que tocarlos dos veces.

✅ **Aceptación:** el certificado de verificación de `DEMO-BFE426` imprime fabricante y matrícula del tanque; `tank_cistern_plate` y `tank_vin_sn` dejan de venir vacíos en solicitudes nuevas.

---

### Fase 1 — Modelo, sin cambio de comportamiento 🟡

| Ítem | Qué |
|---|---|
| B1 | `tanker_type` (Selection, `default='rigid'`, tracking). **Sin `required`** todavía. |
| B2 | `is_trailer` → computed `store=True, readonly=True` |
| B3, B4 | `has_own_tank`, `total_capacity` |
| B27 | `cistern_vin_sn` → `tank_serial_no`, label "Código de tanque (Nº de serie)" (§4.3ter) |
| B7 | `action_assign_trailer` neutral: no toca `tanker_type` |
| B5, B6 | Constraints **escritas pero desactivadas** (feature flag o comentadas) |
| §4.5 | Backfill de `tanker_type` + rename de columna en pre-migrate |

**Todavía no se colapsan fantasmas.** Esta fase sólo *clasifica*. El portal sigue creando fantasmas y todo sigue funcionando igual.

**Las constraints van desactivadas a propósito:** "un `articulated` no tiene `capacity` propio" es falso para los datos actuales hasta que la Fase 3 los limpie. Activarlas antes rompe el guardado en backoffice.

✅ **Aceptación:** el backfill sobre copia de producción da **~97,6 % `rigid` / ~2,2 % `rigid`+acoplado / ~0,03 % `articulated`** y **≤ 5 registros** en revisión manual (§3.5). **Si la proporción se aleja de eso, frenar** — la heurística está mal.

---

### Fase 2 — Backoffice 🟢

F17-F23. `tanker_type` visible y editable, "Tank Data" por `has_own_tank`, `total_capacity`, filtros.

**Por qué antes que el portal:** le da a ONM la herramienta para **revisar y corregir la clasificación** del backfill sobre datos reales antes de que nada dependa de ella. Es la red de seguridad de la Fase 1.

✅ **Aceptación:** un rígido muestra su tanque en el formulario (hoy imposible, §2.6); ONM puede reclasificar los ~4 registros del log de revisión.

---

### Fase 3 — Alta de vehículo + colapso de fantasmas 🔴

**La fase pesada. Todo junto en un solo release.**

| Ítem | Qué |
|---|---|
| B9-B15, B28 | Alta desde el portal: `rigid` escribe el tanque en el propio camión; **se deja de crear el fantasma** |
| B12 | Borrar el parche `vals["capacity"] = tank_vals.get("capacity")` (`portal.py:1292`, `cistern_service_request_mixin.py:839`) |
| **B20** | `_portal_fleet_trucks_domain`: certificado del rígido se busca **en el propio camión** |
| F1-F7, F2b, F2c | Toggle rígido / no-rígido, panel de tanque condicional, aviso |
| §4.5 pasos 1-4 | Colapsar fantasmas: copiar datos al camión, re-apuntar SR/certificados/precintos/inspecciones, archivar |

🔴 **B10 y B20 son inseparables.** Si el rígido deja de tener fantasma pero el dominio sigue buscando el certificado vía `current_trailer_id`, **todos los rígidos desaparecen del combo** de la solicitud con el mensaje engañoso «Ninguno de los camiones de su empresa cuenta con una Verificación Inicial vigente». Mismo PR, sin excepción.

🔴 **El colapso va en este release, no antes.** Si se colapsa en la Fase 1, el portal sigue creando fantasmas nuevos durante todo el intervalo y hace falta una segunda pasada.

**Orden interno sugerido:** B20 primero (es compatible con los datos viejos: buscar el certificado en el camión *o* en su acoplado), después el resto.

✅ **Aceptación:** alta de rígido no crea segundo `fleet.vehicle`; alta de tractor muestra el aviso y guarda igual; los 71 casos "rígido + acoplado" de v12 son registrables (§2.5); cero fantasmas nuevos; ningún camión sale del combo de la solicitud.

---

### Fase 4 — Solicitud de servicio 🔴

| Ítem | Qué |
|---|---|
| B16, B17, B26 | Acoplado obligatorio **sólo** si `articulated` |
| B25 | Vincular el acoplado existente elegido, si está libre (matriz de §4.3bis) |
| B19 | `_portal_serialize_vehicle_option` deja de sobrescribir la `capacity` del camión con la del acoplado |
| F8-F12, F15, F16 | Asterisco dinámico, `needsTrailerSelection`, mensaje, tipo en el combo |
| B29 (refinar) | `_intn_tank_holder()` pasa de `trailer_id or vehicle_id` a `has_own_tank ? self : current_trailer_id` |

🔴 **B19 es el que cierra el doble conteo.** Con B12 (Fase 3) ya hecho, B19 es la última pieza: recién ahí `capacity` deja de inflarse.

⚠️ **El refinamiento del helper va acá, no antes.** Con rígidos que arrastran acoplado (71 unidades), `trailer_id or vehicle_id` devolvería el acoplado y no el tanque propio del rígido. Sólo es seguro una vez que `has_own_tank` refleja datos ya colapsados.

✅ **Aceptación:** `TN-001` (rígido sin acoplado) crea solicitud sin pedir acoplado — los 12 casos de `intn_demo` desbloqueados; `EURI3299` declara **60 000 L, no 120 000** (§2.3); rígido 15 000 + acoplado 30 000 declara **45 000** (§3.4).

---

### Fase 5 — Cierre 🟡

- Activar B5 y B6 (los datos ya están limpios).
- `tanker_type` pasa a `required=True`.
- Verificar que no queden escrituras vivas de `is_trailer`:
  `grep -rn '"is_trailer":\|is_trailer\s*=' custom_addons/`
- Demo (`fleet_vehicle_trailer_demo.xml`, `fleet_portal_users_demo.xml`) migrada a `tanker_type`.
- Retirar o migrar la ruta HTTP legacy `portal_create_vehicle` (`portal.py:1805`), único sitio que aún escribe `cistern_plate` en el camión.

✅ **Aceptación:** ningún registro con `tanker_type` NULL; constraints activas sin romper el guardado.

---

### Fase 6 — Validación

Ejecutable: **`scripts/verify/tanker_type_acceptance.py`** (24 verificaciones, hace
`rollback` al final). Correr con:

```bash
.venv/bin/python src/odoo/odoo-bin shell -d <db> -c odoo.conf.local --no-http \
  < scripts/verify/tanker_type_acceptance.py
```

Cubre modelo y litraje, campos derivados, resolución del portador del tanque,
reglas de acoplado en la solicitud, **los cuatro caminos de alta** (rígido,
tractor, acoplado y los dos contratos legacy), las rutas del portal, el render
del alta y el i18n del portal.

> **Por qué incluye chequeos del render y de las rutas.** La primera versión del
> checklist daba 11/11 mientras `/my/trailer/new` mostraba el formulario de
> camión: sólo miraba el modelo y la solicitud, ningún camino de alta. El
> chequeo "el alta pasa `is_trailer` a los valores de render" se validó
> reintroduciendo la regresión a propósito — falla 23/24 — antes de darlo por
> bueno.

Complementan, fuera del script:

- [ ] Los 4 reportes imprimen la identidad del tanque para rígido y para articulado.
- [ ] Conteo de `fleet.vehicle` post-migración = previo − fantasmas colapsados, y ninguno borrado (sólo archivado).
- [ ] Checklist en §8 de `tanker_type_refactor.md`.

---

### Dependencias

```
Fase 0 ─────────────────────────────────────► (independiente)

Fase 1 ──► Fase 2 ──► Fase 3 ──► Fase 4 ──► Fase 5 ──► Fase 6
           (revisión   (B10+B20   (B19 cierra
            humana)     juntos)    el doble conteo)
```

### Sobre tests

La política vigente (`AGENTS.md`, 2026-07-17) es **no agregar tests nuevos** salvo pedido explícito. Este plan la respeta: los criterios de aceptación de arriba están redactados para verificarse por `odoo shell` o navegando el portal.

**Recomendación:** hacer una excepción para **la Fase 1**. Un backfill sobre 3 165 vehículos con historial legal enganchado (certificados, precintos, inspecciones) es el tipo de cambio donde un test de migración cuesta mucho menos que el rollback. Decisión del equipo.

---

## 7. Puntos a confirmar con negocio

- ~~**¿Un rígido puede además enganchar un acoplado?**~~ **RESUELTO (2026-07-27): sí, si lo necesita.** `tanker_type` deja de ser "¿arrastra acoplado?" y pasa a ser exclusivamente "¿tiene tanque propio?". Consecuencias aplicadas: B8 eliminado, F9/F12 sin ocultación condicional, tabla §3 y `total_capacity` revisados, backfill §4.5 reformulado.

- ~~**¿La verificación de un rígido certifica el chasis o el tanque?**~~ **RESUELTO (2026-07-27):** el chasis es del acoplado; el tanque del rígido se identifica por **código de tanque**. El certificado ya cuelga del motorizado, así que la estructura es correcta — lo que falla es de dónde se leen los datos del tanque. **No hacen falta campos nuevos.** Detalle e inventario en §4.3ter (B27-B30).
- ~~**¿Rígido con acoplado: se verifican por separado?**~~ **RESUELTO (2026-07-27): una sola solicitud, con el litraje sumado** (15 000 + 30 000 = 45 000). Consecuencia: B18 y F13 pasan a "sin cambios" — la fórmula existente ya es ésa. Detalle en §3.4.
- ~~**¿El aviso de "registrá un acoplado" bloquea el guardado del tractor?**~~ **RESUELTO (2026-07-27):** no en `/my/vehicle/new` (se guarda, aviso informativo); sí en el modal de la solicitud, donde un `articulated` necesita acoplado registrado o vinculado antes de continuar. Detalle en §5.1; hueco de implementación que destapó, en §4.3bis (B24-B26).

### 7.1 Abiertos

1. **¿Se incorpora el material del tanque?** Campo nuevo, sin dato histórico y sin dueño (§4.3ter). Si se acepta, definir primero **quién lo carga**: cliente en el portal o técnico en la verificación. Recomendación: fuera de alcance.
2. **Litraje del articulado con multi-acoplado**: ¿`total_capacity` suma todos los acoplados enganchados o sólo el de la solicitud? Hoy `_syncTotalCapacity` usa el seleccionado; `current_trailer_ids` admite varios.
3. **¿Se habilita `multi_trailer_enabled`?** Con el fantasma eliminado, el default de 1 acoplado alcanza para "rígido + acoplado" y para "tractor + acoplado". Sólo hace falta activarlo si una unidad arrastra **dos o más** acoplados a la vez.
4. **Los 12 rígidos de demo/producción sin acoplado**: la tabla de backfill §4.5 los clasifica como `rigid` por tener litraje propio. ¿Se acepta esa inferencia o hay que auditarlos uno a uno?

---

## 8. Delta de la revisión 2026-07-27

Cuánto cambia "el rígido puede enganchar acoplado" + toggle explícito, respecto de la primera redacción de este doc.

**Sin cambios (el grueso).** El diagnóstico completo (§2) y los tres bugs de raíz siguen idénticos. El discriminador `tanker_type`, `is_trailer` computado y `has_own_tank` no se tocan. De los 46 ítems originales, **38 quedan igual**: B1-B7, B9-B23, F1, F3-F8, F10-F11, F15-F23. El total pasa a 52 (−1 eliminado, +7 nuevos: B24-B30).

**Cambia (12 ítems):**

| Ítem | Antes | Ahora | Efecto |
|---|---|---|---|
| B8 | El *caller* marca `articulated` al asignar acoplado externo | **Eliminado** | −1 ítem, y desaparece la regla más frágil del diseño |
| §3 tabla | `rigid` → acoplado "no aplica" | `rigid` → acoplado **opcional** | neutro |
| §3 `total_capacity` | `rigid` = capacity propio | `rigid` = propio + Σ acoplados | neutro |
| F9 | Ocultar bloque de acoplado si `rigid` | Siempre visible; sólo cambia obligatoriedad | **−trabajo** |
| F12 | Ocultar "Nuevo acoplado" si `rigid` | Sin cambio respecto del código actual | **−trabajo** |
| F2 | Radio de 3 opciones | Toggle de 2 botones con icono | ≈ igual |
| F2b, F2c | — | Aviso condicional + Guardar deshabilitado sin elección | **+trabajo** (chico) |
| §4.5 backfill | `current_trailer_ids` no vacío ⇒ candidato `articulated` | Señal = ¿tiene tanque propio? | neutro |
| B18, F13, F14 | Reemplazar la suma por `total_capacity` | **Sin cambios**: la suma existente ya da 45 000 (§3.4) | **−trabajo** (−3 ítems) |
| B24-B26 | — | Vincular el acoplado creado/elegido desde el modal + validación servidor | **+trabajo** (hallazgo, §4.3bis) |
| B27-B30 | `cistern_vin_sn` → `tank_serial_no` (rename suelto) | Es el **código de tanque**; + rutear identidad del tanque al portador en reportes | **+trabajo** (hallazgo, §4.3ter) |

**Balance: el alcance baja.** Se eliminan un ítem de backend y tres más pasan a "sin cambios" (B18/F13/F14), dos de frontend se vuelven "no hacer nada" (F9/F12), y se suman dos de UI pequeños más los tres de vinculación (B24-B26). Lo que más se gana es en migración: `tanker_type_refactor.md` §3.1bis mandaba "rígido con tanque propio + acoplado real" a **revisión manual**; ahora es un estado legal y esa cola desaparece.

**Lo que sí se descubrió de nuevo:**

1. §4.3bis — el acoplado creado desde el modal de la solicitud **nunca se vincula** al camión (`_portal_build_and_create_trailer` no llama a `action_assign_trailer`). Hoy queda enmascarado porque todo camión nace con fantasma; con la regla nueva se vuelve un bug visible. Es el único ítem que **suma** trabajo real.
2. §4.3ter — el certificado de verificación imprime **fabricante y matrícula del tanque en blanco** para toda unidad articulada, porque los lee de `vehicle_id.cistern_*` y el tanque vive en el acoplado. Verificado en `intn_demo`. B29 lo arregla y **es independiente de este refactor**: puede adelantarse.
3. §2.5 — con `max_trailers_per_truck=1` por defecto y el fantasma ocupando la plaza, el escenario que el negocio acaba de confirmar como válido **hoy es imposible de registrar**. Es un argumento extra para priorizar B10 (dejar de crear fantasmas) por encima del resto.
