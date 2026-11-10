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
| `app/domain` | `PDFDocument` (entidad), `UploadedFile` (value object), puertos (`PDFReader`, `PDFWriter`, `PDFTextExtractor`), errores del dominio | solo la stdlib y el propio `domain` |
| `app/use_cases` | Un caso de uso por operación: `UploadPDF`, `ListPDFs`, `GetPDF`, `DeletePDF` | `domain` |
| `app/infrastructure` | Adaptadores: `MongoPDFRepository`, `PypdfTextExtractor`, `database_setup` | `domain`, drivers externos |
| `app/routes`, `app/schemas`, `app/api` | HTTP: rutas, DTOs (`from_document`), traducción de errores a RFC 9457 | `use_cases`, `domain`, `dependencies` |
| `app/dependencies.py` | Único lugar que conoce concretos y `settings` | todo |

`tests/unit/test_architecture.py` hace cumplir la columna "Puede importar"
para `domain` y `use_cases`: si alguien importa FastAPI, pymongo, pypdf,
`app.config` o una capa externa, la suite falla.

Reglas:

- **El dominio y los casos de uso no importan FastAPI, Pydantic, pymongo, pypdf ni `settings`.**
  La configuración (p. ej. `max_file_size`) se inyecta por constructor.
- **Las invariantes viven en el dominio.** `UploadedFile` valida nombre y
  contenido al construirse y calcula checksum y tamaño; `PDFDocument.from_upload`
  rechaza un PDF sin texto.
- **Los errores del dominio no conocen HTTP.** El status y el título de cada
  uno se deciden en `app/api/exception_handlers.py`; cualquier error no
  mapeado es un 500 y su detalle técnico va solo al log.
- **Cada caso de uso depende solo del puerto que usa** (`PDFReader` para leer,
  `PDFWriter` para escribir). `MongoPDFRepository` implementa ambos.
- **La deduplicación la decide el índice único de `checksum`** (a prueba de
  subidas simultáneas); `PDFWriter.create` lanza `DuplicateDocumentException`.
- **El mapeo entidad → DTO vive en el schema** (`PDFUploadResponse.from_document`, etc.).
- **Los adaptadores traducen errores de librería a errores del dominio**
  (`PDFExtractionException`, `RepositoryException`). Nunca se convierte un
  error de infraestructura en "no encontrado".
- No se agregan capas de paso: si un módulo solo delega, se elimina.
  Excepción consciente: `ListPDFs` solo delega en `PDFReader.find_all`; se
  mantiene para que las rutas dependan siempre de casos de uso y no de puertos.

## Seams de testing

| Seam | Qué se prueba | Dobles | Archivo |
|---|---|---|---|
| HTTP | Contrato de la API (status, cuerpo, cabeceras) con el cableado real | `InMemoryPDFRepository` vía `dependency_overrides[get_pdf_repository]`; pypdf real | `tests/unit/api/test_pdf_api.py` |
| Caso de uso | Flujo de la subida | `InMemoryPDFRepository` + `FakeTextExtractor` | `tests/unit/use_cases/` |
| Dominio | Invariantes de `UploadedFile` y `PDFDocument` | ninguno | `tests/unit/domain/` |
| Puertos `PDFReader` + `PDFWriter` | Contrato común a todas las implementaciones | se ejecuta contra fake, mongomock y MongoDB real | `tests/contract/` |
| Adaptadores | Comportamiento propio (pypdf con PDFs reales, errores de Mongo, índice único) | PDFs generados con reportlab, mongomock | `tests/unit/infrastructure/` |
| Arquitectura | Regla de dependencias | ninguno (analiza imports) | `tests/unit/test_architecture.py` |

Reglas:

- Se testea a través de interfaces públicas. No se accede a atributos
  privados (`_collection`) ni se asertan llamadas a mocks propios.
- Se prefieren **fakes con comportamiento** a `MagicMock`. Un fake nuevo
  debe pasar el test de contrato de su puerto.
- Cada test tiene al menos una aserción sobre un efecto observable.
- Los tests de MongoDB real usan la base `<MONGODB_DATABASE>_test` y se
  omiten si no hay servidor.
- Flujo TDD: cuando se corrige un bug o se cambia un comportamiento, el
  test se commitea primero en rojo (`test(...)`) y después el código que lo
  pone en verde (`fix(...)` / `feat(...)`). Los refactors sin cambio de
  comportamiento se apoyan en la suite existente.
