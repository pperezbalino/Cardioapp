
import streamlit as st

def calcular_bmi(peso_kg, altura_cm):
    altura_m = altura_cm / 100
    bmi = peso_kg / (altura_m ** 2)
    if bmi < 18.5:
        categoria = "Bajo peso"
    elif 18.5 <= bmi < 25:
        categoria = "Normal"
    elif 25 <= bmi < 30:
        categoria = "Sobrepeso"
    else:
        categoria = "Obesidad"
    return round(bmi, 1), categoria

def calcular(t):
    st.subheader("Índice de Masa Corporal (BMI)")
    peso = st.number_input("Peso (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.1)
    altura = st.number_input("Altura (cm)", min_value=100.0, max_value=220.0, value=170.0, step=0.1)
    if st.button("Calcular BMI"):
        bmi_val, categoria = calcular_bmi(peso, altura)
        result = f"BMI: {bmi_val} kg/m²\nCategoría: {categoria}"
        st.success(result)
        return result
    return None
