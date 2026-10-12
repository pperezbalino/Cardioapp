"""Named adult infusion references; distinct from dose selection and arithmetic.

A reference interval is neither an absolute safety limit nor a default prescription.
"""
from dataclasses import dataclass
from access import Feature, require

VERSION = '2026.10.12-dose-reference-1'
HF_SOURCE = 'ESC Heart Failure 2021, Table 22: https://doi.org/10.1093/eurheartj/ehab368'
VT_SOURCE = 'ESC Ventricular Arrhythmias 2022, Table 8: https://doi.org/10.1093/eurheartj/ehac262'
TACHY_SOURCE = 'AHA ACLS 2025, Adult Tachyarrhythmia With a Pulse: https://www.heart.org/-/media/CPR-Files/CPR-Guidelines-Files/2025-Algorithms/Algorithm-ACLS-Tachycardia-250514.pdf'
BRADY_SOURCE = 'AHA ACLS 2025, Adult Bradycardia With a Pulse: https://www.heart.org/-/media/CPR-Files/CPR-Guidelines-Files/2025-Algorithms/Algorithm-ACLS-Bradycardia-250514.pdf'
NTG_SOURCE = 'AHA/ACC ACS 2025, Table 6: https://doi.org/10.1016/j.jacc.2024.11.009'


@dataclass(frozen=True)
class DoseReference:
    profile_id: str
    drug: str
    context_key: str
    unit: str
    low: float
    high: float | None
    kind: str  # range / fixed / start
    source: str
    note_key: str


REFERENCES = (
    DoseReference('adrenaline_ahf_esc2021','adrenaline','ref_ahf','mcg/kg/min',.05,.5,'range',HF_SOURCE,'ref_inotrope_note'),
    DoseReference('adrenaline_brady_aha2025','adrenaline','ref_brady','mcg/min',2,10,'range',BRADY_SOURCE,'ref_brady_note'),
    DoseReference('noradrenaline_ahf_esc2021','noradrenaline','ref_ahf','mcg/kg/min',.2,1,'range',HF_SOURCE,'ref_inotrope_note'),
    DoseReference('dobutamine_ahf_esc2021','dobutamine','ref_ahf','mcg/kg/min',2,20,'range',HF_SOURCE,'ref_inotrope_note'),
    DoseReference('levosimendan_ahf_esc2021','levosimendan','ref_ahf','mcg/kg/min',.05,.2,'range',HF_SOURCE,'ref_levo_note'),
    DoseReference('lidocaine_vt_esc2022','lidocaine','ref_lido_vt','mg/min',2,4,'range',VT_SOURCE,'ref_lido_note'),
    DoseReference('amiodarone_wide_aha2025','amiodarone','ref_amio_wide','mg/min',1,1,'fixed',TACHY_SOURCE,'ref_amio_note'),
    DoseReference('nitroglycerin_acs_aha2025','nitroglycerin','ref_ntg_acs','mcg/min',10,None,'start',NTG_SOURCE,'ntg_safety'),
)
BY_ID = {r.profile_id:r for r in REFERENCES}
PRO_DRUGS = tuple(dict.fromkeys(r.drug for r in REFERENCES))


def profiles(drug, *, context=None):
    require(context, Feature.DOSE_REFERENCE)
    return tuple(r.profile_id for r in REFERENCES if r.drug==drug)


def get_reference(drug, profile_id, *, context=None):
    require(context, Feature.DOSE_REFERENCE)
    reference=BY_ID.get(profile_id)
    if reference is None or reference.drug!=drug: raise ValueError('drug_profile')
    return reference


def reference_rates(reference, total_mg, final_ml, weight=None, *, context=None):
    require(context, Feature.DOSE_REFERENCE)
    from calculations import infusion
    values={'reference_low_ml_h': infusion(reference.low,reference.unit,total_mg,final_ml,weight)['ml_h']}
    if reference.high is not None and reference.high!=reference.low:
        values['reference_high_ml_h']=infusion(reference.high,reference.unit,total_mg,final_ml,weight)['ml_h']
    return values


def outside_reference(reference,dose, *, context=None):
    require(context, Feature.DOSE_REFERENCE)
    from calculations import number
    number(dose,.000001,100000,'dose')
    if reference.kind=='start': return False  # A start is not an upper/lower maintenance bound.
    return dose<reference.low or dose>reference.high
