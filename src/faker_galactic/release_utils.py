"""Pure business logic functions for release automation.

This module contains testable functions with no I/O dependencies.
All file operations, git commands, and user interactions are handled
in scripts/release.py which imports these utilities.
"""

import re
from datetime import datetime


def parse_version(version: str) -> tuple[int, int, int]:
    """Parse semver string into (major, minor, patch).

    Args:
        version: Semantic version string (e.g., "1.2.3")

    Returns:
        Tuple of (major, minor, patch) integers

    Raises:
        ValueError: If version format is invalid
    """
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version)
    if not match:
        raise ValueError(f"Invalid version format: {version}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def calculate_versions(current: str) -> dict[str, str]:
    """Calculate patch, minor, major versions from current version.

    Args:
        current: Current semantic version string

    Returns:
        Dictionary with 'patch', 'minor', and 'major' version strings

    Raises:
        ValueError: If current version format is invalid
    """
    major, minor, patch = parse_version(current)
    return {
        "patch": f"{major}.{minor}.{patch + 1}",
        "minor": f"{major}.{minor + 1}.0",
        "major": f"{major + 1}.0.0",
    }


def parse_commit_message(commit: str) -> tuple[str, str | None]:
    """Parse git commit line into message and PR number.

    Expects format: "abc1234 Commit message (#123)"

    Args:
        commit: Git commit line with hash and message

    Returns:
        Tuple of (message, pr_number). PR number is None if not present.
    """
    match = re.match(r"^[a-f0-9]+\s+(.+?)(?:\s+\(#(\d+)\))?$", commit)
    if not match:
        return commit, None
    return match.group(1), match.group(2)


def format_changelog_entry(
    version: str, commits: list[str], owner: str, repo: str, date: str | None = None
) -> str:
    """Generate CHANGELOG entry from commits.

    Args:
        version: Version string for the release
        commits: List of commit strings from git log
        owner: GitHub repository owner
        repo: GitHub repository name
        date: Release date (defaults to today if None)

    Returns:
        Formatted changelog entry string
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    lines = [f"## [{version}] - {date}\n"]

    for commit in commits:
        message, pr_num = parse_commit_message(commit)
        if pr_num:
            pr_link = f"[#{pr_num}](https://github.com/{owner}/{repo}/pull/{pr_num})"
            lines.append(f"- {message} {pr_link}")
        else:
            lines.append(f"- {message}")

    return "\n".join(lines)


def generate_version_anchor(version: str, date: str | None = None) -> str:
    """Generate GitHub-compatible anchor for version header.

    Converts "## [1.2.0] - 2024-12-01" into "#120---2024-12-01"

    Args:
        version: Version string
        date: Release date (defaults to today if None)

    Returns:
        Anchor string for linking to changelog section
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    return f"{version.replace('.', '')}---{date}"


def extract_changes_from_entry(changelog_entry: str) -> str:
    """Extract change list from changelog entry (without header).

    Args:
        changelog_entry: Full changelog entry including header

    Returns:
        Just the bullet-pointed changes without the header line
    """
    lines = changelog_entry.split("\n")
    return "\n".join(line for line in lines[1:] if line.strip())
