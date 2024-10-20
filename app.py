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
    recognizer = sr.Recognizer() # criando uma instância do reconhecedor de fala
    with sr.Microphone() as source: ## microfone como fonte de entrada de áudio
        print("Diga algo...")## informando ao usuário para falar algo
        audio = recognizer.listen(source)#capturando o audio do usuário
        # tentando reconhecer e converter o áudio capturado para texto
    try:
        texto = recognizer.recognize_google(audio, language='pt-BR') ## reconhecendo o texto em português
        print(f"Você disse: {texto}")
        return texto #retornando o texto convertido
    except sr.UnknownValueError:
        return "Não consegui entender o que você disse."
    except sr.RequestError:
        return "Erro ao conectar com o serviço de reconhecimento de voz."

# função para converter texto em áudio
def falar(texto):
    engine = pyttsx3.init() ## inicializa o motor de TTS (Text-to-Speech)
    engine.say(texto) # Colocando o texto na fila para ser falado
    engine.runAndWait()  # executando o TTS e espera até que o áudio termine

# função para consultar o GPT-3 e obter uma resposta
def gerar_resposta(pergunta_usuario):
    resposta = openai.Completion.create(
        engine="text-davinci-003", # especificando qual modelo do OpenAI usar
        prompt=pergunta_usuario, #  prompt (pergunta) que será enviado ao GPT-3
        max_tokens=150, # número máximo de tokens na resposta gerada
        n=1, ## número de respostas a serem retornadas
        stop=None, ## fim da resposta não especificado
        temperature=0.7, # controlando a criatividade da resposta (0.7 é moderadamente criativo)
    )
    return resposta.choices[0].text.strip()


# função para traduzir texto usando a API do OpenAI
# utilizando API do OpenAI para traduzir o texto para o idioma especificado (português por padrão).
def traduzir_texto(texto, idioma_destino='PT'):
    prompt_traducao = f"Traduza o seguinte texto para {idioma_destino}: {texto}"
    resposta = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt_traducao,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.0  # Para tradução, definindo temperatura baixa
    )
    return resposta.choices[0].text.strip()

# rota inicial para renderizar a página HTML
@app.route('/')
def home():
    return render_template('index.html')

# rota para processar o áudio do usuário e retornar a resposta em áudio
@app.route('/chat', methods=['POST'])
def chat():
    pergunta_usuario = capturar_audio()  # Capturando a fala do usuário e converte para texto
    if pergunta_usuario:
        resposta = gerar_resposta(pergunta_usuario)  # gerando a resposta usando GPT-3
        resposta_traduzida = traduzir_texto(resposta)  # traduzindo a resposta
        falar(resposta_traduzida)  # convertendo a resposta traduzida em áudio
        return jsonify({'response': resposta_traduzida})
    else:
        return jsonify({'response': 'Não consegui entender sua pergunta.'})

# executando a aplicação Flask
if __name__ == '__main__':
    app.run(port=5000, debug=True)

