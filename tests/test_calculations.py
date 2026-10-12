import math
import pytest
import calculations as c


def test_framingham_negative_points_and_bounds():
    assert c.framingham(35, 'M', 150, 65, 110) == {'points': -5, 'risk': '<1'}
    assert c.framingham(30, 'F', 150, 65, 110) == {'points': -8, 'risk': '<1'}
    assert c.framingham(79, 'M', 300, 30, 180, smoker=True, treated=True)['risk'] == '≥30'
    assert c.framingham(79, 'F', 300, 30, 180, smoker=True, treated=True)['risk'] == '≥30'


def test_framingham_published_point_tables():
    # Men 55: age 8 + cholesterol 3 + HDL 0 + untreated SBP 1 = 12 -> 10%.
    assert c.framingham(55, 'M', 220, 50, 130) == {'points': 12, 'risk': '10'}
    # Women 55: age 8 + cholesterol 4 + HDL 0 + untreated SBP 2 = 14 -> 2%.
    assert c.framingham(55, 'F', 220, 50, 130) == {'points': 14, 'risk': '2'}
    # Younger men get age-specific cholesterol points, not the old fixed 1-4.
    assert c.framingham(40, 'M', 280, 50, 110, smoker=True) == {'points': 13, 'risk': '12'}


@pytest.mark.parametrize('flag', ['diabetes', 'vascular_disease'])
def test_framingham_exclusions(flag):
    with pytest.raises(ValueError, match='framingham_ineligible'):
        c.framingham(55, 'M', 220, 50, 130, **{flag: True})


def test_euroscore_baseline_and_age_transform():
    # Published intercept and age transform: ≤60 has x_age=1.
    expected = 100 / (1 + math.exp(5.324537 - .0285181))
    assert c.euroscore(60, 'M') == pytest.approx(expected)
    assert c.euroscore(18, 'M') == pytest.approx(expected)
    assert c.euroscore(65, 'M') == pytest.approx(0.574634476973, rel=1e-8)
    assert c.euroscore(61, 'M') > c.euroscore(60, 'M')


def test_euroscore_all_lv_and_urgency_categories():
    lv = [c.euroscore(65, 'M', lv=x) for x in ['good', 'moderate', 'poor', 'very_poor']]
    assert all(a < b for a, b in zip(lv, lv[1:]))
    urgency = [c.euroscore(65, 'M', urgency=x) for x in ['elective', 'urgent', 'emergency', 'salvage']]
    assert all(a < b for a, b in zip(urgency, urgency[1:]))
    # Independent Table 6 sum for a multivariable fixture.
    expected_logit = -5.324537 + .0285181 * 11 + .2196434 + .303553 + .2958358 + .8084096 + .1788899 + .3174673 + .5521478 + .3542749 + 1.118599
    assert c.euroscore(70, 'F', renal='moderate', nyha=3, lv='poor', pulmonary='moderate',
                       urgency='urgent', procedure='two', insulin=True, previous_surgery=True) == pytest.approx(100/(1+math.exp(-expected_logit)))


@pytest.mark.parametrize('factor', list(c.EURO_COEFFICIENTS))
def test_euroscore_each_binary_factor(factor):
    assert c.euroscore(65, 'M', **{factor: True}) > c.euroscore(65, 'M')


def test_renal_clearance_boundaries():
    assert c.cockcroft_gault(65, 'M', 72, 1) == 75
    assert c.cockcroft_gault(65, 'F', 72, 1) == 63.75
    assert [c.renal_category(x) for x in [50, 50.01, 85, 85.01]] == ['severe', 'moderate', 'moderate', 'normal']
    assert c.renal_category(0, dialysis=True) == 'dialysis'


def test_chads_sex_alone_and_thresholds():
    assert c.chads_vasc(40, 'M') == (0, 'af_low')
    assert c.chads_vasc(40, 'F') == (1, 'af_low')
    assert c.chads_vasc(65, 'F') == (2, 'af_consider')
    assert c.chads_vasc(75, 'M') == (2, 'af_recommended')
    assert c.chads_vasc(80, 'F', True, True, True, True, True) == (9, 'af_recommended')


def test_timi_seventh_variable_and_endpoint():
    assert c.timi(40) == (0, 5)
    assert c.timi(40, known_cad=True) == (1, 5)
    assert c.timi(65, True, True, True, True, True, True) == (7, 41)


def test_grace_published_nomogram_fixtures():
    # Age 58 + HR 9 + SBP 34 + creat 7 + positive markers 14 = 122.
    assert c.grace(65, 85, 120, 1.1, biomarkers=True) == 122
    assert c.grace(25, 40, 210, .3) == 1
    assert c.grace(95, 210, 70, 4.5, 4, True, True, True) == 372
    assert c.grace(90, 200, 160, 3.99) == 177
    assert c.grace(90, 200, 160, 4) == 184


@pytest.mark.parametrize('age,sex,creatinine,expected', [
    (60,'M',1,86.162620779669), (60,'F',1,64.495000353945),
    (40,'M',.9,110.725599603555), (40,'F',.7,112.054306798798),
])
def test_ckd_epi_2021_reference_values(age, sex, creatinine, expected):
    assert c.ckd_epi(age, creatinine, sex) == pytest.approx(expected, rel=1e-9)


@pytest.mark.parametrize('weight,height,category', [(50,180,'bmi_underweight'), (70,170,'bmi_normal'),
                                                   (80,170,'bmi_overweight'), (100,170,'bmi_obese')])
def test_bmi_categories(weight, height, category):
    assert c.bmi(weight, height)[1] == category


def test_infusion_dimensional_fixtures():
    # 0.1 mcg/kg/min × 70kg = 7 mcg/min; 4mg/250mL = 16mcg/mL -> 26.25mL/h.
    result = c.infusion(.1, 'mcg/kg/min', 4, 250, 70)
    assert result['ml_h'] == pytest.approx(26.25)
    assert result['mg_min'] == pytest.approx(.007)
    # Fixed mg/min does NOT multiply by weight.
    assert c.infusion(1, 'mg/min', 1000, 250, 70)['ml_h'] == 15
    assert c.infusion(1, 'mg/min', 1000, 250, 140)['ml_h'] == 15
    assert c.infusion(.5, 'mg/min', 900, 500)['ml_h'] == pytest.approx(16.6666666667)
    assert c.infusion(10, 'mcg/min', 50, 250)['ml_h'] == pytest.approx(3)


@pytest.mark.parametrize('dose,amount,volume,weight', [(0,4,250,70),(.1,0,250,70),(.1,4,0,70),(.1,4,250,0),
                                                      (float('nan'),4,250,70),(float('inf'),4,250,70)])
def test_infusion_rejects_invalid_values(dose, amount, volume, weight):
    with pytest.raises(ValueError): c.infusion(dose, 'mcg/kg/min', amount, volume, weight)


@pytest.mark.parametrize('function,args', [(c.ckd_epi,(17,1,'M')), (c.ckd_epi,(60,0,'M')),
                                          (c.ckd_epi,(60,1,'other')), (c.framingham,(80,'M',200,50,120)),
                                          (c.bmi,(70,0)), (c.euroscore,(float('nan'),'M'))])
def test_validation(function, args):
    with pytest.raises(ValueError): function(*args)
