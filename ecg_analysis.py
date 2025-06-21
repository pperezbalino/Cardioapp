
import streamlit as st
from PIL import Image
import base64
import io
from pdf_utils import generate_pdf
from translations import translations

def ecg_analysis(lang):
    t = translations.get(lang, translations["es"])
    st.markdown("### " + t["ecg_title"])
    st.write(t["ecg_instruction"])

    uploaded_file = st.file_uploader(t["upload_prompt"], type=["png", "jpg", "jpeg", "pdf"])
    ecg_image = None

    if uploaded_file and uploaded_file.type != "application/pdf":
        ecg_image = Image.open(uploaded_file)
        st.image(ecg_image, caption=t["ecg_image_preview"], use_column_width=True)

    patient_initials = st.text_input(t["patient_initials_label"])
    license_number = st.text_input(t["license_number_label"])

    if st.button(t["analyze_button"]):
        if uploaded_file:
            st.markdown("### " + t["ecg_report_title"])
            st.write(f"**{t['patient_initials_label']}:** {patient_initials or t['not_provided']}")
            st.write(f"**{t['license_number_label']}:** {license_number or t['not_provided']}")
            st.write(f"**{t['ecg_result_label']}:** {t['ecg_mock_result']}")
            st.write(f"**{t['ecg_note_label']}:** {t['ecg_mock_note']}")

            if st.button(t["export_pdf_button"]):
                pdf_bytes = generate_pdf(
                    patient_initials or t["not_provided"],
                    license_number or t["not_provided"],
                    t["ecg_mock_result"],
                    t["ecg_mock_note"],
                    ecg_image,
                    lang
                )
                b64 = base64.b64encode(pdf_bytes).decode()
                href = f'<a href="data:application/pdf;base64,{b64}" download="{t["ecg_report_filename"]}">{t["download_pdf_link"]}</a>'
                st.markdown(href, unsafe_allow_html=True)
        else:
            st.error(t["ecg_error_no_file"])
