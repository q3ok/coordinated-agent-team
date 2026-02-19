class FunctionPlotCliError(Exception):
    """Base error for Function Plot CLI."""


class InputValidationError(FunctionPlotCliError):
    """Raised when a user input value is invalid."""


class ExpressionValidationError(FunctionPlotCliError):
    """Raised when expression syntax is unsafe or unsupported."""


class ExpressionDomainError(FunctionPlotCliError):
    """Raised when expression cannot be evaluated for a given x."""


class StorageError(FunctionPlotCliError):
    """Raised when recents persistence fails."""


class ExportError(FunctionPlotCliError):
    """Raised when export operation fails."""
