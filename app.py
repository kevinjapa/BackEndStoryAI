from flask import Flask, request, jsonify
import assemblyai as aai
from flask_cors import CORS
import os
from pydub import AudioSegment
import requests
import json
import openai
from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

app = Flask(__name__)
CORS(app)  

aai.settings.api_key = "e5416e4013334ec99cfcdda0e9ba7429"

@app.route('/api/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    try:
        audio_file = request.files['audio']
        audio_path = 'temp_audio.webm'
        audio_file.save(audio_path)

        wav_path = 'temp_audio.wav'
        audio = AudioSegment.from_file(audio_path, format='webm')
        audio.export(wav_path, format='wav')

        config = aai.TranscriptionConfig(language_code="es")

        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(wav_path, config=config)

        os.remove(audio_path)
        os.remove(wav_path)

        return jsonify({'transcript': transcript.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/llama3', methods=['POST'])
def llama3():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400

        message = data['message']
        
        url = 'https://api.aimlapi.com/chat/completions'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer 97304204becd4c15b50434f26b8f5d5a' 

        }
        payload = {
            "model": "meta-llama/Llama-3-70b-chat-hf",
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ],
            "max_tokens": 512,
            "stream": False
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            result = response.json()
            return jsonify(result) 
        else:
            return jsonify({'error': response.text}), response.status_code

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# generar las historias
@app.route('/api/chat-gpt', methods=['POST'])
def chat_gpt():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'No message provided'}), 400

        message = data['message']
        
        def chat_gpt_api(message):
            try:
                url = 'https://api.openai.com/v1/chat/completions'
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer sk-None-pZvhT36Lo37E34AZP0ZZT3BlbkFJm5LRgULNtRF4ufYykAXu'
                }
                payload = {
                    'model': 'gpt-3.5-turbo',
                    'messages': [
                        {
                            'role': 'user',
                            'content': message
                        }
                    ],
                    'max_tokens': 100
                }

                response = requests.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and result['choices']:
                        return result['choices'][0]['message'].get('content', '').strip()
                    else:
                        return 'No se encontró una respuesta válida en la API'
                else:
                    return f'Error en la solicitud a la API: {response.status_code} - {response.text}'

            except Exception as e:
                return f'Error en la solicitud a la API: {str(e)}'
                
        response_text = chat_gpt_api(message)
        return jsonify({'response': response_text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# generar imagenes

# Configura tu clave de API de OpenAI
api_key = 'sk-None-pZvhT36Lo37E34AZP0ZZT3BlbkFJm5LRgULNtRF4ufYykAXu'

# Directorio donde se guardarán las imágenes
image_directory = '/Users/kevinjapa/Downloads/API Speech Text/imagenes/'

# Crear el directorio si no existe
os.makedirs(image_directory, exist_ok=True)

@app.route('/generate-image', methods=['POST'])
def generate_image():
    try:
        data = request.get_json()
        prompt = data.get('prompt')

        if not prompt:
            return jsonify({'error': 'Falta la descripción de la imagen'}), 400

        # Hacer una solicitud a la API de OpenAI para generar una imagen
        response = requests.post(
            'https://api.openai.com/v1/images/generations',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'prompt': prompt,
                'n': 1,
                'size': '256x256'
            }
        )

        if response.status_code != 200:
            return jsonify({'error': response.text}), response.status_code

        response_data = response.json()
        image_url = response_data['data'][0]['url']

        # Descargar la imagen
        image_response = requests.get(image_url)

        if image_response.status_code != 200:
            return jsonify({'error': 'No se pudo descargar la imagen'}), image_response.status_code

        # Guardar la imagen en el servidor
        # image_path = os.path.join(image_directory, f"{prompt.replace(' ', '_')}.png")
        image_path = os.path.join(image_directory, f"hola.png")
        with open(image_path, 'wb') as f:
            f.write(image_response.content)

        return jsonify({'image_url': image_url, 'saved_path': image_path})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Configuración de la base de datos
DATABASE_URL = 'postgresql+psycopg2://postgres:root@localhost:5432/postgres'
# engine = create_engine(DATABASE_URL)
# Base = declarative_base()
# Session = sessionmaker(bind=engine)
# session = Session()

# # Definir el modelo de datos
# class ChatHistory(Base):
#     __tablename__ = 'chat_history'
#     id = Column(Integer, primary_key=True)
#     question = Column(Text, nullable=False)
#     answer = Column(Text, nullable=False)
#     image_url = Column(Text)

# # Crear las tablas en la base de datos
# Base.metadata.create_all(engine)

# @app.route('/api/save-chat-history', methods=['POST'])
# def save_chat_history():
#     data = request.get_json()
#     if not data or 'chatHistory' not in data:
#         return jsonify({'error': 'No chat history provided'}), 400

#     chat_history = data['chatHistory']
#     try:
#         for chat in chat_history:
#             new_entry = ChatHistory(
#                 question=chat['question'],
#                 answer=chat['answer'],
#                 image_url=chat.get('imageUrl')
#             )
#             session.add(new_entry)
#         session.commit()
#         return jsonify({'message': 'Chat history saved successfully'}), 200
#     except Exception as e:
#         session.rollback()
#         return jsonify({'error': str(e)}), 500
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# Definir el modelo de datos
class ChatHistory(Base):
    __tablename__ = 'chat_history'
    id = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    image_url = Column(Text)

# Crear las tablas en la base de datos
Base.metadata.create_all(engine)

# Endpoint de prueba de conexión
@app.route('/api/test-db-connection', methods=['GET'])
def test_db_connection():
    try:
        # Realiza una consulta simple para verificar la conexión
        result = session.execute("SELECT 1").fetchone()
        return jsonify({'message': 'Connection successful', 'result': result[0]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-chat-history', methods=['POST'])
def save_chat_history():
    data = request.get_json()
    if not data or 'chatHistory' not in data:
        return jsonify({'error': 'No chat history provided'}), 400

    chat_history = data['chatHistory']
    try:
        for chat in chat_history:
            new_entry = ChatHistory(
                question=chat['question'],
                answer=chat['answer'],
                image_url=chat.get('imageUrl')
            )
            session.add(new_entry)
        session.commit()
        return jsonify({'message': 'Chat history saved successfully'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
