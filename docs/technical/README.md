# Documentación técnica (Sphinx)

Build local estilo ReadTheDocs de la documentación de módulos custom.

## Requisitos

```bash
.venv/bin/pip install -r docs/technical/requirements-docs.txt
sudo pacman -S graphviz   # binario `dot` del sistema (para los diagramas)
```

## Servir / build

```bash
scripts/serve-docs.sh                  # live-reload en http://localhost:8400
make -C docs/technical html            # build estático → _build/html/index.html
```

El sitio incluye también las guías de `docs/admin/` y `docs/portal/` (symlinks `admin`/`portal` dentro de esta carpeta). Puerto configurable con `DOCS_PORT` (8400 por defecto; no choca con Odoo dev 8069 ni los shell runs 8199).

`_build/` está gitignored. En CI/pre-merge usar `SPHINXOPTS="-W --keep-going"` para que los warnings sean fatales.

## Regenerar páginas de módulos y diagramas

Las páginas bajo `generated/` (una por módulo + diagramas `.dot` por módulo y por grupo de addons) se emiten desde el **registry** de Odoo, no desde las clases Python crudas. Se regeneran contra la DB sandbox de verificación **sin tocar el dev server vivo**:

```bash
scripts/run-technical-docs.sh
# equivale a:
# .venv/bin/python src/odoo/odoo-bin shell -c odoo.conf -d intn_verify_1784261328 \
#   --http-port 8199 --gevent-port 8299 --no-http < scripts/generate-technical-docs.py
```

El script borra y reescribe `generated/` completo de forma determinista (correrlo dos veces no produce diff). Las páginas de `manual/` nunca se tocan.

## Estructura

| Ruta | Contenido | Editable |
|------|-----------|----------|
| `manual/` | Prosa: arquitectura, widgets OWL, formularios de portal, modelo de seguridad | Sí |
| `generated/modules/<module>.md` | Manifest, modelos, campos, vistas, seguridad, menús, rutas | No (generado) |
| `generated/diagrams/*.dot` | Diagramas de clases/relaciones (graphviz) | No (generado) |
| `_static/` | Assets (capturas de widgets, css) | Sí |
