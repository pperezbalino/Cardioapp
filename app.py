from pathlib import Path
import streamlit as st
from tools import framingham, euroscore, chads_vasc, grace, timi, bmi, ckd_epi, drug_calculator, ecg_analysis, has_bled
from translations import translations, LANGUAGES
from access_ui import render_access, clear_clinical_session
from access import AccessDenied
from case_ui import render_case

st.set_page_config(page_title='CardioApp', layout='centered', page_icon='🫀')
previous_language = st.session_state.get('_last_language', 'es')
lang = st.selectbox(translations[previous_language]['language'], list(LANGUAGES),
                    format_func=LANGUAGES.__getitem__, key='language')
if lang != previous_language:
    for key in list(st.session_state):
        if key.startswith(('report:', 'calculation:')):
            del st.session_state[key]
    st.session_state['_last_language'] = lang
    st.rerun()
st.session_state['_last_language'] = lang
t = translations[lang]
direction = 'rtl' if lang == 'ar' else 'ltr'
alignment = 'right' if lang == 'ar' else 'left'
st.markdown(f'''<style>
.stMain .stMarkdown, .stMain label, .stMain .stTextInput input, .stMain textarea {{direction:{direction};text-align:{alignment};}}
.stMain .stNumberInput input {{direction:ltr;text-align:left;}}
.stMain h1, .stMain h2, .stMain h3 {{direction:{direction};text-align:{alignment};}}
</style>''', unsafe_allow_html=True)

if not st.session_state.get('disclaimer_accepted', False):
    st.write(t['disclaimer_text'])
    if st.button(t['accept_disclaimer'], key='accept_disclaimer'):
        st.session_state.disclaimer_accepted = True
        st.rerun()
    st.stop()

st.image(str(Path(__file__).with_name('logo.png')), width=120)
st.title('🫀 CardioApp')
render_access(t)
workspace = st.radio(t['workspace'], ['tools_nav', 'emergency', 'outpatient'],
                     format_func=t.__getitem__, key='workspace', horizontal=True)
modules = {'framingham': framingham, 'euroscore': euroscore, 'chads': chads_vasc,
           'grace': grace, 'has_bled': has_bled, 'timi': timi, 'bmi': bmi, 'ckd': ckd_epi}
try:
    if workspace == 'tools_nav':
        with st.expander(t['scores'], expanded=True):
            selected = st.selectbox(t['select_score'], list(modules), format_func=t.__getitem__, key='score')
            modules[selected].calcular(t)
        with st.expander(t['drugs']):
            drug_calculator.calcular(t)
        with st.expander(t['ecg']):
            ecg_analysis.calcular(t)
    else:
        render_case(t, workspace)
except AccessDenied:
    clear_clinical_session()
    st.session_state.pop('_access_context', None)
    st.session_state['_access_notice'] = True
    st.rerun()
st.caption(t['pdf_disclaimer'])
