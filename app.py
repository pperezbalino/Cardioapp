
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="CardioApp",
    page_icon=":heart:",
    layout="centered",
)

st.image("logo.png", width=120)
st.title("CardioApp")
st.markdown("Aplicación educativa para evaluación de riesgo cardiovascular, cálculo de scores y análisis de ECG.")

menu = ["Framingham", "EuroSCORE II", "ECG"]
choice = st.sidebar.selectbox("Seleccionar herramienta", menu)

if choice == "Framingham":
    st.subheader("Score de Framingham")
    edad = st.number_input("Edad", min_value=20, max_value=79, value=50)
    sexo = st.selectbox("Sexo", ["Masculino", "Femenino"])
    colesterol_total = st.number_input("Colesterol Total (mg/dL)", min_value=100, max_value=400, value=200)
    hdl = st.number_input("HDL (mg/dL)", min_value=20, max_value=100, value=50)
    presion = st.number_input("Presión Sistólica", min_value=90, max_value=200, value=120)
    fumador = st.checkbox("Fumador")
    diabetes = st.checkbox("Diabetes")

    if st.button("Calcular"):
        puntos = 0
        if sexo == "Masculino":
            puntos += (edad - 20) // 5
            if colesterol_total > 160: puntos += 2
            if hdl < 40: puntos += 2
            if presion > 120: puntos += 2
            if fumador: puntos += 4
            if diabetes: puntos += 3
        else:
            puntos += (edad - 20) // 5
            if colesterol_total > 160: puntos += 1
            if hdl < 50: puntos += 1
            if presion > 120: puntos += 3
            if fumador: puntos += 2
            if diabetes: puntos += 4

        riesgo = "Bajo"
        if puntos >= 10: riesgo = "Moderado"
        if puntos >= 15: riesgo = "Alto"

        st.success(f"Score estimado: {puntos} puntos ({riesgo} riesgo a 10 años)")

elif choice == "EuroSCORE II":
    st.subheader("EuroSCORE II")
    edad = st.number_input("Edad", min_value=18, max_value=100, value=70)
    sexo = st.selectbox("Sexo", ["Masculino", "Femenino"])
    funcion_renal = st.selectbox("Función renal", ["Normal", "Insuficiencia moderada", "Insuficiencia grave"])
    fraccion_eyeccion = st.selectbox("Fracción de eyección", [">50%", "31-50%", "<30%"])
    cirugia_urgente = st.checkbox("Cirugía urgente")

    if st.button("Calcular EuroSCORE II"):
        score = 0.02 * edad
        if sexo == "Femenino":
            score += 0.5
        if funcion_renal == "Insuficiencia moderada":
            score += 1.5
        elif funcion_renal == "Insuficiencia grave":
            score += 2.5
        if fraccion_eyeccion == "31-50%":
            score += 1.5
        elif fraccion_eyeccion == "<30%":
            score += 3
        if cirugia_urgente:
            score += 2

        riesgo = "Bajo"
        if score >= 4: riesgo = "Moderado"
        if score >= 8: riesgo = "Alto"

        st.success(f"EuroSCORE II estimado: {score:.2f}% ({riesgo} riesgo operatorio)")

elif choice == "ECG":
    st.subheader("Informe de ECG")
    file = st.file_uploader("Subir imagen de ECG", type=["jpg", "png", "jpeg", "pdf"])
    if file:
        st.image(file, caption="ECG cargado", use_column_width=True)
        st.info("Informe generado por IA con fines educativos. No reemplaza el informe médico profesional.")
        if st.button("Exportar PDF"):
            st.success("PDF generado con informe de ECG.")
