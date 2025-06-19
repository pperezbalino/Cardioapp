
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

def chads_vasc_app():
    st.header("CHA₂DS₂-VASc Score")
    age = st.number_input("Edad", min_value=0, max_value=120, value=65)
    gender = st.selectbox("Sexo", ["M", "F"])
    hypertension = st.checkbox("Hipertensión")
    diabetes = st.checkbox("Diabetes")
    heart_failure = st.checkbox("Insuficiencia cardíaca")
    stroke = st.checkbox("ACV/AIT previo")
    vascular_disease = st.checkbox("Enfermedad vascular (IAM previo, enfermedad arterial periférica)")

    if st.button("Calcular"):
        score = calculate_chads_vasc(age, gender, hypertension, diabetes, heart_failure, stroke, vascular_disease)
        st.success(f"Puntaje CHA₂DS₂-VASc: {score}")
        if score == 0:
            st.info("Riesgo bajo: no se recomienda anticoagulación.")
        elif score == 1 and gender == 'M':
            st.info("Riesgo intermedio: considerar anticoagulación.")
        else:
            st.warning("Riesgo alto: se recomienda anticoagulación.")

