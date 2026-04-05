# Policy Gap Analyzer vNext Plan

## Goal

Upgrade the MVP into a richer single-report experience before expanding input scope. The next implementation cycle should prioritize structured findings, severity scoring, evidence visibility, better report UX, and PDF export.

## Guiding Principles

- Build on the working MVP rather than replacing it.
- Upgrade report usefulness before adding more document ingestion paths.
- Keep modules simple and responsibilities clear.
- Make each milestone independently testable and demoable.
- Defer batch and OCR complexity until the richer single-analysis contract is stable.

## Phase Strategy

### Phase 1: Rich Single-Report Upgrade

This is the active implementation phase.

Phase 1 focuses on:
- structured findings instead of plain text lists
- severity scoring with `Critical`, `High`, `Medium`, and `Low`
- evidence-backed analysis output
- executive scorecard and improved scanability
- filterable and drill-down results UI
- PDF export

### Phase 2: Expanded Intake and Comparison

This phase is intentionally deferred until after Phase 1.

Phase 2 will explore:
- multi-document analysis
- richer reference comparison flows
- DOCX support
- OCR or scanned-PDF support

## Milestone 1: Rich Finding Schema and Severity Model

### Objective

Create the richer result contract needed for every downstream upgrade.

### Scope

1. Replace string-only category lists with a structured finding model.
2. Define consistent category and severity fields.
3. Add support for evidence and recommendation text within each finding.
4. Preserve compatibility with the current single primary plus optional reference workflow.

### Deliverables

- A planned `Finding`-style model documented and ready for implementation.
- A documented severity model with `Critical`, `High`, `Medium`, and `Low`.
- Updated report contract expectations across PRD, plan, and brief.

### Acceptance Criteria

- The planned output contract is clear enough to implement without inventing new fields later.
- Severity is categorical only and consistent across all docs.
- Evidence is treated as a first-class requirement, not an optional enhancement.

### Out of Scope

- Multi-document inputs
- OCR
- DOCX support
- PDF generation implementation details

## Milestone 2: Analyzer Prompt and Schema Upgrade

### Objective

Update the staged analysis pipeline to produce richer structured findings plus evidence.

### Scope

1. Separate chunk-level and final-report output expectations where needed.
2. Extend prompts to request evidence-backed findings with severity.
3. Keep the current staged analysis approach and OpenAI wrapper.
4. Normalize and validate the richer structured output before it reaches the UI.

### Deliverables

- A richer analyzer schema definition for chunk and final outputs.
- Prompt guidance for severity, evidence, and deduplicated findings.
- Updated model-normalization behavior expectations.

### Acceptance Criteria

- The analyzer contract supports severity, evidence, description, and recommendation fields.
- Final results remain structured and deterministic enough for UI and export use.
- The optional reference document still acts as supporting comparison context.

### Out of Scope

- Batch analysis across many documents
- New model providers
- Framework-specific compliance mapping

## Milestone 3: Results UI Upgrade

### Objective

Turn the current polished but static report into a more interactive and prioritizable results experience.

### Scope

1. Add an executive scorecard near the top of the report.
2. Surface severity clearly in the interface.
3. Add filter or quick-view controls for category and severity.
4. Add drill-down or expandable finding details showing evidence and recommendations.
5. Preserve the current clean purple/blue identity.

### Deliverables

- A scorecard-driven report layout.
- Category and severity scanning improvements.
- Finding detail views with evidence context.

### Acceptance Criteria

- A user can quickly identify the highest-priority issues.
- Evidence is visible in the report without forcing users into raw chunk previews.
- The page remains readable on common laptop screens.

### Out of Scope

- Redesigning the upload flow into a multi-file workspace
- Persistent report history
- Team dashboards

## Milestone 4: PDF Export Flow

### Objective

Allow users to generate a polished report artifact from the richer analysis output.

### Scope

1. Define a lightweight export path suitable for Streamlit and Python.
2. Export the executive summary, scorecard, findings, evidence, and recommendations.
3. Ensure the exported document is suitable for sharing outside the app.

### Deliverables

- A documented PDF export capability in the product plan.
- Clear export contents and formatting expectations.

### Acceptance Criteria

- The exported PDF reflects the same prioritized findings shown in the UI.
- The export includes severity and evidence context.
- The flow works without adding persistence or user accounts.

### Out of Scope

- DOCX export
- Saved export history
- Custom report branding systems

## Milestone 5: Testing and End-to-End Hardening

### Objective

Make the richer reporting flow reliable enough for demos and iterative product work.

### Scope

1. Expand tests beyond current extraction, chunking, and normalization coverage.
2. Add analyzer-contract tests for richer structured findings.
3. Add end-to-end smoke coverage for the upgraded single-report flow.
4. Improve recovery paths for malformed model output and export failures.
5. Refresh run and usage documentation as needed.

### Deliverables

- Broader automated coverage for the richer analysis contract.
- Stronger failure handling expectations for UI, analyzer, and export paths.
- Updated developer-facing documentation where the workflow changed.

### Acceptance Criteria

- The richer output contract is covered by tests.
- A valid single-policy analysis plus export flow can be exercised end-to-end.
- Common failure states remain understandable and recoverable.

### Out of Scope

- Performance optimization for large-scale batch processing
- Persistence-backed job tracking
- Background worker infrastructure

## Milestone 6: Future Phase Placeholders

### Objective

Capture the next logical expansion areas without pulling them into the active build.

### Scope

1. Reserve a future path for multi-document intake.
2. Reserve a future path for richer reference comparison workflows.
3. Reserve a future path for DOCX parsing.
4. Reserve a future path for OCR and scanned-PDF handling.

### Deliverables

- A clearly deferred Phase 2 backlog in the plan.
- Scope boundaries that prevent early over-engineering.

### Acceptance Criteria

- Multi-document support is explicitly deferred until after the richer single-report workflow is complete.
- Future enhancements are described at a high level without forcing early schema or architecture decisions.

### Out of Scope

- Implementing batch workflows now
- Designing persistence or queueing systems
- Building OCR pipelines in this phase

## Recommended Build Order

1. Milestone 1: Rich Finding Schema and Severity Model
2. Milestone 2: Analyzer Prompt and Schema Upgrade
3. Milestone 3: Results UI Upgrade
4. Milestone 4: PDF Export Flow
5. Milestone 5: Testing and End-to-End Hardening
6. Milestone 6: Future Phase Placeholders

## Release Check for Phase 1

Phase 1 is ready when all of the following are true:

- Structured findings replace plain string-only categories in the planned output.
- Severity is visible and consistent across the report experience.
- Evidence is included for meaningful findings.
- The UI is more interactive and prioritization-friendly than the MVP.
- A user can export the report to PDF.
- The workflow still runs cleanly with one primary PDF and one optional reference PDF.

## Out of Scope for This Plan

- User accounts
- Database storage
- Saved report history
- Real-time collaboration
- Framework-specific compliance mapping
- Team dashboards
- Batch analysis implementation in Phase 1

