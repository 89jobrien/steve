"""Tests for build_index.py - Component index builder."""

from pathlib import Path

from scripts.build_index import (
    build_index,
    build_index_incremental,
    get_file_hash,
    load_cache,
    parse_frontmatter,
    save_cache,
    scan_directory,
)


class TestParseFrontmatter:
    """Tests for parse_frontmatter function."""

    def test_parse_valid_frontmatter(self) -> None:
        """Test parsing valid YAML frontmatter."""
        content = """---
name: test-agent
description: A test agent
tools: Read, Write
---

# Body content here
"""
        frontmatter, body = parse_frontmatter(content)

        assert frontmatter["name"] == "test-agent"
        assert frontmatter["description"] == "A test agent"
        assert frontmatter["tools"] == "Read, Write"
        assert "# Body content here" in body

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
        content = "# Just a heading\n\nSome content"
        frontmatter, body = parse_frontmatter(content)

        assert frontmatter == {}
        assert body == content

    def test_parse_invalid_yaml_frontmatter(self) -> None:
        """Test invalid YAML in frontmatter returns empty dict."""
        content = """---
invalid: yaml: content: [
---

Body
"""
        frontmatter, body = parse_frontmatter(content)

        assert frontmatter == {}
        # When YAML is invalid, returns full content as body
        assert "invalid" in body or "Body" in body


class TestScanDirectory:
    """Tests for scan_directory function."""

    def test_scan_empty_directory(self, tmp_path: Path) -> None:
        """Test scanning an empty directory returns empty list."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        result = scan_directory(empty_dir, "agent", tmp_path)

        assert result == []

    def test_scan_nonexistent_directory(self, tmp_path: Path) -> None:
        """Test scanning nonexistent directory returns empty list."""
        nonexistent = tmp_path / "does_not_exist"

        result = scan_directory(nonexistent, "agent", tmp_path)

        assert result == []

    def test_scan_directory_with_agent_file(self, tmp_path: Path) -> None:
        """Test scanning directory with an agent markdown file."""
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        agent_file = agents_dir / "test-agent.md"
        agent_file.write_text("""---
name: test-agent
description: Test agent description
tools: Read, Write
model: sonnet
---

# Test Agent
""")

        result = scan_directory(agents_dir, "agent", tmp_path)

        assert len(result) == 1
        assert result[0]["name"] == "test-agent"
        assert result[0]["description"] == "Test agent description"
        assert result[0]["type"] == "agent"
        assert result[0]["tools"] == "Read, Write"
        assert result[0]["model"] == "sonnet"

    def test_scan_directory_skips_readme(self, tmp_path: Path) -> None:
        """Test that README.md files are skipped during scan."""
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir()

        readme = agents_dir / "README.md"
        readme.write_text("# Readme")

        agent = agents_dir / "agent.md"
        agent.write_text("""---
name: agent
description: An agent
---
Content
""")

        result = scan_directory(agents_dir, "agent", tmp_path)

        assert len(result) == 1
        assert result[0]["name"] == "agent"

    def test_scan_directory_with_skill_type(self, tmp_path: Path) -> None:
        """Test scanning skills via build_index adds skill-specific fields.

        Note: Skills are handled specially in build_index() rather than through
        scan_directory() because they need skill_dir context for has_* checks.
        """
        steve_dir = tmp_path / "steve"
        steve_dir.mkdir()
        (steve_dir / "agents").mkdir()
        (steve_dir / "commands").mkdir()
        (steve_dir / "hooks").mkdir()

        skills_dir = steve_dir / "skills"
        skills_dir.mkdir()

        skill_dir = skills_dir / "test-skill"
        skill_dir.mkdir()

        # Create subdirectories to test has_references, has_scripts, has_assets
        (skill_dir / "references").mkdir()
        (skill_dir / "scripts").mkdir()

        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("""---
name: test-skill
description: A test skill
---
Skill content
""")

        result = build_index(tmp_path)

        assert len(result["skills"]) == 1
        assert result["skills"][0]["has_references"] is True
        assert result["skills"][0]["has_scripts"] is True
        assert result["skills"][0]["has_assets"] is False


class TestBuildIndex:
    """Tests for build_index function."""

    def test_build_index_empty_repo(self, tmp_path: Path) -> None:
        """Test building index from empty repo structure."""
        steve_dir = tmp_path / "steve"
        steve_dir.mkdir()

        # Create empty directories
        (steve_dir / "agents").mkdir()
        (steve_dir / "commands").mkdir()
        (steve_dir / "skills").mkdir()
        (steve_dir / "hooks").mkdir()

        index = build_index(tmp_path)

        assert index["version"] == "1.0.0"
        assert index["agents"] == []
        assert index["commands"] == []
        assert index["skills"] == []
        assert index["hooks"] == []
        assert index["templates"] == []

    def test_build_index_with_agent(self, tmp_path: Path) -> None:
        """Test building index with an agent file."""
        steve_dir = tmp_path / "steve"
        agents_dir = steve_dir / "agents" / "core"
        agents_dir.mkdir(parents=True)

        agent_file = agents_dir / "test.md"
        agent_file.write_text("""---
name: test
description: Test agent
tools: Read
---
Content
""")

        # Create other required directories
        (steve_dir / "commands").mkdir()
        (steve_dir / "skills").mkdir()
        (steve_dir / "hooks").mkdir()

        index = build_index(tmp_path)

        assert len(index["agents"]) == 1
        assert index["agents"][0]["name"] == "test"


class TestIncrementalCaching:
    """Tests for incremental caching functions."""

    def test_get_file_hash(self, tmp_path: Path) -> None:
        """Test file hash generation based on mtime and size."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        hash1 = get_file_hash(test_file)
        assert isinstance(hash1, str)
        assert len(hash1) == 32  # MD5 hex digest length

        # Same file should produce same hash
        hash2 = get_file_hash(test_file)
        assert hash1 == hash2

    def test_save_and_load_cache(self, tmp_path: Path) -> None:
        """Test saving and loading cache."""
        cache_path = tmp_path / "test-cache.json"
        test_data = {"key": {"hash": "abc123", "data": {"name": "test"}}}

        save_cache(test_data, cache_path)
        loaded = load_cache(cache_path)

        assert loaded == test_data

    def test_load_cache_nonexistent(self, tmp_path: Path) -> None:
        """Test loading nonexistent cache returns empty dict."""
        cache_path = tmp_path / "nonexistent.json"

        result = load_cache(cache_path)

        assert result == {}

    def test_build_index_incremental_cold_cache(self, tmp_path: Path) -> None:
        """Test incremental build with cold cache (all misses)."""
        steve_dir = tmp_path / "steve"
        agents_dir = steve_dir / "agents" / "core"
        agents_dir.mkdir(parents=True)

        agent_file = agents_dir / "test.md"
        agent_file.write_text("""---
name: test
description: Test agent
tools: Read
---
Content
""")

        # Create other required directories
        (steve_dir / "commands").mkdir()
        (steve_dir / "skills").mkdir()
        (steve_dir / "hooks").mkdir()

        index, stats = build_index_incremental(tmp_path)

        assert len(index["agents"]) == 1
        assert stats["misses"] == 1
        assert stats["hits"] == 0

    def test_build_index_incremental_warm_cache(self, tmp_path: Path) -> None:
        """Test incremental build with warm cache (all hits)."""
        steve_dir = tmp_path / "steve"
        agents_dir = steve_dir / "agents" / "core"
        agents_dir.mkdir(parents=True)

        agent_file = agents_dir / "test.md"
        agent_file.write_text("""---
name: test
description: Test agent
tools: Read
---
Content
""")

        # Create other required directories
        (steve_dir / "commands").mkdir()
        (steve_dir / "skills").mkdir()
        (steve_dir / "hooks").mkdir()

        # First build populates cache
        build_index_incremental(tmp_path)

        # Second build should hit cache
        index, stats = build_index_incremental(tmp_path)

        assert len(index["agents"]) == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 0
