# Importando as bibliotecas necessárias
from dotenv import load_dotenv
import os
from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import openai
import pyttsx3

# carregando as variáveis do arquivo .env
load_dotenv()

# chave API do OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Inicializando o Flask
app = Flask(__name__)



# função para capturar áudio do usuário e converter para texto
def capturar_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Diga algo...")
        audio = recognizer.listen(source)
    try:
        texto = recognizer.recognize_google(audio, language='pt-BR')
        print(f"Você disse: {texto}")
        return texto
    except sr.UnknownValueError:
        return "Não consegui entender o que você disse."
    except sr.RequestError:
        return "Erro ao conectar com o serviço de reconhecimento de voz."

# função para converter texto em áudio
def falar(texto):
    engine = pyttsx3.init()
    engine.say(texto)
    engine.runAndWait()

# função para consultar o GPT-3 e obter uma resposta
def gerar_resposta(pergunta_usuario):
    resposta = openai.Completion.create(
        engine="text-davinci-003",
        prompt=pergunta_usuario,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return resposta.choices[0].text.strip()

# rota inicial para renderizar a página HTML
@app.route('/')
def home():
    return render_template('index.html')

# rota para processar o áudio do usuário e retornar a resposta em áudio
@app.route('/chat', methods=['POST'])
def chat():
    pergunta_usuario = capturar_audio()  # capturando a fala do usuário e converte para texto
    if pergunta_usuario:
        resposta = gerar_resposta(pergunta_usuario)  # gerando a resposta usando GPT-3
        falar(resposta)  # convertemdo a resposta de texto em áudio
        return jsonify({'response': resposta})
    else:
        return jsonify({'response': 'Não consegui entender sua pergunta.'})

# executando a aplicação Flask
if __name__ == '__main__':
    app.run(port=5000, debug=True)