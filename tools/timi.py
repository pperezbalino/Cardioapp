
import streamlit as st

def calcular_timi(edad, factores_riesgo, uso_aspirina, angina_severa, elevacion_st, troponina):
    score = 0
    if edad >= 65:
        score += 1
    if factores_riesgo:
        score += 1
    if uso_aspirina:
        score += 1
    if angina_severa:
        score += 1
    if elevacion_st:
        score += 1
    if troponina:
        score += 1
    return score

def calcular(t):
    st.subheader("TIMI Risk Score (Síndrome Coronario Agudo sin elevación del ST)")

    edad = st.number_input("Edad", min_value=0, max_value=120, value=60)
    factores_riesgo = st.checkbox("≥ 3 factores de riesgo coronario (HTA, DM, dislipemia, tabaquismo, antecedentes familiares)")
    uso_aspirina = st.checkbox("Uso de aspirina en los últimos 7 días")
    angina_severa = st.checkbox("≥ 2 episodios de angina en 24 hs")
    elevacion_st = st.checkbox("Desviación del ST ≥ 0.5 mm")
    troponina = st.checkbox("Marcadores cardíacos positivos (troponina elevada)")

    if st.button("Calcular TIMI"):
        score = calcular_timi(edad, factores_riesgo, uso_aspirina, angina_severa, elevacion_st, troponina)

        if score <= 2:
            riesgo = "bajo"
            recomendacion = "Manejo conservador, considerar alta precoz si se normalizan marcadores y ECG."
        elif score <= 4:
            riesgo = "intermedio"
            recomendacion = "Monitoreo intensivo, considerar estratificación invasiva temprana."
        else:
            riesgo = "alto"
            recomendacion = "Indicar estrategia invasiva precoz, anticoagulación y doble antiagregación."

        resultado = (
            f"TIMI Score: {score}\n"
            f"Nivel de riesgo: {riesgo.capitalize()}\n"
            f"Recomendación: {recomendacion}"
        )
        st.success(resultado)
        return resultado

    return None
