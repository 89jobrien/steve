---
status: DEPRECATED
deprecated_in: "2026-01-20"
---
# Boundary Testing Patterns

## Overview

Boundary value analysis (BVA) is a testing technique that focuses on values at the edges of input domains. Most errors occur at boundaries rather than in the middle of valid ranges.

## Core Boundary Categories

### 1. Numeric Boundaries

#### Integer Types

For any integer type with range [MIN, MAX]:

```
Test Values:
- MIN - 1 (underflow)
- MIN (minimum valid)
- MIN + 1 (just inside minimum)
- -1 (if signed)
- 0 (zero boundary)
- 1 (smallest positive)
- MAX - 1 (just inside maximum)
- MAX (maximum valid)
- MAX + 1 (overflow)
```

**Language-specific limits:**

```rust
// Rust
i8:  [-128, 127]
i16: [-32768, 32767]
i32: [-2147483648, 2147483647]
i64: [-9223372036854775808, 9223372036854775807]
u8:  [0, 255]
u16: [0, 65535]
u32: [0, 4294967295]
u64: [0, 18446744073709551615]
```

```python
# Python
import sys
sys.maxsize  # 9223372036854775807 on 64-bit
-sys.maxsize - 1  # -9223372036854775808
```

#### Floating Point

Special values to test:
- `0.0` and `-0.0`
- Smallest positive: `f32::MIN_POSITIVE`, `f64::MIN_POSITIVE`
- Largest finite: `f32::MAX`, `f64::MAX`
- Infinity: `f32::INFINITY`, `f32::NEG_INFINITY`
- Not-a-Number: `f32::NAN`
- Subnormal numbers (very small)
- Epsilon boundaries for precision

### 2. Collection Boundaries

#### Arrays/Vectors/Lists

```
Test Sizes:
- Empty collection (size 0)
- Single element (size 1)
- Two elements (size 2) - tests pair logic
- Typical size (3-10 elements)
- Large size (1000+ elements)
- Maximum allowed size
- Size that triggers reallocation
```

#### Strings

```
Test Cases:
- Empty string ""
- Single character "a"
- Single space " "
- Only whitespace "   \t\n"
- Maximum length string
- Unicode boundaries (ASCII vs UTF-8)
- Special characters (\0, \n, \r, \t)
- Mixed scripts (Latin + Cyrillic + Emoji)
```

### 3. Date/Time Boundaries

```
Critical Dates:
- Epoch: 1970-01-01 00:00:00 UTC
- Unix timestamp limits: 2038-01-19 (32-bit)
- Leap years: Feb 28/29
- DST transitions
- Time zone boundaries (+14:00 to -12:00)
- Month boundaries (28, 29, 30, 31 days)
- Year boundaries (Dec 31 -> Jan 1)
```

### 4. Loop Boundaries

```
Iteration Counts:
- 0 iterations (never enters loop)
- 1 iteration (single pass)
- 2 iterations (tests loop continuation)
- N-1 iterations (off-by-one check)
- N iterations (exact expected)
- N+1 iterations (off-by-one check)
- Maximum iterations before timeout
```

## Boundary Testing Strategies

### Strategy 1: Two-Value Boundary Testing

Test exactly on the boundary and just outside:
- For upper bound N: test N and N+1
- For lower bound M: test M and M-1

### Strategy 2: Three-Value Boundary Testing

Test on, just inside, and just outside:
- For upper bound N: test N-1, N, N+1
- For lower bound M: test M-1, M, M+1

### Strategy 3: Domain Matrix Testing

For functions with multiple parameters, create a matrix:

```python
def test_rectangle_area(width, height):
    boundaries_width = [0, 1, 100, 1000]
    boundaries_height = [0, 1, 100, 1000]

    for w in boundaries_width:
        for h in boundaries_height:
            result = calculate_area(w, h)
            # Verify result
```

### Strategy 4: Equivalence Partitioning + Boundaries

Divide input into equivalence classes, then test boundaries:

```
Age Groups Example:
- Invalid: age < 0 → test -1, -100
- Child: 0 ≤ age < 13 → test 0, 1, 12, 13
- Teen: 13 ≤ age < 20 → test 13, 14, 19, 20
- Adult: 20 ≤ age < 65 → test 20, 21, 64, 65
- Senior: age ≥ 65 → test 65, 66, 100, 150
```

## Common Boundary Bugs

### Off-by-One Errors

```rust
// Wrong: excludes last element
for i in 0..array.len() - 1 {  // Should be 0..array.len()
    process(array[i]);
}

// Wrong: includes invalid index
for i in 0..=array.len() {  // Should be 0..array.len()
    process(array[i]);  // Panic on last iteration
}
```

### Integer Overflow

```rust
// Dangerous
let result = a + b;  // Can overflow

// Safe
let result = a.checked_add(b).ok_or(Error::Overflow)?;
```

### Floating Point Comparison

```rust
// Wrong
if float_a == float_b {  // Exact comparison fails

// Right
if (float_a - float_b).abs() < EPSILON {
```

### Empty Collection Handling

```python
# Wrong
def average(numbers):
    return sum(numbers) / len(numbers)  # Division by zero

# Right
def average(numbers):
    if not numbers:
        return None
    return sum(numbers) / len(numbers)
```

## Boundary Test Checklist

### For Any Function

- [ ] Identify all input parameters
- [ ] Determine valid ranges for each parameter
- [ ] List boundary values for each range
- [ ] Test combinations of boundaries (if multiple params)
- [ ] Verify error handling at invalid boundaries
- [ ] Check for overflow/underflow conditions
- [ ] Test special values (null, empty, zero)

### For Numeric Functions

- [ ] Test with 0, 1, -1
- [ ] Test MIN and MAX values for type
- [ ] Test just inside and outside valid range
- [ ] Test overflow scenarios
- [ ] Test precision boundaries (for floats)
- [ ] Test NaN, Infinity (for floats)

### For String Functions

- [ ] Empty string
- [ ] Single character
- [ ] Maximum length
- [ ] Special characters (\0, \n, etc.)
- [ ] Unicode edge cases
- [ ] Whitespace-only strings

### For Collection Functions

- [ ] Empty collection
- [ ] Single element
- [ ] Two elements (pair operations)
- [ ] Maximum size
- [ ] Duplicate elements
- [ ] Sorted vs unsorted

### For Time/Date Functions

- [ ] Epoch boundaries
- [ ] Leap years
- [ ] DST transitions
- [ ] Time zone boundaries
- [ ] Month/year transitions
- [ ] Invalid dates (Feb 30, etc.)

## Automated Boundary Generation

### Python Example

```python
def generate_integer_boundaries(min_val, max_val):
    """Generate boundary test values for integer range."""
    boundaries = set()

    # Add boundary values
    boundaries.add(min_val - 1)  # Underflow
    boundaries.add(min_val)      # Minimum
    boundaries.add(min_val + 1)  # Just inside min

    # Add zero if in range
    if min_val <= 0 <= max_val:
        boundaries.add(-1)
        boundaries.add(0)
        boundaries.add(1)

    boundaries.add(max_val - 1)  # Just inside max
    boundaries.add(max_val)      # Maximum
    boundaries.add(max_val + 1)  # Overflow

    return sorted(boundaries)

# Usage
test_values = generate_integer_boundaries(-100, 100)
```

### Rust Example

```rust
fn generate_boundaries<T>(min: T, max: T) -> Vec<T>
where
    T: Copy + PartialOrd + std::ops::Add<Output = T> + std::ops::Sub<Output = T> + From<i8>,
{
    let mut boundaries = Vec::new();
    let one = T::from(1);

    // Boundary values
    boundaries.push(min);
    boundaries.push(max);

    // Just inside boundaries (if possible)
    if min < max {
        boundaries.push(min + one);
        boundaries.push(max - one);
    }

    boundaries
}
```

## Best Practices

1. **Document boundary assumptions**: Make valid ranges explicit
2. **Test boundaries first**: They're most likely to fail
3. **Combine boundaries**: Test multiple parameters at boundaries simultaneously
4. **Use property-based testing**: Tools like QuickCheck/Hypothesis can generate boundaries
5. **Consider domain knowledge**: Business rules may create additional boundaries
6. **Test boundary interactions**: How do boundaries in one field affect another?
7. **Automate generation**: Use scripts to generate boundary test cases
8. **Review historical bugs**: Past boundary bugs indicate testing gaps