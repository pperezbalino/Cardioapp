"""Guideline ECG reference for clinician use; no automatic ECG diagnosis."""
import streamlit as st
from access import Feature, require

VERSION = 'AHAACC2025-ESC2023-ECG-1'
SOURCES = (
    'AHA/ACC ACS (2025), Table 3: https://doi.org/10.1161/CIR.0000000000001309',
    'ESC ACS (2023), section 3.2.1: https://doi.org/10.1093/eurheartj/ehad191',
)
# Each threshold applies in the requisite anatomically contiguous leads.
THRESHOLDS = (
    ('ecg_other_leads', 'ecg_any_population', '≥1 mm (≥0.10 mV)'),
    ('V2–V3', 'ecg_male_40_plus', '≥2 mm (≥0.20 mV)'),
    ('V2–V3', 'ecg_male_under_40', '≥2.5 mm (≥0.25 mV)'),
    ('V2–V3', 'ecg_female_any_age', '≥1.5 mm (≥0.15 mV)'),
)


def render_stemi_ecg_reference(context, t):
    require(context, Feature.CLINICAL_CASE)
    with st.expander(t['stemi_ecg_criteria'], expanded=True):
        st.write(t['ecg_st_rule'])
        st.caption(t['ecg_measurement'])
        st.table([{t['ecg_leads_column']: t.get(leads, leads),
                   t['ecg_population_column']: t[population],
                   t['ecg_threshold_column']: threshold}
                  for leads, population, threshold in THRESHOLDS])
        st.write(t['ecg_contiguous'])
        st.warning(t['ecg_complex_context'])
        st.write(t['ecg_posterior'])
        st.write(t['ecg_block'])
        st.caption(t['ecg_no_ruleout'])
        for source in SOURCES:
            st.caption(source)
        st.caption(VERSION)
