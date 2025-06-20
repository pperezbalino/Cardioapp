
import streamlit as st

def drug_calculator():
    st.header("Calculadora de Dosis de Drogas de Urgencia")

    drugs = {
        "Adrenalina": {
            "concentration": "1 mg/mL (1:1000)",
            "dose_range": "0.01–0.5 mcg/kg/min",
            "info": "Dosis inicial habitual: 0.01 mcg/kg/min. Título según respuesta."
        },
        "Noradrenalina": {
            "concentration": "1 mg/mL",
            "dose_range": "0.01–3 mcg/kg/min",
            "info": "Dosis inicial: 0.05 mcg/kg/min. Aumentar según presión arterial."
        },
        "Dobutamina": {
            "concentration": "250 mg/20 mL",
            "dose_range": "2–20 mcg/kg/min",
            "info": "Iniciar con 2–5 mcg/kg/min. Aumentar según respuesta clínica."
        },
        "Nitroglicerina": {
            "concentration": "50 mg/10 mL",
            "dose_range": "5–200 mcg/min",
            "info": "Dosis inicial: 5 mcg/min. Aumentar cada 3–5 minutos si es necesario."
        },
        "Levosimendan": {
            "concentration": "12.5 mg/5 mL",
            "dose_range": "0.05–0.2 mcg/kg/min",
            "info": "Usado en IC descompensada. Infusión continua 24 h."
        },
        "Milrinona": {
            "concentration": "10 mg/10 mL",
            "dose_range": "0.25–0.75 mcg/kg/min",
            "info": "Usado en IC. Puede necesitar bolo inicial."
        },
        "Lidocaína": {
            "concentration": "20 mg/mL",
            "dose_range": "1–4 mg/min",
            "info": "Inicial: bolo de 1–1.5 mg/kg, luego infusión 1–4 mg/min."
        },
        "Amiodarona": {
            "concentration": "150 mg/3 mL",
            "dose_range": "1 mg/min",
            "info": "Dosis: bolo 150 mg en 10 min, luego 1 mg/min por 6 h."
        },
        "Solución polarizante": {
            "concentration": "Variable",
            "dose_range": "Uso específico",
            "info": "Glucosa, insulina y potasio para cardioprotección en CI."
        }
    }

    drug = st.selectbox("Selecciona la droga", list(drugs.keys()))
    weight = st.number_input("Peso del paciente (kg)", min_value=30, max_value=200, value=70)

    st.subheader(f"Dosis sugerida para {drug}")
    st.write(f"**Concentración habitual:** {drugs[drug]['concentration']}")
    st.write(f"**Rango terapéutico:** {drugs[drug]['dose_range']}")
    st.write(f"**Recomendación:** {drugs[drug]['info']}")

    if "mcg/kg/min" in drugs[drug]["dose_range"]:
        min_dose = float(drugs[drug]["dose_range"].split("–")[0])
        max_dose = float(drugs[drug]["dose_range"].split("–")[1].split()[0])
        st.write(f"**Dosis total recomendada:** entre {round(min_dose * weight, 2)} y {round(max_dose * weight, 2)} mcg/min")

