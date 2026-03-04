#!/usr/bin/env python3
"""
Generate boundary test cases from function signatures.

This script analyzes function parameters and generates comprehensive boundary
test cases including edge cases, boundary values, and common error conditions.

Usage:
    python generate_boundaries.py --lang rust --func "divide(a: i32, b: i32) -> Result<i32>"
    python generate_boundaries.py --lang python --func "calculate_age(birth_year: int, current_year: int) -> int"
    python generate_boundaries.py --interactive
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ParamType(Enum):
    """Supported parameter types."""
    INT8 = "i8"
    INT16 = "i16"
    INT32 = "i32"
    INT64 = "i64"
    UINT8 = "u8"
    UINT16 = "u16"
    UINT32 = "u32"
    UINT64 = "u64"
    FLOAT32 = "f32"
    FLOAT64 = "f64"
    BOOL = "bool"
    STRING = "string"
    ARRAY = "array"
    GENERIC_INT = "int"
    GENERIC_FLOAT = "float"
    GENERIC_STR = "str"
    UNKNOWN = "unknown"


@dataclass
class Parameter:
    """Function parameter representation."""
    name: str
    param_type: ParamType
    optional: bool = False
    default_value: Any | None = None


@dataclass
class TestCase:
    """Represents a single test case."""
    inputs: dict[str, Any]
    category: str
    description: str
    expected_behavior: str = "verify"


class BoundaryGenerator:
    """Generate boundary test cases for different types."""

    # Type limits
    TYPE_LIMITS = {
        ParamType.INT8: (-128, 127),
        ParamType.INT16: (-32768, 32767),
        ParamType.INT32: (-2147483648, 2147483647),
        ParamType.INT64: (-9223372036854775808, 9223372036854775807),
        ParamType.UINT8: (0, 255),
        ParamType.UINT16: (0, 65535),
        ParamType.UINT32: (0, 4294967295),
        ParamType.UINT64: (0, 18446744073709551615),
        ParamType.GENERIC_INT: (-9223372036854775808, 9223372036854775807),
    }

    def __init__(self):
        self.test_cases: list[TestCase] = []

    def generate_integer_boundaries(self, param: Parameter) -> list[Any]:
        """Generate boundary values for integer types."""
        if param.param_type not in self.TYPE_LIMITS:
            return [0, 1, -1, 10, -10, 100, -100]

        min_val, max_val = self.TYPE_LIMITS[param.param_type]
        boundaries = []

        # Basic boundaries
        boundaries.extend([min_val, min_val + 1, max_val - 1, max_val])

        # Zero boundaries if in range
        if min_val <= 0 <= max_val:
            boundaries.extend([-1, 0, 1])

        # Common values
        if min_val <= -100 <= max_val:
            boundaries.append(-100)
        if min_val <= 100 <= max_val:
            boundaries.append(100)

        # Powers of 2 (important for binary operations)
        for power in [8, 16, 32, 64, 128, 256, 1024]:
            if min_val <= power <= max_val:
                boundaries.append(power)
            if min_val <= -power <= max_val:
                boundaries.append(-power)

        return sorted(set(boundaries))

    def generate_float_boundaries(self, param: Parameter) -> list[Any]:
        """Generate boundary values for floating-point types."""
        boundaries = [
            0.0, -0.0, 1.0, -1.0,
            0.1, -0.1, 0.5, -0.5,
            1.1, -1.1, 10.0, -10.0,
            100.0, -100.0,
            1e-10, -1e-10,  # Very small
            1e10, -1e10,    # Very large
            float('inf'), float('-inf'),  # Infinity
            float('nan'),   # NaN
        ]

        if param.param_type == ParamType.FLOAT32:
            boundaries.extend([
                3.4028235e38,   # f32::MAX
                -3.4028235e38,  # f32::MIN
                1.1754944e-38,  # f32::MIN_POSITIVE
            ])
        else:  # f64
            boundaries.extend([
                1.7976931348623157e308,   # f64::MAX
                -1.7976931348623157e308,  # f64::MIN
                2.2250738585072014e-308,  # f64::MIN_POSITIVE
            ])

        return boundaries

    def generate_bool_boundaries(self, param: Parameter) -> list[Any]:
        """Generate boundary values for boolean types."""
        return [True, False]

    def generate_string_boundaries(self, param: Parameter) -> list[Any]:
        """Generate boundary values for string types."""
        return [
            "",                    # Empty
            " ",                   # Single space
            "a",                   # Single char
            "abc",                 # Short
            "   ",                 # Whitespace only
            "\t\n\r",             # Special whitespace
            "Hello World",         # Normal
            "123",                # Numeric string
            "!@#$%^&*()",         # Special characters
            "null",               # Literal null
            "undefined",          # Literal undefined
            "true",               # Literal true
            "false",              # Literal false
            "0",                  # Zero string
            "\\n\\t\\r",          # Escaped characters
            "🚀🎉😀",            # Emoji/Unicode
            "A" * 1000,           # Long string
            "日本語",              # Non-ASCII
            "<script>alert()</script>",  # Potential XSS
            "'; DROP TABLE;",     # SQL injection attempt
        ]

    def generate_array_boundaries(self, param: Parameter) -> list[Any]:
        """Generate boundary values for array/list types."""
        return [
            [],                    # Empty
            [1],                   # Single element
            [1, 2],                # Two elements
            [1, 2, 3],             # Few elements
            [0] * 100,             # Many same elements
            list(range(100)),     # Many different elements
            [1, None, 3],          # With None/null
            [-1, 0, 1],            # Mixed signs
            [1, "2", 3],           # Mixed types (if allowed)
        ]

    def generate_test_cases(self, params: list[Parameter]) -> list[TestCase]:
        """Generate comprehensive test cases for given parameters."""
        test_cases = []

        # Single parameter boundary testing
        for param in params:
            boundaries = self._get_boundaries_for_type(param)

            for value in boundaries:
                inputs = {p.name: None for p in params}
                inputs[param.name] = value

                # Set normal values for other params
                for other_param in params:
                    if other_param.name != param.name:
                        inputs[other_param.name] = self._get_normal_value(other_param)

                category = self._categorize_value(value, param)
                description = f"Boundary test for {param.name}={value}"

                test_cases.append(TestCase(
                    inputs=inputs,
                    category=category,
                    description=description
                ))

        # Combinatorial boundary testing (pairwise)
        if len(params) >= 2:
            for i, param1 in enumerate(params):
                for param2 in params[i+1:]:
                    boundaries1 = self._get_boundaries_for_type(param1)[:3]  # Limit for combinations
                    boundaries2 = self._get_boundaries_for_type(param2)[:3]

                    for val1 in boundaries1:
                        for val2 in boundaries2:
                            inputs = {p.name: self._get_normal_value(p) for p in params}
                            inputs[param1.name] = val1
                            inputs[param2.name] = val2

                            test_cases.append(TestCase(
                                inputs=inputs,
                                category="combinatorial",
                                description=f"Combination: {param1.name}={val1}, {param2.name}={val2}"
                            ))

        return test_cases

    def _get_boundaries_for_type(self, param: Parameter) -> list[Any]:
        """Get boundary values based on parameter type."""
        if param.param_type in [ParamType.INT8, ParamType.INT16, ParamType.INT32,
                                ParamType.INT64, ParamType.UINT8, ParamType.UINT16,
                                ParamType.UINT32, ParamType.UINT64, ParamType.GENERIC_INT]:
            return self.generate_integer_boundaries(param)
        elif param.param_type in [ParamType.FLOAT32, ParamType.FLOAT64, ParamType.GENERIC_FLOAT]:
            return self.generate_float_boundaries(param)
        elif param.param_type == ParamType.BOOL:
            return self.generate_bool_boundaries(param)
        elif param.param_type in [ParamType.STRING, ParamType.GENERIC_STR]:
            return self.generate_string_boundaries(param)
        elif param.param_type == ParamType.ARRAY:
            return self.generate_array_boundaries(param)
        else:
            return [None, "default", 0]

    def _get_normal_value(self, param: Parameter) -> Any:
        """Get a normal (non-boundary) value for a parameter."""
        if param.default_value is not None:
            return param.default_value

        type_defaults = {
            ParamType.INT8: 5,
            ParamType.INT16: 5,
            ParamType.INT32: 5,
            ParamType.INT64: 5,
            ParamType.UINT8: 5,
            ParamType.UINT16: 5,
            ParamType.UINT32: 5,
            ParamType.UINT64: 5,
            ParamType.GENERIC_INT: 5,
            ParamType.FLOAT32: 5.0,
            ParamType.FLOAT64: 5.0,
            ParamType.GENERIC_FLOAT: 5.0,
            ParamType.BOOL: True,
            ParamType.STRING: "test",
            ParamType.GENERIC_STR: "test",
            ParamType.ARRAY: [1, 2, 3],
        }

        return type_defaults.get(param.param_type, "default")

    def _categorize_value(self, value: Any, param: Parameter) -> str:
        """Categorize a test value."""
        if value is None:
            return "null"
        elif param.param_type in [ParamType.STRING, ParamType.GENERIC_STR]:
            if value == "":
                return "empty"
            elif len(value) > 100:
                return "large"
            elif not value.strip():
                return "whitespace"
            else:
                return "boundary"
        elif param.param_type == ParamType.ARRAY:
            if len(value) == 0:
                return "empty"
            elif len(value) == 1:
                return "single"
            elif len(value) > 50:
                return "large"
            else:
                return "boundary"
        elif isinstance(value, (int, float)):
            if value == 0:
                return "zero"
            elif abs(value) == 1:
                return "unit"
            elif param.param_type in self.TYPE_LIMITS:
                min_val, max_val = self.TYPE_LIMITS[param.param_type]
                if value == min_val or value == max_val:
                    return "limit"
            return "boundary"
        else:
            return "boundary"


class FunctionParser:
    """Parse function signatures from different languages."""

    @staticmethod
    def parse_rust(signature: str) -> tuple[str, list[Parameter]]:
        """Parse Rust function signature."""
        # Example: divide(a: i32, b: i32) -> Result<i32>
        match = re.match(r'(\w+)\s*\((.*?)\)', signature)
        if not match:
            raise ValueError(f"Invalid Rust signature: {signature}")

        func_name = match.group(1)
        params_str = match.group(2)

        params = []
        if params_str:
            for param_str in params_str.split(','):
                param_match = re.match(r'\s*(\w+)\s*:\s*(\S+)', param_str.strip())
                if param_match:
                    name = param_match.group(1)
                    type_str = param_match.group(2)

                    # Map Rust types to ParamType
                    type_map = {
                        'i8': ParamType.INT8, 'i16': ParamType.INT16,
                        'i32': ParamType.INT32, 'i64': ParamType.INT64,
                        'u8': ParamType.UINT8, 'u16': ParamType.UINT16,
                        'u32': ParamType.UINT32, 'u64': ParamType.UINT64,
                        'f32': ParamType.FLOAT32, 'f64': ParamType.FLOAT64,
                        'bool': ParamType.BOOL,
                        '&str': ParamType.STRING, 'String': ParamType.STRING,
                        'Vec': ParamType.ARRAY, '&[': ParamType.ARRAY,
                    }

                    param_type = ParamType.UNKNOWN
                    for rust_type, param_enum in type_map.items():
                        if rust_type in type_str:
                            param_type = param_enum
                            break

                    params.append(Parameter(name, param_type))

        return func_name, params

    @staticmethod
    def parse_python(signature: str) -> tuple[str, list[Parameter]]:
        """Parse Python function signature."""
        # Example: calculate_age(birth_year: int, current_year: int = 2024) -> int
        match = re.match(r'(\w+)\s*\((.*?)\)', signature)
        if not match:
            raise ValueError(f"Invalid Python signature: {signature}")

        func_name = match.group(1)
        params_str = match.group(2)

        params = []
        if params_str:
            for param_str in params_str.split(','):
                # Handle type hints and defaults
                param_match = re.match(r'\s*(\w+)\s*(?::\s*(\w+))?\s*(?:=\s*(.+))?', param_str.strip())
                if param_match:
                    name = param_match.group(1)
                    type_str = param_match.group(2) or 'any'
                    default = param_match.group(3)

                    # Map Python types to ParamType
                    type_map = {
                        'int': ParamType.GENERIC_INT,
                        'float': ParamType.GENERIC_FLOAT,
                        'bool': ParamType.BOOL,
                        'str': ParamType.GENERIC_STR,
                        'list': ParamType.ARRAY,
                        'List': ParamType.ARRAY,
                    }

                    param_type = type_map.get(type_str, ParamType.UNKNOWN)
                    params.append(Parameter(name, param_type, default_value=default))

        return func_name, params


def format_test_output(func_name: str, test_cases: list[TestCase], lang: str) -> str:
    """Format test cases for output."""
    output = []

    if lang == "rust":
        output.append(f"// Boundary tests for {func_name}")
        output.append("#[cfg(test)]")
        output.append("mod boundary_tests {")
        output.append("    use super::*;\n")

        for i, test in enumerate(test_cases):
            output.append("    #[test]")
            output.append(f"    fn test_{func_name}_boundary_{i}() {{")
            output.append(f"        // Category: {test.category}")
            output.append(f"        // {test.description}")

            args = ", ".join(str(v) for v in test.inputs.values())
            output.append(f"        let result = {func_name}({args});")
            output.append("        // TODO: Assert expected behavior")
            output.append("    }\n")

        output.append("}")

    elif lang == "python":
        output.append(f"# Boundary tests for {func_name}")
        output.append("import pytest\n")

        # Create parametrize data
        param_names = list(test_cases[0].inputs.keys()) if test_cases else []
        param_str = ",".join(param_names)

        output.append(f"@pytest.mark.parametrize(\"{param_str}\", [")
        for test in test_cases:
            values = tuple(test.inputs.values())
            output.append(f"    {values},  # {test.category}: {test.description}")
        output.append("])")
        output.append(f"def test_{func_name}_boundaries({param_str}):")
        output.append(f"    result = {func_name}({param_str})")
        output.append("    # TODO: Add assertions based on expected behavior")

    else:  # JSON format
        json_output = {
            "function": func_name,
            "test_cases": [
                {
                    "inputs": test.inputs,
                    "category": test.category,
                    "description": test.description,
                    "expected_behavior": test.expected_behavior
                }
                for test in test_cases
            ]
        }
        output.append(json.dumps(json_output, indent=2))

    return "\n".join(output)


def interactive_mode():
    """Run in interactive mode."""
    print("Boundary Test Case Generator - Interactive Mode")
    print("=" * 50)

    lang = input("Language (rust/python): ").lower()
    if lang not in ["rust", "python"]:
        print("Unsupported language. Using generic mode.")
        lang = "generic"

    signature = input("Function signature: ")

    try:
        if lang == "rust":
            func_name, params = FunctionParser.parse_rust(signature)
        elif lang == "python":
            func_name, params = FunctionParser.parse_python(signature)
        else:
            print("Please specify parameters manually.")
            return

        print(f"\nParsed function: {func_name}")
        print("Parameters:")
        for param in params:
            print(f"  - {param.name}: {param.param_type.value}")

        generator = BoundaryGenerator()
        test_cases = generator.generate_test_cases(params)

        print(f"\nGenerated {len(test_cases)} test cases")

        output_format = input("\nOutput format (code/json) [code]: ").lower() or "code"

        if output_format == "json":
            print("\n" + format_test_output(func_name, test_cases, "json"))
        else:
            print("\n" + format_test_output(func_name, test_cases, lang))

    except Exception as e:
        print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(description="Generate boundary test cases from function signatures")
    parser.add_argument("--lang", choices=["rust", "python"], help="Programming language")
    parser.add_argument("--func", help="Function signature")
    parser.add_argument("--output", choices=["code", "json"], default="code", help="Output format")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--limit", type=int, help="Limit number of test cases")

    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
        return

    if not args.func or not args.lang:
        print("Error: --lang and --func are required (or use --interactive)")
        sys.exit(1)

    try:
        if args.lang == "rust":
            func_name, params = FunctionParser.parse_rust(args.func)
        else:  # python
            func_name, params = FunctionParser.parse_python(args.func)

        generator = BoundaryGenerator()
        test_cases = generator.generate_test_cases(params)

        if args.limit:
            test_cases = test_cases[:args.limit]

        output_lang = "json" if args.output == "json" else args.lang
        print(format_test_output(func_name, test_cases, output_lang))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
