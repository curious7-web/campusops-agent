import re


def sanitize_user_text(text: str) -> str:
    # Remove bot mention tokens like <@U123>.
    text = re.sub(r"<@[A-Z0-9]+>", "", text or "")
    # Keep content short enough for prototype context.
    return text.strip()[:2000]


def contains_sensitive_data_warning(text: str) -> bool:
    t = text.lower()
    sensitive_terms = [
        "password is",
        "ssn",
        "social security",
        "student id",
        "date of birth",
        "medical",
        "diagnosis",
        "credit card",
    ]
    return any(term in t for term in sensitive_terms)
