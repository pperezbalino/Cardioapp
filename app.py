
import streamlit as st
from tools import framingham, euroscore, chads_vasc, grace, timi, bmi, ckd_epi, ecg_analysis, drug_calculator
from translations import translations
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(page_title="CardioApp", layout="centered")

# --- SELECCIÓN DE IDIOMA ---
if 'language' not in st.session_state:
    st.session_state.language = 'es'

lang = st.selectbox("Idioma / Language / Langue / Sprache / Idioma / لغة", 
                    ['es', 'en', 'fr', 'it', 'de', 'pt', 'ar'], 
                    index=['es', 'en', 'fr', 'it', 'de', 'pt', 'ar'].index(st.session_state.language))

st.session_state.language = lang
t = translations[lang]

# --- DISCLAIMER DE ACEPTACIÓN ---
if 'disclaimer_accepted' not in st.session_state:
    st.session_state.disclaimer_accepted = False

if not st.session_state.disclaimer_accepted:
    if st.button(t['accept_disclaimer']):
        st.session_state.disclaimer_accepted = True
    else:
        st.warning(t['disclaimer_text'])
        st.stop()

# --- MENÚ PRINCIPAL ---
st.title("CardioApp")
option = st.selectbox(t['select_function'], [t['scores'], t['drugs'], t['ecg']])

# --- PANTALLAS ---
if option == t['scores']:
    score_option = st.selectbox(t['select_score'], 
        [t['framingham'], t['euroscore'], t['chads'], t['grace'], t['timi'], t['bmi'], t['ckd']])

    if score_option == t['framingham']:
        framingham.run(t)
    elif score_option == t['euroscore']:
        euroscore.run(t)
    elif score_option == t['chads']:
        chads_vasc.run(t)
    elif score_option == t['grace']:
        grace.run(t)
    elif score_option == t['timi']:
        timi.run(t)
    elif score_option == t['bmi']:
        bmi.run(t)
    elif score_option == t['ckd']:
        ckd_epi.run(t)

elif option == t['drugs']:
    drug_calculator.run(t)

elif option == t['ecg']:
    ecg_analysis.run(t)

# --- FUNCIONES AUXILIARES (PDF ECG) ---
def generate_ecg_pdf(initials, ecg_report, lang):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Logo
    try:
        logo_path = "logo.png"
        logo = ImageReader(logo_path)
        p.drawImage(logo, 40, height - 80, width=50, preserveAspectRatio=True)
    except:
        pass

    # Encabezado
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, height - 60, f"CardioApp - {translations[lang]['ecg_report']}")
    p.setFont("Helvetica", 11)
    p.drawString(100, height - 80, f"{translations[lang]['initials']}: {initials}")
    p.drawString(100, height - 95, f"{translations[lang]['date']}: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Informe
    p.setFont("Helvetica", 12)
    text = p.beginText(40, height - 130)
    text.setLeading(16)
    for line in ecg_report.splitlines():
        text.textLine(line)
    p.drawText(text)

    # Advertencia
    p.setFont("Helvetica-Oblique", 9)
    p.drawString(40, 40, translations[lang]['disclaimer_pdf'])
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
