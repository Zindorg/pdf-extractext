# 📄 PDF-Extractext

[![Python 3.13](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248.svg?logo=mongodb)](https://www.mongodb.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Extractor de texto de PDFs con arquitectura de 3 capas y API REST.**

Permite subir archivos PDF, extraer su contenido textual y gestionar los documentos mediante una API RESTful construida con FastAPI.

---

## 📑 Tabla de Contenidos

- [Características](#-características)
- [Requisitos Previos](#-requisitos-previos)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [API Endpoints](#-api-endpoints)
- [Principios Aplicados](#-principios-aplicados)
- [Autores](#-autores)
- [Licencia](#-licencia)

---

## ⭐ Características

- 📄 **Extracción de texto** de PDFs con soporte multi-página
- 🔍 **Validación automática** de archivos (formato, tamaño, contenido no vacío)
- 🗃️ **Almacenamiento persistente** en MongoDB con metadatos completos
- ⚡ **API RESTful** construida con FastAPI y documentación automática
- ✅ **Tests unitarios** con pytest y cobertura de código
- 🏗️ **Arquitectura limpia** de 3 capas (Presentación, Aplicación, Datos)
- 📝 **Generación de archivos `.txt`** con el contenido extraído
- 🔒 **Manejo de errores** robusto con excepciones personalizadas

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- **Python 3.13+** - [Descargar Python](https://www.python.org/downloads/)
- **UV** - Gestor de paquetes ultra-rápido para Python
  - Windows: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
  - Linux/Mac: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **MongoDB** (opcional para desarrollo local)
  - Puede usar [MongoDB Atlas](https://www.mongodb.com/atlas) (gratuito) o instalar localmente

---

### Descripción de Capas

| Capa | Responsabilidad | Componentes |
|------|----------------|-------------|
| **Presentación** | Interfaz HTTP/API | `api/routes/`, `api/schemas/` |
| **Aplicación** | Lógica de negocio | `services/`, `models/` |
| **Datos** | Persistencia y adaptadores | `repositories/`, `infrastructure/` |

---

## 🔌 API Endpoints

La API expone los siguientes endpoints para gestionar archivos PDF:

| Método | Endpoint | Descripción | Request | Response |
|--------|----------|-------------|---------|----------|
| `POST` | `/pdf/upload` | Subir PDF y extraer texto automáticamente | `multipart/form-data` con archivo PDF | `PDFUploadResponse` con metadatos y preview del texto |
| `POST` | `/pdf/{file_id}/extract` | Extraer texto de páginas específicas de un PDF existente | `JSON` con `start_page` y `end_page` opcionales | `PDFExtractResponse` con texto completo |
---

## 🎯 Principios Aplicados

Este proyecto sigue rigurosamente las mejores prácticas de desarrollo de software:

### Metodologías

- ✅ **TDD (Test Driven Development)** - Tests escritos antes del código de producción
- ✅ **Desarrollo dirigido en GitHub** - Control de versiones y gestión de tareas
- ✅ **12-Factor App** - Aplicación de los 6 primeros principios para apps cloud-native

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
- **Dependency Injection** - Inyección de dependencias para testabilidad
- **Repository Pattern** - Abstracción del acceso a datos
- **Adapter Pattern** - Adaptadores para servicios externos (extracción PDF)

---

## 👥 Autores

Proyecto desarrollado por el equipo de **PDF-Extractext** como trabajo práctico universitario.

| Nombre | Rol | GitHub |
|--------|-----|--------|
| **Zinik Facundo** | - | [@Facundo Nahuel Zinik](https://github.com/Zindorg) |
| **Velez Marcos** | - |[@Marcos Velez](https://github.com/marcos-velez-20) |
| **Gonzalez Ignacio Matias** | - | [@Matias Ignacio Gonzalez](https://github.com/MatiGonza3)|
| **Monardi Dalma** | - | [@Dalma Monardi](https://github.com/DalmaM1105) |

---

## 📄 Licencia

```
MIT License

Copyright (c) 2025 Equipo PDF-Extractext

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<div align="center">
  <p>⭐ Desarrollado con Python, FastAPI y MongoDB ⭐</p>
  <p>
    <a href="https://github.com/Zindorg/pdf-extractext">GitHub Repository</a>
  </p>
</div>
