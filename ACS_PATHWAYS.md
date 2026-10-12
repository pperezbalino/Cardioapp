# Chest-pain ACS pathways: clinical review branch

The urgent STEMI/CEST pathway and the NSTE-ACS/SEST pathway are separate. A clinician selects the working diagnosis; the app does not interpret ECG images or extract a diagnosis from prose. They are implemented in `acs_pathways.py`, independently of generative AI. No clinical deployment, service activation or billing is performed.

## Authoritative references and rule provenance

Only society ACS guidelines are used for this module:

- ESC 2023, European Heart Journal, DOI https://doi.org/10.1093/eurheartj/ehad191, sections 4–6 and Figure 8: executable invasive/reperfusion pathway rules and the identified reference treatment notes.
- AHA/ACC/ACEP/NAEMSP/SCAI 2025, Circulation, DOI https://doi.org/10.1161/CIR.0000000000001309: comparison notes on timing and upstream antiplatelet treatment. Official public materials: https://professional.heart.org/en/science-news/2025-guideline-for-the-management-of-patients-with-acute-coronary-syndromes . Full journal/PPTX retrieval was blocked by the publisher in this environment; the official public summary and indexed recommendations were checked. The implementation does not claim a full independent validation against every AHA/ACC recommendation.

The rule profile is explicitly ESC 2023 with AHA/ACC 2025 comparison notes, not an invented combined guideline. ESC's diagnosis-to-reperfusion clock is not interchangeable with AHA/ACC's first-medical-contact-to-device clock: the latter identifies targets of 90 min for direct care and 120 min for transfer. The entered `pci_delay_min` is specifically the ESC diagnosis-to-PCI reperfusion estimate. AHA/ACC notes also address possible upstream clopidogrel/ticagrelor when NSTE-ACS angiography is planned beyond 24 h; this is distinguished from routine pretreatment for early angiography.

## CEST/STEMI

A clinician-selected STEMI context displays the priority notice at the top before confirmation, saving, laboratory completion or score calculation. It directs activation of the local reperfusion pathway and catheterization/transfer coordination. App interaction is not necessary for emergency activation. Clinical decision support uses only subsequently saved confirmed inputs.

The reference decision branches are:

1. Documented haemodynamic instability, life-threatening arrhythmia or mechanical complication: emergency invasive/support assessment, without entering the ordinary fibrinolysis branch. This does not classify instability as an absolute fibrinolysis contraindication; individualized emergency management remains a clinician decision.
2. Estimated diagnosis-to-PCI reperfusion delay at most 120 min: primary PCI in the current centre or through coordinated transfer.
3. Delay above 120 min and symptom duration within 12 h: review fibrinolysis eligibility, including contraindications, and stability. Unknown eligibility or stability does not equal safety. A pharmaco-invasive reference route is shown only after clinician-confirmed eligibility and explicitly absent instability/arrhythmia/mechanical complication.
4. Fibrinolysis marked ineligible: urgent invasive/transfer assessment, without recommending a fibrinolytic.
5. Presentation beyond 12 h: invasive-strategy assessment, without routine fibrinolysis; ongoing ischaemia and instability influence urgency.
6. Missing timing or eligibility: retain emergency priority and show the missing routing inputs. Scores and biomarkers are not conditions for activation.

Fibrinolysis follow-up reference text includes transfer to a PCI centre, assessment of reperfusion, rescue PCI for failure/instability and early angiography after successful lysis. No medication is selected or administered by the app.

## SEST/NSTE-ACS

One confirmed very-high-risk criterion is sufficient for the immediate invasive reference route even if GRACE is unavailable: instability/shock, refractory or recurrent pain despite treatment, life-threatening arrhythmia, mechanical complication, ACS-related heart failure, or recurrent dynamic ST/T changes.

If these criteria remain unknown, the app cannot assert that waiting is safe. When all are explicitly absent, confirmed NSTEMI, dynamic ECG changes, transient ST elevation or a complete original GRACE score above 140 identify the high-risk reference route: inpatient invasive management and consideration of angiography within 24 h. A GRACE value of exactly 140 does not satisfy the above-140 rule. Confirmed high suspicion of unstable angina supports the inpatient invasive route. Other cases retain physician assessment and an individualized strategy; there is no automatic discharge or rule-out.

Fibrinolysis is excluded from the SEST pathway. If a confirmed SEST case nevertheless records a fibrinolysis plan, the mismatch is flagged and report creation/review is blocked until corrected.

## Therapeutic support and documentation

Both branches show reference initial assessment, ECG review, monitoring/defibrillation availability and physician-entered support. Antithrombotic documentation distinguishes bleeding/contraindication review, antiplatelet selection/timing and anticoagulation. NTG reference doses and safety/reassessment documentation are now included from AHA/ACC 2025 Table 6 and ESC 2023 section 4.2.2.2. Other drug-dose regimens, detailed interactive contraindication checklists and patient-specific prescriptions are not implemented; these require a separately reviewed clinical specification. The pathway is a therapeutic decision route with reference treatment notes, not a clinically validated complete medication order set.

Unknown is never absent. Normal-looking blood pressure does not automatically clear shock/instability; absent coronary history does not establish absence of >=50% coronary stenosis. Killip A in Pablo's fictitious test is manually mapped to class I, with the equivalence documented; there is no automatic prose extraction.

Activation, selected strategy, times, receiving centre and contraindication review are clinician documentation. The app never marks activation as completed without a confirmed entry and never contacts a service. Numerical scores remain supplementary. PDF priority and pathway outputs are independent of editable prose and include pathway version; editing narrative cannot remove the source pathway. Updating the report template invalidates prior reviews.

## Fictitious reference case

Male, 54 years, smoker, no coronary history reported; oppressive precordial pain 8/10 with sweating and tachycardia, one hour of evolution; BP 140/90, HR 100, Killip I (A); clinician-reported ST elevation V1–V5 and clinician-selected STEMI working diagnosis. Expected behavior: emergency reperfusion priority, TIMI UA/NSTEMI ineligible, no invented creatinine/troponin/arrest or GRACE result, and activation status unknown until documented. Timing to PCI and eligibility remain pending without suppressing the priority notice.

Tests cover this case, the 120-min/12-h/GRACE-140 boundaries, each very-high-risk SEST criterion, missing safety data, separate diagnostic contexts, ownership and Free permissions, pre-save priority, report integrity and multilingual PDFs. Clinical review and authorization remain required before release.

## Guideline authority and NTG update

Clinical rules come from the named AHA/ACC and ESC guidelines. Clinician review verifies the implementation and enters patient findings/actions; it does not create a separate clinician-named guideline. NTG uses guideline reference dosing (SL 0.3–0.4 mg every 5 min up to 3 doses; IV reference start 10 micrograms/min) and a documented safety check. Unknown stability/contraindications never confer reference eligibility; SBP below 90, instability or documented contraindication exclude it. The aggregate contraindication datum requires professional review of the displayed guideline conditions, not an automatic independent clearance.

Administered treatment and current pain response are recorded separately. Untreated pain never automatically becomes refractory; conflicting untreated/refractory entries require correction before report review. A previously confirmed urgent/recurrent-pain criterion is not silently removed because the current pain improves. The lower-risk selective-invasive reference is identified as AHA/ACC 2025 section 6.1, not a rule equating one negative troponin with low risk. No NTG trial is required to activate the CEST pathway or treat another urgent criterion. Report template changes invalidate previous reviews.

## ECG reference before selecting an ACS branch (2026-10-12)

Pro emergency intake now shows an expanded guideline reference before the physician selects a diagnostic context or confirms case data. AHA/ACC ACS 2025 Table 3 supplies the standard-lead J-point thresholds for new/presumed-new elevation in at least two anatomically contiguous leads: ≥1 mm outside V2–V3; V2–V3 ≥2 mm for men ≥40, ≥2.5 mm for men <40, ≥1.5 mm for women at any age. Units assume standard 10 mm/mV calibration. The clinician checks calibration, morphology, contiguity and the clinical ischaemia context.

ESC ACS 2023 section 3.2.1 supplies the clinical context and recognition of posterior occlusion and difficult ECG interpretation in LBBB/RBBB/ventricular pacing. The panel warns against mechanical application in LVH, blocks, pacing and repolarisation abnormalities; a new LBBB alone does not diagnose MI (AHA/ACC 2025 Table 3 footnote). A negative standard threshold is not an ACS/occlusion rule-out. Posterior/right-sided numeric thresholds and formal Sgarbossa calculations are not implemented by this reference. No image interpretation, automatic case classification, biomarker requirement or new patient-data fields are introduced. The reference does not alter physician-entered facts, existing CEST/SEST routes or report review. Reference version: `AHAACC2025-ESC2023-ECG-1`.
