# Policy Gap Analyzer Lite MVP Plan

## Goal

Build a clean, modular MVP that can be demoed quickly. The app should let a user upload a PDF policy, extract readable text, analyze it with an AI-powered pipeline, and display structured findings in a polished UI.

## Guiding Principles

- Ship the smallest end-to-end flow first.
- Keep the architecture modular, but avoid premature abstraction.
- Prefer reliable structured output over ambitious analysis depth.
- Optimize for demo readiness, not full compliance coverage.
- Make each milestone independently testable.

## Proposed MVP Scope

- One primary uploaded PDF is required.
- One optional reference PDF may be uploaded.
- Extraction supports text-based PDFs only for MVP.
- Analysis returns:
  - gaps
  - inconsistencies
  - risks
  - recommendations
- Results are displayed in a simple polished web UI.
- No accounts, persistence, history, or export in MVP.

## Milestone 0: Project Foundation

### Objective

Set up the project skeleton so implementation can proceed cleanly without rework.

### Steps

1. Create the application directory structure.
2. Add dependency management and environment configuration.
3. Define core data models for:
   - uploaded document
   - extracted document
   - analysis result
4. Create a configuration module for:
   - OpenAI API key
   - model name
   - upload limits
   - chunk size defaults
5. Add a README with local run instructions.

### Deliverables

- App folder structure exists.
- Dependencies are declared.
- Config loading is centralized.
- Core schemas/interfaces are defined before feature code is added.

### Definition of Done

- A developer can install dependencies and run the app shell locally.
- The codebase has a clear module layout for UI, services, and models.
- Configuration values are not hardcoded across the app.

## Milestone 1: File Upload Flow

### Objective

Enable users to upload a required policy PDF and an optional reference PDF from the UI.

### Steps

1. Build the main screen with:
   - title
   - short subtitle
   - primary file upload control
   - optional reference upload control
   - analyze button
2. Restrict uploads to PDF for MVP.
3. Add validation for:
   - missing primary file
   - unsupported file type
   - oversized files
4. Store uploaded files in session state during a run.
5. Add user-facing error messages and loading states.

### Deliverables

- Users can upload one or two PDFs.
- The analyze action is blocked until a valid primary file is present.
- Validation feedback appears in the UI.

### Definition of Done

- A user can open the app and upload a valid PDF without manual setup beyond environment configuration.
- Invalid upload cases are handled cleanly in the UI.
- The upload step is reliable enough for a live demo.

## Milestone 2: Text Extraction

### Objective

Convert uploaded PDFs into normalized text that is suitable for downstream analysis.

### Steps

1. Implement PDF parsing with `pypdf`.
2. Extract text page by page.
3. Normalize extracted text by:
   - collapsing repeated whitespace
   - preserving paragraph breaks where possible
   - removing obvious junk formatting
4. Capture extraction metadata:
   - filename
   - page count
   - extracted character count
   - warnings
5. Detect likely extraction failures:
   - empty output
   - near-empty output
   - unreadable or malformed PDF
6. Surface extraction warnings in the UI.

### Deliverables

- A service that converts uploaded PDFs into structured extracted-document objects.
- Basic failure and warning handling for poor-quality PDFs.

### Definition of Done

- A valid text-based PDF produces readable extracted text.
- Failed or low-quality extraction is reported clearly instead of silently continuing.
- Extraction results can be passed directly into the analysis pipeline.

## Milestone 3: Chunking and Preprocessing

### Objective

Prepare extracted text for efficient and predictable LLM analysis.

### Steps

1. Implement a chunking strategy using fixed-size chunks with overlap.
2. Prefer section-aware splitting when headings are easy to detect.
3. Keep chunking deterministic for repeatable outputs.
4. Add safeguards for:
   - very short documents
   - very long documents
   - duplicate or near-empty chunks
5. Produce a normalized chunk structure with:
   - chunk id
   - source document label
   - text content
   - optional location metadata

### Deliverables

- A reusable chunking service independent of the UI.
- Chunk output suitable for both single-document and comparison analysis.

### Definition of Done

- Extracted text is split into manageable chunks within model limits.
- Chunking is stable and testable.
- The output format is ready for direct use by the analyzer.

## Milestone 4: Analysis Pipeline

### Objective

Generate structured policy findings from the extracted and chunked content.

### Steps

1. Define a strict internal response schema:
   - summary
   - gaps
   - inconsistencies
   - risks
   - recommendations
2. Create prompt templates for:
   - single-policy review
   - optional reference-assisted review
3. Implement a lightweight LLM client wrapper.
4. Build a two-stage analysis flow:
   - stage 1: analyze chunks for localized findings
   - stage 2: consolidate findings into one final report
5. Add prompt rules to reduce noisy output:
   - do not claim legal certainty
   - avoid fabricated standards
   - prefer specific practical improvements
6. Validate and normalize model output before returning it to the UI.
7. Add fallback handling for malformed LLM responses.

### Deliverables

- A service that turns extracted documents into a structured final analysis result.
- Prompt templates and LLM access isolated from the rest of the app.

### Definition of Done

- A valid uploaded policy produces a structured report without manual intervention.
- The output consistently maps into the defined result schema.
- Optional reference-policy input changes the analysis behavior in a controlled way.

## Milestone 5: Results UI

### Objective

Display findings in a polished, easy-to-demo interface.

### Steps

1. Build a results layout with separate sections for:
   - summary
   - gaps
   - inconsistencies
   - risks
   - recommendations
2. Render each category in clear cards or panels.
3. Add empty states when a category has no findings.
4. Show analysis context:
   - uploaded file names
   - reference file presence
   - extraction warnings if any
5. Add visual polish:
   - purple/blue palette
   - rounded containers
   - clean spacing
   - readable hierarchy
6. Keep the page usable on common laptop screen sizes for demos.

### Deliverables

- A results screen that presents the report clearly and professionally.
- A UI theme that matches the PRD without adding frontend complexity.

### Definition of Done

- A user can understand the main findings without reading raw model output.
- Results are grouped cleanly by category.
- The UI is polished enough for a live demo.

## Milestone 6: End-to-End Hardening

### Objective

Make the MVP reliable enough to demo without manual recovery steps.

### Steps

1. Test the full flow with:
   - one valid policy PDF (refer to samples/policies)
   - policy plus reference PDF (refer to samples/references)
   - invalid file upload
   - extraction failure case
2. Add logging around:
   - upload
   - extraction
   - chunking
   - LLM analysis
3. Improve user-facing errors for:
   - missing API key
   - extraction failure
   - model/API failure
   - invalid structured response
4. Add basic unit tests for:
   - extraction normalization
   - chunking behavior
   - result schema handling
5. Verify startup and run instructions from a clean environment.

### Deliverables

- Baseline tests for core non-UI logic.
- Stable error handling for the most likely demo failures.
- A documented local run flow.

### Definition of Done

- The full MVP works end-to-end without manual patching during a demo.
- Common failure states are understandable and recoverable.
- Core pipeline logic has at least minimal automated test coverage.

## Recommended Build Order

1. Milestone 0: Project Foundation
2. Milestone 1: File Upload Flow
3. Milestone 2: Text Extraction
4. Milestone 3: Chunking and Preprocessing
5. Milestone 4: Analysis Pipeline
6. Milestone 5: Results UI
7. Milestone 6: End-to-End Hardening

## Demo Readiness Check

The MVP is demo-ready when all of the following are true:

- A user can upload a policy PDF from the UI.
- The app extracts readable text without manual intervention.
- The system returns structured findings in under a few minutes.
- The UI displays findings clearly across all required categories.
- Failure states do not break the session or require code changes during a demo.

## Out of Scope for This Plan

- User accounts
- Saved reports or persistent storage
- Export to PDF or DOCX
- Compliance framework mapping
- OCR for scanned PDFs
- Batch processing
- Collaboration features
