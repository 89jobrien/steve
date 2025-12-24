#!/usr/bin/env python3
"""
Benchmark different build_index implementations.

Tests four variations:
- A: Sequential (current implementation)
- B: ThreadPoolExecutor (parallel I/O)
- C: Async (asyncio + aiofiles)
- D: Incremental (hash-based caching)

Usage:
    uv run scripts/build_index_benchmark.py [--iterations 5]
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import re
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from typing import Any

import yaml


# Optional async dependency
try:
    import aiofiles

    HAS_AIOFILES = True
except ImportError:
    HAS_AIOFILES = False


# =============================================================================
# Shared Utilities
# =============================================================================


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Extract YAML frontmatter from markdown content."""
    frontmatter_pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(frontmatter_pattern, content, re.DOTALL)

    if match:
        frontmatter_str = match.group(1)
        body = match.group(2)
        try:
            frontmatter = yaml.safe_load(frontmatter_str) or {}
            return frontmatter, body
        except yaml.YAMLError:
            return {}, content
    return {}, content


def build_component_dict(
    file_path: Path,
    frontmatter: dict[str, Any],
    component_type: str,
    base_dir: Path,
) -> dict[str, Any]:
    """Build component dictionary from parsed data."""
    component = {
        "type": component_type,
        "path": str(file_path.relative_to(base_dir)),
        "name": frontmatter.get("name", file_path.stem),
        "description": frontmatter.get("description", ""),
    }

    if component_type == "agent":
        component.update(
            {
                "tools": frontmatter.get("tools", ""),
                "model": frontmatter.get("model", "sonnet"),
                "color": frontmatter.get("color", ""),
                "skills": frontmatter.get("skills", ""),
            }
        )
    elif component_type == "skill":
        component.update(
            {
                "has_references": (file_path.parent / "references").exists(),
                "has_scripts": (file_path.parent / "scripts").exists(),
                "has_assets": (file_path.parent / "assets").exists(),
            }
        )

    return component


def create_empty_index() -> dict[str, Any]:
    """Create empty index structure."""
    return {
        "version": "1.0.0",
        "generated_at": "",
        "agents": [],
        "commands": [],
        "skills": [],
        "hooks": [],
        "templates": [],
    }


# =============================================================================
# Variation A: Sequential (Current Implementation)
# =============================================================================


def scan_directory_sequential(
    directory: Path, component_type: str, base_dir: Path
) -> list[dict[str, Any]]:
    """Original sequential implementation."""
    components: list[dict[str, Any]] = []

    if not directory.exists():
        return components

    for file_path in directory.rglob("*.md"):
        if file_path.name == "README.md":
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
            frontmatter, _ = parse_frontmatter(content)
            component = build_component_dict(file_path, frontmatter, component_type, base_dir)
            components.append(component)
        except Exception:
            continue

    return components


def build_index_sequential(repo_root: Path) -> dict[str, Any]:
    """Variation A: Sequential processing."""
    steve_dir = repo_root / "steve"
    index = create_empty_index()

    # Scan agents
    agents_dir = steve_dir / "agents"
    for domain_dir in agents_dir.iterdir():
        if domain_dir.is_dir():
            index["agents"].extend(scan_directory_sequential(domain_dir, "agent", steve_dir))

    # Scan commands
    commands_dir = steve_dir / "commands"
    for category_dir in commands_dir.iterdir():
        if category_dir.is_dir():
            index["commands"].extend(scan_directory_sequential(category_dir, "command", steve_dir))

    # Scan skills
    skills_dir = steve_dir / "skills"
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir():
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                try:
                    content = skill_file.read_text(encoding="utf-8")
                    frontmatter, _ = parse_frontmatter(content)
                    component = {
                        "type": "skill",
                        "path": str(skill_file.relative_to(steve_dir)),
                        "name": frontmatter.get("name", skill_dir.name),
                        "description": frontmatter.get("description", ""),
                        "has_references": (skill_dir / "references").exists(),
                        "has_scripts": (skill_dir / "scripts").exists(),
                        "has_assets": (skill_dir / "assets").exists(),
                    }
                    index["skills"].append(component)
                except Exception:
                    pass

    # Scan hooks
    hooks_dir = steve_dir / "hooks"
    for hook_type_dir in hooks_dir.iterdir():
        if hook_type_dir.is_dir():
            index["hooks"].extend(scan_directory_sequential(hook_type_dir, "hook", steve_dir))

    # Scan templates
    templates_dir = steve_dir / "templates"
    if templates_dir.exists():
        index["templates"] = [
            {"type": "template", "path": str(f.relative_to(steve_dir)), "name": f.stem}
            for f in templates_dir.glob("*.md")
        ]

    return index


# =============================================================================
# Variation B: ThreadPoolExecutor (Parallel I/O)
# =============================================================================


def scan_file_threaded(
    file_path: Path, component_type: str, base_dir: Path
) -> dict[str, Any] | None:
    """Thread-safe file scanner."""
    if file_path.name == "README.md":
        return None
    try:
        content = file_path.read_text(encoding="utf-8")
        frontmatter, _ = parse_frontmatter(content)
        return build_component_dict(file_path, frontmatter, component_type, base_dir)
    except Exception:
        return None


def scan_directory_threaded(
    directory: Path, component_type: str, base_dir: Path, executor: ThreadPoolExecutor
) -> list[dict[str, Any]]:
    """Parallel directory scanning with ThreadPoolExecutor."""
    if not directory.exists():
        return []

    files = list(directory.rglob("*.md"))
    scanner = partial(scan_file_threaded, component_type=component_type, base_dir=base_dir)
    results = list(executor.map(scanner, files))

    # Filter None and sort for deterministic output
    return sorted([r for r in results if r is not None], key=lambda x: x["path"])


def build_index_threaded(repo_root: Path, max_workers: int = 8) -> dict[str, Any]:
    """Variation B: ThreadPoolExecutor parallel processing."""
    steve_dir = repo_root / "steve"
    index = create_empty_index()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Scan agents
        agents_dir = steve_dir / "agents"
        for domain_dir in agents_dir.iterdir():
            if domain_dir.is_dir():
                index["agents"].extend(
                    scan_directory_threaded(domain_dir, "agent", steve_dir, executor)
                )

        # Scan commands
        commands_dir = steve_dir / "commands"
        for category_dir in commands_dir.iterdir():
            if category_dir.is_dir():
                index["commands"].extend(
                    scan_directory_threaded(category_dir, "command", steve_dir, executor)
                )

        # Scan hooks
        hooks_dir = steve_dir / "hooks"
        for hook_type_dir in hooks_dir.iterdir():
            if hook_type_dir.is_dir():
                index["hooks"].extend(
                    scan_directory_threaded(hook_type_dir, "hook", steve_dir, executor)
                )

    # Skills need special handling (SKILL.md in subdirs)
    skills_dir = steve_dir / "skills"
    skill_files = [
        (skill_dir / "SKILL.md", skill_dir)
        for skill_dir in skills_dir.iterdir()
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists()
    ]

    for skill_file, skill_dir in skill_files:
        try:
            content = skill_file.read_text(encoding="utf-8")
            frontmatter, _ = parse_frontmatter(content)
            component = {
                "type": "skill",
                "path": str(skill_file.relative_to(steve_dir)),
                "name": frontmatter.get("name", skill_dir.name),
                "description": frontmatter.get("description", ""),
                "has_references": (skill_dir / "references").exists(),
                "has_scripts": (skill_dir / "scripts").exists(),
                "has_assets": (skill_dir / "assets").exists(),
            }
            index["skills"].append(component)
        except Exception:
            pass

    # Scan templates
    templates_dir = steve_dir / "templates"
    if templates_dir.exists():
        index["templates"] = [
            {"type": "template", "path": str(f.relative_to(steve_dir)), "name": f.stem}
            for f in templates_dir.glob("*.md")
        ]

    # Sort all lists for deterministic output
    index["agents"].sort(key=lambda x: x["path"])
    index["commands"].sort(key=lambda x: x["path"])
    index["skills"].sort(key=lambda x: x["path"])
    index["hooks"].sort(key=lambda x: x["path"])

    return index


# =============================================================================
# Variation C: Async (asyncio + aiofiles)
# =============================================================================


async def scan_file_async(
    file_path: Path, component_type: str, base_dir: Path
) -> dict[str, Any] | None:
    """Async file scanner using aiofiles."""
    if file_path.name == "README.md":
        return None
    try:
        async with aiofiles.open(file_path, encoding="utf-8") as f:
            content = await f.read()
        frontmatter, _ = parse_frontmatter(content)
        return build_component_dict(file_path, frontmatter, component_type, base_dir)
    except Exception:
        return None


async def scan_directory_async(
    directory: Path, component_type: str, base_dir: Path
) -> list[dict[str, Any]]:
    """Async directory scanning with asyncio.gather."""
    if not directory.exists():
        return []

    files = list(directory.rglob("*.md"))
    tasks = [scan_file_async(f, component_type, base_dir) for f in files]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter valid results and sort
    valid = [r for r in results if isinstance(r, dict)]
    return sorted(valid, key=lambda x: x["path"])


async def build_index_async_impl(repo_root: Path) -> dict[str, Any]:
    """Variation C: Async implementation."""
    steve_dir = repo_root / "steve"
    index = create_empty_index()

    # Collect all scan tasks
    tasks = []

    # Agent directories
    agents_dir = steve_dir / "agents"
    for domain_dir in agents_dir.iterdir():
        if domain_dir.is_dir():
            tasks.append(("agents", scan_directory_async(domain_dir, "agent", steve_dir)))

    # Command directories
    commands_dir = steve_dir / "commands"
    for category_dir in commands_dir.iterdir():
        if category_dir.is_dir():
            tasks.append(("commands", scan_directory_async(category_dir, "command", steve_dir)))

    # Hook directories
    hooks_dir = steve_dir / "hooks"
    for hook_type_dir in hooks_dir.iterdir():
        if hook_type_dir.is_dir():
            tasks.append(("hooks", scan_directory_async(hook_type_dir, "hook", steve_dir)))

    # Run all directory scans concurrently
    results = await asyncio.gather(*[t[1] for t in tasks])

    # Merge results
    for (category, _), components in zip(tasks, results, strict=True):
        index[category].extend(components)

    # Skills (special handling)
    skills_dir = steve_dir / "skills"
    skill_tasks = []
    skill_dirs = []
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir():
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                skill_dirs.append(skill_dir)
                skill_tasks.append(read_skill_file_async(skill_file, skill_dir, steve_dir))

    skill_results = await asyncio.gather(*skill_tasks, return_exceptions=True)
    for result in skill_results:
        if isinstance(result, dict):
            index["skills"].append(result)

    # Templates (sync is fine, few files)
    templates_dir = steve_dir / "templates"
    if templates_dir.exists():
        index["templates"] = [
            {"type": "template", "path": str(f.relative_to(steve_dir)), "name": f.stem}
            for f in templates_dir.glob("*.md")
        ]

    # Sort all
    for key in ["agents", "commands", "skills", "hooks"]:
        index[key].sort(key=lambda x: x["path"])

    return index


async def read_skill_file_async(
    skill_file: Path, skill_dir: Path, base_dir: Path
) -> dict[str, Any] | None:
    """Read and parse a skill file asynchronously."""
    try:
        async with aiofiles.open(skill_file, encoding="utf-8") as f:
            content = await f.read()
        frontmatter, _ = parse_frontmatter(content)
        return {
            "type": "skill",
            "path": str(skill_file.relative_to(base_dir)),
            "name": frontmatter.get("name", skill_dir.name),
            "description": frontmatter.get("description", ""),
            "has_references": (skill_dir / "references").exists(),
            "has_scripts": (skill_dir / "scripts").exists(),
            "has_assets": (skill_dir / "assets").exists(),
        }
    except Exception:
        return None


def build_index_async(repo_root: Path) -> dict[str, Any]:
    """Variation C: Async wrapper."""
    if not HAS_AIOFILES:
        raise ImportError("aiofiles required for async variation: uv add aiofiles")
    return asyncio.run(build_index_async_impl(repo_root))


# =============================================================================
# Variation D: Incremental (Hash-based Caching)
# =============================================================================

CACHE_FILE = ".index-cache.json"


def get_file_hash(file_path: Path) -> str:
    """Generate hash based on mtime and size for fast comparison."""
    stat = file_path.stat()
    return hashlib.md5(f"{stat.st_mtime_ns}:{stat.st_size}".encode()).hexdigest()


def load_cache(cache_path: Path) -> dict[str, Any]:
    """Load cache from file."""
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text())
        except Exception:
            return {}
    return {}


def save_cache(cache: dict[str, Any], cache_path: Path) -> None:
    """Save cache to file."""
    cache_path.write_text(json.dumps(cache, indent=2))


def build_index_incremental(repo_root: Path, use_cache: bool = True) -> dict[str, Any]:
    """Variation D: Incremental building with hash-based cache."""
    steve_dir = repo_root / "steve"
    cache_path = repo_root / CACHE_FILE
    cache = load_cache(cache_path) if use_cache else {}
    new_cache: dict[str, Any] = {}

    index = create_empty_index()

    # Collect all component files
    component_files: list[tuple[Path, str, Path | None]] = []

    # Agents
    agents_dir = steve_dir / "agents"
    for domain_dir in agents_dir.iterdir():
        if domain_dir.is_dir():
            for f in domain_dir.rglob("*.md"):
                if f.name != "README.md":
                    component_files.append((f, "agent", None))

    # Commands
    commands_dir = steve_dir / "commands"
    for category_dir in commands_dir.iterdir():
        if category_dir.is_dir():
            for f in category_dir.rglob("*.md"):
                if f.name != "README.md":
                    component_files.append((f, "command", None))

    # Skills
    skills_dir = steve_dir / "skills"
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir():
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                component_files.append((skill_file, "skill", skill_dir))

    # Hooks
    hooks_dir = steve_dir / "hooks"
    for hook_type_dir in hooks_dir.iterdir():
        if hook_type_dir.is_dir():
            for f in hook_type_dir.rglob("*.md"):
                if f.name != "README.md":
                    component_files.append((f, "hook", None))

    # Process files with caching
    cache_hits = 0
    cache_misses = 0

    for file_path, component_type, skill_dir in component_files:
        file_key = str(file_path.relative_to(repo_root))
        file_hash = get_file_hash(file_path)

        # Check cache
        if file_key in cache and cache[file_key].get("hash") == file_hash:
            # Cache hit
            component = cache[file_key]["data"]
            cache_hits += 1
        else:
            # Cache miss - parse file
            try:
                content = file_path.read_text(encoding="utf-8")
                frontmatter, _ = parse_frontmatter(content)

                if component_type == "skill" and skill_dir:
                    component = {
                        "type": "skill",
                        "path": str(file_path.relative_to(steve_dir)),
                        "name": frontmatter.get("name", skill_dir.name),
                        "description": frontmatter.get("description", ""),
                        "has_references": (skill_dir / "references").exists(),
                        "has_scripts": (skill_dir / "scripts").exists(),
                        "has_assets": (skill_dir / "assets").exists(),
                    }
                else:
                    component = build_component_dict(
                        file_path, frontmatter, component_type, steve_dir
                    )
                cache_misses += 1
            except Exception:
                continue

        # Update new cache and index
        new_cache[file_key] = {"hash": file_hash, "data": component}

        # Add to appropriate index list
        if component_type == "agent":
            index["agents"].append(component)
        elif component_type == "command":
            index["commands"].append(component)
        elif component_type == "skill":
            index["skills"].append(component)
        elif component_type == "hook":
            index["hooks"].append(component)

    # Templates (simple, no caching needed)
    templates_dir = steve_dir / "templates"
    if templates_dir.exists():
        index["templates"] = [
            {"type": "template", "path": str(f.relative_to(steve_dir)), "name": f.stem}
            for f in templates_dir.glob("*.md")
        ]

    # Sort all lists
    for key in ["agents", "commands", "skills", "hooks"]:
        index[key].sort(key=lambda x: x["path"])

    # Save updated cache
    if use_cache:
        save_cache(new_cache, cache_path)

    # Store stats for reporting
    index["_cache_stats"] = {"hits": cache_hits, "misses": cache_misses}

    return index


# =============================================================================
# Benchmark Runner
# =============================================================================


def run_benchmark(
    name: str,
    func: callable,
    repo_root: Path,
    iterations: int = 5,
    warmup: int = 1,
) -> dict[str, Any]:
    """Run benchmark for a single variation."""
    times = []

    # Warmup runs (not counted)
    for _ in range(warmup):
        func(repo_root)

    # Timed runs
    for _ in range(iterations):
        start = time.perf_counter()
        result = func(repo_root)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return {
        "name": name,
        "times": times,
        "min": min(times),
        "max": max(times),
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0,
        "component_count": sum(
            len(result.get(k, []))
            for k in ["agents", "commands", "skills", "hooks", "templates"]
        ),
    }


def print_results(results: list[dict[str, Any]], baseline_name: str = "Sequential") -> None:
    """Print benchmark results in a formatted table."""
    baseline = next((r for r in results if r["name"] == baseline_name), results[0])

    print("\n" + "=" * 80)
    print("BENCHMARK RESULTS")
    print("=" * 80)
    print(f"\n{'Variation':<25} {'Mean':>10} {'Median':>10} {'Min':>10} {'Speedup':>10}")
    print("-" * 80)

    for r in results:
        speedup = baseline["mean"] / r["mean"] if r["mean"] > 0 else 0
        speedup_str = f"{speedup:.2f}x" if r["name"] != baseline_name else "baseline"
        print(
            f"{r['name']:<25} {r['mean']*1000:>9.1f}ms {r['median']*1000:>9.1f}ms "
            f"{r['min']*1000:>9.1f}ms {speedup_str:>10}"
        )

    print("-" * 80)
    print(f"Components indexed: {results[0]['component_count']}")
    print(f"Iterations per test: {len(results[0]['times'])}")
    print("=" * 80)


def main() -> None:
    """Run all benchmarks."""
    parser = argparse.ArgumentParser(description="Benchmark build_index variations")
    parser.add_argument("--iterations", type=int, default=5, help="Number of iterations")
    parser.add_argument("--workers", type=int, default=8, help="Thread pool workers")
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    results = []

    print("Running build_index benchmarks...")
    print(f"Repository: {repo_root}")
    print(f"Iterations: {args.iterations}")
    print()

    # Variation A: Sequential
    print("Testing A: Sequential...", end=" ", flush=True)
    results.append(
        run_benchmark("Sequential", build_index_sequential, repo_root, args.iterations)
    )
    print(f"{results[-1]['mean']*1000:.1f}ms")

    # Variation B: ThreadPool
    print(f"Testing B: ThreadPool ({args.workers} workers)...", end=" ", flush=True)
    threaded_func = partial(build_index_threaded, max_workers=args.workers)
    results.append(
        run_benchmark(f"ThreadPool-{args.workers}", threaded_func, repo_root, args.iterations)
    )
    print(f"{results[-1]['mean']*1000:.1f}ms")

    # Variation B2: ThreadPool with different worker counts
    for workers in [4, 16]:
        if workers != args.workers:
            print(f"Testing B: ThreadPool ({workers} workers)...", end=" ", flush=True)
            threaded_func = partial(build_index_threaded, max_workers=workers)
            results.append(
                run_benchmark(f"ThreadPool-{workers}", threaded_func, repo_root, args.iterations)
            )
            print(f"{results[-1]['mean']*1000:.1f}ms")

    # Variation C: Async
    if HAS_AIOFILES:
        print("Testing C: Async...", end=" ", flush=True)
        results.append(run_benchmark("Async", build_index_async, repo_root, args.iterations))
        print(f"{results[-1]['mean']*1000:.1f}ms")
    else:
        print("Skipping C: Async (aiofiles not installed)")

    # Variation D: Incremental (cold cache)
    cache_path = repo_root / CACHE_FILE
    if cache_path.exists():
        cache_path.unlink()
    print("Testing D: Incremental (cold)...", end=" ", flush=True)
    results.append(
        run_benchmark("Incremental-cold", build_index_incremental, repo_root, args.iterations)
    )
    print(f"{results[-1]['mean']*1000:.1f}ms")

    # Variation D: Incremental (warm cache)
    print("Testing D: Incremental (warm)...", end=" ", flush=True)
    results.append(
        run_benchmark("Incremental-warm", build_index_incremental, repo_root, args.iterations)
    )
    print(f"{results[-1]['mean']*1000:.1f}ms")

    # Cleanup cache
    if cache_path.exists():
        cache_path.unlink()

    print_results(results)


if __name__ == "__main__":
    main()
