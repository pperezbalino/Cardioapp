"""Pro-only ECG reference: published thresholds, no patient inference/mutation."""
from dataclasses import replace
import pytest

from access import AccessDenied, anonymous_access
from ecg_criteria import render_stemi_ecg_reference, THRESHOLDS
from translations import LANGUAGES, translations
from test_ui_and_reports import start_app


def test_aha2025_table3_ecg_thresholds_and_units():
    # Independent published fixtures: non-V2/V3 1 mm, male >=40 2 mm,
    # male <40 2.5 mm, all women 1.5 mm (each at standard 10 mm/mV).
    assert [(row[1], row[2]) for row in THRESHOLDS] == [
        ('ecg_any_population', '≥1 mm (≥0.10 mV)'),
        ('ecg_male_40_plus', '≥2 mm (≥0.20 mV)'),
        ('ecg_male_under_40', '≥2.5 mm (≥0.25 mV)'),
        ('ecg_female_any_age', '≥1.5 mm (≥0.15 mV)'),
    ]


def test_reference_service_denies_free_and_forged_pro(pro_context):
    free = anonymous_access()
    for context in (None, free, replace(free, plan='pro', subject='test-doctor')):
        with pytest.raises(AccessDenied):
            render_stemi_ecg_reference(context, translations['es'])


@pytest.mark.parametrize('lang', LANGUAGES)
def test_reference_visible_before_diagnosis_and_does_not_change_case(lang):
    app = start_app(lang)
    app.radio(key='workspace').set_value('emergency').run()
    assert not app.exception
    t = translations[lang]
    case = app.session_state['_clinical_case']
    draft = app.session_state['_clinical_draft']
    assert draft['raw']['acs_context'] == 'unknown'
    assert 'acs_context' not in case.facts
    assert len(app.table) == 1
    table = app.table[0].value
    assert list(table.columns) == [t['ecg_leads_column'], t['ecg_population_column'], t['ecg_threshold_column']]
    assert table[t['ecg_threshold_column']].tolist() == [
        '≥1 mm (≥0.10 mV)', '≥2 mm (≥0.20 mV)',
        '≥2.5 mm (≥0.25 mV)', '≥1.5 mm (≥0.15 mV)']
    assert t['ecg_complex_context'] in [x.value for x in app.warning]
    assert t['ecg_posterior'] in [x.value for x in app.markdown]
    assert t['ecg_block'] in [x.value for x in app.markdown]
    assert 'ecg_reviewed' not in case.facts
    app.radio(key='workspace').set_value('outpatient').run()
    assert not app.exception
    assert len(app.table) == 0


@pytest.mark.parametrize('lang', LANGUAGES)
def test_reference_not_exposed_to_free(lang):
    app = start_app(lang, pro=False)
    app.radio(key='workspace').set_value('emergency').run()
    assert not app.exception
    assert len(app.table) == 0
    assert translations[lang]['pro_required'] in [x.value for x in app.info]
    assert '_clinical_case' not in app.session_state
