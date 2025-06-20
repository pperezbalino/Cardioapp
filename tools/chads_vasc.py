
import streamlit as st

def calculate_chads_vasc(age, gender, hypertension, diabetes, heart_failure, stroke, vascular_disease):
    score = 0
    if age >= 75:
        score += 2
    elif age >= 65:
        score += 1
    if gender == 'F':
        score += 1
    if hypertension:
        score += 1
    if diabetes:
        score += 1
    if heart_failure:
        score += 1
    if stroke:
        score += 2
    if vascular_disease:
        score += 1
    return score

def calcular(t):
    st.subheader("CHA₂DS₂-VASc Score (Fibrilación Auricular)")

    age = st.number_input("Edad", min_value=0, max_value=120, value=70)
    gender = st.selectbox("Sexo", ["M", "F"])
    hypertension = st.checkbox("Hipertensión")
    diabetes = st.checkbox("Diabetes")
    heart_failure = st.checkbox("Insuficiencia cardíaca")
    stroke = st.checkbox("ACV/AIT previo")
    vascular_disease = st.checkbox("Enfermedad vascular (IAM previo, enfermedad arterial periférica)")

    if st.button("Calcular CHA₂DS₂-VASc"):
        score = calculate_chads_vasc(age, gender, hypertension, diabetes, heart_failure, stroke, vascular_disease)

        if score == 0:
            riesgo = "muy bajo"
            recomendacion = "No se recomienda anticoagulación."
        elif score == 1 and gender == 'M':
            riesgo = "bajo"
            recomendacion = "Considerar anticoagulación individualizada."
        else:
            riesgo = "elevado"
            recomendacion = "Recomendada anticoagulación oral (NOACs o AVK)."

        resultado = (
            f"CHA₂DS₂-VASc Score: {score}\n"
            f"Nivel de riesgo tromboembólico: {riesgo.capitalize()}\n"
            f"Recomendación: {recomendacion}"
        )
        st.success(resultado)
        return resultado

    return None
