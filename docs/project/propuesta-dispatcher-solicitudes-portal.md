# Propuesta: dispatcher de solicitudes de servicio en el portal

> **Estado: parcialmente implementada** (actualizado el 2026-08-08). Dejó de ser
> una propuesta el 2026-07-30, con `b4b2818d`.
>
> | Pieza | Estado |
> |---|---|
> | 1 — El dispatcher se muda a `intn_service_request` | **Pendiente.** La ruta sigue viviendo en el controller de flota |
> | 2 — Un handler por categoría, resuelto por convención | **Hecho.** Los cinco `portal.service.request.handler.*` existen |
> | 3 — Los tipos son configuración, no código | **Hecho** para los adjuntos: ONC migró a `attachment_spec_ids` el 2026-08-07 |
> | GET compartido, POST por categoría | **Hecho.** `/my/service_request/<categoría>/new` |
>
> Lo que queda es la pieza 1. Y quedó a la vista lo que cuesta no cerrarla: el
> controller de flota todavía despacha a METCI con un `hasattr`, que es
> exactamente la inversión de propiedad que esta propuesta describe.
>
> Dos rutas dedicadas que contradecían el patrón —METCI y OIAT— se retiraron el
> 2026-08-07; ver [`plan-tours-portal.md`](plan-tours-portal.md).
>
> El orden original decía esperar a cerrar la cobertura de controllers
> ([`plan-tests-controllers-portal.md`](plan-tests-controllers-portal.md)), y esa
> razón sigue en pie para la pieza 1: refactorizar la ruta por donde entran las
> 26 solicitudes es exactamente cómo se llegó a los 8 bugs de producción que
> encontró el saneamiento.

---

## 1. El problema

`/my/service_request/new` es la única puerta de entrada de las **26 solicitudes
de servicio** de las 5 categorías. Hoy se resuelve así:

```
onc_create.py:326                    (intn_onc_certification_requests)
  └─ cistern_service_request.py:26   (intn_portal_fleet_cistern)
      └─ service_request.py:1839     (intn_portal_fleet_requests)  ← 1.966 LOC
```

Tres addons encadenados por herencia sobre el mismo método, y el eslabón final
—el que decide para todas las categorías— vive en **el addon de flota**.

### La inversión de propiedad

`intn_portal_fleet_requests` es dueño de:

- la ruta `/my/service_request/new` para todas las categorías
- `/catalog/resolve`, `/catalog/form_payload`, `/estimate_total`
- el serializador de la cabecera compartida

Eso obliga al addon de flota a conocer categorías de las que no depende (ni
debe: la dependencia correría al revés). El resultado concreto ya está
documentado: `service_request.py:434` llamaba
`_portal_metrology_header_display_vals`, que sólo existe en el addon de
metrología, y el formulario de flota reventaba con `AttributeError` cuando
metrología no estaba instalado.

### El patrón que produjo los bugs

Cuatro de los ocho bugs de producción encontrados son la misma forma: **un
addon hermano no replicó algo que los otros sí tenían.**

| Bug | Dónde faltó |
|---|---|
| `technician_id` sin default | 2 de 6 addons ONI, y 2 de 2 OIAT |
| Departamento de Maquila | 1 de 7 catálogos ONI |
| Resolvedor de producto | Se perdió al renombrar un addon |
| Mixin de emblema | Quedó apuntando a tipos retirados |

Con la responsabilidad repartida entre N addons, cada regla nueva hay que
acordarse de replicarla N veces. No es descuido de nadie: es la estructura
pidiéndolo.

---

## 2. La propuesta

**Se mantiene la URL.** `/my/service_request/new` sigue siendo la puerta única.
Lo que cambia es que deja de ser un embudo con ramas y pasa a ser un
**dispatcher delgado**: resuelve el catálogo, obtiene la categoría, y delega en
el handler que corresponde.

El despacho ya existe a medias en el GET —`/catalog/resolve` y
`/catalog/form_payload` ya hacen trabajo por categoría cuando el cliente elige
el servicio—. Esta propuesta lo completa en el POST en vez de inventar un
mecanismo nuevo.

### Tres piezas

**1. El dispatcher se muda a `intn_service_request`.**
El módulo base pasa a ser dueño de la ruta genérica. Flota se vuelve un
consumidor más, al mismo nivel que metrología, OIAT, ONI y marcas.

**2. Un handler por categoría, resuelto por convención.**

```python
# En el dispatcher, sin registry manual y sin if por categoria:
handler = request.env.get("portal.service.request.handler.%s" % category_code)
if handler is None:
    return self._portal_service_unavailable()
return handler.portal_create(post, files)
```

Cinco `AbstractModel`, uno por categoría:

| Handler | Addon dueño | Tipos |
|---|---|---:|
| `portal.service.request.handler.fleet` | `intn_portal_fleet_cistern` | 5 |
| `portal.service.request.handler.metrology` | `intn_portal_metrology_dispenser_requests` | 5 |
| `portal.service.request.handler.oiat` | `intn_portal_oiat_service_request` | 4 |
| `portal.service.request.handler.oni` | `intn_portal_oni_seguridad_industrial` | 7 |
| `portal.service.request.handler.brand` | `intn_brand_service_requests` | 5 |

Un addon que no registra su handler **simplemente no aparece en el portal**, en
vez de romper en runtime. El fallo se vuelve visible y contenido.

**3. Los tipos son configuración, no código.**
Los 7 ONI comparten handler; lo que los distingue —departamento, campos extra,
adjuntos— ya sale del catálogo. Un tipo nuevo dentro de una categoría existente
pasa a ser **cero código de controller**.

---

## 3. Qué arregla

| Hoy | Con dispatcher |
|---|---|
| `technician_id` se completa en cada addon (2 familias lo olvidaron) | Se completa **una vez** por handler |
| El header de metrología necesita guarda en el controller de flota | Cada handler aporta lo suyo; nadie llama lo ajeno |
| Un tipo nuevo toca el controller | Sólo data de catálogo |
| 1.966 LOC con ramas por categoría | Dispatcher delgado + 5 handlers acotados |
| Un addon roto rompe la ruta para todos | Un handler ausente afecta sólo a su categoría |

---

## 4. Por qué después de la cobertura, y no antes

Dos razones, la segunda más fuerte que la primera.

**La obvia**: refactorizar sin tests la ruta por donde entra todo el negocio es
la operación de mayor riesgo del repo.

**La que decide**: los tests que se están escribiendo pegan a
`/my/service_request/new` con payloads por tipo de servicio. **Si el refactor
conserva la URL —que es la decisión tomada— esos tests no se tocan.** Se
vuelven la red de seguridad del refactor sin modificar una línea, y cada
movimiento del dispatcher queda verificado contra los ~450 casos.

Hacerlo al revés obligaría a reescribir los tests junto con el código, que es
la situación donde un refactor "pasa los tests" porque los tests se adaptaron
al refactor.

---

## 5. Secuencia sugerida

1. **Cobertura de controllers completa** (~4–5 semanas, plan aparte) y en el
   gate de CI.
2. **Mover la ruta y los endpoints de catálogo** a `intn_service_request`, sin
   cambiar comportamiento. Los tests deben seguir en verde sin tocarse: ése es
   el criterio de aceptación del paso.
3. **Extraer un handler**, empezando por la categoría más chica (OIAT, 4 tipos)
   para validar la forma con poco riesgo.
4. **Las cuatro restantes**, una por vez, verificando con el gate entre cada
   una.
5. **Podar** del controller de flota lo que quedó sin uso.

## 5bis. Estado real y pendientes al 2026-07-30

La secuencia de arriba se ejecutó parcialmente y en otro orden: la cobertura se
hizo por familia y los handlers se fueron extrayendo a medida que cada una
tenía red. Estado:

| Categoría | Creación | Ruta propia |
|---|---|---|
| Metrología | handler | no |
| ONI | handler | no |
| OIAT | handler | no |
| Marcas | handler | no |
| **Flota** | **ciclo completo en el controller** | **sí, override en cisternas** |

El contrato del handler quedó en dos métodos, y el segundo apareció al extraer
marcas:

- `portal_create(controller, values, kw)` devuelve el registro
- `portal_values(controller, kw)` arma los valores de la página, para las
  categorías cuyos valores no son los que arma el controller compartido

### El objetivo: `/my/service_request/new` en solo-GET

La forma final no es solo "un handler por categoría": es que la ruta compartida
sirva únicamente el GET y que cada formulario postee a la ruta de su categoría.
El componente OWL ya sabe qué formulario montó, así que también puede saber a
dónde enviarlo.

Lo que **ya está** para eso:

- `/my/service_request/catalog/form_payload` devuelve por catálogo un
  descriptor con `service_category`, `owl_component`, `config`, `view` y
  `create_handler`
- el shell (`service_request_form_shell.js`) consume ese descriptor en
  `_onHeaderLocked`, resuelve el componente y **ya escribe la categoría** en el
  input oculto
- el envío es `form.submit()` nativo multipart, y los adjuntos se leen de
  `request.httprequest.files`

Lo que **falta**:

1. el `action` del formulario está fijo en la plantilla
   (`action="/my/service_request/new"`), no sale del descriptor
2. no hay una ruta POST por categoría; los handlers son modelos sin ruta
3. flota no tiene handler
4. el override de la ruta en `intn_portal_fleet_cistern` intercepta todo

### Orden acordado — completo al 2026-07-31

Los cuatro pasos estan hechos. `/my/service_request/new` sirve la pagina y
cada categoria crea por `/my/service_request/<categoria>/new`, resuelta por
convencion con el mismo codigo que nombra al handler. El campo
`portal_create_handler` del catalogo quedo sin uso y corresponde borrarlo.

Verificacion: 1313 tests en verde, sin regresiones en ninguno de los pasos.

Lo que sigue de la version original, por si hace falta reconstruir el
razonamiento:

### Orden acordado

1. **Partir `_portal_fleet_create_service_request`** (~330 líneas, hoy resuelve
   GET y POST juntos) en `portal_values` + `portal_create`, y registrar el
   handler de flota. Es el único paso difícil de los cuatro y el que habilita
   los otros tres.
2. **Una ruta POST por categoría**, con un controller fino que delegue en su
   handler. Con las cinco categorías ya en handlers, es mecánico.
3. **El shell setea `form.action`** desde el descriptor, en el mismo lugar
   donde hoy setea `service_category`.
4. **`/my/service_request/new` queda en solo-GET** y se borra el override de
   cisternas.

Sobre cómo viaja el endpoint: **por convención**
(`/my/service_request/<categoría>/new`, derivada del catálogo), y no por el
campo `portal_create_handler`. Ese campo ya existe, ya viaja al cliente dentro
del mismo descriptor y **no lo lee nadie**; es un dispatcher a medio construir.
Su `help` dice "nombre de un método Python en `service.request`", que no es una
URL, y es un `Char` libre que un administrador puede escribir mal: volvería a
poner el ruteo en manos de datos editables, que es la clase de problema que
esta propuesta viene a sacar. Al cerrar el paso 2 corresponde borrarlo.

Nota para el paso 3: mientras solo cambie el `action`, el envío sigue siendo
nativo y los adjuntos siguen funcionando igual. Si en algún momento se pasa a
`fetch`, hay que armar el `FormData` a mano; conviene no mezclar ese cambio con
éste.

### Por qué este orden importa mas de lo que parecia

El override de cisternas no es un detalle de organizacion: **es el que produjo
el bug mas caro del saneamiento**. Decidia por todas las categorias con

```python
category = (kw.get("service_category") or "fleet").strip() or "fleet"
if category == "fleet":
    return self._portal_fleet_create_service_request(**kw)
```

Cuando el POST no traía la categoría, mandaba solicitudes de ONI y de OIAT al
ciclo de flota, que no sabe crearlas: la página se volvía a renderizar sin
solicitud y sin ningún mensaje. Un controller que solo debía atender flota era
el que decidía para todos, con un default que reclamaba lo que no era suyo.

Un handler no puede hacer eso: el que no reconoce el tipo delega en `super()`.
Por eso el paso 4 no es cosmético — elimina la clase de fallo, no un caso.

## 6. Riesgos

| Riesgo | Mitigación |
|---|---|
| La cadena de herencia actual tiene comportamiento no documentado que se pierde al extraer | El paso 2 no cambia comportamiento: si los tests pasan sin tocarse, la línea base está capturada |
| Un handler queda sin registrar y su categoría desaparece del portal en silencio | Test transversal: recorrer las 5 categorías y exigir handler registrado. Es el mismo test de consistencia de familia que recomienda el plan de rebalanceo |
| El refactor se solapa con trabajo en curso sobre esos archivos | `service_request.py` y los controllers de portal están en zona de WIP activo; coordinar el momento, no arrancar con cambios sin mergear encima |
