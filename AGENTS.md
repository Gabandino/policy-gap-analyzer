# AGENTS.md

## Purpose

This project is a simple, modular web-app for a Policy Gap Analyzer.  
Focus on clean, readable, and minimal code that supports fast iteration.

---

## Current Product Phase

The MVP is complete. The project is now in the vNext Phase 1 upgrade cycle.

Current Phase 1 priorities:
- richer structured findings
- severity scoring using `Critical`, `High`, `Medium`, and `Low`
- evidence-backed analysis output
- a more interactive results experience
- PDF export

Not part of the active phase unless the current milestone explicitly calls for it:
- multi-document analysis
- DOCX support
- OCR or scanned-PDF support

---

## Core Principles

- Always prioritize a working end-to-end flow over perfection
- Keep the architecture simple and modular
- Avoid over-engineering or premature abstraction
- Each module should have a clear, single responsibility

---

## Project Structure Rules

- `app/main.py` is the Streamlit entrypoint
- `app/ui/` contains Streamlit views, display logic, session state helpers, and theme code
- `app/services/` contains business logic such as extraction orchestration and chunking
- `app/parsers/` handles PDF/text extraction
- `app/analyzer/` handles LLM prompts, schemas, client wrapper, and analysis pipeline
- `app/models/` defines application data schemas
- `app/config.py` handles environment and settings

Do not mix responsibilities across modules.

Additional structure guidance:
- keep UI concerns in `app/ui/`, not in analyzer or service modules
- keep parsing concerns in `app/parsers/`, not in UI code
- keep LLM-specific logic inside `app/analyzer/`
- keep shared data contracts in `app/models/`

---

## Coding Guidelines

- Prefer small, readable functions
- Avoid deeply nested logic
- Use clear variable and function names
- Add comments only when logic is not obvious

---

## Dependencies

- Only add dependencies when necessary
- Prefer lightweight libraries
- Avoid duplicate or overlapping packages

---

## AI Integration Rules

- All LLM calls must go through a single wrapper module
- Prompts should be stored in a dedicated file
- Output must follow a strict structured schema
- When extending the report, prefer richer finding objects over adding more plain-text lists
- Evidence and severity are first-class parts of the planned output contract for vNext

---

## UI Guidelines

- Use a clean, minimal Streamlit interface
- Maintain a consistent purple/blue theme
- Keep layout simple and readable
- Prefer stronger scanability over decorative complexity
- New UI work should improve prioritization and drill-down, not just styling

---

## Development Approach

- Build in small, testable steps
- Do not implement multiple milestones at once
- After each milestone, ensure the app runs end-to-end
- Phase 1 work should strengthen the single-report workflow before expanding input scope

---

## What to Avoid

- Do not introduce databases
- Do not add authentication
- Do not implement advanced compliance frameworks yet
- Do not refactor large parts of the code unless necessary
- Do not introduce batch or multi-document abstractions before the richer single-report model is in place
- Do not add DOCX or OCR support unless the current milestone explicitly requires it

---

## Important Considerations

- Keep future scalability in mind, but do not introduce abstractions unless they are required by the current milestone.
- Prefer simple implementations that can be extended later over complex designs that anticipate future needs.
- Avoid major refactoring by keeping responsibilities clearly separated from the start.

---

## Decision Rule

When in doubt:
- Choose the simplest implementation that satisfies the current milestone
- Do not generalize unless a second use case already exists
