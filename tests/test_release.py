"""Tests for the release script I/O operations.

Business logic tests are in test_release_utils.py.
These tests focus on I/O wrapper functions that call git, read files, etc.
"""

# Import the release script functions
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import release


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


class TestGenerateChangelogEntry:
    """Integration test for generate_changelog_entry wrapper."""

    @patch("release.get_repo_info")
    def test_generate_changelog_entry_integration(self, mock_get_repo: Mock) -> None:
        """Test that generate_changelog_entry correctly wraps utility function."""
        mock_get_repo.return_value = ("owner", "repo")
        commits = ["abc1234 Add feature (#123)"]

        result = release.generate_changelog_entry("1.0.0", commits)

        # Verify it calls get_repo_info
        mock_get_repo.assert_called_once()
        # Verify result contains expected content
        assert "## [1.0.0]" in result
        assert "Add feature" in result
        assert "#123" in result
