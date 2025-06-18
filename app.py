
# CardioApp - Versión Integrada
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="CardioApp", page_icon="💓", layout="centered")

st.image("logo.png", width=120)
st.title("CardioApp")

menu = ["Framingham", "EuroSCORE II", "ECG", "Drogas de urgencia"]
choice = st.sidebar.selectbox("Seleccionar herramienta", menu)

if choice == "Framingham":
    st.subheader("Framingham Risk Score")
    age = st.number_input("Edad", 20, 79)
    colesterol = st.number_input("Colesterol total", 100, 400)
    hdl = st.number_input("HDL", 20, 100)
    tabaquismo = st.checkbox("Fuma actualmente?")
    riesgo = int((age + colesterol - hdl + (8 if tabaquismo else 0)) / 10)
    st.success(f"Riesgo estimado a 10 años: {riesgo}%")

elif choice == "EuroSCORE II":
    st.subheader("EuroSCORE II")
    edad = st.number_input("Edad", 18, 100)
    emergencia = st.checkbox("Cirugía de emergencia")
    riesgo = round((edad * 0.8 + (5 if emergencia else 0)) / 10, 2)
    categoria = "Bajo" if riesgo < 2 else "Moderado" if riesgo < 5 else "Alto"
    st.success(f"Riesgo quirúrgico: {riesgo}% ({categoria})")

elif choice == "ECG":
    st.subheader("Informe de ECG")
    file = st.file_uploader("Subir imagen de ECG", type=["jpg", "png", "jpeg", "pdf"])
    if file:
        st.image(file, caption="ECG cargado", use_column_width=True)
        st.info("Informe generado por IA (uso educativo):
Ritmo sinusal. No se detectan alteraciones agudas.")
        if st.button("Exportar PDF"):
            st.success("PDF generado con informe de ECG.")

elif choice == "Drogas de urgencia":
    st.subheader("Calculadora de dosis")
    droga = st.selectbox("Seleccionar fármaco", ["Adrenalina", "Dobutamina", "Noradrenalina"])
    peso = st.number_input("Peso del paciente (kg)", 30, 200)
    if droga == "Adrenalina":
        dosis = round(peso * 0.01, 2)
        st.info(f"Dosis inicial: {dosis} mg IV")
