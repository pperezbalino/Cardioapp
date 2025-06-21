import streamlit as st
from pdf_utils import render_pdf_view

def calcular(t):
    st.subheader(t["framingham"])
    edad = st.number_input(t["age"], min_value=20, max_value=79, step=1)
    colesterol_total = st.number_input(t["total_chol"], min_value=100, max_value=400, step=1)
    hdl = st.number_input(t["hdl"], min_value=20, max_value=100, step=1)
    sistolica = st.number_input(t["sbp"], min_value=90, max_value=200, step=1)
    fumador = st.checkbox(t["smoker"])
    diabetes = st.checkbox(t["diabetes"])
    sexo = st.radio(t["sex"], [t["male"], t["female"]])

    if st.button(t["calculate"]):
        # Simplificación del cálculo de riesgo
        puntos = 0
        if sexo == t["male"]:
            puntos += (edad - 20) * 0.3
            puntos += (colesterol_total - 160) * 0.02
            puntos -= (hdl - 35) * 0.1
            puntos += (sistolica - 120) * 0.05
            if fumador:
                puntos += 4
            if diabetes:
                puntos += 5
        else:
            puntos += (edad - 20) * 0.2
            puntos += (colesterol_total - 160) * 0.015
            puntos -= (hdl - 35) * 0.08
            puntos += (sistolica - 120) * 0.04
            if fumador:
                puntos += 3
            if diabetes:
                puntos += 4

        riesgo = min(max(int(puntos), 1), 30)
        categoria = t["high"] if riesgo >= 20 else t["moderate"] if riesgo >= 10 else t["low"]

        recomendacion = t["recommendation_moderate"]
        if riesgo >= 20:
            recomendacion = t["recommendation_high"]
        elif riesgo < 10:
            recomendacion = t["recommendation_low"]

        st.success(f"{t['10yr_risk']}: {riesgo}%\n{t['risk_level']}: {categoria}\n{t['recommendation']}: {recomendacion}")
