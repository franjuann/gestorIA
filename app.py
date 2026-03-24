import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# --- CONFIGURACIÓN DE MARCA ---
st.set_page_config(page_title="GestorIA - Optimización Fiscal Pro", layout="wide", initial_sidebar_state="expanded")

# Estilo profesional (Clean & Trust)
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .main-card { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    h1 { color: #1e293b; font-weight: 800; }
    .stButton>button { background-color: #2563eb; color: white; border-radius: 8px; font-weight: 600; transition: all 0.3s; }
    .stButton>button:hover { background-color: #1d4ed8; transform: translateY(-2px); }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE IA ---
def configurar_ia(api_key):
    genai.configure(api_key=api_key)
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    return "models/gemini-2.5-flash" if "models/gemini-2.5-flash" in available_models else available_models[0]

# --- UI PRINCIPAL ---
st.title("🎯 GestorIA: Optimizador de Ahorro Fiscal")
st.caption("Consultoría inteligente basada en normativa vigente 2025-2026")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/5501/5501375.png", width=80)
    st.header("Acceso Profesional")
    api_key = st.text_input("Introduce tu API Key para activar:", type="password")
    st.divider()
    st.markdown("### 📊 Estado de la sesión")
    if api_key:
        st.success("Conexión Activa")
    else:
        st.error("Esperando Llave...")

if api_key:
    model_name = configurar_ia(api_key)
    model = genai.GenerativeModel(model_name)

    # --- FORMULARIO DE ALTA PRECISIÓN ---
    st.markdown("### 📝 Formulario de Diagnóstico Fiscal")
    st.info("Completa los datos para identificar tus deducciones. Datos protegidos y no almacenados.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 👤 Perfil Básico")
        edad = st.number_input("Edad actual", min_value=16, max_value=100, value=30)
        situacion = st.selectbox("Situación laboral", ["Asalariado (Nómina)", "Autónomo", "Pluriactividad", "Desempleado", "Estudiante", "Pensionista"])
        ingresos = st.select_slider("Rango de ingresos anuales (€)", options=["0-15k", "15k-22k", "22k-35k", "35k-60k", "+60k"])
    
    with col2:
        st.markdown("#### 🏠 Ubicación y Vivienda")
        comunidad = st.selectbox("Comunidad Autónoma", ["Andalucía", "Aragón", "Asturias", "Baleares", "Canarias", "Cantabria", "Castilla y León", "Castilla-La Mancha", "Cataluña", "Comunidad Valenciana", "Extremadura", "Galicia", "Madrid", "Murcia", "Navarra", "País Vasco", "La Rioja"])
        zona_rural = st.radio("¿Vives en un municipio de menos de 5.000 hab. o en riesgo de despoblación?", ["No", "Sí"])
        vivienda = st.selectbox("Tipo de vivienda", ["Alquiler", "Propiedad con hipoteca (pre-2013)", "Propiedad con hipoteca (post-2013)", "Propiedad pagada", "Vivienda cedida"])

    with col3:
        st.markdown("#### 👨‍👩‍👧 Familia y Salud")
        hijos = st.number_input("Hijos menores de 25 años", min_value=0, step=1)
        discapacidad = st.checkbox