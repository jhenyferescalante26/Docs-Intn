# Plan de cobertura de los controllers de portal

> Objetivo: cada proceso de portal con casos positivos, negativos, de borde y
> validación por mutación, **un archivo por proceso**. Hoy los controllers de
> portal son la capa peor cubierta del repo: sus validadores son funciones
> puras con 8+ ramas y varios tienen cero tests.
>
> Complementa a [`plan-rebalanceo-piramide-tests.md`](plan-rebalanceo-piramide-tests.md),
> que trata en qué capa vive cada aserción. Este documento trata **qué falta
> cubrir** en la capa de controller.

---

## 1. Inventario

### 1.1 Superficie total

| | Cantidad |
|---|---:|
| Rutas `/my/*` | **110** |
| De ellas, POST (mutan estado) | **37** |
| Tipos de servicio activos | **26** |
| Categorías de solicitud | 5 |

Los POST se reparten así:

| Módulo | POST |
|---|---:|
| `intn_fleet_cistern` | 11 |
| `intn_portal_fleet_cistern` | 8 |
| `intn_portal_fleet_requests` | 4 |
| `intn_portal_registration` | 3 |
| `intn_brand_service_requests` | 3 |
| `intn_service_request` | 2 |
| `intn_portal_metrology_dispenser_requests` | 2 |
| `intn_account_pagopar`, `intn_portal_hybrid_auth`, `intn_portal_oiat_service_request`, `intn_onc_certification_requests` | 1 c/u |

### 1.2 Solicitudes de servicio — los 26 tipos

Verificado contra la DB (catálogos activos, 2026-07-30). La columna de adjuntos
es la cantidad de specs obligatorios que declara el catálogo.

| Categoría | Tipo de servicio | Adjuntos |
|---|---|---:|
| **fleet** | `enabling` (Verificación Inicial) | 9 |
| | `annual_verification` (Periódica) | 10 |
| | `eventual_verification` | 9 |
| | `seal_replacement` | 9 |
| | `certificate_modification` (4 subtipos) | 1 |
| **metrology** | `initial_verification` | 0 |
| | `periodic` | 0 |
| | `subsequent` | 0 |
| | `complementary_dispenser` | 0 |
| | `model_approval` | 0 |
| **oiat** | `sample_request` | 0 |
| | `combustibles_normal` | 0 |
| | `combustibles_mic` | 0 |
| | `combustibles_barcazas` | 0 |
| **oni** | `oni_seguridad_industrial` | 0 |
| | `oni_textil` | 0 |
| | `oni_materiales_construccion` | 0 |
| | `oni_metalurgia` | 0 |
| | `oni_muestreo` | 0 |
| | `oni_maquila` | 0 |
| | `oni_inspeccion` | 0 |
| **brand** | `onn_normas` | 0 |
| | `reprint_onn_normas` | 0 |
| | `onc_product_cert` | 0 |
| | `onc_person_cert` | 0 |
| | `onc_system_cert` | 0 |

`certificate_modification` cuenta como **4 casos** por sus subtipos (`ruc`,
`emblem`, `company_name`, `company_name_emblem`), que tienen reglas de
validación distintas. Total efectivo: **29 archivos de solicitud**.

### 1.3 Procesos de portal que no son solicitudes

Van en su propio grupo de archivos:

| Proceso | Rutas principales |
|---|---|
| Vehículos | `/my/vehicle/api/create`, `/write`, `/deactivate`, `/assign_driver`, `unlink_tractor`, lookups |
| Empresas y contactos | `/my/company/new`, `/my/company/<id>/contact/new`, `/my/companies` |
| Establecimientos | `/my/establishment/new`, `/my/establishment/<id>` |
| Documentos (DMS) | `/my/documents`, paginación, filtros, descarga |
| Certificados | `/my/certificates`, `/my/certificate/<id>`, descarga con gate de pago |
| Pagos y transferencias | `/my/invoices/<id>/transfer_receipt`, PagoPar |
| Registro e identidad | signup, MITIC, validación de RUC/nacionalidad |
| Catálogo y cabecera | `/catalog/search`, `/catalog/resolve`, `/form_payload`, `/estimate_total` |
| Agenda | `/my/appointments`, `unavailable_days`, `validate_slot` |

---

## 2. Estructura de archivos

Un archivo por proceso, nombrado por el tipo de servicio:

```
custom_addons/<addon>/tests/portal/
  test_portal_fleet_enabling.py
  test_portal_fleet_annual_verification.py
  test_portal_fleet_eventual_verification.py
  test_portal_fleet_seal_replacement.py
  test_portal_fleet_cert_mod_ruc.py
  test_portal_fleet_cert_mod_emblem.py
  test_portal_fleet_cert_mod_company_name.py
  test_portal_fleet_cert_mod_company_name_emblem.py
  test_portal_metrology_initial_verification.py
  ...
```

Cada archivo tiene **una clase** y cuatro bloques marcados con comentario:

```python
@tagged("post_install", "-at_install", "intn", "<addon>", "intn_portal_cases")
class TestPortalFleetEnabling(PortalCaseCommon):
    """Verificación Inicial de cisternas desde el portal."""

    # -- positivos ------------------------------------------------------
    def test_post_creates_request_with_all_required_fields(self): ...
    def test_post_links_truck_and_trailer(self): ...

    # -- negativos ------------------------------------------------------
    def test_post_without_csrf_is_rejected(self): ...
    def test_post_missing_mandatory_attachment_is_rejected(self): ...
    def test_post_for_foreign_company_is_forbidden(self): ...

    # -- borde ----------------------------------------------------------
    def test_post_with_max_compartments(self): ...
    def test_post_on_weekend_slot_is_rejected(self): ...
    def test_post_at_daily_capacity_limit(self): ...

    # -- mutación -------------------------------------------------------
    def test_validator_rejects_each_missing_field(self): ...
```

### Base común

Un `PortalCaseCommon` que resuelva de una vez lo que hoy cada fixture
resuelve a medias — y que fue la causa de buena parte de los 83 fallos:

- token CSRF (`portal_csrf_token`)
- usuario portal con empresa y scoping
- certificado inicial del vehículo (`ensure_fleet_asset_done_certificate`)
- funcionario autorizado vigente (`ensure_certificate_authorized_official`)
- precintos del registro de medición (`seed_measurement_record_seals`)
- fecha de cita que nunca cae en fin de semana (`next_weekday_on_or_after`)
- helper de adjuntos por tipo de servicio

Los seis helpers ya existen dispersos; falta componerlos.

---

## 3. Taxonomía de casos

Mínimo por tipo de servicio:

| Bloque | Casos mínimos | Qué cubre |
|---|---:|---|
| **Positivos** | 2–3 | Alta con payload completo; variantes del flujo (vehículo existente vs nuevo, con y sin acoplado) |
| **Negativos** | 4–6 | Sin CSRF; sin adjunto obligatorio; campo requerido vacío; empresa ajena (403); catálogo inactivo; precondición de negocio no cumplida |
| **Borde** | 3–5 | Límites numéricos (compartimientos máx., capacidad 0, tope diario); fecha en fin de semana o feriado; strings sólo espacios; unicidad/normalización |
| **Mutación** | 1–2 | Ver §4 |

Con 29 archivos de solicitud a ~12 casos promedio: **~350 tests**. Más los
procesos que no son solicitudes: **~450–500 tests** en total.

---

## 4. Sobre la validación por mutación

Vale una advertencia de viabilidad, porque el costo cambia mucho según qué se
mute.

**Lo que no es práctico**: mutación con herramienta (`mutmut`, `cosmic-ray`)
sobre el suite completo. Cada mutante exige un arranque de Odoo — entre 30 s y
varios minutos. Con cientos de mutantes son días de cómputo por corrida, y no
entra en un gate de CI.

**Lo que sí es práctico**: mutación acotada a los **validadores puros de
controller** — funciones que reciben el dict del POST y devuelven un mensaje.
`_portal_validate_fleet_certificate_modification_fields`,
`_portal_validate_fleet_enabling_contact_fields` y sus equivalentes por
categoría corren en milisegundos y no necesitan base de datos.

La forma concreta, sin herramienta externa: **un test parametrizado que borra
o corrompe un campo a la vez** sobre un payload válido, y exige que el
validador rechace cada variante. Si un campo se puede borrar y el validador
sigue aceptando, la rama que lo cubre está muerta o el test no la ejercía.

```python
def test_validator_rejects_each_missing_field(self):
    """Cada campo obligatorio, borrado de a uno, debe hacer fallar."""
    for field in self.REQUIRED_POST_FIELDS:
        with self.subTest(field=field):
            payload = self.valid_payload(**{field: ""})
            self.assertTrue(self.validate(payload), f"{field} no se valida")
```

Eso da la garantía que interesa —que cada rama del validador está viva y
cubierta— al costo de un `TransactionCase` normal. Es la técnica que ya
apliqué en `test_portal_fleet_field_validation.py` (13 tests, 0,17 s).

---

## 4bis. Forma del POST por familia (descubierto al implementar)

El plan asumia que un mixin por familia alcanzaba. Alcanza, **pero la forma
del payload hay que descubrirla en cada una** y no se parecen entre si. Esto
es lo medido hasta ahora; ahorra la vuelta de diagnostico:

| Familia | Forma del POST | Adjuntos |
|---|---|---|
| **Flota** | Campos planos. `capacity`, seccion de contactos completa (legal_rep_*, contact_*, driver_*), `appointment_date` en dia habil y entre 08:00 y 17:00 | Por clave del catalogo, de `_get_required_attachment_specs()` |
| **ONI** | JSON en `oni_service_lines` con secciones `billing`, `contact` y la de servicios | Ninguno |
| **Metrologia** | Campos planos con lineas indexadas: `line_<campo>_<n>` | Ficha tecnica por linea en `line_technical_sheet_<n>` |
| **Marcas (ONC)** | `service_category=brand` en la ruta compartida; el resto lo parsea un modelo de formulario por tipo via `_portal_parse_vals(kw, partner)` | Specs por `service_type` |
| **Marcas (ONN)** | Rutas propias: `/my/brand_request/new`, `/my/brand_print_request/new` | Por definir |
| **OIAT** | JSON en `oiat_service_lines`, **dict con clave `services`** (una lista pelada se descarta en silencio) | Ninguno |

Dentro de ONI la forma tampoco es unica: la mayoria manda `services` como
lista, maquila manda un dict unico bajo `sample` y programa de inspeccion una
lista bajo `garrafas`. Por eso el mixin expone `services_section()`.

### Precondiciones que no viajan en el POST

Cuestan una vuelta de diagnostico cada una porque el mensaje de error no dice
de donde sale el dato:

- **RUC de ONI**: `_portal_oni_resolve_company_vat` lo toma del partner
  comercial, no del payload. Sin el, cuatro de los siete tipos rechazan.
- **Certificado del vehiculo**: todos los tipos de flota salvo `enabling` y
  `certificate_modification` lo exigen.
- **Hora de la cita**: fuera de 08:00-17:00 el portal rechaza, asi que heredar
  la hora de `now()` hace que el test dependa de cuando se corra.

### Sobre REQUIRED_*_FIELDS

Dos veces se colo un campo que parecia obligatorio y no lo era: `catalog_id`
en ONI (se resuelve desde el `service_type` de la raiz) y
`metrology_request_date` (la migracion 18.0.1.13.5 lo dejo como dato visible
que ya no gobierna nada). En ambos casos el test fallaba **contra
comportamiento correcto**, que es el falso positivo mas caro: ensena al equipo
a ignorar el suite.

**Cada campo que entra a la lista se verifica contra el validador, no se
supone por su nombre.**

## 5. Orden de trabajo

1. **`PortalCaseCommon`** con los seis helpers compuestos. Sin esto cada
   archivo repite el mismo prólogo frágil.
2. **Un tipo de servicio completo como patrón**, revisado y aprobado, antes de
   generar los otros 28.
3. **Fleet (8 archivos)** — es la categoría con más reglas: adjuntos
   obligatorios, gate de certificado, agenda con capacidad diaria, subtipos.
4. **ONI (7) y OIAT (4)** — comparten forma de payload; salen rápido una vez
   hecho el primero de cada familia.
5. **Metrología (5) y marcas (5)**.
6. **Procesos que no son solicitudes** (~9 archivos).

Cada archivo entra al gate de CI apenas queda verde, sumándolo a
`GREEN_MODULES` en `.github/workflows/odoo-tests.yml`.

## 6. Estimación

| Etapa | Archivos | Tests | Esfuerzo |
|---|---:|---:|---|
| Base común + patrón | 1 + 1 | ~15 | 1–2 días |
| Fleet | 8 | ~110 | 1 sem |
| ONI + OIAT | 11 | ~120 | 1 sem |
| Metrología + marcas | 10 | ~110 | 1 sem |
| No-solicitudes | ~9 | ~100 | 1 sem |
| **Total** | **~40** | **~455** | **4–5 semanas** |

Es la inversión que convierte a la capa de controller —hoy la peor cubierta y
donde vivieron 4 de los 8 bugs de producción encontrados— en la mejor.
