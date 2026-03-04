---
status: DEPRECATED
deprecated_in: "2026-01-20"
name: code-permutation-testing
description: "Systematic testing of code variations, edge cases, boundary conditions, and alternative implementations. This skill provides methodologies and tools for exhaustive testing including input permutation, code path analysis, mutation testing, and implementation alternatives. Use when ensuring code robustness through comprehensive test coverage or when exploring edge cases and boundary conditions."
user-invocable: true
---


# Code Permutation Testing

## Overview

This skill enables systematic testing of code variations, edge cases, and alternative implementations to ensure robustness and comprehensive test coverage. It provides methodologies for input permutation, code path analysis, mutation testing, and implementation exploration.

## When to Use

Invoke this skill when:
- Testing functions with complex input domains requiring boundary testing
- Exploring edge cases and corner conditions systematically
- Analyzing code path coverage and branch conditions
- Running mutation testing to verify test suite effectiveness
- Comparing alternative implementations for correctness
- Generating comprehensive test suites for critical code
- Validating error handling and recovery paths

## Core Testing Modes

### 1. Input Permutation Testing

Generate comprehensive test cases covering:
- **Boundary values**: Min, max, just inside, just outside boundaries
- **Edge cases**: Empty inputs, null values, extreme sizes
- **Type variations**: Different numeric types, string encodings, data structures
- **Combinatorial testing**: Pairwise and n-wise testing of input combinations

Load `references/boundary_patterns.md` for common boundary testing patterns and strategies.

Use `scripts/generate_boundaries.py` to automatically generate boundary test cases from function signatures.

### 2. Code Path Analysis

Analyze all possible execution paths through code:
- **Branch coverage**: Test all conditional branches
- **Loop coverage**: Zero, one, many, maximum iterations
- **Exception paths**: Force error conditions systematically
- **State transitions**: Test all valid and invalid state changes

Use `scripts/analyze_paths.py` to identify uncovered code paths and generate test suggestions.

### 3. Mutation Testing

Verify test suite effectiveness by introducing controlled mutations:

**For Rust projects:**
```bash
# Install cargo-mutants
cargo install cargo-mutants

# Run mutation testing
cargo mutants --no-shuffle --test-timeout 30

# Generate detailed report
cargo mutants --json > mutations.json
```

**For Python projects:**
```bash
# Install mutmut
pip install mutmut

# Run mutation testing
mutmut run --paths-to-mutate src/

# Show results
mutmut results
```

Load `references/mutation_testing.md` for detailed mutation testing guidance and interpretation.

### 4. Implementation Alternatives

Test different algorithmic approaches:
- **Iterative vs Recursive**: Compare implementations for stack safety
- **Mutable vs Immutable**: Test functional and imperative variations
- **Synchronous vs Asynchronous**: Verify concurrency behavior
- **Naive vs Optimized**: Validate optimizations maintain correctness

## Workflow

### Step 1: Analyze Target Code

First, understand the code structure:
- Identify function signatures and parameter types
- Map control flow and decision points
- Note error handling and edge cases
- Document assumptions and invariants

### Step 2: Generate Test Matrix

Create comprehensive test coverage:

```python
# Example for a function: divide(a: i32, b: i32) -> Result<i32, Error>

# Boundary tests
test_cases = [
    # Normal cases
    (10, 2, Ok(5)),
    (10, 3, Ok(3)),

    # Boundary values
    (i32::MAX, 1, Ok(i32::MAX)),
    (i32::MIN, 1, Ok(i32::MIN)),
    (i32::MIN, -1, Err(Overflow)),  # Special overflow case

    # Edge cases
    (0, 5, Ok(0)),
    (5, 0, Err(DivisionByZero)),
    (0, 0, Err(DivisionByZero)),

    # Sign variations
    (-10, 2, Ok(-5)),
    (10, -2, Ok(-5)),
    (-10, -2, Ok(5)),
]
```

### Step 3: Execute Permutation Tests

Run the generated test matrix:
- Execute each test case
- Verify expected outcomes
- Check for unexpected behaviors
- Monitor performance characteristics

### Step 4: Analyze Coverage

Evaluate test completeness:
- Generate coverage reports
- Identify uncovered paths
- Run mutation testing
- Add tests for gaps

### Step 5: Document Results

Create comprehensive test documentation:
- List all tested scenarios
- Document discovered edge cases
- Note performance characteristics
- Highlight critical paths

## Language-Specific Guidance

### Rust

```rust
#[cfg(test)]
mod permutation_tests {
    use super::*;
    use proptest::prelude::*;

    // Property-based testing for automatic permutation
    proptest! {
        #[test]
        fn test_function_properties(
            a in any::<i32>(),
            b in any::<i32>().prop_filter("non-zero", |x| *x != 0)
        ) {
            let result = divide(a, b);
            prop_assert!(result.is_ok());
            prop_assert_eq!(result.unwrap(), a / b);
        }
    }

    // Boundary value testing
    #[test]
    fn test_boundaries() {
        let boundaries = vec![
            i32::MIN, i32::MIN + 1, -1, 0, 1, i32::MAX - 1, i32::MAX
        ];

        for a in &boundaries {
            for b in &boundaries {
                if *b != 0 {
                    let result = divide(*a, *b);
                    // Verify result or expected error
                }
            }
        }
    }
}
```

### Python

```python
import hypothesis.strategies as st
from hypothesis import given, assume
import pytest

# Property-based testing
@given(st.integers(), st.integers())
def test_division_properties(a, b):
    assume(b != 0)  # Precondition
    result = divide(a, b)
    assert result == a // b

# Parametrized boundary testing
@pytest.mark.parametrize("a,b,expected", [
    (10, 2, 5),
    (sys.maxsize, 1, sys.maxsize),
    (-sys.maxsize-1, 1, -sys.maxsize-1),
    (0, 5, 0),
    # Add more boundary cases
])
def test_boundaries(a, b, expected):
    assert divide(a, b) == expected
```

## Resources

### Scripts

- `scripts/generate_boundaries.py` - Analyzes function signatures and generates boundary test cases
- `scripts/analyze_paths.py` - Identifies code paths and suggests tests for uncovered branches

### References

- `references/boundary_patterns.md` - Common patterns for boundary value analysis and edge case identification
- `references/mutation_testing.md` - Comprehensive guide to mutation testing tools and result interpretation

## Best Practices

1. **Start with boundaries**: Test limits before normal cases
2. **Consider combinations**: Use pairwise testing for multiple parameters
3. **Test error paths**: Ensure error handling is robust
4. **Use property-based testing**: Let tools generate test cases automatically
5. **Verify with mutations**: Ensure tests actually catch bugs
6. **Document discoveries**: Record edge cases for future reference
7. **Automate generation**: Use scripts to create test matrices
8. **Monitor performance**: Track execution time across permutations