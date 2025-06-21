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

def show(t):
    st.subheader(t["ckd"])
    st.write(t["ckd_description"])

    age = st.number_input(t["age"], min_value=1, max_value=120, value=60)
    creatinine = st.number_input(t["serum_creatinine"], min_value=0.1, max_value=15.0, value=1.0)
    sex = st.radio(t["sex"], [t["male"], t["female"]])
    race = st.radio(t["race"], [t["race_non_black"], t["race_black"]])

    if st.button(t["calculate"]):
        race_input = "Black" if race == t["race_black"] else "Non-Black"
        gfr = ckd_epi(age, creatinine, sex, race_input)
        st.success(f"{t['result']}: {round(gfr)} mL/min/1.73 m²")
