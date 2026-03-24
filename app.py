import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import datetime
import re

# --- CONFIGURACIÓN DE PÁGINA Y MARCA ---
st.set_page_config(page_title="GestorIA - Tu Ahorro Inteligente", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .contador-box {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .caja-ayuda {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border-left: 8px solid #2563eb;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .precio-tag {
        font-size: 1.4rem;
        font-weight: 800;
        color: #059669;
        float: right;
    }
    .stButton>button { background-color: #2563eb; color: white; border-radius: 8px; height: 3rem; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE CONEXIÓN (SECRETS) ---
def configurar_ia():
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        try:
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            return "models/gemini-2.5-flash" if "models/gemini-2.5-flash" in models else models[0]
        except: return None
    return None

model_name = configurar_ia()

# --- INTERFAZ PRINCIPAL ---
st.title("🎯 GestorIA: Optimizador Fiscal Pro")
st.write("Descubre y descarga tu plan de ahorro personalizado en 2 minutos.")

# --- FORMULARIO INTEGRAL (MANTENIENDO TODO LO ANTERIOR) ---
with st.expander("👤 CONFIGURAR MI PERFIL FISCAL (Completa aquí)", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        edad = st.number_input("Edad", 18, 99, 30)
        situacion = st.selectbox("Trabajo", ["Asalariado", "Autónomo", "Pluriactividad", "Desempleado", "Estudiante", "Pensionista"])
        ingresos = st.select_slider("Ingresos brutos/año", options=["0-15k", "15k-22k", "22k-35k", "35k-60k", "+60k"], value="22k-35k")
    with col2:
        comunidad = st.selectbox("Comunidad Autónoma", ["Andalucía", "Aragón", "Asturias", "Baleares", "Canarias", "Cantabria", "Castilla y León", "Castilla-La Mancha", "Cataluña", "Valencia", "Extremadura", "Galicia", "Madrid", "Murcia", "Navarra", "País Vasco", "La Rioja"])
        vivienda = st.selectbox("Vivienda", ["Alquiler", "Hipoteca pre-2013", "Hipoteca post-2013", "Propiedad pagada"])
        zona_rural = st.checkbox("Vivo en zona rural o municipio pequeño (<5.000 hab)")
    with col3:
        hijos = st.number_input("Hijos a cargo", 0, 10, 0)
        discapacidad = st.checkbox("Discapacidad propia/familiar (≥33%)")
        familia_numerosa = st.checkbox("Familia Numerosa")

st.divider()

# --- ACCIÓN Y RESULTADOS ---
if st.button("🚀 CALCULAR MI AHORRO TOTAL"):
    if not model_name:
        st.error("Error: Configura tu GOOGLE_API_KEY en los Secrets.")
    else:
        model = genai.GenerativeModel(model_name)
        with st.spinner("Analizando normativas estatales y autonómicas..."):
            
            prompt = f"""
            Actúa como un Socio de Gestoría Senior. Analiza este perfil:
            - Edad: {edad}, Comunidad: {comunidad}, Trabajo: {situacion}, Ingresos: {ingresos}.
            - Vivienda: {vivienda}, Zona Rural: {zona_rural}, Hijos: {hijos}, Discapacidad: {discapacidad}, F. Numerosa: {familia_numerosa}.

            Busca las 4 mejores deducciones o ayudas. Responde EXCLUSIVAMENTE con este formato para cada una:
            [AYUDA]
            TITULO: Nombre corto
            EUROS: Solo el número estimado de ahorro anual (ej: 500)
            RESUMEN: Una frase explicativa
            LINK: Enlace o nombre del organismo
            [/AYUDA]
            Separa cada bloque con '---'. Al final, añade un resumen motivador.
            """
            
            response = model.generate_content(prompt)
            texto_ia = response.text
            st.session_state['full_report'] = texto_ia # Guardamos para el informe descargable

            # --- EXTRACCIÓN DE DATOS Y CONTADOR ---
            bloques = texto_ia.split("---")
            total_ahorro = 0
            cards_data = []

            for b in bloques:
                if "[AYUDA]" in b:
                    try:
                        titulo = re.search(r"TITULO: (.*)", b).group(1)
                        euros_str = re.search(r"EUROS: (\d+)", b).group(1)
                        resumen = re.search(r"RESUMEN: (.*)", b).group(1)
                        link = re.search(r"LINK: (.*)", b).group(1)
                        
                        euros = int(euros_str)
                        total_ahorro += euros
                        cards_data.append({"t": titulo, "e": euros, "r": resumen, "l": link})
                    except: continue

            # --- MOSTRAR CONTADOR TOTAL ---
            st.markdown(f"""
                <div class="contador-box">
                    <p style="margin:0; font-size:1.2rem; opacity:0.8;">Ahorro Potencial Total</p>
                    <h1 style="margin:0; font-size:4rem; color:white;">{total_ahorro} €</h1>
                    <p style="margin:0; font-size:0.9rem;">Estimación basada en tu perfil para el ejercicio actual</p>
                </div>
            """, unsafe_allow_html=True)

            # --- MOSTRAR CAJITAS VISUALES ---
            cols_cards = st.columns(2)
            for i, card in enumerate(cards_data):
                with cols_cards[i % 2]:
                    st.markdown(f"""
                        <div class="caja-ayuda">
                            <span class="precio-tag">+{card['e']}€</span>
                            <h3 style="margin-top:0;">{card['t']}</h3>
                            <p style="color:#475569; font-size:0.9rem;">{card['r']}</p>
                            <small>📍 {card['l']}</small>
                        </div>
                    """, unsafe_allow_html=True)

            # --- BOTÓN DE DESCARGA (MANTENIENDO LO ANTERIOR) ---
            st.divider()
            fecha = datetime.date.today().strftime("%d/%m/%Y")
            info_descarga = f"INFORME GESTORIA PRO\nFecha: {fecha}\nAhorro Total Estimado: {total_ahorro}€\n\nDetalles:\n{texto_ia}"
            
            st.download_button(
                label="📥 DESCARGAR MI INFORME PROFESIONAL",
                data=info_descarga,
                file_name=f"Plan_Ahorro_{comunidad}.txt",
                mime="text/plain"
            )

# --- ÁREA DE PDF (MANTENIENDO LO ANTERIOR) ---
with st.sidebar:
    st.divider()
    st.subheader("📄 Analizar Documento Extra")
    pdf_file = st.file_uploader("Sube un PDF (Borrador, carta, etc.)", type="pdf")
    if pdf_file and model_name:
        reader = PdfReader(pdf_file)
        pdf_text = "".join([p.extract_text() for p in reader.pages])
        if st.button("Analizar PDF"):
            model = genai.GenerativeModel(model_name)
            res = model.generate_content(f"Explica este documento para un {situacion} de {edad} años: {pdf_text[:5000]}")
            st.info(res.text)