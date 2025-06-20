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

def mostrar_timi():
    st.subheader("Calculadora de TIMI Score")

    edad = st.number_input("Edad", min_value=0, max_value=120, value=50)
    factores_riesgo = st.checkbox("Tres o más factores de riesgo coronario (HTA, DM, dislipidemia, tabaquismo, antecedentes familiares)")
    uso_aspirina = st.checkbox("Uso de aspirina en los últimos 7 días")
    angina_severa = st.checkbox("Dos o más episodios de angina en 24 hs")
    elevacion_st = st.checkbox("Elevación del segmento ST ≥0.5 mm")
    troponina = st.checkbox("Marcadores cardíacos positivos")

    if st.button("Calcular TIMI"):
        score = calcular_timi(edad, factores_riesgo, uso_aspirina, angina_severa, elevacion_st, troponina)

        st.success(f"Puntaje TIMI: {score}")
        if score <= 2:
            st.info("Riesgo bajo de eventos isquémicos (3-8%)")
        elif score <= 4:
            st.warning("Riesgo intermedio de eventos isquémicos (13-20%)")
        else:
            st.error("Riesgo alto de eventos isquémicos (26-41%)")
