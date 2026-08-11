# Plan de cierre — Bloques B a F

> Relevado el 29/07/2026 contra `6388290e` (rama `18.0`).
> Complementa el informe interno del Bloque A
> (`docs/project/informes/INTN-informe-cierre-bloque-A-2026-07-29.pdf`), que cubre
> las 32 tarjetas ya cerrables.
>
> **Ampliado el 29/07 con el barrido de subtareas y comentarios** (Frente 1,
> sección "Segundo relevamiento"). El relevamiento original se hizo sobre un
> export que no incluía subtareas; el barrido por API corrigió los números y
> destapó observaciones abiertas que no estaban en este plan.
>
> **⛔ Leer primero el Frente 2.8.** INTN no puede validar el sprint #3 porque no
> logra enviar una solicitud desde el portal. Cualquier otra priorización queda
> subordinada a eso.
>
> **Fuera de alcance inicial por decisión:** aplicación móvil de precintos
> (RF 16.1–16.9, 9 tarjetas).
>
> **Ventana disponible:** sprint #11 cierra el 31/07, sprint #12 el 14/08.

---

## Estado de los frentes

| Frente | Alcance | Naturaleza | Estado |
|--------|---------|------------|--------|
| 1 | Higiene del tablero | Coordinación | Pendiente de autorización de INTN — y de rehacer la clasificación sobre 415 tarjetas |
| 2 | Cerrar el ciclo de lo hecho (B) | Mixto | En curso — se sumaron 2.5 a 2.9. **El 2.8 bloquea la validación del resto** |
| 3 | Integridad documental (F1) | Desarrollo | Pendiente |
| 4 | Defectos acotados (F2, F4, F5) | Desarrollo | Pendiente |
| 5 | Dependencias externas (D) | Escalamiento | Pendiente |
| 6 | Brechas de alcance (E) | Decisión | Pendiente |

---

## Frente 1 · Higiene del tablero

**No es desarrollo.** Es prerrequisito de cualquier priorización: mientras el tablero
no distinga "terminado sin firmar" de "no empezado", no hay forma de leer el estado
real del proyecto.

**Documento de respaldo:**
`docs/project/informes/INTN-saneamiento-tablero-2026-07-29.pdf` (presentable a INTN,
a diferencia del informe del Bloque A que es interno).

**Estrategia adoptada:** separar decisión de ejecución. Se pide a INTN *una*
autorización, no ~110 ediciones manuales. Con el visto bueno, la ejecución se hace
por API desde nuestro lado.

### Clasificación verificada contra el tablero en vivo (29/07)

| Grupo | N.º | Acción |
|-------|-----|--------|
| A · Cerrables | 32 | Cerrar |
| B · Alcance real sin sprint | ~90 | **Planificar, no archivar** |
| C · Duplicados | ~35 | Fusionar |
| D · Registros administrativos | ~42 | Archivar |
| E · Entregables contractuales | 11 | No tocar |

> **Corrección respecto del análisis inicial.** Las cubetas `rf 7`, `rf 8`, `rf 10`,
> `rf 11`, `rf 12`, `rf 14` y `rf 15` **no son espejos de las tarjetas de sprint**:
> son el único registro de alcance que nunca se planificó. Sólo `rf 5` (23 de 25),
> `rf 6` (5) y `rf 7` (3) tienen par real en sprints. Aplicar una regla de
> "cubeta temática = duplicado" habría eliminado ~90 tarjetas de alcance contratado.

### Pasos

- [ ] Verificar permiso de escritura en la lista `Sistema ERP -INTN` (está bajo
      "Shared with me") con un cambio de prueba sobre una sola tarjeta
- [x] Redactar el documento de pedido para INTN
- [ ] Presentarlo en un único lugar (tarjeta nueva o punto de reunión), con mención
      a Isaura Flores y Luz Lezcano
- [ ] Obtener autorización explícita antes de tocar nada
- [ ] Generar el anexo con IDs exactos por acción (se produce al momento de ejecutar,
      contra el tablero en vivo, para que no quede desactualizado)
- [ ] Ejecutar por API una vez autorizado:
  - [ ] Cerrar las 32 tarjetas del Grupo A
  - [ ] Fusionar los ~31 duplicados de cubeta (usar *merge*, no borrado: varias
        tienen definiciones funcionales en los comentarios)
  - [ ] Fusionar los 4 duplicados cruzados entre sprints
  - [ ] Archivar las ~29 entrevistas de relevamiento y las 13 tarjetas de agenda
  - [ ] Desambiguar los 7 pares de RF colisionados (RF 8.x, 10.1, 10.2, 10.3, 7.1,
        11.1, 14.1 designan dos requerimientos distintos según la cubeta)
  - [ ] **No tocar** las 11 tarjetas de `documentaciones` y
        `documentación y glosario` — son los Informes 1 a 8 y el glosario
- [ ] Entregar el detalle de lo ejecutado, tarjeta por tarjeta, para revisión de INTN
- [ ] Planificar el Grupo B con INTN — es la conversación de alcance del Frente 6

**Resultado esperado:** de 315 a ~205 tarjetas, con ~90 de alcance pendiente
explícitas y priorizables.

> Los números de arriba se calcularon sobre `docs/project/tasks.csv`. El barrido
> por API los corrige — ver la sección siguiente.

### Segundo relevamiento (29/07): subtareas y comentarios

Se recorrió la lista por API con `filter_tasks(subtasks=true, include_closed=true)`.

**El tablero tiene 415 tarjetas, no 315.** El export `tasks.csv` que sirvió de base
al primer relevamiento contiene **264 únicas**: faltan ~151, y son justamente las
subtareas donde vive la conversación de QA. Ninguna de estas figura en el CSV:

`86e22rtv7` Observaciones Generales de Ajuste · `86e1y063u` Nuevo Camión Tanque ·
`86e1ykdme` Acoplado · `86e1y8yxx` Restricciones de agendamiento · `86e24eq4g`
Cambio de RUC · `86e26yfny` Precintos · `86e24ehyv` Camión Tanque - Modificaciones
y sus 14 subtareas.

Consecuencia práctica: la clasificación A–E hay que rehacerla sobre las 415 antes
de ejecutar nada por API. El grupo D (registros administrativos) y el E
(entregables) no cambian —son tarjetas raíz—, pero A, B y C sí.

#### Estado de desarrollo desactualizado en el tablero

Tarjetas marcadas `Pendiente`, en blanco o `Trancado` que **sí tienen código en la
rama**. Verificado por existencia de módulo o commit, no por cumplimiento funcional
(las de sprint #5–#8 requieren auditoría RF por RF antes de cerrarlas):

| Tarjeta | Estado en tablero | Código en `18.0` |
|---------|-------------------|------------------|
| RF 13.1 / 13.3 / 13.4 / 13.5 Picos | Pendiente (sprint #10/#11) | `51388e0b` — **RF 13.2 sí sigue sin código** |
| RF 11.1 QR público | Pendiente (sprint #11) | `db37c026` |
| RF 4.2 DNIT en facturación | **Trancado** (sprint #4) | `0c34d060`, `intn_account_dnit_validation` |
| In situ / laboratorio `86e0yymtz` | en blanco (sprint #2) | `979c4581` + `74ad2693` |
| Tipos de servicio Picos `86e0yymuh` | en blanco (sprint #2) | `intn_portal_metrology_dispenser_requests` |
| RUC duplicado `86e0yymtp` | en blanco (sprint #2) | `partner_vat_unique` + `l10n_py_ruc` |
| Archivar datos `86e0yymtv` | en blanco (sprint #2) | campo `active` |
| GPS del contacto `86e0yymtd` | en blanco (sprint #2) | `partner_map_picker` — el comentario de la tarjeta todavía dice "no implementado" |
| Inspección de Tanque Cisterna `86e1fvep0` | Pendiente (sprint #5) | `intn_fleet_cistern_verification` + `84a772d5` |
| Portal OIAT `86e1fy9c2` | Pendiente (sprint #7) | `intn_portal_oiat_service_request` |
| Portal ONI `86e1fy9ft` | Pendiente (sprint #7) | 7 módulos `intn_portal_oni_*` |
| RF 6.7 / 6.8 / 6.9 ONC | Pendiente (sprint #7) | `intn_onc_certification_requests` |
| RF 5.14 / 5.15 / 5.17 METCI | Pendiente (sprint #5) | `intn_mrp_metci`, con 3 reportes |
| RF 5.9–5.13 informes ONI | Pendiente (sprint #6/#7) | `intn_mrp_oni/report` + `legacy_adapted` |

Pendientes reales confirmados por ausencia de código: RF 9.1–9.5 Básculas,
formulario METCI en portal `86e1fxawe`, RF 13.2, RF 7.1–7.3 inventarios,
RF 10.1/10.2 calendario general, RF 3.13 cuotas, RF 2.10 mapa, RF 12.1 TRA,
RF 1.1 limpieza de contactos.

#### Tarjetas de alcance que el export tampoco mostraba

Aparecieron en el barrido, tienen especificación funcional en los comentarios y no
figuran en ningún sprint:

- `86e2ahzqp` **Categoría de producto y sus determinaciones** — el portal hoy toma
  las categorías de `Ventas → Service Categories`, que no son las categorías
  funcionales de los laboratorios. Pide una parametrización nueva donde elegir
  categoría filtre las determinaciones asociadas. HU completa del 12/07
- `86e28whkw` **Bases y condiciones en el portal** — enlace parametrizable a
  Nextcloud con las condiciones de servicios y ensayos, visible durante toda la
  carga de la solicitud
- `86e0yxqnf` **RF 3.9 costos adicionales** — figura como *Listo para pruebas* pero
  tiene dos HU detalladas de abril sin verificación registrada: precios de
  combustible por ciudad con historial de variaciones, y viáticos por departamento
  (con/sin pernocte) más carga masiva de peajes sobre ~300 ciudades

#### ⚠️ El barrido sigue incompleto

Se hizo por tandas, con la cuota de la API como límite:

| Pase | Alcance | Leídas |
|------|---------|--------|
| 1 | Sprints #1 y #2 | 55 (cortado por `RATE_LIMIT_EXCEEDED`) |
| 2 | Sprint #3 y las movidas en julio | ~35 |
| A | Sprints #3 resto, #4 y #5 | 29 |
| B | Sprints #6, #7 y #8 | 16 |
| C | Sprints #9 a #12 + documentos | 16 |
| D | Cubetas `rf 5`–`rf 16` y `solicitudes a analizar` | ~130 |
| E | Administrativas (muestra) | 12 |

**Los doce sprints y las doce cubetas temáticas quedaron cubiertos por completo.**

#### Resultado de la tanda D: las cubetas no tienen conversación

De las ~130 tarjetas de `rf 5`, `rf 6`, `rf 7`, `rf 8`, `rf 10`, `rf 11`, `rf 12`,
`rf 14`, `rf 15`, `rf 16` y `solicitudes a analizar`, **una sola tiene comentario**
(`86e0yxrqp`, y es la especificación original de ClickBot).

Esto cierra una duda del primer relevamiento y tiene dos consecuencias:

1. **Confirma que son registro de alcance, no trabajo en curso.** Nadie las discutió
   nunca. Su contenido vive en la descripción, no en la conversación.
2. **No aportan nada al estado de la 18.0.** Todo lo que estaba en juego —
   observaciones abiertas, defectos, decisiones pendientes — estaba en los sprints,
   que es donde se concentró el esfuerzo del barrido.

Para el Frente 1 esto simplifica la ejecución: fusionar o planificar estas tarjetas
no destruye información, porque no hay ninguna sepultada en sus comentarios. La única
salvedad sigue siendo la del primer relevamiento: **`rf 7` a `rf 15` no son espejos
de tarjetas de sprint**, así que se planifican, no se archivan.

#### Resultado de la tanda E: sólo material de relevamiento

Muestra de 12 sobre las ~55 administrativas. Las tarjetas de agenda diaria y los
Informes 1 a 8 no tienen comentarios. Las entrevistas de enero sí: son minutas con
el pedido original de cada área (pasarela de pago, restricción de impresión del PDF,
cierre de caja individual, calendario con bloqueo de fechas, QR de validación,
personal tercerizado, in situ / laboratorio). **Todos esos pedidos ya tienen su RF
correspondiente en un sprint** — son la fuente del alcance, no alcance suelto.

Valen como material de consulta cuando falte contexto de negocio; no como pendientes.
- [ ] Rehacer la clasificación A–E sobre las 415
- [ ] Corregir en el tablero el estado de desarrollo de las tarjetas de la tabla de arriba

> **Lección del segundo pase, para no repetirla.** Los comentarios de
> "Verificación de implementación" que se dejaron el 28/07 se apoyaron sólo en el
> código. En al menos dos casos (`86e204nrm` y `86e2054g6`, ver 2.9) la tarjeta de
> observaciones asociada tenía puntos abiertos que contradecían ese "implementado".
> **Cerrar contra código y no contra la conversación produce falsos cierres.**

---

## Frente 2 · Cerrar el ciclo de lo ya hecho (Bloque B)

Desarrollo hecho, falta un pedido puntual. Son horas, no semanas.

### 2.1 · RF 2.5 — Límite de descargas de 2 a 1 · `86e0yxqtm`

Instrucción explícita de Luz Lezcano del 04/06: *"cámbialo directo a 1 sola
descarga"*. El valor sigue en 2 y su único commit es anterior al pedido.

- [x] `document_download_policy.py`: default del campo `portal_max_downloads` 2 → 1
- [x] `document_download_policy.py`: fallbacks de `_intn_default_portal_max_downloads`
      y `_intn_default_portal_report_max_downloads` 2 → 1
- [x] `data/intn_documents_config_data.xml`: ambos parámetros 2 → 1
- [x] Bump de versión del manifiesto `18.0.1.0.0` → `18.0.1.1.0`
- [x] Migración `migrations/18.0.1.1.0/post-migrate.py`: el archivo de datos es
      `noupdate`, así que las bases existentes conservan el valor viejo. Actualiza los
      dos `ir.config_parameter` y las filas de política que aún tengan 2, respetando
      cualquier valor que un administrador haya fijado a otra cosa (incluido 0 =
      ilimitado)
- [x] Verificado que no rompe tests: `test_portal_download_limit_blocks_after_max_reached`
      fija `portal_max_downloads: 2` explícitamente, así que no depende del default
- [x] Migración ejecutada contra `intn_docs`: los dos parámetros pasaron a 1, una fila
      de política bajó de 2 a 1, versión del módulo en `18.0.1.1.0`. Re-ejecución
      idempotente (no vuelve a correr). Carga de registro posterior sin errores

### 2.2 · RF 8.2 — Informes de certificados · `86e0yxqk3`

Estado `Retornado`. El Excel ya exporta chasis y conductor (`d2a1c68e`). **No es
desarrollo**: falta una definición de negocio pendiente desde el 19/02.

- [ ] Pedir a INTN la definición: ¿la reimpresión consume litraje del cupo diario?
      (hoy no lo consume — el cupo es por litraje y sólo lo descuentan cuatro tipos
      de servicio; la reimpresión vive como `reprint_reason`)
- [ ] Con la respuesta, levantar el `Retornado` o abrir tarjeta por el cambio

### 2.3 · Restricción de agendamiento · `86e26ndkn`

**Cero desarrollo.** La tarjeta dice que la restricción se aplica al cliente; el
código ya la aplica al camión.

- [ ] Verificar en instancia: `fleet_no_show` / `fleet_no_show_date` sobre
      `fleet.vehicle`, ventana de 30 días, cancelación tardía configurable a 48 h
- [ ] Actualizar la tarjeta y cerrarla

### 2.4 · Subtareas de Camión Tanque · `86e24ehyv`

14 subtareas, ninguna cerrada. Priorizar las que ya tienen corrección commiteada sin
validar.

- [ ] Observación Registro de Medición `86e24g250` — parcial; **el detalle exacto de
      lo que falta está en 2.7**, confirmado por INTN el 29/07
- [x] Pestaña de Adjuntos — `f25c13df`, con captura de respaldo en la tarjeta
- [ ] DINATRAN pedido de más — `a579b597`
- [ ] Certificado hereda revisión aprobada — `1e9dfdda`
- [ ] Observación Verificación Inicial `86e24fkb1` — **no está resuelta**: Luz
      Lezcano el 21/07 respondió "sigue igual". Detalle en 2.7
- [ ] Asignación de remolque `86e24ejqe` — Luz el 27/07: *"el acoplado es OPCIONAL,
      ¿por qué se implementó esto?"*; la respuesta fue que se iba a subir un cambio y
      que por ahora se pruebe con acoplados. Verificar si ya está en la rama
- [x] Datos históricos `86e2cbzpj` — resuelto en el Frente 3, comentado en la
      tarjeta el 29/07

### 2.5 · "Listo para pruebas" con observaciones sin responder

Salió del barrido de comentarios del 29/07. Son tarjetas que el tablero da por
terminadas pero que tienen preguntas de INTN sin contestar. Ninguna se puede cerrar
sin resolver esto primero, y varias son respuesta, no desarrollo.

| Tarjeta | Estado | Qué quedó abierto |
|---------|--------|-------------------|
| `86e0yxqjn` RF 8.3 Check de procedimientos | Listo para pruebas / Aprob. **En Proceso** | 12/04 Luz Lezcano: faltan campos de la v12 (Dimensiones del Tanque, Especificaciones de Neumático). 14/04: el botón Confirmar de Prueba Hidrostática y de Registro de Medición **lanza error**. Sin respuesta desde entonces |
| `86e0yxqkd` RF 2.3 Carga de documentos | Listo para pruebas | 9 observaciones del 25/03 y la lista del 15/04 (baja de camión, cancelación con 42 h, validación de calendario por 160 l/día, historial completo del camión). Se derivó a `86e24ggwq` sin cerrar la original |
| `86e0yxqkh` RF 1.2 Empresa matriz | Listo para pruebas | Punto 9 (un encargado por sucursal, que sólo vea lo suyo) sin resolver. Los puntos 7 y 8 dependen del servicio DNIT/MITIC — van al Frente 5 |
| `86e0yxqm6` RF 2.1 Registro de cliente | Listo para pruebas | Abierto desde el 13/02: la compra de normas debe funcionar **sin** aprobación previa de ATC |
| `86e0yxqk9` RF 8.1 Historial de camiones | Listo para pruebas | "Consultar por Cédula del Chofer — ya se tiene el servicio (solicitar)". Es la misma clase de dependencia que el RF 1.3 del Frente 5 |
| `86e0yxqma` RF 2.6 Estado del pedido | Listo para pruebas / Aprob. **Listo** | Comentario nuevo del 29/07 sobre una tarjeta ya aprobada. Revisar antes de darla por firme |

- [ ] Contestar las seis en la tarjeta, con evidencia o con la pregunta que falte
- [ ] Reproducir el error del botón Confirmar de `86e0yxqjn` — es el único defecto
      técnico del grupo y no tiene tarjeta propia

### 2.6 · RF 2.7 Presupuesto en portal · `86e0yxqna`

Estado `Retornado` con **dos observaciones sin responder**: el precio debe salir
según capacidad y compartimientos del vehículo, y la etiqueta debe decir
"PRESUPUESTOS", no "COTIZACIONES".

Existe `docs/project/specs/rf-2.7-presupuesto-en-portal.md`. No se verificó si lo
especificado llegó a implementarse.

- [ ] Contrastar el spec contra el código y responder en la tarjeta

### 2.7 · Defectos de QA sin cerrar en subtareas de sprint #1 y #3

Reportados por jhenyfer.escalante y Luz Lezcano entre el 25/06 y el 12/07. El 08/07
Isaura Flores preguntó por el estado de dos de ellos; la respuesta fue "esperando
que Felix suba los cambios" y ahí quedó. Ninguna de estas tarjetas estaba en el
export, por eso no figuraban en este plan.

- [ ] `86e22rtv7` Observaciones Generales de Ajuste — 6 puntos, sólo el 6 marcado
      resuelto. **Abiertos 1 a 5:** un usuario Administrador no ve los agendamientos;
      faltan los checks de Estado de Precintos e Inscripciones Obligatorias en
      Verificación Visual; el motivo de rechazo debe ser obligatorio; la edición de
      datos durante la verificación debe dejar traza en el chatter; el formulario
      Vehículos debe seguir la estructura del portal
- [ ] `86e1y063u` Nuevo Camión Tanque — registra el vehículo pero no redirecciona;
      el código de camión debe ser único dentro del emblema y repetible entre
      emblemas. Sobre el rango 1–7 ver la nota de abajo
- [ ] `86e1ykdme` Acoplado — mismo reporte del rango 1–7

> **Sobre el rango 1–7.** El constraint existe en el modelo:
> `_check_compartment_count_range()` en
> `intn_fleet_cistern/models/fleet_vehicle.py:1237` rechaza `<1` y `>7`. El reporte
> de QA es del 30/06 y puede haberse corregido después, o el defecto puede estar en
> el camino del portal (validación de cliente o creación del acoplado) y no en el
> modelo. **Hay que reproducirlo en instancia antes de estimarlo** — no darlo por
> abierto ni por cerrado desde el tablero.
- [ ] `86e24p8rp` Recuperación automática — no recupera los datos del Representante
      Legal ni del Conductor Autorizado. Hilo de 11 respuestas sin conclusión, con
      una pregunta de Yamil sin contestar: *dónde se registran esos datos para poder
      traerlos al formulario*
- [ ] `86e26yfny` Precintos — "Registro de Medición no permite cargar datos al crear
      un nuevo registro". Es el mismo síntoma que `86e0yxqjn`, conviene tratarlos juntos
- [ ] `86e24fkb1` Observación Verificación Inicial — Luz Lezcano el 21/07:
      *"Sigue igual, leer nuevamente lo solicitado"*. Lo pedido: el técnico debe
      verificar cada punto **antes** de fijar el resultado final (hoy es al revés);
      al elegir Rechazo no se puede ingresar el motivo, y por eso no se puede guardar;
      los datos documentales deben mostrarse desde la solicitud del portal para
      comparar, editables sólo para errores de tipeo

#### Ya resueltos — verificar y cerrar, no desarrollar

Salió de leer los comentarios completos: tres ítems que este plan daba por abiertos
ya tienen respuesta en la tarjeta.

- [ ] `86e1y8yxx` / `86e272gg6` alerta de técnico no asignado — Yamil Torrico el
      09/07: *"La alerta aparecerá cuando intenten aprobar documentos o confirmar la
      solicitud. El PR se subirá al finalizar el día."* Falta verificar
- [ ] `86e1y0ae7` adjuntos en PDF o imagen — Yamil el 13/07: hecho, y el texto de
      declaración jurada quedó dinámico y editable desde Compañía
- [ ] `86e24ggwq` Modificaciones Documentos Adjuntos — mismo cambio que el anterior,
      ya aplicado

#### `86e24g250` Registro de Medición — parcial, con el resto identificado

De los 4 puntos, **hoy Luz Lezcano confirmó qué falta**: *"Falta punto 2 y en punto 3
sólo el campo Descripción (debo consultar si debe estirar de alguna parte o deben ser
campos libres)"*.

| Punto | Estado |
|-------|--------|
| 1 · Pestaña Compartimientos con el orden y cálculo de v12 | ✅ resuelto |
| 2 · Pestaña Precintos igual a la de v12 | ❌ **falta** |
| 3 · Pestaña Patrones Utilizados | 🟡 falta sólo el campo **Descripción** — y está pendiente de definición si es libre o parametrizado |
| 4 · Campo Comentarios visible en borrador | ✅ resuelto |

Es el ítem más cerca de cerrarse de todo el Frente 2. El punto 2 tiene además una
nota de Luz de abril: *"El de la V18 no entendí su funcionamiento, podemos revisar
antes de que cambies"* — conviene una pasada juntos antes de tocarlo.

### 2.8 · ⛔ Bloqueo de QA en el portal — prioridad sobre el resto del Frente 2

**Es el hallazgo más importante del barrido.** INTN no puede validar *nada* del
sprint #3 porque no logra enviar una solicitud desde el portal. El mismo síntoma
aparece reportado de forma independiente en cuatro tarjetas distintas, lo que
explica por qué tantas quedaron "esperando pruebas" durante semanas:

| Tarjeta | Reporte | Fecha |
|---------|---------|-------|
| `86e24j2kq` Validación de calendario | *"No es posible continuar con las pruebas, los problemas en la base persisten. El sistema carga datos por defecto; logro cambiar organismo y departamento, pero después no permite seleccionar el vehículo"* — con video | 21/07 |
| `86e26ndkn` Restricción de agendamiento | *"No puedo probar porque no puedo enviar la solicitud"* | 19/07 |
| `86e2dqw56` Pruebas en general | *"En cualquier tipo de servicio, al querer enviar la solicitud no permite a pesar de que todos los datos estén ingresados"* — pide el tipo de transporte y el producto a transportar como si estuvieran vacíos | 20/07 |
| `86e2hcgbn` Pruebas 28/07 | Los camiones con Verificación Inicial confirmada no aparecen para los demás procesos; **todas** las fechas del calendario se muestran deshabilitadas | 28/07 |

- [ ] Reproducir el envío de solicitud desde el portal con un usuario cliente real
- [ ] Revisar por qué el desplegable de vehículo queda vacío tras cambiar
      organismo/departamento
- [ ] Revisar por qué el calendario marca todas las fechas como ocupadas
- [ ] Recién después, pedir a INTN que retome las pruebas

> **Nota.** Al momento de escribir esto el árbol de trabajo tiene cambios sin
> commitear en 24 archivos que tocan exactamente este camino
> (`service_request_fleet_portal_create.py`, `fleet_portal_widgets.js`,
> `cistern_create_handlers.py`, `portal_fleet_form_views.xml`). Conviene confirmar
> si ese trabajo en curso ya cubre el bloqueo antes de abrir tarjeta nueva.

### 2.9 · Formularios de Picos — "implementado" contra observaciones abiertas

El 28/07 se comentó en `86e204nrm` y `86e2054g6` que los formularios de Aprobación
de Modelo y de Recepción ya estaban implementados. **Las dos tarjetas de
observaciones asociadas dicen otra cosa** y no se habían leído:

- [ ] `86e243ewk` Observaciones · Aprobación de Modelo — Luz el 21/07 deja **cuatro
      puntos sin resolver**: agrupar Valor Inicial / Valor Máximo / Unidades bajo el
      título *Rango de Funcionamiento*; mover los campos de carga de archivos a la
      pestaña Adjuntos y pasar Nota de Compromiso a opcional; agregar el campo
      **Número de VUI**; agregar el botón **Agregar Instrumento** para varios
      instrumentos por solicitud. Más una consulta sin responder: *"¿está
      parametrizada la descarga de requisitos? ¿dónde lo encuentro?"*
- [ ] `86e243m92` Observaciones · Verificación Visual — cuatro puntos abiertos:
      quitar el campo Fecha del portal y tomarlo de la creación de la solicitud;
      Ciudad debe filtrarse por Departamento; Marca/Modelo/Fabricación necesitan
      catálogos propios, distintos de los de Cisternas; agrupar bajo *Rango de
      Funcionamiento*. Hay además una pregunta del Equipo de Desarrollo del 09/07
      sin contestar: si de verdad hay que eliminar el campo Fecha, dado que se usa
      para el agendamiento

**Conclusión:** el "implementado" del 28/07 se apoyó en el código, no en las
observaciones. Estas dos tarjetas son alcance real pendiente, chico pero concreto.

### 2.10 · Bloqueos por definición pendiente — cero desarrollo

Salió de las tandas A–C del barrido (sprints #3 a #12). **Siete tarjetas están
detenidas esperando que alguien conteste una pregunta, no esperando código.** Varias
llevan dos meses así, con la pregunta escrita en la tarjeta y sin respuesta.

| Tarjeta | Pregunta abierta | Desde |
|---------|------------------|-------|
| `86e0yxqwc` RF 5.15 tablas de reportes METCI | Equipo de Desarrollo: *"¿podrías mejorar esta descripción? le di 3 releídas y sigo confundido… no tengo claro qué variables quieren ni qué cálculos"* | 02/06 |
| `86e0yxqwu` RF 5.17 reportes METCI | Felix: *"¿hay detalle de las observaciones?"* | 30/05 |
| `86e0yxr79` RF 10.1 bloqueo de fechas | Equipo de Desarrollo: *"es un poco grande esta funcionalidad, ¿dónde lo tenés pensado poner, o lo dejo a mi criterio?"*. La HU incluye reagendamiento automático con estado propio y notificación al cliente | 22/06 |
| `86e0yxqmz` RF 4.5 formato de factura | Felix: *"necesitamos una validación directa con el cliente para el nuevo formato de factura. Caso contrario no podremos avanzar"* | 29/04 |
| `86e0yxqtd` RF 4.3 cierre de caja | INTN pide varias sesiones simultáneas; se advirtió el riesgo contable y de auditoría y quedó en *"si lo quieren de esa forma, ellos son responsables"*. **Decisión de negocio, no técnica** | 25/05 |
| `86e0yxquv` RF 2.11 facturas vencidas | La regla pedida no distingue "vence hoy" de "vencida". Se pidió el detalle del comportamiento esperado | 04/06 |
| `86e0yxqtq` RF 3.5 variación de campos | Se propuso pasarla a *wont do*: con un DoD claro alcanza con marcar el campo obligatorio. Sin respuesta | 14/05 |

- [ ] Llevar las siete juntas a la próxima reunión — es una sola conversación, no siete
- [ ] Registrar la respuesta en cada tarjeta antes de estimar nada

### 2.11 · Observaciones abiertas en tarjetas "Listo para pruebas" (tandas A–C)

Se suman a las seis de 2.5. Mismo patrón: la tarjeta figura terminada y tiene una
observación de INTN sin contestar.

- [ ] `86e1fvep0` Migrar Inspección de Tanque Cisterna — **el hallazgo más serio del
      grupo.** Luz Lezcano el 28/05: *"Los reportes que se migraron para Inspección de
      Tanques y Certificado de Inspección no son correctos. Descarga totalmente otro
      documento no relacionado. Los reportes que aparecen en la v12 son vigentes y los
      clientes reciben en el portal dichos certificados."* Nunca se respondió, y el
      28/07 la tarjeta se marcó como implementada contra el código
- [ ] `86e0yxqve` RF 5.22 revisión de documentación — de cuatro observaciones quedan
      dos: los adjuntos rechazados siguen apareciendo junto a los nuevos, y al
      confirmar el certificado de Inspección la solicitud pasa a Finalizado y
      desaparecen los botones de los demás procesos. Ambas necesitan reproducción en UI
- [ ] `86e0yxqw0` RF 5.6 reportes OIAT — el campo Nombre muestra la sigla en vez del
      nombre completo del departamento, y la pestaña "Descripciones Adicionales" quedó
      bajo permisos de OIAT cuando corresponde a COSTOS (11/06)
- [ ] `86e0yxqu6` RF 4.6 pago/crédito/cancelación — el comprobante cargado en PDF no
      se puede visualizar desde el backoffice; sólo funciona con imagen (06/06). Va de
      la mano con `86e0yxquy` RF 4.4, que el propio equipo marcó como vinculada
- [ ] `86e1hn8bm` Portal ONC — Luz dejó comentarios en un PDF, preguntó por qué el
      Tipo de Solicitud ofrece la opción ONN (otro organismo, sin procesos en común) y
      pidió migrar todos los procesos de v12 de Trazabilidad de Uso de Marca (03/06)

### 2.12 · Avance real no registrado en el tablero

Trabajo de Kath Groos y Luis Recalde documentado con capturas en la tarjeta, sobre
tarjetas que el tablero marca `Pendiente`:

- [ ] `86e18pgn0` RF 5.9 Informe de Muestreo ONI — módulo hecho, con formulario
      dinámico por tipo de informe (Muestreo / No Intervención), estados
      Borrador→Aprobado→Confirmado, numeración al confirmar y PDF con título dinámico.
      **Pendiente:** que Descripción, Abreviaturas y Notas sean formateables por los
      usuarios de ONI
- [ ] `86e1fy9c2` Portal OIAT — formulario con jerarquía en cascada, tipos de muestra
      parametrizables desde Manufactura → Configuración, campo "Otros" condicional y
      grilla multi-servicio. Genera orden de venta. **Pendiente:** la HU del 20/07 que
      pide valor numérico + selector de unidad de medida (`product.uom`)
- [ ] `86e1fxawe` Portal METCI — en desarrollo. Último reporte del 22/07: *"Pendiente:
      revisar el error que sale al momento de enviar la solicitud"* — **es el mismo
      bloqueo del 2.8**. Además quedó sin resolver el escenario 2 que planteó Luz:
      volver a Seleccionar Categoría tras "Agregar Servicio", para cargar productos de
      distintas categorías en una misma solicitud
- [ ] `86e1fy9ft` Portal ONI — la tarjeta no tiene **ningún** comentario, pero existen
      7 módulos `intn_portal_oni_*` en la rama. Revisar qué cubre cada uno

### 2.13 · Defectos con tarjeta propia, sin atender

- [ ] `86e1c6c40` Reporte de Notas de Crédito con facturas origen — Luz el 09/05: hay
      campos que quedan vacíos o recortados y *"queda inutilizable dicho reporte"*. Es
      un reporte que INTN usa hoy. Sin respuesta
- [ ] `86e1awy4h` Reporte de bugs — Luis Recalde el 12/05: se pueden crear dos órdenes
      de servicio con la misma fecha y hora mientras están en borrador
- [ ] `86e0yxqzp` RF 5.1 Constancias OIAT — **alcance especificado y sin código.** La
      HU del 07/06 es precisa: submenú Constancias en Manufactura → Operaciones → OIAT,
      modelo `oiat.constancia`, campos que se estiran de la orden de venta, cuerpo
      editable inicializado con la plantilla base y PDF fiel al Word actual

### 2.14 · Módulo de reportes `86e1ecqer` — la épica que quedó a medias

En mayo se definió una estrategia por olas para migrar los ~38 reportes de v12, con
rama de integración `18.0-report-migration`. **Sólo la ola A y la B llegaron a la
rama.** Verificado contra los manifiestos:

| Ola | Módulo previsto | En `18.0` |
|-----|-----------------|-----------|
| A · flota cisterna, MRP ONI/OIAT, certificados | varios | ✅ |
| B · listados de organismos | `intn_organization_reports` | ✅ |
| C · trazabilidad de marca | `intn_trademark_traceability_reports` | ❌ |
| D · contabilidad | `intn_accounting_reports` | ❌ |
| E · flota institucional, stock, cisterna legacy | `intn_institutional_fleet_reports`, `intn_stock_reports`, `intn_fleet_cistern_legacy_reports` | ❌ |
| parcial · metrología | `intn_metrology_reports` | ❌ |

- [ ] Convertir `86e1ecqer` en épica y colgarle las tarjetas de reporte, como se
      propuso el 14/05 y quedó sin hacer
- [ ] Decidir las cinco definiciones que el propio comentario dejó abiertas
      (`factura_autoimpresor`, ola B wizard único vs cuatro módulos,
      `multa_verificacion` vs `intn_fleet_cistern_fines`, metrología, nombre de trazabilidad)

---

## Frente 3 · Integridad documental · `86e2cbzpj`

**Máxima prioridad técnica.** Único hallazgo con riesgo real sobre documentos que
INTN entrega a clientes.

### Diagnóstico

Los certificados y registros de verificación leen los datos del vehículo mediante
campos `related` **no almacenados**:

| Archivo | Líneas |
|---------|--------|
| `intn_fleet_cistern_verification/models/measurement_record.py` | 112–160 |
| `.../tank_inspection_certificate.py` | 63–82 |
| `.../tank_inspection.py` | 90–110 |
| `.../hydrostatic_test.py` | 155–218 |
| `.../visual_verification.py` | 243–296 |

Dos consecuencias:

1. **Cambiar el emblema, la chapa o el propietario de un camión reescribe todos los
   certificados ya emitidos.** Es exactamente lo reportado el 12/07.
2. En `measurement_record.py` esos `related` están declarados **`readonly=False`**:
   un técnico que corrige la chapa dentro de un Registro de Medición **escribe sobre
   la ficha maestra del vehículo**, sin advertencia.

### Hallazgo que cambió el diseño

El certificado **no leía los campos `related`**: el reporte QWeb recorría
`s.vehicle_id.*` y `s.partner_id.*` en vivo. Congelar los `related` de
`measurement_record` no habría arreglado nada. El congelado tenía que vivir en
`certificate.management`, que es el modelo del reporte.

### Trabajo hecho

- [x] Campos de snapshot en `intn_fleet_cistern_certificates` — 13 columnas
      (`issued_license_plate`, `issued_emblem_name`, `issued_partner_vat`, …),
      derivadas de lo que el reporte realmente imprime
- [x] Captura en borrador y **congelado al confirmar**:
      `_intn_refresh_issued_snapshot()` sólo escribe si `state == "draft"`, y
      `action_confirm()` la invoca antes del `super()`
- [x] Identidad del tanque resuelta vía `_intn_tank_holder()` — una tractora lleva
      el tanque en el acoplado, leer `vehicle_id.cistern_*` daría vacío
- [x] Reporte reescrito para leer `_intn_certificate_display_values()`, con
      *fallback* a los datos vivos para certificados sin snapshot
- [x] Migración `18.0.1.3.0` que rellena los certificados existentes
- [x] Escritura inversa cortada: 16 campos `related` de `measurement_record`
      (9 de vehículo + 6 de acoplado + compartimientos) pasaron a `readonly=True`.
      Antes, corregir la chapa en un Registro de Medición reescribía la ficha
      maestra del vehículo
- [x] Verificado de punta a punta sobre `intn_demo`

### Verificación

Confirmado un certificado, se cambió emblema, chapa, razón social y RUC:

```
vehiculo hoy     -> chapa: F3-ZZZ-999 | emblema: EMBLEMA B
certificado dice -> chapa: F3-AAA-111 | emblema: EMBLEMA A
cliente hoy      -> Transportes Nuevo Dueno SA 80077732-2
certificado dice -> Transportes Viejo Dueno SA 80077731-4
el REPORTE imprime -> chapa: F3-AAA-111 | emblema: EMBLEMA A
```

Suites: `intn_fleet_cistern_certificates` 0/11, `intn_certificate_management` 0/9,
`intn_documents` 4 fallos idénticos al baseline.

### Limitación a comunicar

Los certificados **ya confirmados antes de la migración** no tienen forma de
recuperar sus valores originales: nunca se persistieron. La migración los rellena
con los datos de hoy, lo que corta el sangrado hacia adelante pero no deshace las
alteraciones ya ocurridas. Deben leerse como "exactos a la fecha de migración",
no a su fecha de emisión.

### Pendiente relacionado, fuera de alcance

`measurement_record` tiene además `partner_street`, `partner_city`,
`partner_city_id` y `partner_state_id` como `related` a `partner_id` con
`readonly=False`: editarlos reescribe el contacto. No afecta la integridad del
certificado (que ahora congela la dirección), pero es la misma clase de mutación
silenciosa de datos maestros. Queda a criterio de negocio si es deseado.

---

## Frente 4 · Defectos acotados

### 4.1 · F2 — Guard de certificado válido demasiado amplio

`intn_portal_fleet_requests/models/fleet_vehicle_service_request.py:523-560` bloquea
toda solicitud que no sea Habilitación si el activo no tiene certificado en estado
`done`. Se dispara en `create` y en `action_confirm`.

- [x] Acotar el guard para que no aplique a `certificate_modification`
- [x] Confirmar que los 5 tests de `TestCertificateModificationAutofill` pasan a verde
- [x] Verificado sin regresión: baseline 24 failed / **39** errors → con el cambio
      24 failed / **34** errors sobre 166 tests. Arregla los 5, no rompe nada

**No era un test desactualizado: era un bloqueo circular.** Guardar un cambio de
propietario dispara `_cancel_done_certificates_on_ownership_change()`
(`intn_fleet_cistern/models/fleet_vehicle.py:1118`), que cancela los certificados
`done`. Acto seguido el guard exigía un certificado `done` para pedir
`certificate_modification` — que es justamente el trámite con el que se actualiza
el certificado tras el cambio de RUC. El cliente quedaba sin salida.

La exención quedó en la constante `SERVICE_TYPES_WITHOUT_CERTIFICATE_PRECONDITION`
junto a `enabling`, con el porqué documentado en el docstring para que nadie lo
"corrija" de vuelta.

### 4.2 · F4 — Tests de derivación de OT que nunca corrieron

`intn_mrp_workorder_forwarding/tests/` no tiene `__init__.py`, así que Odoo nunca
descubrió sus 13 casos. Al habilitarlos, 11 erran por una causa compartida:
`generate_mo()` de Odoo 18 arma la LdM sin operaciones, de modo que la orden nace sin
órdenes de trabajo.

- [x] Reescribir el helper para que la LdM lleve operaciones sobre `workcenter_1`
      (`_make_mo_with_operation`), con stock del componente y `action_assign()`:
      un work order sólo llega a `ready` con `production_availability = assigned`
- [x] Agregar `__init__.py`
- [x] **11 de 11 en verde** (el módulo tiene 11 casos, no 13)

Al habilitarlos aparecieron dos fallos más allá del helper, con causas distintas:

- **Bug real de producción.** `is_forwarded_receiver` se computa a partir de
  `self.env.user` pero no declaraba `@api.depends_context("uid")`. Odoo cachea el
  valor del primer lector y se lo sirve a todos los demás del mismo worker: dos
  usuarios distintos veían el mismo resultado. Verificado quitando y reponiendo el
  decorador — sin él el test falla, con él pasa
- **Bug del test.** Usaba `self.env.user` como usuario permitido, que en un
  `TransactionCase` es OdooBot (id 1) y está **archivado**. Un registro archivado se
  filtra al releer el many2many, así que la lista quedaba vacía y el guard de
  `button_start` nunca se disparaba. Corregido a `base.user_admin`, con aserción
  explícita para que no vuelva a pasar silenciosamente

### 4.3 · F5 y varios

- [x] **Reglas de acceso de `service.request.portal.form.layout` — ya estaban.** El
      ítem quedó obsoleto: `intn_service_request/security/ir.model.access.csv` las
      declara (líneas 10–11) desde el commit `6abb2b35`, y la advertencia ya no
      aparece al cargar módulos. Verificado sobre `intn_demo`
- [x] **Bug de `qty_done` corregido** en `brand_voucher.py` y
      `brand_label_print_job.py`. El campo no existe en Odoo 18: se dividió en
      `quantity` + `picked`. Confirmado contra el registro del modelo
      (`qty_done -> NO existe`). Ambas creaciones de `stock.move.line` habrían
      reventado al validar el picking. Suite de `intn_brand_service_requests`:
      1 fallo de 68, el preexistente `test_portal_brand_pages_and_pdf_download`
- [x] **Los tests ya no generan PDF.** Regla cambiada y aplicada en todo el repo

#### Nueva regla de testeo de reportes

Decisión: **ningún test genera PDF**. Se valida el contenido del QWeb en HTML; si el
HTML sale correcto, en producción el PDF sale bien.

`AGENTS.md` quedó actualizado con la regla y el porqué. Antes exigía smoke tests
HTML **y** PDF con `force_report_rendering=True`, en contradicción con
`pendientes-tecnicos.md` §4. Ahora exige:

- `_render_qweb_html` + aserciones sobre el **contenido** renderizado
- `report_type == "qweb-pdf"`, que cubre que la acción esté cableada para PDF
- Rutas de portal: `HttpCase` contra `report_type=html` (200 + `text/html`)
- Prohibido `_render_qweb_pdf`, `force_report_rendering=True` y aserciones `%PDF`
- Mockear `_render_qweb_pdf` sigue permitido: nunca invoca el binario

**Causa raíz documentada.** Dos hipótesis descartadas con evidencia: el binario
funciona (`wkhtmltopdf 0.12.6.1`, 0,26 s en HTML trivial) y `web.base.url` es
alcanzable (0,89 s). La pista real salió en la suite de marcas —
`Exit with code 1 due to network error: ContentNotFoundError` —: wkhtmltopdf
resuelve las URLs absolutas del template contra `web.base.url`, es decir contra la
instancia de Odoo que corre aparte, que no ve los registros de la transacción del
test. De ahí el 404 en un caso y la espera larga en el otro.

Archivos convertidos (7 tests, 9 bloques):

| Archivo | Cambio |
|---------|--------|
| `intn_brand_service_requests/tests/test_brand_report_rendering.py` | helper `_assert_report_renders` a HTML + contenido |
| `intn_brand_service_requests/tests/test_portal_brand_requests.py` | ruta de portal a `report_type=html` |
| `intn_fleet_cistern_certificates/tests/test_onm_measurement.py` | HTML + verifica que el certificado imprima la chapa del vehículo |
| `intn_fleet_cistern_verification/tests/test_onm_visual.py` | HTML + verifica el motivo de rechazo en el documento |
| `intn_mrp_dse/tests/test_report_rendering.py` | el test de PDF pasó a verificar el tipo de acción |
| `intn_portal_metrology_dispenser_requests/tests/test_model_approval_reports.py` | 2 bloques |
| `intn_portal_metrology_dispenser_requests/tests/test_initial_verification_habilitation.py` | 1 bloque |

Verificado: `intn_fleet_cistern_certificates` 0/11, `intn_mrp_dse` 0/3,
`intn_onm_measurement` 0/8. No queda ninguna llamada real a `_render_qweb_pdf` ni
ninguna ruta pidiendo `report_type=pdf` en tests.

### 4.4 · No hacer ahora

- Alturas de compartimiento con nombres invertidos en `compartment_dimension.py`.
  El cálculo es correcto; sólo confunde a quien lee el código. Arreglarlo toca 12
  archivos en 4 módulos e incluye reportes QWeb, con beneficio funcional cero.

---

## Frente 5 · Dependencias externas (Bloque D)

Cuatro tarjetas paradas ~3 meses. **Tres de ellas no necesitan desarrollo: necesitan
que alguien cargue un parámetro.** Eso es lo que hay que llevar a la reunión.

| Tarjeta | Nuestro lado | Qué falta del otro lado | Sin novedad desde |
|---------|--------------|--------------------------|-------------------|
| SIFEN `86e184aww` `86e0yxqzb` | `l10n_py_edi_segel` (account_move, res_company, ajustes) | Entorno de pruebas habilitado por SIFEN. El código v12 sólo trae llaves de **producción**. Y aclarar si `192.168.0.229:8080/fcws/factura` apunta a producción | 05/05/2026 |
| MITIC `86e0yxqmf` | `intn_portal_hybrid_auth` **terminado** | Accesos y documentación | 20/04/2026 |
| DNIT — consulta RUC `86e0yxqp3` | `intn.ruc.service` **terminado** | URL del servicio | 20/04/2026 |
| DNIT — validación de factura `86e0yxqtv` | **No hay código** | — | sin comentarios |

### El argumento para la reunión

**MITIC ya está listo y esperando seis parámetros.** `intn_portal_hybrid_auth`
define `mitic_provider_enabled`, `mitic_client_id`, `mitic_auth_endpoint`,
`mitic_validation_endpoint`, `mitic_data_endpoint` y `mitic_scope`, más
`identity_validation_service.py` y los adapters OAuth. En cuanto lleguen los
accesos, es configuración, no desarrollo.

**La consulta de RUC igual.** `intn.ruc.service` tiene `fetch_ruc_data()`,
sincronización de sucursales y los parámetros `ruc_service_base_url`,
`ruc_service_timeout`, `ruc_integration_enabled` y
`ruc_sync_establishments_enabled`. Falta la URL.

**SIFEN es el único con riesgo técnico real**, porque sin sandbox no se puede
probar el flujo sin emitir documentos fiscales de verdad.

### ⚠️ Corrección al inventario de módulos

`intn_account_dnit_validation` **no es un módulo**. El directorio existe en disco
pero sólo contiene `__pycache__`: no tiene `__manifest__.py`, ni `__init__.py`, ni
un solo archivo fuente, y **no está trackeado por git**. Los `.pyc` delatan que
alguna vez tuvo `account_move.py`, `dnit_validation_service.py` y
`res_config_settings.py`, pero eso nunca llegó a la rama.

Consecuencia: **RF 4.2 (validación de RUC contra DNIT antes de facturar) no tiene
código en el repositorio.** No está bloqueada por terceros — está sin empezar, y
su estado `Trancado` sin comentarios lo venía ocultando. Conviene además borrar el
directorio huérfano para que no aparezca en futuros relevamientos.

### RF 4.2 — Validación DNIT al facturar ✅ IMPLEMENTADO

Resultó mucho más chico de lo que parecía: **el servicio de consulta ya existía**.
`intn.ruc.service.fetch_ruc_data()` en `intn_portal_registration` consulta el RUC y
devuelve la razón social. Faltaba engancharlo a la facturación.

Módulo nuevo `intn_accounting/intn_account_dnit_validation` (se borró antes el
directorio huérfano del mismo nombre, que sólo tenía `__pycache__` y no estaba
trackeado):

- Guard en `account.move.action_post()`, sólo para facturas y notas de crédito
  de cliente
- Tres modos configurables desde Contabilidad: `off`, `warn` (nota en el chatter)
  y `block` (impide postear)
- **Comparación normalizada de razón social**: sin acentos, sin puntuación y sin
  formas jurídicas. Sin eso, `Logística Sur S.A.` contra
  `LOGISTICA SUR SOCIEDAD ANONIMA` marcaría discrepancia en casi todos los
  clientes y la validación sería inusable

**Degrada en silencio a propósito.** Si la integración está apagada, sin URL, o el
servicio no responde, la factura se postea igual. Un servicio externo caído no
puede dejar al INTN sin poder facturar; el pedido dice validar contra DNIT, no
depender de DNIT para cobrar.

**Por defecto queda en `warn`, no en `block`.** El RF pide bloquear, pero activarlo
antes de medir la tasa de coincidencia contra datos reales de DNIT frenaría la
facturación ante cualquier diferencia inocua de escritura. La recomendación es
pasar a `block` cuando las notas muestren que la comparación está limpia.

Verificado:

```
'Logística Sur S.A.'     vs 'LOGISTICA SUR SOCIEDAD ANONIMA' -> coincide
'Transportes Uno S.R.L.' vs 'TRANSPORTES UNO SRL'            -> coincide
'Empresa A'              vs 'Empresa B'                      -> DIFIERE

DNIT sin configurar  -> no interfiere
DNIT caído           -> no bloquea la facturación
nombre distinto/warn -> nota en el chatter, postea
nombre distinto/block-> bloqueado, con ambos nombres en el mensaje
nombre coincidente   -> postea (estado: posted)
```

Suites `intn_documents` e `intn_service_request`: iguales al baseline.

### Pasos

- [ ] Mover SIFEN, MITIC y consulta-RUC a `Bloqueado — dependencia externa`, con
      responsable INTN y fecha de compromiso
- [x] **RF 4.2 sacado de ese grupo**: no era bloqueo externo sino desarrollo
      pendiente, y ya está hecho. Queda esperando la URL del servicio para
      activarse, igual que la consulta de RUC del portal
- [x] Borrado el directorio huérfano `intn_account_dnit_validation` y creado el
      módulo de verdad
- [ ] Escalar en la reunión con acta

---

## Frente 6 · Brechas de alcance (Bloque E)

Es una conversación de alcance, no una tarea. Excluida la app móvil, queda sin código:

| Alcance | Tarjetas | Situación |
|---------|----------|-----------|
| Básculas (RF 9.x, RF 10.x) | ~15 | Sin módulo. Sprint #8 venció el 19/06 |
| Inventarios (RF 7.x) | ~13 | Sin módulos propios — puede ser parametrización de `stock` |
| Calendario transversal (RF 10.1/10.2, RF 11.x) | ~7 | Sólo existe agenda de cisternas |
| Proyectos / básculas (RF 15.x) | 5 | Sin código |
| Portal METCI | 1 | En desarrollo fuera de rama, con error al enviar |
| RF 11.1 validación pública por QR | 1 | **Sprint actual.** Sólo cubierto para marcas |
| RF 13 picos de surtidores | 4 | Existen 19 modelos — requiere auditoría RF por RF |

### Auditoría RF 13 — Picos de surtidores (sprint #10, venció 17/07)

Hecha contra `intn_portal_metrology_dispenser_requests` (19 modelos, 2 994 líneas).
**No colapsa como esperaba**: 2 parciales y 3 sin empezar.

| RF | Estado | Evidencia |
|----|--------|-----------|
| 13.1 — ID de surtidor asignado por el sistema, identificador histórico entre intervenciones | ✅ **Implementado** | Ver abajo. Antes sólo había `serial_number` cargado a mano, sin identidad persistente |
| 13.2 — Interfaz de carga de datos técnicos por ONM + cálculo automático de resultados | 🟡 **Parcial, bloqueado por definición** | La interfaz existe y es rica: `metrology_dispenser_technical_verification` con checklist, pruebas por pico (volumen a caudal mín/máx, error máximo, longitud de manguera, descarga residual) y estados de precintos. **Falta el cálculo automático**: el único compute del modelo es `_compute_nozzle_count`. Ver la búsqueda de la fórmula más abajo |
| 13.3 — Estado final Aprobado / Reprobado / **Imposibilidad** | ✅ **Implementado** | Ver abajo. Antes existían sólo `approved` y `rejected` |
| 13.4 — Observaciones del cliente en 48 h y cierre automático | ✅ **Implementado** | Backend + autogestión en el portal. Ver abajo |
| 13.5 — Coordenadas GPS del pico | ✅ **Implementado** | Ver abajo. Antes sólo había GPS a nivel de sucursal |

Esfuerzo estimado: 13.3 y 13.5 son chicos (≈1 día cada uno, y 13.5 reutiliza el
widget que ya existe). 13.1 es un modelo + secuencia + backfill (1–2 días). 13.4
son 1–2 días. **13.2 no está bloqueado por desarrollo sino por definición**: hace
falta la fórmula de evaluación del ONM.

### RF 13.3 — Imposibilidad en metrología ✅ IMPLEMENTADO

En `intn_portal_metrology_dispenser_requests`:

- `evaluation_result` gana `impossibility`, más un campo `impossibility_reason`
  visible y obligatorio sólo cuando se elige esa opción
- `metrology_execution_state` gana `impossibility`, para que la solicitud refleje
  el desenlace y no lo disfrace de rechazo
- `action_confirm_evaluation()` reestructurado: **con imposibilidad no se exige
  checklist ni pruebas de picos**, sólo el motivo. Exigir mediciones completas de
  un servicio que no se pudo realizar era contradictorio. Es el mismo criterio que
  ya usa la verificación visual de cisternas (`is_impossibility` salta el
  checklist), así que los dos organismos se comportan igual
- Nueva **Constancia de No Realización de Servicio**
  (`action_report_metrology_technical_impossibility`), que reutiliza los bloques
  del layout y omite a propósito checklist y picos: no hay mediciones que informar,
  sólo el motivo. Antes, una imposibilidad habría emitido un PDF titulado "Informe
  Técnico de Rechazo", que dice algo distinto de lo ocurrido
- El mapeo resultado → reporte pasó a una tabla `_EVALUATION_REPORTS`, en lugar de
  dos `if/else` paralelos que había que recordar mantener sincronizados

Verificado:

```
approved      -> action_report_metrology_model_approval_certificate
rejected      -> action_report_metrology_technical_rejection
impossibility -> action_report_metrology_technical_impossibility

sin motivo -> bloqueado: "The impossibility reason is required."
con motivo -> confirmado; estado del servicio: impossibility
              (checklist y picos vacíos, no los exigió)
```

Suite `intn_portal_metrology_dispenser_requests`: 6 fallos, los mismos del
baseline.

### RF 13.5 — Coordenadas GPS del surtidor ✅ IMPLEMENTADO

`gps_latitude` / `gps_longitude` en `service.request.line`, más un `gps_map_url`
calculado que abre la posición en OpenStreetMap.

**Van en la línea, no en la solicitud**: una estación puede tener varios surtidores
separados por metros, y el sentido de registrarlos es volver a encontrar esa unidad
en una intervención posterior. Opcionales por diseño — el RF pide "la *opción* de
contar con coordenadas".

No se reutilizó el `partner_map_picker`: no es un widget de campo genérico sino un
diálogo atado a `res.partner`, así que engancharlo acá habría costado más que el
enlace al mapa. Queda como mejora si la usabilidad lo pide.

Validaciones verificadas:

```
solo latitud       -> bloqueado: "Latitude and longitude must be filled together…"
lat fuera de rango -> bloqueado: "Latitude must be between -90 and 90 degrees."
lon fuera de rango -> bloqueado: "Longitude must be between -180 and 180 degrees."
caso valido        -> -25.26374 / -57.575926 + enlace a mapa
sin coordenadas    -> permitido (el campo es opcional)
```

Suites: metrología 6 fallos y `intn_service_request` 1 fallo + 14 errores, ambos
idénticos al baseline verificado con *stash*.

### RF 13.1 — ID histórico del surtidor ✅ IMPLEMENTADO

**El problema no era un campo faltante sino una entidad faltante.** Un surtidor
sólo existía descrito en línea dentro de cada solicitud, así que dos intervenciones
sobre la misma máquina no tenían nada que las vinculara. Un simple código en la
línea no habría alcanzado: hay que poder volver a encontrar el mismo surtidor.

Nuevo modelo `metrology.dispenser`, el equivalente de `fleet.vehicle` para
cisternas:

- `name` = ID INTN de secuencia (`SUR/00001`), asignado una sola vez
- `serial_number` normalizado (trim + mayúsculas) y **único**, con mensaje que
  remite al registro existente en vez de un error críptico
- Marca, modelo, fabricante, cantidad de picos, propietario, GPS
- `line_ids` con el historial de intervenciones y un botón de estadística

En `service.request.line`, un `dispenser_id` que apunta al registro.

**Asignación en `action_confirm_evaluation()` de la Verificación Inicial, con
cualquier resultado, no sólo aprobado.** La máquina existe físicamente igual, y
una unidad rechazada que vuelve para un segundo intento tiene que caer en el mismo
identificador — que es justamente para lo que sirve tenerlo. Las líneas ya
vinculadas se saltan, así que reconfirmar nunca vuelve a registrar nada.

Verificado:

```
1ra intervencion  -> ID SUR/00001, serie '  sn-abc-123  ' normalizada a 'SN-ABC-123'
2da intervencion  -> serie 'Sn-Abc-123' -> mismo registro SUR/00001
                     contador de intervenciones: 2
serie duplicada   -> bloqueado: "Serial SN-ABC-123 already belongs to dispenser SUR/00001…"
```

Suites: metrología 6 fallos e `intn_service_request` 1 + 14, ambos idénticos al
baseline.

**Pendiente menor:** hoy la vinculación automática ocurre en la Verificación
Inicial. Para servicios posteriores (periódica, subsecuente) el surtidor se puede
elegir a mano desde la línea; automatizar también ese enganche por número de serie
es un agregado chico si la operación lo pide.

### RF 13.4 — Ventana de observaciones de 48 h ✅ IMPLEMENTADO

- La ventana **se abre en la entrega**, al confirmar la evaluación técnica, que es
  cuando el cliente recibe su documento
- `observation_deadline` se **almacena**, no se calcula al vuelo: si mañana alguien
  cambia el parámetro de 48 h, un servicio ya entregado debe conservar el plazo
  bajo el que se entregó
- Plazo configurable en `intn_metrology.observation_window_hours` (48 por defecto)
- `action_metrology_register_observation()` valida que haya entrega, que no exista
  ya una observación y que el plazo no haya vencido; deja el servicio en
  `observation_review`
- Cron horario `_cron_metrology_close_observation_windows()` que cierra a `done`
  los servicios cuyo plazo venció sin objeciones
- Nuevo estado `observation_review`, y la barra de estados incluye también
  `impossibility` y `done`, que antes no se mostraban

Verificado el ciclo completo:

```
entrega                    -> ventana abierta, vence +48 h exactas
cron antes del vencimiento -> 0 cerradas, servicio sigue en approved
cliente observa a tiempo   -> estado observation_review
segunda observacion        -> bloqueada
plazo vencido sin observar -> cron cierra a done
observar fuera de plazo    -> bloqueado con la fecha exacta
```

#### Autogestión en el portal

Ruta POST `/my/service_request/<id>/metrology/observation` más una sección en la
página de detalle. El controlador sólo verifica acceso y delega: todas las reglas
de plazo viven en el modelo, así que no hay dos lugares donde puedan divergir.

La sección muestra los tres desenlaces posibles: ventana abierta con su fecha de
vencimiento y el formulario, observación ya registrada con su fecha y texto, o
ventana cerrada sin objeciones.

**Probado como cliente real**, no sólo por API: login de portal, carga del detalle,
POST del formulario y recarga.

```
detalle (ventana abierta) -> "puede registrar una observación hasta el 31/07/2026 17:38:05"
POST                      -> 303 -> ?observation=registered
recarga                   -> "Su observación fue registrada"
                             "Observación registrada el 29/07/2026 17:39:23: El totalizador
                              marca 19,7 L cuando se cargaron 20 L."
                             formulario ya no visible
backend                   -> metrology_execution_state = observation_review
```

Suites: metrología 6 e `intn_portal_fleet_requests` 24 + 34, ambos iguales al
baseline. Cron registrado y corriendo cada hora.

### Inventarios RF 7.x — probablemente parametrización, no desarrollo

Es la mayor oportunidad de bajar el alcance sin escribir código. De las 13
tarjetas, la mayoría son funciones nativas de `stock`: almacenes, ubicaciones y
sububicaciones, recepción/transferencia/salida, lote y serie, código de barras,
desecho (`stock.scrap`) e informe de stock por almacén. Lo específico de INTN —
«recepción y control de stock de METCI / Precintados / DVIR / ONC» — es
configuración de almacenes y tipos de operación, más algún pegamento menor.

Conviene validarlo en una sesión de configuración antes de estimarlo como
desarrollo.

### RF 11.1 — Validación pública por QR (sprint #11) ✅ IMPLEMENTADO

**El QR no llevaba a ninguna página de validación.** Codificaba `access_url`, o sea
`/my/certificate/<id>?access_token=…`: el portal privado del cliente. Quien escanea
un certificado impreso —un fiscalizador, un comprador— no es el dueño y no tiene
login, así que el flujo que pide el RF sencillamente no existía.

Implementado en `intn_certificate_management`:

- `verification_url` → `/certificate/verify/<id>/<access_token>`, y el QR ahora
  codifica esa URL en lugar de la del portal. `access_url` queda intacta para el
  portal y los correos
- `_intn_verification_status()` → `valid` / `expired` / `cancelled` / `not_issued`
- Controlador público `controllers/public_verification.py`, con comparación de
  token en tiempo constante (`consteq`) para que el endpoint no sea enumerable.
  Ruta adicional sin token para QR dañados, que responde "no encontrado" en vez
  de 404
- Plantillas: página de verificación con banner de validez, más una página de
  "no encontrado" indistinguible entre token inválido e id inexistente
- Punto de extensión `certificate_verification_extra_rows`, para que cada dominio
  agregue sus filas sin que la página genérica sepa de vehículos ni instrumentos

En `intn_fleet_cistern_certificates`, la extensión de flota que agrega titular,
RUC, chapa, chasis, chapa del tanque y emblema — **todo desde el snapshot del
Frente 3**, nunca del vehículo vivo. Sin ese congelado la página pública habría
mostrado datos que cambian solos.

Verificado con una instancia efímera en un puerto aparte:

```
1) token valido    : HTTP 200  -> banner "Valid" + 12 filas
2) token falso     : HTTP 200  -> "Certificate not found"
3) id inexistente  : HTTP 200  -> "Certificate not found"
4) sin token       : HTTP 200  -> "Certificate not found"

estado done   -> ('valid', 'Valid')
estado cancel -> ('cancelled', 'Cancelled')
estado draft  -> ('not_issued', 'Not issued')
```

Suites: `intn_certificate_management` 0/9, `intn_fleet_cistern_certificates` 0/11,
`intn_documents` 4 fallos idénticos al baseline.

**Pendiente de definición de INTN:** el RF habla de "una url autorizada por INTN".
Hoy la URL sale de `web.base.url`. Si quieren un dominio propio para verificación
pública, es cambiar ese parámetro o agregar uno específico.

### La fórmula del RF 13.2: buscada en v12 y en el relevamiento, no existe

Se rastrearon **cuatro** fuentes antes de dar la definición por faltante:

- **Código fuente v12** (`~/Projects/Appex/intn_repo_viejo`, 76 módulos custom) —
  no hay módulo de picos. Las únicas apariciones de «surtidor» están en los CSV
  del catálogo de servicios, y son verificaciones de **instalaciones de GLP del
  ONI**, sin relación con la verificación metrológica del ONM
- **Base v12** — no hay **ninguna** tabla de picos de surtidores. Se buscó por
  `surt`, `pico`, `eess`, `umle`, `dram`, `aprobacion_modelo` y `modelo`: cero
  resultados. El área nunca estuvo en v12, así que no es una brecha de migración
- **Relevamiento (pizarrón UMLE, «2. Verificación inicial»)** — confirma el
  requisito pero no la matemática: el paso 10 es una caja que dice
  «FORM. DATOS + CÁLCULOS Y EVALUACIÓN DE RESULTADOS». Los pasos 6 («el sistema
  Odoo asigna Id») y 11 («Aprob / Reprob / Imposibilidad») corresponden a los
  RF 13.1 y 13.3, ya implementados
- **Matriz del pliego** — lo declara como desarrollo nuevo: *"Se requiere
  desarrollar formularios para la realización de cálculos (Ensayo + Evaluación de
  Resultados)"*, junto a la nota *"Servicios de laboratorios (No se hará el
  cálculo en Odoo)"*, que conviene aclarar porque parecen contradictorias

**Conclusión:** la tolerancia y la fórmula sólo pueden venir del ONM. Ahora se le
puede hacer una pregunta mucho más precisa (ver abajo).

### ⚠️ Corrección: Básculas **no** es desarrollo desde cero

Lo reporté como «~15 tarjetas sin una línea escrita». Es cierto para el código
v18, pero **v12 tiene el módulo completo y con datos reales**:

| Tabla v12 | Filas | |
|-----------|-------|--|
| `intn_bascula` | 1 219 | el padrón de básculas |
| `desempeno_carga` | 727 | ensayos de desempeño de carga |
| `app_basculas` | 182 | **la app móvil ya existía** (RF 9.4 / 10.12, Segel) |
| `repetitibilidad` | 135 | ensayos de repetibilidad |
| `excentricidad` | 92 | ensayos de excentricidad |
| `certificado_bascula_aprobado` | 50 | certificados emitidos |
| `registro_medicion_basculas` | 12 | 108 columnas |

Son 18 tablas en total. `registro_medicion_basculas` incluye
`resultado_1era_condicion` … `resultado_4ta_condicion` y `resultado_verificacion`:
es decir, **el modelo de cálculo y evaluación de resultados que falta para picos
ya está resuelto en v12 para básculas**.

Conviene separar dos cosas que no valen igual:

- **Los datos sí son un activo real.** 1 219 básculas y ~1 000 registros de
  ensayo existen y hay que migrarlos. Eso cambia el perfil respecto de un
  *greenfield* y hay que reestimarlo antes de la conversación de alcance
- **El código es referencia de forma, no plantilla.** Muestra qué mide el INTN y
  con qué criterio decide, que es lo que no sabíamos. Cómo se implemente en v18 es
  decisión aparte
2. Para el RF 13.2 tenemos ahora un molde concreto. En vez de pedirle al ONM «la
   fórmula» en abstracto, se le puede pedir **la tabla de tolerancias por caudal**
   y proponer modelarla igual que `registro_medicion_basculas`, con condiciones
   evaluadas y un resultado derivado

El código está en `intn_repo_viejo/extra-addons/intn_addons/registro_medicion/`,
método `_compute_condiciones()`: cuatro condiciones sobre promedios y desviaciones,
con tolerancias de ±1 % en la primera y ±3 % con 2σ en las demás. Eso es
exactamente la forma que necesita el RF 13.2, cambiando peso por volumen.

### MITIC: v12 muestra que el servicio existe y qué expone

Reporté MITIC como bloqueado esperando «accesos y documentación». `intn_mitic`
en el repo viejo llama a `{servidor}mbohape-core/sii/security` para obtener token
y a `{servidor}frontend-identificaciones/api/persona/obtenerPersonaPorCedula/{ci}`
para consultar por cédula.

Sirve para **afilar el pedido**: en vez de «necesitamos la documentación del
MITIC», se puede preguntar por servidor, credenciales y si esos endpoints siguen
vigentes.

No sirve como especificación. Aquello es de 2019 y el MITIC pudo cambiar; el
`intn_portal_hybrid_auth` actual está armado sobre OAuth, que es el camino
correcto en v18. **Lo que corresponde confirmar con el MITIC es qué expone hoy**,
no alinear el adapter a lo que exponía en v12.

### Inventarios (RF 7.x): mirar el viejo para entender necesidades

El repo viejo tiene `intn_stock` con `pedido_materiales_equipos.py` y ajustes
sobre `stock_picking`, `stock_picking_type`, `stock_move` y `stock_move_line`.

Vale abrirlo antes de la sesión de inventarios **para saber qué necesidades
operativas cubrían** —el pedido de materiales y equipos, sobre todo—, no para
replicar la implementación. Buena parte de eso puede estar resuelto hoy con
configuración nativa de `stock`.

### Proyectos y Calendario transversal — nada

Verificado por búsqueda en los manifiestos: `project` no aparece en ningún módulo
y `calendar` sólo en los tres de cisternas.

### Lo que entra en la ventana disponible

- [x] Auditar RF 13 — hecho, ver arriba
- [x] RF 11.1 QR público — implementado
- [x] RF 13.1, 13.3, 13.4 y 13.5 — implementados
- [x] RF 4.2 validación DNIT — implementado
- [ ] Sesión de configuración de inventarios para separar parametrización de desarrollo
- [ ] Terminar Portal METCI e integrarlo a la rama (lo lleva Kath Groos)
- [ ] Reestimar Básculas ahora que se sabe que hay migración de datos v12

### Lo que no entra

Básculas (~15), calendario transversal (~7) y proyectos (5). Requieren
replanificación explícita con INTN.

---

## Decisiones pendientes de INTN

1. **Criterio de cierre de tareas** — objeto del Frente 1
2. **Prioridad del Frente 3** sobre trabajo nuevo — integridad de certificados emitidos
3. **Básculas, calendario transversal y proyectos** — se replanifica con fechas
   nuevas o sale de alcance
4. **Reimpresión y litraje** — bloquea el cierre de RF 8.2 (Frente 2.2)
5. **Tabla correlativo → color de etiquetas** — marcada como inferida en el spec del
   RF 6.2; sin los colores cargados no puede confirmarse ninguna entrega en producción
