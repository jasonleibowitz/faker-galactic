"""Faker provider for sci-fi themed data."""

import logging
from typing import Literal, TypeVar, cast, overload

from faker.providers import BaseProvider

from .data.constants import UniverseAttribute
from .data.domains import CanonicalCharacter, RegistryConfig
from .data.startrek import StarTrekData

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Static universe registry
UNIVERSES = {
    "startrek": StarTrekData(),
    # Future: 'starwars': StarWarsData(),
}


class SciFiProvider(BaseProvider):
    """Faker provider for sci-fi themed data."""

    @overload
    def _get_data(
        self,
        attr: Literal[
            UniverseAttribute.FIRST_NAMES_MALE,
            UniverseAttribute.FIRST_NAMES_FEMALE,
            UniverseAttribute.LAST_NAMES_MALE,
            UniverseAttribute.LAST_NAMES_FEMALE,
            UniverseAttribute.RANKS,
            UniverseAttribute.STARSHIPS,
            UniverseAttribute.STARSHIP_CLASSES,
            UniverseAttribute.BASE_LOCATIONS,
            UniverseAttribute.LOCATION_DETAILS,
            UniverseAttribute.LANGUAGES,
            UniverseAttribute.QUOTES,
        ],
        universe: str | None = None,
    ) -> list[str]: ...

    @overload
    def _get_data(
        self,
        attr: Literal[UniverseAttribute.STARSHIP_REGISTRIES],
        universe: str | None = None,
    ) -> list[RegistryConfig]: ...

    @overload
    def _get_data(
        self,
        attr: Literal[UniverseAttribute.CANONICAL_CHARACTERS],
        universe: str | None = None,
    ) -> list[CanonicalCharacter]: ...

    def _get_data(
        self, attr: UniverseAttribute, universe: str | None = None
    ) -> list[str] | list[RegistryConfig] | list[CanonicalCharacter]:
        """
        Get data attribute from universe(s).

        If universe is None, collects from all universes.
        If data is empty, logs warning and falls back to mixed mode.

        Args:
            attr: Attribute to get from universe data (type-safe enum)
            universe: Universe name to get data from, or None for mixed mode

        Returns:
            List of data from requested universe or all universes

        Raises:
            ValueError: If universe name is not in registry
        """
        if universe:
            if universe not in UNIVERSES:
                raise ValueError(
                    f"Unknown universe '{universe}'. "
                    f"Available: {list(UNIVERSES.keys())}"
                )

            data = getattr(UNIVERSES[universe], attr.value)

            # Fallback to mixed mode if universe doesn't provide this data
            if not data:
                logger.warning(
                    f"Universe '{universe}' does not provide {attr.value}. "
                    f"Falling back to mixed universe mode."
                )
                universe = None

        if universe is None:
            # Collect from all universes
            data = []
            for univ_data in UNIVERSES.values():
                universe_attr = getattr(univ_data, attr.value)
                if isinstance(universe_attr, list):
                    data.extend(universe_attr)

        return cast(list[str] | list[RegistryConfig] | list[CanonicalCharacter], data)

    def _random_element(self, items: list[T]) -> T:
        """Type-safe wrapper for random_element.

        Centralizes the cast needed for Faker's untyped random_element() method.
        """
        return self.random_element(items)

    # Name methods

    def scifi_first_name(self, universe: str | None = None) -> str:
        """Generate sci-fi first name (any gender)."""
        male_names = self._get_data(UniverseAttribute.FIRST_NAMES_MALE, universe)
        female_names = self._get_data(UniverseAttribute.FIRST_NAMES_FEMALE, universe)
        all_names = male_names + female_names
        return self._random_element(all_names)

    def scifi_first_name_male(self, universe: str | None = None) -> str:
        """Generate male sci-fi first name."""
        names = self._get_data(UniverseAttribute.FIRST_NAMES_MALE, universe)
        return self._random_element(names)

    def scifi_first_name_female(self, universe: str | None = None) -> str:
        """Generate female sci-fi first name."""
        names = self._get_data(UniverseAttribute.FIRST_NAMES_FEMALE, universe)
        return self._random_element(names)

    def scifi_last_name(self, universe: str | None = None) -> str:
        """Generate sci-fi last name (any gender)."""
        male_names = self._get_data(UniverseAttribute.LAST_NAMES_MALE, universe)
        female_names = self._get_data(UniverseAttribute.LAST_NAMES_FEMALE, universe)
        all_names = male_names + female_names
        return self._random_element(all_names)

    def scifi_last_name_male(self, universe: str | None = None) -> str:
        """Generate male sci-fi last name."""
        names = self._get_data(UniverseAttribute.LAST_NAMES_MALE, universe)
        return self._random_element(names)

    def scifi_last_name_female(self, universe: str | None = None) -> str:
        """Generate female sci-fi last name."""
        names = self._get_data(UniverseAttribute.LAST_NAMES_FEMALE, universe)
        return self._random_element(names)

    def scifi_name(self, universe: str | None = None) -> str:
        """Generate full sci-fi name (first + last)."""
        first = self.scifi_first_name(universe)
        last = self.scifi_last_name(universe)
        return f"{first} {last}"

    # Other methods

    def scifi_rank(self, universe: str | None = None) -> str:
        """Generate military/organizational rank."""
        ranks = self._get_data(UniverseAttribute.RANKS, universe)
        return self._random_element(ranks)

    def starship(self, universe: str | None = None) -> str:
        """Generate starship name."""
        starships = self._get_data(UniverseAttribute.STARSHIPS, universe)
        return self._random_element(starships)

    def starship_registry(
        self,
        universe: str | None = None,
        prefix_only: bool = False,
        number_only: bool = False,
    ) -> str:
        """
        Generate starship registry number.

        Args:
            universe: Universe to generate from (None = mixed)
            prefix_only: Return only the prefix (e.g., "NCC")
            number_only: Return only the number (e.g., "1701")

        Returns:
            Full registry like "NCC-1701", or prefix/number if requested
        """
        registries = self._get_data(UniverseAttribute.STARSHIP_REGISTRIES, universe)

        # Weighted random selection
        registry_config = self._random_element(registries)
        pattern = registry_config.pattern

        # Use Faker's bothify to generate from pattern  ("NCC-####" -> "NCC-1701")
        full_registry = self.bothify(pattern)

        if prefix_only:
            return full_registry.split("-")[0]  # "NCC"
        if number_only:
            return full_registry.split("-")[1]  # "1701"

        return full_registry

    def starship_class(self, universe: str | None = None) -> str:
        """Generate starship class name."""
        classes = self._get_data(UniverseAttribute.STARSHIP_CLASSES, universe)
        return self._random_element(classes)

    def scifi_location(self, universe: str | None = None) -> str:
        """
        Generate sci-fi location name by combining base + detail.

        Combines starships or base locations with detail suffixes:
        - "USS Enterprise Recreation Deck"
        - "Starfleet Academy Holodeck"
        - "Quark's Bar Back Room"
        """
        starships = self._get_data(UniverseAttribute.STARSHIPS, universe)
        base_locations = self._get_data(UniverseAttribute.BASE_LOCATIONS, universe)
        location_details = self._get_data(UniverseAttribute.LOCATION_DETAILS, universe)

        # Pick either a starship or base location
        all_bases = starships + base_locations
        base = self._random_element(all_bases)
        detail = self._random_element(location_details)

        return f"{base} {detail}"

    def scifi_language(self, universe: str | None = None) -> str:
        """Generate language/dialect name."""
        languages = self._get_data(UniverseAttribute.LANGUAGES, universe)
        return self._random_element(languages)

    def scifi_quote(self, universe: str | None = None) -> str:
        """Generate famous quote."""
        quotes = self._get_data(UniverseAttribute.QUOTES, universe)
        return self._random_element(quotes)

    def scifi_canonical_character(
        self, universe: str | None = None
    ) -> CanonicalCharacter:
        """
        Generate complete canonical character profile.

        Returns actual character with full metadata (name, rank, ship, quotes).
        """
        characters = self._get_data(UniverseAttribute.CANONICAL_CHARACTERS, universe)
        return self._random_element(characters)
