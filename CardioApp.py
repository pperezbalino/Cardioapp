
import streamlit as st
from fpdf import FPDF
import base64
from io import BytesIO
from PIL import Image
import datetime

# Idiomas soportados
langs = {
    "Español": {
        "app_title": "CardioApp",
        "select_tool": "Seleccione una herramienta",
        "tools": {
            "framingham": "Framingham",
            "euroscore": "EuroSCORE II",
            "ecg": "Lectura de ECG"
        },
        "sex": "Sexo",
        "male": "Masculino",
        "female": "Femenino",
        "age": "Edad",
        "cholesterol": "Colesterol Total (mg/dL)",
        "hdl": "HDL (mg/dL)",
        "systolic": "Presión Sistólica (mmHg)",
        "smoker": "¿Fuma?",
        "diabetic": "¿Diabético?",
        "calculate": "Calcular",
        "risk_result": "Riesgo a 10 años",
        "low": "Bajo",
        "moderate": "Moderado",
        "high": "Alto",
        "upload_ecg": "Subir ECG",
        "generate_pdf": "Exportar PDF",
        "edit": "Editar informe",
        "name": "Nombre del médico",
        "id": "Matrícula",
        "save_info": "Guardar para próximos informes"
    }
}

# Selección de idioma
lang = st.sidebar.selectbox("Language / Idioma", list(langs.keys()))
t = langs[lang]

# Título de la app
st.title(t["app_title"])
tool = st.selectbox(t["select_tool"], [t["tools"]["framingham"], t["tools"]["euroscore"], t["tools"]["ecg"]])

# Datos persistentes para médico
if "med_name" not in st.session_state:
    st.session_state["med_name"] = ""
if "med_id" not in st.session_state:
    st.session_state["med_id"] = ""

def export_pdf(report_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Heart_corazón_icon.svg/1024px-Heart_corazón_icon.svg.png", 10, 8, 20)
    pdf.ln(20)
    for line in report_text.split("
"):
        pdf.cell(200, 10, txt=line, ln=True)
    buffer = BytesIO()
    pdf.output(buffer)
    st.download_button(label=t["generate_pdf"], data=buffer.getvalue(), file_name="cardioapp_reporte.pdf")

if tool == t["tools"]["framingham"]:
    sex = st.selectbox(t["sex"], [t["male"], t["female"]])
    age = st.number_input(t["age"], min_value=20, max_value=79, value=50)
    chol = st.number_input(t["cholesterol"], value=200)
    hdl = st.number_input(t["hdl"], value=50)
    sys = st.number_input(t["systolic"], value=120)
    smoker = st.checkbox(t["smoker"])
    diabetic = st.checkbox(t["diabetic"])
    if st.button(t["calculate"]):
        points = 0
        points += (age - 20) // 5
        points += (chol - 160) // 40
        points -= (hdl - 35) // 10
        points += (sys - 120) // 20
        if smoker: points += 2
        if diabetic: points += 3
        risk = min(max(points * 2, 1), 30)
        risk_cat = t["low"] if risk < 10 else t["moderate"] if risk < 20 else t["high"]
        st.success(f"{t['risk_result']}: {risk}% ({risk_cat})")

elif tool == t["tools"]["euroscore"]:
    age = st.number_input(t["age"], min_value=18, max_value=120, value=65)
    creat = st.checkbox("Creatinina > 2 mg/dL")
    lvef = st.selectbox("Fracción de eyección", ["Normal", "Moderada", "Disfunción severa"])
    pulm = st.checkbox("Hipertensión pulmonar > 60 mmHg")
    urg = st.checkbox("Cirugía urgente")
    cabg = st.checkbox("Cirugía coronaria aislada")
    score = 0.01 * age
    if creat: score += 1.2
    if lvef == "Moderada": score += 1
    elif lvef == "Disfunción severa": score += 2
    if pulm: score += 1
    if urg: score += 2
    if cabg: score -= 0.5
    risk_cat = t["low"] if score < 2 else t["moderate"] if score < 5 else t["high"]
    st.success(f"{t['risk_result']}: {round(score, 2)}% ({risk_cat})")

elif tool == t["tools"]["ecg"]:
    st.info(t["upload_ecg"])
    uploaded_file = st.file_uploader("ECG", type=["png", "jpg", "jpeg", "pdf"])
    if uploaded_file:
        st.image(uploaded_file)
        # Simulación de lectura automatizada
        diagnosis = "Ritmo sinusal. Bloqueo de rama derecha incompleto. QT dentro de límites normales."
        if "edit_text" not in st.session_state:
            st.session_state["edit_text"] = diagnosis
        if st.checkbox(t["edit"]):
            st.session_state["edit_text"] = st.text_area("Informe", st.session_state["edit_text"])
        else:
            st.markdown(f"**{st.session_state['edit_text']}**")
        name = st.text_input(t["name"], value=st.session_state["med_name"])
        mid = st.text_input(t["id"], value=st.session_state["med_id"])
        if st.checkbox(t["save_info"]):
            st.session_state["med_name"] = name
            st.session_state["med_id"] = mid
        footer = f"

Informe generado automáticamente. Médico responsable: {name} (Mat: {mid})"
        export_pdf(st.session_state["edit_text"] + footer)
