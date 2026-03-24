import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

st.set_page_config(page_title="GestorIA Pro", layout="wide")

st.markdown("<style>.stApp { background-color: #f5f7f9; } .stButton>button { background-color: #002b5b; color: white; }</style>", unsafe_allow_html=True)

with st.sidebar:
    st.header("Configuración")
    api_key = st.text_input("Google API Key", type="password")
    st.divider()
    archivo = st.file_uploader("Sube un PDF", type="pdf")

texto_pdf = ""
if archivo:
    reader = PdfReader(archivo)
    for page in reader.pages:
        texto_pdf += page.extract_text()

col1, col2 = st.columns([2, 1])

with col2:
    st.subheader("Acciones")
    resumir = st.button("📋 Resumir")
    ayudas = st.button("💰 Ayudas")

with col1:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Duda...")
    if resumir: user_input = "Resume este PDF en 5 puntos."
    if ayudas: user_input = "¿Qué ayudas menciona este texto?"

    if user_input:
        if not api_key:
            st.error("Falta API Key")
        else:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            instrucciones = f"Eres un gestor experto en España. Contexto: {texto_pdf[:5000]}"
            response = model.generate_content(f"{instrucciones}\n\nPregunta: {user_input}")
            
            with st.chat_message("assistant"):
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})