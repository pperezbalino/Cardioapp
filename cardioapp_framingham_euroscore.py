
import streamlit as st
import math

st.set_page_config(page_title="CardioApp: Framingham + EuroSCORE II", layout="centered")
st.title("🫀 CardioApp: Herramientas de Riesgo Cardiovascular")

# Selección de herramienta
tool = st.selectbox("Seleccionar herramienta", ["Framingham", "EuroSCORE II"])

# ============================
# FRAMINGHAM
# ============================
if tool == "Framingham":
    st.header("🔹 Calculadora de Riesgo Framingham (10 años)")
    edad = st.number_input("Edad (años)", min_value=20, max_value=79, value=50)
    sexo = st.selectbox("Sexo", ["Masculino", "Femenino"])
    colesterol_total = st.number_input("Colesterol total (mg/dL)", min_value=100, max_value=400, value=200)
    hdl = st.number_input("HDL (mg/dL)", min_value=20, max_value=100, value=50)
    presion_sistolica = st.number_input("Presión sistólica (mmHg)", min_value=90, max_value=200, value=120)
    tratamiento_hta = st.selectbox("¿Está en tratamiento para HTA?", ["No", "Sí"])
    fumador = st.selectbox("¿Fuma actualmente?", ["No", "Sí"])
    diabetico = st.selectbox("¿Es diabético?", ["No", "Sí"])

    def calcular_framingham(edad, sexo, colesterol_total, hdl, presion_sistolica, tratamiento_hta, fumador, diabetico):
        puntos = 0
        if sexo == "Masculino":
            if 20 <= edad <= 34: puntos += -9
            elif 35 <= edad <= 39: puntos += -4
            elif 40 <= edad <= 44: puntos += 0
            elif 45 <= edad <= 49: puntos += 3
            elif 50 <= edad <= 54: puntos += 6
            elif 55 <= edad <= 59: puntos += 8
            elif 60 <= edad <= 64: puntos += 10
            elif 65 <= edad <= 69: puntos += 11
            elif 70 <= edad <= 74: puntos += 12
            elif 75 <= edad <= 79: puntos += 13
        else:
            if 20 <= edad <= 34: puntos += -7
            elif 35 <= edad <= 39: puntos += -3
            elif 40 <= edad <= 44: puntos += 0
            elif 45 <= edad <= 49: puntos += 3
            elif 50 <= edad <= 54: puntos += 6
            elif 55 <= edad <= 59: puntos += 8
            elif 60 <= edad <= 64: puntos += 10
            elif 65 <= edad <= 69: puntos += 12
            elif 70 <= edad <= 74: puntos += 14
            elif 75 <= edad <= 79: puntos += 16

        if sexo == "Masculino":
            if colesterol_total < 160: puntos += 0
            elif colesterol_total < 200: puntos += 1
            elif colesterol_total < 240: puntos += 2
            elif colesterol_total < 280: puntos += 3
            else: puntos += 4
        else:
            if colesterol_total < 160: puntos += 0
            elif colesterol_total < 200: puntos += 1
            elif colesterol_total < 240: puntos += 3
            elif colesterol_total < 280: puntos += 4
            else: puntos += 5

        if hdl >= 60: puntos += -1
        elif hdl >= 50: puntos += 0
        elif hdl >= 40: puntos += 1
        else: puntos += 2

        if tratamiento_hta == "Sí":
            if presion_sistolica < 120: puntos += 0
            elif presion_sistolica < 130: puntos += 1
            elif presion_sistolica < 140: puntos += 2
            elif presion_sistolica < 160: puntos += 2
            else: puntos += 3
        else:
            if presion_sistolica < 120: puntos += 0
            elif presion_sistolica < 130: puntos += 0
            elif presion_sistolica < 140: puntos += 1
            elif presion_sistolica < 160: puntos += 1
            else: puntos += 2

        if fumador == "Sí": puntos += 2
        if diabetico == "Sí": puntos += 2 if sexo == "Masculino" else 4

        riesgo = "No calculado"
        if sexo == "Masculino":
            if puntos < 0: riesgo = "<1%"
            elif puntos <= 4: riesgo = "1%"
            elif puntos <= 6: riesgo = "2%"
            elif puntos == 7: riesgo = "3%"
            elif puntos == 8: riesgo = "4%"
            elif puntos == 9: riesgo = "5%"
            elif puntos == 10: riesgo = "6%"
            elif puntos == 11: riesgo = "8%"
            elif puntos == 12: riesgo = "10%"
            elif puntos == 13: riesgo = "12%"
            elif puntos == 14: riesgo = "16%"
            elif puntos == 15: riesgo = "20%"
            elif puntos >= 16: riesgo = ">25%"
        else:
            if puntos < 9: riesgo = "<1%"
            elif puntos == 9: riesgo = "1%"
            elif puntos == 10: riesgo = "1%"
            elif puntos == 11: riesgo = "1%"
            elif puntos == 12: riesgo = "1%"
            elif puntos == 13: riesgo = "2%"
            elif puntos == 14: riesgo = "2%"
            elif puntos == 15: riesgo = "3%"
            elif puntos == 16: riesgo = "4%"
            elif puntos == 17: riesgo = "5%"
            elif puntos == 18: riesgo = "6%"
            elif puntos == 19: riesgo = "8%"
            elif puntos == 20: riesgo = "11%"
            elif puntos == 21: riesgo = "14%"
            elif puntos >= 22: riesgo = ">20%"

        return puntos, riesgo

    if st.button("Calcular riesgo", key="fram"):
        puntos, riesgo = calcular_framingham(edad, sexo, colesterol_total, hdl, presion_sistolica, tratamiento_hta, fumador, diabetico)
        st.success(f"Puntaje Framingham: {puntos}")
        st.markdown(f"**Riesgo cardiovascular a 10 años: {riesgo}**")

# ============================
# EUROSCORE II
# ============================
elif tool == "EuroSCORE II":
    st.header("🔹 Calculadora EuroSCORE II")

    edad = st.number_input("Edad", min_value=18, max_value=120, value=70)
    sexo = st.selectbox("Sexo", ["Masculino", "Femenino"])
    creatinina = st.number_input("Creatinina sérica (mg/dL)", min_value=0.1, max_value=15.0, value=1.0)
    fevi = st.selectbox("Fracción de eyección", ["≥50%", "31–49%", "≤30%"])
    extra_card = st.selectbox("Enfermedad extracardíaca severa", ["No", "Sí"])
    endocarditis = st.selectbox("Endocarditis activa", ["No", "Sí"])
    urgencia = st.selectbox("Urgencia de la cirugía", ["Electiva", "Urgente", "Emergente"])
    tipo_cirugia = st.selectbox("Tipo de cirugía", ["CABG", "Valvular", "CABG + Valvular", "Otros"])
    pulmonar = st.selectbox("Enfermedad pulmonar", ["No", "Moderada", "Severa"])
    movilidad = st.selectbox("Estado funcional (movilidad)", ["Independiente", "Dependiente"])
    reop = st.selectbox("Cirugía cardíaca previa", ["No", "Sí"])

    # Modelo simplificado de cálculo aproximado
    riesgo = 2.4  # valor base ficticio para esta demo
    if edad > 75: riesgo += 1.5
    if creatinina > 2.0: riesgo += 2.0
    if fevi == "31–49%": riesgo += 1.0
    elif fevi == "≤30%": riesgo += 2.5
    if extra_card == "Sí": riesgo += 1.5
    if endocarditis == "Sí": riesgo += 1.8
    if urgencia == "Urgente": riesgo += 1.2
    elif urgencia == "Emergente": riesgo += 2.5
    if tipo_cirugia == "CABG + Valvular": riesgo += 1.3
    if tipo_cirugia == "Otros": riesgo += 2.0
    if pulmonar == "Moderada": riesgo += 0.7
    elif pulmonar == "Severa": riesgo += 1.5
    if movilidad == "Dependiente": riesgo += 1.0
    if reop == "Sí": riesgo += 1.5
    if sexo == "Femenino": riesgo += 0.5

    # Clasificación
    if riesgo < 2:
        clase = "Bajo riesgo"
    elif riesgo <= 5:
        clase = "Riesgo intermedio"
    else:
        clase = "Alto riesgo"

    if st.button("Calcular EuroSCORE II"):
        st.success(f"Riesgo estimado de mortalidad: {riesgo:.1f}% ({clase})")
