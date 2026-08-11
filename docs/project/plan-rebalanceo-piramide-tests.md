# Plan de rebalanceo de la pirámide de tests

> **Estado:** Fase 0 cerrada. Fase A en curso. Este plan **no agrega cobertura**: mueve
> aserciones existentes de Playwright a la capa nativa de Odoo y borra el TS equivalente.
>
> Complementa —no reemplaza— a [`docs/project/_e2e-refactor-plan/`](_e2e-refactor-plan/README.md),
> que inventaría *casos faltantes*. Este documento trata el eje ortogonal: *en qué capa vive
> cada aserción que ya existe*.

---

## 0. Corrección de rumbo (2026-07-29)

**La premisa original de este plan era falsa y hay que decirlo arriba de todo.**

La versión inicial diagnosticaba: *"la pirámide ya existe abajo (Python es sólida), falta la capa
media JS y sobra peso arriba"*. La parte entre paréntesis no se verificó, y no era cierta.

Al cerrar la Fase 0 se corrió por primera vez el suite Python de los 4 módulos tocados:
**79 fallos**, en 4 módulos de 71. Entre ellos, dos suites de ACL cuyo `setUpClass` moría por un
typo y **no ejecutaban un solo test**, y varios archivos apuntando a endpoints removidos hace
tiempo.

### La causa raíz es común a las dos capas

Lo que se encontró arriba y abajo es la misma patología, no dos problemas distintos:

| Capa | Síntoma |
|---|---|
| Playwright | `FUNC 02-5` envuelto en `if (count() > 0)`: pasaba sin verificar nada |
| Playwright | `03-onm-pricing` rojo por diseño, documentado en su propio encabezado |
| Python | `setUpClass` muerto por un typo: dos suites sin correr, en verde aparente |
| Python | Tests contra `/my/service_request/create_truck`, endpoint borrado a propósito |
| Python | `appointment_date` con offset fijo: pasaba 5 de cada 7 días |

**`.github/workflows/` sólo tiene `pre-commit.yml`, que es lint. CI no corre ni un test.** Esa es
la causa raíz: nada ejecuta el conjunto, así que la podredumbre no tiene dónde manifestarse. Mover
aserciones de una capa sin gate a otra capa sin gate no lo arregla — sólo cambia dónde se pudre.

> **Ya no es así (corregido el 2026-08-08).** El párrafo de arriba se deja tal cual porque es el
> diagnóstico que originó este plan, y borrarlo haría incomprensible la Fase A. Pero **dejó de ser
> cierto el día siguiente a escribirse**: `odoo-tests.yml` corre los tests de los 75 módulos desde
> el 2026-07-30, y al 2026-07-31 no queda ningún addon fuera del gate. Desde el 2026-08-07 hay un
> tercer job, `portal-tours`, para la capa de tours de navegador
> (ver [`plan-tours-portal.md`](plan-tours-portal.md)).
>
> Quien lea este plan buscando el estado de CI está leyendo el documento equivocado: esta sección
> es historia, no situación. La afirmación sobrevivió una semana larga sin que nadie la revisara y
> se citó como vigente más de una vez.

### Qué cambia en consecuencia

1. **Se antepone la Fase A**: dejar Python en verde y ponerle un gate en CI. Sin el gate, todo lo
   demás se degrada de nuevo.
2. **La Fase 1 (aislamiento de fixtures) baja a última y pasa a ser opcional.** La versión
   original la recomendaba primero por ROI. Ya no aplica: optimiza el runtime de un suite que la
   Fase 4 reduce de 59 specs a ~6 en CI. Primero se achica, después se mide si los 17 minutos
   siguen doliendo.
3. **El contrato de aserción gana una regla de higiene** (ver §1).

### Lo que este desvío pagó

Más que la Fase 0 en sí, y conviene registrarlo para justificar la Fase A:

- Un `AttributeError` que rompe el formulario del portal de flota en producción cuando el addon de
  metrología no está instalado (dependencia no declarada, arreglada con un no-op base).
- Dos suites de ACL que llevaban sin ejecutarse desde `ba0426e1`.
- Un test que fallaba los fines de semana.

Nada de eso aparece moviendo aserciones de capa.

---

## 1. Diagnóstico

### Estado actual medido

| Capa | Volumen | Runtime |
|---|---|---|
| Playwright (`e2e/`) | 59 specs, 320 tests, 24.5k LOC TS (9.2k specs + **15.3k `lib/`**) | 17 min, `workers: 1` |
| Seed compartido | `seed_e2e_data.py` — 3.023 LOC / 108 KB | — |
| Python nativo | 236 archivos, 27k LOC, 129 `TransactionCase`, ~20 `HttpCase` | segundos, **no verde** |
| JS nativo (hoot) | **0 tests** — con OWL propio en portal | — |
| Tours nativos | **0** (solo `service_catalog_tour_registry.js`, que es registry) | — |
| **Gate en CI** | **ninguno** — `pre-commit.yml` es sólo lint | — |

Acoplamiento a UI: **886 `.locator()`**, 348 `roleContext()`, 118 llamadas RPC,
**158 `captureDocScreenshot()` en 33 specs**.

### Los dos problemas reales

**(a) El costo de mantenimiento no está en los specs, está en `lib/flows/`.**
9.2k LOC de specs contra 15.3k LOC de helpers. Esos helpers existen mayormente para *leer valores
desde el DOM* (`portal-fleet-request.ts` = 1.377 LOC). Cuando la aserción deja de ser sobre valores,
el helper se reduce a "hacer clic hasta el siguiente estado".

**(b) El seed global impide paralelizar.**
`playwright.config.ts` lo documenta explícitamente: *"Parallel workers (>1) race on shared seed
partners/vehicles; use workers=1 for stable CI."* Estado mutable compartido entre 320 tests.

### Contrato de aserción (regla durable)

Esta es la parte del plan que sobrevive a la implementación:

| Capa | Assertea | No assertea |
|---|---|---|
| `TransactionCase` + helper `Form` | **Valores**: montos, correlativos, solapamientos, transiciones, constraints, onchanges, reglas de acceso | Nada de UI |
| `HttpCase` | **Contratos HTTP**: status de ruta, payload JSON, gates de pago, scoping por empresa, `report_type=html` → 200 | Valores de negocio (ya cubiertos arriba) |
| `hoot` | **Componentes OWL**: estado interno, render condicional, handlers | Datos reales |
| Playwright / tours | **Que el cableado existe**: la cadena multi-rol completa produce el registro terminal, con sus vínculos no vacíos, y sin errores de UI | **Valores.** Nunca. |

Corolario operativo: una aserción e2e válida se escribe **por RPC contra el registro final**, no
leyendo el DOM. `certificate_id != False`, `state == 'done'`, el PDF responde 200. Tres o cuatro
por cadena, no veinte.

La excepción —y la aserción de mayor valor por línea de todo el suite— es la **global**:
`assertOdooUiClean()` (`lib/odoo-ui-monitor.ts`) captura crashes de OWL, errores de consola y
diálogos de error. Ningún test Python puede reproducir eso. Se refuerza, no se toca.

### Regla de higiene: un test que no puede fallar es peor que ninguno

Agregada tras la Fase 0, donde aparecieron tres instancias. Un test que no puede fallar cuesta
tiempo de ejecución y produce confianza falsa, que es el peor de los dos mundos. Son sospechosos
hasta que se demuestre lo contrario:

- Cualquier `if` que envuelva la aserción (`if (await button.count() > 0) { expect(...) }`).
- Cualquier `skipTest` / `test.skip` condicional cuya condición nadie verifica que sea falsa en CI.
- Cualquier `setUpClass` que pueda morir en silencio: si revienta, la suite entera reporta 0 tests
  y eso **no** se distingue de "verde" en la salida.
- Cualquier test cuyo resultado dependa del día, la hora o el orden de ejecución.

Corolario para las fases que quedan: **antes de portar un spec, verificar que hoy pase**. Un spec
rojo o redundante se borra sin escribir Python, y son más frecuentes de lo que parece — en la
Fase 0 fueron 3 de 9.

---

## 2. Clasificación del suite

Los 59 specs se parten en tres grupos por destino:

| Grupo | Specs | LOC | Destino |
|---|---|---|---|
| **A — Migrables** (0 screenshots, no journey) | 20 | ~2.540 | Python (`TransactionCase` / `HttpCase`) → borrar el TS |
| **B — Generadores de doc** (≥1 screenshot) | 33 | ~5.900 | Se quedan en Playwright, dejan de ser tests |
| **C — Journeys + smoke** | 6 | ~525 | Se quedan como e2e real, con aserciones de cableado |

### Corrección de método (2026-07-29, tras los 3 primeros ports)

La primera versión de este plan clasificó el grupo A contando `.locator()` **literal** por
archivo, y concluyó que 9 specs con 0–1 ocurrencias eran "Python disfrazado de Playwright".
**Esa medición estaba mal:** los specs manejan la UI a través de helpers de `lib/` (`roleContext`,
`clickHeaderButton`, `selectOdooMany2oneField`, `createFleetRequestViaPortal`…), cuyos locators
viven en el helper, no en el spec. Contar el archivo subestima el acoplamiento a UI.

Medido de nuevo contando llamadas que manejan UI (locators + helpers + navegación), de los 9
candidatos **sólo uno** (`04-verificacion-visual-resultados`) no tocaba el navegador. Los otros 8
sí lo hacen.

La conclusión de fondo no cambia —sus **aserciones** siguen siendo de lógica y pertenecen abajo—
pero el costo por spec sí: no es traducción mecánica, hay que separar en cada uno qué aserción es
valor (baja a Python) de cuál es cableado (se queda o se absorbe en un journey).

| Spec | LOC | Tests | Llamadas UI | Estado |
|---|---:|---:|---:|---|
| `fleet/04-verificacion-visual-resultados` | 76 | 2 | **0** | ✅ borrado — redundante y stale |
| `fleet/04-acoplado-attach-backend` | 88 | 1 | 6 | ✅ portado (4 tests) |
| `fleet/03-solicitud-fleet-cistern-onm-pricing` | 191 | 1 | 4 | ✅ portado (5 tests) |
| `brand/21-brand-control-etiquetas` | 42 | 2 | 5 | ✅ portado (ACL + ruta portal) |
| `brand/20-backoffice-deep` | 47 | 2 | 7 | ✅ portado (ACL); 1 test descartado |
| `fleet/02-backoffice-deep` | 176 | 8 | 17 | ✅ borrado — redundante, 0 Python |
| `fleet/03-solicitud-fleet-cistern-onm-service-types` | 288 | 11 | 17 | ✅ adelgazado a 9 tests (13 en Python) |
| `fleet/03-solicitud-fleet-cistern-derived-fields` | 88 | 5 | 5 | ⤴ **reclasificado a Fase 3** |
| `fleet/25-capacidad-calendario-bug` | 65 | 1 | 5 | ⤴ **reclasificado a Fase 3** |
| **Total** | **1.061** | **33** | — | **Fase 0 cerrada** |

**Reclasificación a Fase 3 (hoot), no a Python.** Dos specs resultaron ser pruebas de
componente OWL, no de lógica de modelo, y forzarlos a Python habría perdido justo la regresión
que vigilan:

- `25-capacidad-calendario-bug` intercepta la llamada de red y verifica que
  `/my/service_request/unavailable_days` se invoque con la capacidad del vehículo recién
  seleccionado. Es cableado JS entre el selector de vehículo y `PortalFleetCalendarField`.
- `03-derived-fields` verifica qué secciones renderiza cada modal y que el formulario de edición
  sea de sólo lectura — su último test nombra literalmente el getter `isReadonly()` de
  `portal_vehicle_app.js`.

Ambos se quedan en Playwright hasta que la Fase 3 monte el bundle de hoot, y son sus dos primeros
candidatos naturales.

**Efecto en el cronograma:** la Fase 0 pasa de 3–5 días a **1–1,5 semanas**. Los tres primeros
ports tomaron ~40 min cada uno incluyendo verificación; los seis restantes son más grandes
(`onm-service-types` y `02-backoffice-deep` concentran 17 llamadas UI cada uno). El total del plan
sube de 6–9 a **7–10 semanas**.

### Hallazgos de los primeros tres ports

Los tres specs portados no sólo eran redundantes o mal ubicados — **dos estaban rotos**, y el
navegador lo ocultaba:

1. `04-verificacion-visual-resultados` era **100 % redundante**: `test_onm_visual.py` ya cubría
   ambos casos. Y estaba **stale**: asserteaba `state == "done"` para el rechazo, pero
   `action_confirm()` cierra los rechazos como `"cancel"`. El test Python ya tenía el
   comportamiento nuevo. Cero Python escrito, sólo borrado.
2. `03-onm-pricing` estaba **rojo por diseño**: su encabezado documentaba que depende de un
   cableado de catálogo que sólo existe en el sandbox `intn_preprod`. Seis escenarios de portal
   completo que no podían pasar.
3. `04-acoplado-attach-backend` tenía el guard server-side de "acoplado de otra empresa" **sin
   ningún test**: el spec sólo lo cubría vía el `domain` del campo, que es UI.

Lección para las fases siguientes: **antes de portar, verificar si el spec pasa**. Un spec rojo o
redundante se borra sin escribir Python, y son más frecuentes de lo esperado.

---

## 3. Fases

Orden original: *primero se borra, después se arregla*. Sigue valiendo dentro de cada fase, pero
ahora está subordinado a una regla más fuerte que salió de la Fase 0: **primero se pone en verde y
se le pone un gate, después se mueve nada**. No tiene sentido bajar aserciones a una capa que no
está verificada ni protegida.

### Fase A — Python en verde y con gate en CI (nueva, primera)

Prerrequisito de todo lo demás. Sin esto, cada fase siguiente deposita trabajo en una capa que se
degrada sin que nadie se entere.

1. **Dimensionar.** Correr el tag `intn` completo (los 71 módulos, no los 4 medidos hasta ahora).
   Es un comando y es lo único que convierte la estimación en un número real:
   ```bash
   .venv/bin/python src/odoo/odoo-bin -c odoo.conf.local -d intn_docs \
     --no-http --stop-after-init --test-enable --test-tags=intn -u all
   ```
2. **Triage por causa raíz, no por test.** En los 4 módulos medidos, 79 fallos se redujeron a 23
   atacando 5 causas. Agrupar por mensaje de excepción antes de tocar nada.
3. **Arreglar**, distinguiendo siempre fixture de bug de producción. En el saneamiento inicial la
   proporción fue ~4 a 1 a favor de fixtures, pero el bug que apareció era real y afectaba al
   portal.
4. **Poner el gate.** Un workflow que corra `odoo test intn` en cada PR. Es el entregable que hace
   durable a todos los demás.

**DoD:** el tag `intn` en verde, y un workflow de CI que lo ejecute y bloquee el merge.

**Estado:** dimensionada. En los 4 módulos del saneamiento inicial se bajó de 79 a 23 fallos.

### Medición del suite completo (2026-07-29, DB `intn_docs`, 179 módulos cargados)

```
845 tests con tag `intn`  →  48 failed + 35 error(s)  =  83 fallos (~10 %)
22 módulos con fallos, sobre 52 que tienen tests
```

Es la primera medición del suite completo que existe en el proyecto. Buenas noticias dentro del
número: **no hay ningún `setUpClass` roto** (los dos que había se arreglaron), y la mitad de los
fallos se concentra en 3 módulos.

| Módulo | Fallos | Nota |
|---|---:|---|
| `intn_portal_fleet_requests` | 17 | En saneamiento; son los 23 conocidos menos los ya resueltos |
| `intn_service_request` | 15 | Módulo base del que dependen casi todos — 8 son el gate de certificado |
| `intn_portal_metrology_dispenser_requests` | 7 | Estados de revisión documental y productos de catálogo |
| 6 módulos `intn_portal_oni_*` | 18 | Hermanos, pero **no** comparten una sola causa |
| 13 módulos restantes | 26 | Cola larga de 1–3 cada uno |

Causas dominantes en todo el suite:

| Causa | Fallos | Naturaleza |
|---|---:|---|
| Gate de certificado inicial (vehículo sin `certificate.management` en `done`) | 16 | Fixture — mismo patrón ya resuelto, falta extenderlo a otros módulos |
| Asserts de status HTTP (`N != N`) | 16 | Mezcla: rutas movidas y respuestas cambiadas |
| Precintos no cargados al confirmar registro de medición | 3 | Fixture |
| Finalizar sin documentación aprobada | 3 | Fixture (falta el paso de aprobación) |
| Resto | 45 | Cola larga heterogénea |

**Interpretación para planificar.** El 10 % de fallos no está repartido parejo: se concentra en el
eje flota/portal, que es la parte más desarrollada del repo. Los módulos `intn_portal_oni_*`
fallan poco individualmente pero son 6, así que conviene revisarlos juntos aunque no compartan
causa única. El gate de certificado sigue siendo la causa #1 y ya tiene solución conocida
(`ensure_fleet_asset_done_certificate`); extenderla fuera de `intn_portal_fleet_requests` requiere
mover el helper a un lugar compartido, porque hoy vive en el `tests/common.py` de ese módulo.

**Estimación:** con 83 fallos, ~4 causas sistemáticas y una cola larga de ~45, y tomando como
referencia el ritmo del saneamiento inicial (79 → 23 en una sesión atacando causas raíz),
**2–3 semanas** para dejar el tag `intn` en verde, más 1–2 días para el workflow de CI.

### Avance de la Fase A

| Medición | Fallos / 845 | Módulos con fallos |
|---|---:|---:|
| Línea base (2026-07-29) | 83 | 22 |
| Helper de certificado compartido + fixtures de `intn_service_request` | 73 | — |
| `es_PY` activo en la DB de test | 72 | — |
| Producto por defecto, CSRF de ONI, certificado en 3 módulos más | 55 | — |
| RUC/adjuntos de ONM, `intn_documents`, `technician_id` de ONI, Maquila, MRO | 43 | 16 |
| Autorrelleno del portal, fixture de precintos, CSRF y `technician_id` de OIAT | **38** | **16** |

**36 de los 52 módulos con tests están hoy en verde.** Eso habilita la estrategia de gate por
módulo descrita en §6, sin esperar a llegar a cero.

### Bugs de producción encontrados por el saneamiento

Cinco, y ninguno se habría encontrado moviendo aserciones de capa:

| Bug | Impacto | Causa |
|---|---|---|
| `_get_default_service_product_xmlid` devolvía `""` siempre | Línea del pedido sin producto | Override perdido al renombrar `intn_portal_metci_service_request` |
| `_portal_metrology_header_display_vals` sin guarda | Portal de flota crashea si metrología no está instalado | Dependencia no declarada (y no declarable: corre al revés) |
| `technician_id` sin default en 2 addons ONI | **500 al enviar la solicitud** desde el portal | Dos de seis hermanos no replicaron el override |
| Departamento "Maquila y Manufactura" inexistente | **Servicio inaccesible desde el portal** (404) | Falta el registro que el modelo busca por nombre exacto |
| No-op base tapando un mixin por MRO | Header de metrología vacío (0 de 18 departamentos) | **Introducido durante este mismo saneamiento** y detectado al re-medir |
| `_portal_fleet_form_defaults` comentada | Autorrelleno del portal muerto desde 2026-07-13 | Se comentó "para evitar el failed en el pre-commit" (04e3b72b) en vez de arreglar un `return` mal indentado |
| `technician_id` sin default en los 2 addons OIAT | **500 al enviar la solicitud** desde el portal | La misma omisión que ONI, en otra familia |

**El patrón dominante:** un módulo nuevo o renombrado no replica algo que sus hermanos sí tienen.
Cuatro de los siete son exactamente eso, y el de `technician_id` apareció en **dos familias
distintas** (ONI y OIAT) antes de cerrarse.

**Barrido de `technician_id` (2026-07-30):** las cinco categorías (`fleet`, `metrology`, `oiat`,
`oni`, `brand`) completan hoy el campo, y las cinco filtran por **categoría**, no por tipo de
servicio — que es justo lo que fallaba en ONI, donde el override existía por addon y cubría sólo
su propio tipo. La clase de bug queda cerrada, no sólo sus instancias. Vale considerar un test transversal de consistencia de
familia (todos los `oni_*` con `portal_header_ready=True`, todos con default de técnico) — sale
mucho más barato que descubrirlos de a uno.

### Trampa de Odoo que costó una regresión

Un **no-op base no reemplaza a un `hasattr`**. En el MRO de un modelo declarado como
`_inherit = ["service.request", "algún.mixin"]`, la definición acumulada de `service.request`
queda **antes** que el mixin: un método agregado en el módulo *base* gana sobre los mixins de
módulos *posteriores*, al revés de lo que sugiere la intuición. Verificable con:

```python
for k in type(env["service.request"]).mro():
    if "_mi_metodo" in vars(k):
        print(k.__module__, k.__name__)
```

Cuando el llamador no puede depender del addon que aporta el método, la guarda va en el **punto
de llamada**, no en una implementación base.

**Lección para el resto de la fase: las precondiciones vienen en capas.** Arreglar el gate de
certificado destapó el de organismo (`_intn_fleet_apply_organism_from_vals` no puede autocompletar
`organism_id` sin `request_type_id`), y arreglar ese destapó el de revisión documental. El conteo
baja en escalones, no linealmente, y cada escalón sólo se ve después de subir el anterior. No
conviene estimar el resto por regla de tres sobre lo ya resuelto.

### Requisito de entorno para la DB de CI

Descubierto al sanear: **`es_PY` debe estar activo** en la base donde corra el gate. Estaba
inactivo en `intn_docs` y eso hacía fallar los tests de etiquetas en español — que son requisito
de producto, no un extra, dado que el despliegue es paraguayo.

Ojo con la tentación de "arreglarlos" poniéndoles una guarda de `skipTest`: los convierte en
skips silenciosos, que es exactamente el antipatrón de §1. La DB de CI tiene que tener el idioma
activo para que esos tests corran de verdad.

**Causas ya resueltas** (útiles como catálogo para el resto del suite):

| Causa | Fallos | Naturaleza |
|---|---:|---|
| Módulos sin instalar en la DB de test (metrología, OIAT) | 17 | Entorno |
| Vehículos de fixture sin el `certificate.management` en `done` | 32 | Fixture |
| Tests contra endpoints removidos (`create_truck`/`create_trailer`) | 8 | Test obsoleto |
| `_portal_metrology_header_display_vals` sin implementación base | 26 | **Bug de producción** |
| `ensure_vehicle_initial_certificate(..., cls.partner)` con atributo inexistente | 2 suites | Fixture (typo en `ba0426e1`) |
| `appointment_date` con offset fijo que cae en fin de semana | 6 | Test dependiente de la fecha |

### Fase 0 — Specs sin DOM → Python (3–5 días)

Los 9 specs de la tabla anterior. Son `adminRpc()` + aserciones sobre el resultado: la traducción a
`TransactionCase` es casi mecánica y elimina el navegador del camino.

Destinos propuestos (confirmar el módulo dueño al portar cada uno):

| Spec | Módulo destino |
|---|---|
| `03-onm-pricing`, `03-onm-service-types`, `03-derived-fields` | `intn_portal/intn_portal_fleet_requests/tests/` (26 tests existentes, ya hay `test_onm_*`) |
| `04-verificacion-visual-resultados` | `intn_fleet/intn_fleet_cistern_verification/tests/` (junto a `test_onm_visual.py`) |
| `04-acoplado-attach-backend` | `intn_fleet/intn_fleet_cistern_verification/tests/` |
| `25-capacidad-calendario-bug` | `intn_portal/intn_portal_fleet_requests/tests/` |
| `02-backoffice-deep` | `intn_base/intn_service_request/tests/` |
| `20-backoffice-deep`, `21-brand-control-etiquetas` | `intn_brand/intn_brand_service_requests/tests/` |

Todos los módulos destino ya tienen `tests/` con casos existentes — no hay scaffolding nuevo.

**DoD:** los 9 archivos `.spec.ts` borrados; `odoo test intn` verde; el helper de `lib/flows/` que
quedó sin consumidores, borrado también.

**Entregable medible:** −1.061 LOC TS, −33 tests de navegador.

### Fase 1 — Aislamiento de fixtures → `workers: 4` (1–2 semanas) — **última y opcional**

> **Reordenada (2026-07-29).** La versión original la ponía segunda y la llamaba "el cambio de
> mayor ROI del plan". Ya no lo es: optimiza el runtime de un suite que la Fase 4 reduce de 59
> specs a ~6 en el gate de CI. Optimizar 17 minutos de algo que se va a achicar un 90% es
> prematuro. Se hace **al final**, y sólo si tras la Fase 4 el tiempo sigue molestando.

El único cambio que mejora el suite *sin* mover una sola aserción.

1. Auditar qué consume `loadSeedState()` y `seed_e2e_data.py` (3.023 LOC) desde los specs sobrevivientes.
2. Separar el seed en dos: **configuración inmutable** (productos, organismos, tipos de servicio,
   secuencias, usuarios de rol) que puede seguir siendo global, contra **datos transaccionales**
   (partners, vehículos, solicitudes) que pasan a crearse por test.
3. Crear los transaccionales vía RPC con prefijo por worker (`E2E_W${index}_...`) y limpiarlos en teardown.
4. Subir `workers` a 4 y correr el suite 3 veces seguidas para detectar races residuales.

**DoD:** `workers: 4` estable en 3 corridas consecutivas; el comentario de `playwright.config.ts`
sobre races, borrado.

**Entregable medible:** 17 min → ~5 min.

### Fase 2 — Backoffice-deep restantes → Python / HttpCase (2–3 semanas)

Los 11 specs restantes del grupo A: `fleet/01`, `fleet/03-backoffice-deep`,
`fleet/03-vehicle-form-fields`, `fleet/05-certificados-vcc-dins`, `brand/21-comprobantes-entregas`,
`brand/21-impresion-etiquetas`, `brand/21-menu-security`, `brand/21-muestreo`,
`metrology/10-backoffice-deep`, `mrp/18-backoffice-deep`, `oiat/16-backoffice-deep`.

Reparto por naturaleza de la aserción:

- **Lógica de negocio y formularios** → `TransactionCase` + helper `Form`. `Form` simula onchanges y
  campos calculados sin navegador; cubre la mayoría de `03-vehicle-form-fields` (12 tests, 3 locators).
- **Permisos y menús** (`21-brand-menu-security`) → `TransactionCase` sobre `ir.model.access` /
  `ir.rule`, no clics. Ojo: `inventario-casos-e2e.md` ya documenta 4 brechas de permisos que
  hoy solo se aplican en UI — al portar, **arreglar el modelo**, no el test.
- **Rutas portal** → `HttpCase`, patrón ya establecido en `intn_portal_fleet_requests/tests/`.

Los dos specs mixtos (`sales/13-14-backoffice-deep` 13 tests/3 shots, `sales/23-costos-backoffice-deep`
5 tests/3 shots) se parten: los tests con screenshot quedan en Playwright (grupo B), el resto migra.

**DoD:** grupo A vacío; `lib/flows/` auditado y podado de helpers huérfanos.

**Entregable estimado:** −2.500 LOC TS adicionales, y una poda significativa de `lib/flows/`
(el número real depende de cuántos helpers quedan sin consumidor — medir, no prometer).

### Fase 3 — hoot para el OWL del portal (1–2 semanas)

La brecha real de cobertura, no un movimiento de tests: hoy hay **cero** tests JS.

Setup (una vez, ~1 día): declarar el bundle `web.assets_unit_tests` en el `__manifest__.py` del
módulo portal, apuntando a `static/tests/**/*.test.js`. Es el mismo mecanismo que usan los módulos
core (`account`, `analytic`, `base_automation` lo tienen declarado en Odoo 18).

Componentes objetivo, en orden de frecuencia de cambio:

1. `intn_fleet_cistern/static/src/js/portal_vehicle_app/portal_vehicle_app.js`
2. `intn_fleet_cistern/static/src/js/portal_vehicle_app/portal_tank_data_panel.js`
3. `intn_fleet_cistern/static/src/js/_shared/vehicle_form_contract.js`

~2–4h por componente una vez montado el bundle.

**DoD:** los 3 componentes con tests hoot corriendo en `odoo test`.

### Fase 4 — Grupo B deja de ser suite de tests (1 semana)

Los 33 specs con screenshots siguen navegando la UI en detalle —lo necesitan para capturar—, pero
cambian de rol: pasan a ser **generador de documentación**.

1. Mover a un proyecto Playwright propio (`docs-capture`), separado de `chromium` y `journey`.
2. Sacarlos del gate de CI: su fallo reporta, no bloquea.
3. Podar sus aserciones de valor (las que quedaron cubiertas en Fases 0–2) y dejar solo la
   navegación + `captureDocScreenshot` + `assertOdooUiClean`.
4. Los scripts `doc:screenshots:*` de `package.json` apuntan al proyecto nuevo.

**Nota:** este grupo **no se migra a tours nunca**. Los tours de Odoo no capturan screenshots y no
hay equivalente nativo. Es la razón por la que Playwright se queda en el repo de forma permanente.

### Fase 5 — Journeys: aserciones de cableado (continuo)

Los 6 specs del grupo C (5 journeys + `smoke-login`) son el e2e legítimo. Se reescriben sus
aserciones al contrato de la sección 1: por cada cadena, 3–4 checks RPC sobre el registro terminal
+ `assertOdooUiClean()`. Cero lecturas de DOM para verificar valores.

---

## 4. Sobre tours nativos

**No hay fase de tours en este plan, y es deliberado.**

Los tours se vuelven viables recién *después* de la Fase 2: su debilidad principal es que no tienen
`expect()` y assertear valores es incómodo, pero si el e2e ya no assertea valores esa objeción
desaparece — un tour es exactamente "navegá estos pasos y que cada trigger aparezca".

Aun así, la decisión se pospone. Cuando un spec del grupo C quede reducido a "clic, clic, clic,
llegó", la diferencia entre dejarlo en Playwright o traducirlo a tour es de gusto, no de costo — y
Playwright gana en debugging (trace viewer, video, `--ui`) contra un volcado de log de browser.

Multi-rol **sí** es posible en tours (`self.start_tour(url, 'tour_a', login='tecnico')` seguido de
otro `start_tour` con otro login en el mismo `HttpCase`), así que no es eso lo que decide. Reevaluar
al cerrar Fase 2.

---

## 5. Cronograma y resultado

Orden revisado tras la Fase 0:

| Orden | Fase | Duración | Acumulado |
|---|---|---|---|
| ✅ | 0 — Aserciones de lógica en specs chicos | 1–1,5 sem | cerrada |
| **1º** | **A — Python en verde + gate en CI** | **2–3 sem** | 3 sem |
| 2º | 2 — Backoffice-deep | 2–3 sem | 6 sem |
| 3º | 3 — hoot OWL | 1–2 sem | 8 sem |
| 4º | 4 — Grupo B a doc-capture | 1 sem | 9 sem |
| 5º | 5 — Journeys | continuo | — |
| último | 1 — Aislamiento de fixtures | 1–2 sem | *opcional* |

**8–10 semanas**, con la Fase A ya dimensionada sobre los 845 tests reales del suite completo (no
extrapolada). Sigue siendo **incremental**: cada fase entrega valor sola.

La Fase A no bloquea a la 2 en sentido estricto — se pueden solapar por módulo, arrancando la
Fase 2 sobre los módulos que ya quedaron verdes. Lo que **no** debe hacerse es empezar la Fase 2
sobre un módulo cuyo Python todavía falla: porta aserciones a una base rota y hereda sus fixtures
frágiles.

Estado final esperado:

| | Antes | Después |
|---|---|---|
| **Gate de tests en CI** | **ninguno** | **`odoo test intn` bloqueando el merge** |
| **Suite Python** | **no verde, sin medir** | **verde y medido** |
| Specs Playwright en CI | 59 | **6** (journeys + smoke) |
| Specs Playwright totales | 59 | 39 (6 CI + 33 doc-capture no bloqueante) |
| LOC TS | 24.5k | ~15k, con `lib/flows/` sustancialmente podado |
| Runtime del gate Playwright | 17 min | ~2 min (6 specs) |
| Tests JS (hoot) | 0 | 3 componentes OWL |
| `workers` | 1 | 1, salvo que la Fase 1 se justifique al final |

Las dos primeras filas son las que más cambian respecto de la versión original del plan, y son las
que sostienen a todas las demás: sin gate, cualquier estado final alcanzado se degrada.

### Modo alternativo: incremental sin proyecto dedicado

Si no se puede asignar un bloque de 6–9 semanas, el mismo plan funciona como regla de trabajo:
**cada vez que se toca un módulo, se bajan sus aserciones de lógica a Python y se borra el spec
correspondiente.** La Fase 1 (fixtures) es la única que conviene hacer de una sola vez, porque es
transversal y desbloquea el runtime para todo lo demás.

---

## 6. Riesgos

| Riesgo | Mitigación |
|---|---|
| **La Fase A resulta mucho más grande de lo previsto al medir los 71 módulos** | Es el riesgo principal y por eso el paso 1 es medir. Si el número es inmanejable de una vez, el gate se introduce **por módulo**: se arranca con los que ya están en verde y se van sumando, en vez de bloquear todo hasta que el 100% pase |
| **El gate se agrega y empieza a fallar por tests dependientes de la fecha** | Ya apareció uno (offset fijo que cae en fin de semana). Al montar el gate, correrlo una vez forzando fechas distintas (o revisar todo `timedelta(days=` en fixtures) antes de hacerlo bloqueante |
| **Se arregla un test adaptándolo al bug en vez de arreglar el bug** | En el saneamiento inicial la proporción fue ~4 fixtures por cada bug real, pero el bug existía. Ante un fallo, la pregunta es siempre "¿el test miente o el código está mal?" — el `AttributeError` de metrología parecía un problema de entorno y era un bug de producción |
| Portar una aserción pierde cobertura sin que nadie lo note | Regla de borrado: el `.spec.ts` se borra **en el mismo commit** que agrega el test Python, nunca antes |
| Fase 1 destapa races que hoy el `workers: 1` oculta | Presupuestar 3 corridas completas del suite como criterio de aceptación; si aparecen races de datos *no* provenientes del seed, es un bug real de concurrencia — escalarlo, no silenciarlo |
| Al portar permisos aparecen las 4 brechas ya documentadas | Arreglar el modelo (`ir.rule` / `ir.model.access`), no adaptar el test a la UI. Ver `inventario-casos-e2e.md` |
| `seed_e2e_data.py` resulta más entrelazado de lo previsto | Fase 1 arranca con una auditoría de consumidores antes de tocar código; si la separación config/transaccional no es limpia, replantear alcance en vez de forzarlo |
| Los specs del grupo B se degradan sin nadie mirando | Corren igual en cada release para regenerar docs; su fallo reporta a un canal, aunque no bloquee el merge |
