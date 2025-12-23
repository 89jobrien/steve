#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Knowledge update hook.

Updates knowledge graph with entities discovered in session.
Runs on Stop event.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation


KNOWLEDGE_DIR = Path.home() / ".claude" / "knowledge-updates"


def extract_entities_from_transcript(transcript_path: str) -> dict:
    """Extract potential knowledge entities from session transcript.

    Returns dict with:
    - files_created: New files created
    - functions_added: Functions/classes added
    - dependencies_added: Dependencies installed
    - patterns_used: Design patterns observed
    """
    entities = {
        "files_created": [],
        "components_added": [],
        "dependencies_added": [],
        "patterns_used": set(),
        "technologies": set(),
    }

    path = Path(transcript_path)
    if not path.exists():
        return entities

    try:
        content = path.read_text()
    except OSError:
        return entities

    # Extract created files
    write_matches = re.findall(r'"tool_name":\s*"Write"[^}]*"file_path":\s*"([^"]+)"', content)
    entities["files_created"] = list(set(write_matches))

    # Extract dependencies (npm install, uv add, pip install)
    dep_patterns = [
        r"npm\s+install\s+(?:--save-dev\s+)?([a-z@][\w./-]+)",
        r"uv\s+add\s+([a-z][\w.-]+)",
        r"pip\s+install\s+([a-z][\w.-]+)",
    ]
    for pattern in dep_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        entities["dependencies_added"].extend(matches)

    entities["dependencies_added"] = list(set(entities["dependencies_added"]))

    # Detect patterns from content
    pattern_indicators = {
        "TDD": [r"\bred-green-refactor\b", r"\btest.?first\b", r"\bfailing test\b"],
        "DI": [r"\bdependency injection\b", r"\binject\b.*\bcontainer\b"],
        "Repository": [r"\brepository pattern\b", r"class \w*Repository"],
        "Factory": [r"\bfactory pattern\b", r"class \w*Factory"],
        "Observer": [r"\bobserver pattern\b", r"\bsubscrib", r"\bpublish"],
        "Singleton": [r"\bsingleton\b"],
        "MVC": [r"\bmodel.?view.?controller\b", r"\bmvc\b"],
        "REST": [r"\brest\s*api\b", r"\bendpoint"],
        "GraphQL": [r"\bgraphql\b", r"\bquery\b.*\bresolver"],
    }

    for pattern_name, indicators in pattern_indicators.items():
        for indicator in indicators:
            if re.search(indicator, content, re.IGNORECASE):
                entities["patterns_used"].add(pattern_name)
                break

    # Detect technologies
    tech_patterns = {
        "React": r"\breact\b|\bjsx\b|\btsx\b",
        "Next.js": r"\bnext\.?js\b|\bgetServerSideProps\b|\bgetStaticProps\b",
        "FastAPI": r"\bfastapi\b|\b@app\.(get|post|put|delete)\b",
        "Django": r"\bdjango\b|\bmanage\.py\b",
        "PostgreSQL": r"\bpostgres(ql)?\b|\bpsql\b",
        "MongoDB": r"\bmongo(db)?\b|\bmongosh\b",
        "Redis": r"\bredis\b",
        "Docker": r"\bdocker\b|\bdockerfile\b",
        "TypeScript": r"\btypescript\b|\b\.tsx?\b",
        "Python": r"\bpython\b|\b\.py\b",
    }

    for tech, pattern in tech_patterns.items():
        if re.search(pattern, content, re.IGNORECASE):
            entities["technologies"].add(tech)

    # Convert sets to lists
    entities["patterns_used"] = list(entities["patterns_used"])
    entities["technologies"] = list(entities["technologies"])

    return entities


def save_knowledge_update(entities: dict, cwd: str, session_id: str) -> Path:
    """Save knowledge update to file."""
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now()
    update_file = KNOWLEDGE_DIR / f"knowledge_{timestamp:%Y%m%d_%H%M%S}.json"

    record = {
        "timestamp": timestamp.isoformat(),
        "session_id": session_id,
        "cwd": cwd,
        "entities": entities,
        "summary": {
            "files_created": len(entities["files_created"]),
            "dependencies_added": len(entities["dependencies_added"]),
            "patterns_observed": len(entities["patterns_used"]),
            "technologies_used": len(entities["technologies"]),
        },
    }

    update_file.write_text(json.dumps(record, indent=2))
    return update_file


def main() -> None:
    with hook_invocation("knowledge_update") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        transcript_path = payload.get("transcript_path", "")
        cwd = payload.get("cwd", ".")
        session_id = payload.get("session_id", "unknown")

        if not transcript_path:
            sys.exit(0)

        # Extract entities
        entities = extract_entities_from_transcript(transcript_path)

        # Skip if nothing interesting found
        if not any(
            [
                entities["files_created"],
                entities["dependencies_added"],
                entities["patterns_used"],
            ]
        ):
            sys.exit(0)

        # Save knowledge update
        update_file = save_knowledge_update(entities, cwd, session_id)

        # Output summary
        print("\n" + "=" * 50, file=sys.stderr)
        print("[Success] Knowledge entities extracted:", file=sys.stderr)

        if entities["files_created"]:
            print(f"  Files created: {len(entities['files_created'])}", file=sys.stderr)

        if entities["dependencies_added"]:
            print(
                f"  Dependencies: {', '.join(entities['dependencies_added'][:5])}", file=sys.stderr
            )

        if entities["patterns_used"]:
            print(f"  Patterns: {', '.join(entities['patterns_used'])}", file=sys.stderr)

        if entities["technologies"]:
            print(f"  Technologies: {', '.join(entities['technologies'])}", file=sys.stderr)

        print(f"\n  Saved to: {update_file}", file=sys.stderr)
        print("=" * 50 + "\n", file=sys.stderr)

        sys.exit(0)


if __name__ == "__main__":
    main()
