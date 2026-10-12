# Stage 2A: integrated deterministic assessment and reviewed report drafts

This review branch extends stage 1 without deployment, billing, API credentials or external model calls. Free retains independent calculators without advertising or reports. All integrated services enforce Pro pilot access and case ownership.

## Clinical workflow

Both intake modes use the same confirmed clinical case. New schema 1.3 inputs start unknown. Missing or unconfirmed inputs never count as negative, normal or zero. Forms accept the displayed canonical units only; adapters reject inconsistent unit metadata and never silently convert values. Free text stays physician-entered narrative, without automatic extraction or diagnoses.

Emergency care supports the initial chest-pain workflow:

- Original GRACE 2003 points require a physician-selected suspected ACS, STEMI or UA/NSTEMI context, age, heart rate, systolic pressure, creatinine, integer Killip class, cardiac arrest at presentation, ST deviation and biomarkers.
- TIMI UA/NSTEMI requires that specific physician-selected context and all seven criteria. The CAD-risk criterion derives from five confirmed factors; its coronary family history is separate from the broader cardiovascular family history. Its ST threshold is recorded separately from GRACE's ST deviation. The displayed percentage retains the 14-day combined endpoint, not isolated mortality.

Outpatient care supports general cardiovascular consultation:

- Framingham ATP III hard CHD is explicitly historical, primary prevention, ages 30–79, excluding diabetes and established vascular disease. No ASCVD or modern prevention-model equivalence is claimed.

Both modes support CHA2DS2-VASc points only when AF is explicitly confirmed, CKD-EPI 2021 only when creatinine is confirmed steady-state without AKI, and adult BMI when weight and height are confirmed. Scores do not rule out emergencies or generate medication orders. The separate clinician-selected therapeutic reference pathways are documented in [ACS_PATHWAYS.md](ACS_PATHWAYS.md). EuroSCORE II and infusion conversion remain independent tools because these first two flows do not justify automatic surgical or prescribing-context integration.

The assessment displays the precise confirmed inputs, missing inputs, applicability status, source and model limitation. It checks diastolic/systolic ordering, HDL/total-cholesterol ordering and known coronary stenosis versus explicitly absent vascular disease. These inconsistencies block affected calculations and report preparation/review. Elevated biomarkers in an explicitly different coronary context produce a review notice, without inferring ACS. This is a small documented rule set, not comprehensive contradiction detection in narrative, units or clinical reasoning.

## Editable local drafts

A reviewed saved case can populate an emergency progress/referral draft or a cardiovascular consultation draft. Templates contain confirmed documented information and explicit missing-field lists. Clinical assessment and management/follow-up remain physician-completion placeholders. There are no AI-generated diagnostic or treatment inferences. Deterministic therapeutic reference routes are displayed separately from editable physician decisions.

Physicians can edit every narrative section without altering the canonical case or deterministic results. Each report carries its owner, case ID/revision/hash, language, template version, text version, creation time and separate review metadata. A change to the text removes review; a change to the case invalidates the draft. Unsaved case edits hide integrated calculations and export. Report editor values survive navigation and language changes within the session; separate language drafts are not automatic translations of physician prose.

PDF export requires an explicit review of the complete report and its calculations. The server checks current entitlements, ownership, case snapshot, language and a session-server HMAC review seal. PDFs distinguish the confirmed source inputs from the editable narrative and recomputed scores, and include source limitations and review/version metadata. The seal checks in-process review integrity; it is not a legal digital signature or persistent audit service. Exported files cannot be recalled after download.

Starting a new case or losing Pro access clears case, report drafts, review state and clinical widgets. No longitudinal database or patient-data storage is added.

## Simulated provider boundary

`copilot_provider.py` defines an interchangeable provider protocol and only a local simulation. Its request contains field names and score statuses, not patient values, aliases, narrative or identifiers. The response is explicitly simulated, reports zero model calls/cost and has no clinical inference. It is a development seam, not an external-provider payload contract or an AI clinical evaluation.

No Qwen, DeepSeek or other provider is selected or connected. Extraction, model prompts, provider privacy/licensing evaluation, per-user quotas and budget reservation/enforcement belong to a separately approved external-AI step. The real AI feature remains denied by access controls.

## Verification and remaining release gates

Automated tests exercise independently checked fictitious ACS/outpatient examples, unknown and unconfirmed inputs, distinct score criteria, applicability, units, conflicts, Free/Pro isolation, ownership/revocation, simulated zero-cost behavior, review forgery/edit/staleness, seven-language PDF generation, and ES/EN/PT navigation and report workflows. PDF pages are also visually inspected. Passing software tests does not establish clinical validation.

This branch is stacked on stage 1. It does not merge or deploy either earlier PR. Clinical review of reference cases, usability review and authorization remain necessary before clinical release. External AI activation and any paid service or deployment require Pablo's explicit authorization.
