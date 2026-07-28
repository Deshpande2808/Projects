import json
from unittest.mock import MagicMock

import pytest

from classify import CATEGORIES, _extract_json, classify_email


def _fake_client(reply: str) -> MagicMock:
    client = MagicMock()
    block = MagicMock()
    block.text = reply
    client.messages.create.return_value.content = [block]
    return client


@pytest.mark.parametrize("category", CATEGORIES)
def test_classify_email_returns_parsed_result(category):
    reply = json.dumps({"category": category, "confidence": 0.9, "reason": "matches example"})
    client = _fake_client(reply)

    result = classify_email("My login stopped working", client=client)

    assert result == {"category": category, "confidence": 0.9, "reason": "matches example"}
    client.messages.create.assert_called_once()


def test_classify_email_rejects_unknown_category():
    reply = json.dumps({"category": "Spam", "confidence": 0.9, "reason": "n/a"})
    client = _fake_client(reply)

    with pytest.raises(ValueError, match="unrecognized category"):
        classify_email("buy pills now", client=client)


def test_extract_json_handles_surrounding_prose():
    text = 'Sure, here is the result:\n{"category": "Sales", "confidence": 0.8, "reason": "pricing question"}\nLet me know if needed.'
    assert _extract_json(text) == {"category": "Sales", "confidence": 0.8, "reason": "pricing question"}


def test_extract_json_raises_without_json():
    with pytest.raises(ValueError, match="No JSON object found"):
        _extract_json("no json here")
