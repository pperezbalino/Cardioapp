
import streamlit as st

def ckd_epi(age, creatinine, sex, race):
    k = 0.7 if sex == "Femenino" else 0.9
    alpha = -0.329 if sex == "Femenino" else -0.411
    min_creat = min(creatinine / k, 1) ** alpha
    max_creat = max(creatinine / k, 1) ** -1.209
    gender_coeff = 1.018 if sex == "Femenino" else 1
    race_coeff = 1.159 if race == "Negro" else 1

    gfr = 141 * min_creat * max_creat * (0.993 ** age) * gender_coeff * race_coeff
    return gfr

def calcular(t):
    st.subheader("Filtrado Glomerular (CKD-EPI)")
    age = st.number_input("Edad", min_value=1, max_value=120, value=60)
    creatinine = st.number_input("Creatinina sérica (mg/dL)", min_value=0.1, max_value=15.0, value=1.0)
    sex = st.selectbox("Sexo", ["Masculino", "Femenino"])
    race = st.selectbox("Raza", ["No Negro", "Negro"])

    if st.button("Calcular GFR CKD-EPI"):
        race_code = "Black" if race == "Negro" else "Non-Black"
        gfr = ckd_epi(age, creatinine, sex, race_code)
        result = f"FG estimado: {gfr:.2f} mL/min/1.73m²"
        st.success(result)
        return result
    return None
