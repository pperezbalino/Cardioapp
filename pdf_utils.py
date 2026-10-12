"""In-memory multilingual PDF reports; no patient-named files on disk."""
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
import re
import json
import threading
from xml.sax.saxutils import escape

import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Flowable, Image
from pypdf import PdfReader, PdfWriter
from access import Feature, require

ROOT = Path(__file__).resolve().parent
_FONT_LOCK = threading.Lock()


def register_fonts():
    with _FONT_LOCK:
        if 'Cardio' not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont('Cardio', str(ROOT / 'assets/fonts/DejaVuSans.ttf')))
            pdfmetrics.registerFont(TTFont('CardioBold', str(ROOT / 'assets/fonts/DejaVuSans-Bold.ttf')))
            pdfmetrics.registerFontFamily('Cardio', normal='Cardio', bold='CardioBold',
                                        italic='Cardio', boldItalic='CardioBold')


def visual(text):
    # Isolate scientific notation/Latin runs: inequalities, percentages, dates and units
    # must keep their left-to-right order inside otherwise right-to-left text.
    text = re.sub(r'[<>≤≥≈]?[A-Za-z0-9][A-Za-z0-9<>≤≥≈%/.:+_\-²₂]*(?:[ \t]+[<>≤≥≈]?[A-Za-z0-9][A-Za-z0-9<>≤≥≈%/.:+_\-²₂]*)*',
                  lambda match: '\u202a' + match.group(0) + '\u202c', text)
    return get_display(arabic_reshaper.reshape(text))


class RTLText(Flowable):
    """Wrap logical text first, then shape and reorder each individual line."""
    def __init__(self, text, size=10, bold=False):
        super().__init__()
        self.text = text
        self.size = size
        self.font = 'CardioBold' if bold else 'Cardio'
        self.leading = size * 1.5
        self.keepWithNext = bold

    def wrap(self, avail_width, avail_height):
        self.width = avail_width
        self.lines = []
        current = ''
        for word in self.text.split():
            candidate = (current + ' ' + word).strip()
            if pdfmetrics.stringWidth(visual(candidate), self.font, self.size) <= avail_width:
                current = candidate
                continue
            if current:
                self.lines.append(visual(current)); current = ''
            for char in word:
                candidate = current + char
                if current and pdfmetrics.stringWidth(visual(candidate), self.font, self.size) > avail_width:
                    self.lines.append(visual(current)); current = char
                else:
                    current = candidate
        if current:
            self.lines.append(visual(current))
        self.height = max(1, len(self.lines)) * self.leading
        return self.width, self.height

    def draw(self):
        self.canv.setFont(self.font, self.size)
        for i, line in enumerate(self.lines):
            self.canv.drawRightString(self.width, self.height - (i + 1) * self.leading + 3, line)


def make_report(title, inputs, results, note, sources, t, *, context=None):
    require(context, Feature.PDF)
    return dict(title=title, inputs=list(inputs), results=list(results), note=note,
                sources=list(sources), lang=t['_lang'],
                owner=context.subject, template_version='1.1', report_version=1,
                generated_at=datetime.now(timezone.utc).isoformat(timespec='seconds'))


def generate_pdf(report, t, *, context=None):
    require(context, Feature.PDF)
    if report.get('owner') != context.subject:
        raise PermissionError('report_owner')
    register_fonts()
    buffer = BytesIO()
    normal = ParagraphStyle('CardioBody', fontName='Cardio', fontSize=10, leading=15,
                            spaceAfter=7, splitLongWords=True)
    heading = ParagraphStyle('CardioHeading', parent=normal, fontName='CardioBold',
                             fontSize=12, leading=17, spaceBefore=10, keepWithNext=True)
    rtl = t['_lang'] == 'ar'
    if rtl:
        normal.alignment = heading.alignment = TA_RIGHT

    def para(text, bold=False):
        if rtl:
            return RTLText(str(text), size=12 if bold else 10, bold=bold)
        return Paragraph(escape(str(text)), heading if bold else normal)

    def heading_gap(height):
        gap = Spacer(1, height)
        gap.keepWithNext = True
        return gap

    story = [para(report['title'], True), Spacer(1, 10),
             para(f"{t['generated_at']}: {report['generated_at']}"), heading_gap(8)]
    if report.get('priority_note'):
        story += [para(report['priority_note']), Spacer(1, 8)]
    for name, items in [(t['inputs'], report['inputs']), (t['result'], report['results'])]:
        story += [para(name, True), heading_gap(8)]
        for label, value in items:
            text = f'{label}: {value}'
            for line in text.splitlines() or ['']:
                if rtl:
                    # Small logical chunks remain splittable across pages.
                    words = line.split(); chunks = []; current = ''
                    for word in words:
                        if len(current) + len(word) > 220 and current:
                            chunks.append(current); current = ''
                        current = (current + ' ' + word).strip()
                        while len(current) > 220:
                            chunks.append(current[:220]); current = current[220:]
                    if current: chunks.append(current)
                    for chunk in chunks:
                        story += [para(chunk), Spacer(1, 3)]
                else:
                    story.append(para(line))
        story.append(heading_gap(8))
    attachment = report.get('attachment')
    if attachment and not attachment['name'].lower().endswith('.pdf'):
        image_reader = ImageReader(BytesIO(attachment['data']))
        width, height = image_reader.getSize()
        scale = min(490 / width, 550 / height)
        story += [para(t['attached_file'], True), heading_gap(8),
                  Image(BytesIO(attachment['data']), width=width * scale, height=height * scale),
                  Spacer(1, 12)]
    story += [para(report['note']), Spacer(1, 10), para(t['references'], True), heading_gap(8)]
    for source in report['sources']:
        story += [para(source), Spacer(1, 4)]
    story += [Spacer(1, 12), para(t['pdf_disclaimer'])]

    def decorate(canvas, doc):
        canvas.saveState()
        canvas.setTitle(report['title']); canvas.setAuthor('CardioApp')
        canvas.setSubject(json.dumps({key: report[key] for key in
            ['template_version', 'report_version', 'algorithm_id', 'algorithm_version', 'input_hash', 'case_id', 'case_revision',
             'review_hash', 'reviewed_by', 'reviewed_at', 'pathway_id', 'pathway_version']
            if key in report}, sort_keys=True))
        logo = ROOT / 'logo.png'
        if logo.exists():
            canvas.drawImage(ImageReader(str(logo)), 42, doc.pagesize[1] - 66,
                             width=34, height=34, preserveAspectRatio=True, mask='auto')
        canvas.setFillColor(colors.HexColor('#174a62')); canvas.setFont('CardioBold', 12)
        header = visual(t['pdf_title']) if rtl else t['pdf_title']
        canvas.drawRightString(doc.pagesize[0] - 42, doc.pagesize[1] - 49, header)
        canvas.setStrokeColor(colors.HexColor('#c4d9e3'))
        canvas.line(42, doc.pagesize[1] - 75, doc.pagesize[0] - 42, doc.pagesize[1] - 75)
        canvas.setFont('Cardio', 9)
        page_label = f"{t['page']} {doc.page}"
        canvas.drawRightString(doc.pagesize[0] - 42, 27, visual(page_label) if rtl else page_label)
        canvas.restoreState()

    doc = SimpleDocTemplate(buffer, rightMargin=42, leftMargin=42,
                            topMargin=90, bottomMargin=45)
    doc.build(story, onFirstPage=decorate, onLaterPages=decorate)
    if attachment:
        writer = PdfWriter()
        writer.clone_document_from_reader(PdfReader(BytesIO(buffer.getvalue())))
        writer.add_attachment(attachment['name'], attachment['data'])
        output = BytesIO()
        writer.write(output)
        return output.getvalue()
    return buffer.getvalue()
