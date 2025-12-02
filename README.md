<div align="center">
  <img src="./logo.png" width="200"/>

  <h1>Faker Galactic</h1>
  <p>Custom Faker provider for generating science fiction themed data from popular sci-fi universes</p>
</div>

## Installation

```bash
pip install faker-galactic
```

Or with uv:

```bash
uv add faker-galactic
```

## Quick Start

```python
from faker import Faker
from faker_galactic import SciFiProvider

fake = Faker()
fake.add_provider(SciFiProvider)

# Generate random sci-fi names
print(fake.scifi_first_name())  # "Spock"
print(fake.scifi_name())  # "James Kirk"

# Generate Star Trek specific data
print(fake.scifi_name(universe='startrek'))  # "Spock Sulu"
print(fake.starship(universe='startrek'))  # "USS Enterprise"
print(fake.scifi_rank(universe='startrek'))  # "Captain"
```

## Methods

All methods accept an optional `universe` parameter. When `None` (default), data is mixed from all universes. When specified (e.g., `'startrek'`), only that universe's data is used.

### Name Generation

```python
faker.scifi_first_name(universe: str | None = None) -> str
faker.scifi_first_name_male(universe: str | None = None) -> str
faker.scifi_first_name_female(universe: str | None = None) -> str
faker.scifi_last_name(universe: str | None = None) -> str
faker.scifi_last_name_male(universe: str | None = None) -> str
faker.scifi_last_name_female(universe: str | None = None) -> str
faker.scifi_name(universe: str | None = None) -> str  # Full name (first + last)
```

### Military & Organizations

```python
faker.scifi_rank(universe: str | None = None) -> str  # "Captain", "Commander", etc.
```

### Starships

```python
faker.starship(universe: str | None = None) -> str  # "USS Enterprise"
faker.starship_class(universe: str | None = None) -> str  # "Galaxy-class"
faker.starship_registry(
    universe: str | None = None,
    prefix_only: bool = False,  # Return "NCC" only
    number_only: bool = False   # Return "1701" only
) -> str  # Full: "NCC-1701"
```

### Locations & Culture

```python
faker.scifi_location(universe: str | None = None) -> str  # "USS Enterprise Recreation Deck"
faker.scifi_language(universe: str | None = None) -> str  # "Klingon", "Vulcan", etc.
faker.scifi_quote(universe: str | None = None) -> str  # Famous quotes
```

### Canonical Characters

Unlike other methods that generate random combinations, canonical characters return **actual characters from the source material** with complete profiles. Use when you need realistic, recognizable characters with consistent metadata (e.g., demo data where "Captain Picard commands the Enterprise" makes sense).

```python
faker.scifi_canonical_character(universe: str | None = None) -> CanonicalCharacter
```

Returns a `CanonicalCharacter` dataclass with:

- `first_name: str`
- `last_name: str`
- `name: str` (property: full name)
- `rank: str | None`
- `starship: str | None`
- `starship_registry: str | None`
- `starship_class: str | None`
- `language: str | None`
- `quotes: list[str] | None`

## Supported Universes

### `'startrek'` - Star Trek (TOS, TNG, DS9, VOY, Discovery)

**Data counts:**

- 30 male first names, 30 female first names
- 30 male last names, 20 female last names
- 19 ranks (Captain, Commander, Admiral, Ensign, etc.)
- 24 starships (USS Enterprise, USS Voyager, USS Defiant, etc.)
- 4 registry patterns with weights (NCC-####, NCC-#####, NX-#####, NAR-#####)
- 18 starship classes (Galaxy-class, Intrepid-class, Constitution-class, etc.)
- 15 base locations (Starfleet Academy, Deep Space Nine, Earth Spacedock, etc.)
- 20 location details (Recreation Deck, Holodeck, Sickbay, etc.)
- 14 languages (Klingon, Vulcan, Romulan, Cardassian, Bajoran, etc.)
- 20 famous quotes
- 20 canonical characters (Picard, Kirk, Janeway, Spock, Data, etc.)

## Contributing

Interested in adding new universes or improving the library? See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup
- Code quality standards
- How to add new universes
- Testing guidelines
- Pull request process
