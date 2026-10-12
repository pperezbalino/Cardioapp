"""Model references and limitations shared by independent and integrated tools."""
SOURCES = {
    'framingham': ['Framingham ATP III (2001), hard CHD point tables: https://www.framinghamheartstudy.org/fhs-for-researchers/fhs-risk-functions/hard-coronary-heart-disease-10-year-risk/'],
    'euroscore': ['Nashef et al. EuroSCORE II (2012), Table 6: https://doi.org/10.1093/ejcts/ezs043',
                 'Variable definitions: https://www.euroscore.org/index.php?id=17'],
    'chads': ['ACC/AHA/ACCP/HRS AF Guideline (2023), section 6.3.1: https://pmc.ncbi.nlm.nih.gov/articles/PMC11095842/',
              'ESC AF Guideline (2024), CHA2DS2-VA: https://doi.org/10.1093/eurheartj/ehae176'],
    'grace': ['Granger et al. (2003), Figure 4, original in-hospital GRACE nomogram: https://doi.org/10.1001/archinte.163.19.2345'],
    'has_bled': ['ESC AF Guideline (2020), Table 10, clinical HAS-BLED definitions: https://doi.org/10.1093/eurheartj/ehaa612',
                 'Pisters et al. (2010), original HAS-BLED: https://doi.org/10.1378/chest.10-0134',
                 'ESC AF Guideline (2024), bleeding scores must not decide withholding/withdrawal of anticoagulation: https://doi.org/10.1093/eurheartj/ehae176',
                 'ACC/AHA/ACCP/HRS AF Guideline (2023), section 6.1: https://doi.org/10.1161/CIR.0000000000001193'],
    'timi': ['TIMI Study Group, UA/NSTEMI calculator: https://timi.org/calculators/timi-risk-score-calculator-for-ua-nstemi/'],
    'ckd': ['NIDDK, 2021 CKD-EPI creatinine equation: https://www.niddk.nih.gov/research-funding/research-programs/kidney-clinical-research-epidemiology/laboratory/glomerular-filtration-rate-equations/adults'],
    'bmi': ['WHO, adult BMI categories: https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight'],
    'drugs': ['mL/h = dose (mg/min) × 60 ÷ final concentration (mg/mL).',
              'mcg/kg/min → mg/min: dose × weight (kg) ÷ 1000.'],
    'ecg': ['CardioApp: manual clinician-authored report. No automated ECG analysis.'],
}
NOTES = {'framingham': 'framingham_note', 'euroscore': 'euroscore_note', 'chads': 'af_note',
         'grace': 'grace_note', 'has_bled': 'has_bled_note', 'timi': 'timi_note', 'ckd': 'ckd_note',
         'drugs': 'infusion_note', 'ecg': 'ecg_note'}

