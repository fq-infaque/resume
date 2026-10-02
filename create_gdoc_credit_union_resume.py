#!/usr/bin/env python3
"""Head of Technology resume tailored for a credit union role.

Two-column sidebar layout. Target: exactly 2 pages.
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
TEAL = {"red": 74 / 255, "green": 124 / 255, "blue": 143 / 255}
DARK_TEAL = {"red": 55 / 255, "green": 97 / 255, "blue": 112 / 255}
WHITE = {"red": 1.0, "green": 1.0, "blue": 1.0}
DARK_GRAY = {"red": 0.2, "green": 0.2, "blue": 0.2}
MED_GRAY = {"red": 0.4, "green": 0.4, "blue": 0.4}
BLACK = {"red": 0.0, "green": 0.0, "blue": 0.0}

LEFT_COL_PT = 99


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


def build_rows():
    rows = []

    # Row 0: PROFILE
    profile_text = (
        "Technology executive with 18+ years leading enterprise technology strategy, "
        "governance, and modernization across regulated financial institutions — including "
        "BMO Capital Markets, Royal Bank of Canada, and Manulife. Proven track record managing "
        "budgets up to $22MM, leading teams of 60+, and delivering measurable outcomes: $30M+ "
        "in cost savings, 50%+ productivity gains, and 2\u00d7 release velocity. "
        "Deep expertise in cybersecurity, compliance, cloud infrastructure, and AI-enabled "
        "modernization, with a strong focus on aligning technology investment with member and business value."
    )
    c = CellContent()
    c.add(profile_text, font="Calibri", size=9, color=DARK_GRAY)
    c.add_spacing(0, len(c.text), above_pt=2, below_pt=2)
    rows.append(("PROFILE", c, True))

    # Row 1: COMPETENCIES
    c = CellContent()
    cats = [
        ("Leadership", "Technology strategy & governance \u00b7 P&L ownership (budgets to $22MM) \u00b7 Team management (60+) \u00b7 Vendor management & cost optimization \u00b7 Regulatory compliance"),
        ("AI & Architecture", "Azure AI Foundry \u00b7 Logic Apps agent workflows \u00b7 Power BI AI integration \u00b7 LLMs & LangChain \u00b7 Claude Code (AI-first development) \u00b7 Multi-cloud (Azure, AWS, GCP) \u00b7 Node.js, React, Java \u00b7 Cosmos DB, SQL Server"),
        ("AI Governance", "Built enterprise AI governance platform incorporating ISO 42001, NIST AI RMF, and EU AI Act \u00b7 Policy operationalization for regulated industries \u00b7 AI risk management frameworks \u00b7 Responsible AI adoption"),
        ("Delivery", "Agile at scale (SAFe, Scrum@Scale) \u00b7 OKR frameworks \u00b7 Portfolio governance & PMO \u00b7 Digital modernization \u00b7 Offshore team scaling \u00b7 CI/CD & DevOps"),
        ("Domain", "Banking & capital markets (BMO, RBC) \u00b7 Insurance enterprise (Manulife) \u00b7 CapEx/OpEx optimization \u00b7 Regulatory readiness \u00b7 AI/LLM governance"),
    ]
    for i, (label, desc) in enumerate(cats):
        start = len(c.text)
        c.add(f"{label}:  ", font="Calibri", size=9, bold=True, color=DARK_GRAY)
        c.add(desc, font="Calibri", size=9, color=DARK_GRAY)
        if i < len(cats) - 1:
            c.add("\n")
        c.add_spacing(start, len(c.text), above_pt=1, below_pt=1)
    rows.append(("COMPETENCIES", c, True))

    # EXPERIENCE rows
    exp_roles = [
        ("CTO & Chief Product Owner", "Prodago",
         "07/2022 \u2013 Present  |  Montreal",
         None,
         [
             "Built and launched an AI/LLM governance platform from $0 to $200K+ ARR, operationalizing regulatory compliance frameworks for enterprise clients",
             "Implemented Azure AI Foundry and Logic Apps to build agentic workflows and pipelines; integrated with Power BI for AI-powered governance reporting and analytics",
             "Pioneered AI-first development using Claude Code across the entire engineering team \u2014 standardizing AI-assisted requirements, design, and coding, resulting in a step-change increase in team productivity",
             "Reduced Azure infrastructure costs by 50% through serverless architecture; established offshore development team reducing monthly spend by 50%",
         ]),
        ("Enterprise Consultant", "Manulife / John Hancock",
         "06/2021 \u2013 06/2025  |  Boston / Toronto",
         None,
         [
             "Realigned cross-functional fraud prevention program at John Hancock, delivering $30M+ in annual savings and doubling throughput",
             "Designed CapEx/OpEx reclassification model using real-time attribution, reclassifying 17% of OpEx to CapEx and eliminating manual timesheets",
             "Achieved 28% ROI improvement and 3\u00d7 OKR attainment; introduced delivery dashboards and agile practices that doubled release velocity",
             "Chaired governance and strategy sessions; led KPI-driven portfolio reviews across $MM technology transformation portfolios",
         ]),
        ("Director & Head of Business Agility COE", "Royal Bank of Canada",
         "06/2018 \u2013 06/2021  |  Toronto",
         None,
         [
             "Built and scaled the Business Agility Centre of Excellence from the ground up, establishing coaching programs, governance frameworks, and tooling adopted across the enterprise",
             "Led enterprise-wide agility transformation across 4 divisions, driving 50%+ productivity gains in four key business units and enabling faster response to regulatory and market changes",
             "Facilitated adoption of prioritization and work visualization practices among 20% of RBC executives within two years, improving strategic alignment and decision-making",
             "Aligned technology delivery to business outcomes via OKR-led operating committees; reduced delivery risk and improved transparency across major programs",
         ]),
        ("FICC Architect & Agile Adoption", "RBC Capital Markets",
         "06/2017 \u2013 06/2018  |  Toronto",
         None,
         [
             "Led the DevOps transformation for Fixed Income, Currencies & Commodities technology, integrating Jira, Jenkins, Ansible, ELK stack, and automated testing tools end-to-end",
             "Increased development efficiency by 35% and reduced downtime and manual effort across 20 applications by 25%, accelerating time-to-market",
             "Coached and mentored Fixed Income IT leadership on Agile practices, embedding a continuous improvement culture across the division",
         ]),
        ("Director & Regional Head of FX Technology", "RBC Capital Markets",
         "10/2016 \u2013 06/2017  |  Toronto",
         None,
         [
             "Joined RBC from BMO as Regional Head of FX Technology with full P&L ownership of a $22MM budget; achieved $5MM in vendor cost savings through strategic renegotiation",
             "Generated $3MM in additional recurring revenue by increasing deal flow in EM FX forwards through targeted technology improvements",
             "Replaced aging legacy infrastructure with a modern, scalable stack; doubled quarterly release cadence through Agile adoption and OKR-driven delivery",
         ]),
        ("Head of FX Technology", "BMO Capital Markets",
         "01/2014 \u2013 02/2016  |  Toronto",
         None,
         [
             "Oversaw 60+ IT professionals and $17MM annual budget across FX trading, operations, and sales technology",
             "Led the end-to-end replacement of IBUK, BMO\u2019s 1970s-era core FX operations system, delivering full CLS (Continuous Linked Settlement) membership and eliminating significant operational risk",
             "Implemented Wall Street Systems 5.0 as the modern FX trading platform, replacing multiple legacy systems and establishing a unified, scalable stack",
             "Built a custom CRM for the FX Sales team, improving client relationship management and deal tracking; eliminated paper-based workflows through digitization and automation",
             "Decreased FX operations costs, amplified recurring revenue, and automated risk management processes through disciplined technology and process transformation",
         ]),
    ]

    for i, (title, company, dates, ctx, bullets) in enumerate(exp_roles):
        label = "EXPERIENCE" if i == 0 else ""
        rc = role_cell(title, company, dates, context=ctx, bullets=bullets)
        rows.append((label, rc, False))

    # BMO Earlier Roles
    c = CellContent()
    rs = len(c.text)
    c.add("Earlier Roles", font="Montserrat", size=10, bold=True, color=BLACK)
    c.add(" \u2014 BMO Capital Markets\n", font="Montserrat", size=10, color=DARK_GRAY)
    c.add("01/2008 \u2013 2014  |  Toronto\n", font="Montserrat", size=9, italic=True, color=MED_GRAY)
    c.add_spacing(rs, len(c.text), above_pt=2, below_pt=0)
    bullets_earlier = [
        "Software Development Manager (2012\u20132014): Managed FX development teams delivering key platform modernization programs including Wall Street Systems 5.0 and the IBUK replacement initiative",
        "Team Lead (2010\u20132012): Led FX trading and operations development team; established engineering practices and mentored junior developers in a Java-based capital markets environment",
        "Java Developer (2008\u20132010): Built deep domain expertise in FX trading workflows, settlement processes, and operations systems as an individual contributor on BMO\u2019s core FX platform",
    ]
    for bullet in bullets_earlier:
        b_start = len(c.text)
        c.add(f"\u2022\t{bullet}\n", font="Calibri", size=9, color=DARK_GRAY)
        c.add_spacing(b_start, len(c.text), above_pt=0, below_pt=2)
        c.add_hanging_indent(b_start, len(c.text))
    rows.append(("", c, True))

    # EDUCATION
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

    # CERTIFICATIONS
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


def create_resume():
    creds = get_credentials()
    docs_service = build("docs", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    doc = docs_service.documents().create(
        body={"title": "Fahad Qureshi - Head of Technology (Credit Union)"}
    ).execute()
    doc_id = doc["documentId"]
    print(f"Created: https://docs.google.com/document/d/{doc_id}/edit")

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

    rows = build_rows()

    # Row indices:
    # 0=Profile, 1=Competencies, 2=Prodago, 3=Manulife,
    # 4=RBC BA COE, 5=FICC Architect, 6=RBC FX Director, 7=BMO Head, 8=BMO Earlier, 9=Education, 10=Certifications
    PAGE_BREAK_AFTER = 3  # page break after Manulife

    page1_rows = rows[:PAGE_BREAK_AFTER + 1]
    page2_rows = rows[PAGE_BREAK_AFTER + 1:]
    print(f"Page 1: {len(page1_rows)} rows, Page 2: {len(page2_rows)} rows")

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

    doc = docs_service.documents().get(documentId=doc_id).execute()
    t1_cells = get_table_cell_indices(doc, table_idx=0)
    t1_start = get_table_start_index(doc, table_idx=0)
    t2_cells = get_table_cell_indices(doc, table_idx=1)
    t2_start = get_table_start_index(doc, table_idx=1)

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

    pdf_path = os.path.join(os.path.dirname(__file__), "Fahad Qureshi - Head of Technology (Credit Union).pdf")
    pdf_content = drive_service.files().export_media(fileId=doc_id, mimeType="application/pdf").execute()
    with open(pdf_path, "wb") as f:
        f.write(pdf_content)

    print(f"\nDone!")
    print(f"Google Doc: https://docs.google.com/document/d/{doc_id}/edit")
    print(f"PDF: {pdf_path}")
    return doc_id


if __name__ == "__main__":
    create_resume()
