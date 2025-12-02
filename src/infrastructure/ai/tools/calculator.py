from typing import List
import math
import operator
from langchain_community.tools import tool


@tool
def add_numbers(numbers: List[float]) -> float:
    """Add a list of numbers together."""
    return sum(numbers)


@tool
def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b


@tool
def multiply_numbers(numbers: List[float]) -> float:
    """Multiply a list of numbers together."""
    result = 1
    for num in numbers:
        result *= num
    return result


@tool
def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


@tool
def power(base: float, exponent: float) -> float:
    """Calculate base raised to the power of exponent."""
    return math.pow(base, exponent)


@tool
def square_root(number: float) -> float:
    """Calculate the square root of a number."""
    if number < 0:
        raise ValueError("Cannot calculate square root of negative number")
    return math.sqrt(number)


@tool
def calculate_percentage(value: float, total: float) -> float:
    """Calculate what percentage value is of total."""
    return (value / total) * 100


@tool
def evaluate_expression(expression: str) -> float:
    """
    Safely evaluate a mathematical expression string.
    Supports basic operations (+, -, *, /, **, ()).
    """
    # Define allowed operators
    operators = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.truediv,
        "**": operator.pow,
    }

    # Remove whitespace and validate characters
    expression = "".join(expression.split())
    allowed_chars = set("0123456789.+-*/() ")
    if not set(expression).issubset(allowed_chars):
        raise ValueError("Invalid characters in expression")

    try:
        # Use eval() with locals dict containing only safe operations
        safe_dict = {**operators, "__builtins__": None}
        return float(eval(expression, {"__builtins__": {}}, safe_dict))
    except Exception as e:
        raise ValueError(f"Invalid expression: {str(e)}")


def get_calculator_toolkit():
    """Return all calculator tools as a toolkit."""
    return [
        add_numbers,
        subtract,
        multiply_numbers,
        divide,
        power,
        square_root,
        calculate_percentage,
        evaluate_expression,
    ]
