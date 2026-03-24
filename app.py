import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from fpdf import FPDF
import datetime
import re

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="GestorIA Pro - Informe Oficial", layout="wide")

AZUL_CORP = (30, 41, 59)   
VERDE_CORP = (16, 185, 129) 

st.markdown(f"""
    <style>
    .stApp {{ background-color: #f8fafc; }}
    .contador-box {{
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: white; padding: 35px; border-radius: 20px; text-align: center;
    }}
    .caja-ayuda {{
        background: white; padding: 25px; border-radius: 15px;
        border-top: 5px solid #10b981; margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }}
    .precio-tag {{ font-size: 1.5rem; font-weight: 800; color: #10b981; float: right; }}
    .stButton>button {{ background-color: #1e293b; color: white; border-radius: 10px; height: 3.5rem; font-weight: bold; border: none; }}
    .stButton>button:hover {{ background-color: #10b981; }}
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN GENERADORA DE PDF PROFESIONAL ---
class PDF_Informe(FPDF):
    def header(self):
        self.set_fill_color(*AZUL_CORP)
        self.rect(0, 0, 210, 40, 'F')
        self.set_font('Arial', 'B', 20)
        self.set_text_color(255, 255, 255)
        self.cell(0, 20, 'INFORME DE OPTIMIZACIÓN FISCAL', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, f'Generado por GestorIA Pro - {datetime.date.today().strftime("%d/%m/%Y")}', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, 'Este informe es orientativo. Consulte con su gestor oficial. GestorIA © 2026', 0, 0, 'C')

def crear_pdf(perfil, ahorro_total, ayudas):
    pdf = PDF_Informe()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    pdf.ln(25)
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(*AZUL_CORP)
    pdf.cell(0, 10, '1. RESUMEN DEL PERFIL ANALIZADO', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(50, 50, 50)
    for k, v in perfil.items():
        pdf.cell(0, 7, f"- {k}: {v}", 0, 1)

    pdf.ln(10)
    pdf.set_fill_color(*VERDE_CORP)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 15, f'AHORRO POTENCIAL TOTAL: {ahorro_total} EUR', 0, 1, 'C', True)

    pdf.ln(10)
    pdf.set_text_color(*AZUL_CORP)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, '2. DETALLE DE DEDUCCIONES Y AYUDAS', 0, 1)
    
    for item in ayudas:
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(*AZUL_CORP)
        pdf.cell(160, 10, item['t'][:40], 0, 0)
        pdf.set_text_color(*VERDE_CORP)
        pdf.cell(30, 10, f"+{item['e']}e", 0, 1, 'R')
        
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(80, 80, 80)
        pdf.multi_cell(0, 6, f"Descripcion: {item['r']}")
        pdf.set_font('Arial', 'I', 9)
        pdf.set_text_color(*AZUL_CORP)
        pdf.multi_cell(0, 6, f"Fuente Legal: {item['f']}")
        pdf.ln(5)
    
    # IMPORTANTE: Devolvemos los bytes del PDF de forma que Streamlit los acepte
    return pdf.output()

# --- LÓGICA DE IA ---
def configurar_ia():
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        try:
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            return "models/gemini-2.5-flash" if "models/gemini-2.5-flash" in models else models[0]
        except: return None
    return None

model_name = configurar_ia()

# --- INTERFAZ ---
st.title("⚖️ GestorIA Pro")

with st.container():
    st.markdown("### 📋 Configuración del Perfil")
    c1, c2, c3 = st.columns(3)
    with c1:
        edad = st.number_input("Edad", 18, 99, 30)
        situacion = st.selectbox("Situación", ["Asalariado", "Autónomo", "Desempleado", "Pensionista"])
        ingresos = st.select_slider("Ingresos", options=["0-15k", "15k-22k", "22k-35k", "35k-60k", "+60k"])
    with c2:
        comunidad = st.selectbox("Comunidad", ["Andalucía", "Aragón", "Asturias", "Baleares", "Canarias", "Cantabria", "Castilla y León", "Castilla-La Mancha", "Cataluña", "Valencia", "Extremadura", "Galicia", "Madrid", "Murcia", "Navarra", "País Vasco", "La Rioja"])
        vivienda = st.selectbox("Vivienda", ["Alquiler", "Hipoteca pre-2013", "Propiedad pagada"])
        zona_rural = st.checkbox("Zona rural")
    with c3:
        hijos = st.number_input("Hijos", 0, 10, 0)
        discapacidad = st.checkbox("Discapacidad")
        familia_numerosa = st.checkbox("Fam. Numerosa")

st.divider()

if st.button("🔍 GENERAR ESTUDIO PERSONALIZADO"):
    if not model_name:
        st.error("Falta API Key.")
    else:
        model = genai.GenerativeModel(model_name)
        with st.spinner("Generando informe..."):
            prompt = f"Actúa como gestor fiscal. Perfil: {edad} años, {situacion}, {ingresos}, {comunidad}, {vivienda}, Rural:{zona_rural}, Hijos:{hijos}, Discapacidad:{discapacidad}, F.Num:{familia_numerosa}. Busca 4 ayudas. Formato obligatorio: [AYUDA] TITULO: x EUROS: x RESUMEN: x FUENTE: x EXPLICACION_LEGAL: x [/AYUDA]"
            response = model.generate_content(prompt)
            texto_ia = response.text
            
            # Extracción limpia
            ayudas_lista = []
            total_ahorro = 0
            bloques = texto_ia.split("[AYUDA]")
            for b in bloques:
                if "TITULO:" in b:
                    try:
                        t = re.search(r"TITULO: (.*)", b).group(1)
                        e = int(re.search(r"EUROS: (\d+)", b).group(1))
                        r = re.search(r"RESUMEN: (.*)", b).group(1)
                        f = re.search(r"FUENTE: (.*)", b).group(1)
                        ayudas_lista.append({"t":t, "e":e, "r":r, "f":f})
                        total_ahorro += e
                    except: continue

            # Visualización
            st.markdown(f'<div class="contador-box"><h1>{total_ahorro} €</h1><p>Ahorro Potencial</p></div>', unsafe_allow_html=True)
            
            for item in ayudas_lista:
                st.markdown(f'<div class="caja-ayuda"><span class="precio-tag">+{item["e"]}€</span><h3>{item["t"]}</h3><p>{item["r"]}</p></div>', unsafe_allow_html=True)
            
            # --- EL ARREGLO DEL BOTÓN ---
            try:
                # Generamos el PDF
                pdf_output = crear_pdf({
                    "Comunidad": comunidad, 
                    "Situación": situacion, 
                    "Ingresos": ingresos
                }, total_ahorro, ayudas_lista)
                
                # Convertimos explícitamente a bytes para Streamlit
                pdf_bytes = bytes(pdf_output)
                
                st.download_button(
                    label="📥 DESCARGAR INFORME PDF PROFESIONAL",
                    data=pdf_bytes,
                    file_name=f"Informe_Fiscal_{comunidad}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Error al generar el PDF: {e}")

with st.sidebar:
    st.subheader("📁 Analizador PDF")
    pdf_up = st.file_uploader("Subir documento", type="pdf")
    if pdf_up and model_name:
        txt_pdf = "".join([p.extract_text() for p in PdfReader(pdf_up).pages])
        if st.button("Analizar"):
            st.info(genai.GenerativeModel(model_name).generate_content(f"Resume: {txt_pdf[:4000]}").text)