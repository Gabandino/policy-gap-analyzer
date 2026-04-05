# Policy Gap Analyzer Upgrade Brief

## Purpose

This brief captures the recommended post-MVP upgrade direction based on the current codebase audit. It is intentionally shorter than the PRD and is meant to explain what should happen next and why.

## MVP Capabilities Confirmed in the Codebase

The current app already provides:
- one required primary policy PDF upload
- one optional reference policy PDF upload
- PDF text extraction with warnings for poor-quality or unreadable text
- deterministic chunking with overlap
- a staged OpenAI analysis pipeline
- a polished Streamlit results view
- baseline unit coverage for extraction, chunking, and schema normalization

In short, the MVP works end-to-end and does not need a foundational rebuild.

## Current Limitations Confirmed from the Codebase

The audit also confirmed several meaningful limitations:
- findings are returned as simple text lists instead of richer structured objects
- there is no severity scoring, so users cannot quickly prioritize issues
- there is no evidence model attached to findings
- the UI is attractive but still mostly static
- there is no export-to-PDF capability
- the app still handles only one primary policy and one optional reference at a time
- scanned PDFs and DOCX files are not supported

## Recommended Priority Order

1. Rich finding schema with severity scoring
2. Evidence-backed analyzer output
3. Executive scorecard and more interactive results UI
4. PDF export
5. Expanded intake such as multi-document workflows, DOCX, and OCR

## Why This Order

The strongest recommendation is to improve the quality of a single report before broadening the app's input scope.

Reasons:
- severity scoring makes the current output much more useful immediately
- evidence-backed findings increase trust and reviewability
- a better report UI improves demos and everyday usability
- PDF export creates immediate business value without introducing major system complexity
- multi-document support will be easier to design once the richer finding contract is stable

If multi-document analysis is built first, the app risks scaling a report format that is still too thin.

## Phase Roadmap

### Phase 1: Rich Single-Report Upgrade

Focus on:
- `Critical`, `High`, `Medium`, and `Low` severity levels
- evidence-backed findings
- executive scorecard metrics
- filterable or drill-down results
- PDF export

### Phase 2: Expanded Intake and Comparison

Focus on:
- multi-document analysis
- richer comparison workflows
- DOCX support
- OCR or scanned-PDF support

## Product Direction Summary

The next iteration should not be a broad grab-bag of features. It should be a deliberate upgrade of the current report model and report experience.

The MVP has already proven:
- upload works
- extraction works
- chunking works
- staged analysis works
- the UI foundation works

The next release should prove:
- findings can be prioritized
- findings can be traced to evidence
- reports can be shared outside the app
- the single-report experience is strong enough to support later expansion

