import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# Configuración de la página
st.set_page_config(page_title="GestorIA", layout="centered")

st.title("🤖 GestorIA")
st.subheader("Tu consultor legal con IA")

# Sidebar para la API Key
with st.sidebar:
    st.title("Configuración")
    api_key = st.text_input("Introduce tu Google API Key:", type="password")
    st.info("Consigue tu llave en: https://aistudio.google.com/app/apikey")

if api_key:
    try:
        # CONFIGURACIÓN UNIVERSAL
        genai.configure(api_key=api_key)
        
        # Probamos con el nombre del modelo que acepta tanto v1 como v1beta
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")

        # Subida de archivos
        uploaded_file = st.file_uploader("Elige un archivo PDF", type="pdf")

        if uploaded_file is not None:
            reader = PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            
            st.success("✅ PDF cargado")

            user_input = st.text_input("Haz tu consulta sobre el documento:")

            if user_input:
                with st.spinner("Pensando..."):
                    # Enviamos el texto del PDF y la pregunta
                    prompt = f"Contexto del PDF: {text[:8000]}\n\nPregunta: {user_input}"
                    response = model.generate_content(prompt)
                    
                    st.markdown("### Respuesta:")
                    st.write(response.text)
                    
    except Exception as e:
        # Si da error de "not found", intentamos con la versión sin el prefijo "models/"
        st.error(f"Error de conexión: {e}")
        st.info("Prueba a generar una nueva API Key si el error persiste.")
else:
    st.warning("⚠️ Introduce la API Key en la izquierda.")