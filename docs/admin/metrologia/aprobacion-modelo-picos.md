---
nn: "25"
dominio: metrologia
roles: [revisor, funcionario-metrologia]
estado: implementado
---

# Aprobación de modelo y verificación técnica de picos en backoffice

## Para quién es esta guía

- **Revisor documental** — aprueba u observa la documentación presentada. Requiere el grupo de seguridad **Revisor de documentos INTN**.
- **Funcionario de metrología** — ejecuta recepción de muestra, clasificación, verificación técnica y devolución. Requiere el grupo **Usuario de Cisterna**.

## Qué resuelve este proceso

Cubre el backoffice desde que INTN recibe la solicitud del portal hasta la evaluación técnica del surtidor, la emisión del certificado o informe de rechazo, y la devolución de la muestra al cliente.

- **Aprobación de modelo:** el cliente usa el formulario dedicado (sin líneas de equipo). Sus datos aparecen en la pestaña **Model Approval** de la solicitud: tipo de solicitud (aprobación de modelo, homologación, revalidación o complemento de certificado), correo y ciudad del solicitante, datos del fabricante (nombre, dirección, ciudad, país, teléfono, correo), e instrumento (descripción, tipo, marca, modelo, familia de modelo, rango de funcionamiento mínimo/máximo con unidad de medida y cantidad de muestras).
- **Verificación inicial:** el cliente usa el formulario con líneas de equipo; INTN emite una **habilitación temporal** antes de confirmar la solicitud. Sus datos técnicos aparecen en la pestaña **Initial Verification**.

Ambos tipos comparten la misma **cadena de ejecución** con su propia barra de estados operativos, además del estado general de la solicitud.

## Dónde se trabaja

Menú **Camiones Tanque → Operaciones → Solicitudes metrología surtidores**, abriendo la solicitud correspondiente. En la lista, la columna del estado operativo de metrología puede mostrarse u ocultarse.

## Configuración previa

- Usuario interno con los grupos indicados arriba.
- Catálogos de metrología cargados en **Camiones Tanque → Configuración → Metrology**: tipos de instrumento, marcas, modelos, unidades de medida y **reglas de clasificación** (qué área responde por cada tipo de instrumento). Los tipos estándar son: máquina surtidora de combustible líquido, medidor de agua, medidor de energía eléctrica, termómetro clínico y GLP o combinado.

## Antes de empezar

- Cuenta de cliente habilitada y solicitud creada desde el portal. Al crearse, el estado operativo arranca en **Document Review**.
- Para aprobación de modelo, el cliente adjuntó los tres documentos obligatorios: *Prototipo / Muestra*, *Nota de compromiso Aduana* y *Documento vinculante fabricante*.

## Pasos por rol

### Revisor documental

1. Abrir la solicitud que llegó desde el portal, visible en **Camiones Tanque → Operaciones → Solicitudes metrología surtidores**, en borrador (estado operativo **Document Review**).

2. Revisar los adjuntos (y las fichas técnicas por línea, en verificación inicial).

3. Usar **Aprobar documentación**, **Observar** o **Rechazar documentación** según corresponda. Observar y rechazar exigen escribir antes el **Comentario de revisión** y disparan un correo automático al cliente con el comentario y el enlace al portal.

4. Efecto sobre el estado operativo:
   - **Aprobado** → en verificación inicial pasa a *Request Approved*; en aprobación de modelo permanece en *Document Review* (lista para confirmar).
   - **Rechazado** → pasa a *Documentation Rejected*.
   - **Observado** o **Restablecer revisión** → vuelve a *Document Review*.

### Funcionario de metrología

#### Estado 1 — Solicitud recibida

1. Verificar que la revisión documental esté en **Aprobado**.
2. Si es **verificación inicial**, pulsar **Issue Temporary Habilitation** (visible solo con documentación aprobada y sin habilitación previa). El sistema:
   - crea la habilitación con numeración propia y **genera el PDF** ("Habilitación Temporal") automáticamente,
   - registra en el chatter *"Temporary habilitation … issued."*,
   - deja el estado operativo en *Temporary Habilitation Issued*,
   - abre la ficha de la habilitación (fecha de emisión, funcionario emisor y PDF adjunto). Luego puede reabrirse con el botón **Temporary Habilitation**.
   Si la documentación no está aprobada, el botón falla con *"Documentation must be approved before issuing temporary habilitation."*.
3. Pulsar **Confirmar**. Bloqueos posibles:
   - *"Documentation must be approved before confirming the request."*
   - En verificación inicial, *"Temporary habilitation must be issued before confirming the request."*
   - En aprobación de modelo, faltan datos obligatorios del formulario ("… es obligatorio.") o cantidad de muestras menor a 1.
   Al confirmar, el estado operativo pasa a *Request Confirmed* y el presupuesto de venta vinculado se confirma.

#### Estado 2 — Recepción de muestra

1. Con la solicitud confirmada, pulsar **Sample Reception** (visible solo en *Request Confirmed*; si se pulsa antes: *"Request must be confirmed before sample reception."*).
2. Completar el formulario de recepción:
   - **Fecha de recepción** (obligatoria, por defecto hoy) y **funcionario receptor** (por defecto, el usuario actual).
   - **Persona que entrega** (nombre obligatorio; correo y teléfono opcionales).
   - **Cantidad de muestras** (obligatoria; por defecto, la cantidad declarada en aprobación de modelo o el número de líneas en verificación inicial) y **cantidad de picos** (por defecto, la suma de picos de las líneas).
   - Tabla de **números de serie**: debe cargarse exactamente un número de serie por muestra; si no coincide, el sistema bloquea con *"You must register one serial number per sample (X required, Y found)."*. La cantidad de muestras debe ser al menos 1 (*"Sample quantity must be at least 1."*).
   - **Accesorios** y **observaciones** (opcionales).
3. Al guardar, la recepción recibe numeración propia y la solicitud pasa automáticamente a *Sample Received*. Queda un acceso directo **Reception** en la solicitud.

#### Estado 3 — Clasificación técnica

1. Pulsar **Classify** (visible solo en *Sample Received*; si no: *"Sample must be received before classification."*).
2. El sistema determina el tipo de instrumento (en aprobación de modelo, el tipo elegido; en verificación inicial, a partir del texto de la línea) y le asigna el **área responsable** según las reglas de clasificación configuradas.
3. El resultado queda en el grupo **Classification** de la pestaña del trámite: área clasificada, quién clasificó y fecha. El estado operativo pasa a *Technically Classified*.

#### Estado 4 — Verificación técnica

1. Pulsar **Technical Verification** (visible en *Technically Classified*; si no existe verificación y el estado no corresponde: *"Request must be classified before verification."*). El sistema crea la verificación con numeración propia, pasa el estado a *Technical Evaluation* y deja el acceso directo **Verification**.
2. La ficha muestra la identificación del instrumento tomada de la solicitud (instrumento, marca, modelo, fabricante, rango de funcionamiento, números de serie de las muestras recibidas y cantidad de picos). Completar además **fecha de inspección**, **tipo de máquina** (*Dispenser*, *Pump* o *Hybrid*) y **tipo de verificación** (*Annual Periodic*, *Complementary* o *Eventual*).
3. Marcar las casillas de **inspección visual** y **validación documental** (con sus notas si corresponde).
4. Completar el checklist de inspección visual, que se genera automáticamente con **29 ítems numerados** repartidos en tres pestañas: **Physical State** (ítems 6.10 a 6.18: indicador, eliminador de aire/gas, punto de transferencia, llenado del sistema de medición, estado físico, funcionamiento general, marcación, panel indicador, información de componentes), **Control Functionality** (6.19 a 6.30.3: precintado, despacho desatendido, dispositivos auxiliares, indicador de precio, impresora, memoria, predeterminación, CPU, relación de caudales, etc.) y **Mandatory Devices** (6.30.4 a 6.32.1.3: protección de memoria, relaciones de caudal en display, marcas metrológicas, precintado de CPU e inscripciones obligatorias). Cada ítem se marca **Complies / Does Not Comply**.
5. Registrar los ensayos volumétricos en **Volumetric Tests**: el sistema crea automáticamente una fila por pico (según la cantidad registrada en la recepción). Por cada pico: volumen a caudal mínimo y máximo (ml), error máximo (ml), largo de manguera (cm), descarga residual (ml), resultado (*Approved* / *Rejected*), número de marca de verificación y estado de los precintos **P1 Medidor**, **P2 Transductor**, **P3 Placa electrónica** y **P4 Otro** (valores *N* o *R*).
6. Adjuntar planillas de ensayo en la pestaña **Test Sheets** si corresponde.
7. Opcional: **Print Verification Sheet** imprime la planilla de verificación en PDF.
8. Indicar el **resultado global de la evaluación** (*Approved* / *Rejected*) y pulsar **Confirm Evaluation**. Bloqueos posibles:
   - *"Visual inspection must be completed."*
   - *"Document validation must be completed."*
   - *"All checklist items must have a result (Complies / Does Not Comply)."*
   - *"All nozzle tests must have an approved/rejected result."*
   - *"Global evaluation result is required."*
   Al confirmar, la verificación pasa a *Done*, la solicitud pasa a **Approved** o **Rejected**, y se genera automáticamente el PDF del resultado, que queda adjunto a la solicitud (grupo **Evaluation Report**) y disponible para el cliente en el portal:
   - aprobado → **"Certificado de Aprobación de Modelo"** con banda *RESULTADO: APROBADO* (nota en chatter: *"Model approval certificate generated."*),
   - rechazado → **"Informe Técnico de Rechazo"** con banda *RESULTADO: REPROBADO* y las observaciones de la validación documental (nota: *"Technical rejection report generated."*).

#### Estado 5 — Devolución de muestra

1. Tras la aprobación o rechazo, pulsar **Sample Return** (si no hay recepción registrada: *"No sample reception registered."*; si aún no se evaluó: *"Request must be evaluated before registering sample return."*).
2. En la ficha de recepción, completar el grupo **Sample Return**: fecha de devolución, persona que retiró la muestra y funcionario que entregó.
3. Pulsar **Register Return**. Si falta alguno de los tres datos, el sistema bloquea con *"Return date, returned-by person and return officer are required."*. La recepción pasa a *Returned* y la solicitud a **Sample Returned**.

## Estados operativos que verá en pantalla

| Estado operativo | Significado | Acción siguiente |
|------------------|-------------|------------------|
| Document Review | Solicitud recibida, pendiente de revisión | Revisor aprueba la documentación |
| Documentation Rejected | Documentación rechazada | El cliente corrige y reenvía |
| Request Approved | Documentación aprobada (verificación inicial) | Emitir habilitación temporal |
| Temporary Habilitation Issued | Habilitación emitida | Confirmar solicitud |
| Request Confirmed | Solicitud confirmada | Recepción de muestra |
| Sample Received | Muestra en laboratorio | Clasificar |
| Technically Classified | Área asignada | Abrir verificación técnica |
| Technical Evaluation | Verificación en curso | Confirmar evaluación |
| Approved / Rejected | Resultado definido | Devolver muestra; el cliente descarga el informe |
| Sample Returned | Muestra devuelta | Cerrar expediente |

## Casos especiales

- **Verificación inicial:** requiere emitir la habilitación temporal antes de poder confirmar la solicitud; el botón de emisión solo aparece con la documentación aprobada y desaparece una vez emitida.
- **Aprobación de modelo:** el formulario del cliente no lleva líneas de equipo; se confirma tras la documentación aprobada (sin habilitación temporal). El estado *Request Approved* no aplica: pasa directo de *Document Review* a *Request Confirmed* al confirmar.
- **Habilitación ya emitida:** volver a entrar por el botón **Temporary Habilitation** no re-emite el documento; si hace falta regenerar el PDF, hacerlo desde la ficha de la habilitación.
- **Checklist incompleto tras actualizaciones:** al reabrir una verificación, el sistema completa automáticamente los ítems de checklist que falten.
- **Reglas de clasificación:** si no hay regla para el tipo de instrumento, el sistema usa el área responsable definida en el propio tipo de instrumento; si tampoco existe, la clasificación queda sin área y conviene configurar la regla y reclasificar.

## Si algo no funciona

| Problema | Causa habitual | Qué hacer |
|----------|----------------|-----------|
| No deja **Confirmar** | Documentación no aprobada o falta la habilitación (verificación inicial) | Aprobar la documentación; emitir la habilitación |
| No aparece **Sample Reception** | Solicitud no confirmada | Confirmar primero |
| No deja guardar la recepción | Números de serie distintos a la cantidad de muestras | Cargar un número de serie por muestra |
| Checklist incompleto al evaluar | Ítems sin Cumple/No cumple | Completar las tres pestañas del checklist |
| No deja **Confirm Evaluation** | Falta inspección visual, validación documental, resultado por pico o resultado global | Completar lo indicado en el mensaje |
| No hay PDF de evaluación en el portal | Evaluación no confirmada | Pulsar **Confirm Evaluation** en la verificación |
| No puede registrar la devolución | Faltan datos de devolución | Completar fecha, persona y funcionario |
| El área clasificada quedó vacía | No hay regla de clasificación para el tipo de instrumento | Crear la regla en Configuración → Metrology → Classification Rules |

## Guías relacionadas

- Gestión de solicitudes de picos de surtidores: [gestion-solicitudes-picos.md](gestion-solicitudes-picos.md)
- Solicitud de laboratorio METCI: [metci-solicitud-laboratorio.md](metci-solicitud-laboratorio.md)
- Trámite del cliente en portal: [../../portal/metrologia/aprobacion-modelo-picos.md](../../portal/metrologia/aprobacion-modelo-picos.md)
