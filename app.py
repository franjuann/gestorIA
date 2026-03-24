import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import datetime

# --- CONFIGURACIÓN DE MARCA Y ESTILO ---
st.set_page_config(page_title="GestorIA - Tu Informe de Ahorro", layout="wide", initial_sidebar_state="collapsed")

# CSS personalizado para profesionalizar la interfaz (Trust & Flow)
st.markdown("""
    <style>
    .stApp { background-color: #fcfdfe; }
    .main-card { background-color: white; padding: 25px; border-radius: 20px; box-shadow: 0 10px 15px rgba(0,0,0,0.03); margin-bottom: 20px;}
    h1 { color: #0f172a; font-weight: 800; font-size: 2.5rem; }
    h4 { color: #1e293b; font-weight: 700; margin-top: 1.5rem;}
    .stButton>button { background-color: #2563eb; color: white; border-radius: 10px; font-weight: 600; transition: all 0.3s; width: 100%; height: 3.5rem; font-size: 1.1rem;}
    .stButton>button:hover { background-color: #1d4ed8; transform: translateY(-2px); }
    .stDownloadButton>button { background-color: #059669; color: white; border-radius: 10px; font-weight: 600; width: 100%; height: 3.5rem; margin-top: 1rem;}
    .stDownloadButton>button:hover { background-color: #047857; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE IA Y CONFIGURACIÓN ---
def configurar_ia(key):
    genai.configure(api_key=key)
    # Autodetector de modelo avanzado (Gemini 2.5 Flash o Pro)
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        return "models/gemini-2.5-flash" if "models/gemini-2.5-flash" in models else models[0]
    except: return None

# --- UI PRINCIPAL: CABECERA Y ACCESO ---
st.title("🎯 GestorIA Pro: Tu Consultoría Fiscal Inteligente")
st.caption("Analizamos la normativa vigente 2025-2026 para encontrar tu ahorro.")

# Barra lateral minimalista para la API Key
with st.sidebar:
    st.header("🔑 Acceso")
    api_key = st.text_input("Introduce tu API Key:", type="password")
    if api_key: st.success("Conexión Activa")
    else: st.warning("Esperando Llave...")

# --- LOGICA PRINCIPAL SI HAY API KEY ---
if api_key:
    model_name = configurar_ia(api_key)
    if not model_name:
        st.error("Error al conectar con los modelos de IA. Revisa tu API Key.")
        st.stop()
    
    model = genai.GenerativeModel(model_name)

    # --- EMBUDO DE DATOS (FORMULARIO FISCAL) ---
    with st.container():
        st.markdown("<div class='main-card'>", unsafe_allow_html=True)
        st.markdown("### 📝 PASO 1: Tu Perfil de Ahorro")
        st.info("Completa los datos con precisión para que la IA encuentre las deducciones exactas.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 👤 Perfil y Trabajo")
            edad = st.number_input("Edad actual", min_value=16, max_value=99, value=30)
            situacion = st.selectbox("Situación laboral", ["Asalariado (Nómina)", "Autónomo", "Pluriactividad", "Desempleado", "Estudiante", "Pensionista"])
            ingresos = st.select_slider("Ingresos brutos anuales aproximados (€)", options=["0-15k", "15k-22k", "22k-35k", "35k-60k", "+60k"], value="22k-35k")
        
        with col2:
            st.markdown("#### 🏠 Vivienda y Residencia")
            comunidad = st.selectbox("Comunidad Autónoma de residencia", ["Andalucía", "Aragón", "Asturias", "Baleares", "Canarias", "Cantabria", "Castilla y León", "Castilla-La Mancha", "Cataluña", "Comunidad Valenciana", "Extremadura", "Galicia", "Madrid", "Murcia", "Navarra", "País Vasco"