from dataclasses import replace
from io import BytesIO
import hashlib
import json
import time

import pytest
from pypdf import PdfReader
from access import (AccessContext, AccessDenied, Feature, ACCESS_LIFETIME_SECONDS,
                    allows, anonymous_access, pilot_access, require, valid_access)
from clinical_case import (FIELD_SPECS, create_case, save_case, raw_values,
                           confirmed_value, matches_saved, SCHEMA_VERSION)
from pdf_utils import make_report, generate_pdf
from tools.ecg_analysis import manual_report
from translations import translations
from test_ui_and_reports import start_app

TEST_CODE = 'test-only-cardioapp-pro-invite-0001'


def case_keys(app):
    case = app.session_state['_clinical_case']
    return 'case:' + case.case_id + ':'


def test_plan_matrix_and_disabled_future_features(pro_context):
    free = anonymous_access()
    assert allows(free, Feature.CALCULATORS)
    for feature in [Feature.CLINICAL_CASE, Feature.PDF, Feature.MANUAL_ECG]:
        assert not allows(free, feature)
        assert allows(pro_context, feature)
    for feature in [Feature.AI, Feature.VOICE, Feature.HISTORY]:
        assert not allows(pro_context, feature)
        with pytest.raises(AccessDenied, match='feature_unavailable'):
            require(pro_context, feature)


def test_forged_client_role_and_expired_access_are_rejected(pro_context):
    free = anonymous_access()
    assert not valid_access(replace(free, plan='pro', subject='test-doctor'))
    assert not valid_access(replace(pro_context, signature='forged'))
    assert not valid_access({'plan': 'pro', 'verified': True})
    expired = pilot_access(TEST_CODE, now=time.time() - ACCESS_LIFETIME_SECONDS - 1)
    assert not valid_access(expired)
    with pytest.raises(AccessDenied): require(expired, Feature.PDF)


def test_invitation_revocation_invalidates_existing_grants(pro_context, monkeypatch):
    assert valid_access(pro_context)
    monkeypatch.setenv('CARDIOAPP_PRO_INVITES', '{}')
    assert not valid_access(pro_context)
    with pytest.raises(AccessDenied): require(pro_context, Feature.CLINICAL_CASE)


@pytest.mark.parametrize('config', ['bad json', '[]', '{"bad": {"sha256": "wrong"}}'])
def test_invalid_invitation_configuration_fails_closed(config, monkeypatch):
    monkeypatch.setenv('CARDIOAPP_PRO_INVITES', config)
    with pytest.raises(AccessDenied): pilot_access(TEST_CODE)


def test_expired_and_duplicate_invites_fail_closed(monkeypatch):
    digest = hashlib.sha256(TEST_CODE.encode()).hexdigest()
    monkeypatch.setenv('CARDIOAPP_PRO_INVITES', json.dumps({'test-doctor':{
        'sha256':digest,'expires_at':'2000-01-01T00:00:00Z'}}))
    with pytest.raises(AccessDenied): pilot_access(TEST_CODE)
    monkeypatch.setenv('CARDIOAPP_PRO_INVITES', json.dumps({'one':{'sha256':digest}, 'two':{'sha256':digest}}))
    with pytest.raises(AccessDenied): pilot_access(TEST_CODE)


def test_free_cannot_call_report_services_directly(pro_context):
    free = anonymous_access()
    t = translations['es']
    with pytest.raises(AccessDenied): make_report('Title',[],[],'',[],t,context=free)
    report = make_report('Title',[],[],'',[],t,context=pro_context)
    for context in [None, free, replace(free, plan='pro')]:
        with pytest.raises(AccessDenied): generate_pdf(report,t,context=context)
    with pytest.raises(AccessDenied): manual_report(b'fake','fake.png','AB','123','text',True,t,context=free)
    with pytest.raises(AccessDenied): create_case(free)


def test_other_account_cannot_read_confirmed_fields_or_export(pro_context, other_context):
    case = create_case(pro_context)
    values = raw_values(case); values['age']='65'
    case = save_case(pro_context,case,values,mode='emergency',confirmed=True)
    with pytest.raises(PermissionError): confirmed_value(other_context,case,'age')
    with pytest.raises(PermissionError): save_case(other_context,case,values,mode='emergency')
    report=make_report('Title',[],[],'',[],translations['es'],context=pro_context)
    with pytest.raises(PermissionError): generate_pdf(report,translations['es'],context=other_context)


def test_unknown_is_not_absent_and_requires_confirmation(pro_context):
    case = create_case(pro_context)
    values = raw_values(case)
    assert all(values[s.key]=='unknown' for s in FIELD_SPECS if s.kind=='tri')
    values['hypertension']='absent';values['diabetes']='present';values['creatinine']='0,85'
    saved = save_case(pro_context,case,values,mode='emergency')
    assert saved.facts['hypertension'].value is False
    assert saved.facts['diabetes'].value is True
    assert saved.facts['stroke'].value is None
    assert saved.facts['creatinine'].value == .85
    assert saved.facts['creatinine'].unit == 'mg/dL'
    for field in ['hypertension','stroke','creatinine']:
        with pytest.raises(ValueError): confirmed_value(pro_context,saved,field)
    reviewed = save_case(pro_context,saved,values,mode='emergency',confirmed=True)
    assert confirmed_value(pro_context,reviewed,'hypertension') is False
    assert reviewed.facts['stroke'].confirmed is False
    with pytest.raises(ValueError): confirmed_value(pro_context,reviewed,'stroke')
    assert reviewed.review_state=='reviewed'


def test_case_versions_sources_and_no_duplicate_revisions(pro_context):
    case=create_case(pro_context); values=raw_values(case);values['clinical_notes']='Clinician-entered text'
    one=save_case(pro_context,case,values,mode='emergency',confirmed=True)
    assert one.schema_version==SCHEMA_VERSION
    assert one.facts['clinical_notes'].source=='clinician_text'
    assert one.facts['clinical_notes'].assertion_type=='documented'
    assert one.facts['clinical_notes'].observed_at is None
    assert one.facts['clinical_notes'].confirmed_by==pro_context.subject
    unchanged=save_case(pro_context,one,values,mode='emergency',confirmed=True)
    assert unchanged is one
    values['clinical_notes']='Edited text'
    two=save_case(pro_context,one,values,mode='outpatient',confirmed=False)
    assert two.case_id==one.case_id
    assert two.revision==one.revision+1
    assert two.review_state=='draft'
    assert two.facts['clinical_notes'].confirmed is False
    assert 'mode' in two.audit[-1].changed_fields
    assert two.audit[-1].input_hash!=one.audit[-1].input_hash
    assert one.facts['clinical_notes'].value=='Clinician-entered text'


@pytest.mark.parametrize('key,value', [('age','0'),('age','65.5'),('oxygen','101'),('creatinine','0'),
                                     ('creatinine','1,234.56'),('weight','nan'),('heart_rate','-1')])
def test_bad_clinical_values_do_not_modify_saved_case(key,value,pro_context):
    case=create_case(pro_context);values=raw_values(case);values[key]=value
    with pytest.raises(ValueError): save_case(pro_context,case,values,mode='emergency')
    assert case.revision==0
    assert not case.facts


def test_numeric_format_changes_do_not_create_false_unsaved_flags(pro_context):
    case=create_case(pro_context);values=raw_values(case);values['creatinine']='0,85'
    saved=save_case(pro_context,case,values,mode='emergency')
    assert matches_saved(saved,values,'','emergency')
    values['creatinine']='0.850'
    assert matches_saved(saved,values,'','emergency')


@pytest.mark.parametrize('lang',['es','en','pt'])
def test_free_calculators_create_no_reports_and_pro_views_are_locked(lang,monkeypatch):
    def fail(*args,**kwargs): raise AssertionError('Free must not generate a report/PDF')
    monkeypatch.setattr('clinical_ui.make_report',fail)
    monkeypatch.setattr('clinical_ui.generate_pdf',fail)
    app=start_app(lang,pro=False)
    app.session_state['plan']='pro'  # A client-facing choice cannot confer server permission.
    for module in ['framingham','euroscore','chads','grace','timi','bmi','ckd']:
        app.selectbox(key='score').set_value(module).run()
        app.button(key=f'calculate:{module}').click().run()
        assert not app.exception
        assert app.success
        saved=app.session_state[f'calculation:{module}']
        assert 'pdf' not in saved and 'report' not in saved
    assert not any(x.key=='calculate:ecg' for x in app.button)
    for mode in ['emergency','outpatient']:
        app.radio(key='workspace').set_value(mode).run()
        assert not app.exception
        assert '_clinical_case' not in app.session_state
        assert translations[lang]['pro_required'] in [x.value for x in app.info]


@pytest.mark.parametrize('lang',['es','en','pt'])
def test_both_modes_share_draft_and_confirmed_case_without_double_entry(lang):
    app=start_app(lang)
    app.radio(key='workspace').set_value('emergency').run()
    assert not app.exception
    prefix=case_keys(app)
    # No clinical numbers or false antecedents are prefilled.
    assert app.text_input(key=prefix+'age').value==''
    assert app.selectbox(key=prefix+'hypertension').value=='unknown'
    app.text_input(key=prefix+'age').set_value('65')
    app.text_input(key=prefix+'creatinine').set_value('0,85')
    app.selectbox(key=prefix+'hypertension').set_value('absent')
    app.text_area(key=prefix+'chief_complaint').set_value('TEST consultation reason')
    app.run()
    assert not app.exception
    app.radio(key='workspace').set_value('outpatient').run()
    assert app.text_input(key=prefix+'age').value=='65'
    assert app.text_area(key=prefix+'chief_complaint').value=='TEST consultation reason'
    app.checkbox(key=prefix+'review').check().run()
    app.button(key=prefix+'save').click().run()
    assert not app.exception
    case=app.session_state['_clinical_case']
    assert case.mode=='outpatient' and case.review_state=='reviewed'
    assert case.facts['creatinine'].value==.85
    assert case.facts['hypertension'].value is False
    assert case.facts['diabetes'].value is None
    # Leaving this view deletes widgets; the stored draft restores their values.
    app.radio(key='workspace').set_value('tools_nav').run()
    app.radio(key='workspace').set_value('outpatient').run()
    assert app.text_input(key=prefix+'age').value=='65'
    app.text_input(key=prefix+'age').set_value('66').run()
    assert app.checkbox(key=prefix+'review').value is False
    app.button(key=prefix+'save').click().run()
    assert app.session_state['_clinical_case'].review_state=='draft'
    assert app.session_state['_clinical_case'].revision==case.revision+1


def test_case_survives_language_change_and_new_case_clears_patient_data():
    app=start_app()
    app.radio(key='workspace').set_value('emergency').run()
    prefix=case_keys(app);old_id=app.session_state['_clinical_case'].case_id
    app.text_area(key=prefix+'medication').set_value('TEST medication').run()
    app.selectbox(key='language').set_value('pt').run()
    assert not app.exception
    assert app.text_area(key=prefix+'medication').value=='TEST medication'
    app.button(key='case:new').click().run()
    assert not app.exception
    assert app.session_state['_clinical_case'].case_id!=old_id
    assert not app.session_state['_clinical_case'].facts
    assert app.text_area(key=case_keys(app)+'medication').value==''


def test_logout_and_revocation_purge_pro_case_and_pdf(pro_context,monkeypatch):
    app=start_app()
    app.button(key='calculate:framingham').click().run()
    assert 'pdf' in app.session_state['calculation:framingham']
    app.radio(key='workspace').set_value('emergency').run()
    assert '_clinical_case' in app.session_state
    app.button(key='access:logout').click().run()
    assert not app.exception
    assert '_clinical_case' not in app.session_state
    assert 'calculation:framingham' not in app.session_state
    assert app.session_state['_access_context'].plan=='free'
    app.text_input(key='access:code').set_value(TEST_CODE).run()
    app.button(key='access:login').click().run()
    app.radio(key='workspace').set_value('emergency').run()
    assert '_clinical_case' in app.session_state
    monkeypatch.setenv('CARDIOAPP_PRO_INVITES','{}')
    app.run()
    assert not app.exception
    assert '_clinical_case' not in app.session_state
    assert app.session_state['_access_context'].plan=='free'


def test_case_interchange_preserves_unknown_and_explicit_absence(pro_context):
    from clinical_case import case_data
    case=create_case(pro_context);values=raw_values(case);values['hypertension']='absent'
    case=save_case(pro_context,case,values,mode='emergency',confirmed=True)
    payload=json.loads(json.dumps(case_data(pro_context,case)))
    assert payload['schema_version']==SCHEMA_VERSION
    assert payload['facts']['hypertension']['value'] is False
    assert payload['facts']['diabetes']['value'] is None
    with pytest.raises(AccessDenied): case_data(anonymous_access(),case)


def test_pdf_traceability_metadata_is_exported(pro_context):
    app=start_app()
    app.button(key='calculate:framingham').click().run()
    saved=app.session_state['calculation:framingham']
    assert saved['algorithm_id']=='framingham' and saved['algorithm_version']=='2026.10.11'
    metadata=json.loads(PdfReader(BytesIO(saved['pdf'])).metadata.subject)
    assert metadata['input_hash']==saved['fingerprint']
    assert metadata['template_version']=='1.1' and metadata['report_version']==1


@pytest.mark.parametrize('lang',['fr','it','de','ar'])
def test_secondary_languages_keep_new_case_screens_functional(lang):
    app=start_app(lang)
    for mode in ['emergency','outpatient']:
        app.radio(key='workspace').set_value(mode).run()
        assert not app.exception
        assert app.text_input(key=case_keys(app)+'age').value==''


def test_forged_session_access_fails_closed_without_crashing():
    app=start_app(pro=False)
    app.session_state['_access_context']={'plan':'pro','verified':True}
    app.radio(key='workspace').set_value('emergency').run()
    assert not app.exception
    assert app.session_state['_access_context'].plan=='free'
    assert '_clinical_case' not in app.session_state


def test_revocation_during_export_returns_to_free_without_error(monkeypatch):
    import clinical_ui
    app=start_app()
    original=clinical_ui.calculation_pdf
    def revoke(context,saved,t):
        monkeypatch.setenv('CARDIOAPP_PRO_INVITES','{}')
        return original(context,saved,t)
    monkeypatch.setattr(clinical_ui,'calculation_pdf',revoke)
    app.button(key='calculate:framingham').click().run()
    assert not app.exception
    assert app.session_state['_access_context'].plan=='free'
    assert 'calculation:framingham' not in app.session_state
