
import streamlit as st
from fpdf import FPDF
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="CardioApp", layout="centered")
st.title("CardioApp - Demo de Lectura de ECG")

st.sidebar.markdown("### Datos del profesional")
med_name = st.sidebar.text_input("Nombre del médico")
med_id = st.sidebar.text_input("Matrícula")

st.markdown("#### Subí una imagen de un ECG para generar un informe automático (demo):")
uploaded_file = st.file_uploader("Seleccioná una imagen", type=["png", "jpg", "jpeg", "pdf"])

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        st.warning("La lectura automática desde PDF estará disponible próximamente.")
    else:
        image = Image.open(uploaded_file)
        st.image(image, caption="ECG cargado", use_column_width=True)

        default_report = (
            "Ritmo sinusal
"
            "Frecuencia 72 lpm
"
            "PR 160 ms - QRS 100 ms - QTc 420 ms
"
            "Eje normal
"
            "No signos de isquemia aguda"
        )

        edited_report = st.text_area("Informe automático (editable)", default_report, height=150)

        if st.button("Exportar informe en PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Informe de ECG - CardioApp", ln=True)
            pdf.ln(10)
            for line in edited_report.split("\n"):
                pdf.cell(200, 10, txt=line, ln=True)
            pdf.ln(10)
            pdf.cell(200, 10, txt=f"Médico: {med_name} - Matrícula: {med_id}", ln=True)
            buffer = BytesIO()
            pdf.output(buffer)
            st.download_button("Descargar PDF", data=buffer.getvalue(), file_name="Informe_ECG.pdf")
