"""Email Classification Service — single-call LLM classifier.

Categorizes an email into Support/Sales/Billing/Other using the Claude API.
"""
import argparse
import json
import os
import re
import sys

import anthropic

MODEL = "claude-sonnet-5"
CATEGORIES = ("Support", "Sales", "Billing", "Other")

SYSTEM_PROMPT = f"""You are an email classifier. Analyze emails and categorize them strictly.

Categories: {", ".join(CATEGORIES)}

Examples:
- Email: "My login stopped working" -> Category: Support
- Email: "How much is the Pro plan?" -> Category: Sales
- Email: "I was charged twice this month" -> Category: Billing

Respond with ONLY a JSON object in this exact shape, no other text:
{{"category": "...", "confidence": 0.0, "reason": "..."}}
"""


def _extract_json(text: str) -> dict:
    text = text.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in model response: {text!r}")
    return json.loads(match.group(0))


def classify_email(email_text: str, client: anthropic.Anthropic | None = None) -> dict:
    """Classify a single email. Returns {"category", "confidence", "reason"}."""
    client = client or anthropic.Anthropic()

    response = client.messages.create(
        model=MODEL,
        max_tokens=256,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Email to classify: {email_text}"}],
    )
    raw_text = response.content[0].text
    result = _extract_json(raw_text)

    if result.get("category") not in CATEGORIES:
        raise ValueError(f"Model returned an unrecognized category: {result.get('category')!r}")

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify an email into Support/Sales/Billing/Other")
    parser.add_argument("email", nargs="?", help="Email text. If omitted, reads from stdin.")
    args = parser.parse_args()

    email_text = args.email if args.email is not None else sys.stdin.read()
    if not email_text.strip():
        parser.error("no email text provided (pass as argument or pipe via stdin)")

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY is not set")

    result = classify_email(email_text)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
