import streamlit as st

def calculate_grace_score(age, heart_rate, systolic_bp, creatinine, killip_class,
                          cardiac_arrest, st_depression, elevated_troponin):
    score = 0
    if age < 30:
        score += 0
    elif age < 40:
        score += 8
    elif age < 50:
        score += 25
    elif age < 60:
        score += 41
    elif age < 70:
        score += 58
    elif age < 80:
        score += 75
    else:
        score += 91

    if heart_rate > 150:
        score += 24
    elif heart_rate > 100:
        score += 14
    elif heart_rate > 80:
        score += 7

    if systolic_bp < 80:
        score += 58
    elif systolic_bp < 100:
        score += 46
    elif systolic_bp < 120:
        score += 29
    elif systolic_bp < 140:
        score += 10

    if creatinine > 2:
        score += 39
    elif creatinine > 1.5:
        score += 21
    elif creatinine > 1.2:
        score += 10

    score += {1: 0, 2: 20, 3: 39, 4: 59}.get(killip_class, 0)

    if cardiac_arrest:
        score += 39
    if st_depression:
        score += 28
    if elevated_troponin:
        score += 14

    return score

def mostrar_grace(t):
    st.subheader(t["grace"])

    age = st.number_input(t["age"], 0, 120, 65)
    hr = st.number_input(t["heart_rate"], 30, 200, 80)
    sbp = st.number_input(t["sbp"], 60, 250, 120)
    cr = st.number_input(t["creatinine"], 0.1, 15.0, 1.0)
    killip = st.selectbox(t["killip_class"], [1, 2, 3, 4])
    arrest = st.checkbox(t["cardiac_arrest"])
    st_dep = st.checkbox(t["st_depression"])
    trop = st.checkbox(t["positive_troponin"])

    if st.button(t["calculate"]):
        score = calculate_grace_score(age, hr, sbp, cr, killip, arrest, st_dep, trop)
        st.success(f"{t['result']}: {score}")
