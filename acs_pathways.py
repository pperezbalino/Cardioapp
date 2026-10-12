"""Physician-selected ACS therapeutic pathways; named ESC 2023 reference rules.

No ECG/text interpretation, drug prescribing, service activation or clinical-release claim.
Missing contraindications and risk features never count as absent.
"""
from dataclasses import dataclass
from integrated_engine import checked, known, evaluate, case_hash

PATHWAY_VERSION = 'ESC2023-AHAACC2025-NTG-review-2'
SOURCE = 'ESC ACS Guidelines (2023), sections 4–6: https://doi.org/10.1093/eurheartj/ehad191'
AHA_SOURCE = 'AHA/ACC ACS Guideline (2025): https://doi.org/10.1161/CIR.0000000000001309; official materials: https://professional.heart.org/en/science-news/2025-guideline-for-the-management-of-patients-with-acute-coronary-syndromes'
VERY_HIGH = ('haemodynamic_instability', 'refractory_pain', 'dangerous_arrhythmia',
             'mechanical_complication', 'hf_acs', 'recurrent_dynamic_ecg')
HIGH = ('nstemi_confirmed', 'dynamic_ecg', 'transient_st')


@dataclass(frozen=True)
class TherapeuticPathway:
    branch: str
    route: str
    reasons: tuple[str, ...]
    missing: tuple[str, ...]
    supplemental: tuple[str, ...]
    input_hash: str
    version: str = PATHWAY_VERSION


def pathway(context, case):
    checked(context, case)
    branch = known(case, 'acs_context')
    if case.mode != 'emergency' or branch not in ('stemi', 'ua_nstemi'):
        return None
    reasons, missing = (), ()
    if branch == 'stemi':
        delay = known(case, 'pci_delay_min')
        duration = known(case, 'symptom_duration_min')
        eligibility = known(case, 'lysis_eligible')
        # Shock/instability must not enter the ordinary fibrinolysis branch.
        urgent = tuple(k for k in ('haemodynamic_instability', 'dangerous_arrhythmia',
                                  'mechanical_complication') if known(case, k) is True)
        if urgent:
            route, reasons = 'stemi_unstable', urgent
        elif delay is None:
            route, missing = 'stemi_timing_pending', ('pci_delay_min',)
        elif delay <= 120:
            route, reasons = 'stemi_primary_pci', ('pci_delay_min',)
        elif duration is None:
            route, missing = 'stemi_timing_pending', ('symptom_duration_min',)
        elif duration > 720:
            route, reasons = 'stemi_late', ('symptom_duration_min',)
        elif eligibility is False:
            route, reasons = 'stemi_lysis_excluded', ('lysis_eligible',)
        else:
            safety = ('haemodynamic_instability', 'dangerous_arrhythmia', 'mechanical_complication')
            missing = tuple(k for k in safety if known(case, k) is None)
            if eligibility is None: missing += ('lysis_eligible',)
            if missing:
                route = 'stemi_safety_pending'
            else:
                route, reasons = 'stemi_pharmaco_invasive', ('pci_delay_min', 'symptom_duration_min', 'lysis_eligible')
    else:
        urgent = tuple(k for k in VERY_HIGH if known(case, k) is True)
        high = tuple(k for k in HIGH if known(case, k) is True)
        grace = next(s for s in evaluate(context, case) if s.algorithm_id == 'grace')
        if grace.status == 'ready' and grace.result['points'] > 140:
            high += ('grace',)
        urgent_missing = tuple(k for k in VERY_HIGH if known(case, k) is None)
        if urgent:
            route, reasons = 'sest_immediate', urgent
        elif urgent_missing:
            route, reasons, missing = 'sest_priority_pending', high, urgent_missing
        elif high:
            route, reasons = 'sest_early', high
        else:
            high_missing = tuple(k for k in HIGH if known(case, k) is None)
            if grace.status != 'ready': high_missing += grace.missing or ('grace',)
            if high_missing:
                route, missing = 'sest_risk_pending', tuple(dict.fromkeys(high_missing))
            elif known(case, 'high_suspicion_ua') is True:
                route, reasons = 'sest_inpatient', ('high_suspicion_ua',)
            elif known(case, 'high_suspicion_ua') is None:
                route, missing = 'sest_risk_pending', ('high_suspicion_ua',)
            else:
                route = 'sest_individualized'
    supplemental = ('acs_guide_basis', 'acs_initial_care', 'acs_antithrombotic')
    supplemental += ('acs_aha_antiplatelet_note', 'sest_no_lysis', 'sest_selective_reference') if branch == 'ua_nstemi' else ('stemi_followup',)
    supplemental += ('ntg_reference', 'ntg_safety', 'angina_reassessment')
    return TherapeuticPathway(branch, route, reasons, missing, supplemental, case_hash(case))


@dataclass(frozen=True)
class NitrateAssessment:
    status: str
    missing: tuple[str, ...]
    source: str = 'AHA/ACC ACS 2025, Table 6; ESC ACS 2023, 4.2.2.2'


def nitrate_assessment(context, case):
    checked(context, case)
    if case.mode != 'emergency' or known(case, 'acs_context') not in ('stemi', 'ua_nstemi'):
        return None
    sbp = known(case, 'sbp')
    instability = known(case, 'haemodynamic_instability')
    contraindications = known(case, 'ntg_contraindications')
    if contraindications is True or instability is True or (sbp is not None and sbp < 90):
        return NitrateAssessment('ntg_not_eligible', ())
    inputs = {'sbp': sbp, 'haemodynamic_instability': instability,
              'ntg_contraindications': contraindications}
    missing = tuple(k for k,v in inputs.items() if v is None)
    if missing:
        return NitrateAssessment('ntg_safety_pending', missing)
    # Reference eligibility only: no order, administered dose or inferred response.
    return NitrateAssessment('ntg_reference_available', ())
