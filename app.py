import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

st.set_page_config(page_title="GestorIA", layout="centered")
st.title("🤖 GestorIA")

with st.sidebar:
    st.title("Configuración")
    api_key = st.text_input("Introduce tu Google API Key:", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # --- BLOQUE DETECTOR DE MODELOS ---
        # Intentamos encontrar un modelo válido en tu cuenta
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Priorizamos gemini-1.5-flash si está, si no, el primero que funcione
        model_to_use = "models/gemini-1.5-flash" if "models/gemini-1.5-flash" in available_models else available_models[0]
        
        model = genai.GenerativeModel(model_to_use)
        st.info(f"Conectado usando: {model_to_use}")
        # ----------------------------------

        uploaded_file = st.file_uploader("Elige un archivo PDF", type="pdf")

        if uploaded_file is not None:
            reader = PdfReader(uploaded_file)
            text = "".join([page.extract_text() for page in reader.pages])
            st.success("✅ PDF cargado")

            user_input = st.text_input("Haz tu consulta:")

            if user_input:
                with st.spinner("Analizando..."):
                    prompt = f"Contexto: {text[:8000]}\n\nPregunta: {user_input}"
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    
    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Asegúrate de que tu API Key sea de Google AI Studio (Gemini).")
else:
    st.warning("⚠️ Introduce la API Key a la izquierda.")