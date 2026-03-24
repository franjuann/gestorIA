import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from fpdf import FPDF
import datetime
import re
import time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="GestorIA Free", layout="wide")

# Colores Corporativos
AZUL = (30, 41, 59)
VERDE = (16, 185, 129)

# --- FUNCIÓN IA (FLASH PARA MÁXIMA CUOTA) ---
def configurar_ia():
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Forzamos Flash 1.5: Es el que más perdonan en el plan gratis
        return genai.GenerativeModel('gemini-1.5-flash')
    return None

model = configurar_ia()

# --- INTERFAZ ---
st.title("⚖️ GestorIA: Optimizador Fiscal")
st.info("Versión Gratuita: Si da error de cuota, espera 30 segundos entre consultas.")

with st.expander("👤 Mi Perfil", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        edad = st.number_input("Edad", 18, 90, 30)
        comunidad = st.selectbox("Comunidad", ["Madrid", "Andalucía", "Cataluña", "Valencia", "Galicia", "Castilla y León", "Otros"])
        hijos = st.number_input("Hijos", 0, 10, 0)
    with c2:
        situacion = st.selectbox("Trabajo", ["Asalariado", "Autónomo", "Desempleado"])
        vivienda = st.selectbox("Vivienda", ["Alquiler", "Hipoteca", "Propiedad"])
        rural = st.checkbox("Zona Rural")

if st.button("🚀 CALCULAR MI AHORRO"):
    if not model:
        st.error("Falta API Key.")
    else:
        with st.spinner("Buscando deducciones..."):
            # Prompt ultra-corto para ahorrar tokens y evitar el 429
            prompt = f"Gestor fiscal España. Perfil: {edad} años, {situacion}, {comunidad}, {vivienda}, Rural:{rural}, Hijos:{hijos}. 4 deducciones. Formato: [AYUDA] TITULO: x EUROS: x RESUMEN: x FUENTE: x LEGAL: x [/AYUDA]"
            
            try:
                response = model.generate_content(prompt)
                res_text = response.text
                
                # Procesar resultados
                ayudas = []
                total = 0
                for b in res_text.split("[AYUDA]"):
                    if "TITULO:" in b:
                        try:
                            t = re.search(r"TITULO:\s*(.*)", b).group(1)
                            e = int(re.search(r"EUROS:\s*(\d+)", b).group(1))
                            r = re.search(r"RESUMEN:\s*(.*)", b).group(1)
                            f = re.search(r"FUENTE:\s*(.*)", b).group(1)
                            l = re.search(r"LEGAL:\s*(.*)", b).group(1)
                            ayudas.append({"t":t, "e":e, "r":r, "f":f, "l":l})
                            total += e
                        except: continue

                # Visualización
                st.markdown(f'<div style="background:#1e293b; color:white; padding:30px; border-radius:15px; text-align:center;"><h1>{total} €</h1><p>Ahorro Potencial Total</p></div>', unsafe_allow_html=True)
                
                for item in ayudas:
                    st.markdown(f"""
                    <div style="background:white; padding:20px; border-radius:10px; border-top:5px solid #10b981; margin:15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <span style="float:right; color:#10b981; font-weight:bold; font-size:1.2rem;">+{item['e']}€</span>
                        <h4 style="margin:0;">{item['t']}</h4>
                        <p style="font-size:0.9rem; color:#64748b;">{item['r']}</p>
                        <small style="color:#2563eb;"><b>📍 Fuente:</b> {item['f']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    with st.expander("📖 Base Legal"):
                        st.write(item['l'])

            except Exception as e:
                if "429" in str(e):
                    st.warning("⚠️ ¡Límite alcanzado! Google nos pide esperar 30 segundos. Por favor, no refresques y vuelve a intentarlo en un momento.")
                else:
                    st.error(f"Error: {e}")

# --- BARRA LATERAL (PDF LIGERO) ---
with st.sidebar:
    st.subheader("📄 Documentación")
    st.info("Sube un PDF solo si es necesario, consume mucha cuota gratuita.")
    f = st.file_uploader("Subir documento", type="pdf")