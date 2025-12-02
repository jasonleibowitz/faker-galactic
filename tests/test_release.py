"""Tests for the release script."""

# Import the release script functions
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import release


class TestCalculateVersions:
    """Tests for version calculation functions."""

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
        versions = release.calculate_versions(current)
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
        with pytest.raises(SystemExit):
            release.calculate_versions(invalid_version)


class TestParseCommitMessage:
    """Tests for commit message parsing."""

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
        message, pr_num = release.parse_commit_message(commit)
        assert message == expected_message
        assert pr_num == expected_pr


class TestGenerateChangelogEntry:
    """Tests for changelog entry generation."""

    @patch("release.datetime")
    @patch("release.get_repo_info")
    def test_generate_changelog_entry_with_pr_links(
        self, mock_get_repo: Mock, mock_datetime: Mock
    ) -> None:
        """Test changelog generation with PR links."""
        mock_datetime.now.return_value = datetime(2024, 12, 1)
        mock_get_repo.return_value = ("owner", "repo")

        commits = [
            "abc1234 Add new feature (#123)",
            "def5678 Fix bug in parser (#456)",
            "ghi9012 Update documentation",
        ]

        result = release.generate_changelog_entry("1.2.0", commits)

        assert "## [1.2.0] - 2024-12-01" in result
        assert (
            "- Add new feature [#123](https://github.com/owner/repo/pull/123)" in result
        )
        assert (
            "- Fix bug in parser [#456](https://github.com/owner/repo/pull/456)"
            in result
        )
        # Commit without PR number includes the whole commit line
        assert "- ghi9012 Update documentation" in result

    @patch("release.get_repo_info")
    @patch("release.datetime")
    def test_generate_changelog_entry_no_commits(
        self, mock_datetime: Mock, mock_get_repo: Mock
    ) -> None:
        """Test changelog generation with no commits."""
        mock_datetime.now.return_value = datetime(2024, 12, 1)
        mock_get_repo.return_value = ("owner", "repo")

        result = release.generate_changelog_entry("1.2.0", [])

        assert "## [1.2.0] - 2024-12-01" in result
        assert result.count("\n") == 1  # Only header line


class TestGetCurrentVersion:
    """Tests for reading version from pyproject.toml."""

    @patch("release.Path")
    def test_get_current_version_success(self, mock_path: Mock) -> None:
        """Test reading version from pyproject.toml."""
        mock_content = """
[project]
name = "faker-galactic"
version = "1.2.3"
description = "A test project"
"""
        mock_path.return_value.read_text.return_value = mock_content
        version = release.get_current_version()
        assert version == "1.2.3"

    @patch("release.Path")
    def test_get_current_version_no_version_field(self, mock_path: Mock) -> None:
        """Test error when version field is missing."""
        mock_content = """
[project]
name = "faker-galactic"
description = "A test project"
"""
        mock_path.return_value.read_text.return_value = mock_content
        with pytest.raises(SystemExit):
            release.get_current_version()


class TestGetRepoInfo:
    """Tests for extracting repo info from git remote."""

    @pytest.mark.parametrize(
        "remote_url,expected_owner,expected_repo",
        [
            ("https://github.com/owner/repo.git\n", "owner", "repo"),
            ("git@github.com:owner/repo.git\n", "owner", "repo"),
            ("https://github.com/test-org/my-project.git\n", "test-org", "my-project"),
        ],
    )
    @patch("subprocess.run")
    def test_get_repo_info_valid_urls(
        self,
        mock_run: Mock,
        remote_url: str,
        expected_owner: str,
        expected_repo: str,
    ) -> None:
        """Test extracting repo info from various valid URL formats."""
        mock_run.return_value = Mock(stdout=remote_url, returncode=0)
        owner, repo = release.get_repo_info()
        assert owner == expected_owner
        assert repo == expected_repo

    @patch("subprocess.run")
    def test_get_repo_info_invalid_url(self, mock_run: Mock) -> None:
        """Test error with invalid remote URL."""
        mock_run.return_value = Mock(stdout="invalid-url\n", returncode=0)
        with pytest.raises(SystemExit):
            release.get_repo_info()


class TestGetLastReleaseTag:
    """Tests for getting the last release tag."""

    @patch("subprocess.run")
    def test_get_last_release_tag_exists(self, mock_run: Mock) -> None:
        """Test getting last release tag when it exists."""
        mock_run.return_value = Mock(stdout="v1.2.3\n", returncode=0)
        tag = release.get_last_release_tag()
        assert tag == "v1.2.3"

    @patch("subprocess.run")
    def test_get_last_release_tag_none_exists(self, mock_run: Mock) -> None:
        """Test when no release tag exists."""
        import subprocess

        mock_run.side_effect = subprocess.CalledProcessError(128, "git")
        tag = release.get_last_release_tag()
        assert tag is None


class TestGetCommitsSince:
    """Tests for getting commits since a tag."""

    @patch("subprocess.run")
    def test_get_commits_since_tag(self, mock_run: Mock) -> None:
        """Test getting commits since a specific tag."""
        mock_run.return_value = Mock(
            stdout="abc1234 Commit 1\ndef5678 Commit 2\n", returncode=0
        )
        commits = release.get_commits_since("v1.0.0")
        assert len(commits) == 2
        assert commits[0] == "abc1234 Commit 1"
        assert commits[1] == "def5678 Commit 2"

    @patch("subprocess.run")
    def test_get_commits_since_none(self, mock_run: Mock) -> None:
        """Test getting all commits when no tag provided."""
        mock_run.return_value = Mock(stdout="abc1234 Commit 1\n", returncode=0)
        commits = release.get_commits_since(None)
        assert len(commits) == 1
        mock_run.assert_called_once()
        # Verify it doesn't include a tag in the git log command
        call_args = mock_run.call_args[0][0]
        assert ".." not in " ".join(call_args)
