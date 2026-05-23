# PDF-Extractext

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248.svg?logo=mongodb)](https://www.mongodb.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Extractor de texto de PDFs con arquitectura de 3 capas y API REST.**

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
- **Validación automática** de archivos (formato, tamaño, contenido no vacío)
- **Almacenamiento persistente** en MongoDB con metadatos completos
- **API RESTful** construida con FastAPI y documentación automática
- **Tests unitarios** con pytest y cobertura de código
- **Arquitectura limpia** de 3 capas (Presentación, Lógica de Negocio, Repositorios)
- **Generación de archivos `.txt`** con el contenido extraído
- **Manejo de errores** robusto con excepciones personalizadas

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

Copiar el archivo de ejemplo y editar las variables necesarias:

```bash
cp .env.example .env
```

Variables esenciales del archivo `.env`:

```bash
# Zona horaria
TZ=America/Argentina/Mendoza

# Credenciales de MongoDB
USERNAME=root
PASSWORD=qwerty1234
MONGO_DATA_PATH=/ruta/a/datos/mongodb

# URI de conexión a MongoDB
MONGODB_URI=mongodb://root:qwerty1234@localhost:27017/?authSource=admin
```

### 3. Instalar dependencias

```bash
uv sync
```

Para desarrollo (incluye dependencias de testing):

```bash
uv sync --extra dev
```

### 4. Configurar permisos en Docker (opcional)

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### 5. Levantar MongoDB

```bash
mkdir -p ~/microservicios/mongodb/data
docker compose -f mongodb-docker-compose.yml up -d
```

> **Nota para usuarios de Windows:** En Windows se pueden usar los mismos comandos en WSL o adaptar rutas a `C:\data\mongodb`.

### 6. Ejecutar la aplicación

#### Opción A: Con UV (desarrollo)

```bash
uv run python -m app.main
```

La API estará disponible en: **http://localhost:8000**

Documentación interactiva: **http://localhost:8000/docs**

#### Opción B: Con Docker Compose (producción)

```bash
# Build y levantar el contenedor
docker compose -f app-docker-compose.yml up --build -d
```

El comando anterior realiza automáticamente el `build` de la imagen (`pdf-extractext:v1.0.1`) a partir del `Dockerfile` en el contexto raíz.

#### Opción C: Con Docker run manual

```bash
# Build manual de la imagen
docker build -t pdf-extractext:v1.0.1 .

# Levantar contenedor
docker run -p 8000:8000 --env-file .env pdf-extractext:v1.0.1
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
| `httpx` | >=0.28.1 | Cliente HTTP para tests de integración |

### Desarrollo (opcional)

| Dependencia | Versión | Uso |
|-------------|---------|-----|
| `reportlab` | >=4.5.0 | Generación y manipulación de archivos PDF |

---

## Estructura del Proyecto

El proyecto sigue una arquitectura de **3 capas** que separa claramente las responsabilidades:

### Descripción de Capas

| Capa | Responsabilidad | Componentes |
|------|----------------|-------------|
| **Presentación** | Interfaz HTTP/API | `main.py`, `routes/`, `api/`, `schemas/`, `dependencies.py` |
| **Lógica de Negocio** | Casos de uso y reglas de negocio | `use_cases/`, `services/`, `models/`, `exceptions/` |
| **Repositorios** | Persistencia y adaptadores | `repositories/`, `infrastructure/`, `config/` |

### Árbol Visual del Proyecto

```
pdf-extractext/
├── app/                          # Capa de aplicación principal
│   ├── api/                      # Manejadores de excepciones (Presentación)
│   ├── config/                   # Configuración de entornos (Repositorios)
│   ├── infrastructure/           # Extractor de PDFs, setup DB (Repositorios)
│   ├── models/                   # Entidades de dominio (Lógica de Negocio)
│   ├── repositories/             # Acceso a MongoDB (Repositorios)
│   ├── routes/                   # Endpoints HTTP (Presentación)
│   ├── schemas/                  # DTOs / Serialización (Presentación)
│   ├── services/                 # Lógica de negocio especializada (Lógica de Negocio)
│   ├── use_cases/                # Orquestación de casos de uso (Lógica de Negocio)
│   ├── dependencies.py           # Inyección de dependencias (Presentación)
│   ├── exceptions/               # Excepciones del dominio (Lógica de Negocio)
│   └── main.py                   # Punto de entrada FastAPI (Presentación)
├── tests/                        # Tests unitarios e integración
├── documents/                    # Documentos de ejemplo
├── Dockerfile                    # Build de imagen Docker
├── app-docker-compose.yml        # Compose de la aplicación
├── mongodb-docker-compose.yml    # Compose de MongoDB
└── README.md                     # Este archivo
```

---

## API Endpoints

La API expone los siguientes endpoints para gestionar archivos PDF:

| Método | Endpoint | Descripción | Request | Response |
|--------|----------|-------------|---------|----------|
| `GET` | `/api/v1/pdfs` | Listar todos los PDFs persistidos | — | `PDFListResponse` |
| `GET` | `/api/v1/pdfs/{doc_id}` | Obtener un PDF por ID | — | `PDFDetailResponse` |
| `POST` | `/api/v1/pdfs` | Subir PDF y extraer texto automáticamente | `multipart/form-data` con archivo PDF | `PDFUploadResponse` con metadatos y preview del texto |
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

- **Clean Architecture** - Separación clara de responsabilidades

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
