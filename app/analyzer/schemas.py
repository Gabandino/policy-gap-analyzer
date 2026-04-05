from __future__ import annotations

FINDING_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "category": {"type": "string"},
        "severity": {"type": "string", "enum": ["Critical", "High", "Medium", "Low"]},
        "title": {"type": "string"},
        "description": {"type": "string"},
        "evidence": {"type": "string"},
        "recommendation": {"type": "string"},
    },
    "required": [
        "category",
        "severity",
        "title",
        "description",
        "evidence",
        "recommendation",
    ],
    "additionalProperties": False,
}

ANALYSIS_RESULT_JSON_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "gaps": {"type": "array", "items": FINDING_SCHEMA},
        "inconsistencies": {"type": "array", "items": FINDING_SCHEMA},
        "risks": {"type": "array", "items": FINDING_SCHEMA},
        "recommendations": {"type": "array", "items": FINDING_SCHEMA},
    },
    "required": [
        "summary",
        "gaps",
        "inconsistencies",
        "risks",
        "recommendations",
    ],
    "additionalProperties": False,
}
