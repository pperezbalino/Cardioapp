"""Deterministic adapters. Unknown facts never become negative score inputs."""
from dataclasses import asdict, dataclass
import hashlib
import json

import calculations as calc
from clinical_case import FIELD_SPECS, require_owner, parse_value

ALGORITHM_VERSION = '2026.10.12-scores-2'
RISK_FIELDS = ('hypertension', 'diabetes', 'dyslipidemia', 'smoker', 'cad_family')


def case_hash(case):
    return hashlib.sha256(json.dumps(asdict(case), sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def checked(context, case):
    require_owner(context, case)
    # Validate the schema boundary, including units; no silent conversions.
    for spec in FIELD_SPECS:
        fact = case.facts.get(spec.key)
        if not fact:
            continue
        if fact.unit != spec.unit:
            raise ValueError('unit:' + spec.key)
        value = fact.value
        raw = ('unknown' if value is None else 'present' if value else 'absent') if spec.kind == 'tri' else (
            'unknown' if value is None else value) if spec.kind in ('sex', 'acs', 'strategy', 'response') else (
            '' if value is None else str(value))
        if parse_value(spec, raw) != value:
            raise ValueError(spec.key)
        expected = 'unknown' if value is None else 'absent' if value is False else 'present'
        if fact.status != expected or (fact.confirmed and fact.confirmed_by != context.subject):
            raise ValueError(spec.key)


def known(case, key):
    datum = case.facts.get(key)
    return datum.value if datum and datum.confirmed and datum.status != 'unknown' else None


@dataclass(frozen=True)
class Issue:
    code: str
    fields: tuple[str, ...]


def consistency(context, case):
    checked(context, case)
    issues = []
    if known(case, 'refractory_pain') is True and known(case, 'angina_response') == 'not_yet_treated':
        issues.append(Issue('pain_response_conflict', ('refractory_pain', 'angina_response')))
    if known(case, 'acs_context') == 'ua_nstemi' and known(case, 'reperfusion_strategy') == 'fibrinolysis':
        issues.append(Issue('sest_lysis_conflict', ('acs_context', 'reperfusion_strategy')))
    if known(case, 'known_cad') is True and known(case, 'vascular_disease') is False:
        issues.append(Issue('cad_history', ('known_cad', 'vascular_disease')))
    def both(a, b):
        return known(case, a) is not None and known(case, b) is not None
    if both('sbp', 'dbp') and known(case, 'dbp') >= known(case, 'sbp'):
        issues.append(Issue('bp_order', ('sbp', 'dbp')))
    if both('total_chol', 'hdl') and known(case, 'hdl') > known(case, 'total_chol'):
        issues.append(Issue('chol_order', ('total_chol', 'hdl')))
    if known(case, 'acs_context') == 'not_acs' and known(case, 'biomarkers') is True:
        # Elevated markers alone do not diagnose ACS: informational review, no inference.
        issues.append(Issue('markers_context', ('acs_context', 'biomarkers')))
    return issues


@dataclass(frozen=True)
class ScoreResult:
    algorithm_id: str
    status: str
    inputs: dict
    result: dict
    missing: tuple[str, ...]
    reason: str
    case_hash: str
    case_revision: int
    algorithm_version: str = ALGORITHM_VERSION


def evaluate(context, case):
    checked(context, case)
    issues = consistency(context, case)
    digest = case_hash(case)
    results = []
    def run(name, keys, gate_keys, applicable, calculate):
        inputs = {key: known(case, key) for key in dict.fromkeys((*gate_keys, *keys))}
        gate_missing = tuple(k for k in gate_keys if inputs[k] is None)
        missing = tuple(k for k, v in inputs.items() if v is None)
        conflict = any(x.code in ('bp_order', 'chol_order', 'cad_history') and set(x.fields) & set(inputs) for x in issues)
        status, output, reason = 'ready', {}, ''
        if gate_missing:
            status, missing = 'missing', gate_missing
        elif not applicable(inputs):
            status, missing, reason = 'ineligible', (), 'scope_' + name
        elif missing:
            status = 'missing'
        elif conflict:
            status, reason = 'blocked', 'conflict'
        else:
            try:
                output = calculate(inputs)
            except ValueError:
                status, reason = 'ineligible', 'scope_' + name
        results.append(ScoreResult(name, status, inputs, output, missing, reason, digest, case.revision))
    if case.mode == 'emergency':
        run('grace', ('age', 'heart_rate', 'sbp', 'creatinine', 'killip', 'arrest', 'st_deviation', 'biomarkers'),
            ('acs_context',), lambda v: v['acs_context'] in ('suspected_acs', 'stemi', 'ua_nstemi'),
            lambda v: calc.grace_assessment(**{k: v[k] for k in ('age', 'heart_rate', 'sbp', 'creatinine', 'killip', 'arrest', 'st_deviation', 'biomarkers')}))
        run('timi', ('age', *RISK_FIELDS, 'known_cad', 'aspirin', 'angina', 'timi_st', 'biomarkers'),
            ('acs_context',), lambda v: v['acs_context'] == 'ua_nstemi',
            lambda v: dict(zip(('points', 'risk_14d'), calc.timi(v['age'],
                risk_factors=sum(v[k] is True for k in RISK_FIELDS) >= 3,
                known_cad=v['known_cad'], aspirin=v['aspirin'], angina=v['angina'],
                st_deviation=v['timi_st'], biomarkers=v['biomarkers']))))
    else:
        run('framingham', ('age', 'sex', 'total_chol', 'hdl', 'sbp', 'smoker', 'treated', 'diabetes', 'vascular_disease'),
            ('primary_prevention', 'diabetes', 'vascular_disease'),
            lambda v: v['primary_prevention'] is True and v['diabetes'] is False and v['vascular_disease'] is False,
            lambda v: calc.framingham(**{k: v[k] for k in ('age', 'sex', 'total_chol', 'hdl', 'sbp', 'smoker', 'treated', 'diabetes', 'vascular_disease')}))
    run('chads', ('age', 'sex', 'hypertension', 'diabetes', 'heart_failure', 'stroke', 'vascular_disease'),
        ('af_confirmed',), lambda v: v['af_confirmed'] is True,
        lambda v: {'points': calc.chads_vasc(**{k: v[k] for k in ('age', 'sex', 'hypertension', 'diabetes', 'heart_failure', 'stroke', 'vascular_disease')})[0]})
    run('ckd', ('age', 'sex', 'creatinine'), ('renal_stable',), lambda v: v['renal_stable'] is True,
        lambda v: {'egfr': calc.ckd_epi(v['age'], v['creatinine'], v['sex'])})
    run('bmi', ('weight', 'height'), (), lambda v: True,
        lambda v: {'bmi': calc.bmi(v['weight'], v['height'])[0]})
    return results


@dataclass(frozen=True)
class EmergencyPriority:
    code: str
    activation: str
    missing_documentation: tuple[str, ...]


def emergency_priority(context, case):
    checked(context, case)
    if case.mode != 'emergency' or known(case, 'acs_context') != 'stemi':
        return None
    value = known(case, 'reperfusion_activated')
    status = 'documented' if value is True else 'not_activated' if value is False else 'unknown'
    fields = ('symptom_duration_min', 'ecg_reviewed', 'reperfusion_activated',
              'reperfusion_strategy', 'reperfusion_times', 'reperfusion_notes')
    return EmergencyPriority('stemi', status, tuple(k for k in fields if known(case, k) is None))
