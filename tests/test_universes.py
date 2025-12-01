"""Tests for universe data validation."""

import pytest

from faker_galactic.data.constants import UniverseAttribute
from faker_galactic.data.domains import CanonicalCharacter
from faker_galactic.provider import UNIVERSES



@pytest.mark.parametrize("universe_name", UNIVERSES.keys())
def test_universe_has_all_required_attributes(universe_name):
    """All universes must have all required attributes defined."""
    universe = UNIVERSES[universe_name]

    for attr in UniverseAttribute:
        assert hasattr(universe, attr.value), (
            f"Universe '{universe_name}' missing attribute: {attr.value}"
        )


@pytest.mark.parametrize("universe_name", UNIVERSES.keys())
def test_universe_has_non_empty_data(universe_name):
    """All universes must have non-empty data for all required attributes."""
    universe = UNIVERSES[universe_name]

    for attr in UniverseAttribute:
        data = getattr(universe, attr.value)
        assert data, f"Universe '{universe_name}' has empty {attr.value}"
        assert len(data) > 0, f"Universe '{universe_name}' has empty {attr.value}"


@pytest.mark.parametrize("universe_name", UNIVERSES.keys())
def test_universe_name_lists_are_lists_of_strings(universe_name):
    """Name attributes must be lists of non-empty strings."""
    universe = UNIVERSES[universe_name]

    name_attrs = [
        UniverseAttribute.FIRST_NAMES_MALE,
        UniverseAttribute.FIRST_NAMES_FEMALE,
        UniverseAttribute.LAST_NAMES_MALE,
        UniverseAttribute.LAST_NAMES_FEMALE,
    ]

    for attr in name_attrs:
        data = getattr(universe, attr.value)
        assert isinstance(data, list), f"{attr.value} must be a list"
        for name in data:
            assert isinstance(name, str), f"{attr.value} must contain strings"
            assert name.strip(), f"{attr.value} contains empty string"


@pytest.mark.parametrize("universe_name", UNIVERSES.keys())
def test_universe_canonical_characters_are_valid(universe_name):
    """Canonical characters must be valid CanonicalCharacter instances."""
    universe = UNIVERSES[universe_name]
    characters = universe.CANONICAL_CHARACTERS

    assert isinstance(characters, list), "CANONICAL_CHARACTERS must be a list"
    assert len(characters) > 0, "CANONICAL_CHARACTERS must not be empty"

    for char in characters:
        assert isinstance(char, CanonicalCharacter), (
            "All characters must be CanonicalCharacter instances"
        )
        assert char.first_name, "Character must have first_name"
        assert char.last_name, "Character must have last_name"
        # Other fields (rank, starship, etc.) are optional


@pytest.mark.parametrize("universe_name", UNIVERSES.keys())
def test_universe_starship_registries_have_valid_format(universe_name):
    """Starship registries must have pattern and weight."""
    universe = UNIVERSES[universe_name]
    registries = universe.STARSHIP_REGISTRIES

    assert isinstance(registries, list), "STARSHIP_REGISTRIES must be a list"
    assert len(registries) > 0, "STARSHIP_REGISTRIES must not be empty"

    for registry in registries:
        assert isinstance(registry, dict), "Each registry must be a dict"
        assert "pattern" in registry, "Registry must have 'pattern'"
        assert "weight" in registry, "Registry must have 'weight'"
        assert isinstance(registry["pattern"], str), "Pattern must be a string"
        assert isinstance(registry["weight"], (int, float)), "Weight must be numeric"
        assert registry["weight"] > 0, "Weight must be positive"


def test_startrek_has_sufficient_variety():
    """Star Trek universe should have sufficient data variety."""
    startrek = UNIVERSES["startrek"]

    # Verify we have enough names (plan calls for ~30 each)
    assert len(startrek.FIRST_NAMES_MALE) >= 25, "Need more male first names"
    assert len(startrek.FIRST_NAMES_FEMALE) >= 15, "Need more female first names"
    assert len(startrek.LAST_NAMES_MALE) >= 25, "Need more male last names"
    assert len(startrek.LAST_NAMES_FEMALE) >= 15, "Need more female last names"

    # Verify we have enough other data
    assert len(startrek.RANKS) >= 15, "Need more ranks"
    assert len(startrek.STARSHIPS) >= 20, "Need more starships"
    assert len(startrek.STARSHIP_CLASSES) >= 15, "Need more ship classes"
    assert len(startrek.CANONICAL_CHARACTERS) >= 15, "Need more canonical characters"


def test_universe_registry_keys():
    """Verify expected universes are registered."""
    assert "startrek" in UNIVERSES, "Star Trek universe should be registered"
    assert len(UNIVERSES) >= 1, "At least one universe should be registered"
