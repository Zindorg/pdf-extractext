# Contexto de diseño — PDF-Extractext

Decisiones de arquitectura y de testing acordadas. Si algo de esto cambia,
actualizar este archivo en el mismo PR.

## Arquitectura

Arquitectura en capas con **puertos y adaptadores** en los dos bordes de
salida (persistencia y extracción de texto). La regla de dependencia es:

```
routes / schemas / api  ──►  use_cases  ──►  domain  ◄──  infrastructure
                 ▲                                            ▲
                 └──────────  dependencies.py  ───────────────┘
                          (composition root + settings)
```

| Paquete | Contiene | Puede importar |
|---|---|---|
| `app/domain` | `PDFDocument`, reglas puras (`pdf_rules`), puertos (`PDFRepository`, `PDFTextExtractor`) | solo `app.exceptions` y la stdlib |
| `app/use_cases` | Un caso de uso por operación: `UploadPDF`, `ListPDFs`, `GetPDF`, `DeletePDF` | `domain`, `exceptions` |
| `app/infrastructure` | Adaptadores: `MongoPDFRepository`, `PypdfTextExtractor`, `database_setup` | `domain`, drivers externos |
| `app/routes`, `app/schemas`, `app/api` | HTTP: rutas, DTOs (`from_document`), handlers RFC 9457 | `use_cases`, `domain`, `dependencies` |
| `app/dependencies.py` | Único lugar que conoce concretos y `settings` | todo |

Reglas:

- **El dominio y los casos de uso no importan FastAPI, pymongo, pypdf ni `settings`.**
  La configuración (p. ej. `max_file_size`) se inyecta por constructor.
- **El mapeo entidad → DTO vive en el schema** (`PDFUploadResponse.from_document`, etc.).
- **Los adaptadores traducen errores de librería a excepciones del dominio**
  (`PDFExtractionException`, `RepositoryException`). Nunca se convierte un
  error de infraestructura en "no encontrado".
- No se agregan capas de paso: si un módulo solo delega, se elimina.

## Seams de testing

| Seam | Qué se prueba | Dobles | Archivo |
|---|---|---|---|
| HTTP | Contrato de la API (status, cuerpo, cabeceras) con el cableado real | `InMemoryPDFRepository` vía `dependency_overrides[get_pdf_repository]`; pypdf real | `tests/unit/api/test_pdf_api.py` |
| Caso de uso | Reglas de negocio de la subida | `InMemoryPDFRepository` + `FakeTextExtractor` | `tests/unit/use_cases/` |
| Dominio | Reglas puras | ninguno | `tests/unit/domain/` |
| Puerto `PDFRepository` | Contrato común a todas las implementaciones | se ejecuta contra fake, mongomock y MongoDB real | `tests/contract/` |
| Adaptadores | Comportamiento propio (pypdf con PDFs reales, errores de Mongo, índice único) | PDFs generados con reportlab, mongomock | `tests/unit/infrastructure/` |

Reglas:

- Se testea a través de interfaces públicas. No se accede a atributos
  privados (`_collection`) ni se asertan llamadas a mocks propios.
- Se prefieren **fakes con comportamiento** a `MagicMock`. Un fake nuevo
  debe pasar el test de contrato de su puerto.
- Cada test tiene al menos una aserción sobre un efecto observable.
- Los tests de MongoDB real usan la base `<MONGODB_DATABASE>_test` y se
  omiten si no hay servidor.
- Flujo TDD: el test se commitea en rojo antes del código que lo pone en
  verde cuando se corrige un bug o se agrega una regla.
