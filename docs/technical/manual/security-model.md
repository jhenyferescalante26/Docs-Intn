# Modelo de seguridad

Vista general de grupos, reglas de registro y autenticación. Las tablas exactas de ACL, grupos y reglas por módulo están en las páginas generadas de [Módulos](../generated/index.md).

## Grupos por dominio

| Dominio | Módulo que los define | Jerarquía |
|---------|----------------------|-----------|
| Organismos MRP | `intn_mrp_organism_access` (`security/security.xml`) | `group_intn_mrp_organism_user` (base) ← grupos por organismo (ONI, ONC, ONM, ONN, OIAT, DSE, METCI); `group_intn_mrp_audit_admin` implica `mrp.group_mrp_manager` |
| OIAT | `intn_mrp_oiat` | técnico → jefe de departamento → jefe de unidad → aprobador de certificados |
| Cisternas | `intn_fleet_cisterns` (`security/cistern_security.xml`) | `cistern_group_user` (implica `fleet.fleet_group_user`) ← manager / technician / measurement_reprint |
| Documentos | `intn_documents` (`security/intn_documents_security.xml`) | `group_intn_documents_department_scoped` (base) ← fleet / metrology / generic; `group_intn_documents_auditor` lo bypassea |
| Solicitudes | `intn_service_request` | `group_intn_document_reviewer`, `group_atc_customer_attention` |
| Marcas | `intn_brand_service_requests`, `intn_onc_certification_requests` | manager / printer / sampling / onn_normas; `group_intn_onc_reviewer` |
| Contabilidad | `intn_account_payment_group`, `intn_account_bank_transfer` | collector / payment_order / cancel_receipts; bank_transfer viewer / manager |
| Ventas | `intn_sale_agreement`, `intn_sale_additional_costs`, `intn_sale_price_update`, `intn_partner_credit_limit` | manager/viewer por módulo |
| Portal fleet | `intn_fleet_cistern` (`security/fleet_portal_security.xml`) | `fleet_group_portal` implicado en `base.group_portal` |

## Reglas de registro: dos patrones dominantes

1. **Aislamiento por organismo (MRP)** — `intn_mrp_organism_access` aísla `mrp.production`, `mrp.workorder`, `mrp.workcenter` y scraps por organismo, con reglas de bypass para managers.
2. **Alcance por partner comercial (portal)** — dominios tipo `[('partner_id', 'child_of', user.commercial_partner_id.ids)]` en vehículos fleet, solicitudes de impresión de marca, certificados ONC y documentos. Un usuario de portal solo ve los registros de su empresa.

## Autenticación de portal (`intn_portal_hybrid_auth`)

Autenticación híbrida MITIC / extranjeros:

- Ciudadanos paraguayos → OAuth **MITIC** (`provider_mitic`).
- Extranjeros → registro manual (`signup_mode == "manual_foreign"`).
- `IntnIdentityValidationService` (`models/identity_validation_service.py`) clasifica el documento (`classify_document` → national/foreign/unknown) y `validate_manual_foreign` bloquea a paraguayos en el alta manual.
- Controller: `IntnHybridAuthHome(OAuthLogin, IntnAuthSignupHome)` en `controllers/main.py`; configuración en `res.config.settings`.

El alta de clientes con aprobación ATC (previa al acceso) vive en `rf_customer_registration` + `intn_portal_registration`.
