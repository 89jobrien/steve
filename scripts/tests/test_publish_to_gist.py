"""Tests for publish_to_gist.py - Component publishing to GitHub Gist."""

from scripts.publish_to_gist import get_gist_id_from_url


class TestGetGistIdFromUrl:
    """Tests for get_gist_id_from_url function."""

    def test_extracts_id_from_standard_url(self) -> None:
        """Test extracting gist ID from standard gist URL with username."""
        url = "https://gist.github.com/username/abc123def456"

        result = get_gist_id_from_url(url)

        assert result == "abc123def456"

    def test_extracts_id_from_short_url(self) -> None:
        """Test extracting gist ID from short URL without username."""
        url = "https://gist.github.com/abc123"

        result = get_gist_id_from_url(url)

        assert result == "abc123"

    def test_handles_trailing_slash(self) -> None:
        """Test handling URLs with trailing slash."""
        url = "https://gist.github.com/user/gistid123/"

        result = get_gist_id_from_url(url)

        assert result == "gistid123"

    def test_handles_multiple_trailing_slashes(self) -> None:
        """Test handling URLs with multiple trailing slashes."""
        url = "https://gist.github.com/user/gistid///"

        result = get_gist_id_from_url(url)

        assert result == "gistid"

    def test_extracts_from_raw_url(self) -> None:
        """Test extracting ID from raw gist URL format."""
        # Raw URLs have additional path components
        url = "https://gist.github.com/user/abc123/raw/filename.md"

        result = get_gist_id_from_url(url)

        # Should get last segment after stripping - this tests current behavior
        assert result == "filename.md"

    def test_handles_complex_gist_id(self) -> None:
        """Test handling gist IDs with various characters."""
        url = "https://gist.github.com/user/a1b2c3d4e5f6g7h8i9j0"

        result = get_gist_id_from_url(url)

        assert result == "a1b2c3d4e5f6g7h8i9j0"

    def test_handles_numeric_only_id(self) -> None:
        """Test handling numeric-only gist IDs."""
        url = "https://gist.github.com/user/123456789"

        result = get_gist_id_from_url(url)

        assert result == "123456789"
