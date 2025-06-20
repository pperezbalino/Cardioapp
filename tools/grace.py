
import streamlit as st
import math

def calculate_grace_score(age, heart_rate, systolic_bp, creatinine, killip_class,
                          cardiac_arrest, st_depression, elevated_troponin):
    score = 0

    if age < 30:
        score += 0
    elif age < 40:
        score += 8
    elif age < 50:
        score += 25
    elif age < 60:
        score += 41
    elif age < 70:
        score += 58
    elif age < 80:
        score += 75
    else:
        score += 91

    if heart_rate < 50:
        score += 0
    elif heart_rate < 70:
        score += 3
    elif heart_rate < 90:
        score += 9
    elif heart_rate < 110:
        score += 15
    elif heart_rate < 150:
        score += 24
    else:
        score += 39

    if systolic_bp < 80:
        score += 58
    elif systolic_bp < 100:
        score += 47
    elif systolic_bp < 120:
        score += 37
    elif systolic_bp < 140:
        score += 26
    elif systolic_bp < 160:
        score += 17
    else:
        score += 0

    if creatinine < 0.4:
        score += 1
    elif creatinine < 0.8:
        score += 4
    elif creatinine < 1.2:
        score += 7
    elif creatinine < 1.6:
        score += 10
    elif creatinine < 2.0:
        score += 13
    elif creatinine < 3.0:
        score += 21
    else:
        score += 28

    score += [0, 20, 39, 59][killip_class - 1]

    if cardiac_arrest:
        score += 39
    if st_depression:
        score += 28
    if elevated_troponin:
        score += 14

    # Estratificación de riesgo hospitalario (GRACE original)
    if score < 109:
        risk_level = "bajo"
    elif score < 140:
        risk_level = "moderado"
    else:
        risk_level = "alto"

    return score, risk_level

def calcular(t):
    st.subheader("GRACE Risk Score - Mortalidad hospitalaria")

    age = st.number_input("Edad", min_value=18, max_value=100, value=65)
    heart_rate = st.number_input("Frecuencia cardíaca (lpm)", min_value=30, max_value=200, value=85)
    systolic_bp = st.number_input("Presión arterial sistólica (mmHg)", min_value=60, max_value=250, value=120)
    creatinine = st.number_input("Creatinina sérica (mg/dL)", min_value=0.1, max_value=10.0, value=1.1)
    killip_class = st.selectbox("Clase Killip", [1, 2, 3, 4])
    cardiac_arrest = st.checkbox("Paro cardíaco al ingreso", value=False)
    st_depression = st.checkbox("Descenso del ST en ECG", value=False)
    elevated_troponin = st.checkbox("Troponina elevada", value=True)

    if st.button("Calcular GRACE"):
        score, risk_level = calculate_grace_score(
            age, heart_rate, systolic_bp, creatinine, killip_class,
            cardiac_arrest, st_depression, elevated_troponin
        )
        result = (
            f"GRACE Score: {score}\n"
            f"Nivel de riesgo hospitalario: {risk_level.capitalize()}\n"
            f"Recomendación: Estratificación y tratamiento guiado por riesgo."
        )
        st.success(result)
        return result

    return None
