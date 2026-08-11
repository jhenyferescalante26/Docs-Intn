# RF 2.9 — Ecommerce de productos (Normas) al iniciar sesión

> Estado: **marcado «Listo para pruebas» en ClickUp, pero incompleto**
> ([86e0yxqnm](https://app.clickup.com/t/86e0yxqnm), sprint #3).
> Análisis al commit `a43632c8` (28/07/2026). No considera trabajo sin commitear.
>
> **Enunciado:** *«Al iniciar login se habilita la opción de Ecommerce de
> productos (Normas).»*

---

## 1. Por qué no debería cerrarse

La tarjeta figura en *Listo para pruebas*, pero tanto el checklist interno como
el código dicen otra cosa:

- `SPRINT_1_5_COMPLIANCE_CHECKLIST.csv` (US-S3-09) la marca **Parcial**, con la
  nota *«Sin catálogo Normas dedicado en custom_addons»* y *«Carrito estándar
  website_sale»*.
- Los únicos commits recientes sobre el tema son de documentación —
  `28b50bc8` y `461f4a5d` (27/07/2026) — es decir, **análisis y plan, no
  implementación**.

Si se manda a QA en este estado, el tester va a encontrar la tienda poblada con
los muebles de la demo de Odoo.

---

## 2. Criterios de aceptación (según ClickUp)

Del comentario registrado en la tarjeta:

> Como cliente del INTN quiero que al ingresar al sistema con mi usuario y
> contraseña se habilite la opción de Ecommerce de productos en el portal.

1. Al hacer login en el portal, se habilita automáticamente la opción de menú
   **Ecommerce de productos**.
2. La opción es visible **únicamente para clientes autenticados**.
3. El acceso lleva a la sección de Ecommerce con **listado de productos
   disponibles, precios y condiciones**.
4. El sistema valida permisos: **sólo perfiles de cliente** pueden visualizar y
   usar la opción.

---

## 3. Qué hay hoy

| Criterio | Estado | Detalle |
|---|---|---|
| 1. Menú habilitado al login | ✅ | `intn_portal_registration` publica el tile **Ecommerce** apuntando a `/my/ecommerce` en el inicio del portal |
| 2. Sólo autenticados | ✅ | La ruta vive bajo `/my/`, que ya exige sesión |
| 3. Listado con precios y condiciones | ❌ | La tienda muestra los **26 muebles de la demo de Odoo**. Cero normas migradas a v18 |
| 4. Validación de permisos por perfil | 🟡 | Hay control de autenticación, pero no hay una regla que distinga *perfil cliente* de otros usuarios de portal |

En síntesis: **la puerta está puesta, la sala está vacía.** El criterio 3 es el
que sostiene el RF y es el que no se cumple.

---

## 4. El alcance real: RF 2.9 depende de la migración del catálogo

RF 2.9 se lee como una tarea de menú, pero no se puede cumplir sin traer las
normas desde `intn_v12`. El relevamiento y el plan completo ya están escritos en
[`docs/design/venta_de_normas.md`](../../design/venta_de_normas.md); este spec
**no los repite**. Lo esencial para dimensionar:

| Dato en v12 | Valor |
|---|---|
| Productos de norma (`NP…`, `PNA-…`) | 887 |
| Publicados en la web | 846 |
| Con el PDF cargado | 857 |
| Órdenes históricas que incluyen normas | 3.025 |

El PDF vive en una columna binaria del producto (`product_template.norma_document`).
En v12 **no existe control de descargas**: contador, límite y bitácora son
funcionalidad nueva.

### Fase que cierra RF 2.9

De las cuatro fases del plan (`venta_de_normas.md` §5), **RF 2.9 se cierra con
la Fase N1 — Catálogo**:

- Migrar los 887 productos con precio, publicación y PDF (a `ir.attachment`,
  no como columna binaria).
- Despublicar los muebles de la demo.
- Cargar los datos institucionales del INTN en la tienda (pedido de la minuta
  del 14/01).

Las fases N2 (compra, pago y cupo de descarga), N3 (marca de agua y restricción
de impresión) y N4 (autorización adicional) exceden RF 2.9 y corresponden a
tarjetas propias — hoy no existen en ClickUp y conviene crearlas.

---

## 5. Qué falta para cerrar

| # | Acción | Tipo | Bloqueante |
|---|---|---|---|
| A1 | Migrar el catálogo de 887 normas con precio, publicación y PDF | Código | **Sí** |
| A2 | Despublicar los productos demo de Odoo | Código | Sí |
| A3 | Datos institucionales del INTN en la tienda | Contenido | Sí |
| A4 | Regla de acceso que limite el Ecommerce al perfil cliente (criterio 4) | Código | Sí |
| A5 | Bloquear la venta de las ~30 normas sin PDF cargado (edge case E8) | Código | No |
| A6 | Crear tarjetas para las fases N2–N4 | Gestión | No |

---

## 6. Decisiones pendientes que afectan a este RF

De `venta_de_normas.md` §6, las que impactan la Fase N1:

- **E19** — 887 productos vs 846 publicados: migrar todos, publicar sólo los que
  lo estaban. *Confirmar con ONN.*
- **E8** — 30 productos sin PDF: si no hay documento, no se publica.
- **E13** — ¿se permite un carrito mixto de normas y servicios? La recomendación
  del análisis es **no**: son circuitos distintos. Afecta cómo se presenta la
  tienda al cliente logueado.

Las restantes (cupo de descargas, versión comprada vs vigente, compras
históricas) pertenecen a la Fase N2 y no bloquean RF 2.9.

---

## 7. Referencias

- Tarea: [86e0yxqnm](https://app.clickup.com/t/86e0yxqnm)
- Análisis y plan completo: [`docs/design/venta_de_normas.md`](../../design/venta_de_normas.md)
- Navegación del portal: [`docs/design/portal_navegacion.md`](../../design/portal_navegacion.md) §1, Fase D
- `docs/project/user-stories/SPRINT_1_5_COMPLIANCE_CHECKLIST.csv` → US-S3-09
- Commits de documentación: `28b50bc8`, `461f4a5d`
