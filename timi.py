import streamlit as st

def calcular_timi(edad, factores_riesgo, uso_aspirina, angina_severa, elevacion_st, troponina):
    score = 0
    if edad >= 65:
        score += 1
    if factores_riesgo:
        score += 1
    if uso_aspirina:
        score += 1
    if angina_severa:
        score += 1
    if elevacion_st:
        score += 1
    if troponina:
        score += 1
    return score

def mostrar_timi(t):
    st.subheader(t["timi"])

    edad = st.number_input(t["age"], min_value=0, max_value=120, value=50)
    factores_riesgo = st.checkbox(t["timi_risk_factors"])
    uso_aspirina = st.checkbox(t["timi_aspirin"])
    angina_severa = st.checkbox(t["timi_angina"])
    elevacion_st = st.checkbox(t["timi_st_elevation"])
    troponina = st.checkbox(t["timi_troponin"])

    if st.button(t["calculate"]):
        score = calcular_timi(edad, factores_riesgo, uso_aspirina, angina_severa, elevacion_st, troponina)
        st.success(f"{t['result']}: {score}")
