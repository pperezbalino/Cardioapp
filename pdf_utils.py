
from fpdf import FPDF
import base64
import streamlit as st
import os

class PDF(FPDF):
    def __init__(self, logo_path, lang_data, ecg_image_path=None):
        super().__init__()
        self.lang_data = lang_data
        self.logo_path = logo_path
        self.ecg_image_path = ecg_image_path

    def header(self):
        if self.logo_path and os.path.exists(self.logo_path):
            self.image(self.logo_path, 10, 8, 20)
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, self.lang_data["pdf_title"], ln=True, align="C")
        self.ln(10)

    def add_report(self, title, content):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, title, ln=True)
        self.set_font("Arial", "", 11)
        for line in content.split("\n"):
            self.multi_cell(0, 8, line)
        self.ln()
        if self.ecg_image_path and os.path.exists(self.ecg_image_path):
            self.set_font("Arial", "B", 11)
            self.cell(0, 10, self.lang_data.get("ecg_image_label", "ECG Image:"), ln=True)
            self.image(self.ecg_image_path, x=None, y=None, w=180)
            self.ln()

    def disclaimer(self):
        self.set_font("Arial", "I", 9)
        self.multi_cell(0, 8, self.lang_data["pdf_disclaimer"])

    def output_to_base64(self):
        pdf_data = self.output(dest="S").encode("latin1")
        b64_pdf = base64.b64encode(pdf_data).decode("utf-8")
        return b64_pdf

def render_pdf_view(title, content, lang_data, logo_path="logo.png", ecg_image_path=None):
    pdf = PDF(logo_path, lang_data, ecg_image_path)
    pdf.add_page()
    pdf.add_report(title, content)
    pdf.disclaimer()
    b64_pdf = pdf.output_to_base64()
    filename = lang_data.get("pdf_filename", "CardioApp_Report.pdf")
    pdf_display = f"""
<iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="600px" type="application/pdf"></iframe>
<p><a href="data:application/pdf;base64,{b64_pdf}" download="{filename}">{lang_data.get("download_pdf", "Download PDF")}</a></p>
"""
    st.markdown(pdf_display, unsafe_allow_html=True)
