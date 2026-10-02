#!/usr/bin/env python3
"""Head of Technology resume tailored for mid-sized credit unions.

Emphasizes: financial services leadership, regulatory compliance, cybersecurity,
core modernization, digital transformation, vendor & budget management, member
experience, and building/scaling high-performing technology teams.
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
        reqs.append({"insertText": {"location": {"index": cell_start_index}, "text": self.text}})
        for s, e, style, fields in self.styles:
            reqs.append({"updateTextStyle": {
                "range": {"startIndex": cell_start_index + s, "endIndex": cell_start_index + e},
                "textStyle": style, "fields": fields,
            }})
        for s, e, ps, fields in self.para_styles:
            reqs.append({"updateParagraphStyle": {
                "range": {"startIndex": cell_start_index + s, "endIndex": cell_start_index + e},
                "paragraphStyle": ps, "fields": fields,
            }})
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

    # PROFILE
    profile_text = (
        "Financial services technology leader with 18+ years building, modernizing, "
        "and securing platforms at Canada\u2019s largest banks (BMO, RBC) and delivering "
        "enterprise transformation at Manulife/John Hancock. Proven at setting technology "
        "strategy, running multi-million-dollar budgets ($22MM P&L), leading 60+ person "
        "teams, and partnering with boards and executives on risk, compliance, and digital "
        "member experience. Deep experience modernizing legacy core systems, hardening "
        "cybersecurity, managing vendors, and safely introducing AI to regulated environments."
    )
    c = CellContent()
    c.add(profile_text, font="Calibri", size=9, color=DARK_GRAY)
    c.add_spacing(0, len(c.text), above_pt=2, below_pt=2)
    rows.append(("PROFILE", c, True))

    # COMPETENCIES
    c = CellContent()
    cats = [
        ("Leadership", "Technology Strategy | Board & Exec Reporting | Team Building (60+) | Vendor & Partner Management | P&L up to $22MM"),
        ("Financial Services", "Core Banking Modernization | Capital Markets | Payments & Settlement (CLS) | Fraud Prevention | Regulatory Compliance & Audit Readiness"),
        ("Security & Risk", "Cybersecurity | Identity & Access (Entra ID, Key Vault) | Data Governance | Third-Party Risk | Business Continuity"),
        ("Platforms", "Multi-Cloud (Azure, AWS, GCP) | Cosmos DB, SQL Server | Node.js, Java, React | CI/CD & DevOps | Responsible AI / LLM Adoption"),
    ]
    for i, (label, desc) in enumerate(cats):
        start = len(c.text)
        c.add(f"{label}:  ", font="Calibri", size=9, bold=True, color=DARK_GRAY)
        c.add(desc, font="Calibri", size=9, color=DARK_GRAY)
        if i < len(cats) - 1:
            c.add("\n")
        c.add_spacing(start, len(c.text), above_pt=1, below_pt=1)
    rows.append(("COMPETENCIES", c, True))

    exp_roles = [
        ("CTO and Chief Product Owner", "Prodago",
         "07/2022 \u2013 Present  |  Montreal",
         "Data and AI governance SaaS serving regulated financial enterprises \u2014 built team and product from zero to $200K+ ARR.",
         [
             "Built engineering organization, delivery practices, and secure Azure platform from scratch; took product from $0 to $200K+ ARR serving regulated financial clients",
             "Operationalized data and AI governance frameworks for enterprise clients, translating regulatory policy into automated controls, monitoring, and audit-ready evidence",
             "Architected on Azure (Entra ID, Key Vault, Cosmos DB, Serverless, AI Foundry) with CI/CD and DevOps, reducing hosting and deployment costs by 50% while raising uptime",
             "Introduced responsible adoption of AI coding assistants (Claude Code, Cursor) under defined guardrails \u2014 improving requirements, test coverage, and throughput without compromising security",
             "Partnered with CEO/COO and client CROs/CFOs on roadmap, risk posture, and board-level storytelling",
         ]),
        ("Enterprise Consultant", "Manulife / John Hancock",
         "06/2021 \u2013 06/2025  |  Boston / Toronto",
         "Embedded multi-year engagement driving technology strategy, portfolio governance, and risk transformation across enterprise tech services.",
         [
             "Realigned cross-functional fraud prevention program at John Hancock, delivering $30M+ in annual savings and doubling investigative throughput",
             "Designed CapEx/OpEx reclassification model with real-time attribution; reclassified 17% of OpEx to CapEx and eliminated manual timesheet overhead",
             "Chaired governance forums and portfolio reviews; rolled out delivery dashboards and KPI tracking that doubled release velocity and tripled OKR attainment",
             "Oversaw delivery risk, benefits realization, and executive reporting across multi-million-dollar transformation portfolios",
         ]),
        ("Director & Head of Business Agility COE", "Royal Bank of Canada",
         "06/2018 \u2013 06/2021  |  Toronto",
         "Led enterprise-wide transformation at one of Canada\u2019s largest banks, spanning 4 divisions and 20% of executives.",
         [
             "Drove enterprise agility and digital delivery transformation across 4 divisions, enabling resilience and adaptability through the shift to remote operations",
             "Equipped 20% of RBC executives with prioritization and portfolio visualization practices within two years, aligning tech spend to business outcomes",
             "Implemented agile and OKR-led operating models, yielding 50%+ productivity gains in four key business units",
         ]),
        ("Director & Regional Head of FX Tech", "RBC Capital Markets",
         "10/2016 \u2013 06/2018  |  Toronto",
         "Full P&L ownership of FX technology function; also led FICC architecture and agile adoption.",
         [
             "Directed a $22MM budget with full P&L responsibility; delivered $5MM in vendor cost savings and $3MM in new recurring revenue through platform modernization",
             "Replaced legacy infrastructure with modern trading stack; doubled quarterly release cadence via CI/CD (Jenkins, Ansible, ELK) and OKR tracking",
             "Coached FICC IT leaders and lifted development efficiency 35% while reducing downtime and manual effort on 20 applications by 25%",
         ]),
        ("Head of FX Technology", "BMO Capital Markets",
         "01/2014 \u2013 02/2016  |  Toronto",
         "Culmination of 8-year BMO career \u2014 rose from Java Developer to department head of a 60+ person technology organization.",
         [
             "Led 60+ person technology team and managed $17MM annual budget across trading, operations, settlement, and sales technology",
             "Replaced IBUK, a 1970s-era core operations system, modernizing BMO\u2019s settlement stack and bringing the bank to full CLS (Continuous Linked Settlement) membership",
             "Modernized the full technology stack via Wall Street Systems 5.0 and best-of-breed vendor products; led vendor selection, negotiation, and implementation",
             "Built custom CRM for sales and automated risk and operations processes, reducing cost-to-serve and eliminating paper-based workflows",
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
    ds = len(c.text)
    c.add(
        "Java Developer (2008) \u2192 Team Lead (2010) \u2192 Software Development Manager (2012). "
        "Built and modernized core trading, operations, and settlement systems in a highly regulated banking environment.",
        font="Calibri", size=9, color=DARK_GRAY,
    )
    c.add_spacing(ds, len(c.text), above_pt=0, below_pt=2)
    rows.append(("", c, True))

    # Founder side entry (kept lean)
    c = CellContent()
    rs = len(c.text)
    c.add("Founder & CTO", font="Montserrat", size=10, bold=True, color=BLACK)
    c.add(" \u2014 Infaque\n", font="Montserrat", size=10, color=DARK_GRAY)
    c.add("01/2021 \u2013 Present  |  Toronto / Lahore\n", font="Montserrat", size=9, italic=True, color=MED_GRAY)
    c.add_spacing(rs, len(c.text), above_pt=2, below_pt=0)
    ds = len(c.text)
    c.add(
        "SaaS platform for the non-profit sector ($0 \u2192 $50K+ ARR, 20+ clients, $1.3M+ processed). "
        "Operates an offshore delivery arm enabling partners to reduce development costs by up to 70%.",
        font="Calibri", size=9, color=DARK_GRAY,
    )
    c.add_spacing(ds, len(c.text), above_pt=0, below_pt=2)
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
        body={"title": "Fahad Qureshi - Head of Technology (Credit Union) Resume"}
    ).execute()
    doc_id = doc["documentId"]
    print(f"Created: https://docs.google.com/document/d/{doc_id}/edit")

    setup_requests = [
        {"updateDocumentStyle": {
            "documentStyle": {
                "marginTop": {"magnitude": 36, "unit": "PT"},
                "marginBottom": {"magnitude": 10, "unit": "PT"},
                "marginLeft": {"magnitude": 32, "unit": "PT"},
                "marginRight": {"magnitude": 45, "unit": "PT"},
            },
            "fields": "marginTop,marginBottom,marginLeft,marginRight",
        }},
        {"createHeader": {"type": "DEFAULT", "sectionBreakLocation": {"index": 0}}},
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

    rows = build_rows()

    # Split: Profile, Competencies, Prodago, Manulife = page 1 (index 0-3)
    PAGE_BREAK_AFTER = 3
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
    t2_cells = get_table_cell_indices(doc, table_idx=1)

    content_reqs = []
    for r in range(len(page2_rows) - 1, -1, -1):
        label, right_content, _ = page2_rows[r]
        content_reqs.extend(right_content.build_requests(t2_cells[r][1]))
        content_reqs.extend(left_cell(label).build_requests(t2_cells[r][0]))
    for r in range(len(page1_rows) - 1, -1, -1):
        label, right_content, _ = page1_rows[r]
        content_reqs.extend(right_content.build_requests(t1_cells[r][1]))
        content_reqs.extend(left_cell(label).build_requests(t1_cells[r][0]))

    docs_service.documents().batchUpdate(documentId=doc_id, body={"requests": content_reqs}).execute()

    doc = docs_service.documents().get(documentId=doc_id).execute()
    t1_start = get_table_start_index(doc, table_idx=0)
    t2_start = get_table_start_index(doc, table_idx=1)

    zero_border = {"color": {"color": {"rgbColor": WHITE}}, "width": {"magnitude": 0, "unit": "PT"}, "dashStyle": "SOLID"}
    teal_border = {"color": {"color": {"rgbColor": TEAL}}, "width": {"magnitude": 0.5, "unit": "PT"}, "dashStyle": "SOLID"}

    def style_table(table_start, table_rows):
        reqs = [{
            "updateTableColumnProperties": {
                "tableStartLocation": {"index": table_start},
                "columnIndices": [0],
                "tableColumnProperties": {"widthType": "FIXED_WIDTH", "width": {"magnitude": LEFT_COL_PT, "unit": "PT"}},
                "fields": "widthType,width",
            }
        }]
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
                            "tableCellLocation": {"tableStartLocation": {"index": table_start}, "rowIndex": r, "columnIndex": col},
                            "rowSpan": 1, "columnSpan": 1,
                        },
                        "tableCellStyle": cs,
                        "fields": fields,
                    }
                })
        return reqs

    style_reqs = style_table(t1_start, page1_rows) + style_table(t2_start, page2_rows)
    docs_service.documents().batchUpdate(documentId=doc_id, body={"requests": style_reqs}).execute()

    doc = docs_service.documents().get(documentId=doc_id).execute()
    body_content = doc.get("body", {}).get("content", [])
    last_el = body_content[-1]
    if "paragraph" in last_el:
        trail_start = last_el["startIndex"]
        trail_end = last_el["endIndex"]
        trail_reqs = [{"updateParagraphStyle": {
            "range": {"startIndex": trail_start, "endIndex": trail_end},
            "paragraphStyle": {
                "spaceAbove": {"magnitude": 0, "unit": "PT"},
                "spaceBelow": {"magnitude": 0, "unit": "PT"},
                "lineSpacing": 100,
            },
            "fields": "spaceAbove,spaceBelow,lineSpacing",
        }}]
        if trail_end - trail_start > 1:
            trail_reqs.append({"updateTextStyle": {
                "range": {"startIndex": trail_start, "endIndex": trail_end - 1},
                "textStyle": {"fontSize": {"magnitude": 1, "unit": "PT"}},
                "fields": "fontSize",
            }})
        docs_service.documents().batchUpdate(documentId=doc_id, body={"requests": trail_reqs}).execute()

    pdf_path = os.path.join(os.path.dirname(__file__), "Fahad Qureshi - Head of Technology Credit Union Resume.pdf")
    pdf_content = drive_service.files().export_media(fileId=doc_id, mimeType="application/pdf").execute()
    with open(pdf_path, "wb") as f:
        f.write(pdf_content)

    print(f"\nDone!")
    print(f"Google Doc: https://docs.google.com/document/d/{doc_id}/edit")
    print(f"PDF: {pdf_path}")
    return doc_id


if __name__ == "__main__":
    create_resume()
