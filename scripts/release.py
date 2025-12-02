#!/usr/bin/env python3
"""Interactive release preparation script."""

import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import questionary
import tomlkit


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


def get_last_release_tag() -> str | None:
    """Get the last release tag, or None if no tags exist."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def get_commits_since(tag: str | None) -> list[str]:
    """Get commit messages since tag (or all if tag is None)."""
    if tag:
        cmd = ["git", "log", f"{tag}..HEAD", "--oneline"]
    else:
        cmd = ["git", "log", "--oneline"]

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip().split("\n") if result.stdout.strip() else []


def parse_commit_message(commit: str) -> tuple[str, str | None]:
    """Parse commit into (message, pr_number)."""
    # Format: "abc1234 Commit message (#123)"
    match = re.match(r"^[a-f0-9]+\s+(.+?)(?:\s+\(#(\d+)\))?$", commit)
    if not match:
        return commit, None
    return match.group(1), match.group(2)


def get_repo_info() -> tuple[str, str]:
    """Get GitHub owner/repo from git remote."""
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        check=True,
    )
    url = result.stdout.strip()

    # Parse: git@github.com:owner/repo.git or https://github.com/owner/repo.git
    match = re.search(r"github\.com[:/]([^/]+)/([^/\.]+)", url)
    if not match:
        print("❌ Could not parse GitHub repo from remote URL")
        sys.exit(1)

    return match.group(1), match.group(2)


def generate_changelog_entry(version: str, commits: list[str]) -> str:
    """Generate CHANGELOG entry from commits."""
    owner, repo = get_repo_info()
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


def preview_changelog(entry: str) -> bool:
    """Show changelog entry and get confirmation."""
    print("\n📝 Generated CHANGELOG entry:\n")
    print(entry)
    print()

    confirm = questionary.confirm("Does this look good?", default=True).ask()

    return confirm if confirm is not None else False


def update_version_in_pyproject(new_version: str) -> None:
    """Update version in pyproject.toml using tomlkit to preserve formatting."""
    pyproject = Path("pyproject.toml")

    try:
        content = pyproject.read_text()
        doc = tomlkit.parse(content)
    except Exception as e:
        print(f"❌ Failed to read/parse pyproject.toml: {e}")
        sys.exit(1)

    # Access project section (tomlkit returns Table objects, not dict)
    project = doc.get("project")
    if project is None:
        print("❌ Could not find [project] section in pyproject.toml")
        sys.exit(1)

    project["version"] = new_version

    try:
        pyproject.write_text(tomlkit.dumps(doc))
    except Exception as e:
        print(f"❌ Failed to write pyproject.toml: {e}")
        sys.exit(1)

    print(f"✓ Updated version in pyproject.toml to {new_version}")


def update_changelog(entry: str) -> None:
    """Prepend new entry to CHANGELOG.md."""
    changelog = Path("CHANGELOG.md")

    if not changelog.exists():
        print("❌ CHANGELOG.md not found")
        sys.exit(1)

    try:
        content = changelog.read_text()
    except Exception as e:
        print(f"❌ Failed to read CHANGELOG.md: {e}")
        sys.exit(1)

    lines = content.split("\n")
    insert_idx = 0
    found_version = False

    # Find the first existing version entry
    for i, line in enumerate(lines):
        if line.startswith("## ["):
            insert_idx = i
            found_version = True
            break

    # If no existing versions, find end of header section
    if not found_version:
        # Skip past title and description to first blank line
        for i, line in enumerate(lines):
            if i > 0 and line.strip() == "" and lines[i - 1].strip() != "":
                insert_idx = i + 1
                break
        else:
            # No blank line found, append at end
            insert_idx = len(lines)

    # Insert new entry
    new_lines = lines[:insert_idx] + [entry, ""] + lines[insert_idx:]

    try:
        changelog.write_text("\n".join(new_lines))
    except Exception as e:
        print(f"❌ Failed to write CHANGELOG.md: {e}")
        sys.exit(1)

    print("✓ Updated CHANGELOG.md")


def verify_on_master() -> None:
    """Check current branch is master, exit if not."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
        )
        current_branch = result.stdout.strip()
        if current_branch != "master":
            print(f"❌ Must be on master branch (currently on {current_branch})")
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to get current branch: {e}")
        sys.exit(1)


def verify_clean_working_dir() -> None:
    """Check no uncommitted changes, exit if dirty."""
    try:
        result = subprocess.run(
            ["git", "diff-index", "--quiet", "HEAD", "--"],
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            print("❌ You have uncommitted changes. Commit or stash them first.")
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to check working directory status: {e}")
        sys.exit(1)


def pull_latest() -> None:
    """Pull latest from origin/master."""
    try:
        print("📥 Pulling latest from origin/master...")
        subprocess.run(
            ["git", "pull", "origin", "master"],
            check=True,
        )
        print("✓ Pulled latest changes")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to pull from origin/master: {e}")
        sys.exit(1)


def create_release_branch(version: str) -> None:
    """Create branch release/vX.X.X and check it out."""
    branch = f"release/v{version}"
    try:
        subprocess.run(
            ["git", "checkout", "-b", branch],
            check=True,
        )
        print(f"✓ Created and checked out branch {branch}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create branch {branch}: {e}")
        sys.exit(1)


def commit_changes(version: str) -> None:
    """Stage pyproject.toml and CHANGELOG.md, commit with message."""
    try:
        # Stage files
        subprocess.run(
            ["git", "add", "pyproject.toml", "CHANGELOG.md"],
            check=True,
        )

        # Commit with message
        commit_msg = f"Prepare release v{version}"
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            check=True,
        )
        print(f"✓ Committed changes: {commit_msg}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to commit changes: {e}")
        sys.exit(1)


def push_branch() -> None:
    """Push current branch to origin with -u flag."""
    try:
        # Get current branch name
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
        )
        branch = result.stdout.strip()

        # Push with upstream tracking
        subprocess.run(
            ["git", "push", "-u", "origin", branch],
            check=True,
        )
        print(f"✓ Pushed branch {branch} to origin")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to push branch: {e}")
        sys.exit(1)


def create_release_pr(version: str, branch: str) -> None:
    """Create PR using template with version placeholders replaced."""
    template_path = Path(".github/RELEASE_PULL_REQUEST_TEMPLATE.md")

    if not template_path.exists():
        print(f"❌ Template not found: {template_path}")
        sys.exit(1)

    try:
        # Read template
        template_content = template_path.read_text()

        # Generate version anchor (e.g., "120" for v1.2.0)
        version_anchor = version.replace(".", "")

        # Replace placeholders
        pr_body = template_content.replace("{{ VERSION }}", version)
        pr_body = pr_body.replace("{{ VERSION_ANCHOR }}", version_anchor)

        # Create temporary file for PR body
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as temp_file:
            temp_file.write(pr_body)
            temp_file_path = temp_file.name

        try:
            # Create PR using gh CLI with template file
            result = subprocess.run(
                [
                    "gh",
                    "pr",
                    "create",
                    "--title",
                    f"Release v{version}",
                    "--body-file",
                    temp_file_path,
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            pr_url = result.stdout.strip()
            print(f"✓ Created PR: {pr_url}")

        finally:
            # Clean up temporary file
            Path(temp_file_path).unlink(missing_ok=True)

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create PR: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error creating PR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Pre-flight checks
    verify_on_master()
    verify_clean_working_dir()
    pull_latest()

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

    # Generate changelog
    last_tag = get_last_release_tag()
    commits = get_commits_since(last_tag)

    if not commits or commits == [""]:
        print("\n⚠️  No commits found since last release.")
        date = datetime.now().strftime("%Y-%m-%d")
        changelog_entry = f"## [{new_version}] - {date}\n\n- No changes"
    else:
        changelog_entry = generate_changelog_entry(new_version, commits)

    # Preview and confirm
    if not preview_changelog(changelog_entry):
        print("\n❌ Release cancelled. Edit CHANGELOG.md manually and re-run.")
        sys.exit(0)

    # Update files
    print("\n📝 Updating files...")
    update_version_in_pyproject(new_version)
    update_changelog(changelog_entry)

    # Git operations
    print("\n🚀 Creating release branch and committing changes...")
    create_release_branch(new_version)
    commit_changes(new_version)
    push_branch()

    # Get branch name for PR creation
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
        check=True,
    )
    branch_name = result.stdout.strip()

    # Create PR
    print("\n📝 Creating release PR...")
    create_release_pr(new_version, branch_name)

    print(f"\n✅ Release v{new_version} PR created!")
    print("\nNext steps:")
    print("  1. Review the PR")
    print("  2. Merge when ready")
    print("  3. GitHub Actions will handle tagging and publishing to PyPI")
