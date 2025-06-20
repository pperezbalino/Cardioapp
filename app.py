
import streamlit as st
from tools import (
    framingham, bmi, euroscore, chads_vasc, grace,
    timi, ckd_epi, drug_calculator, ecg_analysis
)
from translations import translations
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

# Configuración general
st.set_page_config(page_title="CardioApp", layout="centered")

# Selección de idioma
if 'language' not in st.session_state:
    st.session_state.language = 'es'

lang = st.selectbox(
    "Idioma / Language / Langue / Lingua / Idioma / Sprache / Língua",
    ['es', 'en', 'fr', 'it', 'de', 'pt'],
    index=['es', 'en', 'fr', 'it', 'de', 'pt'].index(st.session_state.language)
)
st.session_state.language = lang
t = translations[lang]

# Mostrar disclaimer una vez
if 'disclaimer_accepted' not in st.session_state:
    st.session_state.disclaimer_accepted = False

if not st.session_state.disclaimer_accepted:
    st.markdown(f"**{t['disclaimer_text']}**")
    if st.button(t['accept_disclaimer']):
        st.session_state.disclaimer_accepted = True
    st.stop()

# Menú principal
st.title("🫀 CardioApp")
option = st.selectbox("Selecciona una herramienta:", [
    "Framingham",
    "Índice de Masa Corporal (BMI)",
    "EuroSCORE II",
    "CHA₂DS₂-VASc",
    "HAS-BLED (grace.py)",
    "TIMI",
    "Filtrado Glomerular (CKD-EPI)",
    "Calculadora de Drogas de Urgencia",
    "Análisis de ECG (IA)"
])

# Logo
st.image("logo.png", width=100)

# Generar PDF
def generar_pdf(titulo, contenido, lang_code):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Logo
    try:
        logo = ImageReader("logo.png")
        c.drawImage(logo, 40, height - 80, width=60, preserveAspectRatio=True, mask='auto')
    except:
        pass

    # Título
    c.setFont("Helvetica-Bold", 14)
    c.drawString(120, height - 50, titulo)

    # Contenido principal
    c.setFont("Helvetica", 12)
    text_obj = c.beginText(40, height - 100)
    for line in contenido.split("\n"):
        text_obj.textLine(line)
    c.drawText(text_obj)

    # Disclaimer
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(40, 40, t['report_footer'])

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# Ejecutar herramienta seleccionada
resultado = None
if option == "Framingham":
    resultado = framingham.calcular(t)
elif option == "Índice de Masa Corporal (BMI)":
    resultado = bmi.calcular(t)
elif option == "EuroSCORE II":
    resultado = euroscore.calcular(t)
elif option == "CHA₂DS₂-VASc":
    resultado = chads_vasc.calcular(t)
elif option == "HAS-BLED (grace.py)":
    resultado = grace.calcular(t)
elif option == "TIMI":
    resultado = timi.calcular(t)
elif option == "Filtrado Glomerular (CKD-EPI)":
    resultado = ckd_epi.calcular(t)
elif option == "Calculadora de Drogas de Urgencia":
    resultado = drug_calculator.calcular(t)
elif option == "Análisis de ECG (IA)":
    resultado = ecg_analysis.calcular(t)

# Mostrar resultado y opción de exportar a PDF
if resultado:
    st.markdown("### Resultado")
    st.write(resultado)

    if st.button("📄 Exportar a PDF"):
        pdf = generar_pdf(t['ecg_report_title'], resultado, lang)
        st.download_button(
            label="Descargar informe PDF",
            data=pdf,
            file_name=f"informe_{lang}.pdf",
            mime="application/pdf"
        )
