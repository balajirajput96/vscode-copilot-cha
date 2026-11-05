#!/usr/bin/env python3
"""
======================================================================
 Balaji Dilipsingh Rajput - ATS-Compliant Resume Generator
 Optimized for Freshers (Biotechnology & Pharma QA/QC) & Experienced
 ---------------------------------------------------------------------
 INSTRUCTIONS:
   1. Install dependency:
          pip install reportlab pypdf
   2. Run script:
          python3 resume.py --profile fresher     # (Default)
          python3 resume.py --profile experienced
 ---------------------------------------------------------------------
 DESIGN:
   - ATS-safe single/dual-flow layout with standard Helvetica fonts.
   - Clickable mailto / tel / LinkedIn / GitHub hyperlinks in header.
   - Two-pass NumberedCanvas for dynamic page numbering ('Page X of Y').
   - Strict 2-page pagination budget.
======================================================================
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Flowable,
    Paragraph,
    Spacer,
    HRFlowable,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Table,
    TableStyle,
)
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

# ---------------------------------------------------------------- palette
NAVY = HexColor("#0B2E4F")     # Name + Section headings
ACCENT = HexColor("#1E5F8E")   # Rules, links, subtle markers
DARK = HexColor("#222222")     # Body text
GREY = HexColor("#555555")     # Meta text
HAIR = HexColor("#C9D4DC")     # Divider lines
HDRBG = HexColor("#F2F6F9")    # Header background tint

PW, PH = A4
ML = MR = 14 * mm
MT = 12 * mm
MB = 12 * mm
CW = PW - ML - MR
BUL = "\u2022"
EN = "\u2013"

# ---------------------------------------------------------------- contact details
NAME = "BALAJI DILIPSINGH RAJPUT"
PHONE = "+91 87808 61044"
PHONE_CLEAN = "+918780861044"
EMAIL = "balajirajput966@gmail.com"
LOCATION = "Vadodara, Gujarat 390010, India"
LINKEDIN = "linkedin.com/in/balaji-rajput-483a86194"
LINKEDIN_URL = "https://linkedin.com/in/balaji-rajput-483a86194"
GITHUB = "github.com/balajirajput96"
GITHUB_URL = "https://github.com/balajirajput96"


# ---------------------------------------------------------------- typography styles
def st(name: str, **kw: Any) -> ParagraphStyle:
    base = dict(fontName="Helvetica", fontSize=8.5, leading=11.5, textColor=DARK, spaceAfter=0)
    base.update(kw)
    return ParagraphStyle(name, **base)


S = {
    "name": st("name", fontName="Helvetica-Bold", fontSize=20, leading=22, textColor=NAVY, alignment=TA_CENTER),
    "title": st("title", fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=ACCENT, alignment=TA_CENTER),
    "contact": st("contact", fontSize=8.2, leading=11.5, textColor=DARK, alignment=TA_CENTER),
    "sect": st("sect", fontName="Helvetica-Bold", fontSize=10.2, leading=12.5, textColor=NAVY, spaceBefore=4),
    "body": st("body", fontSize=8.5, leading=11.5, alignment=TA_JUSTIFY, spaceAfter=1),
    "job_left": st("job_left", fontName="Helvetica-Bold", fontSize=9.0, leading=11.5, textColor=NAVY),
    "job_right": st("job_right", fontName="Helvetica-Bold", fontSize=8.4, leading=11.5, textColor=ACCENT, alignment=TA_RIGHT),
    "meta": st("meta", fontName="Helvetica-Oblique", fontSize=8.2, leading=10.5, textColor=GREY, spaceAfter=1),
    "bullet": st("bullet", fontSize=8.2, leading=10.8, alignment=TA_JUSTIFY),
    "small": st("small", fontSize=8.2, leading=10.8, textColor=DARK),
    "decl": st("decl", fontName="Helvetica-Oblique", fontSize=7.8, leading=10.2, textColor=DARK),
}


def rule(space_after: float = 3) -> HRFlowable:
    return HRFlowable(width="100%", thickness=1.0, color=ACCENT, spaceBefore=1, spaceAfter=space_after)


def heading(title: str) -> KeepTogether:
    key = "sec_" + "".join(ch for ch in title.lower() if ch.isalnum())
    para = Paragraph(f"<b>{title.upper()}</b>", S["sect"])
    kt = KeepTogether([para, rule()])
    kt.keepWithNext = 1
    return kt


def bullets(items: List[str], style: str = "bullet", gap: float = 1.0) -> ListFlowable:
    return ListFlowable(
        [ListItem(Paragraph(t, S[style]), leftIndent=10, value=BUL, spaceAfter=gap) for t in items],
        bulletType="bullet",
        bulletColor=ACCENT,
        bulletFontSize=7.5,
        leftIndent=10,
        bulletOffsetY=0.5,
    )


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._saved_page_states: List[Dict[str, Any]] = []

    def showPage(self) -> None:
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self) -> None:
        total = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_decorations(total)
            super().showPage()
        super().save()

    def _draw_decorations(self, total: int) -> None:
        self.saveState()
        # Top rule on page 2+
        if self._pageNumber > 1:
            self.setStrokeColor(ACCENT)
            self.setLineWidth(1.0)
            self.line(ML, PH - 9 * mm, PW - MR, PH - 9 * mm)

            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(NAVY)
            self.drawString(ML, PH - 8 * mm, NAME)

            self.setFont("Helvetica", 7.5)
            self.setFillColor(GREY)
            self.drawRightString(PW - MR, PH - 8 * mm, "Curriculum Vitae | Balaji Dilipsingh Rajput")

        # Footer
        self.setStrokeColor(HAIR)
        self.setLineWidth(0.6)
        self.line(ML, 9 * mm, PW - MR, 9 * mm)

        self.setFont("Helvetica", 7.5)
        self.setFillColor(GREY)
        self.drawString(ML, 6.0 * mm, f"{NAME}   {BUL}   {PHONE}   {BUL}   {EMAIL}")
        self.drawRightString(PW - MR, 6.0 * mm, f"Page {self._pageNumber} of {total}")
        self.restoreState()


def header_block(title_text: str) -> List[Flowable]:
    contact1 = (
        f"Location: {LOCATION} &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"Phone: <a href='tel:{PHONE_CLEAN}'><u>{PHONE}</u></a> &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"Email: <a href='mailto:{EMAIL}'><font color='#1E5F8E'><u>{EMAIL}</u></font></a>"
    )
    contact2 = (
        f"LinkedIn: <a href='{LINKEDIN_URL}'><font color='#1E5F8E'><u>{LINKEDIN}</u></font></a> &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"GitHub: <a href='{GITHUB_URL}'><font color='#1E5F8E'><u>{GITHUB}</u></font></a>"
    )
    return [
        Paragraph(NAME, S["name"]),
        Paragraph(title_text, S["title"]),
        Spacer(1, 1),
        Paragraph(contact1, S["contact"]),
        Paragraph(contact2, S["contact"]),
        HRFlowable(width="100%", thickness=1.2, color=NAVY, spaceBefore=2, spaceAfter=3),
    ]


def build_fresher_story() -> List[Flowable]:
    story: List[Flowable] = []
    title_text = "Biotechnology Graduate | Entry-Level QA/QC Trainee | Computational & Wet-Lab Analyst"
    story.extend(header_block(title_text))

    # Summary
    story.append(heading("Career Objective & Professional Summary"))
    story.append(
        Paragraph(
            "Goal-oriented and detail-focused Biotechnology graduate with demonstrated academic excellence "
            "and foundational competence in cGMP/GDP compliance, wet-lab analytical techniques, and computational pipelines. "
            "Recipient of the <b>Best Research Project Award (2024)</b> and <b>Dean's List</b> distinction. Practical exposure "
            "encompasses genomic data workflows (Biotecnika), GLP microbiology & PCR testing (Gujarat Biotech Innovations), "
            "and industrial exposure in Oral Solid Dosage manufacturing. Proactive learner seeking an entry-level position as "
            "<b>Quality Assurance (QA) Trainee</b>, <b>IPQA Officer</b>, or <b>Quality Control (QC) Chemist</b> in Gujarat's pharmaceutical sector. "
            "Available to join immediately.",
            S["body"],
        )
    )
    story.append(Spacer(1, 2))

    # Core Competencies
    story.append(heading("Core Competencies & Foundational Knowledge"))
    comp_l = [
        "• cGMP, GDP & GLP Principles",
        "• SOP Drafting & Document Lifecycle",
        "• In-Process Quality Checks (IPQA)",
        "• Good Documentation Practices (ALCOA+)",
        "• 21 CFR Part 11 & Schedule M Awareness",
        "• Label Reconciliation & Inspection",
    ]
    comp_r = [
        "• Deviation & CAPA Basics",
        "• BMR / BPR Review Protocols",
        "• HPLC & Spectrophotometry Concepts",
        "• Microbial Testing & Aseptic Culture",
        "• Quality Management System (QMS)",
        "• Root Cause Analysis (5-Why, Fishbone)",
    ]
    c_table = Table(
        [[Paragraph(l, S["small"]), Paragraph(r, S["small"])] for l, r in zip(comp_l, comp_r)],
        colWidths=[CW / 2.0, CW / 2.0],
    )
    c_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )
    story.append(c_table)
    story.append(Spacer(1, 2))

    # Education
    story.append(heading("Education"))
    edu_tbl = Table(
        [
            [
                Paragraph("<b>Diploma in Biotechnology</b>", S["job_left"]),
                Paragraph("2021 – 2025", S["job_right"]),
            ]
        ],
        colWidths=[CW * 0.75, CW * 0.25],
    )
    edu_tbl.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0)]))
    story.append(edu_tbl)
    story.append(
        Paragraph(
            "Parul Institute of Technology & Engineering, Gujarat Technological University (GTU), Vadodara",
            S["meta"],
        )
    )
    story.append(
        bullets(
            [
                "<b>Honors / Performance:</b> CGPA: 6.7 / 10 | Dean's List for Academic Excellence (2024–2025)",
                "Key Subjects: Molecular Biology, Microbiology, Bioprocess Technology, Biochemistry, Immunology, Fermentation Technology, QC & QA.",
            ],
            gap=1,
        )
    )
    story.append(Spacer(1, 2))

    # Industrial Training & Internships
    story.append(heading("Industrial Training & Internship Experience"))

    def exp_block(role: str, comp: str, dur: str, items: List[str]) -> List[Flowable]:
        tbl = Table(
            [[Paragraph(f"<b>{role}</b> — {comp}", S["job_left"]), Paragraph(dur, S["job_right"])]],
            colWidths=[CW * 0.75, CW * 0.25],
        )
        tbl.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0)]))
        return [tbl, Spacer(1, 1), bullets(items, gap=1), Spacer(1, 2)]

    story.extend(
        exp_block(
            "Industrial QA Trainee / Apprentice",
            "Elysium Pharmaceuticals Ltd., Vadodara",
            "Mar 2024 – Mar 2026",
            [
                "Received hands-on industrial training in Oral Solid Dosage (tablets) manufacturing under strict cGMP and Schedule M standards.",
                "Assisted IPQA officers in line clearance, physical parameter checks (hardness, friability, disintegration), and BMR/BPR log verification.",
                "Observed and supported SOP authoring, deviation tracking, and preparation of documentation packages for CDSCO/WHO-GMP audit readiness.",
            ],
        )
    )
    story.extend(
        exp_block(
            "Bioinformatics Intern",
            "Biotecnika (Remote)",
            "2024 (3 Months)",
            [
                "Engineered automated Python / Biopython workflows for sequence alignment, screening over 500+ DNA and protein sequences.",
                "Utilized BLAST, ClustalW, and GenBank annotations to streamline curation workflows, cutting manual processing time by 40%.",
            ],
        )
    )
    story.extend(
        exp_block(
            "Laboratory Research Intern",
            "Gujarat Biotech Innovations",
            "2023 (2 Months)",
            [
                "Carried out routine laboratory assays: PCR, agarose gel electrophoresis, and microbial culture handling for 80+ samples/week.",
                "Authored 3 standard operating procedures (SOPs) compliant with GLP standards; elevated laboratory sample workflow efficiency by 20%.",
            ],
        )
    )

    # PAGE 2
    story.append(PageBreak())

    # Projects
    story.append(heading("Key Academic & Research Projects"))
    story.append(
        bullets(
            [
                "<b>Bioethanol Production from Agricultural Waste (2024):</b> Optimized SSF with <i>S. cerevisiae</i> via Response Surface Methodology (RSM/DOE); achieved a <b>15% yield enhancement</b> validated by HPLC (p &lt; 0.05). <b>Awarded Best Research Project – Parul Institute 2024</b>.",
                "<b>Comparative Genomic Analysis of AMR Genes (2024):</b> Analyzed 120 bacterial genomes from NCBI GenBank using an automated Python/Biopython workflow; identified <b>8 novel Antimicrobial Resistance (AMR) gene variants</b> across 500+ sequence entries.",
                "<b>Protein Structure Prediction & Molecular Docking (2023):</b> Constructed 3D homology models for 5 therapeutic target proteins via SWISS-MODEL; screened and docked 50 ligands via AutoDock Vina, identifying 3 lead inhibitors (&le; -8.0 kcal/mol).",
                "<b>Biogenic Synthesis of Silver Nanoparticles (AgNPs) (2023):</b> Synthesized antimicrobial AgNPs via green biogenic route using <i>Pseudomonas spp.</i>; confirmed nanoparticle formation and bactericidal efficacy via UV-Vis Spectrophotometry and zone assays.",
            ],
            gap=2,
        )
    )
    story.append(Spacer(1, 2))

    # Skills
    story.append(heading("Technical & Laboratory Skills"))
    story.append(
        bullets(
            [
                "<b>Quality & Regulatory:</b> cGMP, GDP, GLP, Schedule M, SOP Drafting, BMR / BPR Verification, Deviation & CAPA Basics, Change Control Awareness, Data Integrity (ALCOA+), 21 CFR Part 11, CDSCO & WHO-GMP Guidelines.",
                "<b>Laboratory & Analytical:</b> HPLC (Fundamentals), PCR / RT-PCR, UV-Vis Spectrophotometry, Agarose Gel Electrophoresis, Microbial & Aseptic Culture, Sterility Testing, Disintegration & Friability, Autoclave, LAF.",
                "<b>Bioinformatics & Computation:</b> Python (Biopython, Pandas, NumPy), R Basics, BLAST, ClustalW, NCBI GenBank, UniProt, AutoDock Vina, SWISS-MODEL, PyMOL.",
                "<b>Software & Digital Tools:</b> MS Office Suite (Advanced Excel, Word, PowerPoint), SPSS, MATLAB (Basic), Git & GitHub, TrackWise (Basics), Google Workspace.",
            ],
            gap=1.5,
        )
    )
    story.append(Spacer(1, 2))

    # Certifications
    story.append(heading("Certifications & Specialized Training"))
    cert_l = [
        "• Bioinformatics Specialization – Coursera / UC San Diego (2024)",
        "• Python for Genomic Data Science – Coursera / Johns Hopkins (2024)",
        "• Industrial Biotechnology & GMP – NPTEL / IIT Madras (2023)",
    ]
    cert_r = [
        "• Advanced Techniques in Biotechnology – Parul University (2025)",
        "• Molecular Biology Techniques – Udemy (2023)",
        "• Digital Marketing & Web Foundations – Google / ITI (2021–2024)",
    ]
    cert_tbl = Table(
        [[Paragraph(l, S["small"]), Paragraph(r, S["small"])] for l, r in zip(cert_l, cert_r)],
        colWidths=[CW / 2.0, CW / 2.0],
    )
    cert_tbl.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )
    story.append(cert_tbl)
    story.append(Spacer(1, 2))

    # Achievements
    story.append(heading("Key Honors & Achievements"))
    story.append(
        bullets(
            [
                "<b>Best Research Project Award (2024)</b> – Parul Institute of Technology & Engineering for Bioethanol SSF optimization.",
                "<b>Dean's List for Academic Excellence (2024–2025)</b> – Recognized for top percentile academic performance in Biotechnology coursework.",
                "<b>Automated Genomic Pipeline</b> – Developed Python workflow reducing manual sequence curation time by 40% (AMR study).",
            ],
            gap=1.5,
        )
    )
    story.append(Spacer(1, 2))

    # Personal Dossier & Declaration
    story.append(heading("Personal Dossier & Declaration"))
    story.append(Paragraph("<b>Languages Known:</b> English (Fluent), Hindi (Fluent), Gujarati (Native)", S["small"]))
    story.append(Spacer(1, 1))
    story.append(Paragraph("<b>Details:</b> Date of Birth: 20 June 2001 | Marital Status: Single | Nationality: Indian | Availability: Immediate Joiner", S["small"]))
    story.append(Spacer(1, 2))
    story.append(Paragraph("<i>I hereby solemnly declare that all statements and particulars provided in this resume are true, complete, and authentic to the best of my knowledge.</i>", S["decl"]))
    story.append(Spacer(1, 3))

    sig_data = [
        [Paragraph("<b>Place:</b> Vadodara, Gujarat", S["small"]), Paragraph("<b>(Balaji Dilipsingh Rajput)</b>", S["job_right"])],
        [Paragraph("<b>Date:</b> ____________________", S["small"]), Paragraph("Candidate Signature", S["job_right"])],
    ]
    sig_table = Table(sig_data, colWidths=[CW * 0.5, CW * 0.5])
    sig_table.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 1)]))
    story.append(sig_table)

    return story


def build_experienced_story() -> List[Flowable]:
    story: List[Flowable] = []
    title_text = "Quality Assurance Officer  |  IPQA Officer  |  Pharmaceutical QA"
    story.extend(header_block(title_text))

    # Professional Summary
    story.append(heading("Professional Summary"))
    story.append(
        Paragraph(
            "Detail-oriented and compliance-focused Quality Assurance Officer with 2+ years of hands-on experience in Oral Solid Dosage "
            "(tablet) manufacturing at Elysium Pharmaceuticals Ltd., Vadodara, working within cGMP, GDP, and Schedule M frameworks. "
            "Skilled in SOP authoring, deviation management, CAPA, BMR/BPR review, change control, in-process quality checks (IPQA), and "
            "OOS/OOT investigation support. Proven audit readiness for CDSCO and WHO-GMP inspections. Available immediately.",
            S["body"],
        )
    )
    story.append(Spacer(1, 2))

    # Core Competencies
    story.append(heading("Core Competencies"))
    comp_l = [
        "• cGMP / GDP / GLP & Schedule M",
        "• SOP Writing & Periodic Review",
        "• Batch Record Review (BMR / BPR)",
        "• Deviation Management & CAPA",
        "• Change Control Management",
        "• OOS / OOT Investigation Support",
    ]
    comp_r = [
        "• In-Process Quality Assurance (IPQA)",
        "• Internal Audit & Self-Inspection",
        "• QMS & Documentation Control",
        "• Data Integrity (ALCOA+) & 21 CFR 11",
        "• CDSCO / WHO-GMP Audit Readiness",
        "• Vendor Qualification Support",
    ]
    c_table = Table(
        [[Paragraph(l, S["small"]), Paragraph(r, S["small"])] for l, r in zip(comp_l, comp_r)],
        colWidths=[CW / 2.0, CW / 2.0],
    )
    c_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )
    story.append(c_table)
    story.append(Spacer(1, 2))

    # Professional Experience
    story.append(heading("Professional Experience"))
    exp_tbl = Table(
        [
            [
                Paragraph("<b>QA Officer / IPQA Officer</b> — Elysium Pharmaceuticals Ltd.", S["job_left"]),
                Paragraph("Mar 2024 – Mar 2026 (2 Years)", S["job_right"]),
            ]
        ],
        colWidths=[CW * 0.75, CW * 0.25],
    )
    exp_tbl.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0)]))
    story.append(exp_tbl)
    story.append(Paragraph("Dabhasa, Vadodara, Gujarat  •  Department: Quality Assurance", S["meta"]))
    story.append(
        bullets(
            [
                "Authored and reviewed Standard Operating Procedures (SOPs) maintaining cGMP, GDP, and Schedule M compliance.",
                "Reviewed and verified 50+ BMRs and BPRs monthly alongside yield reconciliation logs, reducing discrepancies by 15%.",
                "Conducted line clearance and in-process quality checks (IPQA) across granulation, compression, and packaging.",
                "Identified and investigated deviations using structured root-cause analysis (5-Why, Fishbone); executed CAPAs to timely closure.",
                "Prepared documentation packages and supported audit readiness for CDSCO and WHO-GMP regulatory inspections.",
            ],
            gap=1,
        )
    )
    story.append(Spacer(1, 2))

    # Education
    story.append(heading("Education"))
    edu_tbl = Table(
        [
            [
                Paragraph("<b>Diploma in Biotechnology</b>", S["job_left"]),
                Paragraph("2021 – 2025", S["job_right"]),
            ]
        ],
        colWidths=[CW * 0.75, CW * 0.25],
    )
    edu_tbl.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0)]))
    story.append(edu_tbl)
    story.append(Paragraph("Parul Institute of Technology & Engineering, GTU, Vadodara", S["meta"]))
    story.append(
        bullets(
            [
                "Honours: Dean's List for Academic Excellence (2024–25); Best Research Project Award 2024 (Bioethanol SSF).",
                "Key Subjects: Molecular Biology, Biochemistry, Microbiology, Bioprocess Technology, Immunology, Fermentation.",
            ],
            gap=1,
        )
    )

    # PAGE 2
    story.append(PageBreak())

    # Projects
    story.append(heading("Key Research Projects"))
    story.append(
        bullets(
            [
                "<b>Bioethanol Production from Agricultural Waste (2024):</b> Optimised SSF process with S. cerevisiae using RSM/DOE; achieved 15% yield improvement validated via HPLC and ANOVA (p&lt;0.05). Best Research Project Award.",
                "<b>Comparative Genomic Analysis of AMR Genes (2024):</b> Analysed 120 bacterial genomes (NCBI GenBank) with an automated Python/Biopython BLAST pipeline; discovered 8 novel resistance gene variants from 500+ sequences.",
                "<b>Protein Structure Prediction & Molecular Docking (2023):</b> Modelled 5 therapeutic proteins (SWISS-MODEL) and docked 50 ligands (AutoDock Vina); identified 3 lead compounds (binding affinity &le; -8.0 kcal/mol).",
            ],
            gap=2,
        )
    )
    story.append(Spacer(1, 2))

    # Technical Skills
    story.append(heading("Technical Skills"))
    story.append(
        bullets(
            [
                "<b>QA / Regulatory:</b> GMP, cGMP, GDP, GLP, SOP Writing, CAPA, Deviation Management, BMR/BPR Review, Change Control, OOS/OOT, QMS, Internal Audit, 21 CFR Part 11, CDSCO, WHO-GMP.",
                "<b>Laboratory:</b> HPLC, PCR (RT-PCR, qPCR), UV-Vis Spectrophotometry, Gel Electrophoresis, Microbial & Cell Culture, Sterility Testing, Autoclave, LAF.",
                "<b>Bioinformatics:</b> Python (Biopython, Pandas, NumPy), R (Bioconductor), BLAST, ClustalW, NCBI GenBank, UniProt, AutoDock Vina, SWISS-MODEL, PyMOL.",
                "<b>Software & Tools:</b> MS Office Suite (Advanced), TrackWise (Basics), SAP (Basics), SPSS, MATLAB, Git/GitHub.",
            ],
            gap=1.5,
        )
    )
    story.append(Spacer(1, 2))

    # Certifications
    story.append(heading("Certifications"))
    cert_l = [
        "• Bioinformatics Specialization – Coursera / UCSD (2024)",
        "• Python for Genomic Data Science – Coursera / JHU (2024)",
        "• Industrial Biotech & GMP – NPTEL / IIT Madras (2023)",
    ]
    cert_r = [
        "• Advanced Techniques in Biotech – Parul University (2025)",
        "• Molecular Biology Techniques – Udemy (2023)",
        "• Digital Marketing & Web Designing – Google / ITI (2021–2024)",
    ]
    cert_tbl = Table(
        [[Paragraph(l, S["small"]), Paragraph(r, S["small"])] for l, r in zip(cert_l, cert_r)],
        colWidths=[CW / 2.0, CW / 2.0],
    )
    cert_tbl.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )
    story.append(cert_tbl)
    story.append(Spacer(1, 2))

    # Key Achievements
    story.append(heading("Key Achievements"))
    story.append(
        bullets(
            [
                "100% cGMP & GDP compliance maintained across batch records; zero critical observations during inspection reviews.",
                "Authored 15+ SOPs driving 20% efficiency improvement; Best Research Project Award (Parul Institute 2024).",
                "8 novel AMR variants identified; 40% reduction in curation time via Python automation; Dean's List 2024–2025.",
            ],
            gap=1.5,
        )
    )
    story.append(Spacer(1, 2))

    # Personal Details
    story.append(heading("Personal Details & Declaration"))
    story.append(Paragraph("<b>Languages:</b> English (Fluent), Hindi (Fluent), Gujarati (Native)", S["small"]))
    story.append(Spacer(1, 1))
    story.append(Paragraph("<b>Details:</b> Date of Birth: 20 June 2001 | Marital Status: Single | Nationality: Indian | Availability: Immediate Joiner", S["small"]))
    story.append(Spacer(1, 2))
    story.append(Paragraph("<i>I hereby declare that the information furnished above is true and correct to the best of my knowledge and belief.</i>", S["decl"]))
    story.append(Spacer(1, 3))

    sig_data = [
        [Paragraph("<b>Place:</b> Vadodara, Gujarat", S["small"]), Paragraph("<b>(Balaji Dilipsingh Rajput)</b>", S["job_right"])],
        [Paragraph("<b>Date:</b> ____________________", S["small"]), Paragraph("Candidate Signature", S["job_right"])],
    ]
    sig_table = Table(sig_data, colWidths=[CW * 0.5, CW * 0.5])
    sig_table.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 1)]))
    story.append(sig_table)

    return story


def build_pdf(output_file: str, profile: str = "fresher") -> str:
    out_path = Path(output_file).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    doc = BaseDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=ML,
        rightMargin=MR,
        topMargin=MT,
        bottomMargin=MB,
        title=f"Balaji Dilipsingh Rajput - {profile.title()} Resume",
        author="Balaji Dilipsingh Rajput",
        subject=f"{profile.title()} Resume for Biotechnology & Pharmaceutical QA/QC",
    )

    frame = Frame(ML, MB, CW, PH - MT - MB, id="full", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame])])

    story = build_fresher_story() if profile == "fresher" else build_experienced_story()
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Created {out_path} ({profile} profile)")
    return str(out_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate ATS-compliant resume PDF.")
    parser.add_argument("--profile", choices=["fresher", "experienced"], default="fresher", help="Profile to generate (default: fresher)")
    parser.add_argument("--output", "-o", type=str, default=None, help="Output PDF file path")
    args = parser.parse_args()

    default_name = "Balaji_Rajput_Fresher_Resume.pdf" if args.profile == "fresher" else "Balaji_Rajput_QA_Officer_Resume.pdf"
    output = args.output or str(Path(__file__).resolve().parent / default_name)

    build_pdf(output, profile=args.profile)


if __name__ == "__main__":
    main()
