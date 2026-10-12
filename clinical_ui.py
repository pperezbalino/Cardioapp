"""Shared translated widgets, result lifecycle and PDF downloads."""
import hashlib
import json
import streamlit as st

import calculations as calc
from pdf_utils import make_report, generate_pdf

SOURCES = {
    'framingham': ['Framingham ATP III (2001), hard CHD point tables: https://www.framinghamheartstudy.org/fhs-for-researchers/fhs-risk-functions/hard-coronary-heart-disease-10-year-risk/'],
    'euroscore': ['Nashef et al. EuroSCORE II (2012), Table 6: https://doi.org/10.1093/ejcts/ezs043',
                 'Variable definitions: https://www.euroscore.org/index.php?id=17'],
    'chads': ['ACC/AHA/ACCP/HRS AF Guideline (2023), section 6.3.1: https://pmc.ncbi.nlm.nih.gov/articles/PMC11095842/',
              'ESC AF Guideline (2024), CHA2DS2-VA: https://doi.org/10.1093/eurheartj/ehae176'],
    'grace': ['Granger et al. (2003), Figure 4, original in-hospital GRACE nomogram: https://doi.org/10.1001/archinte.163.19.2345'],
    'timi': ['TIMI Study Group, UA/NSTEMI calculator: https://timi.org/calculators/timi-risk-score-calculator-for-ua-nstemi/'],
    'ckd': ['NIDDK, 2021 CKD-EPI creatinine equation: https://www.niddk.nih.gov/research-funding/research-programs/kidney-clinical-research-epidemiology/laboratory/glomerular-filtration-rate-equations/adults'],
    'bmi': ['WHO, adult BMI categories: https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight'],
    'drugs': ['mL/h = dose (mg/min) × 60 ÷ final concentration (mg/mL).',
              'mcg/kg/min → mg/min: dose × weight (kg) ÷ 1000.'],
    'ecg': ['CardioApp: manual clinician-authored report. No automated ECG analysis.'],
}
NOTES = {'framingham': 'framingham_note', 'euroscore': 'euroscore_note', 'chads': 'af_note',
         'grace': 'grace_note', 'timi': 'timi_note', 'ckd': 'ckd_note',
         'drugs': 'infusion_note', 'ecg': 'ecg_note'}


def fingerprint(values, t):
    return hashlib.sha256(json.dumps([t['_lang'], values], sort_keys=True,
                                    ensure_ascii=False).encode()).hexdigest()


def display_value(value, t):
    if isinstance(value, bool):
        return t['yes'] if value else t['no']
    return str(value)


class Fields:
    def __init__(self, module, t):
        self.module, self.t = module, t
        self.values, self.inputs = {}, []

    def key(self, key):
        return f'{self.module}:{key}'

    def add(self, key, value, label, display=None):
        self.values[key] = value
        self.inputs.append((label, display if display is not None else display_value(value, self.t)))
        return value

    def number(self, key, low, high, default, step=None):
        kwargs = dict(min_value=low, max_value=high, value=default, key=self.key(key))
        if step is not None:
            kwargs['step'] = step
        value = st.number_input(self.t[key], **kwargs)
        return self.add(key, value, self.t[key])

    def flag(self, key):
        value = st.checkbox(self.t[key], key=self.key(key))
        return self.add(key, value, self.t[key])

    def select(self, key, options, label_key=None):
        def label(value):
            if label_key:
                return self.t[label_key(value)]
            return str(value)
        value = st.selectbox(self.t[key], options, format_func=label, key=self.key(key))
        return self.add(key, value, self.t[key], label(value))

    def sex(self):
        return self.select('sex', ['M', 'F'], lambda x: x)


def source_panel(module, t):
    with st.expander(t['references']):
        for source in SOURCES[module]:
            # DOI names and mathematical units are intentionally language-independent.
            st.write(source)


def submit_result(module, values, inputs, results, t, note=None):
    report = make_report(t[module], inputs, results,
                         note or t.get(NOTES.get(module), t['pdf_disclaimer']), SOURCES[module], t)
    st.session_state[f'report:{module}'] = {
        'fingerprint': fingerprint(values, t), 'report': report, 'pdf': generate_pdf(report, t)}


def show_result(module, values, t):
    saved = st.session_state.get(f'report:{module}')
    if not saved:
        return
    if saved['fingerprint'] != fingerprint(values, t):
        del st.session_state[f'report:{module}']
        st.info(t['recalculate'])
        return
    report = saved['report']
    st.subheader(t['result'])
    for label, value in report['results']:
        if module == 'ecg':
            # Clinician-authored text must not become executable HTML or remote image markdown.
            st.text(f'{label}: {value}')
        else:
            st.success(f'{label}: {value}')
    st.download_button(t['download_pdf'], data=saved['pdf'],
                       file_name=f'CardioApp_{module}.pdf', mime='application/pdf',
                       key=f'download:{module}')


def render_score(module, t):
    st.subheader(t[module])
    if module in NOTES:
        st.caption(t[NOTES[module]])
    fields = Fields(module, t)
    if module == 'framingham':
        fields.number('age', 30, 79, 55); fields.sex()
        fields.number('total_chol', 1, 1000, 220)
        fields.number('hdl', 1, 200, 50); fields.number('sbp', 1, 350, 130)
        for key in ['smoker', 'treated', 'diabetes', 'vascular_disease']:
            fields.flag(key)
    elif module == 'euroscore':
        age = fields.number('age', 18, 120, 65); sex = fields.sex()
        dialysis = fields.flag('dialysis')
        if dialysis:
            fields.values['renal'] = 'dialysis'
            fields.inputs.append((t['renal'], t['renal_dialysis']))
        else:
            weight = fields.number('weight', 0.1, 500.0, 70.0, 0.1)
            creat = fields.number('creatinine', 0.01, 30.0, 1.0, 0.01)
            clearance = calc.cockcroft_gault(age, sex, weight, creat)
            fields.values['renal'] = calc.renal_category(clearance)
            fields.inputs += [(t['clearance'], f'{clearance:.2f}'),
                              (t['renal'], t['renal_' + fields.values['renal']])]
            st.caption(f"{t['clearance']}: {clearance:.2f}")
        for key in calc.EURO_COEFFICIENTS:
            fields.flag(key)
        fields.select('nyha', [1, 2, 3, 4])
        for key in ['lv', 'pulmonary', 'urgency', 'procedure']:
            fields.select(key, list(calc.EURO_CATEGORIES[key]), lambda x, k=key: k + '_' + x)
    elif module == 'chads':
        fields.number('age', 18, 120, 70); fields.sex()
        for key in ['hypertension', 'diabetes', 'heart_failure', 'stroke', 'vascular_disease']:
            fields.flag(key)
    elif module == 'grace':
        fields.number('age', 18, 120, 65)
        fields.number('heart_rate', 1, 350, 85); fields.number('sbp', 1, 350, 120)
        fields.number('creatinine', 0.01, 30.0, 1.1, 0.01)
        fields.select('killip', [1, 2, 3, 4])
        for key in ['arrest', 'st_deviation', 'biomarkers']:
            fields.flag(key)
    elif module == 'timi':
        fields.number('age', 18, 120, 60)
        for key in ['risk_factors', 'known_cad', 'aspirin', 'angina']:
            fields.flag(key)
        st_value = st.checkbox(t['st_timi'], key=fields.key('st_deviation'))
        fields.add('st_deviation', st_value, t['st_timi'])
        fields.flag('biomarkers')
    elif module == 'ckd':
        fields.number('age', 18, 120, 60); fields.sex()
        fields.number('creatinine', 0.01, 30.0, 1.0, 0.01)
    elif module == 'bmi':
        fields.number('weight', 0.1, 500.0, 70.0, 0.1)
        fields.number('height', 50.0, 250.0, 170.0, 0.1)
    else:
        raise ValueError(module)
    if st.button(t['calculate'], key=f'calculate:{module}'):
        values = fields.values
        try:
            if module == 'framingham':
                result = calc.framingham(**values)
                results = [(t['points'], str(result['points'])), (t['risk_10yr'], result['risk'] + '%')]
            elif module == 'euroscore':
                params = {k: v for k, v in values.items() if k not in ('weight', 'creatinine', 'dialysis')}
                results = [(t['surgical_risk'], f'{calc.euroscore(**params):.2f}%')]
            elif module == 'chads':
                score, interpretation = calc.chads_vasc(**values)
                results = [(t['chads'], str(score)), (t['result'], t[interpretation])]
            elif module == 'grace':
                results = [(t['points'], str(calc.grace(**values)))]
            elif module == 'timi':
                score, risk = calc.timi(**values)
                results = [(t['timi'], str(score)), (t['timi_endpoint'], f'≈{risk}%')]
            elif module == 'ckd':
                results = [(t['egfr'], f'{calc.ckd_epi(**values):.2f} mL/min/1.73 m²')]
            elif module == 'bmi':
                value, category = calc.bmi(**values)
                results = [(t['bmi'], f'{value:.1f} kg/m²'), (t['category'], t[category])]
            submit_result(module, values, fields.inputs, results, t)
        except ValueError as error:
            st.session_state.pop(f'report:{module}', None)
            st.error(t['framingham_ineligible'] if str(error) == 'framingham_ineligible' else t['invalid_input'])
    show_result(module, fields.values, t)
    source_panel(module, t)


def render_drugs(t):
    st.subheader(t['drugs']); st.caption(t['infusion_note'])
    fields = Fields('drugs', t)
    drug = fields.select('select_drug', list(calc.DRUG_UNITS), lambda x: x)
    unit = calc.DRUG_UNITS[drug]
    weight = fields.number('weight', 0.1, 500.0, 70.0, 0.1) if unit == 'mcg/kg/min' else None
    dose = st.number_input(f"{t['dose']} ({unit})", min_value=0.0, max_value=100000.0,
                           value=0.0, step=0.01, format='%.6f', key=f'drugs:dose:{drug}')
    fields.add('dose', dose, f"{t['dose']} ({unit})")
    amount = fields.number('total_mg', 0.0, 100000.0, 0.0, 0.1)
    volume = fields.number('final_ml', 0.0, 100000.0, 0.0, 1.0)
    fields.values['unit'] = unit
    if st.button(t['calculate'], key='calculate:drugs'):
        try:
            result = calc.infusion(dose, unit, amount, volume, weight)
            results = [(t['pump_rate'], f"{result['ml_h']:.4g} mL/h"),
                       (t['concentration'], f"{result['mg_ml']:.6g} mg/mL"),
                       (t['total_dose'], f"{result['mg_min']:.6g} mg/min")]
            submit_result('drugs', fields.values, fields.inputs, results, t)
        except ValueError:
            st.session_state.pop('report:drugs', None); st.error(t['invalid_input'])
    show_result('drugs', fields.values, t)
    # Exact dimensional relationships, translated surrounding labels.
    st.caption('mL/h = (mg/min × 60) / (mg/mL)')
