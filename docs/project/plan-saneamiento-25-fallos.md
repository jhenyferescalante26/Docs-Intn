# Plan de saneamiento de los 25 fallos restantes

> **Cerrado.** Los 25 fallos se sanearon: `odoo-tests.yml` documenta que **al
> 2026-07-31 no queda ningún addon fuera del gate**, y el job exige la línea
> `0 failed, 0 error` para pasar. El documento se conserva como registro de cómo
> se sanearon —las reglas de la sección siguiente se reutilizaron después— pero
> ya no describe trabajo pendiente.
>
> _Nota de cierre agregada el 2026-08-08._

Medicion base: `--test-tags=intn -u all` sobre `intn_docs`, 2026-07-30, corrida
completa (179/179 modulos).

**25 fallos de 1195 tests, en 12 modulos** — exactamente los 12 que estan fuera
del gate. Ningun modulo de los 40 verdes falla, asi que CI sigue pasando
mientras dure este saneamiento.

## Reglas que aplican a todo el plan

Son las mismas con las que se sanearon los 83 fallos anteriores:

1. **Nunca adaptar un test al bug, ni convertirlo en skip silencioso.** Cada
   fallo se cierra declarando donde estaba el defecto: en el test o en el
   producto. Si esta en el producto y no se arregla ahora, se anota con su
   motivo en el `__init__.py` del addon, como ya se hizo con los tres archivos
   sin registrar.
2. **Un test que no puede fallar es peor que ninguno.** Todo arreglo se
   verifica revirtiendolo: si el test sigue verde sin el arreglo, el test no
   sirve. Es lo que destapo que dos mixins corrian sin
   `allow_inherited_tests_method`.
3. **Cada campo obligatorio se verifica contra su validador, no se supone.**
4. Cada modulo que quede en verde se suma a `GREEN_MODULES` en
   `.github/workflows/odoo-tests.yml`. El gate solo crece.

## Bloque 1 — Idioma (7 fallos)

| Test | Espera |
|---|---|
| `TestPortalValidateSlotHttp.test_slot_max_cap_missing_range_and_capacity_limit` | "Limite de agendamientos alcanzado" |
| `TestPortalOniInspeccionServiceRequest.test_post_requires_geo_coordinates` | "georreferencial" |
| `TestPortalOniMuestreoServiceRequest.test_post_requires_geo_coordinates` | "georreferencial" |
| `TestPortalOniMaquilaServiceRequest.test_post_requires_vue_request_number` | "tramite VUE" |
| `TestPortalOiatCombustiblesServiceRequest.test_post_requires_combustibles_fields` | "Licencia VUI" |
| `TestPortalAdditionalCosts.test_portal_shows_category_groups` | "Administrativos" |
| `TestPortalFleetVehicleServiceRequest.test_service_type_label_spanish_onm` | etiqueta en espanol |

**Causa verificada**: ninguno de esos textos existe en el codigo; estan solo en
los `.po`. `es_PY` esta activo en la base, pero el usuario de prueba corre en
`en_US`, asi que la respuesta se renderiza en ingles. El defecto es del
fixture, no del producto.

**Que NO hacer**: cambiar las aserciones al texto en ingles. Eso convertiria
siete tests de mensaje al usuario en tests que ya no verifican que la
traduccion llegue, que es justo lo que estan cuidando.

**Que hacer**: que el usuario de prueba corra en `es_PY`. Se agrega al fixture
compartido, no test por test.

**Riesgo, y por que no se hace de una**: hay tests hoy en verde que asertan
texto en ingles. Cambiar el idioma del fixture compartido los rompe. Por eso el
bloque arranca midiendo: activar `es_PY` en `PortalFleetHttpCase`, correr el
tag completo y comparar contra esta linea base. Si el saldo es negativo, la
alternativa es un mixin `SpanishPortalCase` que solo usen las siete clases.

Costo estimado: medio dia, casi todo en la medicion.

## Bloque 2 — ONI: el POST que no crea y no informa (2 fallos + 3 archivos sin registrar)

El bloque de mas valor del plan, y el unico con un defecto de producto claro.

| Sintoma | Donde |
|---|---|
| `ValueError: invalid literal for int(): 'new'` | `TestPortalOniMaquilaServiceRequest.test_post_creates_request_with_maquila_service_type` |
| idem | `TestPortalOniInspeccionServiceRequest.test_post_creates_request_with_inspeccion_service_type` |
| POST 200 sin error y sin solicitud | `test_portal_oni_inspeccion.py`, sin registrar |
| idem | `test_portal_oni_metalurgia.py`, sin registrar |

**El `ValueError` no es el bug.** El test hace
`int(response.url.rstrip("/").split("/")[-1])` para sacar el id de la
redireccion. La URL sigue terminando en `new` porque el POST nunca redirigio:
no se creo nada. El test revienta en vez de reportar, y esconde el fallo real
detras de una excepcion que parece de parseo.

Primer arreglo, barato y aparte: que esos tests aserten la creacion por
`submission_token` en vez de parsear la URL. Deja de mentir sobre la causa.

**El bug real** es que estos creadores devuelven vacio sin decir por que. Lo ya
descartado, anotado en el `__init__.py` de ONI para no repetirlo:

- el departamento del catalogo coincide con el que busca
  `_portal_is_{inspeccion,metalurgia}_catalog`, asi que el despacho si ocurre
- ambos creadores incluyen `submission_token` en sus vals, igual que los que
  funcionan
- la respuesta no trae ninguna alerta de validacion

La diferencia estructural es que textil delega en
`super()._portal_create_oni_service_request()` y estos construyen la solicitud
por su cuenta. Que la prueba propia de maquila caiga en el mismo sintoma
amplia el racimo: son los tres que se construyen solos.

**Siguiente paso concreto**: instrumentar el creador desde adentro. Un test que
llame al metodo del modelo directamente, sin pasar por HTTP, y afirme sobre el
recordset devuelto. Si ahi crea, el problema esta en el camino del controller;
si no, esta en el creador y el traceback deja de estar tapado por el `except`
del dispatcher.

Entregable: causa identificada, arreglo, y los dos archivos registrados.

Costo estimado: uno a dos dias. Es el unico bloque con incertidumbre real.

## Bloque 3 — Fixtures que el codigo dejo atras (3 fallos)

| Test | Error |
|---|---|
| `TestPortalServiceRequestPages.test_new_post_metrology_success` | `Invalid RUC check digit. Expected digit: 0` |
| `TestPortalServiceRequestPages.test_service_request_detail_redirects_foreign_request` | vehiculo sin certificado valido |
| `TestTankInspectionPortalCertificate.test_legacy_tank_certificate_route_redirects_to_portal_certificate` | checklist sin completar |

Los tres son tests correctos contra precondiciones que el codigo empezo a
exigir despues de que se escribieran. El caso mas claro es el RUC: la
validacion contra DNIT entro en `0c34d034` e invalido un RUC de fixture
anterior. El producto esta bien; el fixture quedo viejo.

Arreglo: usar los helpers que ya existen en `PortalCaseCommon`
(`given_vehicle_with_certificate`) y agregar uno para RUC valido, de modo que
el digito verificador se calcule y no se escriba a mano. Un RUC hardcodeado en
un fixture es esta misma falla esperando repetirse.

Costo estimado: medio dia.

## Bloque 4 — Rutas JSON que devuelven HTML (2 fallos)

`TestPortalOniServiceRequest.test_form_payload_oni_catalogs_filtered_by_department`
y `..._sample_types_filtered_by_department` fallan con
`JSONDecodeError: Expecting value: line 1 column 1`: la ruta contesta una
pagina de error en vez de JSON.

Probable defecto de producto: una excepcion sin manejar dentro de una ruta
`type="json"`. Hay que leer el traceback del servidor, que la respuesta HTML
esconde. Si se confirma, el arreglo incluye que la ruta falle como JSON y no
como pagina, porque un cliente que espera JSON no puede hacer nada con un HTML.

Costo estimado: medio dia.

## Bloque 5 — Estado nunca implementado (2 fallos) — DECISION DEL USUARIO

`TestInitialVerificationWorkflow.test_document_review_{approve,reject}_*`
esperan que `metrology_execution_state` pase de `document_review` a
`request_approved` / `document_rejected`. Esa transicion no existe.

No es un test roto: es una funcionalidad que se especifico y no se
implemento. Las opciones son implementarla o retirar los tests dejando
constancia. **No corresponde decidirlo desde el saneamiento** — es alcance.

## Bloque 6 — ACL de calendario (1 fallo) — DECISION DEL USUARIO

`TestOnmCalendarAcl.test_calendar_acl_unassigned_visible_only_to_manager`
protege un estado al que hoy no se llega. Misma naturaleza que el bloque 5.

## Bloque 7 — Triage de los 8 restantes

Sin causa comun; cada uno pide su vuelta. Lo que ya se sabe:

- `TestFleetPortalAttachmentHttp.test_seal_replacement_post_missing_green_card_fails`
  espera "Green card", que **no existe ni en el codigo ni en las
  traducciones**. A diferencia del bloque 1, aca el mensaje cambio y el test
  quedo viejo. Hay que averiguar cual es el mensaje actual y si sigue diciendo
  lo mismo.
- `TestPortalFleetRequestFlowIntegration` (2): "Portal submission did not
  create a service.request". Mismo sintoma que el bloque 2 pero en flota;
  conviene atacarlo despues, por si comparten causa.
- `TestPortalVehiclesJson.test_form_payload_includes_vehicle_capacity_and_service_location`: 404.
- `TestPortalCertificatePaymentGate`, `TestPortalAutofill.test_portal_model_approval_replay_defaults`,
  `TestPortalServiceRequestPages.test_new_get_renders_metrology_category`.

Costo estimado: un dia, con la reserva propia de un triage.

## Orden sugerido

1. **Bloque 3** (fixtures) — barato, sin incertidumbre, saca 3
2. **Bloque 1** (idioma) — saca 7 de un golpe si la medicion acompana
3. **Bloque 2** (ONI) — el de mas valor: 2 fallos, 2 archivos sin registrar y
   probablemente los 2 de flota del bloque 7
4. **Bloque 4** (JSON) — 2
5. **Bloque 7** (triage) — el resto
6. **Bloques 5 y 6** quedan a la espera de la decision de alcance

Bloques 1 a 4 mas el 7 cierran 22 de los 25. Los otros 3 no son deuda de
tests: son funcionalidad que falta.

## Criterio de salida

Cada modulo que quede sin fallos entra a `GREEN_MODULES`. Cuando los 12 esten
adentro, el gate cubre el 100% de los addons y desaparece la condicion que
dejo que estos 25 se acumularan sin que nadie los viera: que
`.github/workflows/` tuviera lint y no tuviera tests.
