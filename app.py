
import streamlit as st
from PIL import Image
import base64
import io

# Funciones para los scores
def framingham_score():
    st.subheader("Framingham Risk Score")
    age = st.number_input("Edad", 20, 79, 50)
    colesterol_total = st.number_input("Colesterol total (mg/dL)", 100, 400, 200)
    hdl = st.number_input("HDL (mg/dL)", 20, 100, 50)
    presion = st.number_input("Presión sistólica (mmHg)", 80, 200, 120)
    fuma = st.checkbox("Fumador")
    diabetes = st.checkbox("Diabetes")

    puntos = 0
    if fuma:
        puntos += 4
    if diabetes:
        puntos += 3
    if presion > 130:
        puntos += 2
    if colesterol_total > 240:
        puntos += 2
    if hdl < 40:
        puntos += 2
    if age > 55:
        puntos += 3

    st.write(f"Puntaje estimado: {puntos}")
    if puntos < 5:
        st.success("Riesgo bajo")
    elif puntos < 10:
        st.warning("Riesgo moderado")
    else:
        st.error("Riesgo alto")

def euroscore_ii():
    st.subheader("EuroSCORE II")
    edad = st.number_input("Edad", 18, 100, 65)
    creatinina = st.number_input("Creatinina sérica (mg/dL)", 0.3, 10.0, 1.0)
    fraccion_eyeccion = st.selectbox("Fracción de eyección", ["Normal", "Moderada", "Reducida"])
    operacion_urgente = st.checkbox("Cirugía urgente")

    riesgo = 1.5
    if edad > 70:
        riesgo += 1.0
    if creatinina > 2.0:
        riesgo += 1.0
    if fraccion_eyeccion == "Reducida":
        riesgo += 2.0
    if operacion_urgente:
        riesgo += 2.0

    st.write(f"EuroSCORE II estimado: {riesgo:.1f}%")
    if riesgo < 2:
        st.success("Riesgo bajo")
    elif riesgo < 5:
        st.warning("Riesgo intermedio")
    else:
        st.error("Riesgo alto")

# Función para análisis de ECG (demo con IA asistente)
def ecg_analysis_demo():
    st.subheader("Lectura de ECG con IA (Demo)")
    uploaded_file = st.file_uploader("Subir imagen, PDF o foto del ECG", type=["jpg", "jpeg", "png", "pdf"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="ECG cargado", use_column_width=True)
        if st.button("Generar informe"):
            st.info("Procesando...")
            st.markdown("**Informe generado automáticamente (versión demo, requiere validación médica):**")
            st.markdown("*Ritmo sinusal, FC 72 lpm, PR 160 ms, QRS 92 ms, QTc 420 ms.*")
            st.markdown("*Sin alteraciones de la repolarización evidentes. No hay signos de isquemia ni arritmia actual.*")

# Interfaz principal
def main():
    st.set_page_config(page_title="CardioApp", layout="centered")
    st.title("🫀 CardioApp")
    st.markdown("Aplicación para el cálculo de scores cardiovasculares y análisis de ECG.

**Versión de prueba con IA asistente.**")

    menu = ["Framingham", "EuroSCORE II", "ECG IA (demo)"]
    choice = st.sidebar.radio("Seleccionar herramienta", menu)

    if choice == "Framingham":
        framingham_score()
    elif choice == "EuroSCORE II":
        euroscore_ii()
    elif choice == "ECG IA (demo)":
        ecg_analysis_demo()

if __name__ == "__main__":
    main()
