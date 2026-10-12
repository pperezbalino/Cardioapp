"""Versioned, clinician-entered case data. Independent of reports, score adapters and providers."""
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import hashlib
import json
import math
import re
import uuid

from access import Feature, require

SCHEMA_VERSION = '1.2'


@dataclass(frozen=True)
class FieldSpec:
    key: str
    group: str
    kind: str
    unit: str | None = None
    low: float | None = None
    high: float | None = None


FIELD_SPECS = [
    FieldSpec('age', 'identity', 'number', 'years', 18, 120),
    FieldSpec('sex', 'identity', 'sex'),
    FieldSpec('chief_complaint', 'presentation', 'text'),
    FieldSpec('onset', 'presentation', 'text'),
    *[FieldSpec(key, 'symptoms', 'tri') for key in ['chest_pain', 'dyspnea', 'palpitations', 'syncope']],
    FieldSpec('medical_history', 'history', 'text'),
    *[FieldSpec(key, 'history', 'tri') for key in ['hypertension', 'diabetes', 'dyslipidemia',
                                               'smoker', 'family_history', 'heart_failure',
                                               'stroke', 'vascular_disease']],
    FieldSpec('medication', 'treatment', 'text'), FieldSpec('allergies', 'treatment', 'text'),
    FieldSpec('sbp', 'examination', 'number', 'mmHg', 1, 350),
    FieldSpec('dbp', 'examination', 'number', 'mmHg', 1, 250),
    FieldSpec('heart_rate', 'examination', 'number', 'bpm', 1, 350),
    FieldSpec('oxygen', 'examination', 'number', '%', 0, 100),
    FieldSpec('temperature', 'examination', 'number', '°C', 20, 45),
    FieldSpec('weight', 'examination', 'number', 'kg', .1, 500),
    FieldSpec('height', 'examination', 'number', 'cm', 50, 250),
    FieldSpec('physical_exam', 'examination', 'text'),
    FieldSpec('creatinine', 'laboratory', 'number', 'mg/dL', .01, 30),
    FieldSpec('total_chol', 'laboratory', 'number', 'mg/dL', 1, 1000),
    FieldSpec('hdl', 'laboratory', 'number', 'mg/dL', 1, 200),
    FieldSpec('biomarkers', 'laboratory', 'tri'),
    FieldSpec('laboratory_notes', 'laboratory', 'text'),
    FieldSpec('ecg_notes', 'studies', 'text'), FieldSpec('echo_notes', 'studies', 'text'),
    FieldSpec('other_studies', 'studies', 'text'),
    FieldSpec('clinical_notes', 'notes', 'text'),
    FieldSpec('acs_context', 'triage', 'acs'),
    FieldSpec('symptom_duration_min', 'reperfusion', 'number', 'min', 0, 43200),
    *[FieldSpec(key, 'reperfusion', 'tri') for key in ['ecg_reviewed', 'reperfusion_activated']],
    FieldSpec('reperfusion_strategy', 'reperfusion', 'strategy'),
    FieldSpec('reperfusion_times', 'reperfusion', 'text'),
    FieldSpec('reperfusion_notes', 'reperfusion', 'text'),
    FieldSpec('pci_delay_min', 'reperfusion', 'number', 'min', 0, 1440),
    FieldSpec('lysis_eligible', 'reperfusion', 'tri'),
    *[FieldSpec(key, 'acs_risk', 'tri') for key in ['haemodynamic_instability',
        'refractory_pain', 'dangerous_arrhythmia', 'mechanical_complication',
        'hf_acs', 'recurrent_dynamic_ecg', 'nstemi_confirmed', 'dynamic_ecg',
        'transient_st', 'high_suspicion_ua']],
    FieldSpec('bleeding_reviewed', 'acs_treatment', 'tri'),
    FieldSpec('antiplatelet_plan', 'acs_treatment', 'text'),
    FieldSpec('anticoagulation_plan', 'acs_treatment', 'text'),
    FieldSpec('support_plan', 'acs_treatment', 'text'),
    FieldSpec('killip', 'score_context', 'number', None, 1, 4),
    *[FieldSpec(key, 'score_context', 'tri') for key in [
        'arrest', 'st_deviation', 'timi_st', 'known_cad', 'aspirin', 'angina',
        'cad_family', 'af_confirmed', 'treated', 'renal_stable', 'primary_prevention']],

]
FIELDS = {spec.key: spec for spec in FIELD_SPECS}


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec='microseconds')


@dataclass(frozen=True)
class ClinicalDatum:
    value: str | float | bool | None
    status: str  # unknown / present / absent
    unit: str | None
    source: str  # structured_form / clinician_text; no claim of measured vs reported
    recorded_at: str
    observed_at: str | None = None
    confirmed: bool = False
    confirmed_by: str | None = None
    assertion_type: str = 'documented'


@dataclass(frozen=True)
class CaseRevision:
    revision: int
    changed_fields: tuple[str, ...]
    changed_at: str
    changed_by: str
    input_hash: str


@dataclass(frozen=True)
class ClinicalCase:
    case_id: str
    owner: str
    mode: str
    alias: str = ''
    schema_version: str = SCHEMA_VERSION
    revision: int = 0
    review_state: str = 'draft'
    facts: dict[str, ClinicalDatum] = field(default_factory=dict)
    audit: tuple[CaseRevision, ...] = ()


def create_case(context, mode='emergency'):
    require(context, Feature.CLINICAL_CASE)
    if mode not in ('emergency', 'outpatient'):
        raise ValueError('mode')
    return ClinicalCase(str(uuid.uuid4()), context.subject, mode)


def require_owner(context, case):
    require(context, Feature.CLINICAL_CASE)
    if not isinstance(case, ClinicalCase) or case.owner != context.subject:
        raise PermissionError('case_owner')


def parse_value(spec, raw):
    if spec.kind == 'tri':
        if raw not in ('unknown', 'present', 'absent'):
            raise ValueError(spec.key)
        return None if raw == 'unknown' else raw == 'present'
    if spec.kind == 'acs':
        if raw not in ('unknown', 'suspected_acs', 'stemi', 'ua_nstemi', 'not_acs'):
            raise ValueError(spec.key)
        return None if raw == 'unknown' else raw
    if spec.kind == 'strategy':
        if raw not in ('unknown', 'primary_pci', 'transfer_pci', 'fibrinolysis'):
            raise ValueError(spec.key)
        return None if raw == 'unknown' else raw
    if spec.kind == 'sex':
        if raw not in ('unknown', 'M', 'F'):
            raise ValueError(spec.key)
        return None if raw == 'unknown' else raw
    if not isinstance(raw, str):
        raise ValueError(spec.key)
    raw = raw.strip()
    if not raw:
        return None
    if spec.kind == 'text':
        if len(raw) > 4000:
            raise ValueError(spec.key)
        return raw
    if not re.fullmatch(r'\d+(?:[.,]\d+)?', raw):
        raise ValueError(spec.key)
    number = float(raw.replace(',', '.'))
    if not math.isfinite(number) or not spec.low <= number <= spec.high:
        raise ValueError(spec.key)
    if spec.key in ('age', 'killip') and not number.is_integer():
        raise ValueError(spec.key)
    return int(number) if spec.key in ('age', 'killip') else number


def save_case(context, case, raw_values, *, mode, alias='', confirmed=False):
    require_owner(context, case)
    if mode not in ('emergency', 'outpatient') or not isinstance(confirmed, bool):
        raise ValueError('mode')
    if not isinstance(alias, str) or not re.fullmatch(r'[A-Za-z0-9_-]{0,32}', alias):
        raise ValueError('alias')
    if set(raw_values) != set(FIELDS):
        raise ValueError('fields')
    now = utc_now()
    facts, changed = {}, []
    for spec in FIELD_SPECS:
        value = parse_value(spec, raw_values[spec.key])
        status = 'unknown' if value is None else 'absent' if value is False else 'present'
        is_confirmed = confirmed and value is not None
        previous = case.facts.get(spec.key)
        if previous and previous.value == value and previous.status == status and previous.confirmed == is_confirmed:
            facts[spec.key] = previous
        else:
            facts[spec.key] = ClinicalDatum(value, status, spec.unit,
                'clinician_text' if spec.kind == 'text' else 'structured_form', now,
                confirmed=is_confirmed, confirmed_by=context.subject if is_confirmed else None)
            changed.append(spec.key)
    if case.mode != mode: changed.append('mode')
    if case.alias != alias: changed.append('alias')
    review = 'reviewed' if confirmed and any(x.value is not None for x in facts.values()) else 'draft'
    if case.review_state != review: changed.append('review_state')
    if not changed:
        return case
    digest = hashlib.sha256(json.dumps({'facts': {k: asdict(v) for k, v in facts.items()},
                                       'mode': mode, 'alias': alias}, sort_keys=True).encode()).hexdigest()
    revision = case.revision + 1
    event = CaseRevision(revision, tuple(changed), now, context.subject, digest)
    return ClinicalCase(case.case_id, case.owner, mode, alias, revision=revision,
                        review_state=review, facts=facts, audit=case.audit + (event,))


def raw_values(case):
    result = {}
    for spec in FIELD_SPECS:
        value = case.facts.get(spec.key)
        value = value.value if value else None
        if spec.kind == 'tri':
            result[spec.key] = 'unknown' if value is None else 'present' if value else 'absent'
        elif spec.kind in ('sex', 'acs', 'strategy'):
            result[spec.key] = value or 'unknown'
        else:
            result[spec.key] = '' if value is None else format(value, 'g') if isinstance(value, float) else str(value)
    return result


def matches_saved(case, values, alias, mode):
    if case.alias != alias or case.mode != mode:
        return False
    try:
        return all(parse_value(spec, values[spec.key]) ==
                   (case.facts[spec.key].value if spec.key in case.facts else None)
                   for spec in FIELD_SPECS)
    except (ValueError, KeyError):
        return False


def confirmed_value(context, case, key):
    """Future score adapters must request complete, confirmed inputs explicitly."""
    require_owner(context, case)
    datum = case.facts.get(key)
    if not datum or datum.status == 'unknown' or not datum.confirmed:
        raise ValueError('missing_or_unconfirmed')
    return datum.value


def case_data(context, case):
    """Server-side interchange format; not an AI payload or persistent history."""
    require_owner(context, case)
    return asdict(case)
