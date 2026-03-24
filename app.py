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
    # Intentamos sacar la clave de los Secretos de Streamlit
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = None
    st.error("Error de configuración: No se ha encontrado la API Key en los Secrets.")
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
            comunidad = st.selectbox("Comunidad Autónoma de residencia", ["Andalucía", "Aragón", "Asturias", "Baleares", "Canarias", "Cantabria", "Castilla y León", "Castilla-La Mancha", "Cataluña", "Comunidad Valenciana", "Extremadura", "Galicia", "Madrid", "Murcia", "Navarra", "País Vasco", "La Rioja"], index=0)
            zona_rural = st.radio("¿Vives en una zona despoblada o municipio < 5.000 hab.?", ["No", "Sí"], help="Revisa la normativa de tu C.A. sobre despoblación.")
            vivienda = st.selectbox("Tu vivienda habitual es", ["Alquiler", "Propiedad con hipoteca (pre-2013)", "Propiedad con hipoteca (post-2013)", "Propiedad pagada", "Vivienda cedida"])

        with col3:
            st.markdown("#### 👨‍👩‍👧 Cargas y Salud")
            hijos = st.number_input("Hijos a cargo (menores de 25 años)", min_value=0, step=1)
            discapacidad = st.checkbox("Discapacidad propia o familiar (≥33%)")
            familia_numerosa = st.checkbox("Título de familia numerosa activo")
        
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    
    # --- PANELES DE ACCIÓN ---
    col_accion, col_descarga = st.columns([2, 1])

    # Variable de estado para guardar la respuesta de la IA
    if 'report_text' not in st.session_state:
        st.session_state['report_text'] = None

    with col_accion:
        st.markdown("### 🚀 PASO 2: Obtener Resultados")
        if st.button("🔥 GENERAR MI DIAGNÓSTICO DE AHORRO FISCAL"):
            with st.spinner("Consultando normativas y boletines oficiales para {comunidad}..."):
                # Prompt hiper-estructurado para respuesta profesional
                prompt = f"""
                Actúa como un Socio Senior de una gestoría administrativa experta en optimización fiscal en España. 
                Analiza el siguiente perfil y encuentra deducciones IRPF (estatales y de {comunidad}), becas y ayudas:

                DATOS DEL CLIENTE:
                - Edad: {edad} años.
                - Ubicación: Residente en {comunidad} (Zona despoblada: {zona_rural}).
                - Trabajo: {situacion} con ingresos de {ingresos}€ anuales.
                - Vivienda: {vivienda}.
                - Familia: {hijos} hijos, Discapacidad: {discapacidad}, Familia Numerosa: {familia_numerosa}.

                PROPORCIONA UN INFORME ESTRUCTURADO CON:
                1. 💰 DEDUCCIONES IRPF: Lista clara de deducciones a las que califica (estatales y autonómicas de {comunidad}).
                2. 🎓 BECAS Y AYUDAS: Identifica becas de estudio, ayudas al alquiler joven, bono térmico o ayudas por hijos.
                3. 🌳 BENEFICIO RURAL: Si vive en zona despoblada, detalla las ventajas específicas por residencia.
                4. 📈 PLAN DE ACCIÓN: Pasos para aplicar esto en la próxima declaración.
                Tono profesional, directo y enfocado al ahorro real. Usa emojis para estructurar.
                """
                
                try:
                    response = model.generate_content(prompt)
                    st.session_state['report_text'] = response.text
                    st.success("✅ Diagnóstico generado con éxito. Revisa el informe abajo.")
                except Exception as e:
                    st.error(f"Error al conectar con Gemini: {e}")

    with col_descarga:
        if st.session_state['report_text']:
            st.markdown("### 📥 PASO 3: Guardar")
            st.write("Descárgate este informe para tenerlo a mano o enseñarlo en tu gestoría.")
            
            # Formateamos el informe profesional para la descarga (Marca Personal)
            fecha_hoy = datetime.date.today().strftime("%d/%m/%Y")
            nombre_archivo = f"Informe_GestorIA_{comunidad}_{fecha_hoy}.txt"
            
            # Contenido formateado del archivo descargable (puedes añadir tu marca aquí)
            contenido_descarga = f"""
============================================================
INFORME DE OPTIMIZACIÓN FISCAL PERSONALIZADO
Generado por GestorIA Pro - Tu Asistente Inteligente
Fecha: {fecha_hoy}
============================================================

RESUMEN DE TU PERFIL:
- Edad: {edad} años.
- Ubicación: {comunidad} (Zona rural/despoblada: {zona_rural}).
- Situación: {situacion} ({ingresos}€ brutos/año).
- Vivienda: {vivienda}.
- Cargas: {hijos} hijos, Discapacidad: {discapacidad}, Familia Numerosa: {familia_numerosa}.

------------------------------------------------------------
DIAGNÓSTICO Y PLAN DE AHORRO CALCULADO POR IA:
------------------------------------------------------------
{st.session_state['report_text']}

------------------------------------------------------------
DISCLAIMER: Este informe es orientativo y basado en la 
normativa fiscal vigente. Se recomienda confirmar con un 
gestor administrativo profesional antes de presentar 
cualquier declaración.

GestorIA Pro © 2025. Contacto: tuemail@empresa.com
============================================================
"""
            
            # Botón de Descarga Oficial de Streamlit
            st.download_button(
                label="📥 DESCARGAR INFORME PROFESIONAL (TXT)",
                data=contenido_descarga,
                file_name=nombre_archivo,
                mime="text/plain"
            )

    # --- ÁREA DE RESULTADOS VISUALES ---
    if st.session_state['report_text']:
        st.divider()
        st.markdown("<div class='main-card'>", unsafe_allow_html=True)
        st.markdown("## 📊 Tu Informe de Ahorro en Pantalla")
        st.write(st.session_state['report_text'])
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.warning("🔒 Sistema bloqueado. Por favor, introduce tu Google API Key en la barra lateral para activar la consultoría.")