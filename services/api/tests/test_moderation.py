import pytest
from app.ai.openai_compatible import parse_moderation_result


def test_moderation_parser_accepts_safe_result():
    result = parse_moderation_result({"results": [{"flagged": False, "categories": {"violence": False}}]})
    assert result.flagged is False
    assert result.categories == ()


def test_moderation_parser_returns_flagged_categories():
    result = parse_moderation_result({
        "results": [{"flagged": True, "categories": {"sexual/minors": True, "violence": False, "harassment": True}}]
    })
    assert result.flagged is True
    assert result.categories == ("harassment", "sexual/minors")


def test_moderation_parser_fails_closed_on_empty_result():
    with pytest.raises(RuntimeError):
        parse_moderation_result({"results": []})
