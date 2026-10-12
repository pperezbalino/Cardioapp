from pathlib import Path
import streamlit as st
from tools import framingham, euroscore, chads_vasc, grace, timi, bmi, ckd_epi, drug_calculator, ecg_analysis
from translations import translations, LANGUAGES

st.set_page_config(page_title='CardioApp', layout='centered', page_icon='🫀')
previous_language = st.session_state.get('_last_language', 'es')
lang = st.selectbox(translations[previous_language]['language'], list(LANGUAGES),
                    format_func=LANGUAGES.__getitem__, key='language')
if lang != previous_language:
    for key in list(st.session_state):
        if key.startswith('report:'):
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
modules = {'framingham': framingham, 'euroscore': euroscore, 'chads': chads_vasc,
           'grace': grace, 'timi': timi, 'bmi': bmi, 'ckd': ckd_epi}
with st.expander(t['scores'], expanded=True):
    selected = st.selectbox(t['select_score'], list(modules), format_func=t.__getitem__, key='score')
    modules[selected].calcular(t)
with st.expander(t['drugs']):
    drug_calculator.calcular(t)
with st.expander(t['ecg']):
    ecg_analysis.calcular(t)
st.caption(t['pdf_disclaimer'])
