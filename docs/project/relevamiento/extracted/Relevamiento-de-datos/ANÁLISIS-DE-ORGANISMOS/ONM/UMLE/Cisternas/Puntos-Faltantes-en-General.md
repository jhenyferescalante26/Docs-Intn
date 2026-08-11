# Puntos-Faltantes-en-General

Fuente: `Relevamiento de datos/ANÁLISIS DE ORGANISMOS/ONM/UMLE/Cisternas/Puntos Faltantes en General.docx`.

Regenerar: `python scripts/extract-relevamiento-sources.py`.

Puntos Faltantes en General

Por cada proceso realizado al camión Ej: Verificación Documental, Verificación Inicial, Prueba Hidrostática, Registro de Medición se tienen que tener las opciones para Aprobar, Rechazar, o Imposibilidad. Por cada opción se debe poder generar un certificado el cuál será enviado al cliente

El cliente debe poder dar de baja su camión si es que ese camión deja de operar.

El cliente debe poder cancelar la solicitud que había realizado con 42hs de antelación, si cancela con menos de 42hs se le debe aplicar un bloqueo de 30 días.

El calendario que le aparece al cliente se tiene que validar dependiendo de la disponibilidad (Debe aparecerle si la fecha está disponible o no al querer marcar una fecha X). Los turnos se validan considerando la capacidad de hasta 160 litros por día (generalmente dentro de esos 160 litros de capacidad suelen entrar hasta 5 camiones por día). Para cuáles tipos de servicios se debe aplicar la restricción de hasta 160 litros?

Los de Cisternas no generan la multa. Necesitan crear un informe sobre el camión dependiendo del tipo de irregularidad cometido y derivar al departamento DJUR para que puedan encargarse de oficializar esa multa

Consultar:

Por cada proceso se debe devolver un certificado al cliente?

A parte del certificado del proceso realizado de igual forma debe recibir también el certificado de Aprobado, Rechazado o Imposibilidad?

Anotaciones

Lo ideal sería conectar la sección en donde se crea el vehículo y el remolque desde el formulario cuando se elige el Tipo de Solicitud con el menú Mis Vehículos para que todos los Vehículos creados puedan aparecer en ese menú con un boton de check de Activo/Inactivo para que los clientes puedan dar de baja a su camión si deja de operar.
