"""Tests for add_metadata.py - Component metadata management."""

from scripts.add_metadata import parse_frontmatter, update_frontmatter


class TestParseFrontmatter:
    """Tests for parse_frontmatter function."""

    def test_parse_valid_frontmatter(self) -> None:
        """Test parsing valid YAML frontmatter."""
        content = """---
name: test-component
description: A test component
---

# Body content
"""
        frontmatter, body = parse_frontmatter(content)

        assert frontmatter["name"] == "test-component"
        assert frontmatter["description"] == "A test component"
        assert "# Body content" in body

    def test_parse_empty_frontmatter(self) -> None:
        """Test parsing empty frontmatter returns empty dict."""
        content = """---
---

Body only
"""
        frontmatter, body = parse_frontmatter(content)

        assert frontmatter == {}
        assert "Body only" in body

    def test_parse_no_frontmatter(self) -> None:
        """Test content without frontmatter returns empty dict and full content."""
        content = "# Just content\n\nNo frontmatter here"
        frontmatter, body = parse_frontmatter(content)

        assert frontmatter == {}
        assert body == content

    def test_parse_invalid_yaml(self) -> None:
        """Test invalid YAML returns empty dict."""
        content = """---
invalid: yaml: [unclosed
---

Body
"""
        frontmatter, _ = parse_frontmatter(content)

        assert frontmatter == {}


class TestUpdateFrontmatter:
    """Tests for update_frontmatter function."""

    def test_update_existing_frontmatter(self) -> None:
        """Test updating existing frontmatter with new values."""
        content = """---
name: original
description: Original description
---

Body content
"""
        updates = {"gist_url": "https://gist.github.com/test/123"}

        result = update_frontmatter(content, updates)

        assert "gist_url: https://gist.github.com/test/123" in result
        assert "name: original" in result
        assert "description: Original description" in result
        assert "Body content" in result

    def test_update_overwrites_existing_value(self) -> None:
        """Test that updates overwrite existing values."""
        content = """---
name: old-name
---

Body
"""
        updates = {"name": "new-name"}

        result = update_frontmatter(content, updates)

        assert "name: new-name" in result
        assert "old-name" not in result

    def test_update_no_frontmatter_creates_one(self) -> None:
        """Test updating content without frontmatter creates frontmatter."""
        content = "# Just a heading\n\nBody content"
        updates = {"name": "new-component"}

        result = update_frontmatter(content, updates)

        assert result.startswith("---\n")
        assert "name: new-component" in result
        # Body should still be present
        assert "# Just a heading" in result or "Body content" in result

    def test_update_multiple_values(self) -> None:
        """Test updating multiple values at once."""
        content = """---
name: test
---

Body
"""
        updates = {
            "gist_url": "https://gist.github.com/test/123",
            "version": "1.0.0",
            "author": "test-author",
        }

        result = update_frontmatter(content, updates)

        assert "gist_url:" in result
        assert "version:" in result
        assert "author:" in result
        assert "name: test" in result

    def test_update_empty_frontmatter(self) -> None:
        """Test updating empty frontmatter."""
        content = """---
---

Body
"""
        updates = {"name": "new-name"}

        result = update_frontmatter(content, updates)

        assert "name: new-name" in result
        assert "Body" in result


class TestAddMetadataIntegration:
    """Integration tests for add_metadata functionality."""

    def test_roundtrip_parse_update(self) -> None:
        """Test that parse + update produces valid frontmatter."""
        original = """---
name: test
description: Test description
---

# Content

Some body text here.
"""
        # Parse original
        frontmatter, _ = parse_frontmatter(original)
        assert frontmatter["name"] == "test"

        # Update with new field
        updated = update_frontmatter(original, {"gist_url": "https://example.com"})

        # Parse updated
        new_frontmatter, _ = parse_frontmatter(updated)

        # Verify all fields present
        assert new_frontmatter["name"] == "test"
        assert new_frontmatter["description"] == "Test description"
        assert new_frontmatter["gist_url"] == "https://example.com"
