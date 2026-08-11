---
nn: "NN"
dominio: laboratorios
estado: implementado
---

# Solicitud de Combustibles y Lubricantes (OIAT) en el portal

## Para quién es esta guía

Clientes que necesitan solicitar el análisis de combustibles y lubricantes en el laboratorio **OIAT**: **Servicio Normal**, **Servicio MIC** o **Servicio Barcazas**. Los tres comparten el mismo formulario del portal; solo cambia el producto que elige en la cabecera.

## Qué necesita antes de empezar

- Cuenta de portal **habilitada** ([registro y aprobación](../cuenta/registro-y-aprobacion.md)).
- Los datos de la persona de contacto: **nombre completo** y **teléfono**.
- El **número de trámite VUI**, el **número LPI** (Licencia Previa de Importación) y la **Licencia VUI** en PDF, JPG o PNG (este adjunto es **obligatorio**).
- La fecha/hora estimada de descarga, el lugar o puerto de descarga y el volumen a descargar con su unidad de medida.

## Pasos

1. Ingrese a **Mi cuenta → Solicitudes de Servicio** y pulse **Nueva Solicitud de Servicio**.

2. En la cabecera elija el servicio en cascada: **Organismo** (*OIAT*) → **Departamento** (*Departamento de Combustibles y Lubricantes*) → **Producto**: *Combustibles: Servicio Normal*, *Combustibles: Servicio MIC* o *Combustibles: Servicio Barcazas*, según el trámite que corresponda. La **Categoría** no se muestra porque hay una sola disponible.

3. Complete **Datos de Contacto**: **Persona de Contacto** y **Teléfono de Contacto** (obligatorios) y **Observaciones** (opcional). El campo Proveedor no aplica a este servicio.

4. Complete **Datos de la Muestra**:
   - **Categoría** y **Producto / Determinación** (obligatorios).
   - **Tipo de Muestra** (obligatorio): *Líquido*, *Sólido*, *Gaseoso*, *Crudo* u *Otros* (con especificación obligatoria si elige *Otros*).
   - **Presentación de la Muestra** y su **UoM** (ambos obligatorios para este servicio).
   - **Cantidad de Muestra** y su **UoM** (obligatorios).
   - **Fecha y Hora de Muestreo** y **Nro. de Acta** quedan disponibles como opcionales, igual que en la solicitud de muestra de alimentos.

5. Complete **Datos del Trámite Exterior**:
   - **Número de Solicitud/Trámite VUI** (obligatorio).
   - **Número LPI** (obligatorio).
   - **Adjuntar Licencia VUI** (obligatorio, PDF/JPG/PNG).

6. Complete **Datos de la Operación Técnica**:
   - **Fecha/hora estimada de descarga** (obligatoria).
   - **Lugar/Puerto de descarga** (obligatorio).
   - **Volumen/Cantidad** y su **UoM** (obligatorios): volumen de combustible a descargar.

7. Pulse **Agregar Servicio**. El botón se habilita cuando completó categoría, producto, tipo de muestra, presentación con su UoM, cantidad de muestra con su UoM, los datos del trámite exterior (incluida la Licencia VUI) y los datos de la operación técnica.

8. El servicio queda en la lista; puede repetir los pasos 4 a 7 para agregar más líneas o usar **Eliminar** para quitar alguna.

9. Envíe la solicitud.

## Qué esperar después

- La solicitud queda visible en **Mis Solicitudes de Servicio** en estado **Borrador**, con su ticket y presupuesto/pedido de venta asociados.
- El **Departamento de Combustibles y Lubricantes** de OIAT procesa la muestra. Los informes de este laboratorio siguen un circuito propio (Técnico enviar → Aprobar Departamento → Unidad confirmar) y no parten de una orden de trabajo, sino directo del expediente: vea el detalle en la sección **Informes de combustible** de [Informes y certificados OIAT](../../admin/oiat-oni-mrp/oiat-informes-certificados.md).
- Cuando el informe quede confirmado podrá descargarlo desde el detalle de su solicitud o desde [Mis documentos](../documentos-pagos/mis-documentos.md).
- Consulte y pague el presupuesto/pedido asociado desde [Facturas y pagos](../documentos-pagos/facturas-y-pagos.md).

## Si algo sale mal

| Problema | Causa habitual | Qué hacer |
|----------|----------------|-----------|
| "Adjunte la Licencia VUI." | Intentó agregar el servicio sin adjuntar la Licencia VUI | Adjunte el archivo (PDF, JPG o PNG) antes de pulsar **Agregar Servicio** |
| "Complete los datos de Combustibles y Lubricantes en todos los servicios." | Falta algún dato del trámite exterior u operación técnica en alguna línea agregada | Revise cada línea agregada y complete los campos faltantes |
| "Adjunte la Licencia VUI para Combustibles y Lubricantes." | Envió la solicitud sin el adjunto de Licencia VUI | Adjúntelo antes de enviar |
| "Servicio N: el numero de solicitud VUI es obligatorio." | Falta el número de trámite VUI en esa línea | Complételo |
| "Servicio N: el numero LPI es obligatorio." | Falta el número LPI en esa línea | Complételo |
| "Servicio N: la fecha y hora de descarga son obligatorias." | Falta la fecha/hora estimada de descarga | Complétela |
| "Servicio N: el lugar de descarga es obligatorio." | Falta el lugar/puerto de descarga | Complételo |
| "Servicio N: el volumen de combustible debe ser mayor a 0." | Volumen vacío o en cero | Ingrese un volumen mayor a 0 |
| "Servicio N: la UoM del volumen de combustible es obligatoria." | No eligió unidad de medida del volumen | Selecciónela |

## Trámites relacionados

- [Solicitud de muestra de alimentos (OIAT)](solicitud-muestra-alimentos.md)
- [Registro y aprobación de la cuenta](../cuenta/registro-y-aprobacion.md)
- [Facturas y pagos](../documentos-pagos/facturas-y-pagos.md)
- [Mis documentos](../documentos-pagos/mis-documentos.md)
- Seguimiento interno de INTN (backoffice): [Informes y certificados OIAT](../../admin/oiat-oni-mrp/oiat-informes-certificados.md)
