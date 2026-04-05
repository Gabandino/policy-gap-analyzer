from __future__ import annotations

import json
import logging
from typing import Any

from openai import APIConnectionError, APIStatusError, OpenAI, RateLimitError


logger = logging.getLogger(__name__)


class AnalysisClientError(Exception):
    """Raised when the LLM analysis client cannot return a usable structured response."""


class OpenAIAnalysisClient:
    def __init__(self, api_key: str, model: str) -> None:
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def generate_structured_output(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema_name: str,
        schema: dict[str, object],
        max_output_tokens: int = 1400,
    ) -> dict[str, object]:
        logger.info("Submitting structured analysis request: %s.", schema_name)
        try:
            response = self._client.responses.create(
                model=self._model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_output_tokens=max_output_tokens,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": schema_name,
                        "strict": True,
                        "schema": schema,
                    }
                },
            )
        except RateLimitError as exc:
            logger.warning("Rate limit while requesting %s.", schema_name)
            raise AnalysisClientError(
                "The OpenAI API rate limit was hit during analysis. Wait a moment and try again."
            ) from exc
        except APIConnectionError as exc:
            logger.warning("Connection error while requesting %s.", schema_name)
            raise AnalysisClientError(
                "The app could not reach the OpenAI API. Check your network connection and try again."
            ) from exc
        except APIStatusError as exc:
            logger.warning("API status error %s while requesting %s.", exc.status_code, schema_name)
            raise AnalysisClientError(
                f"The OpenAI API returned an error during analysis ({exc.status_code}). Try again shortly."
            ) from exc
        except Exception as exc:
            logger.exception("Unexpected analysis client failure while requesting %s.", schema_name)
            raise AnalysisClientError(
                "The analysis request could not be completed due to an unexpected client error."
            ) from exc

        refusal = self._extract_refusal(response)
        if refusal:
            logger.warning("Model refusal received for %s.", schema_name)
            raise AnalysisClientError(f"The model refused the analysis request: {refusal}")

        output_text = getattr(response, "output_text", "") or ""
        if not output_text:
            logger.warning("Empty model output received for %s.", schema_name)
            raise AnalysisClientError("The model returned an empty analysis response.")

        try:
            payload = json.loads(output_text)
        except json.JSONDecodeError as exc:
            logger.warning("Invalid JSON returned for %s.", schema_name)
            raise AnalysisClientError(
                "The model returned malformed structured output. Please try the analysis again."
            ) from exc

        if not isinstance(payload, dict):
            logger.warning("Unexpected JSON shape returned for %s.", schema_name)
            raise AnalysisClientError(
                "The model returned an unexpected structured response shape."
            )

        logger.info("Structured analysis response received for %s.", schema_name)
        return payload

    def _extract_refusal(self, response: Any) -> str | None:
        output = getattr(response, "output", None)
        if not isinstance(output, list):
            return None

        refusals: list[str] = []
        for item in output:
            content_items = getattr(item, "content", None)
            if not isinstance(content_items, list):
                continue

            for content_item in content_items:
                if getattr(content_item, "type", None) == "refusal":
                    refusal_text = getattr(content_item, "refusal", None)
                    if isinstance(refusal_text, str) and refusal_text.strip():
                        refusals.append(refusal_text.strip())

        if refusals:
            return " ".join(refusals)

        return None
