# Detalle-para-etiquetas-rojas

Fuente: `Relevamiento de datos/ANÁLISIS DE ORGANISMOS/ONC/Detalle para etiquetas rojas.xlsx`.

Regenerar: `python scripts/extract-relevamiento-sources.py`.

## Hoja `sheet1.xml`

|  | Caso 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | Regimiento 8 | Parana | Fire Masters |  |  |  |  |  |  |  |  |  |  |  |
|  | Etiqueta | cantidad | kgL/un | KgL/total | Certificados | Facturas |  | En el caso que empresas fabricantes de cilindros no requiere factura |  |  |  |  |  |  |
|  | Rojas | 1000.0 | 1.0 | 1000 | cert.1 | no tiene por que es fabricante |  | solo stock de Polvo que debe contar con stock para el total requerido |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  | una alternativa sería crear una factura o un certificado tipo lote de PQS en vez de la factura |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  | para no variar el calculo por empresa |  |  |  |  |  |  |
|  | Caso 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  | Etiqueta | cantidad | kgL/un | KgL/total | Certificados | Facturas |  |  |  |  |  |  |  |  |
|  | Rojas | 50.0 | 4.0 | 200 | cert.propio | fact. 1 cilindros |  | el cliente compro los cilindros que cargamos por tamaño para el descuento |  |  |  |  |  |  |
|  |  | 3.0 | 25.0 | 75 | cert.propio | fact. 1 cilindros |  | del certificado en el ejmplo el cliente cuenta con certificado de pqs, por lo que |  |  |  |  |  |  |
|  |  | 50.0 | 6.0 | 300 | cert.propio | fact. 2 cilindros |  | solo se carga la o las facturas de compra de cilindoros que debe coincidir con la |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  | cantidad de etiquetas solicitadas. |  |  |  |  |  |  |
|  | Caso 3 |  |  |  |  |  |  | IMPORTANTE: puede quedar stock de cilindros en las facturas para compra posteriores |  |  |  |  |  |  |
|  | Etiqueta | cantidad | kgL/un | KgL/total | Certificados | Facturas |  |  |  |  |  |  |  |  |
|  | Rojas | 50.0 | 4.0 | 200 | X | fact. 1 cilindros | fact. X POLVO | parecido al caso 2, pero el cliente compra tanto el cilindro como el polvo |  |  |  |  |  |  |
|  |  | 3.0 | 25.0 | 75 | X | fact. 1 cilindros | fact. X POLVO | en la misma factura puede detallarse los cilindros y el polvo o |  |  |  |  |  |  |
|  |  | 50.0 | 6.0 | 300 | X | fact. 2 cilindros | fact. X POLVO | en facturas diferentes. |  |  |  |  |  |  |
|  | Caso 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  | Etiqueta | cantidad | kgL/un | KgL/total | Certificados | Facturas |  | casos muy aislados, en este caso no requiere certificado por que van a cargar |  |  |  |  |  |  |
|  | Rojas | 50.0 | 4.0 | 200 | no requiere | fact. 1 cilindros | fact. Y CO2 | otro tipo de agente como es el caso de CO2 o Espuma Mecanica, por lo que |  |  |  |  |  |  |
|  |  | 30.0 | 25.0 | 750 | no requiere | fact. 1 cilindros | fact. Z espuma | deben conrtar con la factura de compra cuya cantidad coincida con el total |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  | requerido y por supuesto la compra de cilindros. |  |  |  |  |  |  |
|  | Nota: cuando mencionamos certificado, se trata de polvo quimico seco |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  | Caso 5 |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  | Etiqueta | cantidad | kgL/un | KgL/total | Certificados | Facturas |  |  |  |  |  |  |  |  |
|  | Rojas | 300.0 | 3.5 | 1050 | no requiere | fact. 1 extintor CO2 |  |  |  |  |  |  |  |  |
|  |  | 750.0 | 5.0 | 3750 | no requiere | fact. 1 extintor CO2 |  |  |  |  |  |  |  |  |
|  |  | 220.0 | 10.0 | 2200 | no requiere | fact. 1 extintor CO2 |  |  |  |  |  |  |  |  |
