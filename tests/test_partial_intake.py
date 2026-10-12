"""Current valid data remain usable despite unrelated missing/invalid inputs."""
import pytest
from clinical_case import create_case, raw_values, usable_inputs, save_case
from integrated_engine import evaluate
from translations import LANGUAGES, translations
from test_ui_and_reports import start_app


def test_invalid_current_value_is_unknown_not_previous_patient_fact(pro_context):
    case = create_case(pro_context)
    values = raw_values(case)
    values.update(age='54', weight='80', height='180')
    case = save_case(pro_context, case, values, mode='emergency', confirmed=True)
    current = raw_values(case)
    current['age'] = 'mal escrito'
    usable, alias, pending = usable_inputs(pro_context, case, current, 'Paciente 1')
    preview = save_case(pro_context, case, usable, mode='emergency', alias=alias, confirmed=True)
    assert preview.facts['age'].value is None
    assert case.facts['age'].value == 54
    assert pending == ('age',)
    assert alias == 'Paciente 1'
    assert {s.algorithm_id: s for s in evaluate(pro_context, preview)}['bmi'].status == 'ready'
    assert not preview.facts['diabetes'].confirmed


@pytest.mark.parametrize('lang', LANGUAGES)
def test_partial_form_evaluates_before_save_and_invalid_alias_does_not_block(lang):
    app = start_app(lang)
    app.radio(key='workspace').set_value('emergency').run()
    case = app.session_state['_clinical_case']
    p = 'case:' + case.case_id + ':'
    app.text_input(key=p+'alias').set_value('Paciente 1')
    app.text_input(key=p+'weight').set_value('80')
    app.text_input(key=p+'height').set_value('180')
    app.text_input(key=p+'age').set_value('no es número')
    app.run()
    assert not app.exception
    assert not app.error
    assert any('24.69' in x.value for x in app.markdown)
    # Automatic assessment never silently confirms the canonical report snapshot.
    assert app.session_state['_clinical_case'].revision == 0
    app.checkbox(key=p+'review').check().run()
    app.button(key=p+'save').click().run()
    assert not app.exception and not app.error
    saved = app.session_state['_clinical_case']
    assert saved.facts['age'].value is None
    assert saved.facts['weight'].value == 80
    assert saved.alias == 'Paciente 1'
    assert translations[lang]['case_saved'] in [x.value for x in app.success]
