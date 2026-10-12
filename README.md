# CardioApp

A Streamlit reference application for cardiovascular scores, adult renal function and BMI, prescribed infusion conversion, and clinician-authored ECG reports.

The recovered logo and the three main sections (scores, infusions and ECG) are preserved. All controls and report text have Spanish, English, French, Italian, German, Portuguese and Arabic catalogues. Model names, citations, mathematical notation and units retain their conventional forms.

## Free and Pro pilot

Free is the default: independent calculators, without advertising or report generation. Pro pilot access adds shared emergency/outpatient cases, deterministic integrated assessment, editable reviewed report drafts and PDF/manual ECG reports. The target Pro price is US$5.99/month; no billing or AI is active. Access is verified by server-configured invitations, not a browser plan selector. See [STAGE1.md](STAGE1.md) for the access foundation and [STAGE2A.md](STAGE2A.md) for the integrated workflow and [ACS_PATHWAYS.md](ACS_PATHWAYS.md) for the separate CEST/SEST therapeutic reference paths, guideline-based NTG reference and their review limits.

## Run locally

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Use Python 3.11 or 3.12. No API key is required and no external AI service is called. Streamlit Cloud should use `app.py` as the entry point. Embedded DejaVu fonts and their licence are in `assets/fonts/`.

## Implemented tools

- Framingham ATP III hard coronary heart disease risk, with applicability restrictions.
- Complete EuroSCORE II model, including Cockcroft-Gault renal clearance.
- CHA₂DS₂-VASc, with named ACC/AHA 2023 interpretation and an ESC 2024 model note.
- Original GRACE in-hospital point nomogram.
- Seven-variable TIMI UA/NSTEMI and the 14-day combined endpoint.
- Adult race-free CKD-EPI creatinine 2021.
- Adult BMI.
- Conversion of a prescribed infusion dose and actual final dilution to mL/h.
- Pro: manual ECG reports with validated image/PDF uploads and an embedded original file.
- Pro: PDF downloads for every calculator and manual ECG report, including inputs, units, sources, UTC time and version metadata.
- Pro: shared adult clinical case for emergency/outpatient forms, with unknown/present/absent states, provenance, explicit review and session-local revisions.

HAS-BLED and STS are not implemented. Automatic ECG interpretation is not implemented. The app does not claim otherwise.

## Verification

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Tests cover source-based numeric fixtures, original failure cases, boundaries and invalid input, seven-language UI execution, stale-result invalidation, PDF pagination and Unicode, and ECG validation/attachments. [SOURCES.md](SOURCES.md) documents the precise models, publications, applicability and worked examples. Code-level verification does not establish clinical validation in patients.

## Project layout

- `calculations.py`: model arithmetic, independent of Streamlit and language.
- `access.py` / `access_ui.py`: server-issued pilot entitlements and access controls.
- `clinical_case.py` / `case_ui.py`: versioned shared clinical data and the two intake modes.
- `acs_pathways.py`: distinct clinician-selected STEMI/NSTE-ACS reference therapeutic routes, with ESC 2023 rules and AHA/ACC 2025 comparison notes.
- `integrated_engine.py`: confirmed-case score adapters and a limited consistency rule set.
- `case_reports.py` / `integrated_ui.py`: editable local drafts, separate physician review and guarded export.
- `copilot_provider.py`: provider protocol and explicitly local simulation; no model calls.
- `clinical_sources.py`: shared model sources and limitations.
- `clinical_ui.py`: translated calculator controls and report lifecycle.
- `tools/`: screen entry points and manual ECG upload handling.
- `translations.py`: complete seven-language catalogue; missing translations fail visibly.
- `pdf_utils.py`: in-memory reports with embedded Unicode fonts and Arabic shaping.
- `tests/`: calculation, interface, report and upload tests.

There is one implementation of each model; the conflicting old copies at the repository root have been removed. Numerical results and Pro PDF downloads persist across reruns, and are invalidated when their inputs or language change. Shared case drafts survive navigation and language changes; closing/revoking Pro access or starting a new case clears clinical session data.

## Use and data

Reference results require professional review and do not replace clinical judgement. Infusion results are unit conversions, not prescriptions. Historical models are identified by name and year. Before use in patient care, review the definitions and applicability of each model.

The app itself does not send patient uploads to an AI service or deliberately persist them on disk. Hosting and session access must still be appropriate for the data entered. Use initials rather than full patient names.

Pablo Pérez Baliño · © 2025-2026 CardioApp
