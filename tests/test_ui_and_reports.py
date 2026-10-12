from io import BytesIO
from pathlib import Path
import hashlib

import pytest
from PIL import Image
from pypdf import PdfReader, PdfWriter
from streamlit.testing.v1 import AppTest

from pdf_utils import make_report, generate_pdf
from tools.ecg_analysis import validate_upload, manual_report
from translations import LANGUAGES, translations

ROOT = Path(__file__).resolve().parents[1]


def start_app(lang='es', pro=True):
    app = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=15).run()
    assert not app.exception
    app.selectbox(key='language').set_value(lang).run()
    app.button(key='accept_disclaimer').click().run()
    assert not app.exception
    if pro:
        app.text_input(key='access:code').set_value('test-only-cardioapp-pro-invite-0001').run()
        app.button(key='access:login').click().run()
        assert not app.exception
    return app


@pytest.mark.parametrize('lang', LANGUAGES)
def test_all_calculator_screens_and_pdfs(lang):
    app = start_app(lang)
    t = translations[lang]
    for module in ['framingham', 'euroscore', 'chads', 'grace', 'has_bled', 'timi', 'bmi', 'ckd']:
        app.selectbox(key='score').set_value(module).run()
        assert not app.exception, (lang, module)
        if module == 'has_bled':
            app.checkbox(key='has_bled:has_bled_reviewed').check().run()
        app.button(key=f'calculate:{module}').click().run()
        assert not app.exception, (lang, module)
        assert app.success
        saved = app.session_state[f'calculation:{module}']
        reader = PdfReader(BytesIO(saved['pdf']))
        assert len(reader.pages) >= 1
        assert saved['report']['lang'] == lang
        # Each visible widget must use the selected catalogue rather than hard-coded Spanish.
        assert app.number_input[0].label == t['weight' if module == 'bmi' else 'age']
        assert app.button(key=f'calculate:{module}').label == t['calculate']


def test_report_persists_and_is_invalidated_on_input_and_language_change():
    app = start_app()
    app.button(key='calculate:framingham').click().run()
    original = app.session_state['calculation:framingham']['pdf']
    app.run()
    assert app.session_state['calculation:framingham']['pdf'] == original
    app.number_input(key='framingham:age').set_value(65).run()
    assert 'calculation:framingham' not in app.session_state
    assert not app.success
    app.button(key='calculate:framingham').click().run()
    app.selectbox(key='language').set_value('en').run()
    assert 'calculation:framingham' not in app.session_state
    app.button(key='calculate:framingham').click().run()
    assert app.session_state['calculation:framingham']['report']['lang'] == 'en'
    app.selectbox(key='score').set_value('bmi').run()
    app.selectbox(key='score').set_value('framingham').run()
    # Streamlit may reset hidden widgets; any changed values must invalidate old reports.
    if 'calculation:framingham' in app.session_state:
        assert app.session_state['calculation:framingham']['report']['inputs'][0][1] == str(app.number_input(key='framingham:age').value)


def test_framingham_exclusion_and_sex_only_af_in_ui():
    app = start_app()
    app.checkbox(key='framingham:diabetes').check().run()
    app.button(key='calculate:framingham').click().run()
    assert app.error[0].value == translations['es']['framingham_ineligible']
    assert not app.success
    app.selectbox(key='score').set_value('chads').run()
    app.number_input(key='chads:age').set_value(40).run()
    app.selectbox(key='chads:sex').set_value('F').run()
    app.button(key='calculate:chads').click().run()
    assert not app.exception
    assert translations['es']['af_low'] in app.success[-1].value


@pytest.mark.parametrize('lang', LANGUAGES)
def test_drug_and_ecg_validation_in_all_languages(lang):
    app = start_app(lang)
    app.button(key='calculate:drugs').click().run()
    assert not app.exception
    assert translations[lang]['invalid_input'] in [x.value for x in app.error]
    app.selectbox(key='drugs:select_drug').set_value('lidocaine').run()
    app.number_input(key='drugs:dose:lidocaine').set_value(1.0).run()
    app.number_input(key='drugs:total_mg').set_value(1000.0).run()
    app.number_input(key='drugs:final_ml').set_value(250.0).run()
    app.button(key='calculate:drugs').click().run()
    assert not app.exception
    assert app.session_state['calculation:drugs']['report']['results'][0][1] == '15 mL/h'
    assert all('weight' not in str(x) for x in app.session_state['calculation:drugs']['report']['inputs'])
    app.button(key='calculate:ecg').click().run()
    assert not app.exception
    assert translations[lang]['ecg_required'] in [x.value for x in app.error]
    assert 'report:ecg' not in app.session_state


def png_bytes():
    buffer = BytesIO()
    Image.new('RGB', (500, 200), 'white').save(buffer, format='PNG')
    return buffer.getvalue()


@pytest.mark.parametrize('data,name', [(b'', 'empty.png'), (b'not an image', 'fake.png'),
                                       (b'not a PDF', 'fake.pdf'), (b'junk', 'file.exe')])
def test_invalid_ecg_files_never_generate_diagnosis(data, name, pro_context):
    with pytest.raises(ValueError, match='invalid_file'):
        manual_report(data, name, 'AB', '123', 'test', True, translations['es'], context=pro_context)


def test_manual_ecg_requires_author_and_confirmation(pro_context):
    data = png_bytes()
    for fields in [('', '123', 'Written findings', True), ('AB', '', 'Written findings', True),
                   ('AB','123','',True), ('AB','123','Written findings',False)]:
        with pytest.raises(ValueError, match='ecg_required'):
            manual_report(data, 'trace.png', *fields, translations['es'], context=pro_context)


@pytest.mark.parametrize('lang', LANGUAGES)
def test_ecg_report_embeds_original_and_only_authored_findings(lang, pro_context):
    data = png_bytes()
    report = manual_report(data, 'trace.png', 'AB', '123', 'TEST: clinician authored findings <>&', True, translations[lang], context=pro_context)
    pdf = generate_pdf(report, translations[lang], context=pro_context)
    reader = PdfReader(BytesIO(pdf))
    assert reader.attachments['trace.png'][0] == data
    assert hashlib.sha256(data).hexdigest() == report['inputs'][3][1]
    assert report['results'][0][1] == 'TEST: clinician authored findings <>&'
    assert 'ECG dentro de límites normales' not in str(report)
    assert any(page.images for page in reader.pages)
    if lang != 'ar':
        text = '\n'.join(page.extract_text() for page in reader.pages)
        assert 'TEST: clinician authored findings <>&' in text
        assert translations[lang]['manual_status'] in text


def test_pdf_ecg_upload_and_attachment_and_encryption(pro_context):
    writer = PdfWriter(); writer.add_blank_page(width=600,height=300)
    output = BytesIO(); writer.write(output); original = output.getvalue()
    assert validate_upload(original, 'trace.pdf')['pages'] == 1
    report = manual_report(original, 'trace.pdf', 'AB','123','Written interpretation',True,translations['es'], context=pro_context)
    result = PdfReader(BytesIO(generate_pdf(report, translations['es'], context=pro_context)))
    assert result.attachments['trace.pdf'][0] == original
    writer.encrypt('password'); encrypted = BytesIO(); writer.write(encrypted)
    with pytest.raises(ValueError): validate_upload(encrypted.getvalue(), 'encrypted.pdf')


@pytest.mark.parametrize('lang', LANGUAGES)
def test_unicode_long_reports_paginate_without_losing_text(lang, pro_context):
    t = translations[lang]
    text = (t['ecg_note'] + ' ') * 100
    report = make_report(t['ecg'], [(t['patient_initials'],'AB')], [(t['findings'],text)],
                         t['ecg_note'], [t['manual_status']], t, context=pro_context)
    pdf = generate_pdf(report, t, context=pro_context)
    reader = PdfReader(BytesIO(pdf))
    assert 2 <= len(reader.pages) <= 25
    assert all(page.extract_text().strip() for page in reader.pages)


def test_catalogues_have_identical_complete_keys():
    expected = set(translations['es'])
    for lang, catalogue in translations.items():
        assert set(catalogue) == expected
        assert all(isinstance(x,str) and x for x in catalogue.values())


def test_arabic_scientific_notation_keeps_ltr_order():
    from pdf_utils import visual
    for value in ['2.07%', '<1%', '≥30%', '>50', '≤85', 'mL/min', '2026-10-12T00:00:00+00:00']:
        assert value in visual('النتيجة: ' + value)


def test_manual_ecg_ui_generates_and_invalidates_report(monkeypatch):
    class Upload(BytesIO):
        name = 'trace.png'
    uploaded = Upload(png_bytes())
    import streamlit as st
    monkeypatch.setattr(st, 'file_uploader', lambda *args, **kwargs: uploaded)
    app = start_app()
    app.text_input(key='ecg:initials').set_value('AB').run()
    app.text_input(key='ecg:registration').set_value('123').run()
    app.text_area(key='ecg:findings').set_value('Only a clinician-authored finding').run()
    app.checkbox(key='ecg:confirmed').check().run()
    app.button(key='calculate:ecg').click().run()
    assert not app.exception
    assert app.session_state['report:ecg']['report']['results'][0][1] == 'Only a clinician-authored finding'
    assert PdfReader(BytesIO(app.session_state['report:ecg']['pdf'])).attachments['trace.png'][0] == uploaded.getvalue()
    app.run()
    assert 'report:ecg' in app.session_state
    app.text_area(key='ecg:findings').set_value('Changed findings').run()
    assert not app.exception
    assert 'report:ecg' not in app.session_state
