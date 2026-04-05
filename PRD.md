# Product Requirements Document
## Product: Policy Gap Analyzer vNext

## 1. Objective

Evolve the MVP into a more credible policy review tool that produces prioritized, evidence-backed findings and exportable reports while keeping the codebase simple, modular, and demo-friendly.

The next release should make the current analysis materially more actionable before expanding into broader document intake or batch workflows.

## 2. Current State

The current codebase already supports:
- one required primary policy PDF upload
- one optional reference policy PDF upload
- PDF text extraction with warnings for poor-quality input
- deterministic chunking with overlap
- staged LLM analysis using OpenAI
- a polished Streamlit results screen with summary, gaps, inconsistencies, risks, and recommendations
- baseline test coverage for extraction, chunking, and schema normalization

This means the next release does not need to rebuild the core analysis flow. It should upgrade the quality, structure, and usability of the report output.

## 3. Target User

### Primary
- Consultants in governance, risk, and compliance
- Internal audit teams
- Small and medium businesses without full compliance teams

### Secondary
- Founders needing basic policy validation
- Operations managers handling internal documentation

## 4. Problem Statement

The MVP proves that policy upload, extraction, and AI review work end-to-end, but the current report is still limited for practical decision-making:
- findings are plain text lists without severity
- results do not cite evidence from the source document
- the UI is readable but only lightly interactive
- users cannot export a clean report to PDF
- the app still handles only one primary policy and one optional reference at a time

As a result, the app is demoable, but it does not yet help users quickly prioritize what matters most or share the analysis in a polished deliverable.

## 5. Product Direction

The next product phase is intentionally phased.

### Phase 1: Rich Single-Report Upgrade

This is the committed implementation phase for the next iteration. It focuses on making one analysis run substantially more useful.

Phase 1 includes:
- 4-tier severity scoring for findings: `Critical`, `High`, `Medium`, `Low`
- evidence-backed findings with page, chunk, or source context
- an executive scorecard with top-level metrics and summary signals
- a more interactive results experience
- PDF export for polished report delivery

### Phase 2: Expanded Intake and Comparison

This is the next wave after the richer single-report experience is complete.

Phase 2 includes:
- multi-document analysis
- richer comparison workflows against one or more references
- DOCX support
- OCR or scanned-PDF support

Phase 2 is explicitly deferred until after Phase 1, because the app first needs a stronger finding model and reporting experience.

## 6. Core Workflow

### Phase 1 Workflow

1. User uploads one primary policy PDF and optionally one reference PDF.
2. System extracts and chunks the document content.
3. Analyzer produces structured findings with severity and supporting evidence.
4. UI presents:
   - executive summary
   - scorecard metrics
   - filterable findings
   - supporting evidence
   - recommendations
5. User exports the analysis as a PDF report if needed.

### Phase 2 Workflow Direction

1. User uploads multiple policy documents and optionally richer reference material.
2. System analyzes each document and comparison relationships between them.
3. User reviews batch or comparison output in a unified interface.

## 7. Planned Output Contract

The next release should move away from category-only string lists and toward a structured finding model.

### Finding Shape

Each finding should support:
- `category`
- `severity`
- `title`
- `description`
- `evidence`
- `recommendation`

### Severity Model

Severity must be categorical only:
- `Critical`
- `High`
- `Medium`
- `Low`

### Evidence Requirement

Evidence is required product behavior in Phase 1. Each finding should reference the source material clearly enough that a user can understand why the issue was raised. Evidence may include:
- page numbers
- chunk identifiers
- short supporting excerpts
- source label such as primary or reference policy

### Result Categories

The app should still organize findings under familiar categories:
- gaps
- inconsistencies
- risks
- recommendations

The difference is that these categories should now contain structured findings instead of plain text strings.

## 8. Phase 1 Feature Requirements

| Feature | Description |
|---|---|
| Severity scoring | Every meaningful finding is labeled `Critical`, `High`, `Medium`, or `Low` |
| Evidence-backed output | Findings include source context and supporting evidence |
| Executive scorecard | Results include summary metrics and top-priority takeaways |
| Interactive report UI | Users can filter, scan, and drill into findings more efficiently |
| PDF export | Users can generate a polished report from the analysis results |

## 9. UI Requirements

### Visual Direction
- Keep the existing purple and blue identity
- Preserve the clean Streamlit layout and readable hierarchy
- Increase interactivity without making the app feel crowded

### Phase 1 Results Experience

The upgraded results view should include:
- a clear executive summary
- scorecard metrics near the top of the page
- visible severity labels
- grouped findings by category
- filters or quick controls for severity and category
- expandable finding details with evidence and recommendation text
- a prominent export-to-PDF action

### Main Screen

The upload screen should remain simple:
- title and short subtitle
- primary policy upload
- optional reference upload
- analyze button

Phase 1 should avoid turning the upload workflow into a multi-file batch interface.

## 10. Technical Direction

| Layer | Direction |
|---|---|
| Frontend | Continue using Streamlit for the next release |
| Backend | Continue using Python |
| Parsing | Keep `pypdf` for current text-based PDF support |
| Analysis | Extend the current staged OpenAI pipeline rather than replacing it |
| Schemas | Introduce a richer structured finding contract |
| Export | Add a lightweight PDF generation path suitable for polished reports |

## 11. Out of Scope

The following remain out of scope for this release:
- user accounts
- database storage
- saved report history
- real-time collaboration
- framework-specific compliance mapping such as SOC 2 or ISO 27001
- team dashboards
- broad workflow automation beyond a single analysis run

The following are planned later but not part of Phase 1:
- multi-document analysis
- richer comparison workflows
- DOCX parsing
- OCR for scanned or image-based PDFs

## 12. Success Criteria

Phase 1 is successful when:
- users can immediately distinguish the most important issues by severity
- each major finding includes clear supporting evidence
- the report feels more interactive and easier to scan than the MVP
- users can export a polished PDF deliverable
- the architecture remains simple enough to support Phase 2 later

## 13. Definition of Done for Phase 1

Phase 1 is complete when all of the following are true:
- the analysis output uses structured findings rather than plain string-only lists
- severity is applied consistently using `Critical`, `High`, `Medium`, and `Low`
- evidence appears in the final report for meaningful findings
- the UI includes a scorecard and a more interactive results experience
- a user can export the final report to PDF from the app
- the end-to-end flow works with the current single primary plus optional reference upload pattern
- tests and error handling are updated to cover the richer reporting flow

## 14. Product Constraints

- Prioritize end-to-end usefulness over maximum analytical sophistication
- Keep the architecture modular and readable
- Avoid introducing new infrastructure unless it is required for the current phase
- Upgrade the current report quality before expanding the scope of document ingestion

## 15. Build Notes for Codex

When implementing this PRD:
- preserve the current modular boundaries across UI, services, parser, analyzer, and models
- treat the richer finding contract as the foundation for later UI and export work
- avoid designing batch or persistence abstractions before Phase 2
- optimize for a reliable, polished single-report workflow first

