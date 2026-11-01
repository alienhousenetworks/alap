import pytest
from pydantic import ValidationError
from app.schemas.character import CharacterCreate, CharacterUpdate

def test_character_create_bounds_fields():
    item = CharacterCreate(name="Mira", personality={"tone": "warm"}, visibility="private")
    assert item.name == "Mira"
    with pytest.raises(ValidationError):
        CharacterCreate(name="x")

def test_character_update_rejects_invalid_visibility():
    with pytest.raises(ValidationError):
        CharacterUpdate(visibility="secret")
