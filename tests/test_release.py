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

    def test_calculate_versions_from_1_0_0(self) -> None:
        """Test version calculation from 1.0.0."""
        versions = release.calculate_versions("1.0.0")
        assert versions["patch"] == "1.0.1"
        assert versions["minor"] == "1.1.0"
        assert versions["major"] == "2.0.0"

    def test_calculate_versions_from_2_5_3(self) -> None:
        """Test version calculation from 2.5.3."""
        versions = release.calculate_versions("2.5.3")
        assert versions["patch"] == "2.5.4"
        assert versions["minor"] == "2.6.0"
        assert versions["major"] == "3.0.0"

    def test_calculate_versions_from_10_99_99(self) -> None:
        """Test version calculation with large numbers."""
        versions = release.calculate_versions("10.99.99")
        assert versions["patch"] == "10.99.100"
        assert versions["minor"] == "10.100.0"
        assert versions["major"] == "11.0.0"

    def test_calculate_versions_invalid_format(self) -> None:
        """Test version calculation with invalid format."""
        with pytest.raises(SystemExit):
            release.calculate_versions("1.0")

    def test_calculate_versions_non_numeric(self) -> None:
        """Test version calculation with non-numeric parts."""
        with pytest.raises(SystemExit):
            release.calculate_versions("1.a.0")


class TestParseCommitMessage:
    """Tests for commit message parsing."""

    def test_parse_commit_with_pr_number(self) -> None:
        """Test parsing commit message with PR number."""
        commit = "abc1234 Add new feature (#123)"
        message, pr_num = release.parse_commit_message(commit)
        assert message == "Add new feature"
        assert pr_num == "123"

    def test_parse_commit_without_pr_number(self) -> None:
        """Test parsing commit message without PR number."""
        commit = "abc1234 Fix typo in README"
        message, pr_num = release.parse_commit_message(commit)
        assert message == "Fix typo in README"
        assert pr_num is None

    def test_parse_commit_with_multiple_pr_numbers(self) -> None:
        """Test parsing commit with multiple PR numbers (takes last one)."""
        commit = "abc1234 Merge PRs (#100) and (#200)"
        message, pr_num = release.parse_commit_message(commit)
        assert message == "Merge PRs (#100) and"
        assert pr_num == "200"

    def test_parse_commit_malformed(self) -> None:
        """Test parsing malformed commit message."""
        commit = "not-a-valid-commit-format"
        message, pr_num = release.parse_commit_message(commit)
        # When regex doesn't match, returns whole commit and None
        assert message == commit
        assert pr_num is None


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

    @patch("subprocess.run")
    def test_get_repo_info_https_url(self, mock_run: Mock) -> None:
        """Test extracting repo info from HTTPS URL."""
        mock_run.return_value = Mock(
            stdout="https://github.com/owner/repo.git\n", returncode=0
        )
        owner, repo = release.get_repo_info()
        assert owner == "owner"
        assert repo == "repo"

    @patch("subprocess.run")
    def test_get_repo_info_ssh_url(self, mock_run: Mock) -> None:
        """Test extracting repo info from SSH URL."""
        mock_run.return_value = Mock(
            stdout="git@github.com:owner/repo.git\n", returncode=0
        )
        owner, repo = release.get_repo_info()
        assert owner == "owner"
        assert repo == "repo"

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
