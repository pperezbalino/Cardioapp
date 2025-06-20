
import streamlit as st

def calculate_framingham_score(age, gender, total_chol, hdl, systolic_bp, smoker, diabetic, on_treatment):
    points = 0
    if gender == 'male':
        if age < 35:
            points += -9
        elif age < 40:
            points += -4
        elif age < 45:
            points += 0
        elif age < 50:
            points += 3
        elif age < 55:
            points += 6
        elif age < 60:
            points += 8
        elif age < 65:
            points += 10
        elif age < 70:
            points += 11
        else:
            points += 12

        if smoker:
            if age < 40:
                points += 8
            elif age < 50:
                points += 5
            elif age < 60:
                points += 3
            elif age < 70:
                points += 1
            else:
                points += 1

        if total_chol < 160:
            points += 0
        elif total_chol < 200:
            points += 1
        elif total_chol < 240:
            points += 2
        elif total_chol < 280:
            points += 3
        else:
            points += 4

        if hdl >= 60:
            points += -1
        elif hdl < 40:
            points += 2
        elif hdl < 50:
            points += 1

        if on_treatment:
            if systolic_bp < 120:
                points += 0
            elif systolic_bp < 130:
                points += 1
            elif systolic_bp < 140:
                points += 2
            elif systolic_bp < 160:
                points += 2
            else:
                points += 3
        else:
            if systolic_bp < 120:
                points += 0
            elif systolic_bp < 130:
                points += 0
            elif systolic_bp < 140:
                points += 1
            elif systolic_bp < 160:
                points += 1
            else:
                points += 2
    else:  # female
        if age < 35:
            points += -7
        elif age < 40:
            points += -3
        elif age < 45:
            points += 0
        elif age < 50:
            points += 3
        elif age < 55:
            points += 6
        elif age < 60:
            points += 8
        elif age < 65:
            points += 10
        elif age < 70:
            points += 12
        else:
            points += 14

        if smoker:
            if age < 40:
                points += 9
            elif age < 50:
                points += 7
            elif age < 60:
                points += 4
            elif age < 70:
                points += 2
            else:
                points += 1

        if total_chol < 160:
            points += 0
        elif total_chol < 200:
            points += 1
        elif total_chol < 240:
            points += 3
        elif total_chol < 280:
            points += 4
        else:
            points += 5

        if hdl >= 60:
            points += -1
        elif hdl < 40:
            points += 2
        elif hdl < 50:
            points += 1

        if on_treatment:
            if systolic_bp < 120:
                points += 0
            elif systolic_bp < 130:
                points += 3
            elif systolic_bp < 140:
                points += 4
            elif systolic_bp < 160:
                points += 5
            else:
                points += 6
        else:
            if systolic_bp < 120:
                points += 0
            elif systolic_bp < 130:
                points += 1
            elif systolic_bp < 140:
                points += 2
            elif systolic_bp < 160:
                points += 3
            else:
                points += 4

    if gender == 'male':
        thresholds = [1, 1, 1, 1, 1, 1, 2, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 25, 30]
    else:
        thresholds = [1, 1, 1, 1, 1, 2, 2, 3, 4, 5, 6, 8, 11, 14, 17, 22, 27, 30]

    risk = thresholds[min(points, len(thresholds) - 1)]

    if risk < 10:
        risk_level = "bajo"
        recommendation = "Promover hábitos saludables: dieta, ejercicio, abandono del tabaco. Reevaluar cada 4-6 años."
    elif risk < 20:
        risk_level = "moderado"
        recommendation = "Considerar tratamiento farmacológico si hay otros factores. Educación y seguimiento."
    else:
        risk_level = "alto"
        recommendation = "Indicar prevención secundaria. Control intensivo y seguimiento periódico."

    return risk, risk_level, recommendation

def calcular(t):
    st.subheader("Framingham Risk Score")
    age = st.number_input("Edad", min_value=20, max_value=79, value=55)
    gender = st.selectbox("Sexo", ["male", "female"])
    total_chol = st.number_input("Colesterol total (mg/dL)", min_value=100, max_value=400, value=220)
    hdl = st.number_input("HDL (mg/dL)", min_value=20, max_value=100, value=50)
    systolic_bp = st.number_input("Presión sistólica (mmHg)", min_value=80, max_value=250, value=130)
    smoker = st.checkbox("Fumador", value=False)
    diabetic = st.checkbox("Diabético", value=False)
    on_treatment = st.checkbox("En tratamiento antihipertensivo", value=False)

    if st.button("Calcular riesgo"):
        risk, risk_level, recommendation = calculate_framingham_score(
            age, gender, total_chol, hdl, systolic_bp, smoker, diabetic, on_treatment
        )
        result = f"Riesgo a 10 años: {risk}%\nNivel de riesgo: {risk_level}\nRecomendación: {recommendation}"
        st.success(result)
        return result
    return None
