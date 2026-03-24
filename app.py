import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from fpdf import FPDF
import datetime
import re

# --- ESTILOS CORPORATIVOS ---
st.set_page_config(page_title="GestorIA - Consultoría Oficial", layout="wide")

AZUL_CORP = (30, 41, 59)   
VERDE_CORP = (16, 185, 129) 

st.markdown(f"""
    <style>
    .stApp {{ background-color: #f8fafc; }}
    .contador-box {{
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: white; padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 25px;
    }}
    .caja-ayuda {{
        background: white; padding: 20px; border-radius: 12px;
        border-bottom: 4px solid #10b981; margin-bottom: 5px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }}
    .precio-tag {{ font-size: 1.4rem; font-weight: 800; color: #10b981; float: right; }}
    .fuente-tag {{
        background-color: #e2e8f0; color: #475569; padding: 3px 8px;
        border-radius: 5px; font-size: 0.75rem; font-weight: bold;
    }}
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
    pdf.cell(0, 10, f"Perfil: {perfil_str}", 0, 1)
    pdf.set_fill_color(*VERDE_CORP)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, f"AHORRO TOTAL ESTIMADO: {total} EUR", 0, 1, 'C', True)
    pdf.ln(10)
    pdf.set_text_color(0,0,0)
    for a in ayudas:
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(150, 8, a['t'], 0, 0)
        pdf.cell(40, 8, f"+{a['e']}e", 0, 1, 'R')
        pdf.set_font('Arial', '', 9)
        pdf.multi_cell(0, 5, f"Fuente: {a['f']}\nResumen: {a['r']}")
        pdf.ln(3)
    return pdf.output()

# --- LÓGICA DE IA ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Falta API Key en Secrets")
    st.stop()

# --- UI ---
st.title("⚖️ GestorIA Pro")

with st.expander("👤 Configuración de Perfil", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        edad = st.number_input("Edad", 18, 90, 30)
        situacion = st.selectbox("Trabajo", ["Asalariado", "Autónomo", "Desempleado", "Estudiante"])
    with col2:
        comunidad = st.selectbox("Comunidad Autónoma", ["Madrid", "Andalucía", "Cataluña", "Valencia", "Galicia", "Castilla y León", "Otras"])
        vivienda = st.selectbox("Vivienda", ["Alquiler", "Propiedad"])
    with col3:
        hijos = st.number_input("Hijos", 0, 5, 0)
        rural = st.checkbox("Vivo en zona rural")

if st.button("🚀 ANALIZAR MI AHORRO"):
    with st.spinner("Consultando fuentes oficiales..."):
        prompt = f"""
        Actúa como gestor fiscal senior. Perfil: {edad} años, {situacion}, {comunidad}, {vivienda}, Rural:{rural}, Hijos:{hijos}.
        Busca las 4 mejores deducciones. Responde EXACTAMENTE con este formato:
        [AYUDA]
        TITULO: nombre de la deduccion
        EUROS: solo el numero
        RESUMEN: explicacion muy breve de la ayuda
        FUENTE: Solo el nombre de la fuente oficial (ej: BOE, BOCM, DOGA o Web Oficial Ayuntamiento)
        [/AYUDA]
        Separa con ---
        """
        res = model.generate_content(prompt).text
        
        ayudas_finales = []
        total = 0
        bloques = res.split("[AYUDA]")
        
        for b in bloques:
            if "TITULO:" in b:
                try:
                    t = re.search(r"TITULO:\s*(.*)", b).group(1)
                    e = re.search(r"EUROS:\s*(\d+)", b).group(1)
                    r = re.search(r"RESUMEN:\s*(.*)", b).group(1)
                    f = re.search(r"FUENTE:\s*(.*)", b).group(1)
                    ayudas_finales.append({"t":t, "e":e, "r":r, "f":f})
                    total += int(e)
                except: continue

        # Pantalla de Resultados
        st.markdown(f'<div class="contador-box"><p>Tu ahorro potencial es de</p><h1>{total} €</h1></div>', unsafe_allow_html=True)
        
        for item in ayudas_finales:
            # La Cajita limpia
            st.markdown(f"""
            <div class="caja-ayuda">
                <span class="precio-tag">+{item['e']}€</span>
                <h3 style="margin:0; font-size:1.1rem; color:#1e293b;">{item['t']}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # El desplegable con la fuente y el resumen
            with st.expander("🔍 Ver detalles y Fuente Oficial"):
                st.write(f"**¿En qué consiste?** {item['r']}")
                st.markdown(f"**Fuente:** <span class='fuente-tag'>{item['f']}</span>", unsafe_allow_html=True)

        # Botón PDF
        if ayudas_finales:
            p_str = f"{situacion} en {comunidad}"
            pdf_bytes = generar_pdf_bytes(ayudas_finales, total, p_str)
            st.download_button("📥 Descargar Informe PDF Corporativo", data=bytes(pdf_bytes), file_name="Estudio_Fiscal_GestorIA.pdf", mime="application/pdf")

# Sidebar
with st.sidebar:
    st.subheader("📁 Analizador de Documentos")
    f = st.file_uploader("Subir PDF", type="pdf")
    if f:
        t_pdf = "".join([p.extract_text() for p in PdfReader(f).pages])
        if st.button("Analizar"):
            st.write(model.generate_content(f"Resume este documento fiscal: {t_pdf[:3000]}").text)