"""Tests for CanonicalCharacter dataclass."""

from faker_galactic.data.domains import CanonicalCharacter
from faker_galactic.provider import UNIVERSES


class TestCanonicalCharacterDataclass:
    """Tests for CanonicalCharacter dataclass behavior."""

    def test_canonical_character_creation_with_required_fields(self):
        """Can create character with only required fields."""
        char = CanonicalCharacter(first_name="James", last_name="Kirk")

        assert char.first_name == "James"
        assert char.last_name == "Kirk"
        assert char.name == "James Kirk"

    def test_canonical_character_creation_with_all_fields(self):
        """Can create character with all fields."""
        char = CanonicalCharacter(
            first_name="Jean-Luc",
            last_name="Picard",
            rank="Captain",
            starship="USS Enterprise",
            starship_registry="NCC-1701-D",
            starship_class="Galaxy-class",
            language="English",
            quotes=["Engage!", "Make it so."],
        )

        assert char.first_name == "Jean-Luc"
        assert char.last_name == "Picard"
        assert char.rank == "Captain"
        assert char.starship == "USS Enterprise"
        assert char.starship_registry == "NCC-1701-D"
        assert char.starship_class == "Galaxy-class"
        assert char.language == "English"
        assert char.quotes == ["Engage!", "Make it so."]
        assert char.name == "Jean-Luc Picard"

    def test_canonical_character_name_property(self):
        """name property returns full name."""
        char = CanonicalCharacter(first_name="Spock", last_name="Vulcan")
        assert char.name == "Spock Vulcan"

    def test_canonical_character_optional_fields_default_none(self):
        """Optional fields default to None."""
        char = CanonicalCharacter(first_name="Data", last_name="Soong")

        assert char.rank is None
        assert char.starship is None
        assert char.starship_registry is None
        assert char.starship_class is None
        assert char.language is None
        assert char.quotes is None

    def test_canonical_character_with_empty_quotes_list(self):
        """Can create character with empty quotes list."""
        char = CanonicalCharacter(first_name="William", last_name="Riker", quotes=[])

        assert char.quotes == []


class TestCanonicalCharacterIntegration:
    """Integration tests with real Star Trek characters."""

    def test_picard_character_has_expected_data(self):
        """Jean-Luc Picard character has expected attributes."""

        startrek = UNIVERSES["startrek"]
        picard = next(
            (c for c in startrek.CANONICAL_CHARACTERS if c.first_name == "Jean-Luc"),
            None,
        )

        assert picard is not None, "Picard should be in canonical characters"
        assert picard.last_name == "Picard"
        assert picard.rank == "Captain"
        assert picard.starship == "USS Enterprise"
        assert picard.starship_registry == "NCC-1701-D"
        assert picard.name == "Jean-Luc Picard"

    def test_all_startrek_canonical_characters_valid(self):
        """All Star Trek canonical characters are valid."""

        startrek = UNIVERSES["startrek"]

        for char in startrek.CANONICAL_CHARACTERS:
            assert isinstance(char, CanonicalCharacter)
            assert char.first_name
            assert char.last_name
            assert char.name  # Property should work
            # rank, starship, etc. are optional
