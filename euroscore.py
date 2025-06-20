import streamlit as st
from pdf_utils import render_pdf_view

def calcular(t):
    st.subheader(t["euroscore"])
    edad = st.number_input(t["age"], min_value=18, max_value=100, step=1)
    sexo = st.radio(t["sex"], [t["male"], t["female"]])
    creatinina = st.number_input(t["creatinine"], min_value=0.1, max_value=10.0, step=0.1)
    fraccion_eyeccion = st.slider(t["lvef"], 10, 70, 55)
    cirugia_urgente = st.checkbox(t["urgent_surgery"])
    reoperacion = st.checkbox(t["redo_surgery"])
    isquemia_cronica = st.checkbox(t["chronic_angina"])

    if st.button(t["calculate"]):
        # Cálculo simulado de EuroSCORE II logístico
        riesgo = (
            0.02 * edad +
            (0.5 if sexo == t["female"] else 0) +
            1.2 * (creatinina > 2) +
            1.5 * (fraccion_eyeccion < 30) +
            1.5 * cirugia_urgente +
            1.5 * reoperacion +
            1.0 * isquemia_cronica
        )

        riesgo = min(max(riesgo, 0), 40)
        categoria = t["high"] if riesgo >= 10 else t["moderate"] if riesgo >= 4 else t["low"]

        # Mostrar resultado en pantalla
        st.markdown(f"### {t['result']}")
        st.success(f"{t['surgical_risk']}: **{riesgo:.1f}%**")
        st.info(f"{t['risk_level']}: **{categoria}**")

        # Preparar texto para el PDF
        pdf_text = f"""{t['euroscore']}\n\n{t['age']}: {edad}\n{t['sex']}: {sexo}\n{t['creatinine']}: {creatinina} mg/dL\n{t['lvef']}: {fraccion_eyeccion}%\n{t['urgent_surgery']}: {"Sí" if cirugia_urgente else "No"}\n{t['redo_surgery']}: {"Sí" if reoperacion else "No"}\n{t['chronic_angina']}: {"Sí" if isquemia_cronica else "No"}\n\n{t['surgical_risk']}: {riesgo:.1f}%\n{t['risk_level']}: {categoria}"""

        # Mostrar PDF integrado
        render_pdf_view(t["euroscore"], pdf_text, t)