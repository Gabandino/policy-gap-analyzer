from __future__ import annotations

import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
        <style>
            :root {
                --bg-start: #0f0b1f;
                --bg-end: #171f4f;
                --panel: rgba(17, 24, 39, 0.72);
                --panel-border: rgba(147, 197, 253, 0.18);
                --text-main: #eef2ff;
                --text-muted: #c7d2fe;
                --accent: #8b5cf6;
                --accent-soft: #60a5fa;
                --success: #38bdf8;
                --warning: #fbbf24;
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(139, 92, 246, 0.35), transparent 28%),
                    radial-gradient(circle at top right, rgba(96, 165, 250, 0.28), transparent 32%),
                    linear-gradient(135deg, var(--bg-start), var(--bg-end));
            }

            .block-container {
                max-width: 1120px;
                padding-top: 2.5rem;
                padding-bottom: 3rem;
            }

            .hero-card,
            .panel-card {
                background: var(--panel);
                border: 1px solid var(--panel-border);
                border-radius: 24px;
                box-shadow: 0 20px 60px rgba(15, 23, 42, 0.25);
                backdrop-filter: blur(10px);
            }

            .hero-card {
                padding: 2.5rem;
                margin-bottom: 1.5rem;
            }

            .hero-kicker {
                display: inline-block;
                margin-bottom: 1rem;
                padding: 0.35rem 0.75rem;
                border-radius: 999px;
                background: rgba(96, 165, 250, 0.16);
                color: #dbeafe;
                font-size: 0.85rem;
                letter-spacing: 0.04em;
                text-transform: uppercase;
                font-weight: 600;
            }

            .hero-title {
                margin: 0;
                color: var(--text-main);
                font-size: clamp(2.4rem, 4vw, 4.25rem);
                line-height: 1;
                font-weight: 800;
            }

            .hero-copy {
                max-width: 760px;
                margin-top: 1rem;
                color: var(--text-muted);
                font-size: 1.05rem;
                line-height: 1.7;
            }

            .feature-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 0.9rem;
                margin-top: 1.5rem;
            }

            .feature-chip {
                padding: 1rem 1.1rem;
                border-radius: 18px;
                background: rgba(15, 23, 42, 0.42);
                border: 1px solid rgba(199, 210, 254, 0.12);
                color: var(--text-main);
                font-size: 0.95rem;
            }

            .panel-card {
                padding: 1.4rem;
            }

            .panel-title {
                margin: 0 0 0.35rem 0;
                color: var(--text-main);
                font-size: 1.2rem;
                font-weight: 700;
            }

            .panel-copy {
                color: var(--text-muted);
                margin-bottom: 1rem;
            }

            .status-note {
                margin-top: 0.9rem;
                color: var(--text-muted);
                font-size: 0.92rem;
            }

            .results-shell {
                margin-top: 1.6rem;
            }

            .results-kicker {
                display: inline-block;
                margin-bottom: 0.9rem;
                padding: 0.35rem 0.75rem;
                border-radius: 999px;
                background: rgba(139, 92, 246, 0.18);
                color: #e9d5ff;
                font-size: 0.82rem;
                letter-spacing: 0.05em;
                text-transform: uppercase;
                font-weight: 700;
            }

            .results-title {
                margin: 0 0 0.4rem 0;
                color: var(--text-main);
                font-size: 1.75rem;
                font-weight: 800;
            }

            .results-copy {
                margin: 0 0 1.25rem 0;
                color: var(--text-muted);
                font-size: 1rem;
                line-height: 1.6;
            }

            .result-card {
                background: rgba(15, 23, 42, 0.5);
                border: 1px solid rgba(199, 210, 254, 0.14);
                border-radius: 22px;
                padding: 1.25rem;
                min-height: 100%;
            }

            .result-card + .result-card {
                margin-top: 1rem;
            }

            .result-card-title {
                margin: 0 0 0.35rem 0;
                color: var(--text-main);
                font-size: 1.05rem;
                font-weight: 700;
            }

            .result-card-copy {
                margin: 0;
                color: var(--text-muted);
                line-height: 1.65;
            }

            .meta-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 0.75rem;
                margin-bottom: 1rem;
            }

            .meta-chip {
                padding: 0.85rem 0.95rem;
                border-radius: 16px;
                background: rgba(30, 41, 59, 0.72);
                border: 1px solid rgba(147, 197, 253, 0.12);
            }

            .meta-label {
                display: block;
                margin-bottom: 0.2rem;
                color: #c4b5fd;
                font-size: 0.74rem;
                letter-spacing: 0.04em;
                text-transform: uppercase;
                font-weight: 700;
            }

            .meta-value {
                color: var(--text-main);
                font-size: 0.98rem;
                font-weight: 600;
                line-height: 1.4;
            }

            .warning-note {
                margin-top: 0.8rem;
                padding: 0.85rem 0.95rem;
                border-radius: 16px;
                background: rgba(251, 191, 36, 0.12);
                border: 1px solid rgba(251, 191, 36, 0.18);
                color: #fde68a;
                font-size: 0.92rem;
                line-height: 1.5;
            }

            .empty-state {
                margin-top: 0.75rem;
                padding: 0.95rem 1rem;
                border-radius: 16px;
                background: rgba(96, 165, 250, 0.1);
                border: 1px dashed rgba(96, 165, 250, 0.24);
                color: #dbeafe;
                font-size: 0.95rem;
            }

            [data-testid="stFileUploaderDropzone"] {
                background: rgba(15, 23, 42, 0.34);
                border: 1px dashed rgba(147, 197, 253, 0.35);
                border-radius: 18px;
            }

            [data-testid="stFileUploaderDropzone"] * {
                color: var(--text-main);
            }

            .stButton > button {
                width: 100%;
                border: none;
                border-radius: 999px;
                background: linear-gradient(135deg, var(--accent), var(--accent-soft));
                color: white;
                font-weight: 700;
                padding: 0.75rem 1.1rem;
                box-shadow: 0 14px 28px rgba(96, 165, 250, 0.22);
            }

            .stButton > button:hover {
                filter: brightness(1.05);
            }

            @media (max-width: 900px) {
                .hero-card {
                    padding: 1.75rem;
                }

                .panel-card,
                .result-card {
                    padding: 1.05rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
