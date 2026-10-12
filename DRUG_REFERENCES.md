# Independent infusion conversion and Pro dose references

Free retains the original six-drug list and prescribed-dose/dilution conversion to mL/h, concentration and total dose per minute. It does not select a clinical regimen, display recommended ranges, call the reference services, compare a prescribed dose to guideline intervals or create a PDF/report.

Pro adds a separate server-authorized `DOSE_REFERENCE` capability. Reference lookup, interval conversion and interval comparison require a valid Pro context. Client plan values, absent/forged contexts and revoked invitations cannot access these services. Logout/revocation clears reference widget and numerical/PDF state before returning to the original Free controls.

Eight named adult reference profiles cover seven drugs:

| Drug | Named clinical context | Reference unit | Source |
|---|---|---|---|
| Adrenaline | Acute-HF inotropic/vasopressor support | mcg/kg/min | ESC HF 2021, Table 22 |
| Adrenaline | Compromising bradycardia after ineffective atropine | mcg/min | AHA ACLS 2025, bradycardia algorithm |
| Noradrenaline | Acute-HF vasopressor support | mcg/kg/min | ESC HF 2021, Table 22 |
| Dobutamine | Acute-HF inotropic support | mcg/kg/min | ESC HF 2021, Table 22 |
| Levosimendan | Acute-HF infusion and titration | mcg/kg/min | ESC HF 2021, Table 22 |
| Lidocaine | ACS-associated ventricular arrhythmia infusion after bolus | mg/min | ESC VA 2022, Table 8 |
| Amiodarone | Stable wide-QRS tachycardia, first six maintenance hours | mg/min | AHA ACLS 2025, tachycardia algorithm |
| NTG | IV starting-dose reference in the stated ACS context | mcg/min | AHA/ACC ACS 2025, Table 6 |

`drug_references.py` stores the source-versioned values separately from the arithmetic in `calculations.py`. Profiles identify exactly which version/indication was checked; they do not claim to exhaust all indications or to be the latest comprehensive HF guideline. Reconciliation with later guideline revisions, including the 2026 HF revision identified during research, remains a clinical-release review item. No new clinical feature is deployed by this branch.

UI and Pro PDFs display selected context, source, reference interval or fixed/start dose and the equivalent mL/h for the entered real dilution. Bolus/loading information is separate text and never enters the continuous-infusion conversion. NTG has a named starting dose without an invented maintenance ceiling. A dose outside a named interval displays a persistent review notice while permitting conversion; an interval is not a universal safety limit.

The dose input stays zero until the physician enters a prescribed value. Changing profiles resets the dose, preventing values in mcg/kg/min from carrying into mcg/min. Reference versions/profile IDs are retained in Pro records and PDFs. Free numerical records have the original three outputs and no reference metadata. No patient-case integration, prescribing order, clinical inference, advertisement, billing or external model is introduced.

Tests cover the original Free workflow in seven languages with reference-service calls made to fail, all Pro profiles and reports, authentic/forged/revoked entitlements, fixed vs weight-dependent units, starting-dose vs interval semantics, profile changes and persistent review notices. Software checks do not substitute for clinical validation.
