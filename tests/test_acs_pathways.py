from dataclasses import replace
from io import BytesIO
import json

import pytest
from pypdf import PdfReader
from access import AccessDenied, anonymous_access
from acs_pathways import pathway, VERY_HIGH, HIGH, PATHWAY_VERSION
from integrated_engine import evaluate, emergency_priority
from clinical_case import save_case, raw_values
from case_reports import create_draft, review_draft, export_draft
from translations import translations, LANGUAGES
from test_stage2a import saved, acute, results
from test_ui_and_reports import start_app


def user_case(context, **overrides):
    data=dict(age=54, sex='M', smoker=True, chest_pain=True,
              chief_complaint='Dolor precordial opresivo 8/10, sudoración y taquicardia.',
              onset='1 hora', symptom_duration_min=60, sbp=140, dbp=90, heart_rate=100,
              killip=1, medical_history='Sin antecedentes coronarios referidos.',
              ecg_notes='Supradesnivel del ST de V1 a V5 informado por el médico.',
              acs_context='stemi')
    data.update(overrides)
    return saved(context, **data)


def test_pablos_case_immediate_priority_without_missing_lab_delay(pro_context):
    case=user_case(pro_context)
    priority=emergency_priority(pro_context,case)
    assert priority.code=='stemi' and priority.activation=='unknown'
    plan=pathway(pro_context,case)
    assert plan.route=='stemi_timing_pending'
    assert plan.missing==('pci_delay_min',)
    scores=results(pro_context,case)
    assert scores['timi'].status=='ineligible' and not scores['timi'].result
    assert scores['grace'].status=='missing' and not scores['grace'].result
    assert case.facts['known_cad'].value is None
    assert case.facts['haemodynamic_instability'].value is None
    assert case.facts['sex'].value=='M' and case.facts['killip'].value==1
    assert 'creatinine' not in plan.missing


@pytest.mark.parametrize('delay',[0,90,120])
def test_stemi_timely_pci_boundary(delay,pro_context):
    case=user_case(pro_context,pci_delay_min=delay)
    assert pathway(pro_context,case).route=='stemi_primary_pci'


@pytest.mark.parametrize('minutes,route',[(720,'stemi_pharmaco_invasive'),(721,'stemi_late')])
def test_stemi_lysis_time_boundary_and_eligibility(minutes,route,pro_context):
    case=user_case(pro_context,pci_delay_min=121,symptom_duration_min=minutes,
                   lysis_eligible=True,haemodynamic_instability=False,
                   dangerous_arrhythmia=False,mechanical_complication=False)
    assert pathway(pro_context,case).route==route


def test_stemi_unknown_contraindications_or_instability_cannot_enter_lysis(pro_context):
    case=user_case(pro_context,pci_delay_min=180)
    plan=pathway(pro_context,case)
    assert plan.route=='stemi_safety_pending' and 'lysis_eligible' in plan.missing
    case=user_case(pro_context,pci_delay_min=180,lysis_eligible=True)
    assert pathway(pro_context,case).route=='stemi_safety_pending'
    case=user_case(pro_context,pci_delay_min=180,lysis_eligible=False)
    assert pathway(pro_context,case).route=='stemi_lysis_excluded'
    case=user_case(pro_context,pci_delay_min=180,lysis_eligible=True,haemodynamic_instability=True)
    assert pathway(pro_context,case).route=='stemi_unstable'


@pytest.mark.parametrize('field',VERY_HIGH)
def test_each_sest_very_high_criterion_overrides_missing_scores(field,pro_context):
    case=saved(pro_context,acs_context='ua_nstemi',**{field:True})
    plan=pathway(pro_context,case)
    assert plan.route=='sest_immediate' and field in plan.reasons
    assert results(pro_context,case)['grace'].status=='missing'
    assert 'sest_no_lysis' in plan.supplemental


@pytest.mark.parametrize('field',HIGH)
def test_sest_high_risk_only_after_very_high_criteria_assessed(field,pro_context):
    case=saved(pro_context,acs_context='ua_nstemi',**{field:True})
    assert pathway(pro_context,case).route=='sest_priority_pending'
    case=saved(pro_context,acs_context='ua_nstemi',**{k:False for k in VERY_HIGH},**{field:True})
    assert pathway(pro_context,case).route=='sest_early'


def test_sest_grace_high_risk_and_incomplete_not_low_risk(pro_context):
    case=acute(pro_context,age=80,**{k:False for k in VERY_HIGH})
    assert results(pro_context,case)['grace'].result['points']>140
    assert pathway(pro_context,case).route=='sest_early'
    case=acute(pro_context,**{k:False for k in VERY_HIGH},**{k:False for k in HIGH})
    assert pathway(pro_context,case).route=='sest_risk_pending'
    case=acute(pro_context,**{k:False for k in VERY_HIGH},**{k:False for k in HIGH},high_suspicion_ua=True)
    assert pathway(pro_context,case).route=='sest_inpatient'
    case=acute(pro_context,**{k:False for k in VERY_HIGH},**{k:False for k in HIGH},high_suspicion_ua=False)
    assert pathway(pro_context,case).route=='sest_individualized'


def test_activation_is_documentation_not_service_call(pro_context):
    for flag,status in [(None,'unknown'),(False,'not_activated'),(True,'documented')]:
        data={} if flag is None else {'reperfusion_activated':flag}
        case=user_case(pro_context,**data)
        assert emergency_priority(pro_context,case).activation==status
    case=saved(pro_context,acs_context='stemi',reperfusion_activated=True,confirmed=False)
    assert emergency_priority(pro_context,case) is None
    assert pathway(pro_context,case) is None


def test_permissions_and_prior_template_review_expire(pro_context,other_context):
    case=user_case(pro_context)
    with pytest.raises(AccessDenied):pathway(anonymous_access(),case)
    with pytest.raises(PermissionError):pathway(other_context,case)
    t=translations['es'];draft=create_draft(pro_context,case,t)
    old=replace(draft,template_version='2A.1')
    with pytest.raises(ValueError,match='report_stale'):review_draft(pro_context,case,old,confirmed=True)


@pytest.mark.parametrize('lang',LANGUAGES)
def test_stemi_report_priority_not_editable_and_pdf_version(lang,pro_context):
    case=user_case(pro_context);t=translations[lang]
    draft=review_draft(pro_context,case,create_draft(pro_context,case,t),confirmed=True)
    report,pdf=export_draft(pro_context,case,draft,t)
    assert t['stemi_priority'] in report['priority_note']
    assert t['activation_unknown'] in report['priority_note']
    assert report['pathway_version']==PATHWAY_VERSION
    assert any(t['sest_no_lysis']==v for _,v in report['results']) is False
    reader=PdfReader(BytesIO(pdf));assert len(reader.pages)>1
    meta=json.loads(reader.metadata.subject)
    assert meta['pathway_id']=='stemi' and meta['pathway_version']==PATHWAY_VERSION


@pytest.mark.parametrize('lang',['es','en','pt'])
def test_priority_appears_in_draft_before_save_and_sest_has_separate_route(lang):
    app=start_app(lang);app.radio(key='workspace').set_value('emergency').run()
    case=app.session_state['_clinical_case'];p='case:'+case.case_id+':'
    app.selectbox(key=p+'acs_context').set_value('stemi').run()
    assert not app.exception
    assert translations[lang]['stemi_priority'] in [x.value for x in app.error]
    assert not app.session_state['_clinical_case'].facts
    app.selectbox(key=p+'acs_context').set_value('ua_nstemi').run()
    app.selectbox(key=p+'refractory_pain').set_value('present').run()
    app.checkbox(key=p+'review').check().run();app.button(key=p+'save').click().run()
    assert not app.exception
    assert translations[lang]['sest_immediate'] in [x.value for x in app.warning]
    assert translations[lang]['stemi_priority'] not in [x.value for x in app.error]


def test_grace_140_is_not_above_140(pro_context):
    case=acute(pro_context,age=75,heart_rate=100,sbp=100,creatinine=.8,
               **{k:False for k in VERY_HIGH},**{k:False for k in HIGH},high_suspicion_ua=False)
    assert results(pro_context,case)['grace'].result['points']==140
    assert pathway(pro_context,case).route=='sest_individualized'


def test_fibrinolysis_in_sest_prevents_report_confirmation(pro_context):
    from integrated_engine import consistency
    case=saved(pro_context,acs_context='ua_nstemi',reperfusion_strategy='fibrinolysis')
    assert consistency(pro_context,case)[0].code=='sest_lysis_conflict'
    with pytest.raises(ValueError,match='report_required'):create_draft(pro_context,case,translations['es'])
