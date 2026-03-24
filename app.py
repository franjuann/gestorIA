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
        color: white; padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 25px;
    }}
    .caja-ayuda {{
        background: white; padding: 20px; border-radius: 12px;
        border-top: 5px solid #10b981; margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }}
    .precio-tag {{ font-size: 1.5rem; font-weight: 800; color: #10b981; float: right; }}
    .fuente-info {{ color: #2563eb; font-weight: bold; font-size: 0.9rem; margin-top: 10px; display: block; }}
    </style>
    """, unsafe_allow_html=True)

# --- CLASE PDF PROFESIONAL ---
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
        pdf.cell(150, 8, a['t'][:50], 0, 0)
        pdf.cell(40, 8, f"+{a['e']}e", 0, 1, 'R')
        pdf.set_font('Arial', '', 9)
        pdf.multi_cell(0, 5, f"Fuente: {a['f']}\nDetalle: {a['r']}\nBase Legal: {a['l']}")
        pdf.ln(3)
    return pdf.output()

# --- LÓGICA DE IA CON AUTODETECCIÓN DE MODELO ---
def configurar_ia():
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        try:
            # Listamos modelos y buscamos el primero que soporte generación de contenido
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    if 'gemini-1.5-flash' in m.name or 'gemini-pro' in m.name:
                        return genai.GenerativeModel(m.name)
            # Si no encuentra los preferidos, devuelve el primero disponible
            return genai.GenerativeModel('gemini-pro') 
        except Exception as e:
            st.error(f"Error al listar modelos: {e}")
            return None
    return None

model = configurar_ia()

# --- INTERFAZ ---
st.title("⚖️ GestorIA: Optimización Fiscal Pro")

with st.expander("👤 Configuración de Perfil", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        edad = st.number_input("Edad", 18, 90, 30)
        situacion = st.selectbox("Trabajo", ["Asalariado", "Autónomo", "Desempleado", "Pensionista"])
    with col2:
        comunidad = st.selectbox("Comunidad", ["Madrid", "Andalucía", "Cataluña", "Valencia", "Galicia", "Castilla y León", "Castilla-La Mancha", "Murcia", "País Vasco", "Aragón", "Extremadura"])
        vivienda = st.selectbox("Vivienda", ["Alquiler", "Propiedad con Hipoteca", "Propiedad Pagada"])
    with col3:
        hijos = st.number_input("Hijos", 0, 10, 0)
        rural = st.checkbox("Zona Rural / Despoblada")
        discapacidad = st.checkbox("Discapacidad (>=33%)")

if st.button("🚀 ANALIZAR Y VERIFICAR FUENTES OFICIALES"):
    if not model:
        st.error("Error: No se ha podido conectar con el modelo de IA. Revisa tu API Key.")
    else:
        with st.spinner("Consultando normativas oficiales..."):
            prompt = f"""Actúa como gestor fiscal. Perfil: {edad} años, {situacion}, {comunidad}, {vivienda}, Rural:{rural}, Hijos:{hijos}, Discapacidad:{discapacidad}. Busca 4 ayudas. Formato obligatorio: [AYUDA] TITULO: x EUROS: x RESUMEN: x FUENTE: x LEGAL: x [/AYUDA]"""
            
            try:
                res = model.generate_content(prompt).text
                ayudas_finales = []
                total = 0
                bloques = res.split("[AYUDA]")
                
                for b in bloques:
                    if "TITULO:" in b:
                        try:
                            t_match = re.search(r"TITULO:\s*(.*)", b)
                            e_match = re.search(r"EUROS:\s*(\d+)", b)
                            r_match = re.search(r"RESUMEN:\s*(.*)", b)
                            f_match = re.search(r"FUENTE:\s*(.*)", b)
                            l_match = re.search(r"LEGAL:\s*(.*)", b)
                            
                            if t_match and e_match:
                                ayudas_finales.append({
                                    "t": t_match.group(1).strip(),
                                    "e": int(e_match.group(1).strip()),
                                    "r": r_match.group(1).strip() if r_match else "",
                                    "f": f_match.group(1).strip() if f_match else "Fuente oficial",
                                    "l": l_match.group(1).strip() if l_match else ""
                                })
                                total += ayudas_finales[-1]["e"]
                        except: continue

                st.markdown(f'<div class="contador-box"><p>Ahorro Total Identificado</p><h1>{total} €</h1></div>', unsafe_allow_html=True)
                
                for item in ayudas_finales:
                    st.markdown(f"""
                    <div class="caja-ayuda">
                        <span class="precio-tag">+{item['e']}€</span>
                        <h3>{item['t']}</h3>
                        <p>{item['r']}</p>
                        <span class="fuente-info">📍 Fuente: {item['f']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    with st.expander("📖 Ver Base Legal Completa"):
                        st.write(item['l'])

                if ayudas_finales:
                    p_str = f"{situacion} en {comunidad}, {edad} años"
                    pdf_out = generar_pdf_bytes(ayudas_finales, total, p_str)
                    st.download_button("📥 Descargar Informe PDF Profesional", data=bytes(pdf_out), file_name="Estudio_Fiscal.pdf", mime="application/pdf")

            except Exception as e:
                st.error(f"Error de proceso con la IA: {e}")