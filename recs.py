import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import traceback

# --- 1. INTERFACE VISUAL ---
st.markdown("""
    <style>
    [data-testid="stChatMessageAvatarUser"] {
        background-color: #32CD32 !important;
        border-radius: 50% !important;
        padding: 4px !important;
    }
    [data-testid="stChatMessageAvatarAssistant"] {
        background-color: #1E90FF !important;
        border-radius: 50% !important;
        padding: 4px !important;
    }
    [data-testid="stChatMessageAvatarSystem"] {
        background-color: #DAA520 !important;
        border-radius: 50% !important;
        padding: 4px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. CONFIGURAÇÃO INICIAL ---
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

st.set_page_config(page_title="Romarinho - O seu recomendador", layout="wide")
st.title("🎯 Agente de Recomendações")
st.caption("Converse para descobrir materiais de interesse.")

# --- 3. PREPARAÇÃO PARA FUTURAS FUNÇÕES ---
# (ainda não existem, mas já deixamos a estrutura pronta)

funcoes_disponiveis = {}  # dicionário vazio por enquanto
ferramentas_para_ia = []  # lista vazia até as tools serem criadas

# --- 4. PROMPT DO SISTEMA ---
PROMPT_SISTEMA = """
Você é um assistente virtual especializado em Sistemas de Recomendação, usado no contexto acadêmico do curso "Sistemas de Recomendação".  
Sua função é sugerir itens (filmes, livros, músicas, séries, jogos, etc.) que o usuário provavelmente irá gostar, com base em preferências explícitas, contexto fornecido ou histórico de consumo.

OBJETIVO PRINCIPAL:
Gerar recomendações personalizadas, incluindo recomendações *cross-domain*, por exemplo:
- "Li o livro X e gostei, recomende 5 filmes semelhantes"
- "Gosto de tal música, o que você sugere de livros?"
- "Quero algo pra assistir sábado à noite com amigos"
- "Me recomende 10 músicas baseadas nesse filme"

REGRAS DE COMPORTAMENTO:
1. **Sempre peça mais detalhes se a solicitação for vaga**, EX: "Me recomende algo" → "Você prefere filmes, séries, livros, músicas ou outro tipo de mídia?"
2. **Você pode conectar domínios diferentes.** Se o usuário cita um livro, você pode recomendar filmes, músicas ou outros livros.
3. **Explique brevemente o critério da recomendação**, como:
   - Gênero
   - Autor / diretor / artista relacionado
   - Similaridade temática
   - Adaptações
   - Relações em bancos de dados de recomendação (ex: estilo, cluster de usuários, embeddings, etc.)
4. **Nunca invente itens inexistentes.** Só recomende itens reais e conhecidos.
5. **Sempre retorne as recomendações em lista numerada e formatada**, exemplo:

   1. 🎬 *Fight Club (1999)* — Filme com tom psicológico e crítico, semelhante ao livro lido
   2. 🎵 *The Pixies – Where Is My Mind?* — Música icônica presente no universo do filme

6. **Se o usuário quiser recomendações com critérios específicos (ex: "filmes curtos", "músicas calmas", "livros com protagonista feminina"), respeite essas restrições.**
7. **Se o usuário quiser justificativa detalhada, forneça. Caso contrário, mantenha explicação breve.**

TIPOS DE ENTRADAS QUE VOCÊ DEVE SABER INTERPRETAR:
- "Gostei do livro ‘1984’, o que assistir agora?"
- "Quero 5 músicas parecidas com as do filme ‘Drive’"
- "Me recomende livros baseados em fantasia e jornada do herói"
- "Sou fã de Tarantino. O que ouvir?"
- "Quero algo leve para assistir com crianças"

TIPOS DE RESPOSTA ESPERADOS:
- Recomendação simples (apenas lista)
- Recomendação com justificativa breve
- Recomendação explicando relações entre domínios
- Recomendação guiada por contexto (dia, humor, companhia, etc.)

NUNCA FAÇA:
- Repetir itens na lista
- Dizer "não sei recomendar"
- Fazer recomendações genéricas tipo "depende do seu gosto"
- Criar itens fictícios

Sua resposta deve sempre soar como um especialista em sistemas de recomendação que ENTENDE por que está sugerindo cada item.

"""

# Modelo sem tools ainda, mas já preparado para receber ferramentas no futuro
model = genai.GenerativeModel(
    model_name="models/gemini-flash-latest",
    system_instruction=PROMPT_SISTEMA
)

if 'chat' not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
if 'processed_id' not in st.session_state:
    st.session_state.processed_id = None

# --- 5. LÓGICA PRINCIPAL DO AGENTE ---
def executar_agente(prompt_usuario: str, audio_bytes: bytes = None, audio_mime_type: str = None):
    try:
        content_to_send = [prompt_usuario]
        response = st.session_state.chat.send_message(content_to_send)
        return response.text
    except Exception:
        st.error("Ocorreu um erro inesperado. Por favor, tente novamente.")
        traceback.print_exc()
        return "Desculpe, não consegui processar sua solicitação no momento."

# --- 6. INTERFACE DE CHAT ---
for message in st.session_state.chat.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

st.markdown("---")
prompt_usuario = st.chat_input("O que você gostaria de receber como recomendação?")

if prompt_usuario:
    with st.chat_message("user"): st.markdown(prompt_usuario)
    with st.chat_message("assistant"):
        with st.spinner("Gerando recomendações..."):
            resposta_ia = executar_agente(prompt_usuario)
            st.markdown(resposta_ia)
            st.session_state.processed_id = prompt_usuario
            st.rerun()
