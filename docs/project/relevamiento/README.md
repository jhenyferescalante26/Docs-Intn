# Documentación de proyecto — relevamiento INTN

Material **no operativo** (talleres, pliego, alcance contractual). La documentación operativa está en [`docs/admin/`](../../admin/README.md), [`docs/portal/`](../../portal/README.md) y [`docs/technical/`](../../technical/README.md).

## Índice

| Documento | Descripción |
|-----------|-------------|
| [matriz-pliego-relevamiento.md](matriz-pliego-relevamiento.md) | Export XLSX Relevamiento vs Pliego |
| [cuestionario-alcance-2025-12.md](cuestionario-alcance-2025-12.md) | Cuestionario 17/12/2025 |
| [plan-freelancer-v2-resumen.md](plan-freelancer-v2-resumen.md) | Plan propuesto v2 |
| [pliego-resumen.md](pliego-resumen.md) | Extracto PBC (referencia) |
| [extracted/](extracted/README.md) | Texto íntegro extraído de PDF/DOCX/XLSX y assets visuales |
| [minutas/INDEX.md](minutas/INDEX.md) | Minutas y resúmenes de reunión por fecha |
| [MAPPING.md](MAPPING.md) | Inventario archivo original → organismo, proceso `NN`, cobertura, ruta markdown |
| [COVERAGE_AUDIT.md](COVERAGE_AUDIT.md) | Auditoría automática archivo → markdown (**no** mide producto Odoo) |
| [BACKLOG.md](BACKLOG.md) | Brechas transversales e ítems Won't Have / Could Have del pliego |

## Regenerar

Requiere copia local de `docs/original_docs/Proyecto INTN APPEX Freelancer/` (no versionada en git).

```bash
python scripts/extract-relevamiento-sources.py
python scripts/export-relevamiento-matrix.py
python scripts/generate-relevamiento-mapping.py
python scripts/audit-relevamiento-coverage.py
```
