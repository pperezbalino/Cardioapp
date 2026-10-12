import pytest
from dataclasses import replace
from drug_references import get_reference, reference_rates, profiles, outside_reference, VERSION, PRO_DRUGS
from access import AccessDenied, Feature, allows, anonymous_access
from calculations import DRUG_UNITS
from test_ui_and_reports import start_app
from translations import translations, LANGUAGES


def test_named_reference_values_and_coverage(pro_context):
    expected={'adrenaline_ahf_esc2021':(.05,.5,'mcg/kg/min'),
              'adrenaline_brady_aha2025':(2,10,'mcg/min'),
              'noradrenaline_ahf_esc2021':(.2,1,'mcg/kg/min'),
              'dobutamine_ahf_esc2021':(2,20,'mcg/kg/min'),
              'levosimendan_ahf_esc2021':(.05,.2,'mcg/kg/min'),
              'lidocaine_vt_esc2022':(2,4,'mg/min'),
              'amiodarone_wide_aha2025':(1,1,'mg/min'),
              'nitroglycerin_acs_aha2025':(10,None,'mcg/min')}
    for drug in PRO_DRUGS:
        for profile in profiles(drug,context=pro_context):
            ref=get_reference(drug,profile,context=pro_context)
            assert (ref.low,ref.high,ref.unit)==expected[profile]
            assert 'http' in ref.source
    with pytest.raises(ValueError):get_reference('adrenaline','lidocaine_vt_esc2022',context=pro_context)


def test_reference_rates_preserve_weight_and_fixed_units(pro_context):
    adr=get_reference('adrenaline','adrenaline_ahf_esc2021',context=pro_context)
    rates=reference_rates(adr,4,250,70,context=pro_context)
    assert rates==pytest.approx({'reference_low_ml_h':13.125,'reference_high_ml_h':131.25})
    brady=get_reference('adrenaline','adrenaline_brady_aha2025',context=pro_context)
    assert reference_rates(brady,4,250,70,context=pro_context)==reference_rates(brady,4,250,140,context=pro_context)
    lido=get_reference('lidocaine','lidocaine_vt_esc2022',context=pro_context)
    assert reference_rates(lido,1000,250,70,context=pro_context)=={'reference_low_ml_h':30,'reference_high_ml_h':60}


def test_ntg_start_is_not_an_invented_ceiling(pro_context):
    ref=get_reference('nitroglycerin','nitroglycerin_acs_aha2025',context=pro_context)
    assert ref.kind=='start' and ref.high is None
    assert reference_rates(ref,50,250,context=pro_context)==pytest.approx({'reference_low_ml_h':3})
    assert not outside_reference(ref,20,context=pro_context)
    assert not outside_reference(ref,5,context=pro_context)
    with pytest.raises(ValueError):reference_rates(ref,0,250,context=pro_context)


@pytest.mark.parametrize('dose,outside',[(.049,True),(.05,False),(.5,False),(.501,True)])
def test_interval_boundaries_not_universal_safety_limits(dose,outside,pro_context):
    ref=get_reference('adrenaline','adrenaline_ahf_esc2021',context=pro_context)
    assert outside_reference(ref,dose,context=pro_context) is outside


@pytest.mark.parametrize('lang',LANGUAGES)
def test_all_references_are_pro_only(lang):
    app=start_app(lang,pro=True);t=translations[lang];ctx=app.session_state['_access_context']
    for drug in PRO_DRUGS:
        app.selectbox(key='drugs:select_drug').set_value(drug).run()
        assert not app.exception
        assert any(t['drug_reference'] in x.value for x in app.info)
        assert not app.number_input(key='drugs:dose:'+drug).value
        ref=get_reference(drug,profiles(drug,context=ctx)[0],context=ctx)
        app.number_input(key='drugs:dose:'+drug).set_value(float(ref.low))
        app.number_input(key='drugs:total_mg').set_value(50.0)
        app.number_input(key='drugs:final_ml').set_value(250.0)
        app.button(key='calculate:drugs').click().run()
        assert not app.exception and app.success
        saved=app.session_state['calculation:drugs']
        assert saved['reference_profile_id']==ref.profile_id and saved['reference_version']==VERSION
        assert 'pdf' in saved
        assert saved['report']['drug_reference_id']==ref.profile_id
        assert any(label==t['drug_reference_rate'] for label,value in saved['results'])


@pytest.mark.parametrize('lang',LANGUAGES)
def test_free_retains_original_conversion_with_no_reference_service(lang,monkeypatch):
    def fail(*args,**kwargs):raise AssertionError('Free cannot use dose-reference services')
    for name in ['get_reference','profiles','reference_rates','outside_reference']:
        monkeypatch.setattr('clinical_ui.'+name,fail)
    app=start_app(lang,pro=False);t=translations[lang]
    assert tuple(app.selectbox(key='drugs:select_drug').options)==tuple(t[d] for d in DRUG_UNITS)
    assert translations[lang]['nitroglycerin'] not in app.selectbox(key='drugs:select_drug').options
    assert not any(x.key and x.key.startswith('drugs:drug_context:') for x in app.selectbox)
    for drug,unit in DRUG_UNITS.items():
        app.selectbox(key='drugs:select_drug').set_value(drug).run()
        assert not app.exception
        app.number_input(key='drugs:dose:'+drug).set_value(.1 if unit=='mcg/kg/min' else 1.0)
        app.number_input(key='drugs:total_mg').set_value(50.0)
        app.number_input(key='drugs:final_ml').set_value(250.0)
        app.button(key='calculate:drugs').click().run()
        assert not app.exception and app.success
        saved=app.session_state['calculation:drugs']
        assert len(saved['results'])==3
        assert not any(k.startswith('reference_') for k in saved)
        assert 'pdf' not in saved and 'report' not in saved
        assert saved['note']==t['infusion_note']
        assert not any(t['drug_reference'] in str(x.value) for x in app.info)
        assert not any(t['drug_outside_reference']==x.value for x in app.warning)


def test_indication_change_resets_dose_and_units_without_weight_carryover():
    app=start_app(pro=True)
    app.number_input(key='drugs:dose:adrenaline').set_value(.1).run()
    app.selectbox(key='drugs:drug_context:adrenaline').set_value('adrenaline_brady_aha2025').run()
    assert not app.exception
    assert app.number_input(key='drugs:dose:adrenaline').value==0
    assert not any(x.key=='drugs:weight' for x in app.number_input)
    assert 'mcg/min' in app.number_input(key='drugs:dose:adrenaline').label
    app.number_input(key='drugs:dose:adrenaline').set_value(2.0)
    app.number_input(key='drugs:total_mg').set_value(4.0)
    app.number_input(key='drugs:final_ml').set_value(250.0)
    app.button(key='calculate:drugs').click().run()
    assert app.session_state['calculation:drugs']['results'][0][1]=='7.5 mL/h'
    app.selectbox(key='drugs:drug_context:adrenaline').set_value('adrenaline_ahf_esc2021').run()
    assert app.number_input(key='drugs:dose:adrenaline').value==0


def test_outside_reference_notice_survives_rerun_without_blocking_conversion():
    app=start_app(pro=True);app.selectbox(key='drugs:select_drug').set_value('lidocaine').run()
    app.number_input(key='drugs:dose:lidocaine').set_value(1.0)
    app.number_input(key='drugs:total_mg').set_value(1000.0)
    app.number_input(key='drugs:final_ml').set_value(250.0)
    app.button(key='calculate:drugs').click().run()
    assert app.success and app.warning
    app.run();assert app.warning
    assert app.session_state['calculation:drugs']['results'][0][1]=='15 mL/h'


def test_reference_service_requires_real_pro_entitlement(pro_context,monkeypatch):
    free=anonymous_access();ref=get_reference('lidocaine','lidocaine_vt_esc2022',context=pro_context)
    assert allows(pro_context,Feature.DOSE_REFERENCE) and not allows(free,Feature.DOSE_REFERENCE)
    for ctx in [None,free,replace(free,plan='pro')]:
        for action in [lambda:profiles('lidocaine',context=ctx),
                       lambda:get_reference('lidocaine',ref.profile_id,context=ctx),
                       lambda:reference_rates(ref,50,250,context=ctx),
                       lambda:outside_reference(ref,3,context=ctx)]:
            with pytest.raises(AccessDenied):action()
    monkeypatch.setenv('CARDIOAPP_PRO_INVITES','{}')
    with pytest.raises(AccessDenied):reference_rates(ref,50,250,context=pro_context)


def test_revocation_removes_reference_widgets_and_cached_reference_results(monkeypatch):
    app=start_app(pro=True)
    app.selectbox(key='drugs:select_drug').set_value('nitroglycerin').run()
    app.number_input(key='drugs:dose:nitroglycerin').set_value(10.0)
    app.number_input(key='drugs:total_mg').set_value(50.0)
    app.number_input(key='drugs:final_ml').set_value(250.0)
    app.button(key='calculate:drugs').click().run()
    assert 'reference_profile_id' in app.session_state['calculation:drugs']
    monkeypatch.setenv('CARDIOAPP_PRO_INVITES','{}');app.run()
    assert not app.exception and app.session_state['_access_context'].plan=='free'
    assert 'calculation:drugs' not in app.session_state
    assert not any(x.key and x.key.startswith('drugs:drug_context:') for x in app.selectbox)
    assert 'nitroglycerin' not in app.selectbox(key='drugs:select_drug').options
