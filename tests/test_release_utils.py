"""Tests for release_utils business logic module."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from faker_galactic import release_utils


class TestParseVersion:
    """Tests for parse_version function."""

    @pytest.mark.parametrize(
        "version,expected",
        [
            ("1.0.0", (1, 0, 0)),
            ("2.5.3", (2, 5, 3)),
            ("10.99.99", (10, 99, 99)),
        ],
    )
    def test_parse_version_valid(
        self, version: str, expected: tuple[int, int, int]
    ) -> None:
        """Test parsing valid version strings."""
        result = release_utils.parse_version(version)
        assert result == expected

    @pytest.mark.parametrize(
        "invalid_version",
        [
            "1.0",  # Missing patch
            "1.a.0",  # Non-numeric
            "v1.0.0",  # Has prefix
            "1.0.0.0",  # Too many parts
        ],
    )
    def test_parse_version_invalid(self, invalid_version: str) -> None:
        """Test parsing invalid version strings."""
        with pytest.raises(ValueError, match="Invalid version format"):
            release_utils.parse_version(invalid_version)


class TestCalculateVersions:
    """Tests for calculate_versions function."""

    @pytest.mark.parametrize(
        "current,expected_patch,expected_minor,expected_major",
        [
            ("1.0.0", "1.0.1", "1.1.0", "2.0.0"),
            ("2.5.3", "2.5.4", "2.6.0", "3.0.0"),
            ("10.99.99", "10.99.100", "10.100.0", "11.0.0"),
        ],
    )
    def test_calculate_versions_valid(
        self,
        current: str,
        expected_patch: str,
        expected_minor: str,
        expected_major: str,
    ) -> None:
        """Test version calculation with valid inputs."""
        versions = release_utils.calculate_versions(current)
        assert versions["patch"] == expected_patch
        assert versions["minor"] == expected_minor
        assert versions["major"] == expected_major

    @pytest.mark.parametrize(
        "invalid_version",
        [
            "1.0",  # Missing patch
            "1.a.0",  # Non-numeric
            "v1.0.0",  # Has prefix
            "1.0.0.0",  # Too many parts
        ],
    )
    def test_calculate_versions_invalid(self, invalid_version: str) -> None:
        """Test version calculation with invalid formats."""
        with pytest.raises(ValueError):
            release_utils.calculate_versions(invalid_version)


class TestParseCommitMessage:
    """Tests for parse_commit_message function."""

    @pytest.mark.parametrize(
        "commit,expected_message,expected_pr",
        [
            ("abc1234 Add new feature (#123)", "Add new feature", "123"),
            ("def5678 Fix typo in README", "Fix typo in README", None),
            ("abc1234 Merge PRs (#100) and (#200)", "Merge PRs (#100) and", "200"),
            ("not-a-valid-format", "not-a-valid-format", None),
        ],
    )
    def test_parse_commit_message(
        self, commit: str, expected_message: str, expected_pr: str | None
    ) -> None:
        """Test parsing various commit message formats."""
        message, pr_num = release_utils.parse_commit_message(commit)
        assert message == expected_message
        assert pr_num == expected_pr


class TestFormatChangelogEntry:
    """Tests for format_changelog_entry function."""

    def test_format_changelog_entry_with_pr_links(self) -> None:
        """Test changelog generation with PR links."""
        commits = [
            "abc1234 Add new feature (#123)",
            "def5678 Fix bug in parser (#456)",
            "ghi9012 Update documentation",
        ]

        result = release_utils.format_changelog_entry(
            "1.2.0", commits, "owner", "repo", date="2024-12-01"
        )

        assert "## [1.2.0] - 2024-12-01" in result
        assert (
            "- Add new feature [#123](https://github.com/owner/repo/pull/123)" in result
        )
        assert (
            "- Fix bug in parser [#456](https://github.com/owner/repo/pull/456)"
            in result
        )
        assert "- ghi9012 Update documentation" in result

    def test_format_changelog_entry_no_commits(self) -> None:
        """Test changelog generation with no commits."""
        result = release_utils.format_changelog_entry(
            "1.2.0", [], "owner", "repo", date="2024-12-01"
        )

        assert "## [1.2.0] - 2024-12-01" in result
        assert result.count("\n") == 1  # Only header line

    @patch("faker_galactic.release_utils.datetime")
    def test_format_changelog_entry_default_date(self, mock_datetime: Mock) -> None:
        """Test that default date uses datetime.now()."""
        mock_datetime.now.return_value = datetime(2024, 12, 15)
        commits = ["abc1234 Test commit (#1)"]

        result = release_utils.format_changelog_entry("1.0.0", commits, "owner", "repo")

        assert "## [1.0.0] - 2024-12-15" in result


class TestGenerateVersionAnchor:
    """Tests for generate_version_anchor function."""

    def test_generate_version_anchor_with_date(self) -> None:
        """Test anchor generation with explicit date."""
        anchor = release_utils.generate_version_anchor("1.2.0", date="2024-12-01")
        assert anchor == "120---2024-12-01"

    def test_generate_version_anchor_complex_version(self) -> None:
        """Test anchor generation with complex version."""
        anchor = release_utils.generate_version_anchor("10.99.5", date="2024-01-15")
        assert anchor == "10995---2024-01-15"

    @patch("faker_galactic.release_utils.datetime")
    def test_generate_version_anchor_default_date(self, mock_datetime: Mock) -> None:
        """Test that default date uses datetime.now()."""
        mock_datetime.now.return_value = datetime(2024, 12, 15)

        anchor = release_utils.generate_version_anchor("2.0.0")

        assert anchor == "200---2024-12-15"


class TestExtractChangesFromEntry:
    """Tests for extract_changes_from_entry function."""

    def test_extract_changes_from_entry(self) -> None:
        """Test extracting changes from changelog entry."""
        entry = """## [1.2.0] - 2024-12-01

- Add new feature [#123](https://github.com/owner/repo/pull/123)
- Fix bug in parser [#456](https://github.com/owner/repo/pull/456)
- Update documentation"""

        result = release_utils.extract_changes_from_entry(entry)

        assert "## [1.2.0]" not in result
        assert "- Add new feature" in result
        assert "- Fix bug in parser" in result
        assert "- Update documentation" in result

    def test_extract_changes_from_entry_empty_lines(self) -> None:
        """Test that empty lines are filtered out."""
        entry = """## [1.2.0] - 2024-12-01

- Change 1

- Change 2"""

        result = release_utils.extract_changes_from_entry(entry)

        # Should not include the header or standalone empty lines
        assert "## [1.2.0]" not in result
        assert "- Change 1" in result
        assert "- Change 2" in result
