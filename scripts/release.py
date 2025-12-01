#!/usr/bin/env python3
"""Interactive release preparation script."""

import re
import sys
from pathlib import Path

import questionary


def get_current_version() -> str:
    """Read current version from pyproject.toml."""
    pyproject = Path("pyproject.toml")
    content = pyproject.read_text()
    match = re.search(r'^version = "([^"]+)"', content, re.MULTILINE)
    if not match:
        print("❌ Could not find version in pyproject.toml")
        sys.exit(1)
    return match.group(1)


def parse_version(version: str) -> tuple[int, int, int]:
    """Parse semver string into (major, minor, patch)."""
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version)
    if not match:
        print(f"❌ Invalid version format: {version}")
        sys.exit(1)
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def calculate_versions(current: str) -> dict[str, str]:
    """Calculate patch, minor, major versions from current."""
    major, minor, patch = parse_version(current)
    return {
        "patch": f"{major}.{minor}.{patch + 1}",
        "minor": f"{major}.{minor + 1}.0",
        "major": f"{major + 1}.0.0",
    }


def show_warning() -> bool:
    """Show warning and get confirmation."""
    print("\n⚠️  You are about to create a public release PR.\n")
    print("This will:")
    print("  - Create a release branch")
    print("  - Update version and CHANGELOG")
    print("  - Push to origin and open a PR\n")

    confirm = questionary.confirm("Continue?", default=False).ask()

    return confirm if confirm is not None else False


def select_version(current: str, versions: dict[str, str]) -> str | None:
    """Show version selection menu."""
    print(f"\nCurrent version: {current}\n")

    choices = [
        questionary.Choice(
            f"patch ({versions['patch']}) - Bug fixes, no new features",
            value="patch",
        ),
        questionary.Choice(
            f"minor ({versions['minor']}) - New features, backwards compatible",
            value="minor",
        ),
        questionary.Choice(
            f"major ({versions['major']}) - Breaking changes", value="major"
        ),
    ]

    bump_type = questionary.select("Select version bump:", choices=choices).ask()

    if bump_type is None:
        return None

    return versions[bump_type]


if __name__ == "__main__":
    # Show warning
    if not show_warning():
        print("\n❌ Release cancelled.")
        sys.exit(0)

    # Get version selection
    current = get_current_version()
    versions = calculate_versions(current)
    new_version = select_version(current, versions)

    if new_version is None:
        print("\n❌ Release cancelled.")
        sys.exit(0)

    print(f"\n✓ Selected version: {new_version}")
