# Product Requirements Document (PRD)
## Product: Policy Gap Analyzer Lite

## 1. Objective

Build a web application that allows users to upload policy documents and automatically analyze them for:
- missing sections
- inconsistencies
- potential risks

The system will return clear, structured recommendations using an AI-powered policy analysis agent.

## 2. Target User

### Primary
- Consultants in governance, risk, and compliance
- Internal audit teams
- Small and medium businesses without full compliance teams

### Secondary
- Founders needing basic policy validation
- Operations managers handling internal documentation

## 3. Problem Statement

Organizations often:
- lack structured policy reviews
- miss critical compliance gaps
- rely on manual, time-consuming analysis

This leads to:
- regulatory risk
- inconsistent documentation
- operational inefficiencies

## 4. Solution Overview

A simple web app where users:
1. Upload policy documents in PDF format, with optional support for DOCX later.
2. The system extracts and processes the text.
3. An AI-powered policy analyzer agent evaluates the document against best practices or a reference document.
4. The app returns:
   - identified gaps
   - inconsistencies
   - risks
   - recommendations

## 5. Core Workflow

1. User uploads:
   - Document A: existing policy
   - Document B: optional reference policy or standard

2. System:
   - extracts text
   - chunks content into manageable sections
   - sends relevant content to the LLM-based policy analyzer

3. System returns a structured analysis report

## 6. MVP Features

| Feature | Description |
|---|---|
| File upload | Accept PDF first, optional DOCX later |
| Text extraction | Convert uploaded documents into raw text |
| Chunking | Split text into manageable sections for analysis |
| AI analysis | Analyze for gaps, inconsistencies, vague language, and risks |
| Output report | Return structured findings and recommendations |
| Basic UI | Clean purple and blue front-end with a polished feel |

## 7. Non-Goals

These are explicitly out of scope for the MVP:
- User accounts
- Database storage
- Real-time collaboration
- Framework-specific compliance mapping such as SOC 2 or ISO 27001
- Multi-document comparison beyond two files
- Report history or saved sessions

## 8. AI Agent Behavior

### Inputs
- Extracted text from uploaded document(s)

### Tasks
- Identify missing policy components
- Detect contradictions and inconsistencies
- Highlight vague, weak, or incomplete language
- Suggest practical improvements
- Summarize overall policy weaknesses

### Output Format

```text
Gaps:
- Missing data retention policy section
- No mention of access control procedures

Inconsistencies:
- Section 2 contradicts Section 5 on user permissions

Risks:
- Lack of audit logging creates compliance and accountability risk

Recommendations:
- Add a role-based access control section
- Define retention periods clearly
- Clarify approval and exception handling processes
```

## 9. UI Requirements

### Visual Style
- Clean and modern
- Purple and blue aesthetic
- Minimal, polished, and professional
- Smooth spacing, rounded cards, and clear sectioning

### Layout

#### Main Screen
- Title: Policy Gap Analyzer
- Short subtitle explaining what the app does
- Drag-and-drop upload area
- Upload field for:
  - Your Policy
  - Reference Policy (optional)
- Analyze button

#### Results Screen
Display analysis in clearly separated cards or panels:
- Gaps
- Inconsistencies
- Risks
- Recommendations

## 10. Technical Architecture (MVP)

| Layer | Tool |
|---|---|
| Frontend | Streamlit for speed, or React if more polished UI is prioritized |
| Backend | Python |
| File parsing | `pypdf` or `pdfplumber` |
| DOCX parsing | `python-docx` later if needed |
| AI model | OpenAI API |
| Chunking | Simple text splitting initially |
| Orchestration | A lightweight analyzer pipeline, agent-style if helpful |

## 11. Definition of Done

The MVP is considered complete when:
- A user can upload at least one PDF
- The system extracts readable text from the file
- The analyzer returns structured findings
- Results are displayed cleanly in the UI
- The full flow works end-to-end without manual intervention

## 12. Future Enhancements

Not part of today's build, but useful later:
- Compliance framework mapping
- Maturity scoring
- Exportable reports
- Multi-file and batch analysis
- User accounts and saved history
- Team dashboards
- Fine-tuned policy analysis prompts by domain

## 13. Product Constraints

- Prioritize end-to-end usability over perfect analysis quality
- Optimize for speed of shipping and demonstrability
- Keep the codebase simple and modular
- Build the MVP so it can later evolve into a more serious compliance tool

## 14. Definition of Success

Success for the MVP means:
- A user can upload a policy and get useful, readable feedback in under a few minutes
- The app feels polished enough to demo
- The architecture is simple enough to extend later
- The project helps the developer learn AI-assisted product building with Codex

## 15. Build Notes for Codex

When implementing this PRD:
- Start with the smallest end-to-end working version
- Prefer a clean modular structure over over-engineered abstractions
- Build the upload, extraction, analysis, and display pipeline first
- Use mock or simplified analysis if needed before improving prompt quality
- Focus on a working MVP before adding advanced compliance logic
