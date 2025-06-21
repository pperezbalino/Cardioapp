import streamlit as st
import datetime
from translations import translations
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
import io
import os

def analyze_and_display_ecg(t, selected_language):
    st.subheader(t["ecg"])

    uploaded_file = st.file_uploader(t["upload_ecg_image"], type=["png", "jpg", "jpeg"])
    patient_initials = st.text_input(t["patient_initials"])
    license_number = st.text_input(t["license_number"])

    if uploaded_file and patient_initials and license_number:
        # Mostrar la imagen del ECG en pantalla
        st.image(uploaded_file, caption=t["ecg_image_preview"], use_column_width=True)

        # Simulación de análisis de ECG
        diagnosis = t["possible_ecg_diagnosis"]

        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        # Mostrar informe en pantalla
        st.markdown(f"### {t['ecg_report_title']}")
        st.markdown(f"**{t['patient_initials']}:** {patient_initials}")
        st.markdown(f"**{t['license_number']}:** {license_number}")
        st.markdown(f"**{t['date']}:** {date_str} &nbsp;&nbsp; **{t['time']}:** {time_str}")
        st.markdown(f"**{t['ecg_findings']}** {diagnosis}")
        st.markdown(f"*{t['disclaimer_footer']}*")

        if st.button(t["generate_pdf"]):
            # Crear el archivo PDF incluyendo la imagen
            filename = f"{t['ecg_report_filename_prefix']}_{date_str}_{time_str.replace(':', '-')}.pdf"
            filepath = os.path.join("/tmp", filename)

            c = canvas.Canvas(filepath, pagesize=letter)
            width, height = letter

            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, t["ecg_report_title"])
            c.setFont("Helvetica", 10)
            c.drawString(50, height - 70, f"{t['patient_initials']}: {patient_initials}")
            c.drawString(50, height - 85, f"{t['license_number']}: {license_number}")
            c.drawString(50, height - 100, f"{t['date']}: {date_str} {t['time']}: {time_str}")

            # Diagnóstico
            c.setFont("Helvetica", 12)
            c.drawString(50, height - 140, t["ecg_findings"])
            c.drawString(70, height - 160, diagnosis)

            # Imagen
            image = Image.open(uploaded_file)
            image_io = io.BytesIO()
            image.save(image_io, format="PNG")
            image_path = os.path.join("/tmp", "temp_ecg.png")
            with open(image_path, "wb") as f:
                f.write(image_io.getvalue())

            c.drawImage(image_path, 50, height - 500, width=500, preserveAspectRatio=True, mask='auto')

            # Descargo
            c.setFont("Helvetica-Oblique", 8)
            c.drawString(50, 50, t["disclaimer_footer"])
            c.save()

            # Mostrar botón para descarga manual
            with open(filepath, "rb") as f:
                b64 = f.read()
                st.download_button(label=t["download_pdf"],
                                   data=b64,
                                   file_name=filename,
                                   mime="application/pdf")
