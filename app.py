import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from fpdf import FPDF
import re

# --- 1. CONFIGURACIÓN INICIAL (DEBE IR PRIMERO) ---
st.set_page_config(page_title="GestorIA Pro", layout="wide", page_icon="⚖️")

# --- 2. LOGO Y CABECERA ---
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    # Intenta cargar 'logo.png' si existe en tu carpeta de GitHub
    try:
        st.image("logo.png", width=100)
    except:
        st.markdown("<h1 style='margin:0;'>⚖️</h1>", unsafe_allow_html=True)

with col_titulo:
    st.title("GestorIA Pro: Inteligencia Fiscal")
    st.subheader("Optimización de ahorro basada en normativas oficiales")

st.divider()

# --- 3. CONFIGURACIÓN DE IA (SOLUCIÓN 404/429) ---
def iniciar_ia():
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Forzamos el modelo Flash que es el más estable para el plan gratuito
        return genai.GenerativeModel('gemini-1.5-flash')
    return None

model = iniciar_ia()

# --- 4. FORMULARIO DE PERFIL ---
with st.expander("👤 Configuración de Perfil Fiscal", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        edad = st.number_input("Edad", 18, 95, 35)
        comunidad = st.selectbox("Comunidad Autónoma", ["Madrid", "Andalucía", "Cataluña", "Valencia", "Galicia", "Castilla y León", "Otros"])
    with c2:
        situacion = st.selectbox("Situación", ["Asalariado", "Autónomo", "Desempleado"])
        vivienda = st.selectbox("Vivienda", ["Alquiler", "Hipoteca", "Propiedad"])
    with c3:
        hijos = st.number_input("Hijos", 0, 10, 0)
        rural = st.checkbox("Zona Rural")

# --- 5. LÓGICA DE CÁLCULO ---
if st.button("🚀 ANALIZAR MI AHORRO"):
    if not model:
        st.error("Error: Configura tu API Key en los Secrets de Streamlit.")
    else:
        with st.spinner("Buscando en BOE y fuentes oficiales..."):
            prompt = f"Gestor fiscal España. Perfil: {edad} años, {situacion}, {comunidad}, {vivienda}, Rural:{rural}, Hijos:{hijos}. 4 deducciones reales. Formato: [AYUDA] TITULO: x EUROS: x RESUMEN: x FUENTE: x LEGAL: x [/AYUDA]"
            
            try:
                response = model.generate_content(prompt)
                texto = response.text
                
                ayudas = []
                total = 0
                for b in texto.split("[AYUDA]"):
                    if "TITULO:" in b:
                        try:
                            t = re.search(r"TITULO:\s*(.*)", b).group(1).strip()
                            e = int(re.search(r"EUROS:\s*(\d+)", b).group(1).strip())
                            r = re.search(r"RESUMEN:\s*(.*)", b).group(1).strip()
                            f = re.search(r"FUENTE:\s*(.*)", b).group(1).strip()
                            l = re.search(r"LEGAL:\s*(.*)", b).group(1).strip()
                            ayudas.append({"t":t, "e":e, "r":r, "f":f, "l":l})
                            total += e
                        except: continue

                # Mostrar Resultados
                st.markdown(f"""
                    <div style="background:#1e293b; color:#10b981; padding:25px; border-radius:15px; text-align:center; border: 1px solid #334155;">
                        <p style="color:white; margin:0; font-size:1rem;">Ahorro Potencial Total</p>
                        <h1 style="margin:0; font-size:3rem;">{total} €</h1>
                    </div>
                """, unsafe_allow_html=True)

                for item in ayudas:
                    st.markdown(f"""
                        <div style="background:white; padding:20px; border-radius:10px; border-left:6px solid #10b981; margin:15px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                            <span style="float:right; font-weight:bold; color:#10b981;">+{item['e']}€</span>
                            <h4 style="margin:0; color:#1e293b;">{item['t']}</h4>
                            <p style="margin:10px 0; font-size:0.95rem;">{item['r']}</p>
                            <small style="color:#2563eb;"><b>📍 Fuente:</b> {item['f']}</small>
                        </div>
                    """, unsafe_allow_html=True)
                    with st.expander("📖 Detalle Técnico / BOE"):
                        st.write(item['l'])

            except Exception as e:
                if "429" in str(e):
                    st.warning("⚠️ Límite de Google alcanzado. Espera 60 segundos antes de volver a intentar.")
                else:
                    st.error(f"Error en la consulta: {e}")