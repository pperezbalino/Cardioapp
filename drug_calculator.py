import streamlit as st

def drug_calculator(t):
    st.subheader(t["drugs"])

    drugs = {
        t["drug_adrenaline"]: {
            "concentration": "1 mg/mL (1:1000)",
            "dose_range": "0.01–0.5 mcg/kg/min",
            "info": t["adrenaline_info"]
        },
        t["drug_noradrenaline"]: {
            "concentration": "1 mg/mL",
            "dose_range": "0.01–3 mcg/kg/min",
            "info": t["noradrenaline_info"]
        },
        t["drug_dobutamine"]: {
            "concentration": "250 mg/20 mL",
            "dose_range": "2–20 mcg/kg/min",
            "info": t["dobutamine_info"]
        },
        t["drug_nitroglycerin"]: {
            "concentration": "50 mg/10 mL",
            "dose_range": "5–200 mcg/min",
            "info": t["nitroglycerin_info"]
        },
        t["drug_levosimendan"]: {
            "concentration": "12.5 mg/5 mL",
            "dose_range": "0.05–0.2 mcg/kg/min",
            "info": t["levosimendan_info"]
        }
    }

    drug = st.selectbox(t["select_drug"], list(drugs.keys()))
    concentration = drugs[drug]["concentration"]
    dose_range = drugs[drug]["dose_range"]
    info = drugs[drug]["info"]

    st.markdown(f"**{t['concentration']}:** {concentration}")
    st.markdown(f"**{t['dose_range']}:** {dose_range}")
    st.info(info)
