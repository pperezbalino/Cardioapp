"""Source fixtures and UI boundaries for the two independent score changes."""
import pytest

import calculations as calc
from translations import LANGUAGES, translations
from test_ui_and_reports import start_app


@pytest.mark.parametrize('score,risk', [
    (0, '≤0.2%'), (60, '≤0.2%'), (70, '0.3%'), (80, '0.4%'),
    (90, '0.6%'), (100, '0.8%'), (110, '1.1%'), (120, '1.6%'),
    (130, '2.1%'), (140, '2.9%'), (150, '3.9%'), (160, '5.4%'),
    (170, '7.3%'), (180, '9.8%'), (190, '13%'), (200, '18%'),
    (210, '23%'), (220, '29%'), (230, '36%'), (240, '44%'),
    (250, '≥52%'), (372, '≥52%'), (61, '0.2–0.3%'),
    (108, '0.8–1.1%'), (122, '1.6–2.1%'), (249, '44–52%'),
])
def test_grace_figure4_mortality_readout(score, risk):
    assert calc.grace_mortality(score) == risk


@pytest.mark.parametrize('value', [-1, 373, 122.5, 122.0, True, None, '122', float('nan')])
def test_grace_readout_rejects_invalid_points(value):
    with pytest.raises(ValueError):
        calc.grace_mortality(value)


def test_grace_assessment_retains_original_numeric_fixture():
    assert calc.grace_assessment(age=65, heart_rate=85, sbp=120, creatinine=1.1,
                                 biomarkers=True) == {'points': 122, 'hospital_mortality': '1.6–2.1%'}


def test_has_bled_esc2020_boundaries_and_independent_components():
    assert calc.has_bled(65, 160) == (0, 'bleed_not_high')
    assert calc.has_bled(66, 160)[0] == 1
    assert calc.has_bled(65, 161)[0] == 1
    assert calc.has_bled(65, 160, extreme_frailty=True)[0] == 1
    assert calc.has_bled(66, 160, extreme_frailty=True)[0] == 1
    assert calc.has_bled(40, 120, renal_dysfunction=True, liver_dysfunction=True) == (2, 'bleed_not_high')
    assert calc.has_bled(40, 120, bleeding_drugs=True, alcohol_excess=True)[0] == 2
    assert calc.has_bled(66, 161, renal_dysfunction=True)[1] == 'bleed_high'
    assert calc.has_bled(66, 161, renal_dysfunction=True, liver_dysfunction=True,
                         prior_stroke=True, bleeding_history=True, on_vka=True,
                         labile_inr=True, extreme_frailty=True, bleeding_drugs=True,
                         alcohol_excess=True) == (9, 'bleed_high')


@pytest.mark.parametrize('field', ['renal_dysfunction', 'liver_dysfunction', 'prior_stroke',
                                  'bleeding_history', 'on_vka', 'labile_inr', 'extreme_frailty',
                                  'bleeding_drugs', 'alcohol_excess'])
def test_has_bled_no_truthy_strings_or_missing_flags(field):
    with pytest.raises(ValueError):
        calc.has_bled(65, 160, **{field: 'unknown'})


def test_has_bled_labile_inr_requires_vka():
    with pytest.raises(ValueError, match='labile_inr_requires_vka'):
        calc.has_bled(40, 120, labile_inr=True)
    assert calc.has_bled(40, 120, on_vka=True, labile_inr=True)[0] == 1
    assert calc.has_bled(40, 120, on_vka=True)[0] == 0


@pytest.mark.parametrize('lang', LANGUAGES)
def test_new_scores_are_free_and_translated_without_reports(lang):
    app = start_app(lang, pro=False)
    t = translations[lang]
    assert t['has_bled'] in app.selectbox(key='score').options
    app.selectbox(key='score').set_value('grace').run()
    app.checkbox(key='grace:biomarkers').check().run()
    app.button(key='calculate:grace').click().run()
    assert not app.exception
    saved = app.session_state['calculation:grace']
    assert saved['results'] == [(t['points'], '122'), (t['hospital_mortality'], '1.6–2.1%')]
    assert 'pdf' not in saved and 'report' not in saved
    app.number_input(key='grace:age').set_value(70).run()
    assert 'calculation:grace' not in app.session_state
    app.selectbox(key='score').set_value('has_bled').run()
    app.button(key='calculate:has_bled').click().run()
    assert app.error[0].value == t['has_bled_review_required']
    assert 'calculation:has_bled' not in app.session_state
    app.checkbox(key='has_bled:renal_dysfunction').check()
    app.checkbox(key='has_bled:liver_dysfunction').check()
    app.number_input(key='has_bled:sbp').set_value(161)
    app.checkbox(key='has_bled:has_bled_reviewed').check().run()
    app.button(key='calculate:has_bled').click().run()
    assert not app.exception
    saved = app.session_state['calculation:has_bled']
    assert saved['results'] == [(t['has_bled'], '3'), (t['bleeding_risk'], t['bleed_high'])]
    assert 'pdf' not in saved and 'report' not in saved
    assert len(app.success) == 2
    app.number_input(key='has_bled:sbp').set_value(160).run()
    assert 'calculation:has_bled' not in app.session_state


def test_vka_deselection_clears_labile_inr_and_result():
    app = start_app(pro=False)
    app.selectbox(key='score').set_value('has_bled').run()
    app.checkbox(key='has_bled:on_vka').check().run()
    app.checkbox(key='has_bled:labile_inr').check()
    app.checkbox(key='has_bled:has_bled_reviewed').check().run()
    app.button(key='calculate:has_bled').click().run()
    assert app.session_state['calculation:has_bled']['results'][0][1] == '1'
    app.checkbox(key='has_bled:on_vka').uncheck().run()
    assert not app.exception
    assert 'calculation:has_bled' not in app.session_state
    assert not any(x.key == 'has_bled:labile_inr' for x in app.checkbox)
    app.button(key='calculate:has_bled').click().run()
    assert app.session_state['calculation:has_bled']['results'][0][1] == '0'
