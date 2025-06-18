
import streamlit as st
from tools import framingham, euroscore, chads_vasc, grace, timi, bmi, ckd_epi, ecg_analysis, drug_calculator
from report_generator import generate_pdf_report
from translation import translate_text

# Configuración inicial
st.set_page_config(page_title="CardioApp", page_icon="❤️")
st.title("❤️ CardioApp")

# Selección de idioma
languages = {
    "Español": "es",
    "English": "en",
    "Français": "fr",
    "Italiano": "it",
    "Português": "pt",
    "Deutsch": "de"
}
language = st.sidebar.selectbox("Idioma / Language", list(languages.keys()))
lang_code = languages[language]

# Menú principal
menu = st.sidebar.radio(translate_text("Selecciona una herramienta:", lang_code), [
    "Framingham",
    "EuroSCORE II",
    "CHA₂DS₂-VASc",
    "GRACE Score",
    "TIMI Score",
    "Índice de Masa Corporal (IMC)",
    "Filtrado Glomerular (CKD-EPI)",
    "Calculadora de Drogas de Emergencia",
    "Lectura de ECG",
    "Exportar PDF"
])

if menu == "Framingham":
    framingham(lang_code)
elif menu == "EuroSCORE II":
    euroscore(lang_code)
elif menu == "CHA₂DS₂-VASc":
    chads_vasc(lang_code)
elif menu == "GRACE Score":
    grace(lang_code)
elif menu == "TIMI Score":
    timi(lang_code)
elif menu == "Índice de Masa Corporal (IMC)":
    bmi(lang_code)
elif menu == "Filtrado Glomerular (CKD-EPI)":
    ckd_epi(lang_code)
elif menu == "Calculadora de Drogas de Emergencia":
    drug_calculator(lang_code)
elif menu == "Lectura de ECG":
    ecg_analysis(lang_code)
elif menu == "Exportar PDF":
    generate_pdf_report(lang_code)
