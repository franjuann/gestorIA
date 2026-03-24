# --- LOGO Y TÍTULO ---
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    try:
        st.image("logo.png", width=120) # Ajusta el ancho según tu logo
    except:
        # Si no encuentra el logo, muestra un emoji como placeholder
        st.markdown("<h1 style='text-align: center; margin-top: 15px;'>🍌</h1>", unsafe_allow_html=True)

with col_titulo:
    st.title("GestorIA Pro: Tu Ahorro Inteligente")
    st.write("Optimizamos tu fiscalidad en tiempo real.")
st.divider()

import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from fpdf import FPDF
import datetime
import re

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="GestorIA Pro", layout="wide")

AZUL_CORP = (30, 41, 59)   
VERDE_CORP = (16, 185, 129) 

st.markdown(f"""
    <style>
    .stApp {{ background-color: #f8fafc; }}
    .contador-box {{
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: white; padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 25px;
    }}
    .caja-ayuda {{
        background: white; padding: 20px; border-radius: 12px;
        border-top: 5px solid #10b981; margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }}
    .precio-tag {{ font-size: 1.5rem; font-weight: 800; color: #10b981; float: right; }}
    .fuente-info {{ color: #2563eb; font-weight: bold; font-size: 0.85rem; margin-top: 10px; display: block; }}
    </style>
    """, unsafe_allow_html=True)

# --- CLASE PDF ---
class PDF_Report(FPDF):
    def header(self):
        self.set_fill_color(*AZUL_CORP)
        self.rect(0, 0, 210, 35, 'F')
        self.set_font('Arial', 'B', 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, 'INFORME DE AHORRO FISCAL - GESTORIA PRO', 0, 1, 'C')
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()} - Documento Informativo Oficial', 0, 0, 'C')

def generar_pdf_bytes(ayudas, total, perfil_str):
    pdf = PDF_Report()
    pdf.add_page()
    pdf.ln(30)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Perfil Analizado: {perfil_str}", 0, 1)
    pdf.set_fill_color(*VERDE_CORP)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, f"AHORRO TOTAL ESTIMADO: {total} EUR", 0, 1, 'C', True)
    pdf.ln(10)
    pdf.set_text_color(0,0,0)
    for a in ayudas:
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(150, 8, a['t'][:55], 0, 0)
        pdf.cell(40, 8, f"+{a['e']} EUR", 0, 1, 'R')
        pdf.set_font('Arial', '', 9)
        pdf.multi_cell(0, 5, f"Fuente: {a['f']}\nExplicacion: {a['r']}\nBase Legal: {a['l']}")
        pdf.ln(4)
    return pdf.output()

def configurar_ia_dinamica():
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        try:
            # Priorizamos el modelo 1.5 Flash que tiene mucha más cuota gratuita
            # que el 3.1 Pro o el Pro normal.
            return genai.GenerativeModel('gemini-1.5-flash')
        except:
            # Si falla, que use el que sea, pero Flash es el objetivo
            return genai.GenerativeModel('gemini-pro')
    return None

model = configurar_ia_dinamica()

# --- INTERFAZ ---
st.title("⚖️ GestorIA Pro")

with st.expander("👤 Configura tu Perfil", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        edad = st.number_input("Edad", 18, 95, 30)
        comunidad = st.selectbox("Comunidad", ["Madrid", "Andalucía", "Cataluña", "Valencia", "Galicia", "Castilla y León", "Otros"])
    with c2:
        situacion = st.selectbox("Trabajo", ["Asalariado", "Autónomo", "Desempleado"])
        vivienda = st.selectbox("Vivienda", ["Alquiler", "Hipoteca", "Propiedad"])
    with c3:
        hijos = st.number_input("Hijos", 0, 10, 0)
        rural = st.checkbox("Zona rural")

if st.button("🚀 CALCULAR AHORRO"):
    if not model:
        st.error("No se pudo conectar con la IA. Revisa tu API Key.")
    else:
        with st.spinner("Consultando normativas..."):
            prompt = f"Gestor fiscal España. Perfil: {edad} años, {situacion}, {comunidad}, {vivienda}, Rural:{rural}, Hijos:{hijos}. 4 deducciones. Formato: [AYUDA] TITULO: x EUROS: x RESUMEN: x FUENTE: x LEGAL: x [/AYUDA]"
            try:
                response = model.generate_content(prompt)
                texto = response.text
                
                ayudas_lista = []
                ahorro_total = 0
                for b in texto.split("[AYUDA]"):
                    if "TITULO:" in b:
                        try:
                            t = re.search(r"TITULO:\s*(.*)", b).group(1).strip()
                            e = int(re.search(r"EUROS:\s*(\d+)", b).group(1).strip())
                            r = re.search(r"RESUMEN:\s*(.*)", b).group(1).strip()
                            f = re.search(r"FUENTE:\s*(.*)", b).group(1).strip()
                            l = re.search(r"LEGAL:\s*(.*)", b).group(1).strip()
                            ayudas_lista.append({"t": t, "e": e, "r": r, "f": f, "l": l})
                            ahorro_total += e
                        except: continue

                st.markdown(f'<div class="contador-box"><h1>{ahorro_total} €</h1><p>Ahorro Estimado</p></div>', unsafe_allow_html=True)
                
                for item in ayudas_lista:
                    st.markdown(f"""<div class="caja-ayuda"><span class="precio-tag">+{item['e']}€</span><h3>{item['t']}</h3><p>{item['r']}</p><span class="fuente-info">📍 Fuente: {item['f']}</span></div>""", unsafe_allow_html=True)
                    with st.expander("📖 Base Legal"):
                        st.write(item['l'])

                if ayudas_lista:
                    pdf_data = generar_pdf_bytes(ayudas_lista, ahorro_total, f"{situacion} en {comunidad}")
                    st.download_button("📥 DESCARGAR PDF", data=bytes(pdf_data), file_name="Estudio_Fiscal.pdf", mime="application/pdf")

            except Exception as e:
                st.error(f"Error: {e}")