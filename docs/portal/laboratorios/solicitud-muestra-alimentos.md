---
nn: "NN"
dominio: laboratorios
estado: implementado
---

# Solicitud de muestra de alimentos (OIAT) en el portal

## Para quién es esta guía

Clientes que necesitan enviar una muestra de alimentos al laboratorio **OIAT** (Organismo de Inspección y Análisis Tecnológico) para su análisis y certificación.

## Qué necesita antes de empezar

- Cuenta de portal **habilitada** ([registro y aprobación](../cuenta/registro-y-aprobacion.md)).
- Los datos de la persona de contacto para este trámite: **nombre completo** y **teléfono**.
- El producto o determinación que desea analizar, el **tipo de muestra** y la **cantidad de muestra** que va a enviar (con su unidad de medida).
- Si corresponde: el **certificado de análisis de origen** y la **planilla PROTEMAPI**, en PDF, JPG o PNG (ambos adjuntos son opcionales).

## Pasos

1. Ingrese a **Mi cuenta → Solicitudes de Servicio** y pulse **Nueva Solicitud de Servicio**.

2. En la cabecera del formulario elija el servicio en cascada: **Organismo** (*OIAT*) → **Departamento** (*Departamento de Muestras*) → **Producto** (*Muestra de alimentos*, es la única opción de este departamento). La **Categoría** no se muestra porque hay una sola disponible; queda seleccionada sola. Si luego quiere cambiar el servicio, use el enlace **Cambiar servicio**.

3. Complete **Datos de Contacto**:
   - **Proveedor** (opcional).
   - **Persona de Contacto** y **Teléfono de Contacto** (obligatorios).
   - **Observaciones y Requerimientos Especiales** (opcional): úselo para pedir un servicio que no esté en la lista o para indicar el nombre exacto que quiere que figure en el informe.

4. Complete **Datos de la Muestra** por cada determinación que quiera solicitar:
   - **Categoría** y **Producto / Determinación** (obligatorios): elija primero la categoría; el buscador de producto se habilita después.
   - **Tipo de Muestra** (obligatorio): *Líquido*, *Sólido*, *Gaseoso*, *Crudo* u *Otros*. Si elige *Otros*, aparece el campo **Especifique el tipo de muestra** (obligatorio).
   - **Presentación de la Muestra** (opcional): texto libre (por ejemplo "2 frascos") más su unidad de medida.
   - **Cantidad de Muestra** y su **UoM** (ambos obligatorios): volumen o peso físico que va a enviar.
   - **Cantidad de Servicios** (obligatorio): texto libre, por ejemplo la cantidad de determinaciones a certificar.
   - **Número de Lote**, **Fecha de Elaboración**, **Fecha de Vencimiento**, **Fecha y Hora de Muestreo**, **Nro. de Factura de Importación**, **Responsable de Muestreo**, **Marca del Producto** y **Nro. de Acta** (todos opcionales).
   - **Clasificación de Riesgo Domisanitario** (opcional): *Riesgo I* o *Riesgo II*.
   - **Certificado de análisis de origen** (opcional, PDF/JPG/PNG).
   - **Número de Solicitud/Trámite VUE** (opcional, si corresponde) y **Adjuntar Planilla PROTEMAPI** (opcional, PDF/JPG/PNG).

5. Pulse **Agregar Servicio**. El botón se habilita recién cuando completó categoría, producto, tipo de muestra, cantidad de muestra con su UoM y cantidad de servicios (y la especificación, si el tipo es *Otros*).

6. El servicio queda en la lista **Servicios solicitados**. Repita los pasos 4 y 5 para agregar más determinaciones a la misma solicitud, o use **Eliminar** para quitar alguna.

7. Revise el aviso **"AVISO IMPORTANTE DE CALIDAD"**: todos los datos consignados deben coincidir exactamente con la etiqueta de la muestra física entregada a INTN; si la muestra va en un envase reutilizado, debe llevar una identificación que coincida con lo registrado en el sistema.

8. Envíe la solicitud.

## Qué esperar después

- La solicitud queda visible en **Mis Solicitudes de Servicio** en estado **Borrador**, junto con el ticket de atención y el presupuesto/pedido de venta generados automáticamente.
- El **Departamento de Muestras** de OIAT recibe la muestra física y procesa el análisis: un técnico OIAT redacta el informe, el jefe de departamento lo aprueba y el jefe de unidad lo confirma; recién en la confirmación se asigna el número oficial. Vea el detalle completo del circuito en [Informes y certificados OIAT](../../admin/oiat-oni-mrp/oiat-informes-certificados.md).
- Cuando el certificado quede confirmado podrá descargarlo desde el detalle de su solicitud o desde [Mis documentos](../documentos-pagos/mis-documentos.md).
- Consulte y pague el presupuesto/pedido asociado desde [Facturas y pagos](../documentos-pagos/facturas-y-pagos.md).

## Si algo sale mal

| Problema | Causa habitual | Qué hacer |
|----------|----------------|-----------|
| "Agregue al menos un servicio antes de enviar." | Envió sin cargar ninguna determinación | Complete los datos de la muestra y pulse **Agregar Servicio** antes de enviar |
| "Ingrese la Persona de Contacto." / "Ingrese el Teléfono de Contacto." | Faltan los datos de contacto | Complete ambos campos en **Datos de Contacto** |
| "Servicio N: el Tipo de Muestra es obligatorio." | No eligió tipo de muestra en esa línea | Selecciónelo antes de agregar el servicio |
| "Servicio N: especifique el tipo de muestra al seleccionar 'Otros'." | Eligió *Otros* sin completar la especificación | Complete el campo **Especifique el tipo de muestra** |
| "Servicio N: la Cantidad de Muestra debe ser mayor que 0." | Cantidad vacía o en cero | Ingrese una cantidad mayor a 0 |
| "Servicio N: la UoM de la Muestra es obligatoria." | No eligió unidad de medida | Selecciónela junto a la cantidad de muestra |
| "Servicio N: la Cantidad Certificada es obligatoria." | Falta la Cantidad de Servicios | Complete ese campo antes de agregar el servicio |
| "Servicio N: el producto no está disponible para este departamento." | El producto elegido no corresponde al Departamento de Muestras | Vuelva a elegir el producto desde la cabecera |
| "Servicio N: el tipo de muestra no está disponible para este departamento." | El tipo de muestra elegido no corresponde a este departamento | Elija uno de los tipos ofrecidos por el buscador |

## Trámites relacionados

- [Combustibles y Lubricantes (OIAT)](solicitud-combustibles-lubricantes.md)
- [Registro y aprobación de la cuenta](../cuenta/registro-y-aprobacion.md)
- [Facturas y pagos](../documentos-pagos/facturas-y-pagos.md)
- [Mis documentos](../documentos-pagos/mis-documentos.md)
- Seguimiento interno de INTN (backoffice): [Informes y certificados OIAT](../../admin/oiat-oni-mrp/oiat-informes-certificados.md)
