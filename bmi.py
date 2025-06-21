import streamlit as st

def calcular_bmi(peso_kg, altura_cm):
    altura_m = altura_cm / 100
    bmi = peso_kg / (altura_m ** 2)
    categoria = ""
    if bmi < 18.5:
        categoria = "bajo"
    elif 18.5 <= bmi < 25:
        categoria = "normal"
    elif 25 <= bmi < 30:
        categoria = "sobrepeso"
    else:
        categoria = "obesidad"
    return round(bmi, 1), categoria

def mostrar_bmi(t):
    st.subheader(t["bmi"])
    peso = st.number_input(t["weight"], min_value=30.0, max_value=300.0, step=0.1)
    altura = st.number_input(t["height"], min_value=100.0, max_value=250.0, step=0.1)

    if st.button(t["calculate"]):
        bmi, categoria = calcular_bmi(peso, altura)
        categoria_texto = {
            "bajo": t["bmi_underweight"],
            "normal": t["bmi_normal"],
            "sobrepeso": t["bmi_overweight"],
            "obesidad": t["bmi_obese"]
        }[categoria]
        st.success(f"{t['result']}: {bmi} — {categoria_texto}")
