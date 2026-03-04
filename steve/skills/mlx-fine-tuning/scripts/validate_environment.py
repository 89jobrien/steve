#!/usr/bin/env python3
"""
Validate MLX fine-tuning environment on Apple Silicon.

This script checks:
- Apple Silicon architecture
- MLX installation and version
- Metal GPU availability
- Memory capacity
- Python version compatibility
"""

import platform
import subprocess
import sys


def check_architecture():
    """Check if running on Apple Silicon."""
    arch = platform.machine()
    is_apple_silicon = arch == "arm64"

    print(f"Architecture: {arch}")
    if is_apple_silicon:
        print("✓ Apple Silicon detected (M1/M2/M3/M4)")
    else:
        print("✗ Not Apple Silicon - MLX requires arm64 architecture")

    return is_apple_silicon


def check_macos():
    """Check if running on macOS."""
    system = platform.system()
    is_macos = system == "Darwin"

    print(f"\nOperating System: {system}")
    if is_macos:
        version = platform.mac_ver()[0]
        print(f"✓ macOS {version}")
    else:
        print("✗ Not macOS - MLX requires macOS")

    return is_macos


def check_mlx_installation():
    """Check if MLX is installed and get version."""
    try:
        import mlx
        import mlx.core as mx

        print("\nMLX Installation:")
        print(f"✓ MLX version: {mlx.__version__}")

        # Check mlx-lm separately
        try:
            import mlx_lm  # noqa: F401
            print("✓ mlx-lm installed")
        except ImportError:
            print("✗ mlx-lm not installed")
            print("  Install with: uv add 'mlx-lm>=0.12.0'")
            return False

        # Test basic MLX functionality
        test_array = mx.array([1, 2, 3])
        _ = test_array * 2
        print("✓ MLX core functionality working")

        return True
    except ImportError as e:
        print("\nMLX Installation:")
        print(f"✗ MLX not installed or import error: {e}")
        print("  Install with: uv add 'mlx>=0.21.0' 'mlx-lm>=0.12.0'")
        return False
    except Exception as e:
        print(f"✗ MLX functionality error: {e}")
        return False


def check_metal_gpu():
    """Check Metal GPU availability."""
    try:
        import mlx.core as mx

        device = mx.default_device()
        print("\nGPU Status:")
        print(f"Default device: {device}")

        if str(device) == "gpu":
            print("✓ Metal GPU available and active")
            return True
        else:
            print("✗ GPU not active - check Metal support")
            return False
    except Exception as e:
        print("\nGPU Status:")
        print(f"✗ Cannot check GPU: {e}")
        return False


def check_memory():
    """Check system memory capacity."""
    try:
        import mlx.core as mx

        # Get memory info using sysctl
        result = subprocess.run(
            ["sysctl", "-n", "hw.memsize"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            mem_bytes = int(result.stdout.strip())
            mem_gb = mem_bytes / (1024**3)

            print("\nSystem Memory:")
            print(f"Total RAM: {mem_gb:.1f} GB")

            if mem_gb >= 16:
                print("✓ Sufficient memory for most fine-tuning tasks")
            elif mem_gb >= 8:
                print("⚠ Limited memory - use gradient checkpointing and small batch sizes")
            else:
                print("✗ Insufficient memory - MLX fine-tuning may fail")

            # Check MLX memory if available
            try:
                active_mem = mx.metal.get_active_memory() / (1024**3)
                print(f"Active MLX memory: {active_mem:.2f} GB")
            except Exception:
                pass

            return mem_gb >= 8
        else:
            print("\nSystem Memory:")
            print("✗ Could not determine memory capacity")
            return False

    except Exception as e:
        print("\nSystem Memory:")
        print(f"✗ Memory check failed: {e}")
        return False


def check_python_version():
    """Check Python version compatibility."""
    version = sys.version_info
    print("\nPython Version:")
    print(f"Python {version.major}.{version.minor}.{version.micro}")

    if version.major == 3 and version.minor >= 9:
        print("✓ Python version compatible")
        return True
    else:
        print("✗ Python 3.9+ required for MLX")
        return False


def check_uv_installation():
    """Check if uv is installed."""
    try:
        result = subprocess.run(
            ["uv", "--version"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("\nPackage Manager:")
            print(f"✓ uv installed: {result.stdout.strip()}")
            return True
        else:
            print("\nPackage Manager:")
            print("✗ uv not found")
            return False
    except FileNotFoundError:
        print("\nPackage Manager:")
        print("✗ uv not installed")
        print("  Install with: curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False


def suggest_model_sizes(mem_gb):
    """Suggest appropriate model sizes based on memory."""
    print("\nRecommended Model Sizes:")

    if mem_gb >= 32:
        print("✓ Can handle 7B-13B models comfortably")
        print("✓ 3B models with large batch sizes")
    elif mem_gb >= 16:
        print("✓ Can handle 3B-7B models")
        print("⚠ Use gradient checkpointing for 7B+")
    elif mem_gb >= 8:
        print("✓ Can handle 1B-3B models")
        print("⚠ Use 4-bit quantization for larger models")
    else:
        print("✗ Limited to very small models (<1B)")


def main():
    """Run all validation checks."""
    print("=" * 60)
    print("MLX Fine-Tuning Environment Validation")
    print("=" * 60)

    checks = {
        "Architecture": check_architecture(),
        "macOS": check_macos(),
        "Python": check_python_version(),
        "MLX": False,
        "GPU": False,
        "Memory": False,
        "uv": check_uv_installation()
    }

    # Only check MLX-specific items if on Apple Silicon macOS
    if checks["Architecture"] and checks["macOS"]:
        checks["MLX"] = check_mlx_installation()
        if checks["MLX"]:
            checks["GPU"] = check_metal_gpu()
            checks["Memory"] = check_memory()

    # Memory capacity suggestions
    try:
        result = subprocess.run(
            ["sysctl", "-n", "hw.memsize"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            mem_gb = int(result.stdout.strip()) / (1024**3)
            suggest_model_sizes(mem_gb)
    except Exception:
        pass

    # Summary
    print("\n" + "=" * 60)
    print("Validation Summary:")
    print("=" * 60)

    all_passed = all(checks.values())
    critical_passed = checks["Architecture"] and checks["macOS"] and checks["MLX"]

    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"{status} {check}")

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ Environment fully ready for MLX fine-tuning!")
    elif critical_passed:
        print("⚠️  Environment partially ready - some optional features missing")
    else:
        print("❌ Environment not ready - critical requirements missing")
        print("\nRequired fixes:")
        if not checks["Architecture"]:
            print("- Need Apple Silicon Mac (M1/M2/M3/M4)")
        if not checks["macOS"]:
            print("- Need to run on macOS")
        if not checks["MLX"]:
            print("- Need to install MLX: uv add 'mlx>=0.21.0' 'mlx-lm>=0.12.0'")

    return 0 if critical_passed else 1


if __name__ == "__main__":
    sys.exit(main())
