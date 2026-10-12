"""Manual ECG documentation with validated upload; no synthetic diagnoses."""
import hashlib
from io import BytesIO
from pathlib import Path
import warnings

from PIL import Image, UnidentifiedImageError
from pypdf import PdfReader
import streamlit as st

from clinical_ui import fingerprint, show_result
from pdf_utils import make_report, generate_pdf

MAX_BYTES = 10 * 1024 * 1024


def validate_upload(data, filename):
    if not data or len(data) > MAX_BYTES:
        raise ValueError('invalid_file')
    extension = Path(filename).suffix.lower()
    try:
        if extension == '.pdf':
            reader = PdfReader(BytesIO(data))
            if reader.is_encrypted or not 1 <= len(reader.pages) <= 30:
                raise ValueError('invalid_file')
            return {'kind': 'pdf', 'pages': len(reader.pages)}
        if extension not in ('.png', '.jpg', '.jpeg'):
            raise ValueError('invalid_file')
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(BytesIO(data)) as image:
                if image.format not in ('PNG', 'JPEG') or image.width * image.height > 25_000_000:
                    raise ValueError('invalid_file')
                image.verify()
            with Image.open(BytesIO(data)) as image:
                image.load()
        return {'kind': 'image'}
    except (ValueError, OSError, UnidentifiedImageError, Image.DecompressionBombWarning,
            Image.DecompressionBombError) as error:
        raise ValueError('invalid_file') from error
    except Exception as error:
        raise ValueError('invalid_file') from error


def manual_report(data, filename, initials, registration, findings, confirmed, t):
    validate_upload(data, filename)
    if not all([initials.strip(), registration.strip(), findings.strip(), confirmed]):
        raise ValueError('ecg_required')
    inputs = [(t['patient_initials'], initials.strip()), (t['license_number'], registration.strip()),
              (t['attached_file'], Path(filename).name),
              (t['file_hash'], hashlib.sha256(data).hexdigest()),
              (t['confirm_manual'], t['yes'])]
    report = make_report(t['ecg'], inputs, [(t['findings'], findings.strip()),
                         (t['result'], t['manual_status'])], t['ecg_note'], [t['manual_status']], t)
    report['attachment'] = {'name': Path(filename).name, 'data': data}
    return report


def calcular(t):
    st.subheader(t['ecg']); st.info(t['ecg_note'])
    uploaded = st.file_uploader(t['upload'], type=['png', 'jpg', 'jpeg', 'pdf'], key='ecg:upload')
    data = uploaded.getvalue() if uploaded is not None else b''
    filename = uploaded.name if uploaded is not None else ''
    valid = False
    if uploaded is not None:
        try:
            info = validate_upload(data, filename); valid = True
            if info['kind'] == 'image':
                st.image(data, width='stretch')
            else:
                st.caption(f"{t['pages']}: {info['pages']}")
            st.download_button(t['view_original'], data=data, file_name=Path(filename).name,
                               mime='application/pdf' if info['kind'] == 'pdf' else 'image/' + ('png' if filename.lower().endswith('.png') else 'jpeg'),
                               key='ecg:original')
        except ValueError:
            st.error(t['invalid_file'])
    initials = st.text_input(t['patient_initials'], max_chars=40, key='ecg:initials')
    registration = st.text_input(t['license_number'], max_chars=80, key='ecg:registration')
    findings = st.text_area(t['findings'], max_chars=20000, height=180, key='ecg:findings')
    confirmed = st.checkbox(t['confirm_manual'], key='ecg:confirmed')
    values = {'sha256': hashlib.sha256(data).hexdigest(), 'filename': filename,
              'initials': initials, 'registration': registration,
              'findings': findings, 'confirmed': confirmed}
    if st.button(t['create_report'], key='calculate:ecg'):
        try:
            if not valid:
                raise ValueError('ecg_required')
            report = manual_report(data, filename, initials, registration, findings, confirmed, t)
            st.session_state['report:ecg'] = {'fingerprint': fingerprint(values, t),
                                            'report': report, 'pdf': generate_pdf(report, t)}
        except ValueError as error:
            st.session_state.pop('report:ecg', None); st.error(t[str(error)])
    show_result('ecg', values, t)
