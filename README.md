# Flask API Server

Este proyecto proporciona una API RESTful utilizando Flask para transcribir audio, generar respuestas con modelos de lenguaje y crear imágenes mediante las APIs de AssemblyAI, OpenAI, y otros servicios de IA.

## Requisitos

- Python 3.7+
- Flask
- AssemblyAI
- Pydub
- OpenAI
- Requests
- Flask-CORS

## Instalación

1. Clona el repositorio:
    ```sh
    git clone https://github.com/kevinjapa/BackEndStoryAI.git
    cd BackEndStoryAI
    ```

2. Crea un entorno virtual e instala las dependencias:
    ```sh
    python -m venv venv
    source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3. Configura tus claves de API en el archivo `config.py`:
    ```python
    ASSEMBLYAI_API_KEY = 'tu_clave_assemblyai'
    OPENAI_API_KEY = 'tu_clave_openai'
    AIMLAPI_API_KEY = 'tu_clave_aimlapi'
    ```

## Uso

Inicia el servidor Flask:
```sh
python app.py
```

El servidor se ejecutará en http://127.0.0.1:5000.

Endpoints
Transcribir Audio

# API Endpoints

## Transcripción de Audio

**URL:** `/api/transcribe`  
**Método:** POST  
**Descripción:** Transcribe un archivo de audio.  
**Parámetros del cuerpo:** 
```json
{
  "audio": "Archivo de audio en formato webm"
}
```
```json
{
  "transcript": "Texto transcrito"
}
```

## Generar Respuesta con Llama-3

**URL:** `/api/llama3`  
**Método:** POST  
**Descripción:** Genera una respuesta usando el modelo Llama-3.
**Parámetros del cuerpo:** 

```json
{
  "message": "Tu mensaje"
}
```
respuesta exitosa
```json
{
  "response": "Respuesta generada por Llama-3"
}
```
**URL:** `/api/chat-gpt`  
**Método:** POST  
**Descripción:** Genera una historia usando el modelo GPT-3.5.
**Parámetros del cuerpo:** 
```json
{
  "message": "Tu mensaje"
}
```
respuesta exitosa
```json
{
  "response": "Respuesta generada por Llama-3"
}
```
**URL:** `/generate-image`  
**Método:** POST  
**Descripción:** Genera una imagen usando la API de OpenAI.
**Parámetros del cuerpo:** 
```json
{
  "prompt": "Descripción de la imagen"
}
```
respuesta exitosa
```json
{
  "image_url": "URL de la imagen generada",
  "saved_path": "Ruta donde se guardó la imagen"
}
```
# Estructura del Proyecto
```html
├── app.py                   # Archivo principal del servidor Flask
├── config.py                # Archivo de configuración con claves de API
├── requirements.txt         # Lista de dependencias del proyecto
└── README.md                # Archivo README con información del proyecto
```
