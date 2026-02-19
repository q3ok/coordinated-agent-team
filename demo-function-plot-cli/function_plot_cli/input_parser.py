from __future__ import annotations

from .errors import InputValidationError


def parse_float(value: str, field_name: str = "value") -> float:
    text = value.strip()
    if not text:
        raise InputValidationError(f"{field_name} cannot be empty.")
    try:
        return float(text)
    except ValueError as error:
        raise InputValidationError(f"{field_name} must be a real number.") from error


def normalize_expression(value: str) -> str:
    text = value.strip()
    if not text:
        raise InputValidationError("Function expression cannot be empty.")
    return text
