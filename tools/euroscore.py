
import streamlit as st
import math

def calcular_euroscore(
    edad, sexo, enfermedad_pulmonar, movilidad, endocarditis, estado_critico,
    disfuncion_ventricular, reciente_mi, hipertension_pulmonar, cirugia_urgente,
    reoperacion, cirugia_aorta, peso_procedimiento
):
    logit = (
        -4.789594
        + 0.0285181 * edad
        + 0.2196434 * sexo
        + 0.5627062 * enfermedad_pulmonar
        + 0.7771778 * movilidad
        + 0.0712351 * endocarditis
        + 0.8557583 * estado_critico
        - 0.2919434 * disfuncion_ventricular
        + 0.3150655 * reciente_mi
        + 0.3013305 * hipertension_pulmonar
        + 1.1936869 * cirugia_urgente
        + 0.4061921 * reoperacion
        + 0.1811609 * cirugia_aorta
        + 0.0121281 * peso_procedimiento
    )
    odds = math.exp(logit)
    riesgo = odds / (1 + odds) * 100
    return round(riesgo, 1)

def calcular(t):
    st.subheader("EuroSCORE II")

    edad = st.number_input("Edad", min_value=0, max_value=120, value=65)
    sexo = st.selectbox("Sexo", ["M", "F"])
    enfermedad_pulmonar = st.checkbox("Enfermedad pulmonar crónica", value=False)
    movilidad = st.checkbox("Limitación movilidad (NYHA III-IV)", value=False)
    endocarditis = st.checkbox("Endocarditis activa", value=False)
    estado_critico = st.checkbox("Estado crítico preoperatorio", value=False)
    disfuncion_ventricular = st.checkbox("Disfunción ventricular (LVEF < 30%)", value=False)
    reciente_mi = st.checkbox("Infarto de miocardio reciente (90 días)", value=False)
    hipertension_pulmonar = st.checkbox("Hipertensión pulmonar (> 60 mmHg)", value=False)
    cirugia_urgente = st.checkbox("Cirugía urgente", value=False)
    reoperacion = st.checkbox("Reoperación torácica", value=False)
    cirugia_aorta = st.checkbox("Cirugía de aorta", value=False)
    peso_procedimiento = st.selectbox("Peso del procedimiento", [0, 1, 2, 3], index=0)

    if st.button("Calcular EuroSCORE II"):
        sexo_val = 1 if sexo == "F" else 0
        riesgo = calcular_euroscore(
            edad, sexo_val, int(enfermedad_pulmonar), int(movilidad), int(endocarditis),
            int(estado_critico), int(disfuncion_ventricular), int(reciente_mi),
            int(hipertension_pulmonar), int(cirugia_urgente), int(reoperacion),
            int(cirugia_aorta), peso_procedimiento
        )
        if riesgo < 4:
            categoria = "Bajo"
        elif riesgo < 8:
            categoria = "Intermedio"
        else:
            categoria = "Alto"
        result = f"EuroSCORE II: {riesgo}%\nCategoría: {categoria}"
        st.success(result)
        return result
    return None
