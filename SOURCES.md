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

This is the original discrete point model, not GRACE 2.0 and not the six-month post-discharge model. Figure 4 supplies all age, heart-rate, systolic-pressure, creatinine and Killip bins, including age ≥90, HR ≥200, SBP 160-199/≥200 and creatinine 2-3.99/≥4. ST deviation includes elevation or depression. The UI displays the score without an invented mortality percentage or a universal treatment/triage category.

Fixtures: age 65, HR 85, SBP 120, creatinine 1.1, Killip I and positive biomarkers = 58 + 9 + 34 + 7 + 14 = 122. The maximum-point fixture is 372.

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
