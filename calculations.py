"""Clinical arithmetic, independent of UI and language. See SOURCES.md."""
from bisect import bisect_right
import math


def number(value, low, high, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(name)
    if not math.isfinite(value) or not low <= value <= high:
        raise ValueError(name)
    return value


def sex_code(sex):
    if sex not in ('M', 'F'):
        raise ValueError('sex')
    return sex


def band(value, boundaries, points):
    return points[bisect_right(boundaries, value)]


def framingham(age, sex, total_chol, hdl, sbp, smoker=False,
               treated=False, diabetes=False, vascular_disease=False):
    """ATP III hard CHD point model; not applicable to diabetes or established disease."""
    number(age, 30, 79, 'age')
    sex_code(sex)
    number(total_chol, 1, 1000, 'total_chol')
    number(hdl, 1, 200, 'hdl')
    if hdl > total_chol:
        raise ValueError('hdl')
    number(sbp, 1, 350, 'sbp')
    if diabetes or vascular_disease:
        raise ValueError('framingham_ineligible')
    male = sex == 'M'
    points = band(age, [35, 40, 45, 50, 55, 60, 65, 70, 75],
                  [-9, -4, 0, 3, 6, 8, 10, 11, 12, 13] if male
                  else [-7, -3, 0, 3, 6, 8, 10, 12, 14, 16])
    age_column = band(age, [40, 50, 60, 70], [0, 1, 2, 3, 4])
    chol_row = band(total_chol, [160, 200, 240, 280], [0, 1, 2, 3, 4])
    chol_points = ([[0, 0, 0, 0, 0], [4, 3, 2, 1, 0], [7, 5, 3, 1, 0],
                    [9, 6, 4, 2, 1], [11, 8, 5, 3, 1]] if male else
                   [[0, 0, 0, 0, 0], [4, 3, 2, 1, 1], [8, 6, 4, 2, 1],
                    [11, 8, 5, 3, 2], [13, 10, 7, 4, 2]])
    points += chol_points[chol_row][age_column]
    if smoker:
        points += ([8, 5, 3, 1, 1] if male else [9, 7, 4, 2, 1])[age_column]
    points += band(hdl, [40, 50, 60], [2, 1, 0, -1])
    bp_points = ([0, 1, 2, 2, 3] if treated else [0, 0, 1, 1, 2]) if male else (
        [0, 3, 4, 5, 6] if treated else [0, 1, 2, 3, 4])
    points += band(sbp, [120, 130, 140, 160], bp_points)
    if male:
        risks = [1, 1, 1, 1, 1, 2, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 25]
        risk = '<1' if points < 0 else '≥30' if points >= 17 else str(risks[points])
    else:
        risks = [1, 1, 1, 1, 2, 2, 3, 4, 5, 6, 8, 11, 14, 17, 22, 27]
        risk = '<1' if points < 9 else '≥30' if points >= 25 else str(risks[points - 9])
    return {'points': points, 'risk': risk}


EURO_COEFFICIENTS = {
    'extracardiac': .5360268, 'poor_mobility': .2407181,
    'previous_surgery': 1.118599, 'lung_disease': .1886564,
    'endocarditis': .6194522, 'critical': 1.086517,
    'insulin': .3542749, 'ccs4': .2226147,
    'recent_mi': .1528943, 'thoracic_aorta': .6527205,
}
EURO_CATEGORIES = {
    'renal': {'normal': 0, 'moderate': .303553, 'severe': .8592256, 'dialysis': .6421508},
    'nyha': {1: 0, 2: .1070545, 3: .2958358, 4: .5597929},
    'lv': {'good': 0, 'moderate': .3150652, 'poor': .8084096, 'very_poor': .9346919},
    'pulmonary': {'normal': 0, 'moderate': .1788899, 'severe': .3491475},
    'urgency': {'elective': 0, 'urgent': .3174673, 'emergency': .7039121, 'salvage': 1.362947},
    'procedure': {'cabg': 0, 'single': .0062118, 'two': .5521478, 'three': .9724533},
}


def euroscore(age, sex, renal='normal', nyha=1, lv='good', pulmonary='normal',
              urgency='elective', procedure='cabg', **factors):
    """Nashef 2012 Table 6, predicted in-hospital mortality (%)."""
    number(age, 18, 120, 'age')
    sex_code(sex)
    if set(factors) - EURO_COEFFICIENTS.keys():
        raise ValueError('unknown_factor')
    logit = -5.324537 + .0285181 * max(1, age - 59) + (.2196434 if sex == 'F' else 0)
    categories = dict(renal=renal, nyha=nyha, lv=lv, pulmonary=pulmonary,
                      urgency=urgency, procedure=procedure)
    for key, value in categories.items():
        if value not in EURO_CATEGORIES[key]:
            raise ValueError(key)
        logit += EURO_CATEGORIES[key][value]
    for key, coefficient in EURO_COEFFICIENTS.items():
        flag = factors.get(key, False)
        if not isinstance(flag, bool):
            raise ValueError(key)
        logit += coefficient * flag
    return 100 / (1 + math.exp(-logit))


def cockcroft_gault(age, sex, weight, creatinine):
    number(age, 18, 120, 'age'); sex_code(sex)
    number(weight, .1, 500, 'weight'); number(creatinine, .01, 30, 'creatinine')
    return (140 - age) * weight / (72 * creatinine) * (.85 if sex == 'F' else 1)


def renal_category(clearance, dialysis=False):
    if dialysis:
        return 'dialysis'
    number(clearance, 0, 1000, 'clearance')
    return 'severe' if clearance <= 50 else 'moderate' if clearance <= 85 else 'normal'


def chads_vasc(age, sex, hypertension=False, diabetes=False, heart_failure=False,
               stroke=False, vascular_disease=False):
    number(age, 18, 120, 'age'); sex_code(sex)
    non_sex = (2 if age >= 75 else 1 if age >= 65 else 0) + sum(
        [bool(hypertension), bool(diabetes), bool(heart_failure), 2 * bool(stroke), bool(vascular_disease)])
    score = non_sex + (sex == 'F')
    # 2023 ACC/AHA: female sex alone does not indicate anticoagulation.
    interpretation = 'af_low' if non_sex == 0 else 'af_consider' if non_sex == 1 else 'af_recommended'
    return score, interpretation


def grace(age, heart_rate, sbp, creatinine, killip=1, arrest=False,
          st_deviation=False, biomarkers=False):
    """Original GRACE 2003 in-hospital discrete nomogram (not GRACE 2.0)."""
    number(age, 18, 120, 'age'); number(heart_rate, 1, 350, 'heart_rate')
    number(sbp, 1, 350, 'sbp'); number(creatinine, .01, 30, 'creatinine')
    if killip not in (1, 2, 3, 4):
        raise ValueError('killip')
    score = band(age, [30, 40, 50, 60, 70, 80, 90], [0, 8, 25, 41, 58, 75, 91, 100])
    score += band(heart_rate, [50, 70, 90, 110, 150, 200], [0, 3, 9, 15, 24, 38, 46])
    score += band(sbp, [80, 100, 120, 140, 160, 200], [58, 53, 43, 34, 24, 10, 0])
    score += band(creatinine, [.4, .8, 1.2, 1.6, 2, 4], [1, 4, 7, 10, 13, 21, 28])
    score += [0, 20, 39, 59][killip - 1] + 39 * bool(arrest) + 28 * bool(st_deviation) + 14 * bool(biomarkers)
    return score


def timi(age, risk_factors=False, known_cad=False, aspirin=False, angina=False,
         st_deviation=False, biomarkers=False):
    number(age, 18, 120, 'age')
    score = int(age >= 65) + sum(bool(x) for x in
        [risk_factors, known_cad, aspirin, angina, st_deviation, biomarkers])
    # 14-day combined endpoint, TIMI Study Group official calculator (rounded %).
    return score, [5, 5, 8, 13, 20, 26, 41, 41][score]


def ckd_epi(age, creatinine, sex):
    """2021 CKD-EPI creatinine, race-free; mL/min/1.73 m², adults only."""
    number(age, 18, 120, 'age'); number(creatinine, .01, 30, 'creatinine'); sex_code(sex)
    k, alpha = (.7, -.241) if sex == 'F' else (.9, -.302)
    ratio = creatinine / k
    return 142 * min(ratio, 1) ** alpha * max(ratio, 1) ** -1.2 * .9938 ** age * (1.012 if sex == 'F' else 1)


def bmi(weight, height):
    number(weight, .1, 500, 'weight'); number(height, 1, 300, 'height')
    value = weight / (height / 100) ** 2
    return value, band(value, [18.5, 25, 30], ['bmi_underweight', 'bmi_normal', 'bmi_overweight', 'bmi_obese'])


DRUG_UNITS = {'adrenaline': 'mcg/kg/min', 'noradrenaline': 'mcg/kg/min',
              'dobutamine': 'mcg/kg/min', 'levosimendan': 'mcg/kg/min',
              'lidocaine': 'mg/min', 'amiodarone': 'mg/min'}


def infusion(dose, unit, total_mg, final_ml, weight=None):
    """Convert prescribed dose and final dilution to pump mL/h; no prescribing."""
    number(dose, .000001, 100000, 'dose')
    number(total_mg, .000001, 100000, 'total_mg')
    number(final_ml, .000001, 100000, 'final_ml')
    if unit == 'mcg/kg/min':
        number(weight, .1, 500, 'weight')
        mg_min = dose * weight / 1000
    elif unit == 'mcg/min':
        mg_min = dose / 1000
    elif unit == 'mg/min':
        mg_min = dose
    else:
        raise ValueError('unit')
    concentration = total_mg / final_ml
    return {'ml_h': mg_min * 60 / concentration, 'mg_min': mg_min,
            'mg_ml': concentration}
