from __future__ import annotations

import streamlit as st


SESSION_DEFAULTS = {
    "primary_document": None,
    "reference_document": None,
    "primary_extracted_document": None,
    "reference_extracted_document": None,
    "primary_chunking_result": None,
    "reference_chunking_result": None,
    "analysis_request": None,
    "analysis_result": None,
    "last_submission_error": None,
    "last_analysis_error": None,
}


def initialize_session_state() -> None:
    for key, value in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value
