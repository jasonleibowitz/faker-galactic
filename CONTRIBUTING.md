# Contributing to faker-galactic

Thank you for contributing! This guide covers development setup, code quality standards, and how to add new universes.

## Development Setup

### Prerequisites

- Python 3.13+
- uv (recommended) or pip

### Install Dependencies

```bash
uv sync --group dev
```

### Install Pre-commit Hooks

```bash
pre-commit install
```

This sets up automatic code quality checks that run before every commit.

## Code Quality Standards

This project enforces strict code quality via pre-commit hooks that block commits if checks fail:

- **ruff** (v0.8.4): Linting and formatting (auto-fixes on commit)
- **mypy** (v1.13.0): Strict type checking

All checks must pass before commits succeed. Use `git commit --no-verify` only for legitimate edge cases.

### Running Checks Manually

```bash
# Run all checks on staged files
pre-commit run

# Run all checks on all files
pre-commit run --all-files

# Run specific tools
ruff check --fix .
ruff format .
mypy src/
```

### Version Synchronization

**Important**: Keep ruff/mypy versions identical in:
- `pyproject.toml` (`[dependency-groups] dev`)
- `.pre-commit-config.yaml` (`rev:` fields)

When upgrading tools:
1. Update version in both files
2. Run `uv sync --group dev`
3. Run `pre-commit run --all-files` to verify

### Spell Checking

The project uses `.cspell.json` for spell-checking configuration. This file contains:
- Project-specific terms (e.g., "startrek", "starwars", "scifi")
- Technical terms (e.g., "bothify")
- Universe-specific terms (e.g., "Starfleet", "Holodeck")

**Adding new terms:**
If you add new sci-fi terms that trigger spell-check warnings, add them to `.cspell.json`:

```json
{
  "words": [
    "existing-term",
    "your-new-term"
  ]
}
```

Most editors with spell-check extensions (VS Code, IntelliJ, Neovim) will automatically read this file.

## Adding New Universes

1. Create `data/{universe}.py` with a data class containing all required attributes
2. Add to `UNIVERSES` registry in `provider.py`
3. Add test coverage in `tests/test_universes.py`

**Required attributes** (see `UniverseAttribute` enum):

- `FIRST_NAMES_MALE`, `FIRST_NAMES_FEMALE`
- `LAST_NAMES_MALE`, `LAST_NAMES_FEMALE`
- `RANKS`
- `STARSHIPS`, `STARSHIP_REGISTRIES`, `STARSHIP_CLASSES`
- `BASE_LOCATIONS`, `LOCATION_DETAILS`
- `LANGUAGES`, `QUOTES`
- `CANONICAL_CHARACTERS`

**Example:**

```python
# data/starwars.py
from .domains import CanonicalCharacter

class StarWarsData:
    FIRST_NAMES_MALE = ["Luke", "Han", "Obi-Wan", ...]
    FIRST_NAMES_FEMALE = ["Leia", "Rey", "Padmé", ...]
    # ... all required attributes

    CANONICAL_CHARACTERS = [
        CanonicalCharacter(
            first_name="Luke",
            last_name="Skywalker",
            rank="Jedi Knight",
            starship="X-Wing",
            quotes=["May the Force be with you."]
        ),
        # ...
    ]

# provider.py
from .data.starwars import StarWarsData

UNIVERSES = {
    'startrek': StarTrekData(),
    'starwars': StarWarsData(),  # Add new universe
}
```

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=faker_galactic --cov-report=term-missing
```

All new features require test coverage. Tests should cover:
- Happy path
- Edge cases
- Error conditions
- Universe-specific data validation

## Pull Request Process

1. Create a feature branch from `master`
2. Make your changes
3. Ensure all checks pass (`pre-commit run --all-files`)
4. Ensure tests pass (`pytest`)
5. Update documentation if needed
6. Create a pull request with a clear description

## Code Style

- Follow PEP 8 (enforced by ruff)
- Use type hints on all functions (enforced by mypy strict mode)
- Use modern Python 3.13+ syntax (`X | Y` instead of `Union[X, Y]`)
- Docstrings for all public functions, classes, and modules
- Keep functions focused and single-purpose

## Questions?

Open an issue on GitHub if you have questions or need help contributing.
