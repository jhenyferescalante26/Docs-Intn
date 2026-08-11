---
nn: "NN"
dominio: laboratorios
estado: implementado
---

# Solicitud de Seguridad Industrial, Textil y Muestreo (ONI) en el portal

## Para quién es esta guía

Clientes que necesitan solicitar servicios de laboratorio del organismo **ONI**: **Seguridad Industrial**, **Textil** o **Muestreo**. Los tres servicios comparten el mismo formulario base del portal; cada uno agrega algunos campos propios de su departamento.

## Qué necesita antes de empezar

- Cuenta de portal **habilitada** ([registro y aprobación](../cuenta/registro-y-aprobacion.md)).
- Datos de facturación: **email** y **teléfono** para la factura, **departamento**, **ciudad** y **dirección** en Paraguay (se precargan con los datos de su empresa cuando existen).
- Datos de contacto para el trámite: **nombre**, **teléfono** y **email**.
- El producto/determinación que desea solicitar, el tipo de muestra y la cantidad a analizar.
- Para **Muestreo**: además necesita obtener la **ubicación georreferencial** desde el navegador antes de enviar (botón **Obtener ubicación**).
- Para **Textil**: si corresponde, tenga a mano la **Planilla de Trámite VUE** (adjunto opcional, PDF/JPG/PNG).

## Pasos

1. Ingrese a **Mi cuenta → Solicitudes de Servicio** y pulse **Nueva Solicitud de Servicio**.

2. En la cabecera elija el servicio en cascada: **Organismo** (*ONI*) → **Departamento** → **Producto**. Según el departamento que elija, el producto ofrecido es distinto:
   - **Seguridad industrial** → *ONI: Seguridad Industrial*.
   - **Textil** → *ONI: Textil*.
   - **MUESTREO** → *ONI: Muestreo*.

   La **Categoría** no se muestra porque hay una sola disponible (ONI).

3. Complete **Datos Administrativos para la Facturación**:
   - **RUC** y **Razón Social / Nombre** (de solo lectura, tomados de su empresa).
   - **Email** y **Teléfono** para la factura (obligatorios).
   - **Departamento** y **Ciudad** en Paraguay (obligatorios, con buscador).
   - **Dirección** (obligatoria).
   - **Ubicación Georreferencial**: pulse **Obtener ubicación** para completar latitud y longitud. Es **obligatoria únicamente para Muestreo**; en Seguridad Industrial y Textil es opcional.

4. Complete **Datos de Contacto**: **Nombre**, **Teléfono** y **Email** (los tres obligatorios).

5. Complete la sección de datos de la muestra/servicio; los campos varían según el producto elegido:

   **Seguridad Industrial**
   - **Categoría (Matriz de Producto)** y **Producto (Determinación)** (obligatorios).
   - **Tipo de Muestra** (obligatorio): *Líquido*, *Sólido* u *Otros*.
   - **Cantidad de Servicios** (obligatoria, texto libre) y **Cantidad de Muestra** con su **UoM** (obligatorias).

   **Textil**
   - Mismos campos que Seguridad Industrial, pero el **Tipo de Muestra** ofrece: *Tejido*, *Hilo*, *Fibra*, *Prenda*, *Calzados* o *Colchones*.
   - **Dimensión de la Muestra** y su **UoM** (obligatorios): por ejemplo "50 x 50 cm".
   - **Observaciones/Descripciones de la Muestra** (opcional).
   - **Adjuntar Planilla de Trámite VUE** (opcional, PDF/JPG/PNG).

   **Muestreo**
   - **Categoría (Matriz de Producto)**, **Producto (Determinación)** y **Tipo de Muestra** (obligatorios; el tipo de muestra ofrece *Líquido*, *Sólido* u *Otros*).
   - **Presentación de la Muestra** y su **UoM** (obligatorios): por ejemplo "2 frascos".
   - **Cantidad de Muestra** y su **UoM** (obligatorios) y **Cantidad de Servicios** (obligatoria).
   - **Marca**, **Lote**, **Fecha de Elaboración**, **Fecha de Vencimiento**, **Fecha y Hora para proceder a la toma de muestra** y **Factura Exportación** (todos opcionales).

6. Pulse **Agregar Servicio**. El botón se habilita cuando completó los campos obligatorios de la sección anterior (en Textil y Muestreo también exige la dimensión/presentación con su UoM).

7. El servicio queda en la lista **Servicios solicitados**. Repita los pasos 5 y 6 para agregar más determinaciones, o use **Eliminar** para quitar alguna.

8. Envíe la solicitud. En Muestreo, si no obtuvo la ubicación georreferencial antes de enviar, el sistema se lo pedirá.

## Qué esperar después

- La solicitud queda visible en **Mis Solicitudes de Servicio** en estado **Borrador**, con su ticket y presupuesto/pedido de venta asociados.
- El departamento ONI correspondiente (Seguridad Industrial, Textil o Muestreo) revisa el trámite y arma el documento que corresponda (informe de ensayo, técnico o de muestreo/no intervención, según el servicio). Vea el circuito completo de aprobación y numeración en [Informes ONI](../../admin/oiat-oni-mrp/oni-informes.md).
- Cuando el documento quede confirmado podrá descargarlo desde el detalle de su solicitud o desde [Mis documentos](../documentos-pagos/mis-documentos.md).
- Consulte y pague el presupuesto/pedido asociado desde [Facturas y pagos](../documentos-pagos/facturas-y-pagos.md).

## Si algo sale mal

| Problema | Causa habitual | Qué hacer |
|----------|----------------|-----------|
| "Ingrese el correo para recepción de factura." / "Ingrese el teléfono para recepción de factura." | Faltan los datos de facturación | Complételos en **Datos Administrativos para la Facturación** |
| "Seleccione el departamento." / "Seleccione la ciudad." | No eligió departamento o ciudad de Paraguay | Elíjalos con el buscador |
| "Ingrese la dirección." | Falta la dirección | Complétela |
| "Obtenga la ubicación georreferencial antes de enviar." | En Muestreo, no obtuvo la ubicación | Pulse **Obtener ubicación** y acepte el permiso del navegador |
| "Ingrese el nombre de contacto." / "Ingrese el teléfono de contacto." / "Ingrese el correo de contacto." | Faltan los datos de contacto | Complételos en **Datos de Contacto** |
| "Agregue al menos un servicio antes de enviar." | Envió sin cargar ninguna determinación | Complete los datos de la muestra y pulse **Agregar Servicio** |
| "Servicio N: el Tipo de Muestra es obligatorio." / "…la Cantidad de Muestra debe ser mayor que 0." / "…la UoM de la Muestra es obligatoria." / "…la Cantidad Certificada es obligatoria." | Falta algún dato obligatorio en esa línea | Complete el campo indicado antes de agregar el servicio |
| "Servicio N: la dimensión de la muestra es obligatoria." / "…la UoM de dimensión de la muestra es obligatoria." | En Textil, falta la dimensión o su UoM | Complételas |
| "Servicio N: la presentación de la muestra es obligatoria." / "…la UoM de presentación de la muestra es obligatoria." | En Muestreo, falta la presentación o su UoM | Complételas |
| "Servicio N: el producto no está disponible para este departamento." | El producto elegido no corresponde al departamento seleccionado en la cabecera | Vuelva a elegir el producto desde la cabecera |

## Trámites relacionados

- [Inspección de Garrafas (ONI)](solicitud-oni-inspeccion-garrafas.md)
- [Maquila y Manufactura (ONI)](solicitud-oni-maquila.md)
- [Registro y aprobación de la cuenta](../cuenta/registro-y-aprobacion.md)
- [Facturas y pagos](../documentos-pagos/facturas-y-pagos.md)
- [Mis documentos](../documentos-pagos/mis-documentos.md)
- Seguimiento interno de INTN (backoffice): [Informes ONI](../../admin/oiat-oni-mrp/oni-informes.md)
