# Stage 1: Free/Pro and the shared clinical case

## Implemented scope

One Streamlit application retains all existing calculator equations. Free is the default and has independent scores and infusion conversions. Free creates only numerical result records; it does not generate clinical reports, PDF bytes or ECG reports. Pro pilot access enables shared clinical intake, calculator PDF export and the existing manual ECG report. Target monthly Pro price is US$5.99; billing is not implemented or activated.

Emergency care and outpatient consultation use the same case and draft. Switching modes, views or language preserves entered case data without importing values from the independent calculators. All new labels have seven-language catalogues; Spanish, English and Portuguese are the initial priority.

No AI provider, transcription, automatic file interpretation, automatic score integration, personalised recommendation or permanent clinical history is enabled. The future AI/voice/history capabilities are explicitly denied by the permission service, including for Pro.

## Access control

`access.py` issues signed server-side access contexts after verifying an invitation against server configuration. Browser menu choices or a client-facing `plan=pro` value cannot confer rights. Report creation, PDF generation, manual ECG services and case operations check permissions in the service code as well as in the UI. Reports/cases are associated with the authorised pilot subject. Another subject cannot use these services to export a report or access confirmed case fields.

Pro sessions last at most eight hours. Revoking or expiring an invitation invalidates its existing contexts at the next server operation. Closing Pro access, changing identity or detecting revoked/expired access clears case data, drafts, calculation/report caches and clinical widgets in that session. Invitation attempts are limited to five per minute per Streamlit session.

This is invitation-based pilot access, not a subscription system or production identity service. Commercial account lifecycle, stronger abuse controls, recovery, persistent entitlements and hosting/data governance need a later approved design. No real pilot invitations or external accounts were created during implementation.

## Server configuration for a future approved pilot

With no configuration, the application remains Free. Invitation material belongs only in the server's secret/environment configuration, never the repository or the browser. A server administrator can prepare an invitation digest locally after choosing a private, randomly generated code:

```bash
python scripts/pilot_invite.py --subject pilot-doctor-01 --days 14
```

The utility requests the code twice through hidden terminal input. It outputs a SHA-256 digest and expiry, not the secret code. It neither enables the application nor sends an invitation. The administrator supplies the resulting JSON as `CARDIOAPP_PRO_INVITES` in the server environment. Multiple distinct subject records can be combined in this JSON object. Duplicate digests and malformed configurations fail closed. Do not use the deterministic codes in the test suite for a real pilot.

## Clinical data semantics

`clinical_case.py` is independent of Streamlit and reports. A case has a UUID, pseudonymous optional alias, owner, emergency/outpatient mode, `schema_version`, revision and review state. It contains demographics, presentation, symptoms, history/risk factors, medications/allergies, examination, laboratory, documented studies and free clinical text.

Numeric fields start empty; sex and clinical booleans start unknown. Unknown is `null`, not `false`. Known absence is `false`; known presence is `true`. Empty narrative text is also unknown, rather than an assertion that no history exists. No normal patient measurements or absent symptoms are prefilled.

Each datum records value, unit, source, entry timestamp, optional observation timestamp, confirmation and author of confirmation. Entry time is not silently treated as measurement time. A structured entry or physician text is documented information; the app does not claim it was independently observed or verified by AI. Text remains physician-entered text; extraction into structured fields belongs to stage 2.

Saving can retain a draft or explicitly confirm entered facts. Unknown facts remain unconfirmed even when the case's entered data are reviewed. An edit resets the UI review checkbox. Saving the edited data without renewed confirmation clears its confirmed state. Blank confirmation cannot mark an entirely empty case as reviewed. Decimal comma and point are accepted; mixed decimal/thousands separators, invalid ranges and fractional ages are rejected without modifying the saved version.

Revisions contain changed field names, UTC time, actor and an input hash. Re-saving identical values/review status does not create a new revision. Decimal formatting alone does not produce a false unsaved-data indicator. `confirmed_value()` is the future adapter contract: it refuses missing or unconfirmed facts, and must never supply implicit negative values to a score. `case_data()` gives a guarded server-side interchange representation; it is not a provider-ready AI payload.

The current saved case/draft and revision metadata exist only in the session. This is not a longitudinal patient-history feature. A new case clears the previous patient's draft/widgets and independent reports. Do not deploy patient-data storage or send full internal case objects to providers without the later approved privacy design.

## Calculation and report traceability

Independent numerical records identify their algorithm, implementation version, inputs hash and computation time. Pro PDFs retain their source documentation and add template/report version and calculation metadata to PDF document properties. Input or language changes invalidate numerical/PDF caches. The existing ECG path still requires clinician-authored findings, explicit manual review and a valid upload; it makes no automated diagnosis.

## Validation and release status

Tests cover the original equations and multilingual report paths plus permission enforcement, forged/expired/revoked contexts, ownership isolation, no PDF/report generation in Free, three-state clinical data, provenance/versioning, shared forms, draft retention, language changes and session cleanup. No model's clinical validation is inferred from passing software tests.

This feature branch is for review. It does not merge the calculator-repair PR, change `main`, activate billing or deploy new clinical functions. The complete strategic specification remains in Pablo's saved planning document; this file records only the implemented stage-1 scope and its technical operating contract.
