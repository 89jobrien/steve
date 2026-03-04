"""Train Lisa AI using OpenPipe ART with pre-generated trajectories.

Loads trajectories from lisa_trajectories.jsonl and trains using GRPO.

Example:
  uv run python scripts/train_lisa.py \
    --trajectories ~/.claude/datasets/lisa_trajectories.jsonl \
    --model-name lisa-ai-v1 \
    --base-model Qwen/Qwen2.5-Coder-3B-Instruct \
    --epochs 3

Requirements:
  - openpipe-art>=0.5.4
  - OPENROUTER_API_KEY env var for RULER scoring
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Ensure art is importable
try:
    import art
except ImportError:
    print("Error: openpipe-art not installed. Run: uv add openpipe-art")
    sys.exit(1)


@dataclass
class TrainingConfig:
    """Training configuration."""

    trajectories_path: Path
    model_name: str
    project_name: str
    base_model: str
    learning_rate: float
    epochs: int
    batch_size: int
    use_ruler: bool
    ruler_model: str
    art_path: Path


def flatten_metadata(metadata: dict[str, Any]) -> dict[str, float | int | str | bool | None]:
    """Flatten nested metadata to scalar values only.

    ART requires metadata values to be float, int, str, bool, or None.
    Lists and dicts are converted to JSON strings or summarized.

    Args:
        metadata: Original metadata dict with potentially nested values.

    Returns:
        Flattened metadata with only scalar values.
    """
    flat: dict[str, float | int | str | bool | None] = {}

    for key, value in metadata.items():
        if isinstance(value, (float, int, str, bool)) or value is None:
            flat[key] = value
        elif isinstance(value, list):
            # Convert list to count and sample
            flat[f"{key}_count"] = len(value)
            if value and isinstance(value[0], str):
                flat[f"{key}_sample"] = value[0][:100] if value else None
        elif isinstance(value, dict):
            # Flatten nested dict with prefix
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, (float, int, str, bool)) or sub_value is None:
                    flat[f"{key}_{sub_key}"] = sub_value

    return flat


def load_trajectories(path: Path, limit: int | None = None) -> list[art.Trajectory]:
    """Load trajectories from JSONL file.

    Args:
        path: Path to trajectories JSONL file.
        limit: Optional limit on number of trajectories to load.

    Returns:
        List of art.Trajectory objects.
    """
    trajectories: list[art.Trajectory] = []

    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if limit and i >= limit:
                break

            data = json.loads(line.strip())

            # Flatten metadata for ART compatibility
            original_metadata = data.get("metadata", {})
            flat_metadata = flatten_metadata(original_metadata)

            # Convert to art.Trajectory
            traj = art.Trajectory(
                reward=data.get("reward", 0.0),
                messages_and_choices=data.get("messages_and_choices", []),
                metadata=flat_metadata,
            )
            trajectories.append(traj)

    return trajectories


def create_trajectory_groups(
    trajectories: list[art.Trajectory],
    group_size: int = 4,
) -> list[art.TrajectoryGroup]:
    """Group trajectories for GRPO training.

    GRPO requires groups of trajectories to compare relative rewards.

    Args:
        trajectories: List of trajectories to group.
        group_size: Number of trajectories per group.

    Returns:
        List of trajectory groups.
    """
    groups: list[art.TrajectoryGroup] = []

    for i in range(0, len(trajectories), group_size):
        batch = trajectories[i : i + group_size]
        if len(batch) >= 2:  # Need at least 2 for comparison
            groups.append(art.TrajectoryGroup(batch))

    return groups


async def score_with_ruler(
    groups: list[art.TrajectoryGroup],
    ruler_model: str,
) -> list[art.TrajectoryGroup]:
    """Re-score trajectory groups using RULER.

    Args:
        groups: Trajectory groups to score.
        ruler_model: Model to use for RULER scoring.

    Returns:
        Scored trajectory groups.
    """
    from art.rewards import ruler_score_group

    scored_groups: list[art.TrajectoryGroup] = []

    for i, group in enumerate(groups):
        try:
            scored = await ruler_score_group(group, ruler_model, debug=False)
            scored_groups.append(scored)
            if (i + 1) % 10 == 0:
                print(f"  Scored {i + 1}/{len(groups)} groups")
        except Exception as e:
            print(f"  Warning: Failed to score group {i}: {e}")
            # Keep original rewards
            scored_groups.append(group)

    return scored_groups


async def train(config: TrainingConfig) -> dict[str, Any]:
    """Run the training pipeline.

    Args:
        config: Training configuration.

    Returns:
        Training results and metrics.
    """
    print(f"Loading trajectories from {config.trajectories_path}...")
    trajectories = load_trajectories(config.trajectories_path)
    print(f"  Loaded {len(trajectories)} trajectories")

    # Stats
    rewards = [t.reward for t in trajectories]
    print(f"  Reward range: [{min(rewards):.3f}, {max(rewards):.3f}]")
    print(f"  Avg reward: {sum(rewards) / len(rewards):.3f}")

    # Create trajectory groups for GRPO
    print("\nCreating trajectory groups...")
    groups = create_trajectory_groups(trajectories, group_size=4)
    print(f"  Created {len(groups)} groups")

    # Initialize ART model
    print(f"\nInitializing model: {config.model_name}")
    print(f"  Base model: {config.base_model}")
    print(f"  ART path: {config.art_path}")

    config.art_path.mkdir(parents=True, exist_ok=True)

    model = art.TrainableModel(
        name=config.model_name,
        project=config.project_name,
        base_model=config.base_model,
    )

    backend = art.LocalBackend(
        in_process=True,
        path=str(config.art_path),
    )

    print("  Registering model with backend...")
    await model.register(backend)
    print("  Model registered successfully")

    # Optional: Re-score with RULER for better training signal
    if config.use_ruler:
        print(f"\nRe-scoring with RULER ({config.ruler_model})...")
        groups = await score_with_ruler(groups, config.ruler_model)

        # Updated stats after RULER
        all_rewards = [t.reward for g in groups for t in g.trajectories]
        print(f"  RULER reward range: [{min(all_rewards):.3f}, {max(all_rewards):.3f}]")
        print(f"  RULER avg reward: {sum(all_rewards) / len(all_rewards):.3f}")

    # Training loop
    print(f"\nStarting training for {config.epochs} epochs...")
    print(f"  Learning rate: {config.learning_rate}")
    print(f"  Batch size: {config.batch_size}")

    total_steps = 0
    epoch_metrics: list[dict[str, Any]] = []

    for epoch in range(config.epochs):
        print(f"\n=== Epoch {epoch + 1}/{config.epochs} ===")

        # Process groups in batches
        for batch_idx in range(0, len(groups), config.batch_size):
            batch = groups[batch_idx : batch_idx + config.batch_size]

            # Train step
            await model.train(
                batch,
                config=art.TrainConfig(learning_rate=config.learning_rate),
            )

            total_steps += 1
            batch_rewards = [t.reward for g in batch for t in g.trajectories]
            avg_reward = sum(batch_rewards) / len(batch_rewards) if batch_rewards else 0

            print(f"  Step {total_steps}: batch {batch_idx // config.batch_size + 1}, "
                  f"avg_reward={avg_reward:.3f}")

        # Epoch metrics
        epoch_metrics.append({
            "epoch": epoch + 1,
            "steps": total_steps,
        })

        # Delete old checkpoints to save space
        await model.delete_checkpoints()

    print(f"\nTraining complete! Total steps: {total_steps}")

    results = {
        "model_name": config.model_name,
        "base_model": config.base_model,
        "trajectories": len(trajectories),
        "groups": len(groups),
        "epochs": config.epochs,
        "total_steps": total_steps,
        "final_reward_avg": sum(rewards) / len(rewards),
        "epoch_metrics": epoch_metrics,
    }

    return results


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--trajectories",
        type=Path,
        default=Path("~/.claude/datasets/lisa_trajectories.jsonl"),
        help="Path to trajectories JSONL file",
    )
    ap.add_argument(
        "--model-name",
        type=str,
        default="lisa-ai-v1",
        help="Name for the trained model",
    )
    ap.add_argument(
        "--project-name",
        type=str,
        default="lisa-ai",
        help="ART project name",
    )
    ap.add_argument(
        "--base-model",
        type=str,
        default="Qwen/Qwen2.5-Coder-3B-Instruct",
        help="HuggingFace base model ID",
    )
    ap.add_argument(
        "--learning-rate",
        type=float,
        default=1e-5,
        help="Training learning rate",
    )
    ap.add_argument(
        "--epochs",
        type=int,
        default=3,
        help="Number of training epochs",
    )
    ap.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help="Training batch size (groups per step)",
    )
    ap.add_argument(
        "--use-ruler",
        action="store_true",
        help="Re-score trajectories with RULER before training",
    )
    ap.add_argument(
        "--ruler-model",
        type=str,
        default="openrouter/openai/gpt-4o-mini",
        help="Model for RULER scoring",
    )
    ap.add_argument(
        "--art-path",
        type=Path,
        default=Path("~/.art/lisa"),
        help="Path for ART model storage",
    )
    args = ap.parse_args()

    # Expand paths
    trajectories_path = args.trajectories.expanduser()
    art_path = args.art_path.expanduser()

    if not trajectories_path.exists():
        print(f"Error: Trajectories file not found: {trajectories_path}")
        return 1

    # Check for RULER API key if needed
    if args.use_ruler and not os.getenv("OPENROUTER_API_KEY"):
        print("Warning: --use-ruler specified but OPENROUTER_API_KEY not set")
        print("  RULER scoring will be skipped")
        args.use_ruler = False

    config = TrainingConfig(
        trajectories_path=trajectories_path,
        model_name=args.model_name,
        project_name=args.project_name,
        base_model=args.base_model,
        learning_rate=args.learning_rate,
        epochs=args.epochs,
        batch_size=args.batch_size,
        use_ruler=args.use_ruler,
        ruler_model=args.ruler_model,
        art_path=art_path,
    )

    print("=" * 60)
    print("Lisa AI Training with OpenPipe ART")
    print("=" * 60)
    print(f"Model: {config.model_name}")
    print(f"Base: {config.base_model}")
    print(f"Epochs: {config.epochs}")
    print(f"Learning rate: {config.learning_rate}")
    print(f"RULER: {'enabled' if config.use_ruler else 'disabled'}")
    print("=" * 60)

    results = asyncio.run(train(config))

    print("\n" + "=" * 60)
    print("Training Results")
    print("=" * 60)
    print(json.dumps(results, indent=2))

    # Save results
    results_path = art_path / "training_results.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.write_text(json.dumps(results, indent=2) + "\n")
    print(f"\nResults saved to: {results_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
