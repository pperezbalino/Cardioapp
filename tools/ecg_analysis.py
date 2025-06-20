
import streamlit as st
import tempfile
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from translations import translations
import datetime

def analyze_ecg_report(image_path, patient_initials, license_number, selected_language):
    t = translations[selected_language]
    diagnosis = t.get("possible_ecg_diagnosis", "Sin hallazgos específicos")

    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")

    filename = f"ECG_Report_{patient_initials}_{date_str}.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, t.get("ecg_report_title", "Informe de ECG"))

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"{t.get('patient_initials', 'Iniciales')}: {patient_initials}")
    c.drawString(50, height - 100, f"{t.get('license_number', 'Licencia')}: {license_number}")
    c.drawString(50, height - 120, f"{t.get('date', 'Fecha')}: {date_str} - {t.get('time', 'Hora')}: {time_str}")

    c.drawString(50, height - 160, t.get("ecg_findings", "Hallazgos:"))
    c.drawString(70, height - 180, diagnosis)

    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, 50, t.get("disclaimer_footer", ""))

    c.showPage()
    c.save()
    return filename

def calcular(t):
    st.subheader("Análisis de ECG (IA)")

    uploaded_file = st.file_uploader("Sube imagen o PDF del ECG", type=["png","jpg","jpeg","pdf"])
    patient_initials = st.text_input("Iniciales del paciente", value="")
    license_number = st.text_input("Número de licencia médica", value="")
    lang = st.session_state.language

    if st.button("Analizar ECG"):
        if uploaded_file and patient_initials and license_number:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            report_file = analyze_ecg_report(tmp_path, patient_initials, license_number, lang)
            with open(report_file, "rb") as f:
                data = f.read()
            st.success("Informe de ECG generado")
            st.download_button("Descargar informe ECG", data=data, file_name=report_file, mime="application/pdf")
            return f"Informe generado: {report_file}"
        else:
            st.error("Debe completar todos los campos y subir el archivo.")
    return None
