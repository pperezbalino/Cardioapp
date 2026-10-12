"""Pro integrated case, local simulation and editable reviewed report."""
import streamlit as st

from clinical_case import require_owner, FIELDS
from integrated_engine import case_hash, evaluate, consistency, emergency_priority
from case_reports import (create_draft, edit_draft, review_draft, export_draft, score_text, field_value)
from copilot_provider import simulate
from acs_pathways import pathway, SOURCE, AHA_SOURCE, nitrate_assessment


def render_integrated(context, case, t, *, unsaved):
    require_owner(context, case)
    st.subheader(t['integrated_title'])
    st.caption(t['integrated_notice'])
    if unsaved:
        st.info(t['case_unsaved'])
        return
    treatment = pathway(context, case)
    if treatment:
        st.subheader(t['acs_pathway'])
        st.caption(t['acs_pathway_notice'])
        st.warning(t[treatment.route])
        if treatment.reasons:
            st.write(t['inputs'] + ': ' + ', '.join(t[k] for k in treatment.reasons))
        if treatment.missing:
            st.write(t['score_missing'].format(fields=', '.join(t[k] for k in treatment.missing)))
        nitrate = nitrate_assessment(context, case)
        if nitrate:
            st.info(t[nitrate.status])
            if nitrate.missing:
                st.caption(t['score_missing'].format(fields=', '.join(t[k] for k in nitrate.missing)))
        for step in treatment.supplemental:
            st.write(t[step])
        st.caption(SOURCE)
        st.caption(AHA_SOURCE)
    issues = consistency(context, case)
    for issue in issues:
        st.warning(t[issue.code])
    priority = emergency_priority(context, case)
    if priority:
        st.warning(t['activation_'+priority.activation])
        st.caption(t['stemi_reference'])
        st.caption('ESC ACS (2023), 5.2.1 / 5.3: https://doi.org/10.1093/eurheartj/ehad191')
        st.caption(t['secondary_scores'])
    scores = evaluate(context, case)
    for score in scores:
        with st.expander(t[score.algorithm_id], expanded=score.status == 'ready'):
            st.write(score_text(score, t))
            if score.status == 'ready':
                st.caption(t['inputs'])
                for key, value in score.inputs.items():
                    st.write(t[key] + ': ' + field_value(FIELDS[key], value, t))
                from clinical_sources import NOTES, SOURCES
                if score.algorithm_id in NOTES:
                    st.caption(t[NOTES[score.algorithm_id]])
                for source in SOURCES[score.algorithm_id]:
                    st.caption(source)
    simulation = simulate(context, case)
    assert simulation.simulated and not simulation.model_calls
    st.caption(t['simulation_notice'])
    prefix = 'case_report:' + case.case_id + ':' + t['_lang'] + ':' + case.mode + ':'
    records = st.session_state.get('_clinical_reports', {})
    record = records.get((case.case_id, t['_lang'], case.mode))
    if record and record['draft'].input_hash != case_hash(case):
        st.info(t['report_stale'])
        record = None
    if st.button(t['report_create'], key=prefix+'create'):
        try:
            draft = create_draft(context, case, t)
            record = {'draft': draft}
            records[(case.case_id, t['_lang'], case.mode)] = record
            st.session_state['_clinical_reports'] = records
            # Regeneration restores the current source, never stale editor widgets.
            for key in list(st.session_state):
                if key.startswith(prefix) and key != prefix+'create':
                    del st.session_state[key]
        except ValueError as error:
            st.error(t[str(error)])
    if not record:
        return
    draft = record['draft']
    st.subheader(t['report_title_' + draft.mode])
    st.caption(t['report_notice'])
    sections = {}
    for key, value in draft.sections:
        sections[key] = st.text_area(t[key], value=value, max_chars=30000,
                                     height=130, key=prefix+key)
    updated = edit_draft(context, case, draft, sections)
    if updated is not draft:
        st.session_state[prefix+'review'] = False
        record.clear()
        record['draft'] = updated
        draft = updated
    confirmed = st.checkbox(t['report_review'], key=prefix+'review')
    if st.button(t['report_confirm'], key=prefix+'confirm'):
        try:
            draft = review_draft(context, case, draft, confirmed=confirmed)
            record['draft'] = draft
        except ValueError as error:
            st.error(t.get(str(error), t['report_required']))
    if draft.reviewed_digest:
        st.caption(t['report_reviewed'].format(actor=draft.reviewed_by,
                   time=draft.reviewed_at, version=draft.version))
        # Authorization and snapshot checks run before each download rendering.
        try:
            report, pdf = export_draft(context, case, draft, t)
            st.download_button(t['report_export'], pdf, 'cardioapp_consultation.pdf',
                               'application/pdf', key=prefix+'download')
        except ValueError as error:
            st.error(t.get(str(error), t['report_required']))



def render_priority_notice(t, mode, selected_context):
    # The physician-selected draft context prompts before saving or scoring.
    if mode == 'emergency' and selected_context == 'stemi':
        st.error(t['stemi_priority'])
        st.caption(t['stemi_origin'])
    elif mode == 'emergency' and selected_context == 'ua_nstemi':
        st.warning(t['sest_priority'])
