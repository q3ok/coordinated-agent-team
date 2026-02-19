from __future__ import annotations

import ast
import math

from .errors import ExpressionDomainError, ExpressionValidationError
from .models import CompiledExpression

_ALLOWED_FUNCTIONS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "sqrt": math.sqrt,
    "log": math.log,
    "exp": math.exp,
}
_ALLOWED_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
}
_ALLOWED_BINOPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)
_ALLOWED_UNARYOPS = (ast.UAdd, ast.USub)
_ALLOWED_AST_NODES = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Call,
    ast.Name,
    ast.Load,
    ast.Constant,
    *_ALLOWED_BINOPS,
    *_ALLOWED_UNARYOPS,
)
_MAX_AST_NODES = 200


def validate_and_compile(expression_text: str) -> CompiledExpression:
    text = expression_text.strip()
    if not text:
        raise ExpressionValidationError("Expression cannot be empty.")

    try:
        tree = ast.parse(text, mode="eval")
    except SyntaxError as error:
        raise ExpressionValidationError("Invalid expression syntax.") from error

    node_count = sum(1 for _ in ast.walk(tree))
    if node_count > _MAX_AST_NODES:
        raise ExpressionValidationError("Expression is too complex.")

    _validate_ast(tree)
    return CompiledExpression(expression_text=text, ast_tree=tree)


def evaluate(compiled: CompiledExpression, x_value: float) -> float:
    try:
        result = _evaluate_node(compiled.ast_tree.body, float(x_value))
    except (OverflowError, ZeroDivisionError, ValueError) as error:
        raise ExpressionDomainError("f(x) is undefined for provided x.") from error

    if not math.isfinite(result):
        raise ExpressionDomainError("f(x) is not finite for provided x.")
    return float(result)


def _validate_ast(tree: ast.AST) -> None:
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_AST_NODES):
            raise ExpressionValidationError("Unsupported expression construct.")

        if isinstance(node, ast.BinOp) and not isinstance(node.op, _ALLOWED_BINOPS):
            raise ExpressionValidationError("Unsupported operator in expression.")

        if isinstance(node, ast.UnaryOp) and not isinstance(node.op, _ALLOWED_UNARYOPS):
            raise ExpressionValidationError("Unsupported unary operator in expression.")

        if isinstance(node, ast.Constant):
            if type(node.value) not in (int, float):
                raise ExpressionValidationError("Only numeric constants are allowed.")

        if isinstance(node, ast.Name):
            if node.id.startswith("__"):
                raise ExpressionValidationError("Dunder names are not allowed.")
            if node.id not in {"x", *_ALLOWED_FUNCTIONS.keys(), *_ALLOWED_CONSTANTS.keys()}:
                raise ExpressionValidationError(f"Unknown identifier: {node.id}")

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in _ALLOWED_FUNCTIONS:
                raise ExpressionValidationError("Only approved math functions are allowed.")
            if len(node.args) != 1:
                raise ExpressionValidationError("Math functions require exactly one argument.")
            if node.keywords:
                raise ExpressionValidationError("Keyword arguments are not allowed.")


def _evaluate_node(node: ast.AST, x_value: float) -> float:
    if isinstance(node, ast.Constant):
        if type(node.value) in (int, float):
            return float(node.value)
        raise ExpressionValidationError("Only numeric constants are allowed.")

    if isinstance(node, ast.Name):
        if node.id == "x":
            return float(x_value)
        if node.id in _ALLOWED_CONSTANTS:
            return float(_ALLOWED_CONSTANTS[node.id])
        raise ExpressionValidationError(f"Unknown identifier: {node.id}")

    if isinstance(node, ast.UnaryOp):
        operand = _evaluate_node(node.operand, x_value)
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand
        raise ExpressionValidationError("Unsupported unary operator.")

    if isinstance(node, ast.BinOp):
        left = _evaluate_node(node.left, x_value)
        right = _evaluate_node(node.right, x_value)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Pow):
            return left**right
        raise ExpressionValidationError("Unsupported binary operator.")

    if isinstance(node, ast.Call):
        func_name = node.func.id
        function = _ALLOWED_FUNCTIONS[func_name]
        argument = _evaluate_node(node.args[0], x_value)
        return float(function(argument))

    raise ExpressionValidationError("Unsupported expression structure.")
