import pytest
from pydantic import ValidationError
from app.schemas.moderation import CharacterReportCreate, ReportResolution


def test_character_report_reason_is_allowlisted():
    assert CharacterReportCreate(reason="minor_safety").reason == "minor_safety"
    with pytest.raises(ValidationError):
        CharacterReportCreate(reason="anything")


def test_report_resolution_only_allows_terminal_states():
    assert ReportResolution(status="resolved", note="Reviewed").status == "resolved"
    with pytest.raises(ValidationError):
        ReportResolution(status="open")
