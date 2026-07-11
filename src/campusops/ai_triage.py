import json
import os
from dataclasses import asdict
from typing import Any

from openai import OpenAI


SYSTEM_PROMPT = """
You are CampusOps Agent, a Slack-native campus support triage assistant.

Convert messy campus support messages into safe, structured ticket content.

Rules:
- Do not ask for passwords, OTP/MFA codes, full student IDs, SSNs, payment details, private medical details, or sensitive screenshots.
- Keep outputs short and operational.
- Prefer human review for account access, phishing/security, identity, facilities emergencies, and administrative changes.
- Return only valid JSON.
"""


def ai_refine_triage(message: str, base: Any) -> Any:
    """
    Uses OpenAI when OPENAI_API_KEY is configured.
    Falls back to the existing deterministic triage if anything fails.
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return base

    try:
        client = OpenAI(api_key=api_key)

        base_payload = asdict(base)

        user_prompt = {
            "message": message,
            "base_triage": base_payload,
            "required_json_schema": {
                "category": "string",
                "priority": "low | normal | high | urgent",
                "summary": "short string",
                "checklist": ["3 to 5 short safe next steps"],
                "escalation": "short escalation rule"
            }
        }

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(user_prompt)}
            ],
        )

        content = response.choices[0].message.content or "{}"
        refined = json.loads(content)
        print("✅ OpenAI AI-assisted triage used")
        return type(base)(
            category=refined.get("category") or base.category,
            priority=refined.get("priority") or base.priority,
            summary=refined.get("summary") or base.summary,
            checklist=refined.get("checklist") or base.checklist,
            escalation=refined.get("escalation") or base.escalation,
        )

    except Exception as e:
        print(f"⚠️ OpenAI triage fallback used: {e}")
        return base
