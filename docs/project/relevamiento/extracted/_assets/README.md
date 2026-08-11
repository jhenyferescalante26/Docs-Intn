# Assets visuales del relevamiento

Copias de archivos que no se transcriben bien a texto plano (flujogramas JPG, capturas PNG/JPEG, plantillas `.doc` legacy).

## Política

| Tipo | Tratamiento en git |
|------|-------------------|
| JPG / PNG / JPEG | Copia en `_assets/` + índice `.md` en `extracted/` con enlace `![...](_assets/...)` |
| PDF flujograma | Texto extraído en `.md` homólogo; conservar PDF solo fuera del repo si hace falta la vista exacta |
| `.doc` (Word 97-2003) | Copia en `_assets/` + índice que apunta al binario |
| `.mp4` | Solo índice markdown; video fuera del repositorio (Drive o copia local de `original_docs`) |
| `.zip` | Índice con listado de entradas; formularios internos se extraen manualmente si se requieren |

## Regenerar

Con copia local de fuentes en `docs/original_docs/` (o `--root`):

```bash
python scripts/extract-relevamiento-sources.py
```

## Git LFS

No es obligatorio para imágenes de relevamiento (tamaño moderado). Si el repo crece, valorar LFS solo para `_assets/**/*.jpg` y certificados PDF de muestra.
