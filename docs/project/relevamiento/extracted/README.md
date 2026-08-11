# Texto extraído del relevamiento

Transcripciones y tablas generadas desde `docs/original_docs/Proyecto INTN APPEX Freelancer/`.

## Estructura

- Rutas bajo `extracted/` reflejan la carpeta original (segmentos con guiones).
- Imágenes y `.doc` legacy: [`_assets/`](_assets/README.md).
- Minutas y documentos de proyecto (matriz, cuestionario, plan): [`../`](../README.md).

## Regenerar todo

```bash
python scripts/extract-relevamiento-sources.py
python scripts/export-relevamiento-matrix.py
python scripts/generate-relevamiento-mapping.py
python scripts/audit-relevamiento-coverage.py
```

## Fuentes fuera del repositorio

Los binarios originales no se versionan en git (ver [`docs/project/relevamiento/README.md`](../README.md)). Mantener un archivo ZIP o carpeta sincronizada para re-ejecutar los scripts con `--root`.
