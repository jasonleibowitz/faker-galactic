#!/usr/bin/env python3
"""Interactive release preparation script."""

import re
import sys
from pathlib import Path


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


if __name__ == "__main__":
    current = get_current_version()
    print(f"Current version: {current}")
    versions = calculate_versions(current)
    print(f"Patch: {versions['patch']}")
    print(f"Minor: {versions['minor']}")
    print(f"Major: {versions['major']}")
