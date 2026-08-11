# Historias de usuario por sprint

Documento derivado de `docs/tasks.csv`. Las tareas se agrupan por sprint (columna `Status`); las subtareas `Open` se asocian al padre por contexto del CSV.

**Formato:** Como **[actor]**, quiero **[acción]**, para **[beneficio]**.

**Actores recurrentes:** Cliente, ATC, Usuario interno INTN, Cajero, Tesorería, Técnico/Inspector, Jefe de departamento, Usuario OIAT/ONI/METCI/ONC/ONM, Administrador, Proveedor de etiquetas, Sistema.

**Excluido del listado:** reuniones de relevamiento (nombres de stakeholders), tareas técnicas internas (flake8, corrección pulso), backlog documental y duplicados del CSV.

---

## Sprint #1 — 23/02/2026 – 06/03/2026

### US-S1-01 — Registro de clientes

**Como** Cliente, **quiero** registrarme en el portal una vez que ATC me dé de alta, **para** acceder a los servicios de INTN.

**Subtareas:** —

---

### US-S1-02 — Estructura de contactos empresariales

**Como** Usuario ATC, **quiero** crear una empresa matriz, sucursales y contactos asociados, **para** gestionar clientes con estructura organizacional.

**Subtareas:** —

---

### US-S1-03 — Carga documental en solicitudes

**Como** Cliente, **quiero** cargar información y documentos en mi solicitud de servicio, **para** completar los requisitos del trámite.

**Subtareas:** —

---

### US-S1-04 — Historial de camiones cisterna

**Como** Usuario interno INTN (Precintados), **quiero** mantener un historial de camiones, **para** evitar pérdida o duplicación de información.

**Subtareas:** —

---

### US-S1-05 — Remisión y devolución de precintos

**Como** Usuario interno INTN (Precintados), **quiero** registrar remisiones y devoluciones de precintos, **para** controlar el ciclo de vida de los precintos.

**Subtareas:**

- Imprimir/generar la Nota de Remisión de Precintos en PDF
- Imprimir/generar la Constancia para precintado de camiones cisterna en PDF
- Generar informe listado de devoluciones de precintos (PDF/Excel) por rango de fechas y lugar
- Informe listado Estado de Precintos
- La constancia debe mostrar la Nota de Remisión y el Certificado VCC asociados
- Restringir generación de informes/certificados por permisos y menú coherente
- Wizard único con tipo de informe
- Permisos y menú Reportes certificados

---

### US-S1-06 — Certificados de cisternas

**Como** Usuario interno INTN (Precintados), **quiero** generar certificados de aprobados, rechazados e imposibilidad para camiones cisterna, **para** documentar el resultado de la inspección.

**Subtareas:**

- Campo resultado (Aprobado/Rechazado/Imposibilidad)
- Reporte listado Certificados de Aprobados
- Reporte listado Certificados de Imposibilidad
- Reporte listado Certificados de Rechazados
- Estados Aprobado/Rechazado/Imposibilidad
- Generación de Certificado de Prueba Hidrostática
- Generación de Certificado de Verificación Visual
- Generación de Requisitos para calibración y solicitud de verificación de camiones

---

### US-S1-07 — Multa por inasistencia a inspección

**Como** Sistema, **quiero** generar una multa obligatoria cuando el cliente no asiste a la inspección, **para** bloquear el reagendamiento hasta el pago y reactivar el camión.

**Subtareas:** —

---

### US-S1-08 — Check de procedimientos

**Como** Técnico/Inspector, **quiero** registrar checks de procedimientos (p. ej. inspección visual), **para** garantizar trazabilidad de las operaciones.

**Subtareas:**

- Asignación de un técnico para interactuar con el sistema y realizar checks de sus operaciones

---

## Sprint #2 — 09/03/2026 – 20/03/2026

### US-S2-01 — Agendamiento y solicitud de servicios

**Como** Cliente, **quiero** agendar y solicitar servicios con un formulario adaptado al servicio seleccionado, **para** iniciar trámites según mi necesidad.

**Subtareas:**

- Completar solicitud o formularios en portal (acoplado, emblema, adjuntos)
- Agregar productos de servicio con precios visibles al solicitar
- El sistema debe permitir al cliente registrar personal tercerizado si la persona asignada no puede presentarse

---

### US-S2-02 — Seguimiento de pedido

**Como** Cliente, **quiero** visualizar el estado de mi pedido, **para** conocer el avance de mi trámite.

**Subtareas:**

- Flujo de Usuario — Portal web
- Diagrama de Estados (general) — Portal web

---

### US-S2-03 — Visualización de presupuesto

**Como** Cliente, **quiero** visualizar el presupuesto asociado a mi solicitud, **para** conocer el costo antes de continuar.

**Subtareas:** —

---

### US-S2-04 — Datos obligatorios de contacto

**Como** Usuario ATC, **quiero** exigir Número de Identificación, Nombre, Teléfono y Correo en los contactos, **para** asegurar datos mínimos de comunicación.

**Subtareas:**

- Capturar dirección del contacto con GPS para visitas y mapeo en Paraguay
- Historial por tipo de servicios a nivel empresa, sucursal y personal
- Uso de etiquetas para servicios, tipo de cliente y segmentación por rubro
- Restringir contactos duplicados validando por RUC
- Permitir archivar datos (sin eliminar) por trazabilidad

---

### US-S2-05 — Solicitudes de picos de surtidores

**Como** Cliente, **quiero** solicitar servicios de picos (aprobación de modelo, verificación inicial, subsecuente, periódica o complementaria), **para** cumplir normativa de surtidores.

**Subtareas:**

- Seleccionar tipo de servicio (in situ o en laboratorio)
- Cargar datos del pico/surtidor: serie, marca, modelo y ficha técnica

---

### US-S2-06 — Órdenes de servicio en portal

**Como** Cliente, **quiero** gestionar mis órdenes de servicio desde el portal, **para** crear, consultar y dar seguimiento a mis trámites.

**Subtareas:**

- Mis órdenes de servicios
- Crear nueva orden de servicio
- Revisar Citas
- Botón Home

---

## Sprint #3 — 23/03/2026 – 10/04/2026

### US-S3-01 — Login con Identidad Electrónica

**Como** Cliente, **quiero** iniciar sesión vinculado a la API de Identidad Electrónica, **para** autenticarme con credenciales oficiales.

**Subtareas:** —

---

### US-S3-02 — Consulta de establecimientos por RUC

**Como** Cliente, **quiero** consultar los establecimientos (sucursales) disponibles para mi RUC, **para** seleccionar el punto correcto del trámite.

**Subtareas:** —

---

### US-S3-03 — Visualización de informes pagados

**Como** Cliente, **quiero** visualizar el informe una vez pagado el servicio, **para** acceder a la documentación emitida.

**Subtareas:**

- Descargar la documentación disponible asociada a mi solicitud

---

### US-S3-04 — Gestión de expedientes

**Como** Usuario interno INTN, **quiero** crear, editar y cancelar expedientes, **para** administrar el ciclo de cada trámite.

**Subtareas:**

- Vincular expediente con facturación para tomar datos
- Recibir solicitudes generadas vía Portal Cliente
- Sumar costo adicional al expediente mediante cálculo de costeo y facturarlo

---

### US-S3-05 — Estado de pago visible en listado

**Como** Usuario interno INTN, **quiero** ver el estado de pago de cada expediente (FACTURADO, PAGADO, NO PAGADO, CANCELADO) sin abrir el registro, **para** agilizar la gestión.

**Subtareas:** —

---

### US-S3-06 — Gestor y beneficiario

**Como** Usuario interno INTN, **quiero** seleccionar dos contactos/clientes como Gestor y Beneficiario, **para** diferenciar roles en el expediente.

**Subtareas:** —

---

### US-S3-07 — Clientes con convenio

**Como** Usuario interno INTN, **quiero** gestionar clientes con convenio (exoneraciones y descuentos), **para** aplicar automáticamente condiciones en ventas.

**Subtareas:** —

---

### US-S3-08 — Clientes a crédito

**Como** Usuario interno INTN, **quiero** un listado de clientes a crédito vinculado a Contactos, **para** identificar sujetos de crédito.

**Subtareas:** —

---

### US-S3-09 — Ecommerce de normas

**Como** Cliente autenticado, **quiero** acceder al ecommerce de productos (Normas) al iniciar sesión, **para** adquirir normas técnicas.

**Subtareas:**

- Habilitar función agregar al carrito en ecommerce

---

## Sprint #4 — 13/04/2026 – 24/04/2026

### US-S4-01 — Jerarquía organizacional para reportes

**Como** Administrador, **quiero** actualizar modelos de Organismos, Unidades, Departamentos, Coordinaciones y Laboratorios, **para** generar reportes de ventas por estructura.

**Subtareas:** —

---

### US-S4-02 — Reestructuración de productos

**Como** Administrador, **quiero** reestructurar los productos del catálogo, **para** alinearlos con la operación actual de INTN.

**Subtareas:** —

---

### US-S4-03 — Historial de variaciones de precios

**Como** Administrador, **quiero** guardar historial de variaciones de precios, **para** mantener trazabilidad de cambios.

**Subtareas:**

- Aumento/descuento masivo de precios mediante función de incremento (sin modificar uno a uno)

---

### US-S4-04 — Restricción de descarga de documentos

**Como** Administrador, **quiero** restringir la descarga de informes, constancias y otros documentos, **para** controlar el acceso según reglas de negocio.

**Subtareas:**

- Configurar qué tipos de documentos pueden limitarse en descarga

---

### US-S4-05 — Pagos, crédito y cancelación

**Como** Cajero, **quiero** registrar pago, otorgar crédito o cancelar operaciones, **para** gestionar la cobranza del servicio.

**Subtareas:**

- Notificar al área o usuario correspondiente para iniciar el servicio vía chatter

---

### US-S4-06 — Validación DNIT en facturación

**Como** Sistema, **quiero** validar que RUC y nombre del contribuyente coincidan con DNIT antes de confirmar facturación, **para** evitar datos incorrectos.

**Subtareas:** —

---

### US-S4-07 — Formato de factura

**Como** Usuario interno INTN (Facturación), **quiero** un formato de factura reestructurado, **para** cumplir requisitos legales y operativos.

**Subtareas:** —

---

### US-S4-08 — Nota de crédito

**Como** Usuario interno INTN (Facturación), **quiero** emitir notas de crédito, **para** corregir o anular facturación.

**Subtareas:**

- Mejora de visualización en reporte de Notas de Crédito con detalles de facturas origen

---

### US-S4-09 — Integración SIFEN

**Como** Usuario interno INTN (Facturación), **quiero** integrar facturación electrónica en línea con SIFEN, **para** cumplir normativa fiscal.

**Subtareas:** —

---

### US-S4-10 — Derivación de órdenes de trabajo

**Como** Jefe de departamento, **quiero** derivar una orden de trabajo entre departamentos, retornarla o cancelar la operación de servicio, **para** gestionar el flujo interdepartamental.

**Subtareas:**

- Restructuración de las Rutas de Producción en el módulo de Fabricación

---

### US-S4-11 — Estados de servicio en Fabricación

**Como** Usuario interno INTN, **quiero** estados Recepcionado, En Proceso y Realizado, **para** seguir el avance del servicio.

**Subtareas:**

- Menú de ingreso por organismo/departamento para diferenciar formularios (Módulo Fabricación)

---

### US-S4-12 — Aprobación/rechazo de documentación

**Como** Usuario interno INTN, **quiero** observar, aprobar o rechazar documentación en todos los módulos, **para** controlar calidad antes de emitir.

**Subtareas:** —

---

### US-S4-13 — Notificación al finalizar servicio

**Como** Sistema, **quiero** enviar correo al cliente al marcar un servicio como Finalizado, **para** informar que su documento está listo.

**Subtareas:**

- Configurar correos entrantes y salientes con Gmail

---

## Sprint #5 — 27/04/2026 – 08/05/2026

### US-S5-01 — Tipos de pago y validación de transferencia

**Como** Cliente, **quiero** seleccionar el tipo de pago; **como** Tesorería, **quiero** validar comprobantes de transferencia, **para** confirmar el pago correctamente.

**Subtareas:** —

---

### US-S5-02 — Cierre de caja por cajero

**Como** Cajero, **quiero** realizar cierre individual de caja, **para** conciliar mi operación diaria.

**Subtareas:**

- Integración con caja AquíPago como bandera configurable

---

### US-S5-03 — Campos variables por tipo de servicio

**Como** Usuario interno INTN, **quiero** que los campos del formulario varíen según el servicio, **para** capturar solo la información relevante.

**Subtareas:** —

---

### US-S5-04 — Bloqueo por facturas vencidas

**Como** Sistema, **quiero** bloquear nuevas solicitudes cuando el cliente tenga N facturas vencidas (configurable), **para** controlar morosidad.

**Subtareas:** —

---

### US-S5-05 — Permisos por departamento en Fabricación

**Como** Administrador, **quiero** controlar acceso a menús del módulo Fabricación por organismo (p. ej. OIAT solo ve lo suyo), **para** segregar información.

**Subtareas:** —

---

### US-S5-06 — Módulo de documentos históricos

**Como** Cliente / Usuario interno INTN, **quiero** acceder al histórico de documentos adjuntos y certificados emitidos (backend y portal), **para** consultar y reutilizar documentación.

**Subtareas:**

- Repositorio único de documentos (configuración base)
- Persistencia byte-estable del PDF al confirmar
- Vista backend "Documentos" en el origen
- Página unificada `/my/documents` en portal
- Reimpresión auditada de certificados
- Auditoría de descargas desde portal
- Subida estructurada de respaldos por cliente
- Visibilidad por departamento

---

### US-S5-07 — Reportes OIAT

**Como** Usuario OIAT, **quiero** tablas de reportes con fechas, expediente, cliente, ensayos, actas, etc., **para** analizar la operación del organismo.

**Subtareas:** —

---

### US-S5-08 — Reportes METCI

**Como** Usuario METCI, **quiero** tablas de reportes y emisión de reportes operativos, **para** seguimiento de solicitudes y servicios.

**Subtareas:**

- Tablas de reportes METCI (fechas de solicitud, revisión, confirmación, facturación, recepción, presupuesto, laboratorio, cantidad)

---

### US-S5-09 — Certificados METCI con QR

**Como** Usuario METCI, **quiero** generar certificados de calibración, informes técnicos e informes de servicio no realizado en PDF con código único y QR, **para** validación de documentos.

**Subtareas:**

- Generación de Certificado de Registro de Medición

---

### US-S5-10 — Migración inspección tanque cisterna

**Como** Usuario interno INTN (Precintados), **quiero** los procesos de inspección de tanque cisterna migrados al nuevo sistema, **para** continuar operación en Odoo 18.

**Subtareas:** —

---

## Sprint #6 — 11/05/2026 – 22/05/2026

### US-S6-01 — Formulario solicitud METCI

**Como** Cliente / Usuario METCI, **quiero** un formulario de solicitud de servicio para METCI, **para** iniciar trámites de calibración/metrología.

**Subtareas:** —

---

### US-S6-02 — Documentos OIAT

**Como** Usuario OIAT, **quiero** generar constancias, informes de ensayo, informes de maquila y solicitudes internas con formatos oficiales, **para** documentar servicios del organismo.

**Subtareas:** —

---

### US-S6-03 — Informes ONI — Inspecciones de instalación

**Como** Usuario ONI (Dept. Inspecciones de Instalación), **quiero** cargar y generar informes de inspección y certificados, **para** emitir documentación oficial.

**Subtareas:**

- FOR-ONI-35 Informe de Inspección Versión 12 / ONA
- FOR-ONI-53 Certificado de Inspección Versión 03
- FOR-ONI-36 Informe Técnico Versión 08
- FOR-ONI-81 Constancia de no realización de servicio Versión 01

---

### US-S6-04 — Informes ONI — Seguridad Industrial

**Como** Usuario ONI (Seguridad Industrial), **quiero** generar informes de inspección, ensayo, técnico y certificado, **para** documentar servicios del departamento.

**Subtareas:** —

---

### US-S6-05 — Informes ONI — Muestreo

**Como** Usuario ONI (Muestreo), **quiero** generar los cuatro tipos de informes con formatos oficiales, **para** cumplir procedimientos del departamento.

**Subtareas:**

- FOR-ONI-76 Informe de Muestreo Versión 02
- FOR-ONI-78 Informe de Muestreo Versión 02

---

### US-S6-06 — Módulo de reportes

**Como** Usuario interno INTN, **quiero** un módulo centralizado de reportes, **para** acceder a informes transversales del sistema.

**Subtareas:** —

---

### US-S6-07 — Integración SIFEN (facturación)

**Como** Usuario interno INTN (Facturación), **quiero** la integración de facturación electrónica SIFEN operativa, **para** emitir comprobantes fiscales válidos.

**Subtareas:** —

---

### US-S6-08 — Operaciones de centro de trabajo DSE

**Como** Usuario interno INTN (DSE), **quiero** operaciones de centro de trabajo migradas desde v12 (electricistas e inspectores), **para** mantener el flujo productivo.

**Subtareas:** —

---

## Sprint #7 — 25/05/2026 – 05/06/2026

### US-S7-01 — Formulario solicitud ONI

**Como** Cliente / Usuario ONI, **quiero** un formulario de solicitud de servicio para ONI, **para** iniciar trámites del organismo.

**Subtareas:** —

---

### US-S7-02 — Formulario solicitud OIAT

**Como** Cliente / Usuario OIAT, **quiero** un formulario de solicitud de servicio para OIAT, **para** iniciar trámites del organismo.

**Subtareas:** —

---

### US-S7-03 — Formularios ONC

**Como** Cliente / Usuario ONC, **quiero** formularios de certificación de productos (ONC-FOR-001), personas (ONC-FPE-001) y sistemas (ONC-FSG-001), **para** solicitar certificaciones.

**Subtareas:** —

---

### US-S7-04 — Reportes ONC

**Como** Usuario ONC, **quiero** tablas de reportes con recepción, ejecución, expediente, cliente, ensayos, actas, etc., **para** seguimiento operativo.

**Subtareas:** —

---

### US-S7-05 — Informes ONI — Metalurgia

**Como** Usuario ONI (Metalurgia), **quiero** generar informes de inspección, ensayo, técnico y certificado, **para** documentar servicios del departamento.

**Subtareas:**

- FOR-ONI-34 Informe de Ensayo Versión 08 / ONA

---

### US-S7-06 — Informes ONI — Ensayo y constancia

**Como** Usuario ONI, **quiero** generar informes de ensayo y constancias, **para** emitir documentación combinada.

**Subtareas:** —

---

### US-S7-07 — Informes ONI — Textiles

**Como** Usuario ONI (Textiles), **quiero** generar los cuatro tipos de informes oficiales, **para** documentar servicios del departamento.

**Subtareas:** —

---

### US-S7-08 — Informes ONI — Materiales de construcción

**Como** Usuario ONI (Materiales de Construcción), **quiero** generar los cuatro tipos de informes oficiales, **para** documentar servicios del departamento.

**Subtareas:** —

---

### US-S7-09 — Trazabilidad de impresión de etiquetas

**Como** Proveedor de etiquetas / Usuario ONC, **quiero** registrar quién imprimió, fecha de entrega y datos de la orden de servicio, **para** trazabilidad de etiquetas.

**Subtareas:** —

---

## Sprint #8 — 08/06/2026 – 19/06/2026

### US-S8-01 — Ventas de etiquetas por periodo

**Como** Usuario ONC, **quiero** un informe de ventas de etiquetas por periodo, **para** control comercial y facturación.

**Subtareas:** —

---

### US-S8-02 — Registro de entregas de etiquetas y anillos

**Como** Usuario ONC, **quiero** registrar entregas de etiquetas y anillos, **para** control de stock y trazabilidad.

**Subtareas:** —

---

### US-S8-03 — Comunicación con impresora de etiquetas

**Como** Sistema, **quiero** garantizar comunicación correcta con la impresora, **para** imprimir etiquetas sin errores.

**Subtareas:** —

---

### US-S8-04 — Registro de básculas

**Como** Usuario ONM (Básculas), **quiero** un formulario con carga máxima/mínima, modelo, serie, tipo, visibilidad en portal, etc., **para** inventariar instrumentos.

**Subtareas:** —

---

### US-S8-05 — Resultados de verificación de básculas

**Como** Técnico ONM, **quiero** registrar fecha de verificación, vencimiento, evaluación visual y estado, **para** documentar resultados de calibración.

**Subtareas:** —

---

### US-S8-06 — Incidencias de básculas

**Como** Usuario ONM, **quiero** registrar básculas e incidencias asociadas, **para** historial de mantenimiento y fallas.

**Subtareas:** —

---

### US-S8-07 — Integración Segel

**Como** Usuario ONM, **quiero** integración con la aplicación de Básculas (Segel), **para** sincronizar datos técnicos.

**Subtareas:** —

---

### US-S8-08 — Gestión de tareas de básculas

**Como** Jefe de departamento ONM, **quiero** crear tareas, asignar responsables y estados personalizados, **para** coordinar verificaciones.

**Subtareas:**

- Reporte por marca, modelo, rubro, tipo, cliente y estado

---

## Sprint #9 — 22/06/2026 – 03/07/2026

### US-S9-01 — Gestión de cuotas

**Como** Cliente, **quiero** ver pagos realizados, pendientes y vencimiento de cuotas, **para** administrar mi deuda.

**Subtareas:** —

---

### US-S9-02 — QR dinámico en etiquetas

**Como** Usuario ONC, **quiero** un código QR dinámico en cada etiqueta, **para** validación y trazabilidad.

**Subtareas:** —

---

### US-S9-03 — Almacenes e inventario

**Como** Administrador / Usuario interno INTN, **quiero** crear almacenes con dirección vinculada, **para** control de stock.

**Subtareas:**

- Creación de ubicaciones y sububicaciones
- Inventario de etiquetas y anillos (vigentes, dañados, desechados)
- Recepción y control de equipos (METCI)
- Recepción control stock equipos (UMLE)
- Recepción control stock productos (Precintados)
- Operaciones de transferencia y salida de productos
- Informe de stock actual por almacén
- Uso de Nº de Lote y Serie para trazabilidad (Precintados y ONC)

---

### US-S9-04 — Baja de productos dañados

**Como** Usuario interno INTN, **quiero** desechar o dar de baja ítems dañados registrando el motivo, **para** mantener inventario actualizado.

**Subtareas:** —

---

### US-S9-05 — Bloqueo de calendario

**Como** Administrador / Jefe de departamento, **quiero** bloquear fechas o períodos no disponibles, **para** impedir asignación de turnos en áreas operativas.

**Subtareas:** —

---

### US-S9-06 — Agenda de servicios pendientes

**Como** Jefe de departamento, **quiero** agendar servicios pendientes (visitas, inspecciones, exámenes), **para** planificar recursos.

**Subtareas:**

- Agenda para visitas de inspección, auditorías y exámenes del Dept. Personas
- Crear estados del proyecto o flujos de trabajo
- El sistema debe ser colaborativo: usuarios ingresan, adjuntan archivos y dejan notas

---

### US-S9-07 — Observaciones del cliente post-entrega (Picos)

**Como** Cliente, **quiero** registrar observaciones dentro de 48 h posteriores a la entrega, **para** que el servicio se cierre o entre en revisión según corresponda.

**Subtareas:** —

---

## Sprint #10 — 06/07/2026 – 17/07/2026

### US-S10-01 — ID histórico de surtidor

**Como** Sistema, **quiero** asignar un ID de surtidor en la Verificación Inicial, **para** usarlo como identificador en intervenciones posteriores.

**Subtareas:** —

---

### US-S10-02 — Datos técnicos de ensayos (ONM)

**Como** Usuario ONM, **quiero** una interfaz para llenar datos técnicos y calcular resultados de ensayos, **para** entregar automáticamente resultados al cliente vía portal.

**Subtareas:**

- Generar automáticamente resultado de ensayos en PDF, descargable solo en estado PAGADO
- Emitir reportes mensuales con número correlativo de ensayos
- Reporte histórico por modelo de pico de surtidor

---

### US-S10-03 — GPS en picos de surtidores

**Como** Usuario ONM, **quiero** registrar coordenadas GPS (X/Y) de picos de surtidores, **para** georreferenciación.

**Subtareas:** —

---

### US-S10-04 — Vencimiento de certificaciones

**Como** Administrador / Jefe de departamento, **quiero** vigilancia y seguimiento de vencimiento de certificaciones, **para** alertar renovaciones.

**Subtareas:** —

---

## Sprint #11 — 20/07/2026 – 31/07/2026

### US-S11-01 — Validación de informes por QR

**Como** Cliente / Autoridad, **quiero** validar informes escaneando un QR en una URL autorizada de INTN, **para** verificar autenticidad y validez.

**Subtareas:** —

---

### US-S11-02 — Mapa de ubicaciones

**Como** Usuario interno INTN, **quiero** visualizar en mapa las ubicaciones georreferenciadas de balanzas y picos, **para** planificación operativa.

**Subtareas:** —

---

### US-S11-03 — Limpieza y migración de contactos

**Como** Administrador, **quiero** limpiar y migrar datos de contactos, **para** partir de una base consistente.

**Subtareas:** —

---

### US-S11-04 — Estado final de servicio (Picos)

**Como** Técnico ONM, **quiero** asignar estado final Aprobado, Reprobado o Imposibilidad, **para** cerrar el servicio con resultado definitivo.

**Subtareas:** —

---

## Sprint #12 — 03/08/2026 – 14/08/2026

### US-S12-01 — Ajustes reportes TRA

**Como** Usuario interno INTN (TRA), **quiero** ajustes en reportes varios del módulo TRA, **para** cumplir requerimientos operativos.

**Subtareas:** —

---

### US-S12-02 — Capacitación y transferencia

**Como** Usuario interno INTN, **quiero** capacitación y transferencia tecnológica del sistema, **para** operarlo de forma autónoma.

**Subtareas:** —

---

## Notas sobre el CSV

1. **Tareas Open sin sprint** se mapearon como subtareas cuando hay relación explícita o contextual (p. ej. FOR-ONI bajo informes ONI, documentos bajo RF 5.21).
2. **Entrevistas de relevamiento** (nombres de responsables por área) no se convirtieron en historias de usuario; son actividades de descubrimiento, no funcionalidad del sistema.
3. **Duplicados** en el CSV (líneas repetidas a partir de ~200) se deduplicaron por `Task ID`.
4. Algunas tareas Open sin padre claro en el CSV (p. ej. `Ventas - Facturación`, `Reporte de bugs`) quedaron fuera hasta definir su sprint padre.

**Fuente:** `docs/tasks.csv`
