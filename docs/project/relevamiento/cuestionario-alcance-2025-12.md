# Cuestionario de alcance (17/12/2025)

Fuente: `Relevamiento de datos/CUESTIONARIO A REALIZAR A INTN 17_12_2025.docx`.

Cuestionario para Definición de Alcance – Migración a Odoo estable

1. Alcance del Corte de Sistema

- ¿Cuál es la fecha exacta del corte del sistema para la migración?

Planteamiento de Freelancers (relevamiento previo)

- ¿Qué información consideran indispensable migrar antes del corte? ¿Identifiquen la información primaria y el resto?

Toda la información es indispensable y están interconectadas.

- ¿Qué información no desean migrar hacia Odoo? ¿Identificaron los errores de datos e información de su actual sistema?

Proponer una limpieza de la data (ejemplo: módulo de contactos)

2. Tipos de Datos a Migrar (relevamiento)

- ¿Qué módulos deben migrar obligatoriamente o por prioridad?

- ¿Desean migrar datos maestros, documentos abiertos, saldos iniciales y/o adjuntos?

- ¿Requieren migrar histórico operacional o solo información vigente?

3. Depuración y Normalización de Datos (relevamiento)

- ¿Desean depurar datos antes del proceso de migración?

- ¿Existe interés en normalizar estructuras de datos antes del corte?

4. Procesos Críticos para Inicio en Odoo (Módulos implementados)

- ¿Qué procesos deben estar completamente operativos desde el día uno?

Ejemplo: Generación de expediente, presupuesto y factura.

- ¿Qué procesos pueden migrar o implementarse posteriormente?

Nota: flujograma y reunión virtual del sistema (sistema). Lunes 15/12 – 10:00 hs

5. Personalizaciones posteriores al Corte (relevamiento)

- ¿Qué módulos personalizados actuales son indispensables replicar o migrar?

- ¿Qué funcionalidades personalizadas pueden eliminarse o rediseñarse?

6. Integraciones con Otros Sistemas

- ¿Qué sistemas externos deben seguir operando tras el corte? ¿Que tecnología usa dicho Sistema externo?

Módulo de precintos vpn offline, módulo de facturación electrónica. Módulo Identificaciones

- ¿Estas integraciones se pueden clasificar por orden de prioridad?

- ¿Qué integraciones actuales requieren reescritura o modernización?

7. Validación Operativa de Odoo

- ¿Cómo se validará que Odoo está listo para operar antes del corte? (Operaciones claves, procesos claves, datos almacenados claves, integraciones claves, etc.)

Documento de conformidad para validación.

- ¿Requieren un ambiente de pruebas previo al corte?

8. Acompañamiento y Soporte Posterior al Corte

- ¿Qué nivel de soporte esperan después del arranque en Odoo?

Pliego

- ¿Desean soporte mensual mediante bolsa de horas o por proyectos específicos?

9. Ventas (Según reunión lunes15/12)

-¿Qué información debe contener cada expediente desde el presupuesto hasta el cierre del pedido?

-¿Cuáles son los estados exactos del ciclo (ej.: presupuestado, aprobado, en fiscalización, facturado, cancelado, etc.)?

-¿Cuales son los niveles de aprobación o permisos, se requiere un panorama para entender los niveles?

Solo a nivel sistema, no documentado. Según flujograma añadir alcance de cada usuario. Ejemplo: jefe de tesorería puede anular factura

-¿Qué reportes requieren? (Se necesita modelos o ejemplos)

10. Fabricación / Producción

-¿Cómo está estructurada una orden de trabajo y qué datos técnicos debe contener? ¿La producción está ligada a ventas, inventario o certificaciones? (Explique)

Solo realizan entrada y salida, no cuentan con receta ni equipos asignados.

-¿Qué tareas o procesos productivos deben registrarse y en qué secuencia?

-¿Se debe controlar tiempos, responsables o uso de equipos/insumos?

-¿Qué reportes requieren? (Se necesita modelos o ejemplos)

11. Camiones de Cisternas

-¿Qué información debe registrarse para cada camión cisterna (datos técnicos, historial, certificados)?

Varias áreas relacionadas

-¿Cuáles son los estados operativos y quién los actualiza?

-¿Debe registrarse trazabilidad completa de cada intervención o inspección?

-¿Qué reportes requieren? (Se necesita modelos o ejemplos)

12. Trazabilidad del Uso de Marcas

-¿Qué tipo de etiquetas o marcas oficiales se gestionan?

-¿Cómo se asignan las marcas a los productos certificados?

-¿Qué datos o procesos deben auditarse para garantizar la trazabilidad?

-¿Cómo se controla el uso indebido o no autorizado de una marca?

-¿Se requiere integración con otros módulos como ONC o Ventas de normas?

-¿Qué reportes requieren? (Se necesita modelos o ejemplos)

Nota: ver modelo y marca de la impresora.

13. Ventas de Normas (relevamiento)

-¿Cómo inicia una solicitud de venta de normas (web, correo, portal)?

-¿Qué información debe incluir la cotización y quién la aprueba?

-¿Cómo se gestiona el proceso de pago y confirmación?

-¿Debe registrarse la entrega digital o física de la norma?

-¿Qué reportes o estadísticas requieren (ventas por norma, por cliente, etc.)?

14. METCI (Metrología y Calibración)

-¿Qué información debe registrarse al recibir una solicitud de calibración?

-¿Cuáles son los pasos del proceso dentro del laboratorio metrológico?

-¿Qué tipos de equipos se calibran y qué datos técnicos se deben capturar?

-¿Se requiere integración con el módulo de Laboratorio o emisión automática de certificados?

-¿Cómo se gestiona la entrega de resultados al cliente? ¿Qué reportes requieren? (Se necesita modelos o ejemplos)

Nota: Servicio, pero no hay registro de datos en el sistema.

Hoja de cálculo para obtener resultados. Requieren trazabilidad en que área está el equipo.

-¿Qué datos deben registrarse para cada báscula (técnicos, ubicación, propietario)?

-¿Qué tipos de verificaciones o inspecciones deben controlarse?

-¿Cómo se gestiona la trazabilidad de las intervenciones técnicas?

-¿Qué certificados o informes deben emitirse?

-¿Existen rangos de vigencia para certificaciones?

-¿Qué reportes requieren? (Se necesita modelos o ejemplos)

16. Portal de Clientes (Reunión miércoles 17/12 – 10:00 hs.)

-¿Qué información podrá visualizar el cliente (facturas, pedidos, certificados, estados de cuenta)? ¿Cuenta con una interfaz modelo?

-¿Qué acciones podrá realizar (solicitar servicios, descargar documentos, hacer pagos)?

-¿El acceso será mediante identidad electrónica o registro simple?

-¿Qué notificaciones debe recibir el cliente desde el portal?

-¿Se requiere integración con pagos en línea?

17. Acceso y Autenticación (relevamiento)

-¿Qué métodos de autenticación se utilizarán (token, certificado digital)?

-¿Cómo se administrarán los permisos y roles de acceso?

-¿Se requiere autenticación para clientes externos o solo para usuarios internos?

-¿Debe integrarse con otros sistemas de identidad del Estado?

-¿Se necesitan auditorías de acceso o bitácoras de actividad?

Nota: acceso vía identidad electrónica (clientes) – integración

18. Laboratorio (4 o más áreas - relevamiento)

-¿Qué tipos de análisis, ensayos o calibraciones se realizan?

-¿Qué datos debe contener cada orden de laboratorio?

-¿Cómo se gestionan los resultados, revisiones y aprobación final?

-¿Debe controlarse el uso de equipos o reactivos por ensayo?

-¿Se generan certificados oficiales? ¿Qué reportes requieren? (Se necesita modelos o ejemplos)

19. ONC – Organismo Nacional de Certificación (relevamiento – un área mas)

-¿Cómo inicia una solicitud de certificación y quién la gestiona?

-¿Cómo se hace el seguimiento del proceso de certificación hasta su cierre?

-¿Qué tipos de certificados deben emitirse y cuál es su formato?

-¿Debe controlarse la vigencia, renovación y suspensiones de certificaciones?

Nota: cada servicio genera un certificado.
