"""
Data Arsenal v1 - PDF Report Generator
Professional GA4 health check PDF using fpdf2.
"""

import os
import re
import sys
from datetime import date

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(SCRIPT_DIR, 'fonts')

# Venv auto-activation (same as _ga4_lib.py)
_config_dir = os.path.expanduser('~/.config/data-arsenal')
_venv_site = os.path.join(_config_dir, 'venv', 'lib')
_venv_site_win = os.path.join(_config_dir, 'venv', 'Lib', 'site-packages')
if os.path.isdir(_venv_site_win) and _venv_site_win not in sys.path:
    sys.path.insert(0, _venv_site_win)
elif os.path.isdir(_venv_site):
    for _d in os.listdir(_venv_site):
        _sp = os.path.join(_venv_site, _d, 'site-packages')
        if os.path.isdir(_sp) and _sp not in sys.path:
            sys.path.insert(0, _sp)
            break

try:
    from fpdf import FPDF
except ImportError:
    print("ERROR: fpdf2 not installed. Run ga4-setup to install dependencies.", file=sys.stderr)
    sys.exit(1)

from _translations import get_translator

# Colors
COLOR_GREEN = (34, 139, 34)
COLOR_YELLOW = (204, 153, 0)
COLOR_RED = (204, 51, 51)
COLOR_GRAY = (128, 128, 128)
COLOR_BLUE = (51, 102, 153)
COLOR_WHITE = (255, 255, 255)
COLOR_LIGHT_GRAY = (245, 245, 245)
COLOR_DARK = (51, 51, 51)

STATUS_COLORS = {
    'PASS': COLOR_GREEN,
    'WARN': COLOR_YELLOW,
    'FAIL': COLOR_RED,
    'SKIP': COLOR_GRAY,
    'INFO': COLOR_BLUE,
}

GATEWAY_PATTERNS = [
    'stripe', 'paypal', 'square', 'braintree', 'adyen', 'mollie',
    'checkout.com', 'worldpay', 'klarna', 'shopify.com/pay'
]


def _score_color(score):
    """Return color tuple based on health score."""
    if score >= 80:
        return COLOR_GREEN
    if score >= 50:
        return COLOR_YELLOW
    return COLOR_RED


def _slugify(text):
    """Simple slugify for filenames."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')[:50]


def _default_output_path(property_name):
    """Return default PDF output path on Desktop."""
    desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    if not os.path.isdir(desktop):
        desktop = os.path.expanduser('~')
    slug = _slugify(property_name)
    today = date.today().strftime('%Y-%m-%d')
    return os.path.join(desktop, f'ga4-audit-{slug}-{today}.pdf')


def _safe_text(text):
    """Sanitize text for PDF - replace emoji and problematic characters."""
    if not text:
        return ''
    # Replace emoji with text alternatives (DejaVu fonts don't support emoji)
    text = text.replace('\u2705', '[OK]').replace('\u2713', '[OK]')   # ✅ ✓
    text = text.replace('\u274c', '[X]').replace('\u2717', '[X]')     # ❌ ✗
    text = text.replace('\u26a0\ufe0f', '[!]').replace('\u26a0', '[!]')  # ⚠️ ⚠
    text = text.replace('\U0001f511', '*')                             # 🔑
    text = text.replace('\U0001f4a1', '*')                             # 💡
    text = text.replace('\U0001f4ca', '')                              # 📊
    text = text.replace('\U0001f6a8', '[!]')                           # 🚨
    text = text.replace('\u2139\ufe0f', '[i]').replace('\u2139', '[i]')  # ℹ️ ℹ
    # Smart quotes and dashes
    text = text.replace('\u2013', '-').replace('\u2014', '-')
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    # Bullet alternatives
    text = text.replace('\u2022', '-')                                 # •
    text = text.replace('\u25cf', '-')                                 # ●
    return text


class AuditPDF(FPDF):
    """Custom PDF class for GA4 audit reports."""

    def __init__(self, lang='en'):
        super().__init__()
        self.t = get_translator(lang)
        self._setup_fonts()

    def _setup_fonts(self):
        """Register DejaVu fonts for Unicode/Cyrillic support."""
        regular = os.path.join(FONTS_DIR, 'DejaVuSans.ttf')
        bold = os.path.join(FONTS_DIR, 'DejaVuSans-Bold.ttf')

        # Check installed location too
        installed_fonts = os.path.join(_config_dir, 'scripts', 'fonts')
        if not os.path.exists(regular) and os.path.isdir(installed_fonts):
            regular = os.path.join(installed_fonts, 'DejaVuSans.ttf')
            bold = os.path.join(installed_fonts, 'DejaVuSans-Bold.ttf')

        if os.path.exists(regular):
            self.add_font('DejaVu', '', regular)
            self.add_font('DejaVu', 'B', bold)
            self._font_family = 'DejaVu'
        else:
            self._font_family = 'Helvetica'

    def header(self):
        pass  # Custom header in content

    def footer(self):
        self.set_y(-15)
        self.set_font(self._font_family, '', 8)
        self.set_text_color(*COLOR_GRAY)
        page_text = f"{self.t['pdf']['page']} {self.page_no()}/{{nb}}"
        self.cell(0, 10, page_text, 0, 0, 'L')
        self.cell(0, 10, self.t['pdf']['footer'], 0, 0, 'R')


def generate_pdf(property_name, results, score, data, lang='en', output_path=None):
    """Generate PDF report, return file path."""
    t = get_translator(lang)

    if not output_path:
        output_path = _default_output_path(property_name)

    pdf = AuditPDF(lang=lang)
    pdf.alias_nb_pages()
    pdf.add_page()
    ff = pdf._font_family

    # --- Header ---
    pdf.set_font(ff, 'B', 22)
    pdf.set_text_color(*COLOR_DARK)
    pdf.cell(0, 12, _safe_text(t['report_title']), 0, 1, 'L')

    pdf.set_font(ff, '', 12)
    pdf.set_text_color(*COLOR_GRAY)
    pdf.cell(0, 7, _safe_text(property_name), 0, 1, 'L')
    pdf.cell(0, 7, date.today().strftime('%B %d, %Y'), 0, 1, 'L')
    pdf.ln(5)

    # --- Health Score ---
    score_color = _score_color(score)
    pdf.set_font(ff, 'B', 48)
    pdf.set_text_color(*score_color)
    pdf.cell(50, 30, str(score), 0, 0, 'L')

    pdf.set_font(ff, '', 14)
    pdf.set_text_color(*COLOR_GRAY)
    x_after_score = pdf.get_x()
    y_score = pdf.get_y()
    pdf.set_xy(x_after_score, y_score + 5)
    pdf.cell(0, 8, _safe_text(f"/ 100  {t['health_score']}"), 0, 1, 'L')

    # Summary counts
    fails = sum(1 for r in results if r['status'] == 'FAIL')
    warns = sum(1 for r in results if r['status'] == 'WARN')
    passes = sum(1 for r in results if r['status'] == 'PASS')

    pdf.set_xy(x_after_score, pdf.get_y())
    pdf.set_font(ff, '', 10)
    summary_parts = []
    if fails:
        summary_parts.append(f"{fails} {t['status_labels']['FAIL']}")
    if warns:
        summary_parts.append(f"{warns} {t['status_labels']['WARN']}")
    summary_parts.append(f"{passes} {t['status_labels']['PASS']}")
    pdf.cell(0, 6, _safe_text('  |  '.join(summary_parts)), 0, 1, 'L')

    pdf.ln(8)

    # --- Results Table ---
    col_widths = [10, 58, 22, 100]  # #, Check, Status, Details
    page_width = pdf.w - pdf.l_margin - pdf.r_margin
    # Scale columns to fit page width
    total = sum(col_widths)
    col_widths = [w / total * page_width for w in col_widths]

    # Table header
    pdf.set_font(ff, 'B', 9)
    pdf.set_fill_color(51, 51, 51)
    pdf.set_text_color(*COLOR_WHITE)
    headers = [t['table_headers']['num'], t['table_headers']['check'],
               t['table_headers']['status'], t['table_headers']['details']]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 8, _safe_text(header), 0, 0, 'C', True)
    pdf.ln()

    # Table rows
    pdf.set_font(ff, '', 8)
    for i, r in enumerate(results, 1):
        check_name = t['check_names'].get(r['check'], r['check'])
        status_label = t['status_labels'].get(r['status'], r['status'])
        status_color = STATUS_COLORS.get(r['status'], COLOR_GRAY)
        detail = r['detail']

        # Alternate row background
        if i % 2 == 0:
            pdf.set_fill_color(*COLOR_LIGHT_GRAY)
            fill = True
        else:
            pdf.set_fill_color(*COLOR_WHITE)
            fill = True

        # Calculate row height based on detail text length
        detail_width = col_widths[3] - 2
        # Estimate lines needed
        char_per_line = max(1, int(detail_width / 1.8))
        lines_needed = max(1, (len(detail) + char_per_line - 1) // char_per_line)
        row_h = max(7, lines_needed * 4.5)

        # Check if we need a new page
        if pdf.get_y() + row_h > pdf.h - 25:
            pdf.add_page()
            # Re-draw table header
            pdf.set_font(ff, 'B', 9)
            pdf.set_fill_color(51, 51, 51)
            pdf.set_text_color(*COLOR_WHITE)
            for j, header in enumerate(headers):
                pdf.cell(col_widths[j], 8, _safe_text(header), 0, 0, 'C', True)
            pdf.ln()
            pdf.set_font(ff, '', 8)

        y_before = pdf.get_y()

        # Row number
        pdf.set_text_color(*COLOR_DARK)
        if i % 2 == 0:
            pdf.set_fill_color(*COLOR_LIGHT_GRAY)
        else:
            pdf.set_fill_color(*COLOR_WHITE)
        pdf.cell(col_widths[0], row_h, str(i), 0, 0, 'C', fill)

        # Check name
        pdf.cell(col_widths[1], row_h, _safe_text(check_name), 0, 0, 'L', fill)

        # Status (colored)
        pdf.set_text_color(*status_color)
        pdf.set_font(ff, 'B', 8)
        pdf.cell(col_widths[2], row_h, _safe_text(status_label), 0, 0, 'C', fill)

        # Details (multi-line via multi_cell)
        pdf.set_text_color(*COLOR_DARK)
        pdf.set_font(ff, '', 7.5)
        x_detail = pdf.get_x()
        pdf.multi_cell(col_widths[3], 4.5, _safe_text(detail), 0, 'L', fill)

        # Ensure next row starts at the right y position
        y_after = pdf.get_y()
        actual_h = max(row_h, y_after - y_before)
        pdf.set_y(max(y_before + row_h, y_after))

        pdf.set_font(ff, '', 8)

    pdf.ln(8)

    # --- What to Fix Section ---
    actionable = [r for r in results if r['status'] in ('FAIL', 'WARN')]
    if actionable:
        # New page if not enough space
        if pdf.get_y() > pdf.h - 60:
            pdf.add_page()

        pdf.set_font(ff, 'B', 14)
        pdf.set_text_color(*COLOR_DARK)
        pdf.cell(0, 10, _safe_text(t['what_to_fix']), 0, 1, 'L')
        pdf.ln(2)

        for r in actionable:
            check_name = t['check_names'].get(r['check'], r['check'])
            status = r['status']
            status_color = STATUS_COLORS.get(status, COLOR_GRAY)
            remediation_dict = t.get('remediation', {}).get(r['check'], {})
            remediation = remediation_dict.get(status, r['detail'])

            if status == 'FAIL':
                priority = t['priority_critical']
            else:
                priority = t['priority_recommended']

            # Check if we need a new page
            if pdf.get_y() > pdf.h - 35:
                pdf.add_page()

            # Check name + priority
            pdf.set_font(ff, 'B', 9)
            pdf.set_text_color(*status_color)
            pdf.cell(0, 6, _safe_text(f"{check_name} ({priority})"), 0, 1, 'L')

            # Remediation text
            pdf.set_font(ff, '', 8)
            pdf.set_text_color(*COLOR_DARK)
            pdf.multi_cell(0, 4.5, _safe_text(remediation))

            # Gateway breakdown table if applicable
            if r['check'] == 'Payment Gateway Referral' and data:
                _render_gateway_table(pdf, data, ff)

            pdf.ln(3)

    # --- Footer note ---
    if pdf.get_y() > pdf.h - 30:
        pdf.add_page()
    pdf.ln(5)
    pdf.set_font(ff, '', 8)
    pdf.set_text_color(*COLOR_GRAY)
    pdf.multi_cell(0, 4, _safe_text(t['footer_note']))

    pdf.ln(3)
    pdf.set_font(ff, 'B', 8)
    pdf.cell(0, 5, _safe_text(t['pdf']['generated_by']), 0, 1, 'L')

    # Write PDF
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    pdf.output(output_path)
    return output_path


# --- Brief PDF ---

# Tag colors for brief findings
TAG_COLORS = {
    'NEW': COLOR_GREEN,
    'ONGOING': (255, 140, 0),       # orange
    'WORSENING': COLOR_RED,
    'IMPROVING': COLOR_BLUE,
    'НОВО': COLOR_GREEN,
    'ПРОДЪЛЖАВА': (255, 140, 0),
    'ВЛОШАВА СЕ': COLOR_RED,
    'ПОДОБРЯВА СЕ': COLOR_BLUE,
}

VERDICT_COLORS = {
    'CONFIRMED': COLOR_GREEN,
    'REFUTED': COLOR_RED,
    'INCONCLUSIVE': COLOR_YELLOW,
    'ПОТВЪРДЕНО': COLOR_GREEN,
    'ОПРОВЕРГАНО': COLOR_RED,
    'НЕОПРЕДЕЛЕНО': COLOR_YELLOW,
}

PRIORITY_COLORS = {
    'high': COLOR_RED,
    'medium': COLOR_YELLOW,
    'low': COLOR_GREEN,
    'висок': COLOR_RED,
    'среден': COLOR_YELLOW,
    'нисък': COLOR_GREEN,
}


def _brief_output_path(property_name):
    """Return default brief PDF output path on Desktop."""
    desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    if not os.path.isdir(desktop):
        desktop = os.path.expanduser('~')
    slug = _slugify(property_name)
    today = date.today().strftime('%Y-%m-%d')
    return os.path.join(desktop, f'ga4-brief-{slug}-{today}.pdf')


def _ensure_page_space(pdf, needed_h):
    """Add a new page if there isn't enough space for needed_h mm."""
    if pdf.get_y() + needed_h > pdf.h - 20:
        pdf.add_page()


def generate_brief_pdf(property_name, period_info, key_insight, findings,
                       next_steps, context_notes=None, notable_mentions=None,
                       data_quality_score=None, baselines=None,
                       lang='en', output_path=None):
    """Generate brief (what-changed) PDF report, return file path.

    Args:
        property_name: Display name + property ID string
        period_info: dict with 'current', 'previous', 'days' keys
        key_insight: One-sentence key insight string
        findings: List of finding dicts (title, tag, metrics, pattern,
                  analysis, verdict, verdict_detail, action, effort)
        next_steps: List of dicts with 'action' and 'priority' keys
        context_notes: Optional list of context note strings
        notable_mentions: Optional list of notable mention strings
        data_quality_score: Optional int (0-100)
        baselines: Optional dict with CR/AOV baselines
        lang: Language code ('en' or 'bg')
        output_path: Optional output file path
    """
    t = get_translator(lang)
    bt = t.get('brief', {})
    tags_t = t.get('tags', {})
    verdicts_t = t.get('verdicts', {})
    priority_t = t.get('priority', {})
    effort_t = t.get('effort', {})

    if not output_path:
        output_path = _brief_output_path(property_name)

    pdf = AuditPDF(lang=lang)
    pdf.alias_nb_pages()
    pdf.add_page()
    ff = pdf._font_family
    page_w = pdf.w - pdf.l_margin - pdf.r_margin

    # --- Header ---
    pdf.set_font(ff, 'B', 22)
    pdf.set_text_color(*COLOR_DARK)
    title = bt.get('title', 'What Changed')
    pdf.cell(0, 12, _safe_text(title), 0, 1, 'L')

    pdf.set_font(ff, '', 11)
    pdf.set_text_color(*COLOR_GRAY)
    pdf.cell(0, 6, _safe_text(property_name), 0, 1, 'L')

    # Period line
    vs_label = bt.get('vs', 'vs')
    days_label = bt.get('days', 'days')
    period_text = (f"{period_info.get('current', '')} {vs_label} "
                   f"{period_info.get('previous', '')} "
                   f"({period_info.get('days', 7)} {days_label})")
    pdf.cell(0, 6, _safe_text(period_text), 0, 1, 'L')

    # Context + Data quality line
    meta_parts = []
    if data_quality_score is not None:
        dq_label = bt.get('data_quality', 'Data quality')
        meta_parts.append(f"{dq_label}: {data_quality_score}/100")
    if meta_parts:
        pdf.cell(0, 6, _safe_text(' | '.join(meta_parts)), 0, 1, 'L')

    # Baselines line
    if baselines:
        cr = baselines.get('conversion_rate', {})
        aov = baselines.get('aov', {})
        bl_parts = []
        cr_label = bt.get('cr', 'CR')
        aov_label = bt.get('aov', 'AOV')
        if cr:
            bl_parts.append(f"{cr_label} {cr.get('baseline', '')}% "
                           f"({bt.get('current', 'Current').lower()}: {cr.get('current', '')}%)")
        if aov:
            currency = aov.get('currency', '')
            bl_parts.append(f"{aov_label} {aov.get('baseline', '')} {currency} "
                           f"({bt.get('current', 'Current').lower()}: {aov.get('current', '')} {currency})")
        if bl_parts:
            bl_label = bt.get('baselines', 'Baselines')
            pdf.set_font(ff, '', 9)
            pdf.cell(0, 6, _safe_text(f"{bl_label}: {' | '.join(bl_parts)}"), 0, 1, 'L')

    pdf.ln(4)

    # --- Key Insight Box ---
    pdf.set_fill_color(230, 240, 250)  # light blue background
    pdf.set_draw_color(*COLOR_BLUE)
    pdf.set_font(ff, 'B', 11)
    pdf.set_text_color(*COLOR_BLUE)
    insight_label = bt.get('key_insight', 'Key Insight')
    pdf.cell(0, 7, _safe_text(insight_label), 0, 1, 'L')
    pdf.set_font(ff, '', 10)
    pdf.set_text_color(*COLOR_DARK)
    x = pdf.get_x()
    y = pdf.get_y()
    # Draw background rect
    lines_est = max(1, len(key_insight) // 80 + 1)
    box_h = lines_est * 5.5 + 4
    pdf.set_fill_color(230, 240, 250)
    pdf.rect(x, y, page_w, box_h, 'F')
    pdf.set_xy(x + 2, y + 2)
    pdf.multi_cell(page_w - 4, 5.5, _safe_text(key_insight), 0, 'L')
    pdf.set_y(max(pdf.get_y(), y + box_h) + 2)

    # --- Context Notes ---
    if context_notes:
        pdf.set_font(ff, '', 8.5)
        pdf.set_text_color(*COLOR_GRAY)
        for note in context_notes:
            pdf.multi_cell(page_w, 4.5, _safe_text(f"  {note}"), 0, 'L')
        pdf.ln(2)

    pdf.ln(3)

    # --- Findings ---
    finding_label = bt.get('finding', 'Finding')
    pattern_label = bt.get('pattern', 'Pattern')
    analysis_label = bt.get('analysis', 'Analysis')
    verdict_label = bt.get('verdict', 'Verdict')
    action_label = bt.get('action', 'Action')
    effort_label = bt.get('effort', 'Effort')

    for idx, f in enumerate(findings, 1):
        _ensure_page_space(pdf, 50)

        # --- Finding title bar ---
        tag = f.get('tag', 'NEW')
        tag_display = tags_t.get(tag, tag)
        tag_color = TAG_COLORS.get(tag_display, TAG_COLORS.get(tag, COLOR_GREEN))

        # Title background
        y_title = pdf.get_y()
        pdf.set_fill_color(245, 245, 248)
        pdf.rect(pdf.l_margin, y_title, page_w, 8, 'F')

        # Tag pill
        pdf.set_xy(pdf.l_margin + 1, y_title + 1)
        pdf.set_fill_color(*tag_color)
        pdf.set_text_color(*COLOR_WHITE)
        pdf.set_font(ff, 'B', 7)
        tag_w = pdf.get_string_width(f" {tag_display} ") + 4
        pdf.cell(tag_w, 6, f" {_safe_text(tag_display)} ", 0, 0, 'C', True)

        # Title text
        pdf.set_x(pdf.get_x() + 3)
        pdf.set_text_color(*COLOR_DARK)
        pdf.set_font(ff, 'B', 10)
        title_text = f"{finding_label} {idx}: {f.get('title', '')}"
        pdf.cell(0, 6, _safe_text(title_text), 0, 1, 'L')
        pdf.set_y(y_title + 10)

        # --- Metrics table ---
        metrics = f.get('metrics', [])
        if metrics:
            col_widths_m = [page_w * 0.35, page_w * 0.22, page_w * 0.22, page_w * 0.21]
            current_label = bt.get('current', 'Current')
            previous_label = bt.get('previous', 'Previous')
            change_label = bt.get('change', 'Change')

            # Table header
            pdf.set_font(ff, 'B', 8)
            pdf.set_fill_color(51, 51, 51)
            pdf.set_text_color(*COLOR_WHITE)
            m_headers = ['Metric', current_label, previous_label, change_label]
            for j, h in enumerate(m_headers):
                pdf.cell(col_widths_m[j], 6, _safe_text(h), 0, 0, 'C', True)
            pdf.ln()

            # Table rows
            pdf.set_font(ff, '', 8)
            for mi, m in enumerate(metrics):
                if mi % 2 == 0:
                    pdf.set_fill_color(*COLOR_LIGHT_GRAY)
                else:
                    pdf.set_fill_color(*COLOR_WHITE)
                pdf.set_text_color(*COLOR_DARK)
                pdf.cell(col_widths_m[0], 6, _safe_text(m.get('name', '')), 0, 0, 'L', True)
                pdf.cell(col_widths_m[1], 6, _safe_text(str(m.get('current', ''))), 0, 0, 'C', True)
                pdf.cell(col_widths_m[2], 6, _safe_text(str(m.get('previous', ''))), 0, 0, 'C', True)

                # Color the change cell
                change_str = str(m.get('change', ''))
                if change_str.startswith('-'):
                    pdf.set_text_color(*COLOR_RED)
                elif change_str.startswith('+'):
                    pdf.set_text_color(*COLOR_GREEN)
                pdf.cell(col_widths_m[3], 6, _safe_text(change_str), 0, 0, 'C', True)
                pdf.set_text_color(*COLOR_DARK)
                pdf.ln()
            pdf.ln(2)

        # --- Pattern ---
        pdf.set_font(ff, 'B', 8)
        pdf.set_text_color(*COLOR_BLUE)
        pdf.cell(25, 5, _safe_text(f"{pattern_label}:"), 0, 0, 'L')
        pdf.set_font(ff, '', 8)
        pdf.set_text_color(*COLOR_DARK)
        pdf.cell(0, 5, _safe_text(f.get('pattern', '')), 0, 1, 'L')

        # --- Analysis ---
        analysis = f.get('analysis', '')
        if analysis:
            _ensure_page_space(pdf, 15)
            pdf.set_font(ff, 'B', 8)
            pdf.set_text_color(*COLOR_BLUE)
            pdf.cell(25, 5, _safe_text(f"{analysis_label}:"), 0, 0, 'L')
            pdf.set_font(ff, '', 8)
            pdf.set_text_color(*COLOR_DARK)
            x_a = pdf.get_x()
            pdf.multi_cell(page_w - (x_a - pdf.l_margin), 4.5, _safe_text(analysis), 0, 'L')

        # --- Verdict ---
        _ensure_page_space(pdf, 10)
        verdict = f.get('verdict', '')
        verdict_display = verdicts_t.get(verdict, verdict)
        verdict_color = VERDICT_COLORS.get(verdict_display, VERDICT_COLORS.get(verdict, COLOR_GRAY))

        pdf.set_font(ff, 'B', 8)
        pdf.set_text_color(*COLOR_BLUE)
        pdf.cell(25, 5, _safe_text(f"{verdict_label}:"), 0, 0, 'L')
        pdf.set_font(ff, 'B', 8)
        pdf.set_text_color(*verdict_color)
        v_w = pdf.get_string_width(verdict_display) + 4
        pdf.cell(v_w, 5, _safe_text(verdict_display), 0, 0, 'L')
        pdf.set_font(ff, '', 8)
        pdf.set_text_color(*COLOR_DARK)
        detail = f.get('verdict_detail', '')
        if detail:
            pdf.cell(0, 5, _safe_text(f" - {detail}"), 0, 1, 'L')
        else:
            pdf.ln()

        # --- Action ---
        _ensure_page_space(pdf, 10)
        pdf.set_font(ff, 'B', 8)
        pdf.set_text_color(*COLOR_BLUE)
        pdf.cell(25, 5, _safe_text(f"{action_label}:"), 0, 0, 'L')
        pdf.set_font(ff, '', 8)
        pdf.set_text_color(*COLOR_DARK)
        action_text = f.get('action', '')
        effort = f.get('effort', '')
        if effort:
            effort_display = effort_t.get(effort, effort)
            action_text += f" [{effort_label}: {effort_display}]"
        x_act = pdf.get_x()
        pdf.multi_cell(page_w - (x_act - pdf.l_margin), 4.5, _safe_text(action_text), 0, 'L')

        # Separator line
        pdf.ln(3)
        if idx < len(findings):
            pdf.set_draw_color(220, 220, 220)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + page_w, pdf.get_y())
            pdf.ln(4)

    # --- Notable Mentions ---
    if notable_mentions:
        _ensure_page_space(pdf, 25)
        pdf.ln(3)
        pdf.set_font(ff, 'B', 12)
        pdf.set_text_color(*COLOR_DARK)
        notable_label = bt.get('notable', 'Notable Mentions')
        pdf.cell(0, 8, _safe_text(notable_label), 0, 1, 'L')
        pdf.set_font(ff, '', 9)
        pdf.set_text_color(*COLOR_GRAY)
        for mention in notable_mentions:
            _ensure_page_space(pdf, 8)
            pdf.cell(5, 5, '-', 0, 0, 'L')
            pdf.multi_cell(page_w - 5, 5, _safe_text(mention), 0, 'L')

    # --- Next Steps ---
    if next_steps:
        _ensure_page_space(pdf, 25)
        pdf.ln(4)
        pdf.set_font(ff, 'B', 12)
        pdf.set_text_color(*COLOR_DARK)
        ns_label = bt.get('next_steps', 'Next Steps')
        pdf.cell(0, 8, _safe_text(ns_label), 0, 1, 'L')

        for i, step in enumerate(next_steps, 1):
            _ensure_page_space(pdf, 8)
            priority = step.get('priority', '')
            priority_display = priority_t.get(priority, priority)
            p_color = PRIORITY_COLORS.get(priority_display, PRIORITY_COLORS.get(priority, COLOR_GRAY))

            pdf.set_font(ff, 'B', 9)
            pdf.set_text_color(*COLOR_DARK)
            pdf.cell(8, 6, f"{i}.", 0, 0, 'L')
            pdf.set_font(ff, '', 9)
            action_text = step.get('action', '')
            pdf.cell(0, 6, _safe_text(action_text), 0, 0, 'L')

            if priority:
                # Priority badge
                pdf.set_x(pdf.l_margin + page_w - 25)
                pdf.set_fill_color(*p_color)
                pdf.set_text_color(*COLOR_WHITE)
                pdf.set_font(ff, 'B', 7)
                pdf.cell(22, 5, _safe_text(priority_display), 0, 0, 'C', True)
                pdf.set_text_color(*COLOR_DARK)
            pdf.ln()

    # --- Footer ---
    pdf.ln(6)
    _ensure_page_space(pdf, 15)
    pdf.set_font(ff, 'B', 8)
    pdf.set_text_color(*COLOR_GRAY)
    pdf.cell(0, 5, _safe_text(t['pdf']['generated_by']), 0, 1, 'L')

    # Write PDF
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    pdf.output(output_path)
    return output_path


def _whatchanged_output_path(property_name):
    """Return default what-changed PDF output path on Desktop."""
    desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    if not os.path.isdir(desktop):
        desktop = os.path.expanduser('~')
    slug = _slugify(property_name)
    today = date.today().strftime('%Y-%m-%d')
    return os.path.join(desktop, f'ga4-what-changed-{slug}-{today}.pdf')


def generate_whatchanged_pdf(property_name, reports, days=7, lang='en', output_path=None):
    """Generate what-changed PDF report, return file path.

    Args:
        property_name: Display name + property ID string
        reports: List of report dicts from ga4-what-changed script
        days: Number of days in the comparison period
        lang: Language code ('en' or 'bg')
        output_path: Optional output file path
    """
    from _ga4_lib import format_number

    if not output_path:
        output_path = _whatchanged_output_path(property_name)

    pdf = AuditPDF(lang=lang)
    pdf.alias_nb_pages()
    pdf.add_page()
    ff = pdf._font_family
    page_w = pdf.w - pdf.l_margin - pdf.r_margin

    # --- Header ---
    pdf.set_font(ff, 'B', 22)
    pdf.set_text_color(*COLOR_DARK)
    pdf.cell(0, 12, _safe_text('What Changed'), 0, 1, 'L')

    pdf.set_font(ff, '', 11)
    pdf.set_text_color(*COLOR_GRAY)
    pdf.cell(0, 6, _safe_text(property_name), 0, 1, 'L')

    # Period info from first report that has it
    for r in reports:
        if r and r.get('period'):
            pdf.cell(0, 6, _safe_text(f"Period: {r['period']}"), 0, 1, 'L')
            break

    pdf.ln(4)

    # --- Reports ---
    for report in reports:
        if report is None:
            continue

        _ensure_page_space(pdf, 20)

        # Section title
        pdf.set_font(ff, 'B', 13)
        pdf.set_text_color(*COLOR_DARK)
        pdf.cell(0, 8, _safe_text(report['title']), 0, 1, 'L')
        pdf.set_draw_color(200, 200, 200)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + page_w, pdf.get_y())
        pdf.ln(2)

        if report['type'] == 'overview':
            _render_overview_table(pdf, report, ff, page_w)
        else:
            if not report.get('rows'):
                pdf.set_font(ff, '', 9)
                pdf.set_text_color(*COLOR_GRAY)
                pdf.cell(0, 6, 'No significant changes detected.', 0, 1, 'L')
            else:
                _render_dimension_table(pdf, report, ff, page_w)

                total = report.get('total_changes', 0)
                shown = len(report.get('rows', []))
                if total > shown:
                    pdf.set_font(ff, '', 8)
                    pdf.set_text_color(*COLOR_GRAY)
                    pdf.cell(0, 5, f'Showing top {shown} of {total} changes.', 0, 1, 'L')

        pdf.ln(6)

    # Footer note
    pdf.set_font(ff, '', 8)
    pdf.set_text_color(*COLOR_GRAY)
    pdf.cell(0, 5, _safe_text('Data Arsenal v1 | dataarsenal.com'), 0, 1, 'L')

    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    pdf.output(output_path)
    return output_path


def _render_overview_table(pdf, report, ff, page_w):
    """Render overview (no-dimension) table."""
    col_w = [page_w * 0.35, page_w * 0.16, page_w * 0.16, page_w * 0.18, page_w * 0.15]
    headers = ['Metric', 'Current', 'Previous', 'Change', '%']

    # Header row
    pdf.set_font(ff, 'B', 8)
    pdf.set_fill_color(230, 230, 230)
    pdf.set_text_color(*COLOR_DARK)
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 6, h, 0, 0, 'C', True)
    pdf.ln()

    # Data rows
    for idx, r in enumerate(report['rows']):
        _ensure_page_space(pdf, 6)
        fill = idx % 2 == 1
        pdf.set_fill_color(248, 248, 248)
        pdf.set_font(ff, '', 8)
        pdf.set_text_color(*COLOR_DARK)

        is_rate = r['metric'] in ('engagementRate', 'bounceRate')
        cur_str = format_number(r['current'], is_rate)
        prev_str = format_number(r['previous'], is_rate)
        pct_str = f"{r['pct']:+.1f}%"

        pct = r['pct']
        change_color = COLOR_RED if pct < -5 else (COLOR_GREEN if pct > 5 else COLOR_DARK)

        pdf.cell(col_w[0], 5, _safe_text(r['metric']), 0, 0, 'L', fill)
        pdf.cell(col_w[1], 5, _safe_text(cur_str), 0, 0, 'C', fill)
        pdf.cell(col_w[2], 5, _safe_text(prev_str), 0, 0, 'C', fill)

        pdf.set_text_color(*change_color)
        pdf.cell(col_w[3], 5, _safe_text(r['change']), 0, 0, 'C', fill)
        pdf.cell(col_w[4], 5, pct_str, 0, 0, 'C', fill)
        pdf.set_text_color(*COLOR_DARK)
        pdf.ln()


def _render_dimension_table(pdf, report, ff, page_w):
    """Render dimension breakdown table."""
    col_w = [page_w * 0.28, page_w * 0.20, page_w * 0.12, page_w * 0.12, page_w * 0.14, page_w * 0.08, page_w * 0.06]
    headers = ['Dimension', 'Metric', 'Current', 'Previous', 'Change', '%', 'Impact']

    # Header row
    pdf.set_font(ff, 'B', 7.5)
    pdf.set_fill_color(230, 230, 230)
    pdf.set_text_color(*COLOR_DARK)
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 6, h, 0, 0, 'C', True)
    pdf.ln()

    # Data rows
    for idx, r in enumerate(report['rows']):
        _ensure_page_space(pdf, 6)
        fill = idx % 2 == 1
        pdf.set_fill_color(248, 248, 248)
        pdf.set_font(ff, '', 7.5)
        pdf.set_text_color(*COLOR_DARK)

        is_rate = r['metric'] in ('engagementRate', 'bounceRate')
        cur_str = format_number(r['current'], is_rate)
        prev_str = format_number(r['previous'], is_rate)
        pct_str = f"{r['pct']:+.1f}%"
        impact_str = f"{r['impact']:,.0f}"
        dim = _safe_text(r['dimension'][:35])

        pct = r['pct']
        change_color = COLOR_RED if pct < -10 else (COLOR_GREEN if pct > 10 else COLOR_DARK)

        pdf.cell(col_w[0], 5, dim, 0, 0, 'L', fill)
        pdf.cell(col_w[1], 5, _safe_text(r['metric']), 0, 0, 'L', fill)
        pdf.cell(col_w[2], 5, _safe_text(cur_str), 0, 0, 'C', fill)
        pdf.cell(col_w[3], 5, _safe_text(prev_str), 0, 0, 'C', fill)

        pdf.set_text_color(*change_color)
        pdf.cell(col_w[4], 5, _safe_text(r['change']), 0, 0, 'C', fill)
        pdf.cell(col_w[5], 5, pct_str, 0, 0, 'C', fill)
        pdf.set_text_color(*COLOR_GRAY)
        pdf.cell(col_w[6], 5, impact_str, 0, 0, 'C', fill)
        pdf.set_text_color(*COLOR_DARK)
        pdf.ln()


def _render_gateway_table(pdf, data, ff):
    """Render payment gateway breakdown table in the PDF."""
    gw_rows = []
    for source in data.get('sources', []):
        name = source.get('sessionSourceMedium', '').lower()
        if '/ referral' not in name:
            continue
        if any(p in name for p in GATEWAY_PATTERNS):
            gw_rows.append(source)

    if not gw_rows:
        return

    pdf.ln(2)
    has_rev = any(s.get('totalRevenue', 0) > 0 for s in gw_rows)

    # Table header
    pdf.set_font(ff, 'B', 8)
    pdf.set_fill_color(220, 220, 220)
    if has_rev:
        cols = [70, 30, 30, 30]
        headers = ['Source', 'Sessions', 'Revenue', 'Purchases']
    else:
        total = data.get('core', {}).get('sessions', 1)
        cols = [80, 40, 40]
        headers = ['Source', 'Sessions', '% of Total']

    for j, h in enumerate(headers):
        pdf.cell(cols[j], 6, h, 0, 0, 'C', True)
    pdf.ln()

    # Table rows
    pdf.set_font(ff, '', 7.5)
    pdf.set_text_color(*COLOR_DARK)
    for s in gw_rows:
        if has_rev:
            pdf.cell(cols[0], 5, _safe_text(s['sessionSourceMedium']), 0, 0, 'L')
            pdf.cell(cols[1], 5, f"{s.get('sessions', 0):,.0f}", 0, 0, 'C')
            pdf.cell(cols[2], 5, f"{s.get('totalRevenue', 0):,.2f}", 0, 0, 'C')
            pdf.cell(cols[3], 5, f"{s.get('ecommercePurchases', 0):,.0f}", 0, 0, 'C')
        else:
            total = data.get('core', {}).get('sessions', 1)
            sess = s.get('sessions', 0)
            pct = (sess / total * 100) if total > 0 else 0
            pdf.cell(cols[0], 5, _safe_text(s['sessionSourceMedium']), 0, 0, 'L')
            pdf.cell(cols[1], 5, f"{sess:,.0f}", 0, 0, 'C')
            pdf.cell(cols[2], 5, f"{pct:.1f}%", 0, 0, 'C')
        pdf.ln()
