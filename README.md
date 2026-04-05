# Policy Gap Analyzer Lite

Policy Gap Analyzer Lite is a Streamlit MVP for uploading policy PDFs and preparing them for structured analysis. The current implementation covers Milestones 0 through 6: project structure, centralized configuration, core schemas, validated upload inputs, PDF text extraction, chunking, staged LLM analysis, a polished results screen, and baseline hardening for demos.

## Project Status

The MVP is complete and the next iteration is now planned as a phased vNext upgrade.

- Product direction: `PRD.md`
- Implementation plan: `PLANS.md`
- Upgrade summary: `docs/UPGRADE_BRIEF.md`
- Archived MVP plan: `docs/archive/PLANS_MVP.md`
- Archived MVP PRD: `docs/archive/PRD_MVP.md`

## Recent vNext Changes

The latest Phase 1 implementation delivered a richer single-report workflow:
- Findings now use a structured object (`category`, `severity`, `title`, `description`, `evidence`, `recommendation`) with normalization and schema validation.
- Analyzer prompts/schemas now require evidence-backed findings with severity levels (`Critical`, `High`, `Medium`, `Low`).
- Results include an executive scorecard, severity/category filters, drill-down finding cards, and PDF export from the report view.
- Shared reporting/export services and unit tests were added to support this flow.

## Current Scope

- Streamlit app shell
- Purple/blue polished landing page
- Required PDF upload for **Your Policy**
- Optional PDF upload for **Reference Policy**
- Analyze button with validation
- Page-by-page PDF text extraction with `pypdf`
- Whitespace normalization for extracted text
- Extraction metadata and warnings in the UI
- Deterministic chunking with overlap
- Section-aware chunk splitting when simple headings are detected
- Chunk previews with page metadata in the UI
- Two-stage LLM analysis using OpenAI
- Structured output with summary, gaps, inconsistencies, risks, and recommendations
- Results screen with separated summary and findings cards
- Analysis context, warning visibility, and empty states in the report view
- Logging across upload, extraction, chunking, and analysis stages
- Baseline unit tests for extraction normalization, chunking, and schema handling
- Centralized environment-based config
- Core models for uploaded documents and analysis results

## Not Implemented Yet

- Multi-document analysis workflows
- DOCX support
- OCR/scanned-PDF extraction support
- Additional hardening beyond the current baseline

## Project Structure

```text
app/
  config.py
  main.py
  models/
    analysis.py
    documents.py
  analyzer/
    client.py
    pipeline.py
    prompts.py
    schemas.py
  parsers/
    pdf.py
  services/
    chunking.py
    extraction.py
  ui/
    results_view.py
    state.py
    theme.py
    upload_view.py
tests/
  test_analysis_models.py
  test_chunking.py
  test_extraction.py
requirements.txt
README.md
PRD.md
PLANS.md
```

## Requirements

- Python 3.11 or newer recommended

## Local Setup

1. Create and activate a virtual environment.

```powershell
python -m venv .venv
```

If PowerShell blocks activation on your machine, skip activation and call the venv directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app/main.py
```

If activation is allowed, you can still use:

```powershell
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
python -m pip install -r requirements.txt
```

3. Set environment variables if you want to override defaults.

```powershell
$env:OPENAI_API_KEY="your-key-here"
$env:OPENAI_MODEL="gpt-4.1-mini"
$env:MAX_UPLOAD_SIZE_MB="15"
$env:LOG_LEVEL="INFO"
```

`OPENAI_API_KEY` is required for the current analysis milestone.

## Run the App

```powershell
.\.venv\Scripts\python.exe -m streamlit run app/main.py
```

Then open the local URL shown in the terminal, typically:

- [http://localhost:8501](http://localhost:8501)

## Run Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

## Demo Samples

Use the included sample files for smoke testing:

- `samples/policies/`
- `samples/references/`

## Validation Behavior

- **Your Policy** is required.
- **Reference Policy** is optional.
- Only PDF uploads are accepted.
- Oversized files are rejected based on `MAX_UPLOAD_SIZE_MB`.
- Empty, near-empty, and unreadable extraction results are surfaced before analysis.
- Extracted text is split into overlapping analysis-ready chunks before analysis is added.
- The analysis step requires a valid `OPENAI_API_KEY`.
- Logging verbosity can be adjusted with `LOG_LEVEL`.

## Roadmap Note

The MVP milestones are complete. The next planned phase focuses on richer structured findings, severity scoring, evidence-backed output, interactive report UX, and PDF export before expanding into multi-document analysis, DOCX, or OCR support.

