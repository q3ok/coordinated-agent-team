import pytest

from function_plot_cli.errors import ExpressionDomainError, ExpressionValidationError
from function_plot_cli.expression import evaluate, validate_and_compile


@pytest.mark.parametrize(
    ("expr", "x", "expected"),
    [
        ("sin(x)", 0.0, 0.0),
        ("cos(x)", 0.0, 1.0),
        ("x**2 - 3*x + 2", 2.0, 0.0),
        ("exp(0)", 5.0, 1.0),
    ],
)
def test_allowed_expressions_evaluate(expr, x, expected):
    compiled = validate_and_compile(expr)
    assert evaluate(compiled, x) == pytest.approx(expected)


@pytest.mark.parametrize(
    "expr",
    [
        "__import__('os')",
        "(1).__class__",
        "x[0]",
        "lambda x: x",
        "[x for x in [1,2]]",
    ],
)
def test_rejects_unsafe_constructs(expr):
    with pytest.raises(ExpressionValidationError):
        validate_and_compile(expr)


@pytest.mark.parametrize(
    "expr",
    [
        "x and 1",
        "x > 0",
        "x if x > 0 else -x",
    ],
)
def test_rejects_unsupported_ast_forms_at_validation(expr):
    with pytest.raises(ExpressionValidationError):
        validate_and_compile(expr)


def test_domain_error_is_typed_for_log_zero():
    compiled = validate_and_compile("log(x)")
    with pytest.raises(ExpressionDomainError):
        evaluate(compiled, 0.0)
