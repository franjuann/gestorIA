import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from fpdf import FPDF
import datetime
import re

# --- 1. CONFIGURACIÓN VISUAL CORPORATIVA ---
st.set_page_config(page_title="GestorIA - Optimización Fiscal", layout="wide")

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

# --- 2. GENERADOR DE PDF PROFESIONAL ---
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

# --- 3. CONEXIÓN CON LA IA (MODELO ESTABLE) ---
def iniciar_modelo():
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Usamos el nombre de modelo más compatible
        return genai.GenerativeModel('gemini-1.5-flash')
    return None

model = iniciar_modelo()

# --- 4. INTERFAZ DE USUARIO ---
st.title("⚖️ GestorIA Pro: Tu Consultor Fiscal IA")

with st.expander("👤 Configura tu Perfil para el Cálculo", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        edad = st.number_input("Edad", 18, 95, 30)
        comunidad = st.selectbox("Comunidad Autónoma", ["Madrid", "Andalucía", "Cataluña", "Valencia", "Galicia", "Castilla y León", "Castilla-La Mancha", "Murcia", "Aragón", "Baleares", "Canarias", "Cantabria", "Extremadura", "Navarra", "País Vasco", "Asturias", "La Rioja"])
    with c2:
        situacion = st.selectbox("Situación Laboral", ["Asalariado", "Autónomo", "Desempleado", "Pensionista"])
        vivienda = st.selectbox("Vivienda", ["Alquiler", "Hipoteca (vivienda habitual)", "Propiedad pagada"])
    with c3:
        hijos = st.number_input("Hijos a cargo", 0, 10, 0)
        rural = st.checkbox("Residencia en zona rural")
        discapacidad = st.checkbox("Discapacidad (>=33%)")

st.divider()

if st.button("🚀 ANALIZAR AHORRO Y BUSCAR FUENTES"):
    if not model:
        st.error("API Key no detectada en Secrets.")
    else:
        with st.spinner("Consultando bases de datos del BOE y boletines autonómicos..."):
            prompt = f"""
            Actúa como gestor fiscal experto. Analiza este perfil: {edad} años, {situacion}, {comunidad}, {vivienda}, Rural:{rural}, Hijos:{hijos}, Discapacidad:{discapacidad}.
            Busca las 4 deducciones más importantes. Responde EXACTAMENTE con este formato:
            [AYUDA]
            TITULO: nombre corto
            EUROS: solo el numero
            RESUMEN: explicacion en una frase
            FUENTE: Referencia oficial (BOE, nombre de boletin o web oficial)
            LEGAL: explicacion tecnica corta de la ley
            [/AYUDA]
            Separa bloques con '---'.
            """
            
            try:
                response = model.generate_content(prompt)
                texto = response.text
                
                ayudas_lista = []
                ahorro_total = 0
                bloques = texto.split("[AYUDA]")
                
                for b in bloques:
                    if "TITULO:" in b:
                        try:
                            # Extracción segura con Regex
                            t_val = re.search(r"TITULO:\s*(.*)", b).group(1).strip()
                            e_val = int(re.search(r"EUROS:\s*(\d+)", b).group(1).strip())
                            r_val = re.search(r"RESUMEN:\s*(.*)", b).group(1).strip()
                            f_val = re.search(r"FUENTE:\s*(.*)", b).group(1).strip()
                            l_val = re.search(r"LEGAL:\s*(.*)", b).group(1).strip()
                            
                            ayudas_lista.append({
                                "t": t_val, "e": e_val, "r": r_val, "f": f_val, "l": l_val
                            })
                            ahorro_total += e_val
                        except:
                            continue

                # --- RENDER DE RESULTADOS ---
                st.markdown(f"""
                    <div class="contador-box">
                        <p style="margin:0; opacity:0.8;">Ahorro Potencial Identificado</p>
                        <h1 style="margin:0; font-size:3.5rem;">{ahorro_total} €</h1>
                    </div>
                """, unsafe_allow_html=True)

                for item in ayudas_lista:
                    st.markdown(f"""
                        <div class="caja-ayuda">
                            <span class="precio-tag">+{item['e']}€</span>
                            <h3 style="margin:0; color:#1e293b;">{item['t']}</h3>
                            <p style="color:#64748b; margin:10px 0;">{item['r']}</p>
                            <span class="fuente-info">📍 Fuente: {item['f']}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    with st.expander("📖 Ver Base Legal y Explicación del BOE"):
                        st.write(f"**Referencia:** {item['f']}")
                        st.write(f"**Justificación:** {item['l']}")

                # --- BOTÓN DE DESCARGA PDF ---
                if ayudas_lista:
                    st.divider()
                    perfil_resumen = f"{situacion} en {comunidad}, {hijos} hijos"
                    pdf_data = generar_pdf_bytes(ayudas_lista, ahorro_total, perfil_resumen)
                    st.download_button(
                        label="📥 DESCARGAR INFORME PDF CORPORATIVO",
                        data=bytes(pdf_data),
                        file_name=f"Informe_Fiscal_{comunidad}.pdf",
                        mime="application/pdf"
                    )

            except Exception as e:
                if "429" in str(e):
                    st.warning("Has superado el límite gratuito de Google. Espera 60 segundos y vuelve a pulsar el botón.")
                else:
                    st.error(f"Error inesperado: {e}")

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 📂 Análisis de Documentos")
    archivo = st.file_uploader("Sube un PDF fiscal", type="pdf")
    if archivo and model:
        if st.button("Analizar Documento"):
            lector = PdfReader(archivo)
            texto_pdf = "".join([p.extract_text() for p in lector.pages])
            analisis = model.generate_content(f"Resume este documento fiscal de forma sencilla: {texto_pdf[:4000]}")
            st.info(analisis.text)