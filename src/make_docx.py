"""
Generate the 6-page Microsoft Word (.docx) version of the RahiScan Data Science Proposal.
Strictly follows GUIDELINES.jfif:
- Font: Times New Roman throughout
- Heading = 16pt, Subheading = 14pt, Body & Sub-subheading = 12pt
- No bullet points anywhere (narrative prose, tables, and callout boxes only)
- Page 1: Group Contributions Form (Member 1: Define, Collect, Deploy; Member 2: Clean, Explore; Member 3: Model, Evaluate)
- Header & Footer: Member names and roll numbers in BOTH header and footer, title in header
- Case-study narrative extracting all 7 Data Science Lifecycle stages with mock data, charts, tables, and explainer illustrations
"""

from pathlib import Path
import shutil
import pymupdf
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

ROOT = Path(__file__).resolve().parent.parent
FIG_DIR = ROOT / "report" / "figures"
PDF_PATH = ROOT / "RahiScan_Proposal.pdf"
OUT_DOCX = ROOT / "RahiScan_Proposal.docx"
OUT_REPORT_DOCX = ROOT / "report" / "RahiScan_Proposal.docx"

# Scientific IEEE / Nature / Viridis Palette
NAVY = RGBColor(0x1B, 0x36, 0x5D)
SLATE = RGBColor(0x33, 0x41, 0x55)
ORANGE = RGBColor(0x1F, 0x7A, 0x7A)
BLUE = RGBColor(0x2B, 0x6C, 0xB0)
GREEN = RGBColor(0x1F, 0x7A, 0x7A)
RED = RGBColor(0xA8, 0x20, 0x20)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

HEX_NAVY = "1B365D"
HEX_SOFTBLUE = "EBF2F7"
HEX_SOFTGREEN = "E6F2F2"
HEX_SOFTORANGE = "E6F2F2"
HEX_SOFTRED = "F9EBEB"
HEX_LIGHTGRAY = "F8FAFC"
HEX_GREEN = "1F7A7A"
HEX_ORANGE = "1F7A7A"


def extract_tikz_diagrams_from_pdf():
    """Crop the vector TikZ lifecycle and architecture diagrams from Page 2 of the compiled PDF."""
    doc = pymupdf.open(str(PDF_PATH))
    page2 = doc[1]
    # Figure 2: 7-stage lifecycle
    clip_lc = pymupdf.Rect(45, 396, 550, 469)
    pix_lc = page2.get_pixmap(dpi=250, clip=clip_lc)
    lc_path = FIG_DIR / "fig_lifecycle_tikz.png"
    pix_lc.save(str(lc_path))

    # Figure 3: 3-box system architecture
    clip_arch = pymupdf.Rect(65, 658, 530, 736)
    pix_arch = page2.get_pixmap(dpi=250, clip=clip_arch)
    arch_path = FIG_DIR / "fig_arch_tikz.png"
    pix_arch.save(str(arch_path))
    doc.close()
    return lc_path, arch_path


def set_cell_bg(cell, hex_color: str):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=40, bottom=40, left=80, right=80):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for m, val in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        node = OxmlElement(f"w:{m}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def set_table_borders(table, color="BEC8D2", sz="4"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:right w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f"</w:tblBorders>"
    )
    tblPr.append(borders)


def remove_table_borders(table):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        f'<w:bottom w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        f'<w:left w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        f'<w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        f'<w:insideH w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        f'<w:insideV w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        f"</w:tblBorders>"
    )
    tblPr.append(borders)


def add_run(p, text, size=12, bold=False, italic=False, color=None, font_name="Times New Roman"):
    r = p.add_run(text)
    r.font.name = font_name
    r.font.size = Pt(size)
    r.bold = bold
    r.italic = italic
    if color is not None:
        r.font.color.rgb = color
    return r


def add_body_p(doc, segments, space_before=0, space_after=3, line_spacing=1.02, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    """Add a 12pt Times New Roman paragraph from a list of (text, bold, italic, color) tuples or strings."""
    p = doc.add_paragraph()
    p.alignment = align
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing = line_spacing
    for seg in segments:
        if isinstance(seg, str):
            add_run(p, seg, size=12)
        else:
            txt = seg[0]
            b = seg[1] if len(seg) > 1 else False
            it = seg[2] if len(seg) > 2 else False
            col = seg[3] if len(seg) > 3 else None
            sz = seg[4] if len(seg) > 4 else 12
            add_run(p, txt, size=sz, bold=b, italic=it, color=col)
    return p


def add_section_heading(doc, title_text, space_before=3, space_after=1.5, page_break=False):
    """Guidelines: Heading = 16pt Times New Roman."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.keep_with_next = True
    if page_break:
        p.paragraph_format.page_break_before = True
    add_run(p, title_text, size=16, bold=True, color=NAVY)
    pPr = p._p.get_or_add_pPr()
    pBdr = parse_xml(
        f'<w:pBdr {nsdecls("w")}>'
        f'<w:bottom w:val="single" w:sz="8" w:space="1" w:color="1F7A7A"/>'
        f"</w:pBdr>"
    )
    pPr.append(pBdr)
    return p


def add_subheading(doc, title_text, space_before=3, space_after=2):
    """Guidelines: Subheading = 14pt Times New Roman."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.keep_with_next = True
    add_run(p, title_text, size=14, bold=True, color=NAVY)
    return p


def add_subsubheading(doc, title_text, space_before=3, space_after=1.5):
    """Guidelines: Sub-subheading = 12pt Times New Roman."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.keep_with_next = True
    add_run(p, title_text, size=12, bold=True, color=NAVY)
    return p


def add_stage_banner(doc, stage_num, stage_name, question, hex_fill=HEX_SOFTBLUE, accent_rgb=NAVY):
    """Subheading = 14pt stage banner table."""
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    remove_table_borders(tbl)
    c0, c1 = tbl.rows[0].cells
    c0.width = Inches(3.2)
    c1.width = Inches(3.8)
    for c in (c0, c1):
        set_cell_bg(c, hex_fill)
        set_cell_margins(c, top=30, bottom=30, left=80, right=80)
    p0 = c0.paragraphs[0]
    p0.paragraph_format.space_before = Pt(0)
    p0.paragraph_format.space_after = Pt(0)
    add_run(p0, f"Stage {stage_num} · {stage_name}", size=14, bold=True, color=accent_rgb)
    p1 = c1.paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p1.paragraph_format.space_before = Pt(0)
    p1.paragraph_format.space_after = Pt(0)
    add_run(p1, question, size=12, italic=True, color=SLATE)


def add_caption(doc, label, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(3)
    add_run(p, label, size=9, bold=True, color=NAVY)
    add_run(p, text, size=9, color=SLATE)
    return p


def format_table_cell(cell, text, size=9.5, bold=False, italic=False, color=None, bg=None, align=WD_ALIGN_PARAGRAPH.LEFT, pad=20):
    if bg:
        set_cell_bg(cell, bg)
    set_cell_margins(cell, top=pad, bottom=pad, left=55, right=55)
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    if isinstance(text, list):
        for seg in text:
            if isinstance(seg, str):
                add_run(p, seg, size=size, bold=bold, italic=italic, color=color)
            else:
                add_run(
                    p,
                    seg[0],
                    size=seg[4] if len(seg) > 4 else size,
                    bold=seg[1] if len(seg) > 1 else bold,
                    italic=seg[2] if len(seg) > 2 else italic,
                    color=seg[3] if len(seg) > 3 else color,
                )
    else:
        add_run(p, text, size=size, bold=bold, italic=italic, color=color)


def add_page_field(run):
    fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls("w"))
    instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> PAGE </w:instrText>' % nsdecls("w"))
    fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls("w"))
    fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls("w"))
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)


def add_numpages_field(run):
    fldChar1 = parse_xml(r'<w:fldChar %s w:fldCharType="begin"/>' % nsdecls("w"))
    instrText = parse_xml(r'<w:instrText %s xml:space="preserve"> NUMPAGES </w:instrText>' % nsdecls("w"))
    fldChar2 = parse_xml(r'<w:fldChar %s w:fldCharType="separate"/>' % nsdecls("w"))
    fldChar3 = parse_xml(r'<w:fldChar %s w:fldCharType="end"/>' % nsdecls("w"))
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)


def build_docx():
    lc_path, arch_path = extract_tikz_diagrams_from_pdf()

    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.top_margin = Cm(1.8)
    sec.bottom_margin = Cm(1.6)
    sec.left_margin = Cm(1.7)
    sec.right_margin = Cm(1.7)
    sec.header_distance = Cm(0.7)
    sec.footer_distance = Cm(0.7)

    # Normal style defaults
    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Times New Roman"
    normal_style.font.size = Pt(12)
    normal_style.paragraph_format.space_before = Pt(0)
    normal_style.paragraph_format.space_after = Pt(2)
    normal_style.paragraph_format.line_spacing = 1.0

    team_line = "M. Saad Hussain (SU92-BSCSM-F25-260) • M. Khubaib (SU92-BSCSM-F25-300) • Huzaifa (SU92-BSCSM-F25-408)"

    # Header (title + member names & roll numbers)
    hdr = sec.header
    hp = hdr.paragraphs[0]
    hp.paragraph_format.space_before = Pt(0)
    hp.paragraph_format.space_after = Pt(2)
    hp.paragraph_format.line_spacing = 1.0
    add_run(hp, "RahiScan: Automated Qingqi Rickshaw Fare & Pace Telemetry, A Data Science Proposal", size=9, bold=True, color=NAVY)
    add_run(hp, "   |   Introduction to Data Science (Due 21 Oct 2026)\n", size=8.5, color=SLATE)
    add_run(hp, team_line, size=8, color=SLATE)
    hpPr = hp._p.get_or_add_pPr()
    hpPr.append(
        parse_xml(
            f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="6" w:space="2" w:color="1F7A7A"/></w:pBdr>'
        )
    )

    # Footer (member names & roll numbers + page number)
    ftr = sec.footer
    fp = ftr.paragraphs[0]
    fp.paragraph_format.space_before = Pt(2)
    fp.paragraph_format.space_after = Pt(0)
    fpPr = fp._p.get_or_add_pPr()
    fpPr.append(
        parse_xml(
            f'<w:pBdr {nsdecls("w")}><w:top w:val="single" w:sz="4" w:space="2" w:color="94A3B8"/></w:pBdr>'
        )
    )
    add_run(fp, team_line + "          Page ", size=8, color=SLATE)
    r_pg = add_run(fp, "", size=8.5, bold=True, color=NAVY)
    add_page_field(r_pg)
    add_run(fp, " of ", size=8.5, bold=True, color=NAVY)
    r_np = add_run(fp, "", size=8.5, bold=True, color=NAVY)
    add_numpages_field(r_np)

    # =========================================================================
    # PAGE 1: GROUP CONTRIBUTIONS FORM
    # =========================================================================
    banner_tbl = doc.add_table(rows=1, cols=2)
    banner_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    remove_table_borders(banner_tbl)
    bc0, bc1 = banner_tbl.rows[0].cells
    bc0.width = Inches(4.5)
    bc1.width = Inches(2.4)
    for c in (bc0, bc1):
        set_cell_bg(c, HEX_NAVY)
        set_cell_margins(c, top=100, bottom=100, left=120, right=120)
    bp0 = bc0.paragraphs[0]
    bp0.paragraph_format.space_after = Pt(2)
    add_run(bp0, "RahiScan\n", size=22, bold=True, color=WHITE)
    add_run(bp0, "Automated Qingqi Rickshaw Fare & Pace Telemetry\n", size=13, color=WHITE)
    add_run(bp0, "A Data Science Lifecycle Proposal · Superior University Gold Campus", size=10.5, italic=True, color=RGBColor(0xD6, 0xE6, 0xF9))

    bp1 = bc1.paragraphs[0]
    bp1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    bp1.paragraph_format.space_after = Pt(2)
    add_run(bp1, "Introduction to Data Science\nGroup Assignment\nSubmitted 21 October 2026\n\n", size=9.5, color=WHITE)
    add_run(bp1, "github.com/ZEKT-VII/RahiScan-DS-Proposal", size=8, color=RGBColor(0xD6, 0xE6, 0xF9))

    add_section_heading(doc, "Group Contributions Form", space_before=8, space_after=4)
    add_body_p(
        doc,
        [
            "This form records how our three-member team divided the work behind this proposal. Each member led specific stages of the Data Science Lifecycle and reviewed the stages led by the others, so the whole report reflects a shared design."
        ],
        space_after=4,
    )

    # Member Contributions Table
    t_mem = doc.add_table(rows=4, cols=4)
    t_mem.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_mem)
    widths_mem = [Inches(0.85), Inches(1.45), Inches(1.45), Inches(3.15)]
    headers_mem = ["Member", "Name", "Roll Number", "Contribution"]
    for j, h in enumerate(headers_mem):
        t_mem.rows[0].cells[j].width = widths_mem[j]
        format_table_cell(t_mem.rows[0].cells[j], h, size=10, bold=True, color=WHITE, bg=HEX_NAVY)

    rows_mem = [
        (
            "Member 1",
            "Muhammad Saad Hussain",
            "SU92-BSCSM-F25-260",
            [
                "Wrote the case-study story, framed the problem, designed the scanning workflow, data-collection schema, system architecture, and planned the in-app deployment, privacy safeguards, and rollout roadmap. Led the ",
                ("Define, Collect", True),
                " and ",
                ("Deploy", True),
                " stages.",
            ],
        ),
        (
            "Member 2",
            "Muhammad Khubaib",
            "SU92-BSCSM-F25-300",
            [
                "Built the mock Lahore Qingqi dataset and Python cleaning pipeline, wrote the OCR-face fusion and walking-tail trimming rules, and conducted the exploratory traffic-baseline and fare-ratio analysis. Led the ",
                ("Clean", True),
                " and ",
                ("Explore", True),
                " stages.",
            ],
        ),
        (
            "Member 3",
            "Huzaifa",
            "SU92-BSCSM-F25-408",
            [
                "Built the two-tier identity and gradient-boosting models for fair fares and pace classification, designed the Week-4 holdout evaluation and success thresholds, produced the charts, and maintained the GitHub repository. Led the ",
                ("Model", True),
                " and ",
                ("Evaluate", True),
                " stages.",
            ],
        ),
    ]
    for i, (m_id, name, roll, desc) in enumerate(rows_mem, start=1):
        row = t_mem.rows[i]
        for j, w in enumerate(widths_mem):
            row.cells[j].width = w
        format_table_cell(row.cells[0], m_id, size=10, bold=True, color=NAVY, bg=HEX_SOFTBLUE)
        format_table_cell(row.cells[1], name, size=10, bold=True)
        format_table_cell(row.cells[2], roll, size=10, align=WD_ALIGN_PARAGRAPH.CENTER)
        format_table_cell(row.cells[3], desc, size=10)

    add_subsubheading(doc, "Lifecycle Ownership Matrix", space_before=6, space_after=2)
    t_own = doc.add_table(rows=4, cols=8)
    t_own.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_own)
    own_hdrs = ["Member", "Define", "Collect", "Clean", "Explore", "Model", "Evaluate", "Deploy"]
    for j, h in enumerate(own_hdrs):
        format_table_cell(
            t_own.rows[0].cells[j],
            h,
            size=9.5,
            bold=True,
            color=WHITE,
            bg=HEX_NAVY,
            align=WD_ALIGN_PARAGRAPH.CENTER if j > 0 else WD_ALIGN_PARAGRAPH.LEFT,
        )
    own_rows = [
        ("M. Saad Hussain", ["Lead", "Lead", "Review", "Support", "Review", "Support", "Lead"]),
        ("M. Khubaib", ["Support", "Support", "Lead", "Lead", "Support", "Review", "Review"]),
        ("Huzaifa", ["Review", "Review", "Support", "Review", "Lead", "Lead", "Support"]),
    ]
    for i, (mname, roles) in enumerate(own_rows, start=1):
        format_table_cell(t_own.rows[i].cells[0], mname, size=9.5, bold=True, color=NAVY)
        for j, role in enumerate(roles, start=1):
            if role == "Lead":
                format_table_cell(t_own.rows[i].cells[j], role, size=9.5, bold=True, color=WHITE, bg=HEX_GREEN, align=WD_ALIGN_PARAGRAPH.CENTER)
            elif role == "Support":
                format_table_cell(t_own.rows[i].cells[j], role, size=9.5, color=GREEN, bg=HEX_SOFTGREEN, align=WD_ALIGN_PARAGRAPH.CENTER)
            else:
                format_table_cell(t_own.rows[i].cells[j], role, size=9.5, color=SLATE, bg=HEX_LIGHTGRAY, align=WD_ALIGN_PARAGRAPH.CENTER)

    add_subsubheading(doc, "Deliverables Submitted", space_before=6, space_after=2)
    t_del = doc.add_table(rows=4, cols=2)
    t_del.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_del)
    deliv_rows = [
        ("This report (PDF & DOCX, 6 pp.)", "Case-study story, 7-stage lifecycle extraction, mock pilot findings and deployment proposal."),
        ("Mock dataset", "1,224 Qingqi ride submissions, 1,200 scans and 411,829 GPS pings from 40 simulated drivers (data/)."),
        ("Reproducible code", "Data generator, cleaning and modelling pipeline, and figure scripts in Python (src/)."),
        ("GitHub Repository", "https://github.com/ZEKT-VII/RahiScan-DS-Proposal"),
    ]
    for i, (k, v) in enumerate(deliv_rows):
        t_del.rows[i].cells[0].width = Inches(2.2)
        t_del.rows[i].cells[1].width = Inches(4.7)
        format_table_cell(t_del.rows[i].cells[0], k, size=9.5, bold=True, bg=HEX_LIGHTGRAY)
        format_table_cell(t_del.rows[i].cells[1], v, size=9.5)

    add_body_p(
        doc,
        [
            ("\n__________________________                __________________________                __________________________\n", False, False, SLATE, 10),
            ("M. Saad Hussain                                        M. Khubaib                                                Huzaifa", False, False, SLATE, 10),
        ],
        space_before=8,
        space_after=0,
        align=WD_ALIGN_PARAGRAPH.LEFT,
    )

    # =========================================================================
    # PAGE 2: CASE STUDY STORY & LIFECYCLE EXTRACTION
    # =========================================================================
    add_section_heading(doc, "1. The Case Study: A Morning on Raiwind Road", page_break=True)

    story_tbl = doc.add_table(rows=1, cols=2)
    story_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    remove_table_borders(story_tbl)
    sc0, sc1 = story_tbl.rows[0].cells
    sc0.width = Inches(4.0)
    sc1.width = Inches(2.9)
    set_cell_margins(sc0, top=10, bottom=10, left=0, right=80)
    set_cell_margins(sc1, top=10, bottom=10, left=40, right=0)

    sp1 = sc0.paragraphs[0]
    sp1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    sp1.paragraph_format.space_after = Pt(2)
    sp1.paragraph_format.line_spacing = 0.98
    add_run(sp1, "It is 7:40 on a Monday in Johar Town and we have an 8:30 lab at ", size=12)
    add_run(sp1, "Superior University Gold Campus", size=12, bold=True)
    add_run(sp1, " on Raiwind Road (9.6 km). The first ", size=12)
    add_run(sp1, "Qingqi rickshaw", size=12, bold=True)
    add_run(
        sp1,
        " quotes 140 rupees; we bargain down to 110 and board. The driver then crawls along the left lane, stops for tea at a roadside dhaba “for one minute”, and delivers us twelve minutes late. The next morning a different Qingqi driver covers the same 9.6 km route to Superior University Gold Campus for the standard ",
        size=12,
    )
    add_run(sp1, "80 rupees", size=12, bold=True)
    add_run(sp1, " in twenty minutes despite heavier traffic (similarly, the 16.1 km ride from ", size=12)
    add_run(sp1, "Raiwind", size=12, bold=True)
    add_run(sp1, " to Gold Campus costs about ", size=12)
    add_run(sp1, "120 rupees", size=12, bold=True)
    add_run(
        sp1,
        ", and inner-city Lahore routes average 40–85 rupees).\n"
        "Lahore's Qingqi motorcycle-rickshaws lack meters, leaving commuters unable to tell at the curb whether a quote is inflated or whether a driver is habitually slow. We propose ",
        size=12,
    )
    add_run(sp1, "RahiScan", size=12, bold=True)
    add_run(
        sp1,
        ", a crowd-sourced mobile app where passengers photograph a Qingqi rickshaw before boarding (Figure 1), fusing number-plate OCR with driver facial recognition, enter the quoted fare, and log 5-second GPS pings until arrival.",
        size=12,
    )

    sp2 = sc1.paragraphs[0]
    sp2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sp2.paragraph_format.space_after = Pt(2)
    sp2.add_run().add_picture(str(FIG_DIR / "hero_scan.jpg"), width=Inches(2.75))
    sp2_cap = sc1.add_paragraph()
    sp2_cap.paragraph_format.space_before = Pt(1)
    sp2_cap.paragraph_format.space_after = Pt(0)
    add_run(sp2_cap, "Figure 1: ", size=8.5, bold=True, color=NAVY)
    add_run(sp2_cap, "Curbside AR scan of a Pakistani Qingqi rickshaw reading the plate (teal) and driver face (steel-blue).", size=8.5, color=SLATE)

    add_section_heading(doc, "2. Extracting the Data Science Lifecycle from the Story")

    p_lc = doc.add_paragraph()
    p_lc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lc.paragraph_format.space_before = Pt(1)
    p_lc.paragraph_format.space_after = Pt(1)
    p_lc.add_run().add_picture(str(lc_path), width=Inches(6.7))
    add_caption(doc, "Figure 2: ", "The seven-stage Data Science Lifecycle mapped to RahiScan's guiding questions and planned actions.")

    add_caption(doc, "Table 1: ", "Data science problems extracted directly from the morning commute story.")
    t_ext = doc.add_table(rows=8, cols=3)
    t_ext.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_ext)
    format_table_cell(t_ext.rows[0].cells[0], "Stage", size=9, bold=True, color=WHITE, bg=HEX_NAVY)
    format_table_cell(t_ext.rows[0].cells[1], "Moment in the story", size=9, bold=True, color=WHITE, bg=HEX_NAVY)
    format_table_cell(t_ext.rows[0].cells[2], "Data science problem it raises and proposed solution", size=9, bold=True, color=WHITE, bg=HEX_NAVY)
    ext_rows = [
        ("Define", "“We could not tell the two drivers apart.”", "Replace subjective complaints with two traffic- and route-normalised ratios: Pace Index Π and Fare Ratio Φ."),
        ("Collect", "“Every bad ride leaves data nobody records.”", "Capture Qingqi plate+face scans, quoted fares, 5-s GPS/accelerometer traces, and corridor fare benchmarks."),
        ("Clean", "“We walked into the lab twelve minutes late.”", "Trim pedestrian walking tails when users forget End Ride; fuse OCR and face embeddings; drop duplicates/typos."),
        ("Explore", "“...even though the traffic was worse.”", "Separate road congestion from driver habit by comparing trip speed against corridor-hour median speed v_base."),
        ("Model", "“A different driver took the same route.”", "Resolve shared-Qingqi drivers via biometric fusion and predict fair fares and pace classes with gradient boosting."),
        ("Evaluate", "“Stuck in traffic is not a slow driver.”", "Test on an unseen Week-4 holdout to measure false flags on single rides versus multi-ride driver profiles."),
        ("Deploy", "“We had to decide at the curb, in seconds.”", "Return a colour-coded scorecard in under 2 seconds, gated behind a 5-ride minimum and monthly fare retraining."),
    ]
    for i, (st, mom, prob) in enumerate(ext_rows, start=1):
        t_ext.rows[i].cells[0].width = Inches(0.8)
        t_ext.rows[i].cells[1].width = Inches(2.1)
        t_ext.rows[i].cells[2].width = Inches(4.0)
        format_table_cell(t_ext.rows[i].cells[0], st, size=8.5, bold=True, color=NAVY, bg=HEX_SOFTBLUE)
        format_table_cell(t_ext.rows[i].cells[1], mom, size=8.5, italic=True)
        format_table_cell(t_ext.rows[i].cells[2], prob, size=8.5)

    p_ar = doc.add_paragraph()
    p_ar.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ar.paragraph_format.space_before = Pt(2)
    p_ar.paragraph_format.space_after = Pt(1)
    p_ar.add_run().add_picture(str(arch_path), width=Inches(6.2))
    add_caption(doc, "Figure 3: ", "End-to-end RahiScan architecture illustrated with simulated Qingqi driver D27 on the 9.6 km Superior Gold Campus route.")

    # =========================================================================
    # PAGE 3: STAGE 1 (DEFINE) & STAGE 2 (COLLECT)
    # =========================================================================
    add_section_heading(doc, "3. Define: Turning Frustration into Measurable Targets", page_break=True)
    add_stage_banner(doc, 1, "DEFINE", "What problem should be solved?", HEX_SOFTBLUE, NAVY)
    add_body_p(
        doc,
        [
            "To replace subjective complaints with testable metrics, we define two dimensionless ratios for every Qingqi ride i, where 1.0 represents typical behaviour on that corridor and hour, and fix badge thresholds prior to data collection (Table 2):"
        ],
    )

    t_eq = doc.add_table(rows=1, cols=2)
    t_eq.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_eq, color="1B365D", sz="6")
    format_table_cell(
        t_eq.rows[0].cells[0],
        [
            ("Driving Pace Index (Π_i)\n", True, False, NAVY, 10),
            ("Π_i = v_obs,i / v_base,i = (d_i / t_i) / median(v_obs on corridor, hour)\n", True, False, SLATE, 9),
            ("Π = 0.60 means moving 40% slower than peer Qingqi rickshaws on the same road and hour.", False, False, SLATE, 8.5),
        ],
        bg=HEX_LIGHTGRAY,
        pad=14,
    )
    format_table_cell(
        t_eq.rows[0].cells[1],
        [
            ("Fare Fairness Ratio (Φ_i)\n", True, False, ORANGE, 10),
            ("Φ_i = Fare_quoted,i / Fare_fair,i\n", True, False, SLATE, 9),
            ("Fare_fair is predicted from distance, corridor, and congestion (≈ 80 PKR for 9.6 km; ≈ 120 PKR Raiwind to Gold Campus).", False, False, SLATE, 8.5),
        ],
        bg=HEX_LIGHTGRAY,
        pad=14,
    )

    add_caption(doc, "Table 2: ", "Pre-registered decision rules for driver badges (applied to a driver's median across ≥ 5 verified rides).")
    t_def = doc.add_table(rows=4, cols=3)
    t_def.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_def)
    for j, h in enumerate(["Badge", "Rule (driver median)", "Curbside guidance shown to the passenger"]):
        format_table_cell(t_def.rows[0].cells[j], h, size=8.5, bold=True, color=WHITE, bg=HEX_NAVY, pad=14)
    def_rows = [
        ("Habitually Slow", "Π < 0.75", "Expect trip duration at least 25% longer than ambient traffic requires.", HEX_SOFTRED, RED),
        ("Normal / Fast Pace", "0.75 ≤ Π ≤ 1.15 / Π > 1.15", "Moves with ambient traffic (≤ 1.15) or noticeably brisker (> 1.15).", HEX_SOFTGREEN, GREEN),
        ("Overpriced", "Φ > 1.25", "Quotes more than 25% above fair benchmark (e.g. > 100 PKR on an 80 PKR route); negotiate or skip.", HEX_SOFTORANGE, ORANGE),
    ]
    for i, (b_lbl, rule, guide, bg_hex, col_rgb) in enumerate(def_rows, start=1):
        format_table_cell(t_def.rows[i].cells[0], b_lbl, size=8.5, bold=True, color=col_rgb, bg=bg_hex, pad=14)
        format_table_cell(t_def.rows[i].cells[1], rule, size=8.5, align=WD_ALIGN_PARAGRAPH.CENTER, pad=14)
        format_table_cell(t_def.rows[i].cells[2], guide, size=8.5, pad=14)

    add_section_heading(doc, "4. Collect: The Evidence We Need")
    add_stage_banner(doc, 2, "COLLECT", "What evidence is needed?", HEX_SOFTBLUE, BLUE)
    add_body_p(
        doc,
        [
            "Since no public dataset links Lahore Qingqi rickshaw drivers to speed and pricing, we designed a four-week pilot with 85 student volunteers commuting to ",
            ("Superior University Gold Campus", True),
            " (from Raiwind, Johar Town, Thokar Niaz Baig, and Township) and across inner-city Lahore corridors. To validate our pipeline beforehand, we generated a synthetic pilot dataset (SEED = 2026) spanning 40 drivers across 34 Qingqi rickshaws (six shift-shared), 1,200 scans, 1,224 trip logs, and 411,829 5-second GPS pings (Table 3, Figure 4). For privacy, only 128-D face embeddings are stored and raw photos are discarded immediately.",
        ],
    )

    add_caption(doc, "Table 3: ", "Planned data streams and volume produced by our four-week simulated Lahore pilot (data/raw/).")
    t_col = doc.add_table(rows=6, cols=4)
    t_col.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_col)
    for j, h in enumerate(["Stream", "Fields captured", "Lifecycle purpose", "Mock rows"]):
        format_table_cell(t_col.rows[0].cells[j], h, size=8.5, bold=True, color=WHITE, bg=HEX_NAVY, pad=14)
    col_rows = [
        ("Curb scan", "Plate OCR text & confidence, 128-D face cosine match, low-light flag", "Verify driver identity", "1,200"),
        ("Ride record", "User ID, corridor, timestamps, quoted fare (PKR), End Ride flag", "Fare & duration log", "1,224"),
        ("GPS pings", "Lat, lon, 5-s timestamp, speed, accelerometer step variance", "Trajectory & tail trim", "411,829"),
        ("Fare benchmark", "Reference Qingqi corridor fare (PKR; ≈ 80 PKR for 9.6 km)", "Ground-truth fair fare", "1,200"),
        ("Driver gallery", "Registered plate-to-driver mapping and shift schedule (34 plates)", "Resolve shared vehicles", "40"),
    ]
    for i, (s_name, flds, purp, nrows) in enumerate(col_rows, start=1):
        format_table_cell(t_col.rows[i].cells[0], s_name, size=8.5, bold=True, color=NAVY, bg=HEX_SOFTBLUE, pad=14)
        format_table_cell(t_col.rows[i].cells[1], flds, size=8.5, pad=14)
        format_table_cell(t_col.rows[i].cells[2], purp, size=8.5, pad=14)
        format_table_cell(t_col.rows[i].cells[3], nrows, size=8.5, align=WD_ALIGN_PARAGRAPH.RIGHT, pad=14)

    p_rm = doc.add_paragraph()
    p_rm.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_rm.paragraph_format.space_before = Pt(1)
    p_rm.paragraph_format.space_after = Pt(1)
    p_rm.add_run().add_picture(str(FIG_DIR / "fig_route_map.png"), width=Inches(3.65))
    add_caption(
        doc,
        "Figure 4: ",
        "Left: simulated GPS traces across Raiwind, Superior Gold Campus, and inner-city Lahore corridors, with red tails showing forgotten End Ride walks. Right: ride volume peaks during the 07:00–09:00 and 16:00–19:00 rush hours.",
    )

    # =========================================================================
    # PAGE 4: STAGE 3 (CLEAN) & STAGE 4 (EXPLORE)
    # =========================================================================
    add_section_heading(doc, "5. Clean: Can the Data Be Trusted?", page_break=True)
    add_stage_banner(doc, 3, "CLEAN", "Can the data be trusted?", HEX_SOFTORANGE, ORANGE)
    add_body_p(
        doc,
        [
            "Street telemetry contains four recurring defects that we injected into our mock pilot and resolved programmatically. First, ",
            ("duplicate uploads", True),
            " from cellular retries within 10 seconds are dropped (1,224 → 1,200). Second, ",
            ("missing or typo fares", True),
            " (e.g. 800 instead of 80 PKR) outside [0.4, 4.0]× benchmark are removed (1,200 → 1,151). Third, ",
            ("night glare and dented plates", True),
            " degrade OCR; requiring plate confidence ≥ 0.85 or face similarity ≥ 0.70 (and using the face to disambiguate shared plates) boosts identity precision from 83.5% to ",
            ("99.8%", True),
            " (1,151 → 1,090), leaving ",
            ("1,071 verified rides", True),
            " after dropping 19 underpass traces with < 75% GPS coverage (Figure 5, left). Fourth, when a student forgets to tap End Ride, our backward change-point filter trims trailing pings with speed < 6 km/h and step variance > 1.0 m/s² for ≥ 60 s, catching ",
            ("82.4%", True),
            " of all 148 walking tails at 100% precision and restoring 2.36 km/h to affected drivers (Figure 5, right).",
        ],
    )

    t_f5 = doc.add_table(rows=1, cols=2)
    t_f5.alignment = WD_TABLE_ALIGNMENT.CENTER
    remove_table_borders(t_f5)
    t_f5.rows[0].cells[0].paragraphs[0].add_run().add_picture(str(FIG_DIR / "fig_cleaning.png"), width=Inches(2.85))
    t_f5.rows[0].cells[1].paragraphs[0].add_run().add_picture(str(FIG_DIR / "fig_gps_trim.png"), width=Inches(2.85))
    add_caption(
        doc,
        "Figure 5: ",
        "Left: multi-stage cleaning funnel (1,224 raw to 1,071 clean rides) and biometric fusion gain. Right: change-point walking-tail trim on a student commute, preventing an artificial speed penalty.",
    )

    add_section_heading(doc, "6. Explore: What Patterns Appear?", space_before=2, space_after=1)
    add_stage_banner(doc, 4, "EXPLORE", "What patterns appear?", HEX_SOFTORANGE, ORANGE)
    add_body_p(
        doc,
        [
            "Exploratory analysis confirms why raw speed is unfair: on inner-city corridors such as Mall Road, ambient median speed v_base drops from 22 km/h at night to 10 km/h during rush hour, whereas Raiwind Road to Superior Gold Campus flows faster (Figure 6, left). Normalising by v_base isolates driver pace across all traffic regimes, while the Fare Ratio Φ separates fair Qingqi quotes (≈ 80 PKR for 9.6 km, ≈ 120 PKR from Raiwind to Gold Campus, Φ ≈ 1.0) from an overpriced tail near Φ ≈ 1.7 (Figure 6, right; Table 4)."
        ],
        space_after=2,
        line_spacing=0.98,
    )

    t_f6 = doc.add_table(rows=1, cols=2)
    t_f6.alignment = WD_TABLE_ALIGNMENT.CENTER
    remove_table_borders(t_f6)
    t_f6.rows[0].cells[0].paragraphs[0].add_run().add_picture(str(FIG_DIR / "fig_heatmap.png"), width=Inches(2.80))
    t_f6.rows[0].cells[1].paragraphs[0].add_run().add_picture(str(FIG_DIR / "fig_explore.png"), width=Inches(2.90))
    add_caption(
        doc,
        "Figure 6: ",
        "Left: weekday ambient speed v_base by corridor and hour. Right: observed vs. baseline speed showing the Normal Pace band, and the bimodal distribution of Fare Ratio Φ.",
    )

    add_caption(doc, "Table 4: ", "Sample of cleaned, feature-engineered Qingqi rides (data/processed/trips_clean.csv) illustrating independent pace and fare scores.")
    t_smp = doc.add_table(rows=5, cols=10)
    t_smp.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_smp)
    smp_hdrs = ["Ride", "Plate # Face", "Corridor", "Hr", "km", "v_obs", "v_base", "Π", "Quoted/Fair", "Φ"]
    for j, h in enumerate(smp_hdrs):
        format_table_cell(t_smp.rows[0].cells[j], h, size=8.5, bold=True, color=WHITE, bg=HEX_NAVY, align=WD_ALIGN_PARAGRAPH.CENTER, pad=6)
    smp_rows = [
        ("TR-0794", "LES-8113#F06", "Johar Town – Gold Campus", "14", "10.0", "22.9", "22.4", "1.02", "80 / 79", "1.02"),
        ("TR-0467", "LEA-6967#F23", "Raiwind – Gold Campus", "8", "16.1", "18.2", "19.7", "0.92", "125 / 126", "0.99"),
        ("TR-0427", "LEP-2758#F27", "Raiwind – Gold Campus", "17", "16.2", "13.0", "23.0", "0.57", "180 / 120", "1.50"),
        ("TR-1092", "LEP-3036#F20", "Thokar – Gold Campus", "11", "8.7", "25.4", "25.4", "1.00", "125 / 71", "1.77"),
    ]
    for i, rvals in enumerate(smp_rows, start=1):
        for j, val in enumerate(rvals):
            format_table_cell(
                t_smp.rows[i].cells[j],
                val,
                size=8.5,
                bold=(j in (0, 7, 9)),
                bg=HEX_SOFTBLUE if j == 0 else None,
                align=WD_ALIGN_PARAGRAPH.LEFT if j == 2 else WD_ALIGN_PARAGRAPH.CENTER,
                pad=6,
            )

    # =========================================================================
    # PAGE 5: STAGE 5 (MODEL) & STAGE 6 (EVALUATE)
    # =========================================================================
    add_section_heading(doc, "7. Model: From Patterns to Predictions", page_break=True)
    add_stage_banner(doc, 5, "MODEL", "Can patterns support prediction?", HEX_SOFTBLUE, BLUE)
    add_body_p(
        doc,
        [
            "Our modelling architecture operates in two tiers (Figure 7, left). ",
            ("Tier 1 (Biometric + OCR Identity Fusion)", True),
            " pairs a CRNN plate reader with a MobileNetV3 128-D face encoder. Because six Qingqi rickshaws in our pilot are shared across shifts, a single plate is often driven by a fair morning driver (Φ ≈ 1.02) and an overpriced evening driver (Φ ≈ 1.75) who would otherwise be blurred into one misleading profile. ",
            ("Tier 2 (Behavioural Prediction)", True),
            " trains a Gradient-Boosted Regressor (GBR) to predict Fare_fair from distance, corridor, hour, weekend indicator, and ambient speed v_base, plus a multiclass GBR pace classifier. Plotting 4-week driver medians reveals four behavioural clusters and confirms that pace and pricing require separate badges (Figure 7, right).",
        ],
        space_after=2,
        line_spacing=0.98,
    )

    t_f7 = doc.add_table(rows=1, cols=2)
    t_f7.alignment = WD_TABLE_ALIGNMENT.CENTER
    remove_table_borders(t_f7)
    t_f7.rows[0].cells[0].paragraphs[0].add_run().add_picture(str(FIG_DIR / "data_journey.jpg"), width=Inches(2.35))
    t_f7.rows[0].cells[1].paragraphs[0].add_run().add_picture(str(FIG_DIR / "fig_quadrant.png"), width=Inches(2.50))
    add_caption(
        doc,
        "Figure 7: ",
        "Left: single-scan data journey from Qingqi phone capture to cloud inference and scorecard. Right: 40 driver profiles across the Pace Index (Π) vs. Fare Ratio (Φ) quadrant.",
    )

    add_section_heading(doc, "8. Evaluate: How Reliable Is the Result?", space_before=2, space_after=1)
    add_stage_banner(doc, 6, "EVALUATE", "How reliable is the result?", HEX_SOFTBLUE, NAVY)
    add_body_p(
        doc,
        [
            "To prevent temporal leakage, models are trained strictly on Weeks 1–3 (808 clean rides) and evaluated on the unseen Week-4 holdout (263 rides across all 40 drivers; Table 5). Fair-fare GBR achieves a Mean Absolute Error of ",
            ("1.8 PKR", True),
            " against a < 5 PKR target (beating distance-only linear regression at 2.6 PKR and a flat median rate at 22.5 PKR). Single-ride pace reaches macro ",
            ("F1 = 0.71", True),
            " (below the 0.88 target, vs. 0.54 for raw speed) because individual trips suffer from one-off traffic luck, whereas aggregating over ≥ 5 rides eliminates single-trip noise and lifts driver-level Pace Badge accuracy to ",
            ("100%", True),
            " (versus 90.0% using raw speed; Figure 8).",
        ],
        space_after=2,
        line_spacing=0.98,
    )

    add_caption(doc, "Table 5: ", "Holdout evaluation summary on unseen Week-4 trips (n = 263 rides, 40 drivers).")
    t_ev = doc.add_table(rows=7, cols=5)
    t_ev.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_ev)
    for j, h in enumerate(["Module", "Metric and baseline comparison", "Target", "Mock result", "Status"]):
        format_table_cell(t_ev.rows[0].cells[j], h, size=8.5, bold=True, color=WHITE, bg=HEX_NAVY, pad=5)
    ev_rows = [
        ("Driver identity", "Precision of verified IDs (plate-only baseline: 83.5%)", "≥ 93%", "99.8%", "Met", HEX_SOFTGREEN, GREEN),
        ("Walking-tail filter", "Recall on 148 forgotten End Ride walking tails (100% precision)", "≥ 0.80", "0.82", "Met", HEX_SOFTGREEN, GREEN),
        ("Fair-fare regressor", "Holdout MAE (linear: 2.6 PKR; flat rate: 22.5 PKR)", "< 5 PKR", "1.8 PKR", "Met", HEX_SOFTGREEN, GREEN),
        ("Pace (single ride)", "Macro F1 on individual trips (raw speed baseline: 0.54)", "≥ 0.88", "0.71", "Not met", HEX_SOFTRED, RED),
        ("Pace (driver badge)", "Badge accuracy over ≥ 5 rides (raw speed baseline: 90.0%)", "≥ 90%", "100%", "Met", HEX_SOFTGREEN, GREEN),
        ("Fare badge", "Overpriced flag accuracy over ≥ 5 rides", "≥ 90%", "100%", "Met", HEX_SOFTGREEN, GREEN),
    ]
    for i, (mod, met, tgt, res, st, st_bg, st_col) in enumerate(ev_rows, start=1):
        format_table_cell(t_ev.rows[i].cells[0], mod, size=8.5, bold=True, color=NAVY, bg=HEX_SOFTBLUE, pad=5)
        format_table_cell(t_ev.rows[i].cells[1], met, size=8.5, pad=5)
        format_table_cell(t_ev.rows[i].cells[2], tgt, size=8.5, align=WD_ALIGN_PARAGRAPH.CENTER, pad=5)
        format_table_cell(t_ev.rows[i].cells[3], res, size=8.5, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, pad=5)
        format_table_cell(t_ev.rows[i].cells[4], st, size=8.5, bold=True, color=st_col, bg=st_bg, align=WD_ALIGN_PARAGRAPH.CENTER, pad=5)

    t_f8 = doc.add_table(rows=1, cols=2)
    t_f8.alignment = WD_TABLE_ALIGNMENT.CENTER
    remove_table_borders(t_f8)
    t_f8.rows[0].cells[0].paragraphs[0].add_run().add_picture(str(FIG_DIR / "fig_evaluate.png"), width=Inches(2.70))
    t_f8.rows[0].cells[1].paragraphs[0].add_run().add_picture(str(FIG_DIR / "fig_normalisation.png"), width=Inches(2.35))
    add_caption(
        doc,
        "Figure 8: ",
        "Left: Week-4 holdout fair-fare predictions, log-scale MAE comparison (< 5 PKR target), and single-ride confusion matrix. Right: traffic normalisation (Π) outperforms raw speed.",
    )

    # =========================================================================
    # PAGE 6: STAGE 7 (DEPLOY), TIMELINE & CONCLUSION
    # =========================================================================
    add_section_heading(doc, "9. Deploy: How Will the Decision Be Used?", page_break=True)
    add_stage_banner(doc, 7, "DEPLOY", "How will the decision be used?", HEX_SOFTGREEN, GREEN)
    add_body_p(
        doc,
        [
            "The evaluated pipeline will run behind a lightweight FastAPI service powering a three-screen mobile workflow (Figure 9, left): (1) curbside AR camera scan of the Qingqi rickshaw's plate and driver face, (2) live 5-second GPS trip telemetry along Raiwind Road and inner-city corridors with automatic walking-tail detection, and (3) an instant curbside scorecard returned within ",
            ("two seconds", True),
            " so the student can negotiate (e.g. comparing a 140 PKR quote against the 80 PKR fair fare) or wave the Qingqi on before boarding.\n"
            "Because our Evaluate stage proved that single rides are too noisy to judge a driver fairly (F1 = 0.71), deployment enforces four operational safeguards (Table 6). First, the app displays Insufficient Rides (< 5) until a driver accumulates at least five verified trips, where badge accuracy reaches 100%. Second, driver scores use an exponentially weighted moving median that weights recent rides more heavily, allowing drivers who improve their pricing or pace to recover their badge. Third, drivers can scan their own plate to inspect their log and flag disputed trips for review. Fourth, because fuel prices and inflation shift over time, the fair-fare GBR model is retrained monthly against fresh commuter benchmarks, feeding every completed trip back into the ",
            ("Collect", True),
            " stage. Figure 9 (right) outlines our eight-week execution plan from prototype to Superior University Gold Campus beta.",
        ],
    )

    t_f9 = doc.add_table(rows=1, cols=2)
    t_f9.alignment = WD_TABLE_ALIGNMENT.CENTER
    remove_table_borders(t_f9)
    t_f9.rows[0].cells[0].paragraphs[0].add_run().add_picture(str(FIG_DIR / "app_mockup.jpg"), width=Inches(3.15))
    t_f9.rows[0].cells[1].paragraphs[0].add_run().add_picture(str(FIG_DIR / "fig_timeline.png"), width=Inches(3.45))
    add_caption(
        doc,
        "Figure 9: ",
        "Left: proposed three-screen mobile workflow (Qingqi AR scan, live GPS tracking to Superior University, and curbside scorecard comparing 140 PKR quoted vs. 80 PKR fair). Right: eight-week execution roadmap.",
    )

    add_caption(doc, "Table 6: ", "Deployment safeguards translating evaluation lessons into responsible real-world operation.")
    t_sf = doc.add_table(rows=5, cols=3)
    t_sf.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_sf)
    for j, h in enumerate(["Operational risk", "Lifecycle evidence", "Deployment safeguard in RahiScan"]):
        format_table_cell(t_sf.rows[0].cells[j], h, size=8.5, bold=True, color=WHITE, bg=HEX_NAVY)
    sf_rows = [
        ("Single-ride traffic luck", "Single-ride pace macro F1 = 0.71 vs. 100% at ≥ 5 rides (Stage 6)", "Suppress pace and fare badges until a driver has ≥ 5 verified trips; show Insufficient Data otherwise."),
        ("Shift-shared Qingqis", "6 of 34 plates shared by day/night drivers with different habits (Stage 5)", "Key profiles to composite Plate#FaceID rather than license plate alone (99.8% precision)."),
        ("Forgotten End Ride taps", "13.8% of trips include pedestrian walking tails (Stage 3)", "Auto-trim trailing pings with speed < 6 km/h and step variance > 1.0 m/s², plus push-notification prompt."),
        ("Fuel & tariff drift", "Static fare models degrade when petrol prices shift (Stage 7)", "Retrain the GBR fair-fare model monthly on rolling benchmark quotes and weight recent rides exponentially."),
    ]
    for i, (rsk, evi, sfg) in enumerate(sf_rows, start=1):
        format_table_cell(t_sf.rows[i].cells[0], rsk, size=8.5, bold=True, color=NAVY, bg=HEX_SOFTBLUE)
        format_table_cell(t_sf.rows[i].cells[1], evi, size=8.5)
        format_table_cell(t_sf.rows[i].cells[2], sfg, size=8.5)

    # Conclusion callout box
    t_conc = doc.add_table(rows=2, cols=1)
    t_conc.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_conc, color="2B6CB0", sz="6")
    format_table_cell(t_conc.rows[0].cells[0], "Conclusion: Closing the Lifecycle Loop", size=10, bold=True, color=WHITE, bg="2B6CB0")
    format_table_cell(
        t_conc.rows[1].cells[0],
        "Our morning Qingqi commute to Superior University Gold Campus exposed a concrete failure mode at every stage of the Data Science Lifecycle. By validating our design on a 1,224-trip simulated Lahore pilot, we demonstrated that combining plate OCR with facial embeddings resolves shared-vehicle ambiguity at 99.8% precision, change-point trimming removes forgotten walking tails, gradient boosting predicts fair Qingqi fares (≈ 80 PKR for 9.6 km and ≈ 120 PKR from Raiwind to Gold Campus) within 1.8 PKR, and traffic-normalised multi-ride medians classify driver pace and pricing at 100% accuracy. Replacing our mock CSV streams with live student telemetry will turn RahiScan into a practical transparency tool for Lahore's daily commuters.",
        size=10.5,
        bg=HEX_SOFTBLUE,
        align=WD_ALIGN_PARAGRAPH.JUSTIFY,
    )

    doc.save(str(OUT_DOCX))
    shutil.copy2(str(OUT_DOCX), str(OUT_REPORT_DOCX))
    print(f"Saved {OUT_DOCX} and {OUT_REPORT_DOCX}")


if __name__ == "__main__":
    build_docx()
