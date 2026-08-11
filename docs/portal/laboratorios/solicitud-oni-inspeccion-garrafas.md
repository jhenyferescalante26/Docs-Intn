---
nn: "NN"
dominio: laboratorios
estado: implementado
---

# Solicitud de Inspección de Garrafas (ONI) en el portal

## Para quién es esta guía

Clientes que necesitan solicitar la inspección de garrafas de gas del **Programa de Inspección** del organismo **ONI**.

## Qué necesita antes de empezar

- Cuenta de portal **habilitada** ([registro y aprobación](../cuenta/registro-y-aprobacion.md)).
- El **RUC** de su empresa cargado en el sistema.
- Datos de facturación: **email** y **teléfono** para la factura, **departamento**, **ciudad** y **dirección** en Paraguay.
- Datos de contacto: **nombre**, **teléfono** y **email**.
- Poder **obtener la ubicación georreferencial** desde el navegador (botón **Obtener ubicación**): es obligatoria para este trámite.
- La **cantidad de garrafas** y la **capacidad exacta** de cada tanda que va a declarar.

## Pasos

1. Ingrese a **Mi cuenta → Solicitudes de Servicio** y pulse **Nueva Solicitud de Servicio**.

2. En la cabecera elija **Organismo** (*ONI*) → **Departamento** (*Programa de Inspección*). El **Producto** se completa solo con *ONI: Inspección de Garrafas* (es la única opción de este departamento) y la **Categoría** tampoco se muestra por el mismo motivo.

3. Complete **Datos Administrativos para la Facturación**:
   - **RUC** y **Razón Social / Nombre** (de solo lectura).
   - **Email** y **Teléfono** para la factura (obligatorios).
   - **Departamento** y **Ciudad** en Paraguay (obligatorios, con buscador).
   - **Dirección** (obligatoria).
   - **Ubicación Georreferencial**: pulse **Obtener ubicación**; es **obligatoria** para este trámite.

4. Complete **Datos de Contacto**: **Nombre**, **Teléfono** y **Email** (los tres obligatorios).

5. En **Datos de la Muestra**, cargue una tanda por cada capacidad de garrafa que declare:
   - **Cantidad de garrafas** (obligatoria, mayor a cero).
   - **Capacidad exacta** (obligatoria, texto libre).
   - **Observaciones/Descripciones de la Muestra** (opcional).

6. Pulse **Agregar** para sumar la tanda a la lista **Garrafas Agregadas**. Repita el paso 5 para declarar más capacidades, o use **Eliminar** para quitar una tanda.

7. Envíe la solicitud. Debe haber agregado al menos una tanda de garrafas.

## Qué esperar después

- La solicitud queda visible en **Mis Solicitudes de Servicio** en estado **Borrador**, con su ticket y presupuesto/pedido de venta asociados.
- El **Programa de Inspección** de ONI procesa la solicitud: se genera el **informe de inspección** correspondiente, que sigue el circuito Borrador → Aprobado → Confirmado, y luego el **certificado de inspección** vinculado. Vea el detalle completo en [Informes ONI](../../admin/oiat-oni-mrp/oni-informes.md).
- Cuando el certificado quede confirmado podrá descargarlo desde el detalle de su solicitud o desde [Mis documentos](../documentos-pagos/mis-documentos.md).
- Consulte y pague el presupuesto/pedido asociado desde [Facturas y pagos](../documentos-pagos/facturas-y-pagos.md).

## Si algo sale mal

| Problema | Causa habitual | Qué hacer |
|----------|----------------|-----------|
| "El RUC es obligatorio." | Su empresa no tiene RUC cargado | Contacte a INTN para completar el RUC de su empresa |
| "Ingrese el correo para recepción de factura." / "Ingrese el teléfono para recepción de factura." | Faltan los datos de facturación | Complételos |
| "Seleccione el departamento." / "Seleccione la ciudad." | No eligió departamento o ciudad de Paraguay | Elíjalos con el buscador |
| "Ingrese la direccion." | Falta la dirección | Complétela |
| "Obtenga la ubicacion georreferencial antes de enviar." | No obtuvo la ubicación | Pulse **Obtener ubicación** y acepte el permiso del navegador |
| "Ingrese el nombre de contacto." / "Ingrese el telefono de contacto." / "Ingrese el correo de contacto." | Faltan los datos de contacto | Complételos |
| "Agregue al menos una garrafa antes de enviar." | Envió sin cargar ninguna tanda | Cargue al menos una tanda y pulse **Agregar** |
| "Garrafa N: la cantidad debe ser mayor a cero." | Cantidad vacía o en cero en esa tanda | Ingrese una cantidad mayor a cero |
| "Garrafa N: la capacidad exacta es obligatoria." | Falta la capacidad exacta en esa tanda | Complétela |
| "Seleccione el producto en el encabezado." | No se completó el producto en la cabecera | Vuelva a la cabecera y confirme la selección de *ONI: Inspección de Garrafas* |

## Trámites relacionados

- [Seguridad Industrial, Textil y Muestreo (ONI)](solicitud-oni-seguridad-textil-muestreo.md)
- [Maquila y Manufactura (ONI)](solicitud-oni-maquila.md)
- [Registro y aprobación de la cuenta](../cuenta/registro-y-aprobacion.md)
- [Facturas y pagos](../documentos-pagos/facturas-y-pagos.md)
- [Mis documentos](../documentos-pagos/mis-documentos.md)
- Seguimiento interno de INTN (backoffice): [Informes ONI](../../admin/oiat-oni-mrp/oni-informes.md)
