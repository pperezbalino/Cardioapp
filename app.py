import streamlit as st
from tools import framingham, euroscore, chads_vasc, grace, timi, bmi, ckd_epi, drug_calculator, ecg_analysis
from translations import translations

# Configuración de idioma
st.set_page_config(page_title="CardioApp", layout="centered")
if "language" not in st.session_state:
    st.session_state.language = "es"
lang = st.selectbox(
    "Idioma / Language / Langue / Sprache / Idioma / اللغة",
    list(translations.keys()),
    index=list(translations.keys()).index(st.session_state.language)
)
st.session_state.language = lang
t = translations[lang]

# Disclaimer
if "disclaimer_accepted" not in st.session_state:
    st.session_state.disclaimer_accepted = False

if not st.session_state.disclaimer_accepted:
    st.markdown(f"**{t['disclaimer_text']}**")
    if st.button(t["accept_disclaimer"]):
        st.session_state.disclaimer_accepted = True
    st.stop()

# Interfaz principal
st.title("🫀 CardioApp")
option = st.selectbox(t["select_function"], [t["scores"], t["drugs"], t["ecg"]])

if option == t["scores"]:
    score_option = st.selectbox(t["select_score"], [
        t["framingham"], t["euroscore"], t["chads"], t["grace"], t["timi"], t["bmi"], t["ckd"]
    ])

    if score_option == t["framingham"]:
        framingham.calcular(t)
    elif score_option == t["euroscore"]:
        euroscore.calcular(t)
    elif score_option == t["chads"]:
        chads_vasc.calcular(t)
    elif score_option == t["grace"]:
        grace.calcular(t)
    elif score_option == t["timi"]:
        timi.calcular(t)
    elif score_option == t["bmi"]:
        bmi.calcular(t)
    elif score_option == t["ckd"]:
        ckd_epi.calcular(t)

elif option == t["drugs"]:
    st.subheader(t["drugs_title"])
    drug_calculator.calcular(t)

elif option == t["ecg"]:
    st.subheader(t["ecg_title"])
    ecg_analysis.calcular(t)