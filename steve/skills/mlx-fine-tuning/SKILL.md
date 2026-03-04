---
status: DEPRECATED
deprecated_in: "2026-01-20"
name: mlx-fine-tuning
description: Specialized skill for MLX-based LLM fine-tuning on Apple Silicon. This skill should be used when working with LoRA fine-tuning, model conversion from HuggingFace to MLX format, adapter management, hyperparameter tuning, memory optimization, and benchmarking on M1/M2/M3/M4 chips.
user-invocable: false
---


# MLX Fine-Tuning

Comprehensive skill for fine-tuning Large Language Models using MLX framework on Apple Silicon (M1/M2/M3/M4).

## Purpose

Enable efficient LLM fine-tuning on Apple Silicon using MLX's unified memory architecture and Metal GPU acceleration. Focus on LoRA (Low-Rank Adaptation) for parameter-efficient fine-tuning without requiring expensive GPU hardware.

## When to Use This Skill

Invoke this skill when:
- Setting up MLX fine-tuning on Apple Silicon
- Converting models from HuggingFace to MLX format
- Configuring LoRA adapters for fine-tuning
- Optimizing hyperparameters for specific datasets
- Troubleshooting memory or performance issues
- Benchmarking fine-tuned models
- Managing and exporting adapters

## Platform Requirements

**Critical**: MLX only works on Apple Silicon (M1/M2/M3/M4) running macOS natively.
- Architecture must be `arm64` (verify with `uname -m`)
- Cannot run in Docker or virtual machines
- Requires macOS 11.0 or later

## Workflow

### 1. Environment Validation

First, validate the environment using the provided script:

```bash
python scripts/validate_environment.py
```

This checks:
- Apple Silicon architecture
- MLX installation
- Metal GPU availability
- Memory capacity

### 2. Model Preparation

Convert HuggingFace models to MLX format or use pre-converted models:

```bash
# Option A: Use pre-converted model from MLX Community
--model mlx-community/Qwen2.5-3B-Instruct-4bit

# Option B: Convert from HuggingFace
uv run mlx_lm.convert \
    --hf-path Qwen/Qwen2.5-3B-Instruct \
    --mlx-path models/Qwen2.5-3B-Instruct-mlx \
    --quantize  # Optional: for 4-bit quantization
```

### 3. Data Preparation

Prepare training data in MLX chat format (JSONL):

```json
{"messages": [
  {"role": "system", "content": "You are a helpful assistant."},
  {"role": "user", "content": "What is machine learning?"},
  {"role": "assistant", "content": "Machine learning is..."}
]}
```

Save as `train.jsonl` and `valid.jsonl` in your data directory.

### 4. Hyperparameter Selection

Load `references/hyperparameter_guidelines.md` for detailed guidance based on dataset size.

Quick reference:
- **Small datasets (<1k samples)**: LR 2e-5, 200-500 iterations, 4-8 layers
- **Medium datasets (1k-10k)**: LR 1e-5, 500-1000 iterations, 8-16 layers
- **Large datasets (10k+)**: LR 5e-6, 1000-2000 iterations, 16-32 layers

### 5. Training Execution

Run fine-tuning with mlx_lm:

```bash
uv run python -m mlx_lm lora \
    --model models/Qwen2.5-3B-Instruct-mlx \
    --train \
    --data ./data \
    --batch-size 1 \
    --iters 500 \
    --learning-rate 1e-5 \
    --num-layers 8 \
    --adapter-path adapters/my-lora \
    --save-every 100 \
    --grad-checkpoint  # Enable for memory efficiency
```

### 6. Memory Optimization

If encountering memory issues, load `references/memory_optimization.md` for techniques:
- Gradient checkpointing (`--grad-checkpoint`)
- Batch size reduction
- Model quantization (4-bit)
- Layer count reduction

### 7. Evaluation and Testing

Test the fine-tuned model:

```bash
# Interactive generation
uv run python -m mlx_lm lora \
    --model models/Qwen2.5-3B-Instruct-mlx \
    --adapter-path adapters/my-lora \
    --prompt "Your test prompt"

# Benchmark comparison
uv run python scripts/hyperparameter_optimizer.py \
    --model models/Qwen2.5-3B-Instruct-mlx \
    --adapter adapters/my-lora \
    --test-samples 20
```

### 8. Adapter Management

Export and merge adapters:

```bash
# Export to safetensors format
uv run mlx_lm.fuse \
    --model models/base-model \
    --adapter-path adapters/my-lora \
    --save-path models/fused-model

# Convert back to HuggingFace format
uv run mlx_lm.convert \
    --mlx-path models/fused-model \
    --hf-path models/hf-export
```

## Troubleshooting

For common issues, load `references/common_issues.md`. Quick solutions:

- **Memory errors**: Reduce batch size to 1, enable gradient checkpointing
- **Slow training**: Verify Metal GPU usage with `mx.default_device()`
- **Training instability**: Lower learning rate, increase warmup ratio
- **Format errors**: Validate data format matches MLX chat structure

## Advanced Techniques

### Multi-Phase Training with LR Decay

```python
# Progressive learning rate schedule
--lr-schedule "400:2e-5,400:1e-5,200:2e-6"
```

### A/B Testing Configurations

Use `scripts/hyperparameter_optimizer.py` to test multiple configurations:

```bash
python scripts/hyperparameter_optimizer.py \
    --config-file configs/experiment.yaml \
    --parallel-runs 4
```

### Monitoring Training

Track key metrics:
- Training/validation loss curves
- Memory usage (`mx.metal.get_active_memory()`)
- Token throughput
- Gradient norms

## Best Practices

1. **Start Small**: Test with few iterations before full training
2. **Checkpoint Frequently**: Use `--save-every` to avoid losing progress
3. **Monitor Memory**: Track unified memory usage throughout training
4. **Validate Often**: Check validation loss to detect overfitting early
5. **Compare Performance**: Always benchmark against base model
6. **Version Control**: Use descriptive names for adapter directories
7. **Document Experiments**: Log all hyperparameters and results

## Resource References

- Load `references/hyperparameter_guidelines.md` for detailed parameter selection
- Load `references/memory_optimization.md` for memory management techniques
- Load `references/common_issues.md` for troubleshooting guide
- Load `references/mlx_api_reference.md` for MLX-specific functions

## Output Artifacts

Training produces:
- `adapters/*/adapters.safetensors` - LoRA weights
- `adapters/*/adapter_config.json` - Configuration
- Training logs with loss curves
- Checkpoint saves at specified intervals

## Integration with Pipelines

For programmatic training, integrate with pipeline systems:

```python
from training.mlx import TrainConfig, TrainPipeline

config = TrainConfig(
    model="mlx-community/Qwen2.5-3B-Instruct-4bit",
    train_data="data/train.jsonl",
    iters=500,
    learning_rate=1e-5,
    num_layers=8,
    grad_checkpoint=True
)

pipeline = TrainPipeline(config)
result = pipeline.execute()
```