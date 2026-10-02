#!/usr/bin/env python3
"""Create a professionally formatted Google Doc resume for BMO Head of AI and Digital Innovation.

Design: White background with teal section labels in left column.
Each role gets its own table row so page breaks happen between roles.
Montserrat + Calibri typography. Exports to PDF via Drive API.
"""

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
]

CREDENTIALS_PATH = os.path.expanduser("~/.claude/.google/client_secret.json")
TOKEN_PATH = os.path.expanduser("~/.claude/.google/token.json")

# --- Design Constants ---
TEAL = {"red": 74 / 255, "green": 124 / 255, "blue": 143 / 255}  # #4A7C8F
DARK_TEAL = {"red": 55 / 255, "green": 97 / 255, "blue": 112 / 255}
WHITE = {"red": 1.0, "green": 1.0, "blue": 1.0}
DARK_GRAY = {"red": 0.2, "green": 0.2, "blue": 0.2}
MED_GRAY = {"red": 0.4, "green": 0.4, "blue": 0.4}
BLACK = {"red": 0.0, "green": 0.0, "blue": 0.0}

LEFT_COL_PT = 99


# --- Content Builder ---
class CellContent:
    def __init__(self):
        self.text = ""
        self.styles = []
        self.para_styles = []

    def add(self, text, font="Calibri", size=9, bold=False, italic=False, color=None):
        start = len(self.text)
        self.text += text
        end = len(self.text)
        style = {
            "weightedFontFamily": {"fontFamily": font},
            "fontSize": {"magnitude": size, "unit": "PT"},
            "bold": bold,
            "italic": italic,
        }
        fields = ["weightedFontFamily", "fontSize", "bold", "italic"]
        if color:
            style["foregroundColor"] = {"color": {"rgbColor": color}}
            fields.append("foregroundColor")
        self.styles.append((start, end, style, ",".join(fields)))
        return self

    def add_spacing(self, start_offset, end_offset, above_pt=0, below_pt=0):
        ps = {"lineSpacing": 100}
        fields = ["lineSpacing"]
        if above_pt is not None:
            ps["spaceAbove"] = {"magnitude": above_pt, "unit": "PT"}
            fields.append("spaceAbove")
        if below_pt is not None:
            ps["spaceBelow"] = {"magnitude": below_pt, "unit": "PT"}
            fields.append("spaceBelow")
        self.para_styles.append((start_offset, end_offset, ps, ",".join(fields)))
        return self

    def add_hanging_indent(self, start_offset, end_offset, indent_pt=14):
        ps = {
            "indentStart": {"magnitude": indent_pt, "unit": "PT"},
            "indentFirstLine": {"magnitude": 0, "unit": "PT"},
        }
        self.para_styles.append((start_offset, end_offset, ps, "indentStart,indentFirstLine"))
        return self

    def build_requests(self, cell_start_index):
        reqs = []
        if not self.text:
            return reqs
        reqs.append({
            "insertText": {
                "location": {"index": cell_start_index},
                "text": self.text,
            }
        })
        for s, e, style, fields in self.styles:
            reqs.append({
                "updateTextStyle": {
                    "range": {"startIndex": cell_start_index + s, "endIndex": cell_start_index + e},
                    "textStyle": style,
                    "fields": fields,
                }
            })
        for s, e, ps, fields in self.para_styles:
            reqs.append({
                "updateParagraphStyle": {
                    "range": {"startIndex": cell_start_index + s, "endIndex": cell_start_index + e},
                    "paragraphStyle": ps,
                    "fields": fields,
                }
            })
        return reqs


def get_credentials():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
    return creds


def get_table_cell_indices(doc, table_idx=0):
    body = doc.get("body", {}).get("content", [])
    tables = [el for el in body if "table" in el]
    table = tables[table_idx]["table"]
    result = []
    for row in table.get("tableRows", []):
        row_indices = []
        for cell in row.get("tableCells", []):
            content = cell.get("content", [])
            if content:
                row_indices.append(content[0].get("startIndex", 0))
        result.append(row_indices)
    return result


def get_table_start_index(doc, table_idx=0):
    body = doc.get("body", {}).get("content", [])
    tables = [el for el in body if "table" in el]
    return tables[table_idx].get("startIndex", 1)


# --- Content helpers ---

def left_cell(label=""):
    c = CellContent()
    if label:
        c.add(label, font="Montserrat", size=9, bold=True, color=TEAL)
    return c


def role_cell(title, company, dates, context=None, bullets=None):
    c = CellContent()
    role_start = len(c.text)
    c.add(title, font="Montserrat", size=10, bold=True, color=BLACK)
    c.add(f" \u2014 {company}\n", font="Montserrat", size=10, color=DARK_GRAY)
    c.add(dates + "\n", font="Montserrat", size=9, italic=True, color=MED_GRAY)
    c.add_spacing(role_start, len(c.text), above_pt=2, below_pt=0)
    if context:
        ctx_start = len(c.text)
        c.add(context + "\n", font="Calibri", size=9, italic=True, color=MED_GRAY)
        c.add_spacing(ctx_start, len(c.text), above_pt=0, below_pt=2)
    if bullets:
        for bullet in bullets:
            b_start = len(c.text)
            c.add(f"\u2022\t{bullet}\n", font="Calibri", size=9, color=DARK_GRAY)
            c.add_spacing(b_start, len(c.text), above_pt=0, below_pt=2)
            c.add_hanging_indent(b_start, len(c.text))
    return c


# --- Define all rows ---

def build_rows():
    rows = []

    # Row 0: PROFILE
    profile_text = (
        "Capital markets technology executive with 18+ years in financial services "
        "\u2014 including 8 years at BMO Capital Markets \u2014 combining deep trading "
        "technology expertise with hands-on AI product leadership. Currently serving as "
        "CTO building an AI governance platform powered by LLMs and agentic AI, while "
        "drawing on 13 years of capital markets experience across FX, FICC, and Fixed "
        "Income. Proven track record driving enterprise-wide digital transformation, "
        "managing $22MM budgets, leading 60+ person teams, and delivering measurable "
        "commercial outcomes including $30M+ in annual savings, $8M in revenue gains, "
        "and 50%+ productivity improvements."
    )
    c = CellContent()
    c.add(profile_text, font="Calibri", size=9, color=DARK_GRAY)
    c.add_spacing(0, len(c.text), above_pt=2, below_pt=2)
    rows.append(("PROFILE", c, True))

    # Row 1: COMPETENCIES
    c = CellContent()
    cats = [
        ("AI & Digital Innovation", "LLM Implementation | Agentic AI | LangChain | Azure AI Foundry | TensorFlow (CNNs, NLP) | AI Governance & Risk Management | Generative AI Product Development | Claude Code"),
        ("Capital Markets & Trading", "FX Trading Systems | FICC Architecture | Wall Street Systems | CLS Settlement | Algorithmic Workflows | Risk Management Automation | Client Engagement Platforms"),
        ("Leadership & Transformation", "Enterprise Digital Strategy | Organizational Change Management | Cross-Functional Program Delivery | Executive Stakeholder Management | P&L Ownership ($22MM) | Portfolio Governance"),
        ("Cloud & Architecture", "Azure (Entra ID, Cosmos DB, Serverless, DevOps Pipelines, Key Vault, AI Foundry) | AWS | GCP | CI/CD | DevOps | Cybersecurity"),
    ]
    for i, (label, desc) in enumerate(cats):
        start = len(c.text)
        c.add(f"{label}:  ", font="Calibri", size=9, bold=True, color=DARK_GRAY)
        c.add(desc, font="Calibri", size=9, color=DARK_GRAY)
        if i < len(cats) - 1:
            c.add("\n")
        c.add_spacing(start, len(c.text), above_pt=1, below_pt=1)
    rows.append(("COMPETENCIES", c, True))

    # Rows 2+: EXPERIENCE
    exp_roles = [
        ("CTO & Chief Product Owner", "Prodago",
         "07/2022 \u2013 Present  |  Montreal",
         "Data and AI governance platform \u2014 built team and product from zero to $200K+ ARR.",
         [
             "Designed and launched an AI platform powered by LLMs and AI agents (LangChain) to operationalize regulatory compliance frameworks, enabling clients to bring governance policies to life",
             "Established AI governance practices ensuring responsible AI deployment, compliance, and risk management across the platform",
             "Pioneered adoption of generative AI tools (Cursor, Claude Code) to accelerate development velocity and improve code quality, requirements, design, and testing",
             "Led global distributed team on Azure infrastructure (AI Foundry, Cosmos DB, Serverless Functions), reducing deployment costs by 50%",
             "Partnered with CEO/COO to align product roadmap with enterprise priorities, presenting to CEO/CRO/CFO forums",
         ]),
        ("Enterprise Consultant", "Manulife / John Hancock",
         "06/2021 \u2013 06/2025  |  Boston / Toronto",
         "Multi-year consulting engagement driving technology strategy transformation for enterprise tech services.",
         [
             "Realigned cross-functional fraud prevention efforts at John Hancock, delivering $30M+ in annual savings and doubling throughput",
             "Achieved 28% increase in ROI on invested capital, 2\u00d7 realization of benefits, and 3\u00d7 improvement in OKR attainment",
             "Designed CapEx/OpEx reclassification model, reclassifying 17% of OpEx to CapEx via real-time attribution \u2014 eliminating timesheets",
             "Introduced delivery dashboards and agile practices that doubled release velocity across the portfolio",
             "Chaired governance and offsite sessions, aligning enterprise strategy with execution for $MM transformation portfolios",
         ]),
        ("Founder & CTO", "Infaque",
         "01/2021 \u2013 Present  |  Toronto / Lahore",
         "SaaS product company and offshore development arm, scaling from concept to $50K+ ARR across 20+ clients.",
         [
             "Built SaaS platform from scratch, scaling to MRR across 20+ non-profit clients",
             "Founded and led offshore development operation (Lahore), reducing client development costs by 70%",
             "Standardized CI/CD, access policies, and observability across a 100% remote engineering team",
         ]),
        ("Director & Head of Business Agility COE", "Royal Bank of Canada",
         "06/2018 \u2013 06/2021  |  Toronto",
         "Led enterprise-wide organizational transformation and digital adoption across one of Canada\u2019s largest banks.",
         [
             "Led transformation of RBC, driving strategic agility initiatives and digital enablement across 4 divisions",
             "Implemented agile methodologies resulting in productivity gains exceeding 50% in four key business units",
             "Facilitated adoption of prioritization and work visualization practices among 20% of RBC executives within two years",
             "Aligned delivery to business outcomes via Operating Committee-led OKRs",
         ]),
        ("FICC Architect & Agile Adoption", "RBC Capital Markets",
         "06/2017 \u2013 06/2018  |  Toronto",
         None,
         [
             "Optimized development activities to increase efficiency by 35% through process optimization and tooling integration",
             "Integrated Jira with Jenkins, Ansible, ELK stack, and automated testing tools for continuous delivery",
             "Streamlined operations, decreasing downtime and manual efforts for 20 applications by 25%",
         ]),
        ("Director & Regional Head of FX Technology", "RBC Capital Markets",
         "10/2016 \u2013 06/2017  |  Toronto",
         None,
         [
             "Directed $22MM budget, achieving $5MM in vendor cost savings through strategic management",
             "Generated $3MM in recurring revenue by increasing deal flow in EM FX forwards",
             "Modernized FX technology stack and doubled quarterly release cadence via Agile and OKR tracking",
         ]),
        ("Head of FX Technology", "BMO Capital Markets",
         "01/2014 \u2013 02/2016  |  Toronto",
         "Culmination of 8-year career at BMO, rising from Java Developer to department head.",
         [
             "Oversaw 60+ professionals and managed $17MM annual budget across FX trading and operations technology",
             "Led replacement of IBUK, a legacy operations system from the 1970s, bringing BMO to full CLS (Continuous Linked Settlement) membership",
             "Modernized the entire FX technology stack by implementing Wall Street Systems 5.0 and bringing in best-of-breed trading systems",
             "Built custom CRM for FX Sales team, improving client engagement and relationship management",
             "Automated risk management and eliminated paper-based processes through digitization",
         ]),
    ]

    for i, (title, company, dates, ctx, bullets) in enumerate(exp_roles):
        label = "EXPERIENCE" if i == 0 else ""
        rc = role_cell(title, company, dates, context=ctx, bullets=bullets)
        rows.append((label, rc, False))

    # BMO Earlier Roles row
    c = CellContent()
    rs = len(c.text)
    c.add("Earlier Roles", font="Montserrat", size=10, bold=True, color=BLACK)
    c.add(" \u2014 BMO Capital Markets\n", font="Montserrat", size=10, color=DARK_GRAY)
    c.add("01/2008 \u2013 2014  |  Toronto\n", font="Montserrat", size=9, italic=True, color=MED_GRAY)
    c.add_spacing(rs, len(c.text), above_pt=2, below_pt=0)
    ds = len(c.text)
    c.add(
        "Java Developer (2008) \u2192 Team Lead (2010) \u2192 Software Development Manager (2012). "
        "Built FX trading and operations systems, leading increasingly larger teams through platform modernization. "
        "Developed deep domain expertise in FX trading workflows, operations, and settlement processes.",
        font="Calibri", size=9, color=DARK_GRAY,
    )
    c.add_spacing(ds, len(c.text), above_pt=0, below_pt=2)
    rows.append(("", c, True))

    # Row: EDUCATION
    c = CellContent()
    s1 = len(c.text)
    c.add("M.A.Sc., Electrical and Computer Engineering", font="Calibri", size=9, bold=True, color=DARK_GRAY)
    c.add(" \u2014 University of Toronto (2003 \u2013 2006)\n", font="Calibri", size=9, color=DARK_GRAY)
    c.add_spacing(s1, len(c.text), above_pt=2, below_pt=4)
    s2 = len(c.text)
    c.add("B.A.Sc., Electrical and Computer Engineering", font="Calibri", size=9, bold=True, color=DARK_GRAY)
    c.add(" \u2014 University of Toronto (1999 \u2013 2003)", font="Calibri", size=9, color=DARK_GRAY)
    c.add_spacing(s2, len(c.text), above_pt=2, below_pt=4)
    rows.append(("EDUCATION", c, True))

    # Row: CERTIFICATIONS
    c = CellContent()
    certs = [
        "Certified SAFe 4 Program Consultant \u2014 Scaled Agile",
        "Certified Scrum@Scale Practitioner \u2014 Scrum Inc.",
        "Convolutional Neural Networks in TensorFlow \u2014 Coursera",
        "Natural Language Processing in TensorFlow \u2014 Coursera",
    ]
    c.add(" | ".join(certs), font="Calibri", size=9, color=DARK_GRAY)
    c.add_spacing(0, len(c.text), above_pt=2, below_pt=2)
    rows.append(("CERTIFICATIONS", c, False))

    return rows


# --- Main ---

def create_resume():
    creds = get_credentials()
    docs_service = build("docs", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    # Phase 1: Create document
    doc = docs_service.documents().create(
        body={"title": "Fahad Qureshi - BMO Head of AI Resume"}
    ).execute()
    doc_id = doc["documentId"]
    print(f"Created: https://docs.google.com/document/d/{doc_id}/edit")

    # Phase 2: Margins + Header
    setup_requests = [
        {
            "updateDocumentStyle": {
                "documentStyle": {
                    "marginTop": {"magnitude": 36, "unit": "PT"},
                    "marginBottom": {"magnitude": 10, "unit": "PT"},
                    "marginLeft": {"magnitude": 32, "unit": "PT"},
                    "marginRight": {"magnitude": 45, "unit": "PT"},
                },
                "fields": "marginTop,marginBottom,marginLeft,marginRight",
            }
        },
        {
            "createHeader": {
                "type": "DEFAULT",
                "sectionBreakLocation": {"index": 0},
            }
        },
    ]
    response = docs_service.documents().batchUpdate(
        documentId=doc_id, body={"requests": setup_requests}
    ).execute()
    header_id = response["replies"][1]["createHeader"]["headerId"]

    # Phase 3: Header content
    name_text = "FAHAD QURESHI\n"
    contact_text = "Toronto  |  647-886-7147  |  fahadq@gmail.com  |  linkedin.com/in/qureshifahad\n"
    header_requests = [
        {"insertText": {"location": {"segmentId": header_id, "index": 0}, "text": name_text + contact_text}},
        {"updateTextStyle": {
            "range": {"segmentId": header_id, "startIndex": 0, "endIndex": len(name_text)},
            "textStyle": {
                "bold": True,
                "fontSize": {"magnitude": 20, "unit": "PT"},
                "weightedFontFamily": {"fontFamily": "Montserrat"},
                "foregroundColor": {"color": {"rgbColor": DARK_TEAL}},
            },
            "fields": "bold,fontSize,weightedFontFamily,foregroundColor",
        }},
        {"updateTextStyle": {
            "range": {"segmentId": header_id, "startIndex": len(name_text), "endIndex": len(name_text) + len(contact_text)},
            "textStyle": {
                "fontSize": {"magnitude": 9, "unit": "PT"},
                "weightedFontFamily": {"fontFamily": "Montserrat"},
                "foregroundColor": {"color": {"rgbColor": MED_GRAY}},
            },
            "fields": "fontSize,weightedFontFamily,foregroundColor",
        }},
        {"updateParagraphStyle": {
            "range": {"segmentId": header_id, "startIndex": 0, "endIndex": len(name_text) + len(contact_text)},
            "paragraphStyle": {
                "spaceBelow": {"magnitude": 2, "unit": "PT"},
                "spaceAbove": {"magnitude": 0, "unit": "PT"},
                "lineSpacing": 100,
            },
            "fields": "spaceBelow,spaceAbove,lineSpacing",
        }},
    ]
    docs_service.documents().batchUpdate(documentId=doc_id, body={"requests": header_requests}).execute()
    print("Header done")

    # Phase 4: Build row data and split into pages
    rows = build_rows()

    # --- PAGE BREAK CONTROL ---
    # Row indices: 0=Profile, 1=Competencies, 2=Prodago, 3=Manulife,
    #   4=Infaque, 5=RBC BA, 6=FICC, 7=RBC FX, 8=BMO Head, 9=BMO Earlier,
    #   10=Education, 11=Certifications
    PAGE_BREAK_AFTER = 4  # page break after Infaque (row 4)

    page1_rows = rows[:PAGE_BREAK_AFTER + 1]
    page2_rows = rows[PAGE_BREAK_AFTER + 1:]
    print(f"Page 1: {len(page1_rows)} rows, Page 2: {len(page2_rows)} rows")

    # Phase 5: Insert Table 1, page break, Table 2
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": [
            {"insertTable": {"rows": len(page1_rows), "columns": 2, "location": {"index": 1}}},
        ]},
    ).execute()

    doc = docs_service.documents().get(documentId=doc_id).execute()
    body_content = doc.get("body", {}).get("content", [])
    table1_end = None
    for el in body_content:
        if "table" in el:
            table1_end = el["endIndex"]
            break

    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": [
            {"insertText": {"location": {"index": table1_end}, "text": "\n"}},
            {"insertPageBreak": {"location": {"index": table1_end}}},
            {"updateParagraphStyle": {
                "range": {"startIndex": table1_end, "endIndex": table1_end + 2},
                "paragraphStyle": {
                    "spaceAbove": {"magnitude": 0, "unit": "PT"},
                    "spaceBelow": {"magnitude": 0, "unit": "PT"},
                    "lineSpacing": 100,
                },
                "fields": "spaceAbove,spaceBelow,lineSpacing",
            }},
            {"updateTextStyle": {
                "range": {"startIndex": table1_end, "endIndex": table1_end + 2},
                "textStyle": {"fontSize": {"magnitude": 1, "unit": "PT"}},
                "fields": "fontSize",
            }},
        ]},
    ).execute()

    doc = docs_service.documents().get(documentId=doc_id).execute()
    body_content = doc.get("body", {}).get("content", [])
    table2_insert_idx = None
    found_table = False
    for el in body_content:
        if "table" in el:
            found_table = True
            continue
        if found_table and "paragraph" in el:
            table2_insert_idx = el["endIndex"]
            break

    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": [
            {"insertTable": {"rows": len(page2_rows), "columns": 2, "location": {"index": table2_insert_idx}}},
        ]},
    ).execute()

    # Phase 6: Read doc for both tables' cell indices
    doc = docs_service.documents().get(documentId=doc_id).execute()
    t1_cells = get_table_cell_indices(doc, table_idx=0)
    t1_start = get_table_start_index(doc, table_idx=0)
    t2_cells = get_table_cell_indices(doc, table_idx=1)
    t2_start = get_table_start_index(doc, table_idx=1)

    # Phase 7: Insert content (reverse order)
    content_reqs = []

    for r in range(len(page2_rows) - 1, -1, -1):
        label, right_content, _ = page2_rows[r]
        content_reqs.extend(right_content.build_requests(t2_cells[r][1]))
        content_reqs.extend(left_cell(label).build_requests(t2_cells[r][0]))

    for r in range(len(page1_rows) - 1, -1, -1):
        label, right_content, _ = page1_rows[r]
        content_reqs.extend(right_content.build_requests(t1_cells[r][1]))
        content_reqs.extend(left_cell(label).build_requests(t1_cells[r][0]))

    print(f"Inserting content ({len(content_reqs)} requests)...")
    docs_service.documents().batchUpdate(documentId=doc_id, body={"requests": content_reqs}).execute()

    # Phase 8: Re-read doc for fresh table indices, then apply styling
    doc = docs_service.documents().get(documentId=doc_id).execute()
    t1_start = get_table_start_index(doc, table_idx=0)
    t2_start = get_table_start_index(doc, table_idx=1)

    zero_border = {
        "color": {"color": {"rgbColor": WHITE}},
        "width": {"magnitude": 0, "unit": "PT"},
        "dashStyle": "SOLID",
    }
    teal_border = {
        "color": {"color": {"rgbColor": TEAL}},
        "width": {"magnitude": 0.5, "unit": "PT"},
        "dashStyle": "SOLID",
    }

    def style_table(table_start, table_rows):
        reqs = []
        reqs.append({
            "updateTableColumnProperties": {
                "tableStartLocation": {"index": table_start},
                "columnIndices": [0],
                "tableColumnProperties": {
                    "widthType": "FIXED_WIDTH",
                    "width": {"magnitude": LEFT_COL_PT, "unit": "PT"},
                },
                "fields": "widthType,width",
            }
        })
        for r in range(len(table_rows)):
            _, _, has_divider = table_rows[r]
            for col in range(2):
                cs = {
                    "paddingTop": {"magnitude": 5, "unit": "PT"},
                    "paddingBottom": {"magnitude": 5, "unit": "PT"},
                    "paddingLeft": {"magnitude": 5, "unit": "PT"},
                    "paddingRight": {"magnitude": 5, "unit": "PT"},
                    "backgroundColor": {"color": {"rgbColor": WHITE}},
                    "borderTop": zero_border,
                    "borderBottom": teal_border if has_divider else zero_border,
                    "borderLeft": zero_border,
                    "borderRight": zero_border,
                }
                fields = "paddingTop,paddingBottom,paddingLeft,paddingRight,backgroundColor,borderTop,borderBottom,borderLeft,borderRight"
                if col == 0:
                    cs["contentAlignment"] = "TOP"
                    fields += ",contentAlignment"
                reqs.append({
                    "updateTableCellStyle": {
                        "tableRange": {
                            "tableCellLocation": {
                                "tableStartLocation": {"index": table_start},
                                "rowIndex": r,
                                "columnIndex": col,
                            },
                            "rowSpan": 1,
                            "columnSpan": 1,
                        },
                        "tableCellStyle": cs,
                        "fields": fields,
                    }
                })
        return reqs

    style_reqs = style_table(t1_start, page1_rows) + style_table(t2_start, page2_rows)
    print(f"Applying styles ({len(style_reqs)} requests)...")
    docs_service.documents().batchUpdate(documentId=doc_id, body={"requests": style_reqs}).execute()
    print("Styled")

    # Phase 9: Shrink trailing paragraph
    doc = docs_service.documents().get(documentId=doc_id).execute()
    body_content = doc.get("body", {}).get("content", [])
    last_el = body_content[-1]
    if "paragraph" in last_el:
        trail_start = last_el["startIndex"]
        trail_end = last_el["endIndex"]
        trail_reqs = [
            {"updateParagraphStyle": {
                "range": {"startIndex": trail_start, "endIndex": trail_end},
                "paragraphStyle": {
                    "spaceAbove": {"magnitude": 0, "unit": "PT"},
                    "spaceBelow": {"magnitude": 0, "unit": "PT"},
                    "lineSpacing": 100,
                },
                "fields": "spaceAbove,spaceBelow,lineSpacing",
            }},
        ]
        if trail_end - trail_start > 1:
            trail_reqs.append({
                "updateTextStyle": {
                    "range": {"startIndex": trail_start, "endIndex": trail_end - 1},
                    "textStyle": {"fontSize": {"magnitude": 1, "unit": "PT"}},
                    "fields": "fontSize",
                }
            })
        docs_service.documents().batchUpdate(documentId=doc_id, body={"requests": trail_reqs}).execute()
        print("Trailing paragraph minimized")

    # Phase 10: Export PDF
    pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Fahad Qureshi - BMO Head of AI Resume.pdf")
    pdf_content = drive_service.files().export_media(fileId=doc_id, mimeType="application/pdf").execute()
    with open(pdf_path, "wb") as f:
        f.write(pdf_content)

    print(f"\nDone!")
    print(f"Google Doc: https://docs.google.com/document/d/{doc_id}/edit")
    print(f"PDF: {pdf_path}")
    return doc_id


if __name__ == "__main__":
    create_resume()
