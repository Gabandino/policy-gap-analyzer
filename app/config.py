from __future__ import annotations

import logging
import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    app_title: str = "Policy Gap Analyzer"
    app_subtitle: str = (
        "Upload a policy document and get a structured review of gaps, "
        "inconsistencies, risks, and recommendations."
    )
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    max_upload_size_mb: int = 15
    default_chunk_size: int = 2500
    default_chunk_overlap: int = 250
    allowed_extensions: tuple[str, ...] = ("pdf",)
    log_level: str = "INFO"


def load_config() -> AppConfig:
    openai_api_key = os.getenv("OPENAI_API_KEY") or None
    openai_model = os.getenv("OPENAI_MODEL", AppConfig.openai_model)
    max_upload_size_mb = _get_int("MAX_UPLOAD_SIZE_MB", AppConfig.max_upload_size_mb)
    default_chunk_size = _get_int("DEFAULT_CHUNK_SIZE", AppConfig.default_chunk_size)
    default_chunk_overlap = _get_int(
        "DEFAULT_CHUNK_OVERLAP",
        AppConfig.default_chunk_overlap,
    )

    log_level = os.getenv("LOG_LEVEL", AppConfig.log_level).upper()

    return AppConfig(
        openai_api_key=openai_api_key,
        openai_model=openai_model,
        max_upload_size_mb=max_upload_size_mb,
        default_chunk_size=default_chunk_size,
        default_chunk_overlap=default_chunk_overlap,
        log_level=log_level,
    )


def _get_int(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    try:
        return int(raw_value)
    except ValueError:
        return default


def configure_logging(level_name: str) -> None:
    level = getattr(logging, level_name.upper(), logging.INFO)
    root_logger = logging.getLogger()

    if not root_logger.handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )
    else:
        root_logger.setLevel(level)
