# pdf-extractext

## Descripción del Proyecto

La funcionalidad principal de este proyecto es permitirle a un usuario ingresar un archivo PDF para que el software realice la transcripción del texto contenido en dicho PDF y genere un archivo `.txt` con el mismo contenido.

## Tareas del Proyecto

>>### Comprobación de Existencia

El software, al recibir el archivo PDF, verificará que la dirección local donde se encuentra el documento exista en el dispositivo en el que se está utilizando.

>>### Lectura de PDF

La aplicación podrá realizar la lectura de enunciados escritos dentro del archivo PDF brindado por el usuario, reconociendo caracteres de índole alfabética y numérica.

>>>#### Corroboración de Lenguaje Aceptado

El software, al realizar la lectura del archivo PDF, corroborará si los caracteres utilizados en el texto son válidos y aceptados por el sistema.

>>>#### Corroboración de Contenido Existente

El software comprobará que el PDF posea contenido y que este no se encuentre vacío, o que no contenga únicamente imágenes escaneadas, lo cual imposibilitaría la lectura del texto.

>>### Transcripción de Contenido

El software transcribirá el contenido legible del archivo PDF en un archivo `.txt`.

>>### Creación de Archivos TXT

El software dará la opción al usuario de crear un archivo `.txt` en el cual se encuentre el contenido transcrito del PDF.

## Estructura de la Aplicación

El desarrollo de este software se basa en una estructura de 3 capas:

>>### Capa de Presentación

En esta capa el usuario podrá cargar el archivo PDF que desea transcribir a `.txt`. Aquí se instruirá al usuario sobre cómo utilizar el software.

>>### Capa de Aplicación

Contendrá la lógica principal del sistema, encargada de coordinar las operaciones de lectura, validación y transcripción.

>>### Capa de Acceso a los Datos

Se encargará de gestionar la interacción con los archivos PDF y la creación de los archivos `.txt`.

## Tecnologías

- Python  
- UV  
- Kimi K2.5  
- Ollama  
- MongoDB (base de datos no relacional)

## Metodologías

- TDD (Test Driven Development)  
- Proyecto dirigido en GitHub  
- Aplicación de los seis primeros principios de 12-Factor App  

## Principios de Programación

- KISS (Keep It Simple, Stupid)  
- DRY (Don't Repeat Yourself)  
- YAGNI (You Aren’t Gonna Need It)  
- SOLID  