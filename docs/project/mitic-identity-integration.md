# MITIC Electronic Identity (Identidad Electrónica) — integration state

Login with Paraguay's national digital identity (MITIC / Portal Paraguay).
ClickUp: **RF 2.8** (`86e0yxqmf`). Module: `custom_addons/intn_portal/intn_portal_hybrid_auth`.

> **Status:** implemented as an authorization-code flow scaffold, **not finished**.
> Blocked on MITIC's technical documentation to confirm endpoints, flow and the
> userinfo schema. Do **not** commit any client secret to the repo — it lives
> only in Settings (`ir.config_parameter`).

## Why it is not "just configuration"

The module was originally built on Odoo's stock `auth_oauth`, which does the
**implicit flow** (`response_type=token`, no client secret, fixed callback
`/auth_oauth/signin`). MITIC delivered a **client secret** and a dedicated
**`/redirect_ie`** callback — that is the **authorization-code flow**, which Odoo
core does not do. So configuration alone would not have worked.

There is also **no public OIDC discovery**: `/.well-known/openid-configuration`
on `devlogin.mitic.gov.py`, `devidentidad.mitic.gov.py` and
`identidad.paraguay.gov.py` all return the login SPA, not JSON. The developer
docs live on `devportalpy.mitic.gov.py/documentos`, which is not reachable from
outside Paraguay.

## What is implemented (branch `18.0-feat-mitic_identity_login_restyle`)

- **Config (dev-mode only).** `res.config.settings` exposes the MITIC provider
  fields plus `MITIC client secret` and `MITIC token endpoint`, stored as
  `ir.config_parameter`. The whole "INTN Hybrid Auth" settings block is gated by
  `groups="base.group_no_one"`, so it only shows to an administrator with
  developer mode active.
- **Authorization-code link.** `IntnHybridAuthHome.list_providers` rebuilds the
  MITIC provider link with `response_type=code` and `redirect_uri=.../redirect_ie`
  (other providers keep Odoo's default implicit link).
- **`/redirect_ie` controller** (`IntnMiticOAuthController`): receives the code,
  exchanges it for a token at the configured token endpoint
  (`client_secret_post`), then hands the access token to the standard
  `res.users.auth_oauth`, so the existing MITIC claim mapping
  (`res_users._intn_extract_mitic_identity` / `_auth_oauth_signin`) is reused
  unchanged (cédula → `vat`, name, email, subject; partner locked as
  `intn_identity_source=mitic`).
- **Login restyle.** INTN logo + divider on top of the already-branded login
  card (`intn_brand_theme`), and a tidied foreign-signup form. Source strings are
  kept verbatim so the `es_PY.po` translations still apply.

## Configuration (staging)

Set on the staging DB, in **Settings → developer mode**, the "INTN Hybrid Auth"
block, using the DEV credentials from the ClickUp card (never in the repo):

- `web.base.url` must match the host registered with MITIC (DEV callback points
  to `http://intn.freelancerpy.com:8069/redirect_ie`, i.e. testing is on staging,
  not local).
- MITIC client id, **client secret**, authorization endpoint, **token endpoint**,
  validation (userinfo) endpoint, scope, and enable the provider.

## Pending from MITIC (needed to finish + test)

Requested on the ClickUp card. To confirm against MITIC's docs:

1. Exact flow (authorization code; with or without PKCE).
2. Real URLs: authorize / token / userinfo (current values are placeholders).
3. Token-endpoint auth method (`client_secret_post` vs `client_secret_basic`).
4. Required scopes.
5. `userinfo` field names for cédula, given/family name and email. The mapping
   already accepts many aliases (`cedula|ci|document_number|…`, `name|full_name|…`,
   `email|correo|…`, `sub|user_id|…`) but must match a definitive negative answer.
6. Confirm the redirect URI (`/redirect_ie`) for DEV and PROD.

## Testing

- `intn_portal_hybrid_auth` tests cover the claim mapping and the login/signup
  render. Run with the language loaded: `--load-language=es_PY` (several tests
  assert the es_PY strings and use `with_context(lang="es_PY")`).
- The `/redirect_ie` token round-trip against MITIC is **not** covered yet: the
  request/response shapes depend on the pending spec, so a mocked test would be
  written against guessed formats. Add it once the spec is confirmed.

## Gotchas

- Translation convention: **English source + `es_PY.po`**. Changing a source
  string, or inserting active `.po` entries after the obsolete `#~` block, breaks
  the translation match and the render tests.
- `.btn-intn-cta` is scoped to `.o_portal_wrap`; on the login page
  (`.o_database_list`) the brand CTA comes from `.o_database_list .btn-primary`.
