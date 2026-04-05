from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import configure_logging, load_config
from app.ui.theme import apply_theme
from app.ui.upload_view import render_upload_section


def main() -> None:
    config = load_config()
    configure_logging(config.log_level)

    st.set_page_config(
        page_title=config.app_title,
        page_icon=":page_facing_up:",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    apply_theme()
    render_upload_section(config)


if __name__ == "__main__":
    main()
