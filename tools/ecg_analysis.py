
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from translations import translations

def analyze_ecg(image_path, patient_initials, license_number, selected_language):
    # Traducciones
    t = translations[selected_language]
    
    # Simulación de análisis de ECG
    diagnosis = t["possible_ecg_diagnosis"]
    
    # Fecha y hora
    now = datetime.datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    # Nombre del archivo PDF en el idioma seleccionado
    filename = f"{t['ecg_report_filename_prefix']}_{date_str}_{time_str.replace(':', '-')}.pdf"
    
    # Crear el PDF
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Encabezado con logo y título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, t["ecg_report_title"])
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, f"{t['patient_initials']}: {patient_initials}")
    c.drawString(50, height - 85, f"{t['license_number']}: {license_number}")
    c.drawString(50, height - 100, f"{t['date']}: {date_str} {t['time']}: {time_str}")

    # Cuerpo del informe
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 140, t["ecg_findings"])
    c.drawString(70, height - 160, diagnosis)

    # Descargo de responsabilidad
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, 50, t["disclaimer_footer"])

    c.save()

    return filename
