"""faker-galactic: Science fiction themed Faker provider for multiple universes."""

from .provider import SciFiProvider
from .data.domains import CanonicalCharacter

__version__ = "1.0.0"
__all__ = ["SciFiProvider", "CanonicalCharacter"]