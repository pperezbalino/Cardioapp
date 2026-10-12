"""Local templates and physician review; case snapshots stay independent of text."""
from dataclasses import dataclass, replace
import hashlib
import hmac
import secrets
import json

from access import Feature, require
from clinical_case import FIELD_SPECS, utc_now
from integrated_engine import checked, case_hash, known, evaluate, consistency, emergency_priority
from pdf_utils import make_report, generate_pdf
from acs_pathways import pathway, SOURCE, AHA_SOURCE, nitrate_assessment

TEMPLATE_VERSION = '2A.3-NTG'
_REVIEW_KEY = secrets.token_bytes(32)


def field_value(spec, value, t):
    if value is None:
        return t['case_unknown']
    if spec.kind == 'tri':
        return t['case_present' if value else 'case_absent']
    if spec.kind == 'sex':
        return t[value]
    if spec.kind in ('acs', 'strategy', 'response'):
        return t[value]
    if spec.kind == 'number':
        return f'{value:g}' + (f' {spec.unit}' if spec.unit and spec.unit != 'years' else '')
    return value


def score_text(score, t):
    if score.status == 'missing':
        return t['score_missing'].format(fields=', '.join(t[k] for k in score.missing))
    if score.status == 'ineligible':
        return t['score_ineligible']
    if score.status == 'blocked':
        return t['score_blocked']
    parts = []
    for key, value in score.result.items():
        if key == 'points': parts.append(f"{t['points']}: {value}")
        elif key == 'risk': parts.append(f"{t['risk_10yr']}: {value}%")
        elif key == 'risk_14d': parts.append(f"{t['timi_endpoint']}: {value}%")
        elif key == 'egfr': parts.append(f"{t['egfr']}: {value:.2f} mL/min/1.73 m²")
        elif key == 'bmi': parts.append(f"{t['bmi']}: {value:.2f} kg/m²")
    return '; '.join(parts)


@dataclass(frozen=True)
class ReportDraft:
    owner: str
    case_id: str
    case_revision: int
    input_hash: str
    mode: str
    lang: str
    sections: tuple[tuple[str, str], ...]
    version: int = 1
    created_at: str = ''
    reviewed_by: str | None = None
    reviewed_at: str | None = None
    reviewed_digest: str | None = None
    template_version: str = TEMPLATE_VERSION
    review_signature: str | None = None


def report_digest(draft):
    payload = [draft.owner, draft.case_id, draft.case_revision, draft.input_hash,
               draft.mode, draft.lang, draft.sections, draft.version,
               draft.created_at, draft.template_version]
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False).encode()).hexdigest()


def review_signature(draft):
    payload = json.dumps([report_digest(draft), draft.reviewed_by, draft.reviewed_at]).encode()
    return hmac.new(_REVIEW_KEY, payload, hashlib.sha256).hexdigest()


def require_current(context, case, draft):
    checked(context, case)
    if not isinstance(draft, ReportDraft) or draft.owner != context.subject:
        raise PermissionError('report_owner')
    if (draft.case_id != case.case_id or draft.case_revision != case.revision
            or draft.input_hash != case_hash(case) or draft.mode != case.mode
            or draft.template_version != TEMPLATE_VERSION):
        raise ValueError('report_stale')


def require_reviewed_case(context, case):
    checked(context, case)
    if case.review_state != 'reviewed' or any(
        datum.value is not None and not datum.confirmed for datum in case.facts.values()):
        raise ValueError('report_required')
    if any(issue.code in ('bp_order', 'chol_order', 'cad_history', 'sest_lysis_conflict', 'pain_response_conflict') for issue in consistency(context, case)):
        raise ValueError('report_required')


def create_draft(context, case, t):
    require_reviewed_case(context, case)
    sections = {}
    missing = {}
    for spec in FIELD_SPECS:
        group = 'case_group_' + spec.group
        value = known(case, spec.key)
        if value is None:
            missing.setdefault(group, []).append(t[spec.key])
            sections.setdefault(group, '')
            continue
        line = f"{t[spec.key]}: {field_value(spec, value, t)}"
        sections[group] = sections.get(group, '') + ('\n' if group in sections else '') + line
    for group, fields in missing.items():
        sections[group] += ('\n' if sections[group] else '') + t['score_missing'].format(fields=', '.join(fields))
    treatment = pathway(context, case)
    sections['report_assessment'] = t['stemi_documented' if treatment.branch == 'stemi' else 'sest_documented'] if treatment else t['report_pending']
    sections['report_plan'] = t['report_pending']
    return ReportDraft(context.subject, case.case_id, case.revision, case_hash(case), case.mode,
                       t['_lang'], tuple(sections.items()), created_at=utc_now())


def edit_draft(context, case, draft, sections):
    require_current(context, case, draft)
    if not isinstance(sections, dict) or set(sections) != set(dict(draft.sections)):
        raise ValueError('sections')
    if any(not isinstance(v, str) or len(v) > 30000 for v in sections.values()):
        raise ValueError('sections')
    updated = tuple((key, sections[key]) for key, _ in draft.sections)
    if updated == draft.sections:
        return draft
    return replace(draft, sections=updated, version=draft.version + 1,
                   reviewed_by=None, reviewed_at=None, reviewed_digest=None, review_signature=None)


def review_draft(context, case, draft, *, confirmed=False):
    require_current(context, case, draft)
    require_reviewed_case(context, case)
    if confirmed is not True:
        raise ValueError('report_review')
    reviewed = replace(draft, reviewed_by=context.subject, reviewed_at=utc_now(),
                       reviewed_digest=report_digest(draft))
    return replace(reviewed, review_signature=review_signature(reviewed))


def export_draft(context, case, draft, t):
    require(context, Feature.PDF)
    require_current(context, case, draft)
    require_reviewed_case(context, case)
    if (draft.reviewed_by != context.subject or not draft.reviewed_at
            or draft.reviewed_digest != report_digest(draft)
            or not draft.review_signature
            or not hmac.compare_digest(draft.review_signature, review_signature(draft))):
        raise ValueError('report_review')
    if t['_lang'] != draft.lang:
        raise ValueError('report_stale')
    # Recompute from the reviewed snapshot; scores are never parsed from narrative.
    scores = evaluate(context, case)
    treatment = pathway(context, case)
    inputs = [(t['case_alias'], case.alias or t['case_unknown']),
              (t['case_version'], str(case.revision))]
    for spec in FIELD_SPECS:
        if known(case, spec.key) is None:
            continue
        inputs.append((t[spec.key], field_value(spec, known(case, spec.key), t)))
    priority = emergency_priority(context, case)
    results = [(t[k], value) for k, value in draft.sections]
    if priority:
        results.insert(0, (t['stemi'], t['stemi_priority']))
        results.insert(1, (t['reperfusion_activated'], t['activation_'+priority.activation]))
    if treatment:
        nitrate = nitrate_assessment(context, case)
        if nitrate:
            results.append((t['case_group_antiischaemic'], t[nitrate.status]))
        results += [(t['acs_pathway'], t[treatment.route]), (t['acs_pathway'], t['acs_pathway_notice'])]
        results += [(t['acs_pathway'], t[step]) for step in treatment.supplemental]
        if treatment.missing:
            results += [(t['acs_pathway'], t['score_missing'].format(fields=', '.join(t[k] for k in treatment.missing)))]
    results += [(t['integrated_title'], t['integrated_notice'])]
    from clinical_sources import SOURCES, NOTES
    for score in scores:
        results.append((t[score.algorithm_id], score_text(score, t)))
        if score.algorithm_id in NOTES:
            results.append((t[score.algorithm_id], t[NOTES[score.algorithm_id]]))
    results += [(t[issue.code], ', '.join(t[k] for k in issue.fields))
                for issue in consistency(context, case)]
    results += [(t['report_review'], t['report_reviewed'].format(
        actor=draft.reviewed_by, time=draft.reviewed_at, version=draft.version))]
    sources = list(dict.fromkeys(source for score in scores if score.status == 'ready'
                                for source in SOURCES[score.algorithm_id]))
    if treatment:
        sources.extend([SOURCE, AHA_SOURCE])
    if priority:
        sources.append('ESC ACS Guidelines (2023), sections 5.2.1 and 5.3: https://doi.org/10.1093/eurheartj/ehad191')
    report = make_report(t['report_title_' + case.mode], inputs, results,
                         t['report_notice'] + ' ' + t['report_documented'], sources, t, context=context)
    if priority:
        report['priority_note'] = t['stemi_priority'] + ' ' + t['activation_'+priority.activation]
    if treatment:
        report['priority_note'] = (report.get('priority_note', '') + ' ' + t[treatment.route]).strip()
        report['pathway_id'] = treatment.branch
        report['pathway_version'] = treatment.version
    report.update(template_version=draft.template_version, report_version=draft.version,
                  algorithm_id='integrated-case', algorithm_version=scores[0].algorithm_version,
                  input_hash=draft.input_hash, case_id=case.case_id, case_revision=case.revision,
                  review_hash=draft.reviewed_digest, reviewed_by=draft.reviewed_by,
                  reviewed_at=draft.reviewed_at)
    return report, generate_pdf(report, t, context=context)
