from flask import Flask, request, jsonify
import assemblyai as aai
from flask_cors import CORS
import os
from pydub import AudioSegment
import requests
import json
import openai
from sqlalchemy import create_engine, Column, Integer, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask import send_from_directory

Base = declarative_base()

app = Flask(__name__)
CORS(app)  

# Configuración de la base de datos
DATABASE_URL = 'postgresql+psycopg2://postgres:root@localhost:5432/postgres' # Connexion Base Datos
aai.settings.api_key = "e5416e4013334ec99cfcdda0e9ba7429"# key Assamble Audio
api_key = 'sk-None-pZvhT36Lo37E34AZP0ZZT3BlbkFJm5LRgULNtRF4ufYykAXu' # key Api Open AI

engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# Definir el modelo de datos
# Definimos las tablas para la base de datos y creamos la relacion con el ususario y el chat
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(Text, nullable=False, unique=True)
    password = Column(Text, nullable=False)

class ChatHistory(Base):
    __tablename__ = 'chat_history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    image_url = Column(Text)
    user = relationship('User', back_populates='chat_history')

User.chat_history = relationship('ChatHistory', order_by=ChatHistory.id, back_populates='user')
# Crear las tablas en la base de datos
Base.metadata.create_all(engine)


#Api para Audio-Text
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

#Modelo para generar cuentos con llama(No Usado)
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

#Generar Historias
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

# Generar Imagenes
# Directorio donde se guardarán las imágenes

# Obtenemos la Imagen con la ruta del Servidor
@app.route('/imagenes/<filename>')
def serve_image(filename):
    return send_from_directory(image_directory, filename)

# Generamos la Imagen con Dall-E y Guardamos en el Servidor
image_directory = 'imagenes/'
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

        # Crear un nombre único para la imagen
        image_id = len(os.listdir(image_directory)) + 1
        image_path = os.path.join(image_directory, f"image_{image_id}.png")
        with open(image_path, 'wb') as f:
            f.write(image_response.content)

        # Devolver la URL de la imagen guardada en el servidor
        server_image_url = f"http://127.0.0.1:5000/{image_path}"

        return jsonify({'image_url': server_image_url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

#Registro de Usuarios
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)

    session.add(new_user)
    session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

#Login de Usuarios
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = session.query(User).filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return jsonify({'message': 'Login successful', 'user_id': user.id}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401

#Guardar Historial de Chat
@app.route('/api/save-chat-history', methods=['POST'])
def save_chat_history():
    data = request.get_json()
    user_id = data.get('user_id')
    chat_history = data.get('chatHistory')

    if not user_id or not chat_history:
        return jsonify({'error': 'User ID and chat history are required'}), 400

    user = session.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        for chat in chat_history:
            new_entry = ChatHistory(
                user_id=user.id,
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

#Obtener el Chat
@app.route('/api/get-chat-history', methods=['GET'])
def get_chat_history():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400

    try:
        chat_history = session.query(ChatHistory).filter_by(user_id=user_id).all()
        result = [{'question': chat.question, 'answer': chat.answer, 'imageUrl': chat.image_url} for chat in chat_history]
        return jsonify({'chatHistory': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='192.168.0.101', port=5000, debug=True)

