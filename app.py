import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# Configuración de la página
st.set_page_config(page_title="GestorIA - Tu Consultor Legal", layout="centered")

st.title("🤖 GestorIA")
st.subheader("Sube un PDF y hazle preguntas técnicas o legales")

# Sidebar para la API Key
with st.sidebar:
    st.title("Configuración")
    api_key = st.text_input("Introduce tu Google API Key:", type="password")
    st.info("Consigue tu llave en: https://aistudio.google.com/app/apikey")

if api_key:
    # CONFIGURACIÓN ROBUSTA: Forzamos el transporte REST para evitar errores de conexión
    genai.configure(api_key=api_key, transport='rest')
    
    # Seleccionamos el modelo más estable actualmente
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Subida de archivos
    uploaded_file = st.file_uploader("Elige un archivo PDF", type="pdf")

    if uploaded_file is not None:
        # Leer el PDF
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        st.success("✅ PDF leído correctamente")

        # Área de chat
        user_input = st.text_input("¿Qué quieres saber sobre este documento?")

        if user_input:
            with st.spinner("Analizando con IA..."):
                try:
                    # Instrucciones del sistema para que actúe como gestor
                    instrucciones = f"Actúa como un gestor administrativo experto. Basándote en este texto: {text[:10000]}"
                    
                    response = model.generate_content(f"{instrucciones}\n\nPregunta: {user_input}")
                    
                    st.markdown("### Respuesta:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Hubo un problema con la IA: {e}")
                    st.info("Si el error persiste, prueba a generar una nueva API Key en Google AI Studio.")
else:
    st.warning("⚠️ Por favor, introduce tu API Key en la barra lateral para comenzar.")