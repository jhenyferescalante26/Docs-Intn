# Documentación INTN

La documentación del proyecto se divide en **tres conjuntos** más los registros de proyecto.

| Conjunto | Carpeta | Audiencia | Contenido |
|----------|---------|-----------|-----------|
| **Administración** | [`admin/`](admin/README.md) | Personal INTN (backoffice) | Operación de cada proceso en el escritorio Odoo, por dominio y rol, con capturas |
| **Técnica** | [`technical/`](technical/README.md) | Desarrolladores | Módulos custom: modelos, vistas, widgets, permisos. Sphinx + páginas generadas desde el registry con diagramas de clases |
| **Portal** | [`portal/`](portal/README.md) | Clientes externos | Pasos de cada trámite disponible en el portal web, con capturas |
| Registros de proyecto | [`project/`](project/README.md) | PM / contractual | Relevamiento, minutas, user stories, plan de migración de datos, i18n |

## Capturas de pantalla

Las capturas se generan automáticamente, nunca a mano. Hay **dos mecanismos** conviviendo mientras
el suite de Playwright se retira; ver [`project/plan-tours-portal.md`](project/plan-tours-portal.md).

**Tours de Odoo** — el mecanismo al que se está migrando. El paso `docScreenshot("<dominio>/<nombre>")`
dentro del tour pide la captura, y la clase de test mezcla `PortalTourScreenshotMixin`:

```bash
export ODOO_BROWSER_BIN=~/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome
INTN_DOC_SCREENSHOTS=1 .venv/bin/python src/odoo/odoo-bin -c odoo.conf.local --no-http \
  -d <db> --stop-after-init --test-enable --test-tags intn_portal_tours
```

Sin `INTN_DOC_SCREENSHOTS=1` el marcador se emite y nadie lo escucha, así que CI nunca escribe en
`docs/`.

**Playwright** — el mecanismo que se retira, todavía responsable de la mayoría de las imágenes:

```bash
cd e2e
CAPTURE_DOC_SCREENSHOTS=1 npm run doc:screenshots            # todas
CAPTURE_DOC_SCREENSHOTS=1 npm run doc:screenshots:cisternas  # un dominio
```

Los dos escriben en `docs/admin/_images/<dominio>/` y `docs/portal/_images/<dominio>/`, con los
mismos nombres de archivo: una imagen migrada a un tour se regenera en su lugar, sin renombrar.

## Servir la documentación en local

El sitio Sphinx incluye los **tres conjuntos** (técnica + guía admin + guía portal) con live-reload:

```bash
.venv/bin/pip install -r docs/technical/requirements-docs.txt   # una vez
scripts/serve-docs.sh          # → http://localhost:8400 (DOCS_PORT para cambiarlo)
```

Build estático sin servidor: `make -C docs/technical html` → `docs/technical/_build/html/index.html`.

Las páginas por módulo y los diagramas se regeneran con `scripts/run-technical-docs.sh` (ver `technical/README.md`).
