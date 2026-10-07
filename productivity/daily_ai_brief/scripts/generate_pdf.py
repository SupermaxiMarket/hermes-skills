#!/usr/bin/env python3
"""
Generate Daily AI Brief PDF from a text content file.

Usage:
  python3 generate_pdf.py [content_file] [output_file]

Defaults:
  content_file: /tmp/daily_ai_brief_content.txt
  output_file: /tmp/daily_ai_brief_YYYY-MM-DD.pdf

Uses DejaVu Sans for full Unicode support (accents, em dashes, etc.).
Falls back to Helvetica with Latin-1 encoding if DejaVu not found.
"""
import sys, os
from datetime import date

def _clean_latin1(text):
    """Strip/replace unsupported chars for Helvetica fallback."""
    reps = {
        '\u2014':'--','\u2013':'-','\u2018':"'",'\u2019':"'",
        '\u201c':'"','\u201d':'"','\u2026':'...','\u20ac':'EUR',
        '\u2022':'-','\u00b0':'deg',
        '\u00e0':'a','\u00e2':'a','\u00e7':'c','\u00e8':'e','\u00e9':'e',
        '\u00ea':'e','\u00eb':'e','\u00ee':'i','\u00ef':'i','\u00f4':'o',
        '\u00f9':'u','\u00fb':'u','\u00fc':'u',
        '\u00c0':'A','\u00c8':'E','\u00c9':'E','\u00ca':'E','\u00cb':'E',
        '\u00ce':'I','\u00d4':'O','\u00d9':'U',
    }
    for old, new in reps.items():
        text = text.replace(old, new)
    return text.encode('latin-1', errors='replace').decode('latin-1')


def main():
    today = date.today().isoformat()
    cf = sys.argv[1] if len(sys.argv) > 1 else '/tmp/daily_ai_brief_content.txt'
    out = sys.argv[2] if len(sys.argv) > 2 else f'/tmp/daily_ai_brief_{today}.pdf'

    if not os.path.exists(cf):
        print(f"ERROR: Content file not found: {cf}", file=sys.stderr)
        sys.exit(1)

    with open(cf, 'r', encoding='utf-8') as f:
        raw = f.read()

    from fpdf import FPDF

    font_dir = '/usr/share/fonts/truetype/dejavu/'
    dejavu_path = os.path.join(font_dir, 'DejaVuSans.ttf')
    dejavu_b_path = os.path.join(font_dir, 'DejaVuSans-Bold.ttf')
    dejavu_i_path = os.path.join(font_dir, 'DejaVuSans-Oblique.ttf')

    use_dejavu = os.path.exists(dejavu_path)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)

    if use_dejavu:
        pdf.add_font('DV', '', dejavu_path)
        pdf.add_font('DV', 'B', dejavu_b_path)
        if os.path.exists(dejavu_i_path):
            pdf.add_font('DV', 'I', dejavu_i_path)
        else:
            pdf.add_font('DV', 'I', dejavu_path)
        fn, fb, fi = 'DV', 'DV', 'DV'
    else:
        raw = _clean_latin1(raw)
        fn, fb, fi = 'Helvetica', 'Helvetica', 'Helvetica'

    w = pdf.w - pdf.l_margin - pdf.r_margin

    for line in raw.split('\n'):
        stripped = line.strip()
        if not stripped:
            pdf.ln(2)
            continue
        if stripped.startswith('---'):
            continue

        if 'DAILY AI BRIEF' in stripped.upper() and any(c.isdigit() for c in stripped):
            pdf.set_font(fb, 'B', 14)
            pdf.cell(w, 8, 'Daily AI Brief', new_x="LMARGIN", new_y="NEXT")
            pdf.ln(4)
            continue

        if stripped.startswith('Meteo IA'):
            pdf.set_font(fi, 'I', 9)
            pdf.multi_cell(w, 4.5, stripped, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
            continue

        if len(stripped) > 2 and stripped[0].isdigit() and '. ' in stripped[:6]:
            pdf.ln(3)
            pdf.set_font(fb, 'B', 10)
            pdf.multi_cell(w, 5, stripped, new_x="LMARGIN", new_y="NEXT")
            continue

        if stripped.startswith('EN BREF'):
            pdf.ln(4)
            pdf.set_font(fb, 'B', 10)
            pdf.multi_cell(w, 5, stripped, new_x="LMARGIN", new_y="NEXT")
            continue

        if stripped.startswith('Source :') or stripped.startswith('Daily AI Brief'):
            pdf.set_font(fi, 'I', 7.5)
            pdf.multi_cell(w, 4, stripped, new_x="LMARGIN", new_y="NEXT")
            continue

        pdf.set_font(fn, '', 9)
        pdf.multi_cell(w, 4.5, stripped, new_x="LMARGIN", new_y="NEXT")

    pdf.output(out)
    print(f"OK: {out} ({os.path.getsize(out)} bytes)")


if __name__ == '__main__':
    main()