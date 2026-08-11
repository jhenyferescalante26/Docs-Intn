# Documentación INTN Odoo 18

Sitio único con los tres conjuntos de documentación del proyecto:

- **Manual técnico** y **Módulos** (desarrolladores): las páginas de módulos y diagramas se **generan** desde el registry de Odoo con `scripts/generate-technical-docs.py` — no editarlas a mano.
- **Guía de administración** (personal INTN, backoffice).
- **Guía de portal** (clientes externos).

```{toctree}
:maxdepth: 1
:caption: Manual

manual/architecture
manual/widgets
manual/portal-forms
manual/portal-forms-guia
manual/portal-forms-estructura
manual/security-model
```

```{toctree}
:maxdepth: 2
:caption: Módulos (generado)

generated/index
```

```{toctree}
:maxdepth: 2
:caption: Guía de administración

admin/README
```

```{toctree}
:maxdepth: 2
:caption: Guía de portal

portal/README
```
