"""faker-galactic: Science fiction themed Faker provider for multiple universes."""

from .data.domains import CanonicalCharacter
from .provider import SciFiProvider

__version__ = "1.0.0"
__all__ = ["SciFiProvider", "CanonicalCharacter"]
