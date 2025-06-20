
import streamlit as st
import math

def calcular_euroscore(
    edad, sexo, enfermedad_pulmonar, movilidad, endocarditis, estado_critico,
    disfuncion_ventricular, reciente_mi, hipertension_pulmonar, cirugia_urgente,
    cirugia_posterior, cirugia_aorta, peso_procedimiento
):
    logit = (
        -4.789594
        + 0.0285181 * edad
        + 0.2196434 * sexo
        + 0.5627062 * enfermedad_pulmonar
        + 0.7771778 * movilidad
        + 0.0712351 * endocarditis
        + 0.8557583 * estado_critico
        + 0.7681095 * disfuncion_ventricular
        + 0.1528943 * reciente_mi
        + 0.3103862 * hipertension_pulmonar
        + 0.2958358 * cirugia_urgente
        + 0.7756916 * cirugia_posterior
        + 0.9711371 * cirugia_aorta
        + 0.1177185 * peso_procedimiento
    )
    riesgo = (math.exp(logit) / (1 + math.exp(logit))) * 100
    return round(riesgo, 2)

def mostrar_euroscore():
    st.subheader("EuroSCORE II")

    edad = st.slider("Edad", 18, 100, 65)
    sexo = st.radio("Sexo", ["Masculino", "Femenino"])
    enfermedad_pulmonar = st.checkbox("Enfermedad pulmonar")
    movilidad = st.checkbox("Movilidad reducida")
    endocarditis = st.checkbox("Endocarditis activa")
    estado_critico = st.checkbox("Estado crítico preoperatorio")
    disfuncion_ventricular = st.checkbox("Disfunción ventricular izquierda moderada o severa")
    reciente_mi = st.checkbox("Infarto de miocardio reciente")
    hipertension_pulmonar = st.checkbox("Hipertensión pulmonar (>60 mmHg)")
    cirugia_urgente = st.checkbox("Cirugía urgente/emergencia")
    cirugia_posterior = st.checkbox("Cirugía cardíaca previa")
    cirugia_aorta = st.checkbox("Cirugía de aorta torácica")
    peso_procedimiento = st.slider("Complejidad del procedimiento (peso)", 0, 5, 1)

    if st.button("Calcular EuroSCORE II"):
        sexo_valor = 1 if sexo == "Femenino" else 0
        riesgo = calcular_euroscore(
            edad, sexo_valor, enfermedad_pulmonar, movilidad, endocarditis,
            estado_critico, disfuncion_ventricular, reciente_mi, hipertension_pulmonar,
            cirugia_urgente, cirugia_posterior, cirugia_aorta, peso_procedimiento
        )
        if riesgo < 4:
            riesgo_cat = "Bajo"
        elif riesgo < 8:
            riesgo_cat = "Intermedio"
        else:
            riesgo_cat = "Alto"
        st.success(f"Riesgo estimado: {riesgo}% ({riesgo_cat})")
