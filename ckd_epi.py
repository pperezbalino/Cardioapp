
import streamlit as st

def ckd_epi(age, creatinine, sex, race):
    k = 0.7 if sex == "Female" else 0.9
    alpha = -0.329 if sex == "Female" else -0.411
    min_creat = min(creatinine / k, 1) ** alpha
    max_creat = max(creatinine / k, 1) ** -1.209
    gender_coeff = 1.018 if sex == "Female" else 1
    race_coeff = 1.159 if race == "Black" else 1

    gfr = 141 * min_creat * max_creat * (0.993 ** age) * gender_coeff * race_coeff
    return gfr

def show():
    st.title("CKD-EPI GFR Calculator")
    st.write("Estimate Glomerular Filtration Rate using CKD-EPI formula")

    age = st.number_input("Age", min_value=1, max_value=120, value=60)
    creatinine = st.number_input("Serum Creatinine (mg/dL)", min_value=0.1, max_value=15.0, value=1.0)
    sex = st.radio("Sex", ["Male", "Female"])
    race = st.radio("Race", ["Non-Black", "Black"])

    if st.button("Calculate GFR"):
        race_input = "Black" if race == "Black" else "Non-Black"
        gfr = ckd_epi(age, creatinine, sex, race_input)
        st.success(f"Estimated GFR: {gfr:.2f} mL/min/1.73m²")

