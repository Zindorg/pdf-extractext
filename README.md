# PDF-Extractext

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248.svg?logo=mongodb)](https://www.mongodb.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Extractor de texto de PDFs con API REST, arquitectura en capas y puertos/adaptadores.**

Permite subir archivos PDF, extraer su contenido textual y gestionar los documentos mediante una API RESTful construida con FastAPI.

---

## Tabla de Contenidos

- [Características](#características)
- [Requisitos Previos](#requisitos-previos)
- [Preparación y Ejecución](#preparación-y-ejecución)
- [Dependencias](#dependencias)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [API Endpoints](#api-endpoints)
- [Principios Aplicados](#principios-aplicados)
- [Autores](#autores)
- [Licencia](#licencia)

---

## Características

- **Extracción de texto** de PDFs con soporte multi-página
- **Validación automática** de archivos (extensión, tamaño máximo, contenido no vacío, PDF legible y con texto)
- **Deduplicación** por checksum SHA-256 (un PDF repetido responde `409 Conflict`)
- **Almacenamiento persistente** en MongoDB con metadatos completos
- **API RESTful** construida con FastAPI y documentación automática
- **Tests** con pytest: contrato HTTP, casos de uso con fakes y contrato del repositorio contra MongoDB
- **Arquitectura en capas** con puertos y adaptadores para persistencia y extracción (ver [`CONTEXT.md`](CONTEXT.md))
- **Generación de archivos `.txt`** con el contenido extraído
- **Errores** en formato RFC 9457 (Problem Details)

---

## Requisitos previos

- **Python 3.13+
- **UV**
- **Docker Engine/Docker Desktop 29.4.1**

---

## Preparación y Ejecución

### 1. Clonar y acceder al repositorio

```bash
git clone https://github.com/Zindorg/pdf-extractext
cd pdf-extractext
```

### 2. Configurar variables de entorno

#### Para ejecución directa (uvicorn)
Copiar el archivo de ejemplo:
```bash
cp .env.example .env
```

Variables disponibles:
- `APP_NAME` — Nombre de la aplicación (default: `PDF Extractext`)
- `DEBUG` — Modo debug (`True`/`False`, default: `False`)
- `MAX_FILE_SIZE` — Tamaño máximo de archivo en bytes (default: `10485760`)
- `MONGODB_DATABASE` — Nombre de la base de datos (default: `pdf_extractext`)
- `MONGODB_URI` — URI de conexión a MongoDB (default: `mongodb://root:qwerty1234@localhost:27017/?authSource=admin`)

#### Para ejecución con Docker
Las variables necesarias para los docker-compose se declaran en un archivo `.env` dentro de cada directorio o se pasan inline:

**docker/mongodb/docker-compose.yml** requiere:
- `TZ` — Zona horaria (ej: `America/Argentina/Mendoza`)
- `USERNAME` — Usuario de MongoDB (ej: `root`)
- `PASSWORD` — Contraseña de MongoDB (ej: `qwerty1234`)
- `MONGO_DATA_PATH` — Ruta local para persistencia (ej: `~/microservicios/mongodb/data`)

**docker/app/docker-compose.yml** requiere:
- `TZ` — Zona horaria
- `VERSION` — Tag de la imagen Docker (ej: `1.0.3`)
- `MONGODB_URI` — URI para conexión entre contenedores (ej: `mongodb://root:qwerty1234@mongodb:27017/?authSource=admin`)

### 3. Instalar dependencias

```bash
uv sync
```

Para desarrollo (incluye dependencias de testing):

```bash
uv sync --extra dev
```

Ejecutar los tests:

```bash
uv run pytest                      # toda la suite; los tests contra MongoDB se omiten si no hay servidor
uv run pytest -m "not integration" # solo los que no necesitan MongoDB
```

Los tests de integración usan la base `<MONGODB_DATABASE>_test` y la eliminan al terminar.

### 4. Configurar permisos en Docker (opcional)

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### 5. Levantar MongoDB

```bash
mkdir -p ~/microservicios/mongodb/data
docker network create mired || true
cp docker/mongodb/.env.example docker/mongodb/.env
docker compose -f docker/mongodb/docker-compose.yml up -d
```

> **Nota para usuarios de Windows:** En Windows se pueden usar los mismos comandos en WSL o adaptar rutas a `C:\data\mongodb`.

### 6. Ejecutar la aplicación

```bash
cp docker/app/.env.example docker/app/.env
docker build -t pdf-extractext:v$(grep VERSION docker/app/.env | cut -d= -f2) .

docker compose -f docker/app/docker-compose.yml up -d
```

### 7. Endpoints de ejemplo (terminal)

**Subir un PDF:**

```bash
curl -X POST "http://localhost:8000/api/v1/pdfs" \
  -F "file=@ruta-al-archivo.pdf"
```

**Listar todos los PDFs:**

```bash
curl -X GET "http://localhost:8000/api/v1/pdfs"
```

**Obtener texto extraído:**

```bash
curl -X GET "http://localhost:8000/api/v1/pdfs/{doc_id}/text"
```

**Descargar texto como .txt:**

```bash
curl -X GET "http://localhost:8000/api/v1/pdfs/{doc_id}/download"
```

**Eliminar un PDF:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/pdfs/{doc_id}"
```

---

## Dependencias

Este proyecto utiliza **[uv](https://docs.astral.sh/uv/)** como gestor de paquetes y requiere **Python >= 3.13**.

### Producción

| Dependencia | Versión | Uso |
|-------------|---------|-----|
| `fastapi` | >=0.136.1 | Framework web para construir la API REST |
| `uvicorn[standard]` | >=0.46.0 | Servidor ASGI para ejecutar la aplicación |
| `python-multipart` | >=0.0.27 | Parseo de formularios multipart (subida de archivos) |
| `pypdf` | >=6.10.2 | Extracción de texto de archivos PDF |
| `pydantic` | >=2.13.3 | Validación de datos y serialización |
| `pydantic-settings` | >=2.14.0 | Gestión de configuración mediante variables de entorno |
| `pymongo` | >=4.17.0 | Cliente y driver para MongoDB |
| `python-dotenv` | >=1.2.2 | Carga de variables de entorno desde archivos `.env` |

### Testing (opcional)

| Dependencia | Versión | Uso |
|-------------|---------|-----|
| `pytest` | >=9.0.3 | Framework de testing |
| `pytest-asyncio` | >=1.3.0 | Soporte para tests asíncronos |
| `pytest-cov` | >=7.1.0 | Medición de cobertura de código |
| `httpx` | >=0.28.1 | Cliente HTTP de `TestClient` |
| `reportlab` | >=4.5.0 | Genera PDFs reales en memoria para los tests |
| `mongomock` | >=4.3.0 | MongoDB en memoria para el test de contrato del repositorio |

---

## Estructura del Proyecto

Arquitectura **en capas** con **puertos y adaptadores** en los bordes de salida
(persistencia y extracción de texto). El dominio y los casos de uso no conocen
FastAPI, MongoDB, pypdf ni la configuración: todo se cablea en `app/dependencies.py`.
Las decisiones y los seams de testing están documentados en [`CONTEXT.md`](CONTEXT.md).

### Descripción de Capas

| Capa | Responsabilidad | Componentes |
|------|----------------|-------------|
| **Presentación** | Interfaz HTTP, DTOs, errores RFC 9457 | `main.py`, `routes/`, `schemas/`, `api/` |
| **Composition root** | Instancia adaptadores e inyecta configuración | `dependencies.py`, `config/` |
| **Casos de uso** | Una clase por operación | `use_cases/` (`UploadPDF`, `ListPDFs`, `GetPDF`, `DeletePDF`) |
| **Dominio** | Entidad, reglas puras y puertos | `domain/` (`PDFDocument`, `pdf_rules`, `PDFRepository`, `PDFTextExtractor`), `exceptions/` |
| **Infraestructura** | Adaptadores de los puertos | `infrastructure/` (`MongoPDFRepository`, `PypdfTextExtractor`, `database_setup`) |

### Árbol Visual del Proyecto

```
pdf-extractext/
├── app/
│   ├── main.py                   # Punto de entrada FastAPI + lifespan (conexión a MongoDB)
│   ├── dependencies.py           # Composition root: cablea adaptadores y settings
│   ├── routes/                   # Endpoints HTTP
│   ├── schemas/                  # DTOs (mapeo desde la entidad con from_document)
│   ├── api/                      # Manejadores de excepciones RFC 9457
│   ├── use_cases/                # upload_pdf, list_pdfs, get_pdf, delete_pdf
│   ├── domain/                   # pdf_document, pdf_rules, ports
│   ├── infrastructure/           # mongo_pdf_repository, pypdf_extractor, database_setup
│   ├── exceptions/               # Excepciones de la aplicación
│   └── config/                   # Settings (pydantic-settings) y logging
├── tests/
│   ├── unit/                     # api (HTTP), use_cases, domain, infrastructure
│   ├── contract/                 # Contrato de PDFRepository: fake, mongomock y MongoDB real
│   └── support/                  # Fakes en memoria y generador de PDFs
├── documents/                    # Diagramas PlantUML de paquetes y clases
├── docker/                       # Docker Compose de la app y de MongoDB
├── CONTEXT.md                    # Decisiones de arquitectura y seams de testing
├── Dockerfile
└── README.md
```

---

## API Endpoints

La API expone los siguientes endpoints para gestionar archivos PDF:

| Método | Endpoint | Descripción | Request | Response |
|--------|----------|-------------|---------|----------|
| `GET` | `/api/v1/pdfs` | Listar todos los PDFs persistidos | — | `PDFListResponse` |
| `POST` | `/api/v1/pdfs` | Subir PDF y extraer texto automáticamente (`409` si ya existe, `422` si es inválido, demasiado grande o sin texto) | `multipart/form-data` con archivo PDF | `PDFUploadResponse` con metadatos y preview del texto |
| `GET` | `/api/v1/pdfs/{file_id}/text` | Obtener texto extraído de un PDF persistido | — | `PDFExtractResponse` con texto completo |
| `GET` | `/api/v1/pdfs/{doc_id}/download` | Descargar texto extraído como archivo `.txt` | — | `text/plain` |
| `DELETE` | `/api/v1/pdfs/{doc_id}` | Eliminar permanentemente un PDF por ID | — | `204 No Content` |

---

## Principios Aplicados

Este proyecto sigue rigurosamente las mejores prácticas de desarrollo de software:

### Metodologías

- **TDD (Test Driven Development)** - Tests escritos antes del código de producción
- **Desarrollo dirigido en GitHub** - Control de versiones y gestión de tareas
- **12-Factor App** - Aplicación de los 6 primeros principios para apps cloud-native

### Principios de Programación

- **KISS** (*Keep It Simple, Stupid*) - Código simple y directo, sin sobre-ingeniería
- **DRY** (*Don't Repeat Yourself*) - Reutilización de código mediante abstracciones
- **YAGNI** (*You Aren't Gonna Need It*) - Implementar solo lo necesario
- **SOLID** - Principios de diseño orientado a objetos:
  - *S*ingle Responsibility: Cada clase tiene una única responsabilidad
  - *O*pen/Closed: Abierto para extensión, cerrado para modificación
  - *L*iskov Substitution: Interfaces bien definidas
  - *I*nterface Segregation: Contratos específicos por rol
  - *D*ependency Inversion: Dependencias de abstracciones, no concretos

### Arquitectura

- **Arquitectura en capas con puertos y adaptadores** - el dominio y los casos de uso dependen de abstracciones (`PDFRepository`, `PDFTextExtractor`); MongoDB y pypdf son adaptadores intercambiables cableados en el composition root

---

## Autores

Proyecto desarrollado por el equipo de **PDF-Extractext** como trabajo práctico universitario.

| Nombre | GitHub |
|--------|--------|
| **Zinik Facundo** | [@Facundo Nahuel Zinik](https://github.com/Zindorg) |
| **Velez Marcos** | [@Marcos Velez](https://github.com/marcos-velez-20) |
| **Gonzalez Ignacio Matias** | [@Matias Ignacio Gonzalez](https://github.com/MatiGonza3) |
| **Monardi Dalma** | [@Dalma Monardi](https://github.com/DalmaM1105) |

---

## Licencia

Este proyecto está bajo la [Licencia MIT](LICENSE).
