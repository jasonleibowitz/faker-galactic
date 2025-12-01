"""Shared data structures for sci-fi universe providers."""

from dataclasses import dataclass


@dataclass
class CanonicalCharacter:
    """Complete profile for a canonical sci-fi character."""

    first_name: str
    last_name: str
    rank: str | None = None
    starship: str | None = None
    starship_registry: str | None = None
    starship_class: str | None = None
    language: str | None = None
    quotes: list[str] | None = None

    @property
    def name(self) -> str:
        """Full character name."""
        return f"{self.first_name} {self.last_name}"
