import streamlit as st
from tools import framingham, euroscore, chads_vasc, grace, timi, bmi, ckd_epi, drug_calculator, ecg_analysis
from translations import translations

# Idiomas legibles
idioma_nombres = {
    "es": "Español",
    "en": "English",
    "fr": "Français",
    "it": "Italiano",
    "de": "Deutsch",
    "pt": "Português"
}

# Configuración general
st.set_page_config(page_title="CardioApp", layout="centered")

# Selector de idioma
if "language" not in st.session_state:
    st.session_state.language = "es"
lang_legible = st.selectbox("Idioma", [idioma_nombres[k] for k in idioma_nombres])
lang = [k for k, v in idioma_nombres.items() if v == lang_legible][0]
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

# Mostrar logo y título
st.image("logo.png", width=120)
st.title("🫀 CardioApp")

# Sección: Scores (expandible)
with st.expander(t["scores"]):
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

# Sección: Drogas (expandible)
with st.expander(t["drugs"]):
    drug_calculator.calcular(t)

# Sección: ECG (expandible)
with st.expander(t["ecg"]):
    ecg_analysis.calcular(t)