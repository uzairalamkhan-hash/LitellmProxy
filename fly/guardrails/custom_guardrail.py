"""
Proxy-level guardrail combining the three guardrail demos from
llm_gateway_tutorial.ipynb (PII redaction, prompt-injection blocking, forbidden
topics) — but running here as a real pre-call hook on the deployed LiteLLM
proxy itself, not just inside a notebook cell.

Registered in config.yaml under `guardrails:` with mode "pre_call", so this
runs on every request before it reaches Gemini/Groq/OpenAI/Claude.
"""
import re

from fastapi import HTTPException
from litellm.integrations.custom_guardrail import CustomGuardrail

PII_PATTERNS = {
    "EMAIL": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "PHONE_IN": r"(\+91[\-\s]?)?[6-9]\d{9}",
    "PHONE_US": r"(\+1[\-\s]?)?\(?\d{3}\)?[\-\s]?\d{3}[\-\s]?\d{4}",
    "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    "AADHAAR": r"\b\d{4}\s?\d{4}\s?\d{4}\b",
    "PAN": r"\b[A-Z]{5}\d{4}[A-Z]\b",
    "CREDIT_CARD": r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b",
    "IP_ADDRESS": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
}

INJECTION_PATTERNS = [
    r"ignore (all |the )?(previous|prior|above) (instructions?|prompts?|rules?)",
    r"disregard (the |all )?(previous|prior|earlier)",
    r"forget (everything|your instructions?|the rules?)",
    r"you are (now |a )?(DAN|jailbroken|unrestricted|unfiltered)",
    r"reveal your (system )?prompt",
    r"what (are|were) your (original )?instructions?",
]

FORBIDDEN_TOPICS = [
    "weapon", "bomb", "explosive", "hack", "exploit", "malware",
    "drugs", "illegal substance", "self-harm", "suicide",
]


def _redact_pii(text: str) -> str:
    clean = text
    for label, pattern in PII_PATTERNS.items():
        clean = re.sub(pattern, f"<{label}_REDACTED>", clean)
    return clean


def _check_injection(text: str):
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            raise HTTPException(status_code=400, detail=f"Request blocked by guardrail: possible prompt injection ('{pattern}')")


def _check_forbidden_topics(text: str):
    lowered = text.lower()
    for keyword in FORBIDDEN_TOPICS:
        if keyword in lowered:
            raise HTTPException(status_code=400, detail=f"Request blocked by guardrail: forbidden topic ('{keyword}')")


class LiveRampSafetyGuardrail(CustomGuardrail):
    """Runs before every call: blocks prompt injection and forbidden topics,
    redacts PII in-place so it never reaches the upstream model provider."""

    async def async_pre_call_hook(self, user_api_key_dict, cache, data: dict, call_type: str):
        messages = data.get("messages", [])
        for msg in messages:
            if msg.get("role") != "user" or not isinstance(msg.get("content"), str):
                continue
            _check_injection(msg["content"])
            _check_forbidden_topics(msg["content"])
            msg["content"] = _redact_pii(msg["content"])
        return data
