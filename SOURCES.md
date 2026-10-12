# Clinical models and arithmetic

Sources checked on 2026-10-11. The tests verify the implementations below; they are not clinical validation of CardioApp in a patient population.

## Framingham ATP III (historical hard CHD model)

[Framingham Heart Study: Hard Coronary Heart Disease, 10-year risk](https://www.framinghamheartstudy.org/fhs-for-researchers/fhs-risk-functions/hard-coronary-heart-disease-10-year-risk/)

[NIH/NHLBI ATP III executive summary, 2001](https://www.nhlbi.nih.gov/files/docs/guidelines/atp3xsum.pdf)

The implementation uses the published sex-specific point tables, including age-dependent cholesterol and smoking points. The outcome is myocardial infarction or coronary death, not total cardiovascular risk. The UI limits use to ages 30-79 and excludes diabetes and established vascular disease. Bounds are displayed as `<1%` and `≥30%`, never substituted with exact risks. High calculated primary-prevention risk does not become a diagnosis of secondary prevention.

Fixtures: a man aged 55, total cholesterol 220, HDL 50, untreated SBP 130 and no smoking has 12 points (10%); the corresponding woman has 14 points (2%). A man aged 35, cholesterol 150, HDL 65, untreated SBP 110 and no smoking has -5 points (<1%).

## EuroSCORE II (2012)

[Nashef et al., original paper, Table 6](https://doi.org/10.1093/ejcts/ezs043)

[Official variable definitions](https://www.euroscore.org/index.php?id=17)

All multivariable Table 6 coefficients are included, with intercept -5.324537 and the published age transform: x_age = 1 at age ≤60; otherwise age - 59. Renal clearance uses Cockcroft-Gault, not CKD-EPI: ≤50, >50 to ≤85, >85 mL/min, or dialysis. Poor mobility refers to neurological or musculoskeletal impairment, not NYHA. NYHA and CCS IV are separate predictors. LV function, pulmonary pressure, urgency, number of major procedures and thoracic aortic surgery are represented independently.

Published pulmonary pressure bins are <31, 31-55 and >55 mmHg. The result is predicted in-hospital mortality for adult cardiac surgery. It is not a TAVI risk model. No unverified low/intermediate/high categorisation is added.

Fixtures: male age ≤60 with all reference factors: approximately 0.4987%; male age 65: 0.574634477%. Increasing LV dysfunction increases predicted risk. A multi-factor fixture independently sums Table 6 coefficients in the tests.

## CHA₂DS₂-VASc

[2023 ACC/AHA/ACCP/HRS AF guideline, section 6.3.1](https://pmc.ncbi.nlm.nih.gov/articles/PMC11095842/)

[2024 ESC AF guideline](https://doi.org/10.1093/eurheartj/ehae176)

The score includes all original variables. Interpretation uses the 2023 ACC/AHA thresholds: no non-sex points, one non-sex point, and ≥2 non-sex points. Female sex alone does not indicate anticoagulation. The app explicitly identifies this guideline and notes that ESC 2024 instead uses CHA₂DS₂-VA. The guidance is not applied to mechanical valves or significant mitral stenosis. It does not assess contraindications or prescribe an anticoagulant.

## GRACE original in-hospital nomogram (2003)

[Granger et al., original paper, Figure 4](https://jamanetwork.com/journals/jamainternalmedicine/fullarticle/216232)

DOI: [10.1001/archinte.163.19.2345](https://doi.org/10.1001/archinte.163.19.2345)

This is the original discrete point model, not GRACE 2.0 and not the six-month post-discharge model. Figure 4 supplies all age, heart-rate, systolic-pressure, creatinine and Killip bins, including age ≥90, HR ≥200, SBP 160-199/≥200 and creatinine 2-3.99/≥4. ST deviation includes elevation or depression. The independent Free calculator and the integrated Pro case display both points and the original Figure 4 hospital-mortality readout. At printed anchors (70, 80, …, 240), the percentage is reproduced. Scores ≤60 show ≤0.2%; scores ≥250 show ≥52%. Intermediate scores show the interval between their two surrounding published anchors, not an interpolated or extrapolated point estimate. For example: 122 points → 1.6–2.1%; 140 points → 2.9%. No universal treatment/triage category is assigned from mortality.

Fixtures: age 65, HR 85, SBP 120, creatinine 1.1, Killip I and positive biomarkers = 58 + 9 + 34 + 7 + 14 = 122. The maximum-point fixture is 372.

## HAS-BLED (independent calculator, added 2026-10-12)

[ESC AF 2020 guideline, Table 10](https://doi.org/10.1093/eurheartj/ehaa612)

[Pisters et al., derivation of HAS-BLED, 2010](https://doi.org/10.1378/chest.10-0134)

[ESC AF 2024 guideline, section 6.7](https://doi.org/10.1093/eurheartj/ehae176)

[ACC/AHA/ACCP/HRS AF 2023 guideline, section 6.1](https://doi.org/10.1161/CIR.0000000000001193)

The explicitly named calculation profile follows ESC 2020 Table 10: uncontrolled SBP >160 mmHg; abnormal renal and hepatic function (one point each); previous stroke; previous major bleeding or predisposition; labile INR/TTR <60% on VKA; age >65 years OR extreme frailty (one point total); concomitant antiplatelets/NSAIDs and clinically relevant alcohol excess/abuse (one each). Maximum 9. Renal dysfunction means dialysis, renal transplant or creatinine >200 µmol/L. Hepatic dysfunction and alcohol excess are physician-assessed under the cited definitions; ESC 2020 cites >14 alcohol units/week as an example, not a universal automatic threshold. No hybrid age/alcohol cutoffs from a different guideline are silently substituted.

The physician confirms AF and assessment of all binary criteria before calculation; an unchecked box is not considered confirmed absence until that acknowledgement. Labile INR is not inferred from a single INR, does not apply to DOACs/no VKA, and is cleared when VKA is deselected. Each renal/liver and drugs/alcohol criterion remains separately visible. The stroke label explicitly reminds the physician that a haemorrhagic stroke also meets the bleeding criterion (ESC 2020 Table 10 footnote a). ≥3 flags high risk for review of modifiable factors and closer follow-up; <3 does not exclude bleeding. There is no universal annual bleeding percentage and no automatic anticoagulation decision. ESC 2024 does not endorse a particular bleeding score for deciding anticoagulation, and both ESC 2024 and ACC/AHA 2023 caution against using bleeding scores alone to withhold/withdraw anticoagulation. This historical, named tool is not advertised as an ESC 2024-preferred score.

Fixtures: adult age 65 and SBP 160, all other criteria absent → 0; age 66 or extreme frailty → 1 (never 2 together); all nine components present → 9. HAS-BLED is available in Free and Pro independent tools, not automatically inferred from shared patient fields.

## TIMI UA/NSTEMI

[TIMI Study Group's own calculator](https://timi.org/calculators/timi-risk-score-calculator-for-ua-nstemi/)

All seven variables are included: age ≥65, ≥3 coronary risk factors, known coronary stenosis ≥50%, aspirin in the prior seven days, ≥2 anginal episodes in 24 hours, ST deviation ≥0.5 mm and elevated biomarkers. Rounded 14-day combined endpoint percentages follow the TIMI Study Group calculator. They refer to death, MI or severe recurrent ischaemia requiring urgent revascularisation, not death alone. The output does not recommend discharge based on the score.

## CKD-EPI creatinine (2021)

[NIDDK: adult race-free equations](https://www.niddk.nih.gov/research-funding/research-programs/kidney-clinical-research-epidemiology/laboratory/glomerular-filtration-rate-equations/adults)

Uses 142, exponents -0.241 (female)/-0.302 (male) and -1.200, age factor 0.9938, and female multiplier 1.012. The adult equation accepts ages ≥18. Output is indexed to 1.73 m² and assumes stable creatinine. It is not absolute creatinine clearance and is not presented as a drug-dosing rule.

Test numerical fixtures were independently evaluated with Python Decimal at 40-digit precision from the published equation. Examples: age 60, creatinine 1 mg/dL: male 86.162620780 and female 64.495000354 mL/min/1.73 m².

## BMI

[WHO: overweight and obesity](https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight)

BMI = weight (kg) / height (m)². Adult categories: <18.5, 18.5-<25, 25-<30, ≥30. No paediatric interpretation is offered.

## Infusion conversions

The calculator takes a user-prescribed dose, drug amount in mg and final solution volume in mL. It does not suggest therapeutic doses, commercial vial concentrations, loading regimens, compatibilities or routes.

- mcg/kg/min × weight (kg) / 1000 = mg/min.
- mg/min is already an absolute rate; patient weight is not applied.
- mg/mL = total mg / final mL.
- mL/h = mg/min × 60 / (mg/mL).

Fixtures: 0.1 mcg/kg/min, 70 kg, 4 mg in a final 250 mL → 26.25 mL/h. Lidocaine 1 mg/min, 1000 mg in 250 mL → 15 mL/h regardless of weight. Blank/zero, negative and non-finite values are rejected.

## ECG reports

There is no connected automatic ECG interpretation engine. The app validates the uploaded image/PDF, requires clinician-authored findings and a manual-review confirmation, and generates an explicitly manual report. It cannot issue a diagnosis from an uploaded file. The original file is embedded as a PDF attachment; images are also displayed in the report. The original SHA-256 fingerprint and UTC generation time are included. Reports are generated in memory, with no patient-named server files.
