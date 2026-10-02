# Resume Project

## Context
This directory contains Fahad Qureshi's resume materials. The master profile at `fahad_qureshi_profile.md` is the single source of truth for all career history, achievements, tech stack, and professional details.

## Key Files
- `fahad_qureshi_profile.md` — Master profile with complete career history, competencies, tech stack, and achievements. Always read this before generating or tailoring any resume content.
- `create_gdoc_resume.py` — Google Docs API script that generates the formatted resume (see details below).

## Instructions
- When generating or tailoring resumes, always reference `fahad_qureshi_profile.md` for accurate details
- Do not fabricate achievements, metrics, or technologies not listed in the profile
- When tailoring for a specific job posting, prioritize relevant experience and keywords from the profile that match the role
- The `tailored-resume-generator` skill is available for generating job-specific resumes

## Google Docs Resume Generation (`create_gdoc_resume.py`)

### Design
- **Layout**: Two-column table — left column is a narrow sidebar with teal (#4A7C8F) section labels (Montserrat 9pt bold), right column has content (Calibri 9pt)
- **Header**: "FAHAD QURESHI" in Montserrat 20pt dark teal, contact line in Montserrat 9pt gray. Uses Google Docs header so it repeats on every page.
- **Typography**: Montserrat for name, section labels, role titles. Calibri for body text.
- **Colors**: White background, teal font for sidebar labels, dark gray for body text, medium gray for dates/context
- **Margins**: top=36pt, bottom=10pt, left=32pt, right=45pt. Sidebar column width=99pt.
- **Bullet points**: Use `•\t` (bullet + tab) with hanging indent (`indentStart=14pt`, `indentFirstLine=0pt`) so wrapped lines align with text, not the bullet

### Two-Table Page Break Approach
The resume uses **two separate tables** with an explicit page break paragraph between them to control pagination:
- **Table 1 (page 1)**: Profile, Competencies, AI Lead Consultant (DEMT), Prodago, Manulife — controlled by `PAGE_BREAK_AFTER = 4`
- **Page break paragraph**: Inserted between tables, styled at 1pt font with 0 spacing to be invisible
- **Table 2 (page 2)**: Infaque, RBC Business Agility, FICC, RBC FX, BMO Head, BMO Earlier, Education, Certifications
- **Trailing paragraph**: After table 2, Google Docs forces a trailing paragraph. Minimize it (0 spacing, 1pt font) to prevent a blank page 3.

**Row index map** (for PAGE_BREAK_AFTER tuning):
| Index | Section |
|-------|---------|
| 0 | Profile |
| 1 | Competencies |
| 2 | AI Lead Consultant (DEMT) |
| 3 | Prodago |
| 4 | Manulife / John Hancock |
| 5 | Infaque |
| 6 | RBC Business Agility |
| 7 | FICC Architect |
| 8 | RBC FX Tech |
| 9 | BMO Head of FX |
| 10 | BMO Earlier Roles |
| 11 | Education |
| 12 | Certifications |

### Page Break / Section Bleeding Rules — ALWAYS CHECK
After generating or modifying the resume, **always verify** that:
1. **No section bleeds across pages** — a role that starts on page 1 must not continue on page 2. Each role should be fully contained on one page.
2. **No blank trailing pages** — the trailing paragraph after the last table must not cause an extra empty page.
3. **Content fits exactly on 2 pages** — if content overflows, adjust by:
   - Trimming bullet text (shorter wording, fewer bullets)
   - Reducing cell padding (currently 3pt)
   - Reducing bottom margin (currently 6pt)
   - Moving the `PAGE_BREAK_AFTER` split point to rebalance pages
4. **If a section bleeds**: move the `PAGE_BREAK_AFTER` index so the split happens before the bleeding section. To fill remaining space on the earlier page, expand bullet text on prior sections.

### Gemini Screenshot Review — MANDATORY VERIFICATION STEP
After generating the PDF, **DO NOT declare success** until you complete this verification:

1. **Generate screenshots**: The script auto-generates PNG screenshots into `review_screenshots/` via `pdftoppm -png -r 150`
2. **Review with Gemini**: Read both `page-1.png` and `page-2.png` using Gemini's image analysis and check for:
   - **Spacing**: Are section labels aligned? Is spacing consistent between roles? Any awkward gaps?
   - **Page breaks**: Does any section start on one page and continue to the next? (Manual page break should be at the right spot)
   - **Page count**: Exactly 2 pages — no blank page 3 from a stray trailing paragraph
   - **Text overflow**: Any text running off the right margin or being clipped?
   - **Visual balance**: Are page 1 and page 2 roughly balanced in content density?
3. **Fix issues**: If Gemini flags any problems, adjust `PAGE_BREAK_AFTER`, padding, or content and re-generate
4. **Clean up**: Remove `review_screenshots/` directory when done

### Technical Notes
- Google Docs API requires **reverse-order insertion** within a batchUpdate to avoid index shifting
- Content insertion and table styling must be in **separate batchUpdate calls** — indices shift after content is inserted, so re-read the doc before styling
- `updateTableCellStyle` uses `tableRange` (not `tableStartLocation` at top level) — they are a oneof
- `tabStops` is NOT allowed in `updateParagraphStyle` — use `\t` character + `indentStart`/`indentFirstLine` instead
- The script requires Google OAuth credentials at `~/.claude/.google/client_secret.json` with Docs + Drive scopes
- PDF export uses Drive API `files().export_media()` with `application/pdf` mimeType
