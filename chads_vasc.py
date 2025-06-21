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

def chads_vasc_app(t):
    st.header(t["chads"])
    age = st.number_input(t["age"], min_value=0, max_value=120, value=65)
    gender = st.selectbox(t["sex"], [t["male"], t["female"]])
    hypertension = st.checkbox(t["hypertension"])
    diabetes = st.checkbox(t["diabetes"])
    heart_failure = st.checkbox(t["heart_failure"])
    stroke = st.checkbox(t["stroke"])
    vascular_disease = st.checkbox(t["vascular_disease"])

    if st.button(t["calculate"]):
        g = 'F' if gender == t["female"] else 'M'
        score = calculate_chads_vasc(age, g, hypertension, diabetes, heart_failure, stroke, vascular_disease)
        st.success(f"{t['result']}: {score}")
