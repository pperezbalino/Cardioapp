"""Pilot invitation UI. Clinical session is cleared on identity changes."""
import time
import streamlit as st
from access import AccessDenied, PRO_PRICE_USD, current_access, pilot_access


def clear_clinical_session():
    for key in list(st.session_state):
        if key.startswith(('case:', '_clinical_', 'report:', 'calculation:', 'download:',
                           'framingham:', 'euroscore:', 'chads:', 'grace:', 'timi:',
                           'bmi:', 'ckd:', 'drugs:', 'ecg:')):
            del st.session_state[key]


def render_access(t):
    previous = st.session_state.get('_access_context')
    context = current_access()
    if getattr(previous, 'plan', None) == 'pro' and context.plan != 'pro':
        clear_clinical_session()
    st.caption('CardioApp Pro' if context.plan == 'pro' else 'CardioApp Free')
    st.caption(t['price_note'].format(price=PRO_PRICE_USD))
    if st.session_state.pop('_access_notice', False):
        st.info(t['pro_required'])
    if context.plan == 'pro':
        if st.button(t['logout'], key='access:logout'):
            clear_clinical_session()
            st.session_state.pop('_access_context', None)
            st.rerun()
    else:
        with st.expander(t['pilot_login']):
            code = st.text_input(t['invitation_code'], type='password', max_chars=200, key='access:code')
            if st.button(t['login'], key='access:login'):
                now = time.time()
                attempts = [x for x in st.session_state.get('_login_attempts', []) if now - x < 60]
                if len(attempts) >= 5:
                    st.error(t['login_wait'])
                else:
                    try:
                        verified = pilot_access(code)
                        clear_clinical_session()
                        st.session_state['_access_context'] = verified
                        st.session_state.pop('access:code', None)
                        st.session_state.pop('_login_attempts', None)
                        st.rerun()
                    except AccessDenied:
                        st.session_state['_login_attempts'] = attempts + [now]
                        st.error(t['invalid_invitation'])
    return context
