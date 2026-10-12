"""Shared intake and deterministic integrated assessment; no external AI."""
from itertools import groupby
import streamlit as st

from access import Feature, allows, current_access
from clinical_case import FIELD_SPECS, create_case, raw_values, save_case, require_owner, matches_saved


def render_case(t, mode):
    context = current_access()
    if not allows(context, Feature.CLINICAL_CASE):
        st.info(t['pro_required'])
        return
    case = st.session_state.get('_clinical_case')
    if case is None or case.owner != context.subject:
        case = create_case(context, mode)
        st.session_state['_clinical_case'] = case
    require_owner(context, case)
    if st.button(t['case_new'], key='case:new'):
        # Clear all draft widget state and any independent reports from the previous patient.
        from access_ui import clear_clinical_session
        clear_clinical_session()
        st.session_state['_clinical_case'] = create_case(context, mode)
        st.rerun()
    st.subheader(t['case_title'])
    st.caption(t['case_notice'])
    st.info(t['case_scope'])
    prefix = 'case:' + case.case_id + ':'
    draft = st.session_state.get('_clinical_draft')
    if not draft or draft['case_id'] != case.case_id:
        draft = dict(case_id=case.case_id, raw=raw_values(case), alias=case.alias, mode=mode)
    alias = st.text_input(t['case_alias'], value=draft['alias'], max_chars=32, key=prefix+'alias')
    values = {}
    for group, specifications in groupby(FIELD_SPECS, key=lambda x: x.group):
        with st.expander(t['case_group_'+group], expanded=group in ('identity', 'presentation')):
            for spec in specifications:
                key = prefix + spec.key
                initial = draft['raw'][spec.key]
                if spec.kind == 'tri':
                    options = ['unknown', 'present', 'absent']
                    values[spec.key] = st.selectbox(t[spec.key], options, index=options.index(initial),
                        format_func=lambda x: t['case_'+x], key=key)
                elif spec.kind == 'acs':
                    options = ['unknown', 'suspected_acs', 'ua_nstemi', 'not_acs']
                    values[spec.key] = st.selectbox(t[spec.key], options, index=options.index(initial),
                        format_func=lambda x: t['case_unknown'] if x == 'unknown' else t[x], key=key)
                elif spec.kind == 'sex':
                    options = ['unknown', 'M', 'F']
                    values[spec.key] = st.selectbox(t['sex'], options, index=options.index(initial),
                        format_func=lambda x: t['case_unknown'] if x == 'unknown' else t[x], key=key)
                elif spec.kind == 'text':
                    values[spec.key] = st.text_area(t[spec.key], value=initial, max_chars=4000, height=90, key=key)
                else:
                    values[spec.key] = st.text_input(t[spec.key], value=initial, key=key)
    new_draft = dict(case_id=case.case_id, raw=values, alias=alias, mode=mode)
    review_key = prefix+'review'
    if new_draft != draft:
        st.session_state[review_key] = False
    st.session_state['_clinical_draft'] = new_draft
    confirmed = st.checkbox(t['case_review'], value=case.review_state == 'reviewed', key=review_key)
    unsaved = not matches_saved(case, values, alias, mode)
    if unsaved:
        st.caption(t['case_unsaved'])
    if st.button(t['case_save'], key=prefix+'save'):
        try:
            case = save_case(context, case, values, mode=mode, alias=alias, confirmed=confirmed)
            st.session_state['_clinical_case'] = case
            unsaved = False
            for key in list(st.session_state):
                if key.startswith('case_report:'):
                    del st.session_state[key]
            st.success(t['case_saved'])
        except ValueError as error:
            field = 'case_alias' if str(error) == 'alias' else str(error)
            st.error(t['case_invalid'].format(field=t.get(field, t['case_title'])))
    state = 'case_reviewed' if not unsaved and case.review_state == 'reviewed' else 'case_draft'
    st.caption(f"{t['case_version']}: {case.revision} · {t[state]}")

    from integrated_ui import render_integrated
    render_integrated(context, case, t, unsaved=unsaved)
