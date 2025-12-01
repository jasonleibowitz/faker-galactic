"""Tests for SciFiProvider methods."""

import pytest
from faker import Faker

from faker_galactic.data.domains import CanonicalCharacter
from faker_galactic.provider import UNIVERSES, SciFiProvider


@pytest.fixture
def faker():
    """Faker instance with SciFiProvider."""
    faker = Faker()
    faker.add_provider(SciFiProvider)
    return faker


class TestNameMethods:
    """Tests for name generation methods."""

    def test_first_name_returns_string(self, faker):
        """scifi_first_name() returns a non-empty string."""
        result = faker.scifi_first_name()
        assert isinstance(result, str)
        assert result

    def test_first_name_with_universe_returns_valid_name(self, faker):
        """scifi_first_name('startrek') returns name from Star Trek universe."""
        result = faker.scifi_first_name("startrek")

        valid_names = (
            UNIVERSES["startrek"].FIRST_NAMES_MALE
            + UNIVERSES["startrek"].FIRST_NAMES_FEMALE
        )

        assert result in valid_names

    def test_first_name_male_returns_male_name(self, faker):
        """scifi_first_name_male() returns name from male list."""
        result = faker.scifi_first_name_male("startrek")
        assert result in UNIVERSES["startrek"].FIRST_NAMES_MALE

    def test_first_name_female_returns_female_name(self, faker):
        """scifi_first_name_female() returns name from female list."""
        result = faker.scifi_first_name_female("startrek")
        assert result in UNIVERSES["startrek"].FIRST_NAMES_FEMALE

    def test_last_name_returns_string(self, faker):
        """scifi_last_name() returns a non-empty string."""
        result = faker.scifi_last_name()
        assert isinstance(result, str)
        assert result

    def test_last_name_with_universe_returns_valid_name(self, faker):
        """scifi_last_name('startrek') returns name from Star Trek universe."""
        result = faker.scifi_last_name("startrek")

        valid_names = (
            UNIVERSES["startrek"].LAST_NAMES_MALE
            + UNIVERSES["startrek"].LAST_NAMES_FEMALE
        )

        assert result in valid_names

    def test_last_name_male_returns_male_name(self, faker):
        """scifi_last_name_male() returns name from male list."""
        result = faker.scifi_last_name_male("startrek")
        assert result in UNIVERSES["startrek"].LAST_NAMES_MALE

    def test_last_name_female_returns_female_name(self, faker):
        """scifi_last_name_female() returns name from female list."""
        result = faker.scifi_last_name_female("startrek")
        assert result in UNIVERSES["startrek"].LAST_NAMES_FEMALE

    def test_name_returns_full_name(self, faker):
        """scifi_name() returns 'FirstName LastName' format."""
        result = faker.scifi_name()
        assert isinstance(result, str)
        assert " " in result  # Should have space between first and last
        parts = result.split()
        assert len(parts) >= 2  # At least first and last name


class TestOtherMethods:
    """Tests for non-name generation methods."""

    def test_rank_returns_valid_rank(self, faker):
        """scifi_rank() returns a valid military/organizational rank."""
        result = faker.scifi_rank("startrek")
        assert result in UNIVERSES["startrek"].RANKS

    def test_starship_returns_valid_starship(self, faker):
        """starship() returns a valid starship name."""
        result = faker.starship("startrek")
        assert result in UNIVERSES["startrek"].STARSHIPS

    def test_starship_class_returns_valid_class(self, faker):
        """starship_class() returns a valid starship class."""
        result = faker.starship_class("startrek")
        assert result in UNIVERSES["startrek"].STARSHIP_CLASSES

    def test_language_returns_valid_language(self, faker):
        """scifi_language() returns a valid language/dialect."""
        result = faker.scifi_language("startrek")
        assert result in UNIVERSES["startrek"].LANGUAGES

    def test_quote_returns_valid_quote(self, faker):
        """scifi_quote() returns a valid quote."""
        result = faker.scifi_quote("startrek")
        assert result in UNIVERSES["startrek"].QUOTES


class TestStarshipRegistry:
    """Tests for starship_registry() method."""

    def test_starship_registry_returns_full_registry(self, faker):
        """starship_registry() returns full registry like 'NCC-1947'."""
        result = faker.starship_registry("startrek")
        assert isinstance(result, str)
        assert "-" in result  # Should have hyphen separator
        parts = result.split("-")
        assert len(parts) == 2  # Prefix and number
        assert parts[0].isalpha()  # Prefix is letters
        assert parts[1].isdigit()  # Number is digits

    def test_starship_registry_prefix_only(self, faker):
        """starship_registry(prefix_only=True) returns only prefix."""
        result = faker.starship_registry("startrek", prefix_only=True)
        assert isinstance(result, str)
        assert result.isalpha()
        assert "-" not in result

    def test_starship_registry_number_only(self, faker):
        """starship_registry(number_only=True) returns only number."""
        result = faker.starship_registry("startrek", number_only=True)
        assert isinstance(result, str)
        assert result.isdigit()
        assert "-" not in result


class TestLocation:
    """Tests for scifi_location() method."""

    def test_location_returns_combined_string(self, faker):
        """scifi_location() returns base + detail combination."""
        result = faker.scifi_location("startrek")
        assert isinstance(result, str)
        assert " " in result  # Should combine base and detail with space

        # Result should contain either a starship or base location
        valid_bases = (
            UNIVERSES["startrek"].STARSHIPS + UNIVERSES["startrek"].BASE_LOCATIONS
        )

        # Check if any valid base is in the result
        assert any(base in result for base in valid_bases)


class TestCanonicalCharacter:
    """Tests for scifi_canonical_character() method."""

    def test_canonical_character_returns_character_instance(self, faker):
        """scifi_canonical_character() returns CanonicalCharacter instance."""
        result = faker.scifi_canonical_character("startrek")
        assert isinstance(result, CanonicalCharacter)

    def test_canonical_character_has_required_fields(self, faker):
        """Canonical character has required name fields."""
        result = faker.scifi_canonical_character("startrek")
        assert result.first_name
        assert result.last_name
        assert result.name  # Property should work

    def test_canonical_character_from_valid_list(self, faker):
        """scifi_canonical_character() returns character from universe list."""
        result = faker.scifi_canonical_character("startrek")
        assert result in UNIVERSES["startrek"].CANONICAL_CHARACTERS


class TestMixedUniverseMode:
    """Tests for mixed universe mode (universe=None)."""

    def test_mixed_mode_first_name(self, faker):
        """scifi_first_name() without universe works (mixed mode)."""
        result = faker.scifi_first_name()
        assert isinstance(result, str)
        assert result

    def test_mixed_mode_starship(self, faker):
        """starship() without universe works (mixed mode)."""
        result = faker.starship()
        assert isinstance(result, str)
        assert result

    def test_mixed_mode_canonical_character(self, faker):
        """scifi_canonical_character() without universe works (mixed mode)."""
        result = faker.scifi_canonical_character()
        assert isinstance(result, CanonicalCharacter)


class TestErrorHandling:
    """Tests for error handling and validation."""

    def test_unknown_universe_raises_error(self, faker):
        """Using unknown universe raises ValueError."""
        with pytest.raises(ValueError, match="Unknown universe"):
            faker.scifi_first_name("starwars")

    def test_error_message_includes_available_universes(self, faker):
        """Error message lists available universes."""
        with pytest.raises(ValueError, match="Available"):
            faker.scifi_first_name("nonexistent")


class TestSeeding:
    """Tests for reproducibility with seeding."""

    def test_seeding_produces_same_results(self):
        """Faker.seed() produces reproducible results."""
        fake1 = Faker()
        fake1.add_provider(SciFiProvider)
        Faker.seed(42)
        result1 = fake1.scifi_name()

        fake2 = Faker()
        fake2.add_provider(SciFiProvider)
        Faker.seed(42)
        result2 = fake2.scifi_name()

        assert result1 == result2

    def test_different_seeds_produce_different_results(self):
        """Different seeds produce different results."""
        fake = Faker()
        fake.add_provider(SciFiProvider)

        # Note: There's a small chance they could be the same
        # Run multiple times to be confident
        results_42 = []
        results_99 = []

        for _ in range(10):
            Faker.seed(42)
            results_42.append(fake.scifi_name())

            Faker.seed(99)
            results_99.append(fake.scifi_name())

        # At least one should differ
        assert results_42 != results_99
