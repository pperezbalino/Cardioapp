
import streamlit as st

def calcular(t):
    st.subheader("Calculadora de Dosis de Drogas de Urgencia")

    drugs = {
        "Adrenalina": {
            "concentration": "1 mg/mL (1:1000)",
            "dose_range": (0.01, 0.5),  # mcg/kg/min
            "info": "Dosis inicial habitual: 0.01 mcg/kg/min. Ajustar según respuesta."
        },
        "Noradrenalina": {
            "concentration": "1 mg/mL",
            "dose_range": (0.01, 3.0),
            "info": "Dosis inicial: 0.05 mcg/kg/min. Ajustar según presión arterial."
        },
        "Dobutamina": {
            "concentration": "12.5 mg/10 mL",
            "dose_range": (2, 20),  # mcg/kg/min
            "info": "Dosis inicial: 5 mcg/kg/min. Aumentar según respuesta clínica."
        },
        "Levosimendán": {
            "concentration": "12.5 mg/5 mL",
            "dose_range": (0.05, 0.2),
            "info": "Dosis de carga: 12 mcg/kg en 10 min seguido de infusión."
        },
        "Lidocaína": {
            "concentration": "20 mg/mL",
            "dose_range": (1, 4),  # mg/min
            "info": "Dosis inicial: 1-1.5 mg/kg bolus. Infusión 1-4 mg/min."
        },
        "Amiodarona": {
            "concentration": "50 mg/mL",
            "dose_range": (1, 2),  # mg/min
            "info": "Dosis inicial: 150 mg en 10 min, luego 1-2 mg/min."
        }
    }

    drug = st.selectbox("Selecciona la droga", list(drugs.keys()))
    weight = st.number_input("Peso del paciente (kg)", min_value=30.0, max_value=200.0, value=70.0)

    if st.button("Calcular dosis"):
        info = drugs[drug]
        min_dose = info["dose_range"][0] * weight
        max_dose = info["dose_range"][1] * weight
        result = (
            f"Droga: {drug}\n"
            f"Concentración habitual: {info['concentration']}\n"
            f"Rango terapéutico: {info['dose_range'][0]}–{info['dose_range'][1]} mcg/kg/min o mg/min según fármaco\n"
            f"Dosis total recomendada: {min_dose:.2f}–{max_dose:.2f} {'mcg/min' if 'mcg' in info['info'] else 'mg/min'}\n"
            f"Recomendación: {info['info']}"
        )
        st.success(result)
        return result
    return None
