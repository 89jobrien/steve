"""Regression tests for the frontmatter repair scripts."""

import importlib.util
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import ModuleType

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]


def load_script(name: str) -> ModuleType:
    """Load a repair script without letting import-time work touch the repository."""
    script_path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, script_path)
    assert spec is not None
    assert spec.loader is not None

    previous_cwd = Path.cwd()
    with TemporaryDirectory() as temporary_directory:
        os.chdir(temporary_directory)
        try:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        finally:
            os.chdir(previous_cwd)
    return module


FIX_FRONTMATTER = load_script("fix_frontmatter")
FIX_FRONTMATTER_STRICT = load_script("fix_frontmatter_strict")
SCRIPTS = (FIX_FRONTMATTER, FIX_FRONTMATTER_STRICT)


def run_fix(module: ModuleType, file_path: Path) -> bool:
    """Call either script's fix function through its public signature."""
    if module is FIX_FRONTMATTER_STRICT:
        return module.fix_file(file_path, "Agent")
    return module.fix_file(file_path)


def read_frontmatter(file_path: Path) -> dict[str, object]:
    """Read the first YAML frontmatter block from a repaired file."""
    content = file_path.read_text(encoding="utf-8")
    frontmatter = content.split("---\n", 2)[1]
    return yaml.safe_load(frontmatter)


@pytest.mark.parametrize("module", SCRIPTS)
def test_extracts_description_after_heading(module: ModuleType, tmp_path: Path) -> None:
    component = tmp_path / "example.md"
    component.write_text(
        "# Example\n\nThis paragraph describes the component.\n\nMore details.\n",
        encoding="utf-8",
    )

    assert run_fix(module, component)
    assert read_frontmatter(component)["description"] == "This paragraph describes the component."


@pytest.mark.parametrize(
    ("module", "expected"),
    [
        (FIX_FRONTMATTER, None),
        (FIX_FRONTMATTER_STRICT, "A useful paragraph without a heading."),
    ],
)
def test_handles_body_without_heading(
    module: ModuleType, expected: str | None, tmp_path: Path
) -> None:
    component = tmp_path / "example.md"
    component.write_text("A useful paragraph without a heading.\n", encoding="utf-8")

    assert run_fix(module, component)
    expected_description = expected or f"Component in {tmp_path.name}"
    assert read_frontmatter(component)["description"] == expected_description


@pytest.mark.parametrize("module", SCRIPTS)
def test_malformed_yaml_is_left_in_the_body(module: ModuleType, tmp_path: Path) -> None:
    content = "---\ninvalid: yaml: [unclosed\n---\n\n# Example\n\nBody paragraph.\n"
    blocks, body = module.parse_all_frontmatter(content)

    assert blocks == []
    assert body == content


@pytest.mark.parametrize("module", SCRIPTS)
def test_merges_duplicate_frontmatter_blocks(module: ModuleType, tmp_path: Path) -> None:
    component = tmp_path / "example.md"
    component.write_text(
        "---\nname: example\n---\n\n---\ndescription: Combined description\n---\n\nBody.\n",
        encoding="utf-8",
    )

    assert run_fix(module, component)
    assert read_frontmatter(component) == {
        "name": "example",
        "description": "Combined description",
    }


@pytest.mark.parametrize("module", SCRIPTS)
def test_second_execution_is_idempotent(module: ModuleType, tmp_path: Path) -> None:
    component = tmp_path / "example.md"
    component.write_text("# Example\n\nThis paragraph describes the component.\n", encoding="utf-8")

    assert run_fix(module, component)
    first_result = component.read_text(encoding="utf-8")

    assert not run_fix(module, component)
    assert component.read_text(encoding="utf-8") == first_result
