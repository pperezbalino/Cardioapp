from io import BytesIO
import pytest
from pypdf import PdfReader
from access import anonymous_access, AccessDenied
from clinical_case import raw_values,save_case
from integrated_engine import consistency
from acs_pathways import nitrate_assessment,pathway,VERY_HIGH
from case_reports import create_draft,review_draft,export_draft
from translations import translations
from test_stage2a import saved,acute
from test_ui_and_reports import start_app


@pytest.mark.parametrize('pressure,status',[(89,'ntg_not_eligible'),(90,'ntg_reference_available'),(140,'ntg_reference_available')])
def test_guideline_pressure_boundary(pressure,status,pro_context):
    case=saved(pro_context,acs_context='ua_nstemi',sbp=pressure,
               haemodynamic_instability=False,ntg_contraindications=False)
    assert nitrate_assessment(pro_context,case).status==status


def test_unknown_safety_never_means_eligible(pro_context):
    case=saved(pro_context,acs_context='ua_nstemi',sbp=140)
    result=nitrate_assessment(pro_context,case)
    assert result.status=='ntg_safety_pending'
    assert set(result.missing)=={'haemodynamic_instability','ntg_contraindications'}
    case=saved(pro_context,acs_context='ua_nstemi',sbp=140,confirmed=False,
               haemodynamic_instability=False,ntg_contraindications=False)
    assert nitrate_assessment(pro_context,case) is None


@pytest.mark.parametrize('field',['ntg_contraindications','haemodynamic_instability'])
def test_documented_exclusion_blocks_reference_eligibility(field,pro_context):
    case=saved(pro_context,acs_context='ua_nstemi',sbp=140,**{field:True})
    assert nitrate_assessment(pro_context,case).status=='ntg_not_eligible'


def test_uncontrolled_pain_does_not_create_refractoriness(pro_context):
    case=saved(pro_context,acs_context='ua_nstemi',angina_response='not_yet_treated')
    plan=pathway(pro_context,case)
    assert plan.route=='sest_priority_pending'
    assert 'refractory_pain' in plan.missing
    assert case.facts['refractory_pain'].value is None


def test_conflicting_refractory_untreated_data_requires_correction(pro_context):
    case=saved(pro_context,acs_context='ua_nstemi',refractory_pain=True,
               angina_response='not_yet_treated')
    assert consistency(pro_context,case)[0].code=='pain_response_conflict'
    with pytest.raises(ValueError,match='report_required'):create_draft(pro_context,case,translations['es'])
    # A conflict cannot silently de-escalate an explicitly reported urgent criterion.
    assert pathway(pro_context,case).route=='sest_immediate'


def test_current_pain_relief_does_not_erase_recurrent_or_other_risk(pro_context):
    case=saved(pro_context,acs_context='ua_nstemi',refractory_pain=True,angina_response='pain_controlled')
    assert not consistency(pro_context,case)
    assert pathway(pro_context,case).route=='sest_immediate'
    case=saved(pro_context,acs_context='ua_nstemi',angina_response='pain_controlled',
               nstemi_confirmed=True,**{k:False for k in VERY_HIGH})
    assert pathway(pro_context,case).route=='sest_early'


def test_stemi_activation_and_selective_reference_independent_of_ntg(pro_context):
    case=saved(pro_context,acs_context='stemi',ntg_contraindications=True)
    assert pathway(pro_context,case).route=='stemi_timing_pending'
    case=acute(pro_context)
    assert 'sest_selective_reference' in pathway(pro_context,case).supplemental
    assert pathway(pro_context,case).route!='sest_individualized'


def test_no_inference_of_administered_treatment_and_review_invalidation(pro_context):
    case=saved(pro_context,acs_context='ua_nstemi',sbp=140,ntg_contraindications=False,
               haemodynamic_instability=False,antiischaemic_given='FICTITIOUS: NTG SL administered',
               angina_response='pain_controlled')
    t=translations['es'];draft=review_draft(pro_context,case,create_draft(pro_context,case,t),confirmed=True)
    report,pdf=export_draft(pro_context,case,draft,t)
    assert any(t['ntg_reference'] in value for _,value in report['results'])
    assert any(t['ntg_reference_available'] in value for _,value in report['results'])
    assert len(PdfReader(BytesIO(pdf)).pages)>1
    raw=raw_values(case);raw['angina_response']='persistent_despite_treatment'
    changed=save_case(pro_context,case,raw,mode='emergency',confirmed=True)
    with pytest.raises(ValueError,match='report_stale'):export_draft(pro_context,changed,draft,t)


def test_permissions(pro_context,other_context):
    case=acute(pro_context)
    with pytest.raises(AccessDenied):nitrate_assessment(anonymous_access(),case)
    with pytest.raises(PermissionError):nitrate_assessment(other_context,case)


@pytest.mark.parametrize('lang',['es','en','pt'])
def test_ui_reference_and_response_are_shared_clinical_data(lang):
    app=start_app(lang);app.radio(key='workspace').set_value('emergency').run()
    case=app.session_state['_clinical_case'];p='case:'+case.case_id+':'
    app.selectbox(key=p+'acs_context').set_value('ua_nstemi')
    app.selectbox(key=p+'angina_response').set_value('not_yet_treated')
    app.text_input(key=p+'sbp').set_value('140')
    app.selectbox(key=p+'haemodynamic_instability').set_value('absent')
    app.selectbox(key=p+'ntg_contraindications').set_value('absent')
    app.run();app.checkbox(key=p+'review').check().run();app.button(key=p+'save').click().run()
    assert not app.exception
    assert translations[lang]['ntg_reference_available'] in [x.value for x in app.info]
    assert any(translations[lang]['ntg_reference']==x.value for x in app.markdown)
    assert app.session_state['_clinical_case'].facts['antiischaemic_given'].value is None
    app.radio(key='workspace').set_value('outpatient').run()
    assert app.selectbox(key=p+'angina_response').value=='not_yet_treated'
